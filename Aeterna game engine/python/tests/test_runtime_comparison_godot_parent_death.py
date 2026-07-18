import os
import sys
import unittest
from pathlib import Path

from tools.runtime_comparison.godot_sidecar_parent_death_proof import (
    DEFAULT_DIAGNOSTICS_DIR,
    _parse_ready_log,
    run_parent_death_proofs,
)


GODOT_EXECUTABLE = os.environ.get("AETERNA_GODOT_EXECUTABLE", "")


class TestGodotParentDeathProofHelpers(unittest.TestCase):
    def test_ready_log_parser_reads_stable_runtime_identity(self):
        text = """AETERNA GODOT VISUAL PYTHON SIDECAR PROOF LOG
run_id: visual-proof-100-1-99
godot_pid: 100
CANCELLATION TEST READY
run_id: visual-proof-100-1-99
READY FOR F8 CANCELLATION TEST
PRESS F8 NOW
sidecar_pid: 200
host: 127.0.0.1
port: 54321
"""
        self.assertEqual(
            _parse_ready_log(text),
            {
                "run_id": "visual-proof-100-1-99",
                "godot_pid": 100,
                "sidecar_pid": 200,
                "host": "127.0.0.1",
                "port": 54321,
            },
        )


@unittest.skipUnless(
    sys.platform == "win32" and GODOT_EXECUTABLE and Path(GODOT_EXECUTABLE).is_file(),
    "Set AETERNA_GODOT_EXECUTABLE for the external Godot parent-death proof.",
)
class TestRuntimeComparisonGodotParentDeath(unittest.TestCase):
    def test_two_external_parent_death_runs_leave_no_orphan(self):
        results = run_parent_death_proofs(
            GODOT_EXECUTABLE,
            diagnostics_dir=DEFAULT_DIAGNOSTICS_DIR / "python_integration",
            runs=2,
        )

        self.assertEqual(len(results), 2)
        for result in results:
            with self.subTest(run=result["run_label"]):
                self.assertTrue(result["success"], result)
                self.assertTrue(result["sidecar_stopped_automatically"])
                self.assertLessEqual(result["sidecar_stop_seconds"], 5.0)
                self.assertTrue(result["listener_closed"])
                self.assertTrue(result["watchdog_tombstone_present"])
                self.assertFalse(result["fallback_cleanup_used"])
                self.assertTrue(result["godot_stderr_empty"])
                self.assertFalse(result["godot_warning_or_error"])


if __name__ == "__main__":
    unittest.main()
