"""External Godot process-death proof for the Python sidecar parent watchdog."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from tools.runtime_comparison.parent_process_watchdog import WindowsProcessHandle


REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
REPOSITORY_TEMP_ROOT = REPOSITORY_ROOT / "TEMP"
GODOT_PROJECT_DIR = Path(__file__).resolve().parents[3] / "Godot"
VISUAL_PROOF_LOG = REPOSITORY_TEMP_ROOT / "godot_visual_sidecar_proof_latest.log"
DEFAULT_DIAGNOSTICS_DIR = (
    REPOSITORY_TEMP_ROOT / "c3b2b_parent_watchdog_and_f8_cleanup"
)
PROCESS_DEATH_SCRIPT = (
    "res://scripts/debug/python_sidecar_visual_proof_process_death_test.gd"
)


class GodotParentDeathProofError(RuntimeError):
    def __init__(self, code, message):
        self.code = str(code)
        self.message = str(message)
        super().__init__("%s: %s" % (self.code, self.message))


def run_parent_death_proofs(
    godot_executable,
    *,
    python_executable=sys.executable,
    diagnostics_dir=DEFAULT_DIAGNOSTICS_DIR,
    runs=2,
):
    godot_executable = _required_file(godot_executable, "Godot executable")
    python_executable = _required_file(python_executable, "Python executable")
    diagnostics_dir = _confined_diagnostics_dir(diagnostics_dir)
    if type(runs) is not int or runs <= 0:
        raise GodotParentDeathProofError(
            "PARENT_DEATH_RUN_COUNT_INVALID",
            "Process-death run count must be a positive integer.",
        )
    results = []
    for run_number in range(1, runs + 1):
        results.append(
            run_parent_death_proof(
                godot_executable,
                python_executable=python_executable,
                diagnostics_dir=diagnostics_dir,
                run_label="process_death_run_%d" % run_number,
            )
        )
    return results


def run_parent_death_proof(
    godot_executable,
    *,
    python_executable=sys.executable,
    diagnostics_dir=DEFAULT_DIAGNOSTICS_DIR,
    run_label="process_death_run",
):
    godot_executable = _required_file(godot_executable, "Godot executable")
    python_executable = _required_file(python_executable, "Python executable")
    diagnostics_dir = _confined_diagnostics_dir(diagnostics_dir)
    stdout_path = diagnostics_dir / (run_label + "_godot_stdout.log")
    stderr_path = diagnostics_dir / (run_label + "_godot_stderr.log")
    preserved_log_path = diagnostics_dir / (run_label + "_cancelled.log")
    result_path = diagnostics_dir / (run_label + "_result.json")
    for path in (stdout_path, stderr_path, preserved_log_path, result_path):
        path.unlink(missing_ok=True)
    VISUAL_PROOF_LOG.unlink(missing_ok=True)

    result = {
        "schema_version": "aeterna-godot-sidecar-parent-death-proof-v1",
        "run_label": run_label,
        "started_at": _utc_timestamp(),
        "godot_pid": None,
        "sidecar_pid": None,
        "host": None,
        "port": None,
        "run_id": None,
        "ready": False,
        "godot_externally_terminated": False,
        "sidecar_stopped_automatically": False,
        "sidecar_stop_seconds": None,
        "listener_closed": False,
        "watchdog_tombstone_present": False,
        "fallback_cleanup_used": False,
        "fallback_cleanup_succeeded": False,
        "godot_stderr_empty": False,
        "godot_warning_or_error": False,
        "success": False,
        "finished_at": None,
    }
    godot_process = None
    sidecar_handle = None
    stdout_file = None
    stderr_file = None
    try:
        environment = os.environ.copy()
        environment["AETERNA_PYTHON_EXECUTABLE"] = str(python_executable)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        stdout_file = stdout_path.open("w", encoding="utf-8", newline="\n")
        stderr_file = stderr_path.open("w", encoding="utf-8", newline="\n")
        command = [
            str(godot_executable),
            "--headless",
            "--path",
            str(GODOT_PROJECT_DIR),
            "--script",
            PROCESS_DEATH_SCRIPT,
            "--",
            "--hold-msec=30000",
        ]
        godot_process = subprocess.Popen(
            command,
            cwd=GODOT_PROJECT_DIR,
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=stdout_file,
            stderr=stderr_file,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        result["godot_pid"] = godot_process.pid
        ready = _wait_for_ready(godot_process, timeout=15.0)
        result.update(ready)
        result["ready"] = True
        if ready["godot_pid"] != godot_process.pid:
            raise GodotParentDeathProofError(
                "PARENT_DEATH_GODOT_PID_MISMATCH",
                "Visual proof log Godot PID did not match the launched process.",
            )
        sidecar_handle = WindowsProcessHandle(
            ready["sidecar_pid"],
            allow_terminate=True,
        )
        if sidecar_handle.wait(0):
            raise GodotParentDeathProofError(
                "PARENT_DEATH_SIDECAR_NOT_RUNNING",
                "Sidecar exited before the parent-death probe.",
            )
        if not _listener_accepts(ready["host"], ready["port"]):
            raise GodotParentDeathProofError(
                "PARENT_DEATH_LISTENER_NOT_READY",
                "Sidecar listener was not accepting connections at READY.",
            )

        stop_started = time.monotonic()
        godot_process.kill()
        godot_process.wait(timeout=5)
        result["godot_externally_terminated"] = True
        result["sidecar_stopped_automatically"] = sidecar_handle.wait(5.0)
        result["sidecar_stop_seconds"] = round(time.monotonic() - stop_started, 3)
        result["listener_closed"] = _wait_for_listener_closed(
            ready["host"],
            ready["port"],
            timeout=1.0,
        )
        log_text = _wait_for_watchdog_tombstone(ready["run_id"], timeout=2.0)
        result["watchdog_tombstone_present"] = _valid_watchdog_tombstone(
            log_text,
            ready,
        )
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        result["error"] = "%s: %s" % (type(exc).__name__, exc)
    except GodotParentDeathProofError as exc:
        result["error_code"] = exc.code
        result["error"] = exc.message
    finally:
        if godot_process is not None and godot_process.poll() is None:
            godot_process.kill()
            try:
                godot_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass
        if sidecar_handle is not None and not sidecar_handle.wait(0):
            result["fallback_cleanup_used"] = True
            sidecar_handle.terminate()
            result["fallback_cleanup_succeeded"] = sidecar_handle.wait(3.0)
        if sidecar_handle is not None:
            sidecar_handle.close()
        if stdout_file is not None:
            stdout_file.close()
        if stderr_file is not None:
            stderr_file.close()
        if VISUAL_PROOF_LOG.exists():
            shutil.copyfile(VISUAL_PROOF_LOG, preserved_log_path)
        stderr_text = stderr_path.read_text(encoding="utf-8") if stderr_path.exists() else ""
        stdout_text = stdout_path.read_text(encoding="utf-8") if stdout_path.exists() else ""
        result["godot_stderr_empty"] = stderr_text == ""
        combined_output = (stdout_text + "\n" + stderr_text).lower()
        result["godot_warning_or_error"] = any(
            marker in combined_output
            for marker in ("warning:", "error:", "script error", "parse error")
        )
        result["success"] = all(
            (
                result["ready"],
                result["godot_externally_terminated"],
                result["sidecar_stopped_automatically"],
                result["listener_closed"],
                result["watchdog_tombstone_present"],
                not result["fallback_cleanup_used"],
                result["godot_stderr_empty"],
                not result["godot_warning_or_error"],
            )
        )
        result["finished_at"] = _utc_timestamp()
        result_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return result


def _wait_for_ready(godot_process, timeout):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if godot_process.poll() is not None:
            raise GodotParentDeathProofError(
                "PARENT_DEATH_GODOT_EXITED_EARLY",
                "Godot exited before the cancellation test reached READY.",
            )
        try:
            text = VISUAL_PROOF_LOG.read_text(encoding="utf-8")
        except OSError:
            time.sleep(0.05)
            continue
        parsed = _parse_ready_log(text)
        if parsed is not None:
            return parsed
        time.sleep(0.05)
    raise GodotParentDeathProofError(
        "PARENT_DEATH_READY_TIMEOUT",
        "Cancellation test did not reach READY before timeout.",
    )


def _parse_ready_log(text):
    if "CANCELLATION TEST READY" not in text:
        return None
    fields = {}
    for line in text.splitlines():
        if ": " not in line:
            continue
        key, value = line.split(": ", 1)
        if key in {"run_id", "godot_pid", "sidecar_pid", "host", "port"}:
            fields[key] = value
    if not all(key in fields for key in ("run_id", "godot_pid", "sidecar_pid", "host", "port")):
        return None
    try:
        return {
            "run_id": fields["run_id"],
            "godot_pid": int(fields["godot_pid"]),
            "sidecar_pid": int(fields["sidecar_pid"]),
            "host": fields["host"],
            "port": int(fields["port"]),
        }
    except ValueError:
        return None


def _wait_for_watchdog_tombstone(run_id, timeout):
    deadline = time.monotonic() + timeout
    latest = ""
    while time.monotonic() < deadline:
        try:
            latest = VISUAL_PROOF_LOG.read_text(encoding="utf-8")
        except OSError:
            time.sleep(0.05)
            continue
        if "PARENT WATCHDOG SUMMARY" in latest and "parent_run_id: %s" % run_id in latest:
            return latest
        time.sleep(0.05)
    return latest


def _valid_watchdog_tombstone(text, ready):
    required = (
        "PARENT WATCHDOG SUMMARY",
        "parent_run_id: %s" % ready["run_id"],
        "interruption_origin: python_parent_watchdog",
        "parent_pid: %d" % ready["godot_pid"],
        "parent_process_alive: false",
        "sidecar_pid: %d" % ready["sidecar_pid"],
        "host: %s" % ready["host"],
        "port: %d" % ready["port"],
        "active_connection_closed: true",
        "listener_closed_by_sidecar: true",
        "sidecar_exit_initiated: true",
        "FINAL RESULT: CANCELLED",
        "ERROR CODE: SIDECAR_PARENT_PROCESS_EXITED",
        "finished_at:",
    )
    return all(item in text for item in required) and "process_stopped:" not in text


def _listener_accepts(host, port):
    try:
        connection = socket.create_connection((host, port), timeout=0.25)
    except OSError:
        return False
    connection.close()
    return True


def _wait_for_listener_closed(host, port, timeout):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if not _listener_accepts(host, port):
            return True
        time.sleep(0.05)
    return not _listener_accepts(host, port)


def _required_file(path, label):
    candidate = Path(path).resolve()
    if not candidate.is_file():
        raise GodotParentDeathProofError(
            "PARENT_DEATH_EXECUTABLE_INVALID",
            "%s was not found." % label,
        )
    return candidate


def _confined_diagnostics_dir(path):
    candidate = Path(path).resolve()
    temp_root = REPOSITORY_TEMP_ROOT.resolve()
    try:
        candidate.relative_to(temp_root)
    except ValueError:
        raise GodotParentDeathProofError(
            "PARENT_DEATH_DIAGNOSTICS_OUTSIDE_TEMP",
            "Diagnostics directory must remain inside repository TEMP.",
        ) from None
    candidate.mkdir(parents=True, exist_ok=True)
    return candidate


def _utc_timestamp():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _build_parser():
    parser = argparse.ArgumentParser(description="Run the Godot sidecar parent-death proof.")
    parser.add_argument("--godot-executable", required=True)
    parser.add_argument("--python-executable", default=sys.executable)
    parser.add_argument("--diagnostics-dir", default=str(DEFAULT_DIAGNOSTICS_DIR))
    parser.add_argument("--runs", type=int, default=2)
    return parser


def main(argv=None):
    try:
        arguments = _build_parser().parse_args(argv)
        results = run_parent_death_proofs(
            arguments.godot_executable,
            python_executable=arguments.python_executable,
            diagnostics_dir=arguments.diagnostics_dir,
            runs=arguments.runs,
        )
    except GodotParentDeathProofError as exc:
        print("%s: %s" % (exc.code, exc.message), file=sys.stderr)
        return 2
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0 if all(result["success"] for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "DEFAULT_DIAGNOSTICS_DIR",
    "GODOT_PROJECT_DIR",
    "GodotParentDeathProofError",
    "VISUAL_PROOF_LOG",
    "main",
    "run_parent_death_proof",
    "run_parent_death_proofs",
]
