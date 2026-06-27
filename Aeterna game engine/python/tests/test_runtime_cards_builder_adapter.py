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
    / "runtime_cards_builder_adapter.py"
)
MAPPER_PATH = (
    Path(__file__).resolve().parents[1]
    / "tools"
    / "runtime_package"
    / "runtime_card_mapper.py"
)
ENGINE_PYTHON_DIR = Path(__file__).resolve().parents[1]


def _load_adapter_module():
    spec = importlib.util.spec_from_file_location("runtime_cards_builder_adapter", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_mapper_module():
    spec = importlib.util.spec_from_file_location("runtime_card_mapper", MAPPER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sample_export_record(card_id="CARD-001"):
    mapper = _load_mapper_module()
    values_by_target = {
        "card_id": card_id,
        "name_hu": "Sample Entity",
        "card_type": "Entitas",
        "realm": "Ignis",
        "clan": "Sample Clan",
        "species": "Elemental",
        "class": "Guardian",
        "magnitude": 1.0,
        "aura_cost": 2.0,
        "atk": 3.0,
        "hp": 4.0,
        "text_hu": "Sample ability text.",
        "structured_ability": "damage(amount=1)",
        "recognized_zone": "board",
        "keywords": "guardian; reaction",
        "trigger": "on_play",
        "target": "enemy_entity",
        "effect_tags": "damage; fire",
        "duration": "instant",
        "condition": "none",
        "machine_description": "Sample machine text.",
        "interpretation_status": "structured",
        "engine_notes": "Ready for builder adapter smoke.",
    }
    return {
        source_field: values_by_target[target_field]
        for source_field, target_field in mapper.FIELD_MAP.items()
    }


class TestRuntimeCardsBuilderAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = _load_adapter_module()
        self.temp_dir = Path(tempfile.gettempdir()) / ("runtime_cards_builder_adapter_%s" % uuid.uuid4().hex)
        self.temp_dir.mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.assertFalse(self.temp_dir.exists(), "Builder adapter temp cleanup left directory: %s" % self.temp_dir)

    def test_loads_temporary_export_runtime_fixture(self):
        input_path = self.temp_dir / "EXPORT_RUNTIME.jsonl"
        _write_jsonl(input_path, [_sample_export_record("CARD-001")])

        result = self.adapter.load_builder_cards_from_export_runtime_jsonl(input_path)

        self.assertEqual(result["summary"]["records_read"], 1)
        self.assertEqual(result["summary"]["records_loaded"], 1)
        self.assertEqual(len(result["cards"]), 1)
        self.assertEqual(result["cards"][0]["card_id"], "CARD-001")

    def test_builder_required_fields_are_present(self):
        input_path = self.temp_dir / "EXPORT_RUNTIME.jsonl"
        _write_jsonl(input_path, [_sample_export_record("CARD-001"), _sample_export_record("CARD-002")])

        result = self.adapter.load_builder_cards_from_export_runtime_jsonl(input_path)

        for card in result["cards"]:
            self.assertIn("runtime_status", card)
            self.assertIn("engine_support_status", card)
            self.assertEqual(card["runtime_status"], "mapped_from_export")
            self.assertEqual(card["engine_support_status"], "not_evaluated")

    def test_output_remains_jsonl_compatible_dict_list(self):
        input_path = self.temp_dir / "EXPORT_RUNTIME.jsonl"
        _write_jsonl(input_path, [_sample_export_record("CARD-001")])

        result = self.adapter.load_builder_cards_from_export_runtime_jsonl(input_path)

        self.assertIsInstance(result["cards"], list)
        self.assertIsInstance(result["cards"][0], dict)
        json.dumps(result["cards"][0], ensure_ascii=False, separators=(",", ":"))

    def test_does_not_write_to_sample_runtime_package(self):
        before = _sample_runtime_package_snapshot()
        input_path = self.temp_dir / "EXPORT_RUNTIME.jsonl"
        _write_jsonl(input_path, [_sample_export_record("CARD-001")])

        self.adapter.load_builder_cards_from_export_runtime_jsonl(input_path)

        after = _sample_runtime_package_snapshot()
        self.assertEqual(after, before)


def _write_jsonl(path, records):
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")


def _sample_runtime_package_snapshot():
    path = ENGINE_PYTHON_DIR / "sample_runtime_package"
    if not path.exists():
        return []
    return sorted(str(item.relative_to(path)) for item in path.rglob("*") if item.is_file())


if __name__ == "__main__":
    unittest.main()
