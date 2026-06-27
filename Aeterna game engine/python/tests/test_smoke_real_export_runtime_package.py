import importlib.util
import json
import shutil
import sys
import tempfile
import uuid
import unittest
from pathlib import Path

from openpyxl import Workbook


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "tools"
    / "runtime_package"
    / "smoke_real_export_runtime_package.py"
)
MAPPER_PATH = (
    Path(__file__).resolve().parents[1]
    / "tools"
    / "runtime_package"
    / "runtime_card_mapper.py"
)
BUILDER_PATH = (
    Path(__file__).resolve().parents[1]
    / "tools"
    / "runtime_package"
    / "build_sample_runtime_package.py"
)
ENGINE_PYTHON_DIR = Path(__file__).resolve().parents[1]


def _load_module(module_name, path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class TestSmokeRealExportRuntimePackage(unittest.TestCase):
    def setUp(self):
        self.runner = _load_module("smoke_real_export_runtime_package", SCRIPT_PATH)
        self.mapper = _load_module("runtime_card_mapper", MAPPER_PATH)
        self.builder = _load_module("build_sample_runtime_package", BUILDER_PATH)
        self.temp_dir = Path(tempfile.gettempdir()) / ("real_export_runtime_package_smoke_%s" % uuid.uuid4().hex)
        self.temp_dir.mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.assertFalse(self.temp_dir.exists(), "Real export smoke temp cleanup left directory: %s" % self.temp_dir)

    def test_smoke_runner_builds_partial_package_from_xlsx(self):
        xlsx_path = self.temp_dir / "aeterna_cards.xlsx"
        output_dir = self.temp_dir / "smoke_output"
        _write_runtime_cards_workbook(xlsx_path, self.builder._sample_cards(), self.mapper.FIELD_MAP)

        summary = self.runner.run_smoke(xlsx_path=xlsx_path, output_dir=output_dir)

        self.assertEqual(summary["exported_card_rows"], 5)
        self.assertTrue(summary["export_runtime_jsonl_exists"])
        self.assertTrue(summary["cards_jsonl_exists"])
        self.assertTrue(summary["manifest_exists"])
        self.assertTrue(summary["diagnostics_exists"])
        self.assertFalse(summary["validation_blocking"])
        self.assertEqual(summary["deck_reference_errors"], 0)
        self.assertEqual(summary["cards_source"], "export-derived")
        self.assertIn("decks", summary["fixture_components"])
        self.assertTrue((output_dir / "exports" / "EXPORT_RUNTIME.jsonl").is_file())
        self.assertTrue((output_dir / "runtime_package" / "cards.jsonl").is_file())

        manifest = json.loads((output_dir / "runtime_package" / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["source_files"][1]["type"], "export_runtime_cards_jsonl")


def _write_runtime_cards_workbook(path, sample_cards, field_map):
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "7. EXPORT_RUNTIME"

    headers = list(field_map.keys())
    for extra_header in ("Set_ID", "Collector_Number"):
        if extra_header not in headers:
            headers.append(extra_header)
    worksheet.append(headers)

    for index, card in enumerate(sample_cards, start=1):
        values_by_target = {
            "card_id": card["card_id"],
            "name_hu": card["name_hu"],
            "card_type": card["card_type"],
            "realm": card["realm"],
            "clan": card["clan"],
            "species": "none",
            "class": "none",
            "magnitude": card["magnitude"],
            "aura_cost": card["aura_cost"],
            "atk": card["atk"],
            "hp": card["hp"],
            "text_hu": "Sample XLSX ability text.",
            "structured_ability": "sample_module()",
            "recognized_zone": "none",
            "keywords": ";".join(card["keywords"]),
            "trigger": "none",
            "target": "none",
            "effect_tags": "sample",
            "duration": "none",
            "condition": "none",
            "machine_description": "Sample XLSX machine text.",
            "interpretation_status": card["interpretation_status"],
            "engine_notes": "Real export runtime package smoke.",
        }
        row = []
        for header in headers:
            if header == "Set_ID":
                row.append("SAMPLE")
            elif header == "Collector_Number":
                row.append(index)
            else:
                row.append(values_by_target[field_map[header]])
        worksheet.append(row)

    workbook.save(path)
    workbook.close()


if __name__ == "__main__":
    unittest.main()
