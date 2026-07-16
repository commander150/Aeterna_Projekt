import hashlib
import json
import math
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from tools.runtime_comparison import canonical_json


class TestRuntimeComparisonCanonicalJson(unittest.TestCase):
    def test_json_bytes_are_stable_sorted_utf8_lf_and_type_preserving(self):
        first = {
            "z": [3, 1, 2],
            "integer": 7,
            "none": None,
            "boolean_true": True,
            "boolean_false": False,
            "accented": "\u00e1rv\u00edzt\u0171r\u0151 t\u00fck\u00f6rf\u00far\u00f3g\u00e9p",
            "nested": {"z": "utolso", "a": "elso"},
        }
        second = {key: first[key] for key in reversed(list(first))}
        original = deepcopy(first)

        first_bytes = canonical_json.canonical_json_bytes(first)
        second_bytes = canonical_json.canonical_json_bytes(second)

        self.assertEqual(first_bytes, second_bytes)
        self.assertFalse(first_bytes.startswith(b"\xef\xbb\xbf"))
        self.assertNotIn(b"\r", first_bytes)
        self.assertTrue(first_bytes.endswith(b"\n"))
        self.assertFalse(first_bytes.endswith(b"\n\n"))
        self.assertIn(b'  "accented":', first_bytes)
        decoded = json.loads(first_bytes.decode("utf-8"))
        self.assertEqual(decoded["z"], [3, 1, 2])
        self.assertEqual(decoded["integer"], 7)
        self.assertIs(type(decoded["integer"]), int)
        self.assertIsNone(decoded["none"])
        self.assertIs(decoded["boolean_true"], True)
        self.assertIs(decoded["boolean_false"], False)
        self.assertEqual(first, original)
        self.assertEqual(canonical_json.canonical_json_text(first).encode("utf-8"), first_bytes)

    def test_json_preserves_non_ascii_utf8_without_escape_conversion(self):
        value = {"label_hu": "\u00e1rv\u00edzt\u0171r\u0151 t\u00fck\u00f6rf\u00far\u00f3g\u00e9p"}

        output = canonical_json.canonical_json_bytes(value)

        self.assertEqual(json.loads(output.decode("utf-8")), value)
        self.assertNotIn(b"\\u", output)

    def test_nan_and_infinity_are_rejected(self):
        for invalid in (math.nan, math.inf, -math.inf):
            with self.subTest(invalid=invalid):
                with self.assertRaises(canonical_json.CanonicalJsonError):
                    canonical_json.canonical_json_bytes({"value": invalid})
                with self.assertRaises(canonical_json.CanonicalJsonError):
                    canonical_json.canonical_jsonl_bytes([{"value": invalid}])

    def test_jsonl_uses_one_compact_sorted_object_per_lf_terminated_line(self):
        records = [
            {"z": 2, "a": ["second", "first"]},
            {"message": "masodik", "enabled": True},
        ]
        original = deepcopy(records)

        output = canonical_json.canonical_jsonl_bytes(records)
        lines = output.decode("utf-8").splitlines()

        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0], '{"a":["second","first"],"z":2}')
        self.assertEqual(json.loads(lines[1]), records[1])
        self.assertNotIn("\r", output.decode("utf-8"))
        self.assertTrue(output.endswith(b"\n"))
        self.assertFalse(output.endswith(b"\n\n"))
        self.assertEqual(records, original)
        self.assertEqual(canonical_json.canonical_jsonl_bytes([]), b"")

    def test_jsonl_rejects_non_object_records(self):
        with self.assertRaisesRegex(canonical_json.CanonicalJsonError, "must be an object"):
            canonical_json.canonical_jsonl_bytes([{"ok": True}, ["not", "an", "object"]])

    def test_file_writers_match_bytes_and_do_not_partially_write_invalid_input(self):
        payload = {"b": 2, "a": "value"}
        records = [{"b": 2, "a": 1}, {"id": "second"}]
        with tempfile.TemporaryDirectory() as temp_dir:
            json_path = Path(temp_dir) / "state.json"
            jsonl_path = Path(temp_dir) / "events.jsonl"
            invalid_path = Path(temp_dir) / "unchanged.json"
            invalid_path.write_bytes(b"sentinel")

            returned_json_path = canonical_json.write_canonical_json(json_path, payload)
            returned_jsonl_path = canonical_json.write_canonical_jsonl(jsonl_path, records)

            self.assertEqual(returned_json_path, json_path)
            self.assertEqual(returned_jsonl_path, jsonl_path)
            self.assertEqual(json_path.read_bytes(), canonical_json.canonical_json_bytes(payload))
            self.assertEqual(jsonl_path.read_bytes(), canonical_json.canonical_jsonl_bytes(records))
            with self.assertRaises(canonical_json.CanonicalJsonError):
                canonical_json.write_canonical_json(invalid_path, {"value": math.nan})
            self.assertEqual(invalid_path.read_bytes(), b"sentinel")

    def test_sha256_uses_exact_bytes_and_binary_file_content(self):
        payload = {"message": "deterministic", "values": [3, 2, 1]}
        output = canonical_json.canonical_json_bytes(payload)
        expected = hashlib.sha256(output).hexdigest()

        self.assertEqual(canonical_json.sha256_bytes(output), expected)
        self.assertRegex(expected, r"^[0-9a-f]{64}$")
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "canonical.json"
            path.write_bytes(output)
            self.assertEqual(canonical_json.sha256_file(path), expected)

        with self.assertRaises(TypeError):
            canonical_json.sha256_bytes("not bytes")


if __name__ == "__main__":
    unittest.main()
