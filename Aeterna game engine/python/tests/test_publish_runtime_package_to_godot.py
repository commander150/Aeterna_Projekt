import importlib.util
import sys
import uuid
import unittest
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "tools"
    / "runtime_package"
    / "publish_runtime_package_to_godot.py"
)
PROJECT_ROOT = Path(__file__).resolve().parents[3]
PROJECT_TEMP = PROJECT_ROOT / "TEMP"


def _load_module(module_name, path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class TestPublishRuntimePackageToGodot(unittest.TestCase):
    def setUp(self):
        self.publisher = _load_module("publish_runtime_package_to_godot", SCRIPT_PATH)
        self.temp_root = PROJECT_TEMP / ("publish_runtime_package_test_%s" % uuid.uuid4().hex)
        self.temp_output_dir = self.temp_root / "candidate"
        self.godot_package_dir = self.temp_root / "godot_package"
        self.temp_root.mkdir(parents=True)
        self.original_runner = self.publisher.SMOKE_RUNNER
        self.original_validate_candidate = self.publisher.validate_candidate
        self.original_copy2 = self.publisher.shutil.copy2
        self.copied_files = []

    def tearDown(self):
        self.publisher.SMOKE_RUNNER = self.original_runner
        self.publisher.validate_candidate = self.original_validate_candidate
        self.publisher.shutil.copy2 = self.original_copy2

    def test_invalid_validation_blocks_publish(self):
        self.publisher.SMOKE_RUNNER = _StubSmokeRunner()
        self.publisher.validate_candidate = lambda _summary, _candidate: ["diagnostic_count must be 0"]
        self.publisher.shutil.copy2 = self._record_copy

        with self.assertRaises(self.publisher.PublishError):
            self.publisher.publish_runtime_package(
                xlsx_path=self.temp_root / "source.xlsx",
                lookups_xlsx_path=self.temp_root / "LOOKUPS.xlsx",
                temp_output_dir=self.temp_output_dir,
                godot_package_dir=self.godot_package_dir,
            )

        self.assertEqual(self.copied_files, [])

    def test_successful_validation_copies_only_package_files(self):
        self.publisher.SMOKE_RUNNER = _StubSmokeRunner()
        self.publisher.validate_candidate = lambda _summary, _candidate: []
        self.publisher.shutil.copy2 = self._record_copy

        summary = self.publisher.publish_runtime_package(
            xlsx_path=self.temp_root / "source.xlsx",
            lookups_xlsx_path=self.temp_root / "LOOKUPS.xlsx",
            temp_output_dir=self.temp_output_dir,
            godot_package_dir=self.godot_package_dir,
        )

        self.assertTrue(summary["published"])
        self.assertFalse(summary["dry_run"])
        self.assertEqual(summary["copied_files"], self.publisher.PACKAGE_FILES)
        self.assertEqual([source for source, _target in self.copied_files], self.publisher.PACKAGE_FILES)
        self.assertEqual([target for _source, target in self.copied_files], self.publisher.PACKAGE_FILES)

    def test_dry_run_validates_without_copying(self):
        self.publisher.SMOKE_RUNNER = _StubSmokeRunner()
        self.publisher.validate_candidate = lambda _summary, _candidate: []
        self.publisher.shutil.copy2 = self._record_copy

        summary = self.publisher.publish_runtime_package(
            xlsx_path=self.temp_root / "source.xlsx",
            lookups_xlsx_path=self.temp_root / "LOOKUPS.xlsx",
            temp_output_dir=self.temp_output_dir,
            godot_package_dir=self.godot_package_dir,
            dry_run=True,
        )

        self.assertFalse(summary["published"])
        self.assertTrue(summary["dry_run"])
        self.assertEqual(summary["lookups_xlsx_path"], str(self.temp_root / "LOOKUPS.xlsx"))
        self.assertEqual(summary["lookups_source"], "LOOKUPS.xlsx:RUNTIME_CORE+RUNTIME_ABILITY")
        self.assertEqual(summary["normalization_aliases_source"], "LOOKUPS.xlsx:RUNTIME_LEGACY_ALIAS")
        self.assertEqual(summary["normalization_aliases_count"], 2)
        self.assertEqual(summary["normalization_aliases_requires_audit_count"], 1)
        self.assertEqual(summary["normalization_aliases_allowed_count"], 1)
        self.assertEqual(summary["normalization_audit_matches"], 3)
        self.assertEqual(summary["normalization_audit_requires_audit"], 1)
        self.assertEqual(summary["normalization_audit_allowed"], 2)
        self.assertEqual(summary["would_copy_files"], self.publisher.PACKAGE_FILES)
        self.assertIn("normalization_audit_report.json", summary["would_copy_files"])
        self.assertEqual(self.copied_files, [])

    def test_existing_candidate_output_uses_fresh_candidate_dir(self):
        existing_output = self.temp_output_dir / "exports" / "EXPORT_RUNTIME.jsonl"
        existing_output.parent.mkdir(parents=True)
        existing_output.write_text("old\n", encoding="utf-8")
        self.publisher.SMOKE_RUNNER = _StubSmokeRunner()
        self.publisher.validate_candidate = lambda _summary, _candidate: []

        summary = self.publisher.publish_runtime_package(
            xlsx_path=self.temp_root / "source.xlsx",
            lookups_xlsx_path=self.temp_root / "LOOKUPS.xlsx",
            temp_output_dir=self.temp_output_dir,
            godot_package_dir=self.godot_package_dir,
            dry_run=True,
        )

        self.assertTrue(summary["dry_run"])
        self.assertTrue(existing_output.exists())
        candidate_dir = Path(summary["candidate_package_dir"]).parent
        self.assertNotEqual(candidate_dir, self.temp_output_dir)
        self.assertTrue(candidate_dir.name.startswith(self.temp_output_dir.name + "_"))

    def _record_copy(self, source, target):
        self.copied_files.append((Path(source).name, Path(target).name))


class _StubSmokeRunner:
    def run_smoke(
        self,
        xlsx_path,
        output_dir,
        include_decklists,
        include_lookups_runtime,
        lookups_xlsx_path=None,
    ):
        return {
            "xlsx_path": str(xlsx_path),
            "lookups_xlsx_path": str(lookups_xlsx_path),
            "runtime_package_output_dir": str(Path(output_dir) / "runtime_package"),
            "cards_jsonl_rows": 2,
            "decks_source": "export-derived",
            "lookups_source": "LOOKUPS.xlsx:RUNTIME_CORE+RUNTIME_ABILITY",
            "normalization_aliases_source": "LOOKUPS.xlsx:RUNTIME_LEGACY_ALIAS",
            "normalization_aliases_count": 2,
            "normalization_aliases_requires_audit_count": 1,
            "normalization_aliases_allowed_count": 1,
            "normalization_audit_matches": 3,
            "normalization_audit_requires_audit": 1,
            "normalization_audit_allowed": 2,
            "validation_blocking": False,
            "diagnostic_count": 0,
            "deck_reference_errors": 0,
            "unknown_realm_errors": 0,
            "unknown_card_type_errors": 0,
        }
if __name__ == "__main__":
    unittest.main()
