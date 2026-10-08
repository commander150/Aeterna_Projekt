from __future__ import annotations

import codecs
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

from tools.aeterna_document_workflow.content import inspect_markdown
from tools.aeterna_document_workflow.create_planner import (
    build_create_plan,
    validate_create_plan_integrity,
)
from tools.aeterna_document_workflow.model import WorkflowError
from tools.aeterna_document_workflow.transaction import apply_plan

from .helpers import RepositoryFixture, markdown


class CreatePlannerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = RepositoryFixture()

    def tearDown(self) -> None:
        self.fixture.close()

    def _valid(self, **options: object) -> tuple[Path, Path]:
        data = markdown(
            str(options.pop("artifact_id", "AET-DOC-NEW")),
            str(options.pop("title", "New Document")),
            version=str(options.pop("version", "0.1")),
            authority=str(options.pop("authority", "project-direction")),
            depends_on=tuple(options.pop("depends_on", ())),
        )
        candidate = self.fixture.candidate(data, "create.md")
        manifest = self.fixture.create_manifest(candidate, **options)
        return candidate, manifest

    def _rewrite_candidate(
        self,
        candidate: Path,
        manifest: Path,
        data: bytes,
        *,
        synchronize_metadata: bool = True,
    ) -> None:
        candidate.write_bytes(data)
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        payload["candidate_sha256"] = hashlib.sha256(data).hexdigest()
        if synchronize_metadata:
            snapshot = inspect_markdown(candidate)
            fields = dict(snapshot.metadata.fields)
            payload["candidate_metadata"] = fields
            payload["candidate_metadata_fingerprint"] = snapshot.metadata_fingerprint
            if isinstance(fields.get("artifact_id"), str):
                payload["artifact_id"] = fields["artifact_id"]
            if isinstance(fields.get("authority"), str):
                payload["declared_authority"] = fields["authority"]
            if isinstance(fields.get("version"), str):
                payload["initial_version"] = fields["version"]
        manifest.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

    def _error(self, manifest: Path) -> str:
        with self.assertRaises(WorkflowError) as caught:
            build_create_plan(self.fixture.root, manifest)
        return caught.exception.diagnostics[0].code

    def test_valid_plan_is_deterministic_read_only_and_complete(self) -> None:
        _, manifest = self._valid(depends_on=("AET-DOC-TARGET",))
        before = self.fixture.tracked_bytes()

        first = build_create_plan(self.fixture.root, manifest)
        second = build_create_plan(self.fixture.root, manifest)

        self.assertEqual(first, second)
        self.assertEqual(first["plan_semantic_sha256"], second["plan_semantic_sha256"])
        self.assertEqual("aeterna-document-create-plan/0.1", first["schema_version"])
        self.assertEqual("create", first["operation"])
        self.assertEqual(4, first["repository"]["baseline_artifact_count"])
        self.assertEqual(5, first["repository"]["expected_artifact_count_after"])
        self.assertRegex(first["repository"]["baseline_artifact_set_identity"], r"^[0-9a-f]{64}$")
        self.assertEqual("project/planning/NEW.md", first["candidate"]["canonical_path"])
        self.assertNotIn("TEMP", first["candidate"]["canonical_path"])
        self.assertEqual(["AET-DOC-TARGET"], first["impact"]["forward_dependencies"])
        self.assertEqual("IN_MEMORY_READ_ONLY", first["generated"]["mode"])
        self.assertEqual(
            ["DOCUMENT_CREATE", "GENERATED_UPDATE", "GENERATED_UPDATE"],
            [item["operation"] for item in first["expected_changes"]],
        )
        self.assertEqual("HIGH", first["authority"]["risk"])
        self.assertEqual({"initial_version": "0.1"}, first["version"])
        self.assertNotIn("change", first)
        self.assertNotIn("metadata_delta", first)
        self.assertNotIn("sha256", first["baseline"])
        self.assertEqual(before, self.fixture.tracked_bytes())
        self.assertEqual("", self.fixture.git("status", "--short"))

    def test_normal_authority_and_pending_integration_are_accepted(self) -> None:
        candidate, manifest = self._valid(authority="operational-workflow")
        data = candidate.read_text(encoding="utf-8").replace("integration: current", "integration: pending_integration").encode("utf-8")
        self._rewrite_candidate(candidate, manifest, data)
        plan = build_create_plan(self.fixture.root, manifest)
        self.assertEqual("NORMAL", plan["authority"]["risk"])
        self.assertEqual("pending_integration", plan["candidate"]["metadata"]["integration"])

    def test_cli_plan_create_outputs_json_without_writes(self) -> None:
        _, manifest = self._valid()
        before = self.fixture.tracked_bytes()
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "tools.aeterna_document_workflow.cli",
                "plan-create",
                "--manifest",
                str(manifest),
                "--repo",
                str(self.fixture.root),
            ],
            cwd=Path(__file__).resolve().parents[3],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("create", json.loads(result.stdout)["operation"])
        self.assertEqual(before, self.fixture.tracked_bytes())

    def test_manifest_schema_exact_fields_and_derived_overrides_block(self) -> None:
        _, manifest = self._valid()
        baseline = json.loads(manifest.read_text(encoding="utf-8"))
        cases = {
            "wrong-schema": {**baseline, "schema_version": "wrong"},
            "missing": {key: value for key, value in baseline.items() if key != "artifact_id"},
            "unknown": {**baseline, "unknown": True},
            "derived-override": {**baseline, "target_must_be_absent": False},
            "malformed": {**baseline, "candidate_metadata": []},
        }
        for name, payload in cases.items():
            with self.subTest(name=name):
                manifest.write_text(json.dumps(payload), encoding="utf-8")
                self.assertTrue(self._error(manifest).startswith("CREATE_"))

    def test_candidate_identity_mismatches_block(self) -> None:
        fields = (
            ("candidate_sha256", "0" * 64, "CREATE_CANDIDATE_HASH_MISMATCH"),
            ("candidate_metadata_fingerprint", "0" * 64, "CREATE_METADATA_FINGERPRINT_MISMATCH"),
            ("declared_authority", "reference", "CREATE_AUTHORITY_MISMATCH"),
            ("initial_version", "9.9", "CREATE_INITIAL_VERSION_MISMATCH"),
            ("artifact_id", "AET-DOC-OTHER", "CREATE_ARTIFACT_ID_MISMATCH"),
        )
        for index, (field, value, code) in enumerate(fields):
            with self.subTest(field=field):
                if index:
                    self.fixture.close()
                    self.fixture = RepositoryFixture()
                _, manifest = self._valid()
                payload = json.loads(manifest.read_text(encoding="utf-8"))
                payload[field] = value
                manifest.write_text(json.dumps(payload), encoding="utf-8")
                self.assertEqual(code, self._error(manifest))

        self.fixture.close()
        self.fixture = RepositoryFixture()
        _, manifest = self._valid()
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        payload["candidate_metadata"] = dict(payload["candidate_metadata"])
        payload["candidate_metadata"]["type"] = "workflow"
        manifest.write_text(json.dumps(payload), encoding="utf-8")
        self.assertEqual("CREATE_CANDIDATE_METADATA_MISMATCH", self._error(manifest))

    def test_candidate_byte_policy_blocks_invalid_forms(self) -> None:
        valid = markdown("AET-DOC-NEW", "New Document", version="0.1")
        cases = {
            "invalid-utf8": b"\xff" + valid,
            "bom": codecs.BOM_UTF8 + valid,
            "crlf": valid.replace(b"\n", b"\r\n"),
            "mixed": valid.replace(b"\n", b"\r\n", 1),
            "lone-cr": valid.replace(b"\n", b"\r", 1),
        }
        for index, (name, data) in enumerate(cases.items()):
            with self.subTest(name=name):
                if index:
                    self.fixture.close()
                    self.fixture = RepositoryFixture()
                candidate, manifest = self._valid()
                self._rewrite_candidate(candidate, manifest, data, synchronize_metadata=False)
                self.assertIn(
                    self._error(manifest),
                    {"CONTENT_UTF8_INVALID", "CREATE_CANDIDATE_BYTE_CONVENTION", "CONTENT_NEWLINE_MIXED", "CONTENT_LONE_CR"},
                )

    def test_h1_contract_blocks_missing_empty_and_multiple(self) -> None:
        cases = {
            "missing": "Body only.",
            "empty": "# ",
            "multiple": "# One\n\n# Two",
        }
        for index, (name, body) in enumerate(cases.items()):
            with self.subTest(name=name):
                if index:
                    self.fixture.close()
                    self.fixture = RepositoryFixture()
                candidate, manifest = self._valid()
                text = candidate.read_text(encoding="utf-8")
                start = text.index("# New Document")
                data = (text[:start] + body + "\n").encode("utf-8")
                self._rewrite_candidate(candidate, manifest, data)
                self.assertIn(self._error(manifest), {"CREATE_H1_MISSING", "CREATE_H1_EMPTY", "CREATE_H1_MULTIPLE"})

    def test_create_metadata_policy_blocks_invalid_forms(self) -> None:
        mutations = {
            "missing": lambda text: text.replace('version: "0.1"\n', ""),
            "unknown": lambda text: text.replace("supersedes: []", "unknown: value\nsupersedes: []"),
            "kind": lambda text: text.replace("kind: document", "kind: package"),
            "generated": lambda text: text.replace("generated: false", "generated: true"),
            "lifecycle": lambda text: text.replace("lifecycle: active", "lifecycle: draft"),
            "integration": lambda text: text.replace("integration: current", "integration: recovery_candidate"),
            "supersedes": lambda text: text.replace("supersedes: []", "supersedes: [AET-DOC-TARGET]"),
            "duplicate-dependency": lambda text: text.replace("depends_on: []", "depends_on: [AET-DOC-TARGET, AET-DOC-TARGET]"),
            "invalid-dependency": lambda text: text.replace("depends_on: []", "depends_on: [bad-id]"),
            "self-dependency": lambda text: text.replace("depends_on: []", "depends_on: [AET-DOC-NEW]"),
        }
        for index, (name, mutate) in enumerate(mutations.items()):
            with self.subTest(name=name):
                if index:
                    self.fixture.close()
                    self.fixture = RepositoryFixture()
                candidate, manifest = self._valid()
                data = mutate(candidate.read_text(encoding="utf-8")).encode("utf-8")
                self._rewrite_candidate(candidate, manifest, data)
                self.assertNotEqual("", self._error(manifest))

    def test_duplicate_artifact_id_and_missing_dependency_block(self) -> None:
        candidate, manifest = self._valid(artifact_id="AET-DOC-TARGET")
        self.assertEqual("CREATE_ARTIFACT_ID_COLLISION", self._error(manifest))

        self.fixture.close()
        self.fixture = RepositoryFixture()
        _, manifest = self._valid(depends_on=("AET-DOC-MISSING",))
        self.assertEqual("DOC_DEPENDENCY_MISSING", self._error(manifest))

    def test_create_plan_integrity_is_separate_and_fail_closed(self) -> None:
        _, manifest = self._valid()
        plan = build_create_plan(self.fixture.root, manifest)
        self.assertIs(plan, validate_create_plan_integrity(plan))
        tampered = dict(plan)
        tampered["artifact_id"] = "AET-DOC-TAMPERED"
        with self.assertRaises(WorkflowError) as caught:
            validate_create_plan_integrity(tampered)
        self.assertEqual("CREATE_PLAN_INTEGRITY_MISMATCH", caught.exception.diagnostics[0].code)

    def test_apply_rejects_create_plan_before_tracked_writes(self) -> None:
        candidate, manifest = self._valid()
        plan = build_create_plan(self.fixture.root, manifest)
        plan_path = candidate.parent / "create-plan.json"
        plan_path.write_text(json.dumps(plan), encoding="utf-8", newline="\n")
        before = self.fixture.tracked_bytes()
        with self.assertRaises(WorkflowError) as caught:
            apply_plan(plan_path, self.fixture.root, candidate.parent / "review")
        self.assertEqual("PLAN_SCHEMA_INVALID", caught.exception.diagnostics[0].code)
        self.assertEqual(before, self.fixture.tracked_bytes())
        self.assertFalse((candidate.parent / "review").exists())


if __name__ == "__main__":
    unittest.main()
