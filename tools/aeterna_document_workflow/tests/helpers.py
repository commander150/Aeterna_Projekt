"""Isolated repository fixtures rooted in the project-local ignored TEMP tree."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile

from tools.aeterna_artifacts.generation import (
    DOCUMENT_INDEX_PATH,
    REGISTRY_PATH,
    build_generated_content,
)
from tools.aeterna_artifacts.scanner import scan_repository
from tools.aeterna_document_workflow.content import inspect_markdown


TEST_ROOT = Path("TEMP/pilot7c_read_only_document_workflow/test_workspaces").resolve()


def markdown(
    artifact_id: str,
    title: str,
    *,
    version: str = "1.0",
    authority: str = "project-direction",
    generated: bool = False,
    depends_on: tuple[str, ...] = (),
    body: str = "Baseline body.",
    newline: str = "\n",
) -> bytes:
    lines = [
        "---",
        f"artifact_id: {artifact_id}",
        "kind: document",
        "type: reference",
        f'version: "{version}"',
        "lifecycle: active",
        "integration: current",
        f"authority: {authority}",
        f"generated: {'true' if generated else 'false'}",
        "depends_on: []" if not depends_on else "depends_on:",
    ]
    lines.extend(f"  - {item}" for item in depends_on)
    lines.extend([
        "supersedes: []",
        "---",
        "",
        f"# {title}",
        "",
        body,
        "",
    ])
    return newline.join(lines).encode("utf-8")


class RepositoryFixture:
    def __init__(self) -> None:
        TEST_ROOT.mkdir(parents=True, exist_ok=True)
        self.root = Path(tempfile.mkdtemp(prefix="repo_", dir=TEST_ROOT))
        self._write(".gitignore", b"TEMP/\n")
        self._write(
            "project/planning/TARGET.md",
            markdown("AET-DOC-TARGET", "Target"),
        )
        self._write(
            "project/governance/DEPENDENT.md",
            markdown(
                "AET-DOC-DEPENDENT",
                "Dependent",
                depends_on=("AET-DOC-TARGET",),
            ),
        )
        self._write(
            "project/governance/TRANSITIVE.md",
            markdown(
                "AET-DOC-TRANSITIVE",
                "Transitive",
                depends_on=("AET-DOC-DEPENDENT",),
            ),
        )
        self._write(
            "project/derived/GENERATED.md",
            markdown(
                "AET-GEN-DERIVED",
                "Generated",
                generated=True,
                depends_on=("AET-DOC-TARGET",),
            ),
        )
        scan = scan_repository(self.root)
        generated = build_generated_content(scan.artifacts)
        self._write(REGISTRY_PATH, generated.registry.encode("utf-8"))
        self._write(DOCUMENT_INDEX_PATH, generated.document_index.encode("utf-8"))
        self.git("init", "-b", "main")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "user.name", "Fixture")
        self.git("add", ".")
        self.git("commit", "-m", "fixture baseline")

    @property
    def target(self) -> Path:
        return self.root / "project/planning/TARGET.md"

    @property
    def head(self) -> str:
        return self.git("rev-parse", "HEAD")

    def _write(self, relative: str | Path, data: bytes) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def git(self, *arguments: str) -> str:
        result = subprocess.run(
            ["git", *arguments],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return result.stdout.strip()

    def candidate(self, data: bytes, name: str = "candidate.md") -> Path:
        return self._write(Path("TEMP") / "operation" / name, data)

    def manifest(
        self,
        candidate: Path,
        *,
        change_class: str = "body-only",
        version_intent: str = "minor",
        metadata_delta: list[dict[str, object]] | None = None,
        **overrides: object,
    ) -> Path:
        baseline = inspect_markdown(self.target)
        candidate_snapshot = inspect_markdown(candidate)
        payload: dict[str, object] = {
            "schema_version": "aeterna-document-update-manifest/0.1",
            "artifact_id": "AET-DOC-TARGET",
            "expected_branch": "main",
            "expected_head": self.head,
            "expected_path": "project/planning/TARGET.md",
            "baseline_sha256": baseline.sha256,
            "metadata_fingerprint": baseline.metadata_fingerprint,
            "change_class": change_class,
            "version_intent": version_intent,
            "candidate_path": candidate.name,
            "candidate_sha256": candidate_snapshot.sha256,
            "metadata_delta": metadata_delta or [],
        }
        payload.update(overrides)
        path = candidate.parent / "manifest.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
        return path

    def tracked_bytes(self) -> dict[str, bytes]:
        names = self.git("ls-files").splitlines()
        return {name: (self.root / name).read_bytes() for name in names}

    def close(self) -> None:
        def remove_readonly(function: object, path: str, error: object) -> None:
            os.chmod(path, stat.S_IWRITE)
            function(path)

        shutil.rmtree(self.root, onexc=remove_readonly)
