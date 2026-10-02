from __future__ import annotations

import contextlib
import hashlib
import io
import json
import shutil
import unittest
import uuid
from pathlib import Path
from unittest import mock

from tools.data.canonical_producer import build_candidate, default_config
from tools.data.runtime_materializer import materialize, validate_runtime_package
from tools.data.runtime_publisher import PromotionError, preflight, promote
from tools.data.runtime_publisher.__main__ import main as cli_main
from tools.data.runtime_publisher import publisher


ROOT = Path(__file__).resolve().parents[4]


def hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


class TestRuntimePublisher(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.class_root = ROOT / "TEMP" / "runtime_publisher_tests" / uuid.uuid4().hex
        cls.class_root.mkdir(parents=True)
        candidate = build_candidate(default_config(ROOT)).candidate_root
        cls.candidate = candidate
        cls.current_authority = read_json(candidate / "readiness.json")
        cls.current = materialize(candidate, cls.class_root / "materialized", ROOT).output_directory

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.class_root, ignore_errors=True)

    def setUp(self) -> None:
        self.case = self.class_root / uuid.uuid4().hex
        self.repo = self.case / "repository"
        self.source = self.repo / "TEMP" / "materialization" / self.current.name
        self.target = self.repo / "src" / "client" / "runtime_package"
        self.source.parent.mkdir(parents=True)
        self.target.parent.mkdir(parents=True)
        shutil.copytree(self.current, self.source)
        shutil.copytree(ROOT / "src" / "client" / "runtime_package", self.target)

    def tearDown(self) -> None:
        shutil.rmtree(self.case, ignore_errors=True)

    def make_ready(self, *, publish_allowed: bool = True, blockers: list[dict] | None = None) -> dict:
        manifest_path = self.source / "manifest.json"
        provenance_path = self.source / "provenance.json"
        manifest = read_json(manifest_path)
        provenance = read_json(provenance_path)
        readiness = dict(manifest["readiness"])
        readiness.update(
            {
                "blockers": [],
                "candidate_production_ready": True,
                "candidate_publish_allowed": publish_allowed,
                "materialization_valid": True,
                "production_ready": True,
                "publish_allowed": publish_allowed,
            }
        )
        readiness["blockers"] = list(blockers or [])
        manifest["readiness"] = readiness
        manifest["validation_summary"]["materialization_valid"] = True
        provenance["readiness"] = readiness
        write_json(manifest_path, manifest)
        provenance["file_hashes"]["manifest.json"] = sha256(manifest_path)
        write_json(provenance_path, provenance)
        self.assertEqual((), validate_runtime_package(self.source))
        return readiness

    def authority_patch(self, readiness: dict):
        return mock.patch.object(publisher, "_read_candidate_authority", return_value=readiness)

    def update_manifest_hash(self) -> None:
        provenance_path = self.source / "provenance.json"
        provenance = read_json(provenance_path)
        provenance["file_hashes"]["manifest.json"] = sha256(self.source / "manifest.json")
        write_json(provenance_path, provenance)

    def assert_code(self, code: str, callable_, *args, **kwargs) -> None:
        with self.assertRaises(PromotionError) as context:
            callable_(*args, **kwargs)
        self.assertEqual(code, context.exception.code, str(context.exception))

    def test_01_current_real_readiness_is_rejected(self) -> None:
        self.assert_code("PROMOTION_PRODUCTION_NOT_READY", preflight, self.current, ROOT)

    def test_02_current_real_apply_is_rejected_without_target_mutation(self) -> None:
        real_target = ROOT / "src" / "client" / "runtime_package"
        before = hashes(real_target)
        self.assert_code("PROMOTION_PRODUCTION_NOT_READY", promote, self.current, ROOT)
        self.assertEqual(before, hashes(real_target))

    def test_03_future_ready_canonical_structure_passes_preflight(self) -> None:
        readiness = self.make_ready()
        with self.authority_patch(readiness):
            result = preflight(self.source, self.repo)
        self.assertFalse(result.applied)
        self.assertEqual(11, result.file_count)

    def test_04_publish_false_is_rejected_after_production_gate(self) -> None:
        readiness = self.make_ready(publish_allowed=False)
        with self.authority_patch(readiness):
            self.assert_code("PROMOTION_NOT_ALLOWED", preflight, self.source, self.repo)

    def test_05_invalid_materialization_has_first_readiness_precedence(self) -> None:
        self.make_ready()
        manifest = read_json(self.source / "manifest.json")
        provenance = read_json(self.source / "provenance.json")
        manifest["readiness"]["materialization_valid"] = False
        manifest["readiness"]["production_ready"] = False
        manifest["readiness"]["publish_allowed"] = False
        manifest["validation_summary"]["materialization_valid"] = False
        provenance["readiness"] = manifest["readiness"]
        write_json(self.source / "manifest.json", manifest)
        provenance["file_hashes"]["manifest.json"] = sha256(self.source / "manifest.json")
        write_json(self.source / "provenance.json", provenance)
        self.assert_code("PROMOTION_MATERIALIZATION_NOT_VALID", preflight, self.source, self.repo)

    def test_06_preflight_is_deterministic_and_pure(self) -> None:
        readiness = self.make_ready()
        source_before = hashes(self.source)
        target_before = hashes(self.target)
        with self.authority_patch(readiness):
            first = preflight(self.source, self.repo)
            second = preflight(self.source, self.repo)
        self.assertEqual(first, second)
        self.assertEqual(source_before, hashes(self.source))
        self.assertEqual(target_before, hashes(self.target))

    def test_07_missing_input(self) -> None:
        self.assert_code("PROMOTION_INPUT_NOT_FOUND", preflight, self.repo / "TEMP" / "missing", self.repo)

    def test_08_input_outside_temp(self) -> None:
        outside = self.repo / "outside"
        shutil.copytree(self.current, outside)
        self.assert_code("PROMOTION_INPUT_OUTSIDE_TEMP", preflight, outside, self.repo)

    def test_09_raw_xlsx_is_not_a_materialization(self) -> None:
        raw = self.repo / "TEMP" / "raw.xlsx"
        raw.write_bytes(b"xlsx")
        self.assert_code("PROMOTION_INPUT_NOT_CANONICAL_MATERIALIZATION", preflight, raw, self.repo)

    def test_10_candidate_directory_is_not_a_materialization(self) -> None:
        candidate = self.repo / "TEMP" / "candidate"
        candidate.mkdir()
        (candidate / "candidate_manifest.json").write_text("{}", encoding="utf-8")
        self.assert_code("PROMOTION_INPUT_NOT_CANONICAL_MATERIALIZATION", preflight, candidate, self.repo)

    def test_11_sample_package_is_not_a_canonical_materialization(self) -> None:
        sample = self.repo / "TEMP" / "sample"
        shutil.copytree(self.target, sample)
        self.assert_code("PROMOTION_INPUT_NOT_CANONICAL_MATERIALIZATION", preflight, sample, self.repo)

    def test_12_arbitrary_directory_is_rejected(self) -> None:
        arbitrary = self.repo / "TEMP" / "arbitrary"
        arbitrary.mkdir()
        (arbitrary / "note.txt").write_text("not a package", encoding="utf-8")
        self.assert_code("PROMOTION_INPUT_NOT_CANONICAL_MATERIALIZATION", preflight, arbitrary, self.repo)

    def test_13_source_reparse_is_rejected(self) -> None:
        original = publisher._is_reparse_point
        with mock.patch.object(
            publisher,
            "_is_reparse_point",
            side_effect=lambda path: path == Path(self.source) or original(path),
        ):
            self.assert_code("PROMOTION_INPUT_OUTSIDE_TEMP", preflight, self.source, self.repo)

    def test_14_wrong_materializer_is_rejected(self) -> None:
        provenance = read_json(self.source / "provenance.json")
        provenance["materializer"]["id"] = "other"
        write_json(self.source / "provenance.json", provenance)
        self.assert_code("PROMOTION_PROVENANCE_INVALID", preflight, self.source, self.repo)

    def test_15_wrong_contract_version_is_rejected(self) -> None:
        provenance = read_json(self.source / "provenance.json")
        provenance["materializer"]["contract_version"] = "2"
        write_json(self.source / "provenance.json", provenance)
        self.assert_code("PROMOTION_PROVENANCE_INVALID", preflight, self.source, self.repo)

    def test_16_wrong_profile_is_rejected(self) -> None:
        provenance = read_json(self.source / "provenance.json")
        provenance["materialization_profile_id"] = "wrong"
        write_json(self.source / "provenance.json", provenance)
        self.assert_code("PROMOTION_PROVENANCE_INVALID", preflight, self.source, self.repo)

    def test_17_wrong_policy_is_rejected(self) -> None:
        provenance = read_json(self.source / "provenance.json")
        provenance["materialization_policy_id"] = "wrong"
        write_json(self.source / "provenance.json", provenance)
        self.assert_code("PROMOTION_PROVENANCE_INVALID", preflight, self.source, self.repo)

    def test_18_candidate_only_false_is_rejected(self) -> None:
        provenance = read_json(self.source / "provenance.json")
        provenance["read_audit"]["candidate_only"] = False
        write_json(self.source / "provenance.json", provenance)
        self.assert_code("PROMOTION_PROVENANCE_INVALID", preflight, self.source, self.repo)

    def test_19_legacy_read_is_rejected(self) -> None:
        provenance = read_json(self.source / "provenance.json")
        provenance["read_audit"]["legacy_source_read_count"] = 1
        write_json(self.source / "provenance.json", provenance)
        self.assert_code("PROMOTION_PROVENANCE_INVALID", preflight, self.source, self.repo)

    def test_20_missing_source_component_is_rejected(self) -> None:
        provenance = read_json(self.source / "provenance.json")
        del provenance["source_components"]["REGISTRY"]
        write_json(self.source / "provenance.json", provenance)
        self.assert_code("PROMOTION_PROVENANCE_INVALID", preflight, self.source, self.repo)

    def test_21_candidate_identity_mismatch_is_rejected(self) -> None:
        manifest = read_json(self.source / "manifest.json")
        manifest["source_identity"]["candidate_id"] = "sha256:" + "1" * 64
        write_json(self.source / "manifest.json", manifest)
        self.update_manifest_hash()
        self.assert_code("PROMOTION_IDENTITY_MISMATCH", preflight, self.source, self.repo)

    def test_22_package_set_mismatch_is_rejected(self) -> None:
        manifest = read_json(self.source / "manifest.json")
        manifest["source_identity"]["package_set_id"] = "sha256:" + "2" * 64
        write_json(self.source / "manifest.json", manifest)
        self.update_manifest_hash()
        self.assert_code("PROMOTION_IDENTITY_MISMATCH", preflight, self.source, self.repo)

    def test_23_runtime_identity_mismatch_is_rejected(self) -> None:
        manifest = read_json(self.source / "manifest.json")
        manifest["runtime_package_id"] = "sha256:" + "3" * 64
        manifest["package_id"] = manifest["runtime_package_id"]
        write_json(self.source / "manifest.json", manifest)
        self.update_manifest_hash()
        self.assert_code("PROMOTION_IDENTITY_MISMATCH", preflight, self.source, self.repo)

    def test_24_readiness_mismatch_is_rejected(self) -> None:
        manifest = read_json(self.source / "manifest.json")
        manifest["readiness"]["production_ready"] = True
        write_json(self.source / "manifest.json", manifest)
        self.update_manifest_hash()
        self.assert_code("PROMOTION_PROVENANCE_INVALID", preflight, self.source, self.repo)

    def test_25_payload_hash_tamper_is_rejected(self) -> None:
        with (self.source / "cards.jsonl").open("ab") as handle:
            handle.write(b" ")
        self.assert_code("PROMOTION_IDENTITY_MISMATCH", preflight, self.source, self.repo)

    def test_26_target_reparse_is_rejected(self) -> None:
        self.make_ready()
        original = publisher._is_reparse_point
        with mock.patch.object(
            publisher,
            "_is_reparse_point",
            side_effect=lambda path: path == Path(self.target) or original(path),
        ):
            self.assert_code("PROMOTION_TARGET_UNSAFE", preflight, self.source, self.repo)

    def test_27_atomic_replacement_is_exact_and_byte_identical(self) -> None:
        readiness = self.make_ready()
        with self.authority_patch(readiness):
            result = promote(self.source, self.repo)
        self.assertTrue(result.applied)
        self.assertEqual(11, len(hashes(self.target)))
        self.assertEqual(hashes(self.source), hashes(self.target))
        self.assertTrue((self.target / "provenance.json").is_file())
        for name in (
            "normalization_apply_report.json",
            "normalization_audit_report.json",
            "normalization_patch_plan.json",
            "normalization_preview_report.json",
        ):
            self.assertFalse((self.target / name).exists())

    def test_28_failure_before_swap_leaves_target_untouched(self) -> None:
        readiness = self.make_ready()
        before = hashes(self.target)
        with self.authority_patch(readiness):
            with mock.patch.object(publisher.shutil, "copytree", side_effect=OSError("injected")):
                self.assert_code("PROMOTION_ATOMIC_REPLACE_FAILED", promote, self.source, self.repo)
        self.assertEqual(before, hashes(self.target))

    def test_29_failure_after_old_target_rename_rolls_back(self) -> None:
        readiness = self.make_ready()
        before = hashes(self.target)
        original = publisher._rename_directory
        calls = 0

        def injected(source: Path, destination: Path) -> None:
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("injected after backup")
            original(source, destination)

        with self.authority_patch(readiness):
            with mock.patch.object(publisher, "_rename_directory", side_effect=injected):
                self.assert_code("PROMOTION_ATOMIC_REPLACE_FAILED", promote, self.source, self.repo)
        self.assertEqual(before, hashes(self.target))

    def test_30_failure_after_new_target_placement_rolls_back(self) -> None:
        readiness = self.make_ready()
        before = hashes(self.target)
        original = publisher._validate_package_contents
        calls = 0

        def injected(path: Path, *args):
            nonlocal calls
            calls += 1
            if calls == 3:
                raise PromotionError("PROMOTION_PACKAGE_INVALID", "injected post-copy failure")
            return original(path, *args)

        with self.authority_patch(readiness):
            with mock.patch.object(publisher, "_validate_package_contents", side_effect=injected):
                self.assert_code("PROMOTION_POSTCOPY_VALIDATION_FAILED", promote, self.source, self.repo)
        self.assertEqual(before, hashes(self.target))

    def test_31_rollback_failure_is_reported(self) -> None:
        readiness = self.make_ready()
        original = publisher._rename_directory
        calls = 0

        def injected(source: Path, destination: Path) -> None:
            nonlocal calls
            calls += 1
            if calls in {2, 3}:
                raise OSError("injected replacement and rollback failure")
            original(source, destination)

        with self.authority_patch(readiness):
            with mock.patch.object(publisher, "_rename_directory", side_effect=injected):
                self.assert_code("PROMOTION_ROLLBACK_FAILED", promote, self.source, self.repo)

    def test_32_double_lock_acquisition_is_rejected(self) -> None:
        with publisher._promotion_lock(self.repo):
            self.assert_code("PROMOTION_ATOMIC_REPLACE_FAILED", publisher._promotion_lock(self.repo).__enter__)

    def test_33_cli_defaults_to_preflight_and_outputs_json(self) -> None:
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = cli_main(["--source", str(self.current)])
        self.assertEqual(2, code)
        payload = json.loads(stderr.getvalue())
        self.assertEqual("PROMOTION_PRODUCTION_NOT_READY", payload["code"])

    def test_34_cli_apply_current_package_is_fail_closed(self) -> None:
        real_target = ROOT / "src" / "client" / "runtime_package"
        before = hashes(real_target)
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = cli_main(["--source", str(self.current), "--apply"])
        self.assertEqual(2, code)
        self.assertEqual("PROMOTION_PRODUCTION_NOT_READY", json.loads(stderr.getvalue())["code"])
        self.assertEqual(before, hashes(real_target))

    def test_35_cli_has_no_target_override(self) -> None:
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = cli_main(["--source", str(self.current), "--target", str(self.target)])
        self.assertEqual(2, code)
        self.assertEqual("PROMOTION_INPUT_NOT_CANONICAL_MATERIALIZATION", json.loads(stderr.getvalue())["code"])

    def test_36_failed_candidate_verifier_is_rejected(self) -> None:
        provenance = read_json(self.source / "provenance.json")
        provenance["candidate_verifier"] = {"errors": ["injected"], "result": "FAIL"}
        write_json(self.source / "provenance.json", provenance)
        self.assert_code("PROMOTION_PROVENANCE_INVALID", preflight, self.source, self.repo)

    def test_37_external_source_read_is_rejected(self) -> None:
        provenance = read_json(self.source / "provenance.json")
        provenance["read_audit"]["external_source_file_read_count"] = 1
        write_json(self.source / "provenance.json", provenance)
        self.assert_code("PROMOTION_PROVENANCE_INVALID", preflight, self.source, self.repo)

    def test_38_runtime_identity_domain_is_exact(self) -> None:
        provenance = read_json(self.source / "provenance.json")
        provenance["runtime_identity_domain"] = "wrong"
        write_json(self.source / "provenance.json", provenance)
        self.assert_code("PROMOTION_PROVENANCE_INVALID", preflight, self.source, self.repo)

    def test_39_extra_directory_is_rejected(self) -> None:
        (self.source / "unexpected").mkdir()
        self.assert_code("PROMOTION_INPUT_NOT_CANONICAL_MATERIALIZATION", preflight, self.source, self.repo)

    def test_40_referenced_candidate_missing_is_rejected(self) -> None:
        self.assert_code("PROMOTION_PROVENANCE_INVALID", preflight, self.source, self.repo)

    def test_41_candidate_verifier_errors_are_rejected(self) -> None:
        candidate_id = read_json(self.source / "provenance.json")["candidate_id"].removeprefix("sha256:")
        governed = self.repo / "TEMP" / "data_build" / candidate_id
        governed.parent.mkdir(parents=True)
        shutil.copytree(self.candidate, governed)
        with mock.patch.object(publisher, "verify_candidate", return_value=("injected verifier error",)):
            self.assert_code("PROMOTION_PROVENANCE_INVALID", preflight, self.source, self.repo)

    def test_42_manual_runtime_readiness_self_assertion_is_rejected(self) -> None:
        self.make_ready()
        with self.authority_patch(self.current_authority):
            self.assert_code("PROMOTION_PROVENANCE_INVALID", preflight, self.source, self.repo)

    def test_43_candidate_blocker_must_be_preserved(self) -> None:
        readiness = self.make_ready()
        authority = dict(readiness)
        authority["blockers"] = [{"id": "FUTURE-BLOCKER", "status": "OPEN", "summary": "test"}]
        with self.authority_patch(authority):
            self.assert_code("PROMOTION_PROVENANCE_INVALID", preflight, self.source, self.repo)

    def test_44_candidate_production_false_keeps_promotion_blocked(self) -> None:
        with self.authority_patch(self.current_authority):
            self.assert_code("PROMOTION_PRODUCTION_NOT_READY", preflight, self.source, self.repo)

    def test_45_candidate_publish_false_is_not_allowed_after_production(self) -> None:
        readiness = self.make_ready(publish_allowed=False)
        with self.authority_patch(readiness):
            self.assert_code("PROMOTION_NOT_ALLOWED", preflight, self.source, self.repo)

    def test_46_nonblocking_materializer_local_blocker_is_allowed(self) -> None:
        local = {
            "blocks_production": False,
            "blocks_publish": False,
            "id": "LOCAL-CHECK",
            "status": "OPEN",
            "summary": "test",
        }
        runtime_readiness = self.make_ready(blockers=[local])
        authority = dict(runtime_readiness)
        authority["blockers"] = []
        with self.authority_patch(authority):
            self.assertFalse(preflight(self.source, self.repo).applied)

    def test_47_transaction_parent_reparse_is_rejected_without_mutation(self) -> None:
        readiness = self.make_ready()
        before = hashes(self.target)
        parent = self.repo / "TEMP" / "runtime_publisher_transactions"
        original = publisher._is_reparse_point
        with self.authority_patch(readiness):
            with mock.patch.object(
                publisher,
                "_is_reparse_point",
                side_effect=lambda path: Path(path) == parent or original(path),
            ):
                self.assert_code("PROMOTION_ATOMIC_REPLACE_FAILED", promote, self.source, self.repo)
        self.assertEqual(before, hashes(self.target))

    def test_48_transaction_resolved_escape_is_rejected_without_mutation(self) -> None:
        readiness = self.make_ready()
        before = hashes(self.target)
        parent = self.repo / "TEMP" / "runtime_publisher_transactions"
        outside = self.repo / "outside"
        outside.mkdir()
        original = publisher._resolve_strict

        def injected(path: Path) -> Path:
            if Path(path) == parent:
                return outside.resolve()
            return original(path)

        with self.authority_patch(readiness):
            with mock.patch.object(publisher, "_resolve_strict", side_effect=injected):
                self.assert_code("PROMOTION_ATOMIC_REPLACE_FAILED", promote, self.source, self.repo)
        self.assertEqual(before, hashes(self.target))

    def test_49_transaction_mkdir_error_is_structured(self) -> None:
        readiness = self.make_ready()
        before = hashes(self.target)
        with self.authority_patch(readiness):
            with mock.patch.object(publisher, "_create_transaction_root", side_effect=OSError("injected mkdir")):
                self.assert_code("PROMOTION_ATOMIC_REPLACE_FAILED", promote, self.source, self.repo)
        self.assertEqual(before, hashes(self.target))

    def test_50_lock_open_error_is_structured(self) -> None:
        readiness = self.make_ready()
        before = hashes(self.target)
        with self.authority_patch(readiness):
            with mock.patch.object(publisher.os, "open", side_effect=OSError("injected lock")):
                self.assert_code("PROMOTION_ATOMIC_REPLACE_FAILED", promote, self.source, self.repo)
        self.assertEqual(before, hashes(self.target))

    def test_51_cli_filesystem_failure_is_json_without_traceback(self) -> None:
        readiness = self.make_ready()
        before = hashes(ROOT / "src" / "client" / "runtime_package")
        stderr = io.StringIO()
        with self.authority_patch(readiness):
            with mock.patch.object(publisher, "_create_transaction_root", side_effect=OSError("injected filesystem")):
                with contextlib.redirect_stderr(stderr):
                    code = cli_main(["--source", str(self.source), "--apply"])
        payload = json.loads(stderr.getvalue())
        self.assertNotEqual(0, code)
        self.assertEqual("PROMOTION_ATOMIC_REPLACE_FAILED", payload["code"])
        self.assertNotIn("Traceback", stderr.getvalue())
        self.assertEqual(before, hashes(ROOT / "src" / "client" / "runtime_package"))


if __name__ == "__main__":
    unittest.main()
