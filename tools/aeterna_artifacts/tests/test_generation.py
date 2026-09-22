from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from tools.aeterna_artifacts.generation import (
    DOCUMENT_INDEX_PATH,
    REGISTRY_PATH,
    GenerationBlockedError,
    build_generated_content,
    generate_repository,
)
from tools.aeterna_artifacts.model import ArtifactRecord, Scope


EXPECTED_FIELDS = {
    "artifact_id",
    "title",
    "kind",
    "type",
    "version",
    "lifecycle",
    "integration",
    "authority",
    "generated",
    "depends_on",
    "supersedes",
    "scope",
    "path",
}


def record(
    artifact_id: str,
    path: str,
    title: str,
) -> ArtifactRecord:
    return ArtifactRecord(
        artifact_id=artifact_id,
        kind="document",
        type="reference",
        version="1.0",
        lifecycle="active",
        integration="current",
        authority="reference",
        generated=False,
        depends_on=(),
        supersedes=(),
        path=path,
        scope=Scope.ACTIVE,
        title=title,
    )


def managed_markdown(kind: str = "document") -> str:
    return f"""---
artifact_id: AET-DOC-TEST
kind: {kind}
type: reference
version: "1.0"
lifecycle: active
integration: current
authority: reference
generated: false
depends_on: []
supersedes: []
---
# Test
"""


class GenerationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.records = (
            record("AET-DOC-ZETA", "Dokumentáció/Zéta.md", "Zéta cím"),
            record("AET-DOC-ALPHA", "Docs/Alpha.md", "Alpha"),
        )

    def test_registry_schema_and_exact_record_fields(self) -> None:
        payload = json.loads(build_generated_content(self.records).registry)

        self.assertEqual("0.1", payload["registry_schema_version"])
        self.assertEqual("native-artifact-metadata", payload["source_model"])
        self.assertEqual(EXPECTED_FIELDS, set(payload["artifacts"][0]))

    def test_registry_is_sorted_by_artifact_id(self) -> None:
        payload = json.loads(build_generated_content(self.records).registry)
        self.assertEqual(
            ["AET-DOC-ALPHA", "AET-DOC-ZETA"],
            [item["artifact_id"] for item in payload["artifacts"]],
        )

    def test_unicode_is_preserved(self) -> None:
        registry = build_generated_content(self.records).registry
        self.assertIn("Dokumentáció/Zéta.md", registry)
        self.assertIn("Zéta cím", registry)
        self.assertNotIn("\\u00e9", registry)

    def test_output_contains_no_absolute_or_backslash_paths(self) -> None:
        payload = json.loads(build_generated_content(self.records).registry)
        for artifact in payload["artifacts"]:
            self.assertNotIn("\\", artifact["path"])
            self.assertFalse(Path(artifact["path"]).is_absolute())

    def test_invalid_path_blocks_generation(self) -> None:
        invalid = record("AET-DOC-INVALID", r"Docs\Invalid.md", "Invalid")
        with self.assertRaises(GenerationBlockedError):
            build_generated_content((invalid,))

    def test_registry_has_no_timestamp_and_exact_final_newline(self) -> None:
        registry = build_generated_content(self.records).registry
        self.assertNotIn("timestamp", registry.casefold())
        self.assertTrue(registry.endswith("\n"))
        self.assertFalse(registry.endswith("\n\n"))

    def test_outputs_use_lf_only(self) -> None:
        content = build_generated_content(self.records)
        self.assertNotIn("\r", content.registry)
        self.assertNotIn("\r", content.document_index)

    def test_document_index_order_matches_registry(self) -> None:
        index = build_generated_content(self.records).document_index
        self.assertLess(index.index("AET-DOC-ALPHA"), index.index("AET-DOC-ZETA"))
        self.assertIn("GENERATED FILE — DO NOT EDIT MANUALLY", index)

    def test_two_builds_are_byte_for_byte_identical(self) -> None:
        first = build_generated_content(self.records)
        second = build_generated_content(tuple(reversed(self.records)))
        self.assertEqual(first.registry.encode("utf-8"), second.registry.encode("utf-8"))
        self.assertEqual(
            first.document_index.encode("utf-8"),
            second.document_index.encode("utf-8"),
        )

    def test_failed_scan_produces_no_partial_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "Docs" / "invalid.md"
            source.parent.mkdir(parents=True)
            source.write_text(managed_markdown(kind="unknown"), encoding="utf-8")

            result = generate_repository(root)

            self.assertIn("KIND_INVALID", {item.code for item in result.diagnostics})
            self.assertFalse((root / REGISTRY_PATH).exists())
            self.assertFalse((root / DOCUMENT_INDEX_PATH).exists())

    def test_successful_generation_writes_only_expected_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "Docs" / "managed.md"
            source.parent.mkdir(parents=True)
            source.write_text(managed_markdown(), encoding="utf-8")

            result = generate_repository(root)

            self.assertEqual(
                (REGISTRY_PATH.as_posix(), DOCUMENT_INDEX_PATH.as_posix()),
                result.written_paths,
            )
            self.assertTrue((root / REGISTRY_PATH).is_file())
            self.assertTrue((root / DOCUMENT_INDEX_PATH).is_file())


if __name__ == "__main__":
    unittest.main()
