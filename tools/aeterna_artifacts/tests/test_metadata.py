from __future__ import annotations

import builtins
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools.aeterna_artifacts.metadata import parse_metadata, read_metadata


YAML_AVAILABLE = importlib.util.find_spec("yaml") is not None

VALID_FRONT_MATTER = """---
artifact_id: AET-DOC-PROJECT-PLAN
kind: document
type: project-plan
version: "6.9"
lifecycle: active
integration: current
authority: project-direction
generated: false
depends_on: []
supersedes: []
---
# Body
"""


class MetadataParserTests(unittest.TestCase):
    def write_temporary_markdown(self, content: str) -> Path:
        temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        path = Path(temporary_directory.name) / "artifact.md"
        path.write_text(content, encoding="utf-8")
        return path

    @unittest.skipUnless(YAML_AVAILABLE, "PyYAML is not installed")
    def test_valid_yaml_front_matter(self) -> None:
        result = read_metadata(self.write_temporary_markdown(VALID_FRONT_MATTER))

        self.assertEqual((), result.diagnostics)
        self.assertIsNotNone(result.metadata)
        assert result.metadata is not None
        self.assertEqual("AET-DOC-PROJECT-PLAN", result.metadata.fields["artifact_id"])
        self.assertIs(False, result.metadata.fields["generated"])

    @unittest.skipUnless(YAML_AVAILABLE, "PyYAML is not installed")
    def test_utf8_bom(self) -> None:
        result = read_metadata(
            self.write_temporary_markdown("\ufeff" + VALID_FRONT_MATTER)
        )

        self.assertEqual((), result.diagnostics)
        self.assertIsNotNone(result.metadata)

    def test_markdown_without_metadata(self) -> None:
        result = read_metadata(self.write_temporary_markdown("# Body only\n"))

        self.assertIsNone(result.metadata)
        self.assertEqual("METADATA_MISSING", result.diagnostics[0].code)

    @unittest.skipUnless(YAML_AVAILABLE, "PyYAML is not installed")
    def test_malformed_yaml(self) -> None:
        result = read_metadata(
            self.write_temporary_markdown("---\nartifact_id: [broken\n---\n")
        )

        self.assertIsNone(result.metadata)
        self.assertEqual("METADATA_YAML_INVALID", result.diagnostics[0].code)

    def test_missing_pyyaml_is_a_structured_dependency_error(self) -> None:
        original_import = builtins.__import__

        def import_without_yaml(
            name: str,
            globals: object = None,
            locals: object = None,
            fromlist: tuple[str, ...] = (),
            level: int = 0,
        ) -> object:
            if name == "yaml":
                raise ImportError("controlled test: yaml unavailable")
            return original_import(name, globals, locals, fromlist, level)

        with patch("builtins.__import__", side_effect=import_without_yaml):
            result = parse_metadata(VALID_FRONT_MATTER)

        self.assertIsNone(result.metadata)
        self.assertEqual("DEPENDENCY_MISSING", result.diagnostics[0].code)


if __name__ == "__main__":
    unittest.main()
