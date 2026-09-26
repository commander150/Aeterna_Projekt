from __future__ import annotations

from dataclasses import replace
import hashlib
import json
from pathlib import Path
import unittest
from unittest import mock

from tools.data.canonical_producer import producer


REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
HASH_A = "sha256:" + "a" * 64
HASH_B = "sha256:" + "b" * 64
HASH_C = "sha256:" + "c" * 64


class TestCandidateIdentity(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.package_set = producer.load_existing_modules(REPOSITORY_ROOT)[
            "canonical_package_set"
        ]
        cls.package_set_id = HASH_A
        cls.sources = {
            producer.CARDDATABASE_PATH: HASH_B,
            producer.REGISTRY_PATH: HASH_C,
        }
        cls.tools = (
            {"path": "canonical/tool.py", "sha256": HASH_A},
        )

    def candidate_id(self, sources=None) -> str:
        return producer._compute_candidate_id(
            package_set_id=self.package_set_id,
            source_hashes=sources or self.sources,
            tool_identities=self.tools,
            package_set=self.package_set,
        )

    def test_source_hash_is_not_a_hard_coded_allowlist(self) -> None:
        source = Path(producer.__file__).read_text(encoding="utf-8")
        self.assertFalse(hasattr(producer, "EXPECTED_SOURCE_HASHES"))
        self.assertNotIn("CANONICAL_SOURCE_HASH_MISMATCH", source)
        self.assertNotIn("2741441e36609854c4b0d0e36679ab4106f525668e2e7658ac062111f4598bbd", source)

    def test_source_hash_change_changes_only_candidate_identity_input(self) -> None:
        changed = dict(self.sources)
        changed[producer.CARDDATABASE_PATH] = "sha256:" + "d" * 64

        first_candidate_id = self.candidate_id()
        second_candidate_id = self.candidate_id(changed)

        self.assertEqual(HASH_A, self.package_set_id)
        self.assertNotEqual(first_candidate_id, second_candidate_id)

    def test_candidate_identity_is_deterministic_for_same_input(self) -> None:
        self.assertEqual(self.candidate_id(), self.candidate_id(dict(self.sources)))

    def test_candidate_preimage_has_durable_semantic_names(self) -> None:
        preimage = producer._candidate_identity_preimage(
            package_set_id=self.package_set_id,
            source_hashes=self.sources,
            tool_identities=self.tools,
        )
        self.assertEqual("aeterna-canonical-candidate-v1", preimage["domain"])
        self.assertEqual("canonical-producer", preimage["tool_contract_id"])
        self.assertEqual("v1", preimage["tool_contract_version"])
        self.assertNotIn("w3b4a", json.dumps(preimage).casefold())

    def test_v2_profile_contract_contains_roles_without_repository_paths(self) -> None:
        contract = producer._profile_contract()
        serialized = json.dumps(contract, ensure_ascii=False, sort_keys=True)
        self.assertEqual("canonical-component-candidate-v2", producer.PROFILE_ID)
        self.assertEqual(["CARDDATABASE", "REGISTRY"], contract["producer_source_roles"])
        self.assertNotIn("producer_sources", contract)
        for role in contract["producer_source_roles"]:
            self.assertNotIn("/", role)
            self.assertNotIn("\\", role)
        for forbidden in (
            "data/canonical/CARDDATABASE.xlsx",
            "data/canonical/REGISTRY.xlsx",
            ("Aeterna " + "dokumentációk") + "/CARDDATABASE.xlsx",
            ("Aeterna " + "dokumentációk") + "/REGISTRY.xlsx",
        ):
            self.assertNotIn(forbidden, serialized)

    def test_package_set_identity_is_independent_of_physical_source_paths(self) -> None:
        component = self.package_set.ComponentDescriptor(
            component_format_version=self.package_set.COMPONENT_FORMAT_VERSION,
            component_identity=HASH_A,
            component_id="carddatabase",
            component_kind="CARDDATABASE",
            package_id="aeterna_carddatabase",
            schema_version="1",
            data_version="1",
            content_hash=HASH_B,
            manifest_file="components/CARDDATABASE/manifest.json",
            manifest_hash=HASH_C,
            dependencies=(),
            consumer_requirement=self.package_set.CONSUMER_REQUIRED,
        )
        component = replace(
            component,
            component_identity=self.package_set.compute_component_identity(component),
        )

        def compute(card_path: str, registry_path: str) -> str:
            with (
                mock.patch.object(producer, "CARDDATABASE_PATH", card_path),
                mock.patch.object(producer, "REGISTRY_PATH", registry_path),
            ):
                profile_hash = self.package_set.sha256_bytes(
                    self.package_set.canonical_json_bytes(producer._profile_contract())
                )
                value = self.package_set.PackageSet(
                    package_set_format_version=self.package_set.PACKAGE_SET_FORMAT_VERSION,
                    package_set_id=HASH_A,
                    package_set_profile_id=producer.PROFILE_ID,
                    profile_contract_hash=profile_hash,
                    validation_policy_id=producer.VALIDATION_POLICY_ID,
                    components=(component,),
                    validation_ledger_file="validation/ledger.json",
                    validation_ledger_hash=HASH_C,
                )
                return self.package_set.compute_package_set_identity(value)

        first = compute("location-a/CARDDATABASE.xlsx", "location-a/REGISTRY.xlsx")
        second = compute("location-b/CARDDATABASE.xlsx", "location-b/REGISTRY.xlsx")
        self.assertEqual(first, second)


class TestProducerConfiguration(unittest.TestCase):
    def setUp(self) -> None:
        self.modules = producer.load_existing_modules(REPOSITORY_ROOT)
        self.package_set = self.modules["canonical_package_set"]

    def test_missing_carddatabase_is_hard_failure(self) -> None:
        config = producer.default_config(REPOSITORY_ROOT)
        with mock.patch.object(Path, "is_file", return_value=False):
            with self.assertRaisesRegex(producer.ProducerError, "CANONICAL_SOURCE_MISSING"):
                producer._validate_config(config, self.package_set)

    def test_missing_registry_is_hard_failure(self) -> None:
        config = producer.default_config(REPOSITORY_ROOT)
        with mock.patch.object(Path, "is_file", side_effect=(True, False)):
            with self.assertRaisesRegex(producer.ProducerError, "CANONICAL_SOURCE_MISSING"):
                producer._validate_config(config, self.package_set)

    def test_legacy_presence_does_not_create_fallback(self) -> None:
        config = producer.default_config(REPOSITORY_ROOT)
        _, _, output = producer._validate_config(config, self.package_set)
        self.assertEqual(output, REPOSITORY_ROOT / producer.DEFAULT_OUTPUT_ROOT)
        self.assertEqual(config.carddatabase_path, producer.CARDDATABASE_PATH)
        self.assertEqual(config.registry_path, producer.REGISTRY_PATH)

    def test_default_canonical_sources_use_data_owner(self) -> None:
        config = producer.default_config(REPOSITORY_ROOT)
        card, registry, _ = producer._validate_config(config, self.package_set)
        self.assertEqual("data/canonical/CARDDATABASE.xlsx", config.carddatabase_path)
        self.assertEqual("data/canonical/REGISTRY.xlsx", config.registry_path)
        self.assertEqual(REPOSITORY_ROOT / "data" / "canonical" / "CARDDATABASE.xlsx", card)
        self.assertEqual(REPOSITORY_ROOT / "data" / "canonical" / "REGISTRY.xlsx", registry)

    def test_old_canonical_source_paths_are_rejected(self) -> None:
        old_owner = "Aeterna " + "dokumentációk"
        substitutions = (
            {"carddatabase_path": f"{old_owner}/CARDDATABASE.xlsx"},
            {"registry_path": f"{old_owner}/REGISTRY.xlsx"},
        )
        for substitution in substitutions:
            with self.subTest(substitution=substitution):
                config = replace(producer.default_config(REPOSITORY_ROOT), **substitution)
                with self.assertRaisesRegex(
                    producer.ProducerError,
                    "CANONICAL_SOURCE_SUBSTITUTION_REJECTED",
                ):
                    producer._validate_config(config, self.package_set)

    def test_munkaforras_substitution_is_rejected(self) -> None:
        config = replace(
            producer.default_config(REPOSITORY_ROOT),
            carddatabase_path="Aeterna dokumentációk/AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.9v.xlsx",
        )
        with self.assertRaisesRegex(producer.ProducerError, "CANONICAL_SOURCE_SUBSTITUTION_REJECTED"):
            producer._validate_config(config, self.package_set)

    def test_lookups_substitution_is_rejected(self) -> None:
        config = replace(
            producer.default_config(REPOSITORY_ROOT),
            registry_path="Aeterna dokumentációk/LOOKUPS.xlsx",
        )
        with self.assertRaisesRegex(producer.ProducerError, "CANONICAL_SOURCE_SUBSTITUTION_REJECTED"):
            producer._validate_config(config, self.package_set)

    def test_absolute_source_path_is_rejected(self) -> None:
        config = replace(
            producer.default_config(REPOSITORY_ROOT),
            carddatabase_path=str((REPOSITORY_ROOT / producer.CARDDATABASE_PATH).resolve()),
        )
        with self.assertRaisesRegex(producer.ProducerError, "SOURCE_PATH_INVALID"):
            producer._validate_config(config, self.package_set)

    def test_invalid_workbook_blocks_before_candidate_success(self) -> None:
        exporter = self.modules["canonical_workbook_exporter"]
        invalid = REPOSITORY_ROOT / "requirements-tooling.txt"
        output = REPOSITORY_ROOT / "TEMP" / "canonical_producer_invalid_workbook"
        with self.assertRaises(exporter.CanonicalExportError):
            exporter.export_canonical_workbooks((invalid,), output, production=False)
        self.assertFalse((output / "CARDDATABASE").exists())

    def test_candidate_id_collision_never_replaces_existing_bytes(self) -> None:
        staging = Path("staging")
        existing = Path("existing")
        with (
            mock.patch.object(Path, "exists", return_value=True),
            mock.patch.object(
                producer,
                "_tree_hashes",
                side_effect=({"file": "new"}, {"file": "existing"}),
            ),
            mock.patch.object(producer.shutil, "rmtree") as remove,
        ):
            with self.assertRaisesRegex(producer.ProducerError, "CANDIDATE_ID_COLLISION"):
                producer._publish_immutable_candidate(staging, existing)
        remove.assert_not_called()


class TestReadinessAndCandidate(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = producer.build_candidate(producer.default_config(REPOSITORY_ROOT))

    def test_blocking_diagnostics_never_permit_publish_ready(self) -> None:
        readiness = json.loads((self.result.candidate_root / "readiness.json").read_text(encoding="utf-8"))
        self.assertFalse(readiness["production_ready"])
        self.assertFalse(readiness["publish_allowed"])

    def test_open_blockers_allow_candidate_but_keep_production_false(self) -> None:
        self.assertTrue(self.result.candidate_root.is_dir())
        self.assertFalse(self.result.production_ready)
        self.assertFalse(self.result.publish_allowed)
        blocker = (self.result.candidate_root / "blocker_report.md").read_text(encoding="utf-8")
        for item in ("P01", "P04 / HD-07", "HD-01"):
            self.assertIn(item, blocker)

    def test_candidate_verifies_and_has_two_components(self) -> None:
        self.assertEqual((), producer.verify_candidate(self.result.candidate_root, REPOSITORY_ROOT))
        manifest = json.loads((self.result.candidate_root / "package_set.json").read_text(encoding="utf-8"))
        self.assertEqual({"CARDDATABASE", "REGISTRY"}, {item["component_kind"] for item in manifest["components"]})
        self.assertNotEqual(self.result.package_set_id, self.result.candidate_id)

    def test_provenance_candidate_id_is_recomputable(self) -> None:
        provenance = json.loads(
            (self.result.candidate_root / "provenance.json").read_text(encoding="utf-8")
        )
        package_set = producer.load_existing_modules(REPOSITORY_ROOT)[
            "canonical_package_set"
        ]
        source_hashes = {
            item["path"]: item["sha256"] for item in provenance["sources"]
        }
        recomputed = producer._compute_candidate_id(
            package_set_id=provenance["package_set_id"],
            source_hashes=source_hashes,
            tool_identities=provenance["tool_identities"],
            package_set=package_set,
        )
        self.assertEqual(provenance["candidate_id"], recomputed)
        self.assertEqual(self.result.candidate_id, recomputed)
        self.assertEqual(
            self.result.candidate_root.name,
            recomputed.removeprefix("sha256:"),
        )

    def test_producer_execution_reads_only_canonical_pair(self) -> None:
        self.assertGreater(self.result.read_counts[producer.CARDDATABASE_PATH], 0)
        self.assertGreater(self.result.read_counts[producer.REGISTRY_PATH], 0)
        for path in producer.AUDITED_DATASETS[2:]:
            self.assertEqual(0, self.result.read_counts[path])

    def test_repeat_build_is_byte_deterministic(self) -> None:
        first = self._hashes(self.result.candidate_root)
        repeated = producer.build_candidate(producer.default_config(REPOSITORY_ROOT))
        second = self._hashes(repeated.candidate_root)
        self.assertEqual(self.result.candidate_id, repeated.candidate_id)
        self.assertEqual(first, second)

    @staticmethod
    def _hashes(root: Path) -> dict[str, str]:
        return {
            path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(root.rglob("*"), key=lambda item: item.as_posix())
            if path.is_file()
        }


if __name__ == "__main__":
    unittest.main()
