"""Parent-process monitoring and durable cancellation logging for sidecar runtimes."""

from __future__ import annotations

import ctypes
import os
import re
import sys
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_POLL_INTERVAL_SECONDS = 0.2
DEFAULT_REPOSITORY_TEMP_ROOT = Path(__file__).resolve().parents[4] / "TEMP"
PARENT_EXIT_CODE = 3
_RUN_ID_PATTERN = re.compile(r"\A[A-Za-z0-9][A-Za-z0-9._:-]{0,127}\Z")


class ParentProcessWatchdogError(ValueError):
    """Stable parent-watchdog configuration or runtime failure."""

    def __init__(self, code, message):
        self.code = str(code)
        self.message = str(message)
        super().__init__("%s: %s" % (self.code, self.message))


@dataclass(frozen=True)
class ParentWatchdogConfig:
    parent_pid: int
    exit_log_path: Path
    run_id: str


def build_parent_watchdog_config(
    parent_pid,
    parent_exit_log,
    parent_run_id,
    *,
    allowed_temp_root=DEFAULT_REPOSITORY_TEMP_ROOT,
):
    """Validate optional CLI values and confine the durable log to repository TEMP."""

    values = (parent_pid, parent_exit_log, parent_run_id)
    if all(value is None for value in values):
        return None
    if any(value is None for value in values):
        raise ParentProcessWatchdogError(
            "SIDECAR_PARENT_WATCHDOG_ARGUMENTS_INCOMPLETE",
            "Parent PID, exit log, and run ID must be provided together.",
        )
    if type(parent_pid) is not int or parent_pid <= 0 or parent_pid == os.getpid():
        raise ParentProcessWatchdogError(
            "SIDECAR_PARENT_PID_INVALID",
            "Parent PID must be a positive external process identifier.",
        )
    if not isinstance(parent_run_id, str) or not _RUN_ID_PATTERN.fullmatch(parent_run_id):
        raise ParentProcessWatchdogError(
            "SIDECAR_PARENT_RUN_ID_INVALID",
            "Parent run ID contains unsupported characters or length.",
        )
    if not isinstance(parent_exit_log, str) or not Path(parent_exit_log).is_absolute():
        raise ParentProcessWatchdogError(
            "SIDECAR_PARENT_EXIT_LOG_INVALID",
            "Parent exit log must be an absolute path inside repository TEMP.",
        )

    temp_root = Path(allowed_temp_root).resolve()
    exit_log_path = Path(parent_exit_log).resolve(strict=False)
    try:
        exit_log_path.relative_to(temp_root)
    except ValueError:
        raise ParentProcessWatchdogError(
            "SIDECAR_PARENT_EXIT_LOG_OUTSIDE_TEMP",
            "Parent exit log must remain inside repository TEMP.",
        ) from None
    if exit_log_path.exists() and not exit_log_path.is_file():
        raise ParentProcessWatchdogError(
            "SIDECAR_PARENT_EXIT_LOG_INVALID",
            "Parent exit log path does not name a regular file.",
        )
    try:
        exit_log_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        raise ParentProcessWatchdogError(
            "SIDECAR_PARENT_EXIT_LOG_UNAVAILABLE",
            "Parent exit log directory could not be prepared.",
        ) from None
    return ParentWatchdogConfig(parent_pid, exit_log_path, parent_run_id)


class WindowsProcessHandle:
    """Small owned Windows process handle used for liveness and test cleanup."""

    SYNCHRONIZE = 0x00100000
    PROCESS_TERMINATE = 0x0001
    WAIT_OBJECT_0 = 0x00000000
    WAIT_TIMEOUT = 0x00000102
    WAIT_FAILED = 0xFFFFFFFF

    def __init__(self, pid, *, allow_terminate=False):
        if sys.platform != "win32":
            raise ParentProcessWatchdogError(
                "SIDECAR_PARENT_WATCHDOG_PLATFORM_UNSUPPORTED",
                "Windows process handles are only available on Windows.",
            )
        if type(pid) is not int or pid <= 0:
            raise ParentProcessWatchdogError(
                "SIDECAR_PARENT_PID_INVALID",
                "Process PID must be a positive integer.",
            )
        self.pid = pid
        self._kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self._configure_api()
        access = self.SYNCHRONIZE
        if allow_terminate:
            access |= self.PROCESS_TERMINATE
        self._handle = self._kernel32.OpenProcess(access, False, pid)
        if not self._handle:
            raise ParentProcessWatchdogError(
                "SIDECAR_PARENT_PROCESS_UNAVAILABLE",
                "Parent process handle could not be opened.",
            )
        self._allow_terminate = allow_terminate

    def _configure_api(self):
        from ctypes import wintypes

        self._kernel32.OpenProcess.argtypes = (
            wintypes.DWORD,
            wintypes.BOOL,
            wintypes.DWORD,
        )
        self._kernel32.OpenProcess.restype = wintypes.HANDLE
        self._kernel32.WaitForSingleObject.argtypes = (wintypes.HANDLE, wintypes.DWORD)
        self._kernel32.WaitForSingleObject.restype = wintypes.DWORD
        self._kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)
        self._kernel32.CloseHandle.restype = wintypes.BOOL
        self._kernel32.TerminateProcess.argtypes = (wintypes.HANDLE, wintypes.UINT)
        self._kernel32.TerminateProcess.restype = wintypes.BOOL

    @property
    def closed(self):
        return not bool(self._handle)

    def wait(self, timeout_seconds):
        if self.closed:
            return True
        timeout_msec = max(0, int(float(timeout_seconds) * 1000))
        result = self._kernel32.WaitForSingleObject(self._handle, timeout_msec)
        if result == self.WAIT_OBJECT_0:
            return True
        if result == self.WAIT_TIMEOUT:
            return False
        raise ParentProcessWatchdogError(
            "SIDECAR_PARENT_WAIT_FAILED",
            "Waiting for the parent process handle failed.",
        )

    def terminate(self, exit_code=PARENT_EXIT_CODE):
        if not self._allow_terminate or self.closed:
            return False
        return bool(self._kernel32.TerminateProcess(self._handle, int(exit_code)))

    def close(self):
        if self._handle:
            self._kernel32.CloseHandle(self._handle)
            self._handle = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return False


