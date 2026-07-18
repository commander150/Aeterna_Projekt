"""Lifecycle harness for the separate Python sidecar server process."""

from __future__ import annotations

import json
import os
import queue
import subprocess
import sys
import threading
from pathlib import Path

from tools.runtime_comparison.python_sidecar_client import (
    PythonSidecarClient,
    PythonSidecarClientError,
)
from tools.runtime_comparison.sidecar_protocol import (
    DEFAULT_SOCKET_TIMEOUT,
    SidecarProtocolError,
    validate_startup_handshake,
)


DEFAULT_PROCESS_TIMEOUT = 10.0
PYTHON_PROJECT_ROOT = Path(__file__).resolve().parents[2]


class PythonSidecarProcessError(Exception):
    """Stable process startup or lifecycle failure."""

    def __init__(self, code, message):
        self.code = str(code)
        self.message = str(message)
        super().__init__("%s: %s" % (self.code, self.message))


class PythonSidecarProcess:
    """Start, connect to, and reliably stop one proof sidecar process."""

    def __init__(
        self,
        *,
        startup_timeout=DEFAULT_PROCESS_TIMEOUT,
        shutdown_timeout=DEFAULT_PROCESS_TIMEOUT,
        client_timeout=DEFAULT_SOCKET_TIMEOUT,
    ):
        self.startup_timeout = _positive_timeout(startup_timeout, "startup_timeout")
        self.shutdown_timeout = _positive_timeout(shutdown_timeout, "shutdown_timeout")
        self.client_timeout = _positive_timeout(client_timeout, "client_timeout")
        self.process = None
        self.client = None
        self.startup = None
        self.host = None
        self.port = None
        self.shutdown_succeeded = False
        self.terminate_used = False
        self.kill_used = False
        self.stdout_remainder = ""
        self.stderr_text = ""
        self._output_collected = False

    @property
    def pid(self):
        return None if self.process is None else self.process.pid

    @property
    def exit_code(self):
        return None if self.process is None else self.process.poll()

    @property
    def is_alive(self):
        return self.process is not None and self.process.poll() is None

    def start(self):
        if self.process is not None:
            raise PythonSidecarProcessError(
                "SIDECAR_PROCESS_ALREADY_STARTED",
                "Sidecar process harness can only be started once.",
            )
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        command = [
            sys.executable,
            "-B",
            "-m",
            "tools.runtime_comparison.python_sidecar_server",
            "--host",
            "127.0.0.1",
            "--port",
            "0",
        ]
        try:
            self.process = subprocess.Popen(
                command,
                cwd=PYTHON_PROJECT_ROOT,
                env=environment,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="strict",
                bufsize=1,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except OSError:
            raise PythonSidecarProcessError(
                "SIDECAR_PROCESS_START_FAILED",
                "Python sidecar process could not be started.",
            ) from None

        startup_line = _readline_with_timeout(
            self.process.stdout,
            self.startup_timeout,
        )
        if startup_line is None:
            self._force_stop()
            self._collect_output()
            raise PythonSidecarProcessError(
                "SIDECAR_STARTUP_TIMEOUT",
                "Python sidecar did not provide its startup handshake in time.",
            )
        if startup_line == "":
            self._wait_or_force_stop()
            self._collect_output()
            raise PythonSidecarProcessError(
                "SIDECAR_STARTUP_MISSING",
                "Python sidecar exited without a startup handshake.",
            )
        try:
            startup = json.loads(startup_line)
            validate_startup_handshake(startup)
        except (json.JSONDecodeError, SidecarProtocolError):
            self._force_stop()
            self._collect_output()
            raise PythonSidecarProcessError(
                "SIDECAR_STARTUP_INVALID",
                "Python sidecar startup handshake is invalid.",
            ) from None

        self.startup = startup
        self.host = startup["host"]
        self.port = startup["port"]
        self.client = PythonSidecarClient(
            self.host,
            self.port,
            timeout=self.client_timeout,
        )
        try:
            self.client.connect()
        except PythonSidecarClientError:
            self._force_stop()
            self._collect_output()
            raise PythonSidecarProcessError(
                "SIDECAR_STARTUP_CONNECT_FAILED",
                "Python sidecar startup succeeded but the client could not connect.",
            ) from None
        return self

    def shutdown(self, request_id="sidecar_process_shutdown"):
        if self.client is None or not self.client.connected:
            raise PythonSidecarProcessError(
                "SIDECAR_PROCESS_CLIENT_UNAVAILABLE",
                "Sidecar process client is not available for shutdown.",
            )
        try:
            response = self.client.shutdown(request_id)
            self.shutdown_succeeded = True
        except PythonSidecarClientError as exc:
            raise PythonSidecarProcessError(
                "SIDECAR_PROCESS_SHUTDOWN_FAILED",
                "Python sidecar did not complete its shutdown request.",
            ) from exc
        finally:
            self.client.close()
        self._wait_or_force_stop()
        self._collect_output()
        return response

    def stop(self):
        if self.process is None:
            return
        if self.is_alive and self.client is not None and self.client.connected:
            try:
                self.shutdown("sidecar_process_context_shutdown")
                return
            except PythonSidecarProcessError:
                pass
        if self.client is not None:
            self.client.close()
        if self.is_alive:
            self._force_stop()
        self._collect_output()

    def _wait_or_force_stop(self):
        if self.process is None or self.process.poll() is not None:
            return
        try:
            self.process.wait(timeout=self.shutdown_timeout)
        except subprocess.TimeoutExpired:
            self._force_stop()

    def _force_stop(self):
        if self.process is None or self.process.poll() is not None:
            return
        self.process.terminate()
        self.terminate_used = True
        try:
            self.process.wait(timeout=self.shutdown_timeout)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.kill_used = True
            self.process.wait(timeout=self.shutdown_timeout)

    def _collect_output(self):
        if self._output_collected or self.process is None or self.process.poll() is None:
            return
        if self.process.stdout is not None:
            self.stdout_remainder = self.process.stdout.read()
            self.process.stdout.close()
        if self.process.stderr is not None:
            self.stderr_text = self.process.stderr.read()
            self.process.stderr.close()
        self._output_collected = True

    def __enter__(self):
        return self.start()

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()
        return False


def _readline_with_timeout(stream, timeout):
    result_queue = queue.Queue(maxsize=1)

    def read_line():
        try:
            result_queue.put(stream.readline())
        except (OSError, UnicodeError):
            result_queue.put("")

    thread = threading.Thread(target=read_line, daemon=True)
    thread.start()
    try:
        return result_queue.get(timeout=timeout)
    except queue.Empty:
        return None


def _positive_timeout(value, name):
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
        raise PythonSidecarProcessError(
            "SIDECAR_PROCESS_TIMEOUT_INVALID",
            "%s must be a positive number." % name,
        )
    return float(value)


__all__ = [
    "DEFAULT_PROCESS_TIMEOUT",
    "PYTHON_PROJECT_ROOT",
    "PythonSidecarProcess",
    "PythonSidecarProcessError",
]
