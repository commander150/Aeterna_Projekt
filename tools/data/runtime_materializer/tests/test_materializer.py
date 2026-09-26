from __future__ import annotations

import hashlib
import json
import shutil
import unittest
import uuid
from pathlib import Path
from unittest import mock

from tools.data.canonical_producer import build_candidate, default_config
from tools.data.runtime_materializer import MaterializationError, compute_runtime_package_id, materialize
from tools.data.runtime_materializer.materializer import (
    _candidate_blocker_diagnostics,
    _derive_readiness,
    _runtime_value_for,
    _tree_hashes,
    _validate_unique_and_refs,
    re_contains_absolute_path,
    validate_runtime_package,
)
from tools.data.runtime_materializer.policy import (
    FORBIDDEN_INPUT_NAMES,
    FORBIDDEN_OUTPUT_FRAGMENTS,
    IDENTITY_PAYLOAD_FILES,
    MATERIALIZATION_POLICY_ID,
    OUTPUT_FILES,
    RUNTIME_MAPPING_RULES,
    TOKEN_ADAPTER_ALLOWLIST,
)


ROOT = Path(__file__).resolve().parents[4]


def file_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


class TestCanonicalRuntimeMaterializer(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.candidate_result = build_candidate(default_config(ROOT))
        cls.candidate = cls.candidate_result.candidate_root
        cls.temp_root = ROOT / "TEMP" / "runtime_materializer_tests" / uuid.uuid4().hex
        cls.output_root = cls.temp_root / "output"
        cls.result = materialize(cls.candidate, cls.output_root, ROOT)

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.temp_root, ignore_errors=True)

    def test_01_verified_candidate_is_required(self) -> None:
        with self.assertRaises(MaterializationError) as context:
            materialize(self.temp_root / "missing-candidate", self.temp_root / "missing-output", ROOT)
        self.assertEqual("CANDIDATE_NOT_FOUND", context.exception.code)

    def test_02_tampered_candidate_is_rejected(self) -> None:
        parent = self.temp_root / "tampered"
        copy = parent / self.candidate.name
        shutil.copytree(self.candidate, copy)
        cards = copy / "components" / "CARDDATABASE" / "carddatabase.cards.json"
        cards.write_bytes(cards.read_bytes() + b" ")
        with self.assertRaises(MaterializationError) as context:
            materialize(copy, self.temp_root / "tampered-output", ROOT)
        self.assertEqual("CANDIDATE_VERIFICATION_FAILED", context.exception.code)

    def test_03_legacy_xlsx_cannot_be_input(self) -> None:
        path = ROOT / "Aeterna dokumentációk" / "cards.xlsx"
        with self.assertRaises(MaterializationError) as context:
            materialize(path, self.temp_root / "legacy-output", ROOT)
        self.assertEqual("CANDIDATE_DIRECTORY_REQUIRED", context.exception.code)

    def test_04_lookups_xlsx_cannot_be_input(self) -> None:
        path = ROOT / "Aeterna dokumentációk" / "LOOKUPS.xlsx"
        with self.assertRaises(MaterializationError) as context:
            materialize(path, self.temp_root / "lookups-output", ROOT)
        self.assertEqual("CANDIDATE_DIRECTORY_REQUIRED", context.exception.code)

    def test_05_double_materialization_is_byte_deterministic(self) -> None:
        before = file_hashes(self.result.output_directory)
        repeated = materialize(self.candidate, self.output_root, ROOT)
        self.assertEqual(self.result.runtime_package_id, repeated.runtime_package_id)
        self.assertEqual(before, file_hashes(repeated.output_directory))
        self.assertTrue(repeated.idempotent)

    def test_06_runtime_package_id_is_stable(self) -> None:
        provenance = json.loads((self.result.output_directory / "provenance.json").read_text(encoding="utf-8"))
        recomputed = compute_runtime_package_id(
            provenance["candidate_id"],
            provenance["package_set_id"],
            provenance["identity_payload_file_hashes"],
        )
        self.assertEqual(self.result.runtime_package_id, recomputed)

    def test_07_candidate_id_change_changes_runtime_identity(self) -> None:
        provenance = json.loads((self.result.output_directory / "provenance.json").read_text(encoding="utf-8"))
        changed = compute_runtime_package_id(
            "sha256:" + "1" * 64,
            provenance["package_set_id"],
            provenance["identity_payload_file_hashes"],
        )
        self.assertNotEqual(self.result.runtime_package_id, changed)

    def test_08_required_file_set_is_complete_and_exact(self) -> None:
        actual = {
            path.relative_to(self.result.output_directory).as_posix()
            for path in self.result.output_directory.rglob("*")
            if path.is_file()
        }
        self.assertEqual(set(OUTPUT_FILES), actual)
        self.assertEqual((), validate_runtime_package(self.result.output_directory))

    def test_09_manifest_and_provenance_hashes_are_valid(self) -> None:
        root = self.result.output_directory
        manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
        provenance = json.loads((root / "provenance.json").read_text(encoding="utf-8"))
        self.assertEqual(set(IDENTITY_PAYLOAD_FILES), set(manifest["identity_payload_file_hashes"]))
        for relative, expected in provenance["file_hashes"].items():
            actual = "sha256:" + hashlib.sha256((root / relative).read_bytes()).hexdigest()
            self.assertEqual(expected, actual, relative)

    def test_10_output_contains_no_absolute_path(self) -> None:
        for path in self.result.output_directory.rglob("*"):
            if path.is_file():
                self.assertFalse(re_contains_absolute_path(path.read_text(encoding="utf-8")), path.name)

    def test_11_output_contains_no_legacy_source_reference(self) -> None:
        for path in self.result.output_directory.rglob("*"):
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8").casefold()
            for fragment in FORBIDDEN_OUTPUT_FRAGMENTS:
                self.assertNotIn(fragment.casefold(), text, f"{fragment} in {path.name}")

    def test_12_duplicate_ids_are_rejected(self) -> None:
        cards = [{"card_id": "A"}, {"card_id": "A"}]
        with self.assertRaises(MaterializationError) as context:
            _validate_unique_and_refs(cards, [], [])
        self.assertEqual("DUPLICATE_CARD_ID", context.exception.code)

    def test_13_broken_foreign_key_is_rejected(self) -> None:
        cards = [{"card_id": "A"}]
        decks = [{"deck_id": "D", "card_entries": [{"card_id": "B", "count": 1}]}]
        with self.assertRaises(MaterializationError) as context:
            _validate_unique_and_refs(cards, decks, [])
        self.assertEqual("BROKEN_DECK_CARD_FK", context.exception.code)

    def test_14_runtime_required_mapping_subset_is_exact(self) -> None:
        self.assertEqual(12, len(RUNTIME_MAPPING_RULES))
        self.assertEqual(7, sum(rule.group == "realm" for rule in RUNTIME_MAPPING_RULES))
        self.assertEqual(5, sum(rule.group == "card_type" for rule in RUNTIME_MAPPING_RULES))
        self.assertEqual(2, sum(rule.mapping_kind == "DETERMINISTIC_TECHNICAL_ADAPTER" for rule in RUNTIME_MAPPING_RULES))

    def test_15_unsupported_semantic_mapping_fails_closed(self) -> None:
        with self.assertRaises(MaterializationError) as context:
            _runtime_value_for("card_type", "spell", "sorcery")
        self.assertEqual("RUNTIME_MAPPING_DECISION_REQUIRED", context.exception.code)

    def test_16_token_adapters_are_exactly_allowlisted(self) -> None:
        actual = {
            (rule.group, rule.canonical_value, rule.runtime_value)
            for rule in RUNTIME_MAPPING_RULES
            if rule.mapping_kind == "DETERMINISTIC_TECHNICAL_ADAPTER"
        }
        self.assertEqual(TOKEN_ADAPTER_ALLOWLIST, actual)

    def test_17_existing_godot_package_is_untouched(self) -> None:
        godot = ROOT / "Aeterna game engine" / "Godot" / "runtime_package"
        before = file_hashes(godot)
        materialize(self.candidate, self.output_root, ROOT)
        self.assertEqual(before, file_hashes(godot))

    def test_18_idempotent_rerun_reuses_identical_identity_directory(self) -> None:
        repeated = materialize(self.candidate, self.output_root, ROOT)
        self.assertTrue(repeated.idempotent)
        self.assertEqual(self.result.output_directory, repeated.output_directory)
        self.assertEqual(_tree_hashes(self.result.output_directory), _tree_hashes(repeated.output_directory))

    def test_19_materializer_opens_no_external_source_file(self) -> None:
        accessed: list[Path] = []
        original_open = Path.open

        def audited_open(path: Path, *args, **kwargs):
            accessed.append(path.resolve())
            return original_open(path, *args, **kwargs)

        audit_output = self.temp_root / "read-audit-output"
        with mock.patch.object(Path, "open", audited_open):
            result = materialize(self.candidate, audit_output, ROOT)
        self.assertTrue(result.materialization_valid)
        forbidden = {name.casefold() for name in FORBIDDEN_INPUT_NAMES}
        self.assertFalse(any(path.name.casefold() in forbidden for path in accessed))
        self.assertFalse(any(path.suffix.casefold() == ".xlsx" for path in accessed))

    def test_20_output_path_outside_repository_temp_is_rejected(self) -> None:
        with self.assertRaises(MaterializationError) as context:
            materialize(self.candidate, ROOT / "Aeterna game engine" / "Godot" / "runtime_package", ROOT)
        self.assertEqual("OUTPUT_PATH_FORBIDDEN", context.exception.code)

    def test_21_candidate_only_provenance_and_readiness_are_explicit(self) -> None:
        provenance = json.loads((self.result.output_directory / "provenance.json").read_text(encoding="utf-8"))
        manifest = json.loads((self.result.output_directory / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(0, provenance["read_audit"]["legacy_source_read_count"])
        self.assertTrue(provenance["read_audit"]["candidate_only"])
        self.assertFalse(manifest["readiness"]["production_ready"])
        self.assertFalse(manifest["readiness"]["publish_allowed"])

    def test_22_durable_contract_has_no_migration_wave_identifier(self) -> None:
        durable_root = ROOT / "tools" / "data" / "runtime_materializer"
        wave_prefix = "w" + "3b"
        source_text = "\n".join(
            path.read_text(encoding="utf-8").casefold()
            for path in sorted(durable_root.rglob("*.py"))
        )
        self.assertEqual("canonical-runtime-materialization-policy-v1", MATERIALIZATION_POLICY_ID)
        self.assertNotIn(wave_prefix, source_text)

    def test_23_future_ready_candidate_is_not_permanently_blocked(self) -> None:
        readiness = _derive_readiness(
            {"blockers": [], "production_ready": True, "publish_allowed": True},
            materialization_valid=True,
        )
        self.assertTrue(readiness["production_ready"])
        self.assertTrue(readiness["publish_allowed"])

    def test_24_current_candidate_readiness_and_blockers_are_propagated(self) -> None:
        candidate_readiness = json.loads((self.candidate / "readiness.json").read_text(encoding="utf-8"))
        manifest = json.loads((self.result.output_directory / "manifest.json").read_text(encoding="utf-8"))
        provenance = json.loads((self.result.output_directory / "provenance.json").read_text(encoding="utf-8"))
        diagnostics = json.loads((self.result.output_directory / "diagnostics.json").read_text(encoding="utf-8"))
        expected_blockers = sorted(candidate_readiness["blockers"], key=lambda item: item["id"])
        self.assertFalse(manifest["readiness"]["production_ready"])
        self.assertFalse(manifest["readiness"]["publish_allowed"])
        self.assertEqual(expected_blockers, manifest["readiness"]["blockers"])
        self.assertEqual(expected_blockers, provenance["readiness"]["blockers"])
        self.assertEqual(expected_blockers, [item["source_blocker"] for item in diagnostics["diagnostics"]])

    def test_25_candidate_blocker_changes_propagate_without_source_changes(self) -> None:
        first = {"id": "BLOCKER-ALPHA", "status": "OPEN", "summary": "First candidate blocker."}
        second = {"id": "BLOCKER-BETA", "status": "OPEN", "summary": "Second candidate blocker."}
        first_readiness = _derive_readiness(
            {"blockers": [first], "production_ready": False, "publish_allowed": False},
            materialization_valid=True,
        )
        second_readiness = _derive_readiness(
            {"blockers": [second], "production_ready": False, "publish_allowed": False},
            materialization_valid=True,
        )
        self.assertEqual([first], first_readiness["blockers"])
        self.assertEqual([second], second_readiness["blockers"])
        self.assertEqual(
            [first],
            [item["source_blocker"] for item in _candidate_blocker_diagnostics(first_readiness["blockers"])],
        )
        self.assertEqual(
            [second],
            [item["source_blocker"] for item in _candidate_blocker_diagnostics(second_readiness["blockers"])],
        )

    def test_26_durable_source_has_no_current_issue_state_constants(self) -> None:
        durable_root = ROOT / "tools" / "data" / "runtime_materializer"
        forbidden_tokens = (
            "p" + "01",
            "p" + "04",
            "hd" + "-01",
            "aqu" + "-mor-017",
            "unresolved" + "_semantic_readiness",
        )
        source_text = "\n".join(
            path.read_text(encoding="utf-8").casefold()
            for path in sorted(durable_root.rglob("*.py"))
        )
        self.assertFalse(any(token in source_text for token in forbidden_tokens))


if __name__ == "__main__":
    unittest.main()
