"""Read-only inspection of repository identity and Git state."""

from __future__ import annotations

from pathlib import Path
import subprocess

from .model import GitState, fail


def _git(root: Path, *arguments: str, binary: bool = False) -> bytes | str:
    try:
        result = subprocess.run(
            ["git", *arguments],
            cwd=root,
            check=False,
            capture_output=True,
        )
    except OSError as exc:
        fail("GIT_EXECUTION_ERROR", str(exc), exit_code=2)
    if result.returncode:
        message = result.stderr.decode("utf-8", errors="replace").strip()
        fail("GIT_EXECUTION_ERROR", message or "Git inspection failed.", exit_code=2)
    if binary:
        return result.stdout
    return result.stdout.decode("utf-8", errors="strict").strip()


def capture_git_state(repository_root: str | Path) -> GitState:
    requested = Path(repository_root).resolve()
    canonical = Path(str(_git(requested, "rev-parse", "--show-toplevel"))).resolve()
    branch = str(_git(canonical, "branch", "--show-current"))
    head = str(_git(canonical, "rev-parse", "HEAD"))
    unstaged_raw = bytes(_git(canonical, "diff", "--name-only", "-z", binary=True))
    untracked_raw = bytes(_git(
        canonical,
        "ls-files",
        "--others",
        "--exclude-standard",
        "-z",
        binary=True,
    ))
    staged_raw = bytes(_git(canonical, "diff", "--cached", "--name-only", "-z", binary=True))
    worktree = tuple(sorted({
        part.decode("utf-8", errors="strict")
        for part in (unstaged_raw + untracked_raw).split(b"\0")
        if part
    }))
    staged = tuple(sorted(
        part.decode("utf-8", errors="strict")
        for part in staged_raw.split(b"\0")
        if part
    ))
    return GitState(canonical, branch, head, worktree, staged)
