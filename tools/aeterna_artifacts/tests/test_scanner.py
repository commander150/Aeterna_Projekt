from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import tempfile
import unittest

from tools.aeterna_artifacts.model import ArtifactRecord, Scope
from tools.aeterna_artifacts.scanner import (
    analyze_dependency_graph,
    scan_repository,
    validate_record_set,
)


def managed_markdown(
    artifact_id: str = "AET-DOC-TEST",
    *,
    title: str | None = "Managed title",
    kind: str = "document",
) -> str:
    heading = f"# {title}\n" if title is not None else "Body without a heading.\n"
    return f"""---
artifact_id: {artifact_id}
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
{heading}"""


def record(**overrides: object) -> ArtifactRecord:
    values: dict[str, object] = {
        "artifact_id": "AET-DOC-TEST",
        "kind": "document",
        "type": "reference",
        "version": "1.0",
        "lifecycle": "active",
        "integration": "current",
        "authority": "reference",
        "generated": False,
        "depends_on": (),
        "supersedes": (),
        "path": "Docs/Test.md",
        "scope": Scope.ACTIVE,
        "title": "Test",
    }
    values.update(overrides)
    return ArtifactRecord(**values)  # type: ignore[arg-type]


class ScannerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name)

    def write(self, relative_path: str, content: str) -> Path:
        path = self.root / Path(relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
        return path

    def test_valid_managed_artifact_discovery(self) -> None:
        self.write("Docs/managed.md", managed_markdown())

        result = scan_repository(self.root)

        self.assertEqual((), result.diagnostics)
        self.assertEqual(("AET-DOC-TEST",), tuple(item.artifact_id for item in result.artifacts))

    def test_legacy_active_markdown_is_ignored(self) -> None:
        self.write("Docs/legacy.md", "# Legacy document\n")

        result = scan_repository(self.root)

        self.assertEqual((), result.artifacts)
        self.assertEqual((), result.diagnostics)

    def test_learning_is_excluded(self) -> None:
        self.write("LEARNING/managed.md", managed_markdown())
        self.assertEqual((), scan_repository(self.root).artifacts)

    def test_archive_is_excluded(self) -> None:
        self.write("archive/managed.md", managed_markdown())
        self.assertEqual((), scan_repository(self.root).artifacts)

    def test_temp_is_excluded(self) -> None:
        self.write("TEMP/managed.md", managed_markdown())
        self.assertEqual((), scan_repository(self.root).artifacts)

    def test_venv_is_excluded(self) -> None:
        self.write(".venv/managed.md", managed_markdown())
        self.assertEqual((), scan_repository(self.root).artifacts)

    def test_git_directory_is_excluded(self) -> None:
        self.write(".git/managed.md", managed_markdown())
        self.assertEqual((), scan_repository(self.root).artifacts)

    def test_generated_directory_is_excluded(self) -> None:
        self.write("project/generated/managed.md", managed_markdown())
        self.assertEqual((), scan_repository(self.root).artifacts)

    def test_project_managed_directories_are_not_broadly_excluded(self) -> None:
        self.write("project/planning/managed.md", managed_markdown())

        result = scan_repository(self.root)

        self.assertEqual(("AET-DOC-TEST",), tuple(item.artifact_id for item in result.artifacts))
        self.assertEqual(("project/planning/managed.md",), tuple(item.path for item in result.artifacts))

    def test_path_is_repository_relative_posix_and_unicode_safe(self) -> None:
        self.write("Dokumentáció/Árvíztűrő.md", managed_markdown())

        artifact = scan_repository(self.root).artifacts[0]

        self.assertEqual("Dokumentáció/Árvíztűrő.md", artifact.path)
        self.assertIs(Scope.ACTIVE, artifact.scope)
        self.assertNotIn("\\", artifact.path)
        self.assertFalse(Path(artifact.path).is_absolute())

    def test_h1_title_extraction(self) -> None:
        self.write("Docs/managed.md", managed_markdown(title="AETERNA cím"))
        self.assertEqual("AETERNA cím", scan_repository(self.root).artifacts[0].title)

    def test_missing_h1_is_an_error(self) -> None:
        self.write("Docs/managed.md", managed_markdown(title=None))

        result = scan_repository(self.root)

        self.assertIn("DOC_TITLE_MISSING", {item.code for item in result.diagnostics})
        self.assertEqual((), result.artifacts)

    def test_duplicate_artifact_id_is_an_error(self) -> None:
        self.write("Docs/one.md", managed_markdown())
        self.write("Docs/two.md", managed_markdown())

        result = scan_repository(self.root)

        self.assertIn("DOC_DUPLICATE_ARTIFACT_ID", {item.code for item in result.diagnostics})

    def test_case_insensitive_path_collision_detection(self) -> None:
        first = record(path="Docs/Test.md")
        second = replace(first, artifact_id="AET-DOC-OTHER", path="docs/test.md")

        diagnostics = validate_record_set((first, second))

        self.assertIn("DOC_PATH_CASE_COLLISION", {item.code for item in diagnostics})

    def test_invalid_registry_paths_are_rejected(self) -> None:
        values = (r"Docs\Test.md", "C:/Docs/Test.md", "/Docs/Test.md", "../Test.md")
        for path in values:
            with self.subTest(path=path):
                diagnostics = validate_record_set((record(path=path),))
                self.assertIn("DOC_INVALID_REGISTRY_PATH", {item.code for item in diagnostics})

    def test_invalid_managed_metadata_fails_scan(self) -> None:
        self.write("Docs/managed.md", managed_markdown(kind="unknown"))

        result = scan_repository(self.root)

        self.assertIn("KIND_INVALID", {item.code for item in result.diagnostics})
        self.assertEqual((), result.artifacts)

    def test_missing_dependency_target_is_an_error(self) -> None:
        diagnostics = validate_record_set((
            record(depends_on=("AET-DOC-MISSING",)),
        ))

        self.assertIn("DOC_DEPENDENCY_MISSING", {item.code for item in diagnostics})

    def test_dependency_cycle_is_an_error(self) -> None:
        first = record(artifact_id="AET-DOC-FIRST", depends_on=("AET-DOC-SECOND",))
        second = record(
            artifact_id="AET-DOC-SECOND",
            path="Docs/Second.md",
            depends_on=("AET-DOC-FIRST",),
        )

        diagnostics = validate_record_set((first, second))

        self.assertIn("DOC_DEPENDENCY_CYCLE", {item.code for item in diagnostics})

    def test_dependency_graph_reports_self_dependency(self) -> None:
        graph = analyze_dependency_graph((
            record(depends_on=("AET-DOC-TEST",)),
        ))

        self.assertEqual(("AET-DOC-TEST",), graph.self_dependencies)

    def test_dependency_graph_reverse_and_transitive_dependents_are_deterministic(self) -> None:
        source = record(artifact_id="AET-DOC-SOURCE")
        direct = record(
            artifact_id="AET-DOC-DIRECT",
            path="Docs/Direct.md",
            depends_on=("AET-DOC-SOURCE",),
        )
        transitive = record(
            artifact_id="AET-DOC-TRANSITIVE",
            path="Docs/Transitive.md",
            depends_on=("AET-DOC-DIRECT",),
        )

        graph = analyze_dependency_graph((transitive, source, direct))

        self.assertEqual(("AET-DOC-DIRECT",), graph.reverse_for("AET-DOC-SOURCE"))
        self.assertEqual(
            ("AET-DOC-DIRECT", "AET-DOC-TRANSITIVE"),
            graph.transitive_dependents("AET-DOC-SOURCE"),
        )


if __name__ == "__main__":
    unittest.main()
