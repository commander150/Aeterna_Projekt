import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "tools" / "runtime_package" / "runtime_card_mapper.py"
ENGINE_PYTHON_DIR = Path(__file__).resolve().parents[1]


def _load_mapper_module():
    spec = importlib.util.spec_from_file_location("runtime_card_mapper", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sample_export_record():
    return {
        "Card_ID": "CARD-001",
        "Kártya név": "Parázsőrző Entitás",
        "Típus": "Entitás",
        "Birodalom": "Ignis",
        "Klán": "Hamvaskéz",
        "Faj": "Elementál",
        "Kaszt": "Őrző",
        "Magnitudó": 1.0,
        "Aura": "2.0",
        "ATK": 3.0,
        "HP": "4",
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
        "Engine_Megjegyzés": "Ready for mapping smoke.",
    }


class TestRuntimeCardMapper(unittest.TestCase):
    def setUp(self):
        self.mapper = _load_mapper_module()

    def test_maps_basic_export_record_to_runtime_card(self):
        result = self.mapper.map_export_runtime_card(_sample_export_record())

        self.assertEqual(result["card_id"], "CARD-001")
        self.assertEqual(result["name_hu"], "Parázsőrző Entitás")
        self.assertEqual(result["card_type"], "Entitás")
        self.assertEqual(result["realm"], "Ignis")
        self.assertEqual(result["clan"], "Hamvaskéz")
        self.assertEqual(result["species"], "Elementál")
        self.assertEqual(result["class"], "Őrző")
        self.assertEqual(result["text_hu"], "Sebez 1-et.")
        self.assertEqual(result["structured_ability"], "damage(amount=1)")
        self.assertEqual(result["recognized_zone"], "board")
        self.assertEqual(result["trigger"], "on_play")
        self.assertEqual(result["target"], "enemy_entity")
        self.assertEqual(result["duration"], "instant")
        self.assertEqual(result["condition"], "none")
        self.assertEqual(result["machine_description"], "Sample machine text.")
        self.assertEqual(result["interpretation_status"], "structured")
        self.assertEqual(result["engine_notes"], "Ready for mapping smoke.")
        self.assertEqual(result["mapping_status"], "ok")
        self.assertEqual(result["diagnostics"], [])

    def test_numeric_fields_keep_integer_values(self):
        result = self.mapper.map_export_runtime_card(_sample_export_record())

        self.assertEqual(result["magnitude"], 1)
        self.assertIsInstance(result["magnitude"], int)
        self.assertEqual(result["aura_cost"], 2)
        self.assertIsInstance(result["aura_cost"], int)
        self.assertEqual(result["atk"], 3)
        self.assertIsInstance(result["atk"], int)
        self.assertEqual(result["hp"], 4)
        self.assertIsInstance(result["hp"], int)

    def test_keywords_and_effect_tags_are_lists(self):
        result = self.mapper.map_export_runtime_card(_sample_export_record())

        self.assertEqual(result["keywords"], ["őrző", "reakció"])
        self.assertEqual(result["effect_tags"], ["damage", "fire"])

    def test_missing_card_id_returns_error_diagnostic(self):
        record = _sample_export_record()
        record["Card_ID"] = ""

        result = self.mapper.map_export_runtime_card(record)

        self.assertEqual(result["mapping_status"], "error")
        self.assertEqual(result["card_id"], "none")
        self.assertEqual(result["diagnostics"][0]["code"], "MISSING_REQUIRED_FIELD")
        self.assertEqual(result["diagnostics"][0]["source_field"], "Card_ID")
        self.assertTrue(result["diagnostics"][0]["blocking"])

    def test_missing_optional_field_does_not_fail_mapping(self):
        record = _sample_export_record()
        del record["Klán"]
        record["Kulcsszavak_Felismerve"] = None

        result = self.mapper.map_export_runtime_card(record)

        self.assertEqual(result["mapping_status"], "ok")
        self.assertEqual(result["clan"], "none")
        self.assertEqual(result["keywords"], [])
        self.assertEqual(result["diagnostics"], [])

    def test_mapper_does_not_create_persistent_repo_output(self):
        before = _repo_output_snapshot()

        self.mapper.map_export_runtime_card(_sample_export_record())

        after = _repo_output_snapshot()
        self.assertEqual(after, before)


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
