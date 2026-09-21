from __future__ import annotations

import unittest

from tools.aeterna_artifacts.model import ArtifactMetadata
from tools.aeterna_artifacts.validation import (
    is_valid_artifact_id,
    validate_metadata,
)


def valid_fields(**overrides: object) -> dict[str, object]:
    fields: dict[str, object] = {
        "artifact_id": "AET-DOC-PROJECT-PLAN",
        "kind": "document",
        "type": "project-plan",
        "version": "6.9",
        "lifecycle": "active",
        "integration": "current",
        "authority": "project-direction",
        "generated": False,
        "depends_on": [],
        "supersedes": [],
    }
    fields.update(overrides)
    return fields


def diagnostic_codes(fields: dict[str, object]) -> set[str]:
    return {
        diagnostic.code
        for diagnostic in validate_metadata(ArtifactMetadata(fields))
    }


class ArtifactIdTests(unittest.TestCase):
    def test_valid_artifact_ids(self) -> None:
        values = (
            "AET-DOC-PROJECT-PLAN",
            "AET-DATA-CARDDATABASE",
            "AET-SOURCE-CARD-AUTHORING",
            "AET-GEN-DATA-SCHEMA",
            "AET-PKG-RUNTIME",
            "AET-BP-RELEASE-COMPATIBILITY",
            "AET-DOC-RELEASE-001-TARGET",
            "AET-DOC-AETERNA-0-0-1-TARGET",
            "AET-GEN-CURRENT-SOURCE-VERSIONS",
            "AET-DOC-PROTOTYPE-STATUS",
            "AET-DOC-PROJECT-PLAN-V1",
        )
        for value in values:
            with self.subTest(value=value):
                self.assertTrue(is_valid_artifact_id(value))

    def test_invalid_artifact_ids(self) -> None:
        values: tuple[object, ...] = (
            "DOC-PROJECT-PLAN",
            "AET-OTHER-PROJECT-PLAN",
            "aet-doc-project-plan",
            "AET-DOC-project-plan",
            "AET-DOC-PROJECT.PLAN",
            "AET-DOC-PROJECT/PLAN",
            "AET-DOC-PROJECT\\PLAN",
            "AET-DOC-PROJECT_PLAN",
            "AET-DOC-PROJECT PLAN",
            "AET-DOC-",
            "AET-DOC--PROJECT",
            42,
        )
        for value in values:
            with self.subTest(value=value):
                self.assertFalse(is_valid_artifact_id(value))


class MetadataValidationTests(unittest.TestCase):
    def test_valid_metadata_and_boolean_generated(self) -> None:
        self.assertEqual(set(), diagnostic_codes(valid_fields(generated=False)))

    def test_missing_artifact_id(self) -> None:
        fields = valid_fields()
        del fields["artifact_id"]
        self.assertIn("ARTIFACT_ID_REQUIRED", diagnostic_codes(fields))

    def test_invalid_artifact_id(self) -> None:
        codes = diagnostic_codes(valid_fields(artifact_id="DOC-PROJECT-PLAN"))
        self.assertIn("ARTIFACT_ID_INVALID", codes)

    def test_unknown_kind(self) -> None:
        self.assertIn("KIND_INVALID", diagnostic_codes(valid_fields(kind="unknown")))

    def test_unknown_type(self) -> None:
        self.assertIn("TYPE_INVALID", diagnostic_codes(valid_fields(type="unknown")))

    def test_unknown_lifecycle(self) -> None:
        codes = diagnostic_codes(valid_fields(lifecycle="unknown"))
        self.assertIn("LIFECYCLE_INVALID", codes)

    def test_unknown_integration(self) -> None:
        codes = diagnostic_codes(valid_fields(integration="unknown"))
        self.assertIn("INTEGRATION_INVALID", codes)

    def test_unknown_authority(self) -> None:
        codes = diagnostic_codes(valid_fields(authority="unknown"))
        self.assertIn("AUTHORITY_INVALID", codes)

    def test_generated_string_is_invalid(self) -> None:
        codes = diagnostic_codes(valid_fields(generated="false"))
        self.assertIn("GENERATED_INVALID", codes)

    def test_manual_document_requires_version(self) -> None:
        fields = valid_fields()
        del fields["version"]
        self.assertIn("VERSION_INVALID", diagnostic_codes(fields))

    def test_valid_depends_on(self) -> None:
        fields = valid_fields(depends_on=["AET-DATA-CARDDATABASE"])
        self.assertEqual(set(), diagnostic_codes(fields))

    def test_invalid_depends_on_element(self) -> None:
        codes = diagnostic_codes(valid_fields(depends_on=["bad-id"]))
        self.assertIn("DEPENDS_ON_ID_INVALID", codes)

    def test_depends_on_must_be_a_list(self) -> None:
        codes = diagnostic_codes(valid_fields(depends_on="AET-DATA-CARDDATABASE"))
        self.assertIn("DEPENDS_ON_INVALID", codes)

    def test_self_dependency(self) -> None:
        codes = diagnostic_codes(valid_fields(depends_on=["AET-DOC-PROJECT-PLAN"]))
        self.assertIn("DEPENDS_ON_SELF", codes)

    def test_valid_supersedes(self) -> None:
        fields = valid_fields(supersedes=["AET-DOC-OLD-PROJECT-PLAN"])
        self.assertEqual(set(), diagnostic_codes(fields))

    def test_invalid_supersedes_element(self) -> None:
        codes = diagnostic_codes(valid_fields(supersedes=["bad-id"]))
        self.assertIn("SUPERSEDES_ID_INVALID", codes)

    def test_supersedes_must_be_a_list(self) -> None:
        codes = diagnostic_codes(valid_fields(supersedes=None))
        self.assertIn("SUPERSEDES_INVALID", codes)

    def test_self_supersedes(self) -> None:
        codes = diagnostic_codes(valid_fields(supersedes=["AET-DOC-PROJECT-PLAN"]))
        self.assertIn("SUPERSEDES_SELF", codes)


if __name__ == "__main__":
    unittest.main()