class ParentProcessWatchdog:
    """Invoke one callback when an owned parent process handle becomes signaled."""

    def __init__(
        self,
        config,
        on_parent_exit,
        *,
        poll_interval_seconds=DEFAULT_POLL_INTERVAL_SECONDS,
    ):
        if not isinstance(config, ParentWatchdogConfig):
            raise TypeError("config must be ParentWatchdogConfig")
        if not callable(on_parent_exit):
            raise TypeError("on_parent_exit must be callable")
        if not 0.1 <= float(poll_interval_seconds) <= 0.25:
            raise ValueError("poll_interval_seconds must be between 0.1 and 0.25")
        self.config = config
        self.on_parent_exit = on_parent_exit
        self.poll_interval_seconds = float(poll_interval_seconds)
        self._stop_event = threading.Event()
        self._thread = None
        self._handle = None

    def start(self):
        if self._thread is not None:
            raise RuntimeError("Parent process watchdog can only be started once.")
        if sys.platform == "win32":
            self._handle = WindowsProcessHandle(self.config.parent_pid)
        self._thread = threading.Thread(
            target=self._watch,
            name="aeterna-sidecar-parent-watchdog",
            daemon=True,
        )
        self._thread.start()
        return self

    def stop(self):
        self._stop_event.set()
        if self._thread is not None and self._thread is not threading.current_thread():
            self._thread.join(timeout=self.poll_interval_seconds * 2 + 0.25)
        self._close_handle()

    def _watch(self):
        try:
            while not self._stop_event.is_set():
                if self._parent_exited():
                    self._close_handle()
                    if not self._stop_event.is_set():
                        self.on_parent_exit()
                    return
        finally:
            self._close_handle()

    def _parent_exited(self):
        if self._handle is not None:
            return self._handle.wait(self.poll_interval_seconds)
        if self._stop_event.wait(self.poll_interval_seconds):
            return False
        try:
            os.kill(self.config.parent_pid, 0)
        except ProcessLookupError:
            return True
        except PermissionError:
            return False
        return False

    def _close_handle(self):
        if self._handle is not None:
            self._handle.close()
            self._handle = None


def append_parent_exit_tombstone(config, context, *, retries=4, retry_delay=0.05):
    """Append one durable UTF-8 tombstone and fsync it before returning."""

    marker = "parent_run_id: %s" % config.run_id
    try:
        if config.exit_log_path.exists():
            existing = config.exit_log_path.read_text(encoding="utf-8", errors="replace")
            if "PARENT WATCHDOG SUMMARY" in existing and marker in existing:
                return True
    except OSError:
        pass

    block = _parent_exit_tombstone_text(config, context)
    for attempt in range(max(1, int(retries))):
        try:
            with config.exit_log_path.open("a", encoding="utf-8", newline="\n") as log_file:
                log_file.write(block)
                log_file.flush()
                os.fsync(log_file.fileno())
            return True
        except OSError:
            if attempt + 1 < retries:
                time.sleep(retry_delay)
    return False


def _parent_exit_tombstone_text(config, context):
    return "\n".join(
        (
            "",
            "PARENT WATCHDOG SUMMARY",
            "parent_run_id: %s" % config.run_id,
            "interruption_origin: python_parent_watchdog",
            "parent_pid: %d" % config.parent_pid,
            "parent_process_alive: false",
            "sidecar_pid: %d" % os.getpid(),
            "host: %s" % context.get("host", "unknown"),
            "port: %s" % context.get("port", "unknown"),
            "active_connection_closed: %s"
            % _bool_text(context.get("active_connection_closed", False)),
            "listener_closed_by_sidecar: %s"
            % _bool_text(context.get("listener_closed_by_sidecar", False)),
            "self_shutdown_requested: true",
            "sidecar_exit_initiated: true",
            "FINAL RESULT: CANCELLED",
            "FAILED AT: parent_process_exit",
            "ERROR CODE: SIDECAR_PARENT_PROCESS_EXITED",
            "ERROR: Godot parent process exited before sidecar shutdown.",
            "finished_at: %s" % _utc_timestamp(),
            "",
        )
    )


def _bool_text(value):
    return "true" if bool(value) else "false"


def _utc_timestamp():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


__all__ = [
    "DEFAULT_POLL_INTERVAL_SECONDS",
    "DEFAULT_REPOSITORY_TEMP_ROOT",
    "PARENT_EXIT_CODE",
    "ParentProcessWatchdog",
    "ParentProcessWatchdogError",
    "ParentWatchdogConfig",
    "WindowsProcessHandle",
    "append_parent_exit_tombstone",
    "build_parent_watchdog_config",
]
