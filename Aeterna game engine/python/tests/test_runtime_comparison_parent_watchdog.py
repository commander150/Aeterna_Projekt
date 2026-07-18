import json
import os
import socket
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path

from tools.runtime_comparison.parent_process_watchdog import (
    DEFAULT_POLL_INTERVAL_SECONDS,
    DEFAULT_REPOSITORY_TEMP_ROOT,
    ParentProcessWatchdog,
    ParentProcessWatchdogError,
    WindowsProcessHandle,
    append_parent_exit_tombstone,
    build_parent_watchdog_config,
)
from tools.runtime_comparison.sidecar_protocol import (
    PROTOCOL_VERSION,
    REQUEST_SCHEMA_VERSION,
    read_frame,
    send_frame,
)


PYTHON_PROJECT_ROOT = Path(__file__).resolve().parents[1]


class TestRuntimeComparisonParentWatchdog(unittest.TestCase):
    def test_optional_configuration_and_temp_confinement(self):
        self.assertIsNone(build_parent_watchdog_config(None, None, None))
        with self.assertRaises(ParentProcessWatchdogError) as incomplete:
            build_parent_watchdog_config(123, None, "run-1")
        self.assertEqual(
            incomplete.exception.code,
            "SIDECAR_PARENT_WATCHDOG_ARGUMENTS_INCOMPLETE",
        )
        outside = str(PYTHON_PROJECT_ROOT / "outside.log")
        with self.assertRaises(ParentProcessWatchdogError) as escaped:
            build_parent_watchdog_config(123, outside, "run-1")
        self.assertEqual(
            escaped.exception.code,
            "SIDECAR_PARENT_EXIT_LOG_OUTSIDE_TEMP",
        )

    def test_tombstone_is_utf8_durable_and_idempotent(self):
        with _watchdog_temp_directory() as temp_dir:
            log_path = Path(temp_dir) / "watchdog.log"
            log_path.write_text("visual proof header\n", encoding="utf-8")
            config = build_parent_watchdog_config(
                12345,
                str(log_path.resolve()),
                "watchdog-unit-run",
            )
            context = {
                "host": "127.0.0.1",
                "port": 54321,
                "active_connection_closed": True,
                "listener_closed_by_sidecar": True,
            }

            self.assertTrue(append_parent_exit_tombstone(config, context))
            self.assertTrue(append_parent_exit_tombstone(config, context))

            payload = log_path.read_bytes()
            text = payload.decode("utf-8")
            self.assertFalse(payload.startswith(b"\xef\xbb\xbf"))
            self.assertEqual(text.count("PARENT WATCHDOG SUMMARY"), 1)
            self.assertIn("parent_run_id: watchdog-unit-run", text)
            self.assertIn("parent_process_alive: false", text)
            self.assertIn("active_connection_closed: true", text)
            self.assertIn("listener_closed_by_sidecar: true", text)
            self.assertIn("sidecar_exit_initiated: true", text)
            self.assertIn("FINAL RESULT: CANCELLED", text)
            self.assertNotIn("process_stopped:", text)

    @unittest.skipUnless(sys.platform == "win32", "Windows handle acceptance")
    def test_windows_handle_reports_current_process_alive_and_closes(self):
        handle = WindowsProcessHandle(os.getpid())
        self.assertFalse(handle.wait(0.01))
        self.assertFalse(handle.closed)
        handle.close()
        self.assertTrue(handle.closed)

    @unittest.skipUnless(sys.platform == "win32", "Windows handle acceptance")
    def test_watchdog_detects_process_exit_without_busy_loop(self):
        parent = _start_sleeping_process()
        callback_called = threading.Event()
        with _watchdog_temp_directory() as temp_dir:
            config = build_parent_watchdog_config(
                parent.pid,
                str((Path(temp_dir) / "callback.log").resolve()),
                "watchdog-callback-run",
            )
            watchdog = ParentProcessWatchdog(config, callback_called.set).start()
            try:
                parent.terminate()
                parent.wait(timeout=3)
                self.assertTrue(callback_called.wait(timeout=3))
                self.assertEqual(DEFAULT_POLL_INTERVAL_SECONDS, 0.2)
            finally:
                watchdog.stop()
                _stop_process(parent)

    @unittest.skipUnless(sys.platform == "win32", "Windows sidecar acceptance")
    def test_sidecar_parent_exit_closes_active_socket_listener_and_logs(self):
        parent = _start_sleeping_process()
        sidecar = None
        connection = None
        with _watchdog_temp_directory() as temp_dir:
            log_path = Path(temp_dir) / "sidecar_parent_exit.log"
            command = [
                sys.executable,
                "-B",
                "-m",
                "tools.runtime_comparison.python_sidecar_server",
                "--host",
                "127.0.0.1",
                "--port",
                "0",
                "--parent-pid",
                str(parent.pid),
                "--parent-exit-log",
                str(log_path.resolve()),
                "--parent-run-id",
                "watchdog-sidecar-run",
            ]
            environment = os.environ.copy()
            environment["PYTHONDONTWRITEBYTECODE"] = "1"
            try:
                sidecar = subprocess.Popen(
                    command,
                    cwd=PYTHON_PROJECT_ROOT,
                    env=environment,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8",
                    errors="strict",
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )
                startup = json.loads(sidecar.stdout.readline())
                self.assertEqual(startup["protocol_version"], PROTOCOL_VERSION)
                port = startup["port"]
                connection = socket.create_connection(("127.0.0.1", port), timeout=2)
                connection.settimeout(2)
                send_frame(
                    connection,
                    {
                        "schema_version": REQUEST_SCHEMA_VERSION,
                        "protocol_version": PROTOCOL_VERSION,
                        "request_id": "watchdog_health",
                        "command": "health",
                        "payload": {},
                    },
                )
                self.assertTrue(read_frame(connection)["ok"])

                parent.terminate()
                parent.wait(timeout=3)
                self.assertEqual(sidecar.wait(timeout=3), 3)
                self.assertTrue(_listener_is_closed(port))
                self.assertEqual(sidecar.stdout.read(), "")
                self.assertEqual(sidecar.stderr.read(), "")
                sidecar.stdout.close()
                sidecar.stderr.close()
                text = log_path.read_text(encoding="utf-8")
                self.assertIn("parent_run_id: watchdog-sidecar-run", text)
                self.assertIn("active_connection_closed: true", text)
                self.assertIn("listener_closed_by_sidecar: true", text)
                self.assertIn("ERROR CODE: SIDECAR_PARENT_PROCESS_EXITED", text)
            finally:
                if connection is not None:
                    connection.close()
                _stop_process(sidecar)
                _close_process_streams(sidecar)
                _stop_process(parent)


def _watchdog_temp_directory():
    DEFAULT_REPOSITORY_TEMP_ROOT.mkdir(parents=True, exist_ok=True)
    return tempfile.TemporaryDirectory(
        prefix="c3b2b_watchdog_test_",
        dir=DEFAULT_REPOSITORY_TEMP_ROOT,
    )


def _start_sleeping_process():
    return subprocess.Popen(
        [sys.executable, "-B", "-c", "import time; time.sleep(30)"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )


def _stop_process(process):
    if process is None or process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=2)


def _close_process_streams(process):
    if process is None:
        return
    for stream_name in ("stdout", "stderr"):
        stream = getattr(process, stream_name, None)
        if stream is not None and not stream.closed:
            stream.close()


def _listener_is_closed(port):
    try:
        connection = socket.create_connection(("127.0.0.1", port), timeout=0.25)
    except OSError:
        return True
    connection.close()
    return False


if __name__ == "__main__":
    unittest.main()
