import importlib.util
import json
import shutil
import tempfile
import uuid
import unittest
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "tools"
    / "runtime_package"
    / "runtime_cards_jsonl_converter.py"
)
ENGINE_PYTHON_DIR = Path(__file__).resolve().parents[1]


def _load_converter_module():
    spec = importlib.util.spec_from_file_location("runtime_cards_jsonl_converter", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sample_export_record(card_id="CARD-001"):
    return {
        "Card_ID": card_id,
        "Kártya név": "Parázsőrző Entitás",
        "Típus": "Entitás",
        "Birodalom": "Ignis",
        "Klán": "Hamvaskéz",
        "Faj": "Elementál",
        "Kaszt": "Őrző",
        "Magnitudó": 1.0,
        "Aura": 2.0,
        "ATK": 3.0,
        "HP": 4.0,
        "Képesség": "Sebez 1-et.",
        "Képesség_Canonical": "damage(amount=1)",
        "Zóna_Felismerve": "board",
        "Kulcsszavak_Felismerve": "őrző; reakció",
        "Trigger_Felismerve": "on_play",
        "Célpont_Felismerve": "enemy_entity",
        "Hatáscímkék": "damage; fire",
        "Időtartam_Felismerve": "instant",
        "Feltétel_Felismerve": "none",
        "Gépi_Leírás": "Sample machine text.",
        "Értelmezési_Státusz": "structured",
        "Engine_Megjegyzés": "Ready for converter smoke.",
    }


class TestRuntimeCardsJsonlConverter(unittest.TestCase):
    def setUp(self):
        self.converter = _load_converter_module()
        self.temp_dir = Path(tempfile.gettempdir()) / ("runtime_cards_jsonl_converter_%s" % uuid.uuid4().hex)
        self.temp_dir.mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.assertFalse(self.temp_dir.exists(), "Converter temp cleanup left directory: %s" % self.temp_dir)

    def test_converts_two_valid_export_records(self):
        input_path = self.temp_dir / "EXPORT_RUNTIME.jsonl"
        output_path = self.temp_dir / "cards.jsonl"
        _write_jsonl(input_path, [_sample_export_record("CARD-001"), _sample_export_record("CARD-002")])

        summary = self.converter.convert_export_runtime_jsonl_to_cards_jsonl(input_path, output_path)

        self.assertEqual(summary["records_read"], 2)
        self.assertEqual(summary["records_written"], 2)
        self.assertEqual(summary["ok_count"], 2)
        self.assertEqual(summary["error_count"], 0)
        rows = _read_jsonl(output_path)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["card_id"], "CARD-001")
        self.assertEqual(rows[1]["card_id"], "CARD-002")
        self.assertEqual(rows[0]["mapping_status"], "ok")

    def test_summary_counts_valid_records(self):
        input_path = self.temp_dir / "EXPORT_RUNTIME.jsonl"
        output_path = self.temp_dir / "cards.jsonl"
        _write_jsonl(input_path, [_sample_export_record("CARD-001")])

        summary = self.converter.convert_export_runtime_jsonl_to_cards_jsonl(input_path, output_path)

        self.assertEqual(
            {
                "records_read": summary["records_read"],
                "records_written": summary["records_written"],
                "ok_count": summary["ok_count"],
                "error_count": summary["error_count"],
            },
            {"records_read": 1, "records_written": 1, "ok_count": 1, "error_count": 0},
        )

    def test_mapping_error_is_written_in_non_strict_mode(self):
        input_path = self.temp_dir / "EXPORT_RUNTIME.jsonl"
        output_path = self.temp_dir / "cards.jsonl"
        record = _sample_export_record("")
        _write_jsonl(input_path, [record])

        summary = self.converter.convert_export_runtime_jsonl_to_cards_jsonl(input_path, output_path, strict=False)

        self.assertEqual(summary["records_read"], 1)
        self.assertEqual(summary["records_written"], 1)
        self.assertEqual(summary["ok_count"], 0)
        self.assertEqual(summary["error_count"], 1)
        self.assertEqual(summary["diagnostics"][0]["code"], "MAPPING_ERROR")
        rows = _read_jsonl(output_path)
        self.assertEqual(rows[0]["mapping_status"], "error")
        self.assertEqual(rows[0]["card_id"], "none")

    def test_mapping_error_does_not_write_output_in_strict_mode(self):
        input_path = self.temp_dir / "EXPORT_RUNTIME.jsonl"
        output_path = self.temp_dir / "cards.jsonl"
        record = _sample_export_record("")
        _write_jsonl(input_path, [record])

        summary = self.converter.convert_export_runtime_jsonl_to_cards_jsonl(input_path, output_path, strict=True)

        self.assertEqual(summary["records_read"], 1)
        self.assertEqual(summary["records_written"], 0)
        self.assertEqual(summary["error_count"], 1)
        self.assertFalse(output_path.exists())

    def test_invalid_json_adds_diagnostic(self):
        input_path = self.temp_dir / "EXPORT_RUNTIME.jsonl"
        output_path = self.temp_dir / "cards.jsonl"
        input_path.write_text('{"Card_ID": "BROKEN"\n', encoding="utf-8")

        summary = self.converter.convert_export_runtime_jsonl_to_cards_jsonl(input_path, output_path)

        self.assertEqual(summary["records_read"], 0)
        self.assertEqual(summary["records_written"], 0)
        self.assertEqual(summary["error_count"], 1)
        self.assertEqual(summary["diagnostics"][0]["code"], "INVALID_JSON")
        self.assertTrue(output_path.exists())
        self.assertEqual(output_path.read_text(encoding="utf-8"), "")

    def test_converter_does_not_create_persistent_repo_output(self):
        before = _repo_output_snapshot()
        input_path = self.temp_dir / "EXPORT_RUNTIME.jsonl"
        output_path = self.temp_dir / "cards.jsonl"
        _write_jsonl(input_path, [_sample_export_record("CARD-001")])

        self.converter.convert_export_runtime_jsonl_to_cards_jsonl(input_path, output_path)

        after = _repo_output_snapshot()
        self.assertEqual(after, before)


def _write_jsonl(path, records):
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")


def _read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _repo_output_snapshot():
    watched_paths = [
        ENGINE_PYTHON_DIR / "exports",
        ENGINE_PYTHON_DIR / "fixture_runtime_package",
    ]
    snapshot = {}
    for path in watched_paths:
        if path.exists():
            snapshot[str(path)] = sorted(str(item.relative_to(path)) for item in path.rglob("*") if item.is_file())
        else:
            snapshot[str(path)] = []
    return snapshot


if __name__ == "__main__":
    unittest.main()
