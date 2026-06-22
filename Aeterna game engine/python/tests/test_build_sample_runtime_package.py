import importlib.util
import json
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "tools" / "runtime_package" / "build_sample_runtime_package.py"


def _load_builder_module():
    spec = importlib.util.spec_from_file_location("build_sample_runtime_package", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestBuildSampleRuntimePackage(unittest.TestCase):
    def test_build_sample_runtime_package_smoke(self):
        builder = _load_builder_module()

        output_dir = Path.cwd() / "sample_runtime_package"
        result = builder.build_package(output_dir)

        self.assertEqual(result["output_dir"], output_dir)
        self.assertTrue(output_dir.is_dir())

        expected_files = {
            "manifest.json",
            "cards.jsonl",
            "decks.jsonl",
            "lookups.json",
            "aliases.json",
            "ability_registry.json",
            "engine_support.json",
            "diagnostics.json",
            "build_report.md",
        }
        self.assertEqual({path.name for path in output_dir.iterdir()}, expected_files)

        manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
        manifest_files = {item["path"] for item in manifest["files"]}
        self.assertEqual(manifest_files, expected_files)
        self.assertFalse(manifest["validation_summary"]["blocking"])

        cards = [
            json.loads(line)
            for line in (output_dir / "cards.jsonl").read_text(encoding="utf-8").splitlines()
            if line
        ]
        decks = [
            json.loads(line)
            for line in (output_dir / "decks.jsonl").read_text(encoding="utf-8").splitlines()
            if line
        ]

        self.assertGreaterEqual(len(cards), 5)
        self.assertGreaterEqual(len(decks), 1)
        self.assertTrue(all(isinstance(card["magnitude"], int) for card in cards))
        self.assertTrue(all(isinstance(card["keywords"], list) for card in cards))

        card_ids = {card["card_id"] for card in cards}
        for deck in decks:
            for entry in deck["card_entries"]:
                self.assertIn(entry["card_id"], card_ids)

        report = (output_dir / "build_report.md").read_text(encoding="utf-8")
        self.assertIn("Kartyak szama: 5", report)
        self.assertIn("Paklik szama: 1", report)
        self.assertIn("Warningok szama: 1", report)
        self.assertIn("Blocking hibak szama: 0", report)


if __name__ == "__main__":
    unittest.main()
