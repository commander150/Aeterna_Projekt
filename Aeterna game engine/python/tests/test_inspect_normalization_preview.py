import importlib.util
import json
import shutil
import tempfile
import uuid
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "tools"
    / "runtime_package"
    / "inspect_normalization_preview.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("inspect_normalization_preview", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestInspectNormalizationPreview(unittest.TestCase):
    def setUp(self):
        self.inspector = _load_module()
        self.temp_dir = Path(tempfile.gettempdir()) / ("aeterna_inspect_normalization_%s" % uuid.uuid4().hex)
        self.package_dir = self.temp_dir / "runtime_package"
        self.package_dir.mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.assertFalse(self.temp_dir.exists(), "Inspector test temp cleanup left directory: %s" % self.temp_dir)

    def test_valid_fixture_formats_summary_and_honors_limit(self):
        _write_reports(self.package_dir, preview_count=2, skipped_count=1)

        summary = self.inspector.inspect_package(self.package_dir, limit=1)
        text = self.inspector.format_inspection(summary)

        self.assertEqual(summary["summary"]["audit_matches_total"], 3)
        self.assertEqual(summary["summary"]["preview_items"], 2)
        self.assertEqual(summary["summary"]["skipped_requires_audit"], 1)
        self.assertEqual(summary["summary"]["applied"], 0)
        self.assertEqual(len(summary["safe_preview_examples"]), 1)
        self.assertEqual(len(summary["manual_audit_examples"]), 1)
        self.assertIn("AETERNA normalization preview inspector", text)
        self.assertIn("preview_items: 2", text)
        self.assertIn("SAFE PREVIEW EXAMPLES", text)
        self.assertIn("MANUAL AUDIT EXAMPLES", text)

    def test_main_returns_error_for_missing_report(self):
        stdout = StringIO()
        stderr = StringIO()

        with redirect_stdout(stdout), redirect_stderr(stderr):
            exit_code = self.inspector.main(["--package-dir", str(self.package_dir)])

        self.assertEqual(exit_code, 1)
        self.assertIn("missing report file", stderr.getvalue())
        self.assertEqual(stdout.getvalue(), "")

    def test_empty_reports_still_format_meaningful_summary(self):
        _write_reports(self.package_dir, preview_count=0, skipped_count=0)

        summary = self.inspector.inspect_package(self.package_dir, limit=20)
        text = self.inspector.format_inspection(summary)

        self.assertEqual(summary["summary"]["audit_matches_total"], 0)
        self.assertEqual(summary["summary"]["preview_items"], 0)
        self.assertEqual(summary["summary"]["skipped_requires_audit"], 0)
        self.assertIn("(none)", text)

    def test_main_success_reads_without_mutating_applied_values(self):
        _write_reports(self.package_dir, preview_count=1, skipped_count=1, applied_value=7)
        before = (self.package_dir / "normalization_preview_report.json").read_text(encoding="utf-8")
        stdout = StringIO()
        stderr = StringIO()

        with redirect_stdout(stdout), redirect_stderr(stderr):
            exit_code = self.inspector.main(["--package-dir", str(self.package_dir), "--limit", "5"])

        after = (self.package_dir / "normalization_preview_report.json").read_text(encoding="utf-8")
        self.assertEqual(exit_code, 0)
        self.assertIn("applied: 7", stdout.getvalue())
        self.assertEqual(stderr.getvalue(), "")
        self.assertEqual(before, after)


def _write_reports(package_dir, preview_count, skipped_count, applied_value=0):
    audit_rows = []
    preview_rows = []
    skipped_rows = []
    for index in range(preview_count):
        audit_rows.append(_audit_row(index, allowed=True))
        preview_rows.append(_preview_row(index, applied=False))
    for index in range(skipped_count):
        row_index = preview_count + index
        audit_rows.append(_audit_row(row_index, allowed=False))
        skipped_rows.append(_skipped_row(row_index))

    audit_report = {
        "normalization_audit": audit_rows,
        "summary": {
            "matches_total": len(audit_rows),
            "field_matches": {"duration": preview_count, "trigger": skipped_count},
            "lookup_group_matches": {"duration": preview_count, "trigger": skipped_count},
        },
    }
    preview_report = {
        "normalization_preview": preview_rows,
        "skipped": skipped_rows,
        "summary": {
            "audit_matches_total": len(audit_rows),
            "preview_items": preview_count,
            "skipped_requires_audit": skipped_count,
            "applied": applied_value,
            "field_preview_counts": {"duration": preview_count},
            "lookup_group_preview_counts": {"duration": preview_count},
        },
    }
    (package_dir / "normalization_audit_report.json").write_text(
        json.dumps(audit_report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (package_dir / "normalization_preview_report.json").write_text(
        json.dumps(preview_report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _audit_row(index, allowed):
    return {
        "object_type": "card",
        "object_id": "CARD-%03d" % index,
        "field": "duration" if allowed else "trigger",
        "lookup_group": "duration" if allowed else "trigger",
        "value": "until_turn_end" if allowed else "on_summon",
        "canonical_value": "until_end_of_turn" if allowed else "audit_required",
        "normalization_allowed": allowed,
        "requires_audit": not allowed,
        "applied": False,
    }


def _preview_row(index, applied):
    return {
        "object_type": "card",
        "object_id": "CARD-%03d" % index,
        "field": "duration",
        "lookup_group": "duration",
        "original_value": "until_turn_end; instant",
        "matched_value": "until_turn_end",
        "canonical_value": "until_end_of_turn",
        "preview_value": "until_end_of_turn; instant",
        "normalization_allowed": True,
        "requires_audit": False,
        "applied": applied,
        "preview_status": "safe_preview",
        "notes": "test fixture",
    }


def _skipped_row(index):
    return {
        "object_type": "card",
        "object_id": "CARD-%03d" % index,
        "field": "trigger",
        "matched_value": "on_summon",
        "canonical_value": "audit_required",
        "normalization_allowed": False,
        "requires_audit": True,
        "preview_status": "manual_audit_required",
        "applied": False,
    }


if __name__ == "__main__":
    unittest.main()
