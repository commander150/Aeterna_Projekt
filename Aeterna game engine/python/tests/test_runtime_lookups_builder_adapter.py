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
    / "runtime_lookups_builder_adapter.py"
)


def _load_adapter_module():
    spec = importlib.util.spec_from_file_location("runtime_lookups_builder_adapter", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestRuntimeLookupsBuilderAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = _load_adapter_module()
        self.temp_dir = Path(tempfile.gettempdir()) / ("runtime_lookups_builder_adapter_%s" % uuid.uuid4().hex)
        self.temp_dir.mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.assertFalse(self.temp_dir.exists(), "Lookup adapter temp cleanup left directory: %s" % self.temp_dir)

    def test_loads_runtime_lookup_rows(self):
        input_path = self.temp_dir / "LOOKUPS_RUNTIME.jsonl"
        _write_jsonl(
            input_path,
            [
                _lookup_row("Card_Type", "Entitás"),
                _lookup_row("Realm", "IGNIS"),
            ],
        )

        result = self.adapter.load_builder_lookups_from_runtime_lookups_jsonl(input_path)

        self.assertEqual(result["summary"]["records_read"], 2)
        self.assertEqual(result["summary"]["lookups_loaded"], 2)
        self.assertEqual(result["lookups"][0]["lookup_group"], "card_type")
        self.assertEqual(result["lookups"][0]["value"], "Entitás")
        self.assertEqual(result["lookups"][1]["lookup_group"], "realm")
        self.assertEqual(result["lookups"][1]["value"], "IGNIS")
        self.assertEqual(result["lookups"][0]["used_for"], ["runtime_validation"])


def _lookup_row(group, value):
    return {
        "Lookup_Group": group,
        "Value": value,
        "Label_HU": value,
        "Status": "active",
        "Canonical_Value": value,
        "Used_For": "runtime_validation",
        "Sort_Order": 10,
        "Source": "test",
        "Notes": "temporary test fixture",
    }


def _write_jsonl(path, records):
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    unittest.main()
