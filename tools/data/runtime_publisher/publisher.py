"""Governed, fail-closed promotion of canonical runtime materializations."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import uuid
from collections import Counter
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

from tools.data.canonical_producer import verify_candidate
from tools.data.runtime_materializer import compute_runtime_package_id, validate_runtime_package
from tools.data.runtime_materializer.policy import (
    IDENTITY_PAYLOAD_FILES,
    MATERIALIZATION_POLICY_ID,
    MATERIALIZATION_PROFILE_ID,
    MATERIALIZER_CONTRACT_VERSION,
    MATERIALIZER_ID,
    OUTPUT_FILES,
    RUNTIME_ID_DOMAIN,
)


TARGET_RELATIVE_PATH = Path("src") / "client" / "runtime_package"
TRANSACTION_ROOT_RELATIVE_PATH = Path("TEMP") / "runtime_publisher_transactions"
LOCK_RELATIVE_PATH = Path("TEMP") / "runtime_publisher.lock"
CANONICAL_SOURCE_COMPONENTS = frozenset({"CARDDATABASE", "REGISTRY"})


class PromotionError(RuntimeError):
    """A stable fail-closed promotion rejection."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class PromotionResult:
    source_directory: Path
    target_directory: Path
    runtime_package_id: str
    file_count: int
    applied: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "applied": self.applied,
            "file_count": self.file_count,
            "runtime_package_id": self.runtime_package_id,
            "source_directory": str(self.source_directory),
            "target_directory": str(self.target_directory),
        }


def _repository_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _tree_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): _sha256_file(path)
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PromotionError("PROMOTION_PACKAGE_INVALID", f"Cannot read package JSON: {path.name}") from exc
    if not isinstance(value, dict):
        raise PromotionError("PROMOTION_PACKAGE_INVALID", f"Package JSON root is not an object: {path.name}")
    return value


def _is_reparse_point(path: Path) -> bool:
    try:
        details = path.lstat()
    except OSError:
        return False
    attributes = getattr(details, "st_file_attributes", 0)
    reparse_attribute = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return path.is_symlink() or bool(attributes & reparse_attribute)


def _relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _assert_no_reparse_below(path: Path, boundary: Path, code: str) -> None:
    if not _relative_to(path, boundary):
        raise PromotionError(code, f"Path is outside its governed boundary: {path}")
    relative = path.relative_to(boundary)
    current = boundary
    for part in relative.parts:
        current = current / part
        if current.exists() and _is_reparse_point(current):
            raise PromotionError(code, f"Reparse-point paths are forbidden: {current}")


def _resolve_strict(path: Path) -> Path:
    return path.resolve(strict=True)


def _resolved_temp_root(repository_root: Path, code: str) -> Path:
    temp_root = repository_root / "TEMP"
    if not temp_root.is_dir():
        raise PromotionError(code, "Repository TEMP root is missing or is not a directory.")
    _assert_no_reparse_below(temp_root, repository_root, code)
    try:
        resolved_temp = _resolve_strict(temp_root)
    except OSError as exc:
        raise PromotionError(code, "Cannot resolve repository TEMP root.") from exc
    if not _relative_to(resolved_temp, repository_root) or resolved_temp == repository_root:
        raise PromotionError(code, "Repository TEMP root resolves outside the repository.")
    return resolved_temp


def _validate_temp_storage_path(path: Path, repository_root: Path, code: str) -> Path:
    temp_root = repository_root / "TEMP"
    resolved_temp = _resolved_temp_root(repository_root, code)
    lexical = Path(os.path.abspath(path))
    if lexical == temp_root or not _relative_to(lexical, temp_root):
        raise PromotionError(code, f"Storage path is outside repository TEMP/: {path}")
    _assert_no_reparse_below(lexical, repository_root, code)
    try:
        resolved = _resolve_strict(lexical)
    except OSError as exc:
        raise PromotionError(code, f"Cannot resolve governed TEMP storage: {path}") from exc
    if resolved == resolved_temp or not _relative_to(resolved, resolved_temp):
        raise PromotionError(code, f"Storage path resolves outside repository TEMP/: {path}")
    return resolved


def _resolve_source(source_root: Path | str, repository_root: Path) -> Path:
    source = Path(source_root)
    if not source.is_absolute():
        source = repository_root / source
    if not source.exists():
        raise PromotionError("PROMOTION_INPUT_NOT_FOUND", f"Promotion source does not exist: {source}")
    if not source.is_dir():
        raise PromotionError(
            "PROMOTION_INPUT_NOT_CANONICAL_MATERIALIZATION",
            f"Promotion source must be a canonical runtime-package directory: {source}",
        )
    lexical_source = Path(os.path.abspath(source))
    temp_root = repository_root / "TEMP"
    if lexical_source == temp_root or not _relative_to(lexical_source, temp_root):
        raise PromotionError("PROMOTION_INPUT_OUTSIDE_TEMP", "Promotion source must be below repository TEMP/.")
    _assert_no_reparse_below(lexical_source, repository_root, "PROMOTION_INPUT_OUTSIDE_TEMP")
    try:
        resolved = lexical_source.resolve(strict=True)
    except OSError as exc:
        raise PromotionError("PROMOTION_INPUT_NOT_FOUND", f"Cannot resolve promotion source: {source}") from exc
    resolved_temp = _resolved_temp_root(repository_root, "PROMOTION_INPUT_OUTSIDE_TEMP")
    if resolved == resolved_temp or not _relative_to(resolved, resolved_temp):
        raise PromotionError("PROMOTION_INPUT_OUTSIDE_TEMP", "Promotion source resolves outside repository TEMP/.")
    for item in resolved.rglob("*"):
        if _is_reparse_point(item):
            raise PromotionError("PROMOTION_INPUT_OUTSIDE_TEMP", f"Source package contains a reparse point: {item}")
    return resolved


def _resolve_target(repository_root: Path) -> Path:
    target = repository_root / TARGET_RELATIVE_PATH
    lexical_target = Path(os.path.abspath(target))
    if lexical_target != target or not _relative_to(lexical_target, repository_root):
        raise PromotionError("PROMOTION_TARGET_FORBIDDEN", "Promotion target escaped the repository root.")
    _assert_no_reparse_below(target, repository_root, "PROMOTION_TARGET_UNSAFE")
    if target.exists() and not target.is_dir():
        raise PromotionError("PROMOTION_TARGET_UNSAFE", "Promotion target exists but is not a directory.")
    if target.exists():
        for item in target.rglob("*"):
            if _is_reparse_point(item):
                raise PromotionError("PROMOTION_TARGET_UNSAFE", f"Promotion target contains a reparse point: {item}")
    return target


def _require_identity(value: Any, label: str) -> str:
    if not isinstance(value, str) or len(value) != 71 or not value.startswith("sha256:"):
        raise PromotionError("PROMOTION_IDENTITY_MISMATCH", f"Invalid {label} identity.")
    try:
        int(value[7:], 16)
    except ValueError as exc:
        raise PromotionError("PROMOTION_IDENTITY_MISMATCH", f"Invalid {label} identity.") from exc
    return value


def _read_candidate_authority(candidate_id: str, repository_root: Path) -> dict[str, Any]:
    identity = _require_identity(candidate_id, "candidate")
    candidate_root = repository_root / "TEMP" / "data_build" / identity.removeprefix("sha256:")
    if not candidate_root.is_dir():
        raise PromotionError(
            "PROMOTION_PROVENANCE_INVALID",
            f"Referenced canonical candidate is missing from governed storage: {candidate_root}",
        )
    try:
        resolved_candidate = _validate_temp_storage_path(
            candidate_root,
            repository_root,
            "PROMOTION_PROVENANCE_INVALID",
        )
        errors = verify_candidate(resolved_candidate, repository_root)
    except PromotionError:
        raise
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise PromotionError("PROMOTION_PROVENANCE_INVALID", f"Canonical candidate verification failed: {exc}") from exc
    if errors:
        raise PromotionError(
            "PROMOTION_PROVENANCE_INVALID",
            "Canonical candidate verification failed: " + "; ".join(errors),
        )
    readiness_path = resolved_candidate / "readiness.json"
    try:
        readiness = json.loads(readiness_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PromotionError("PROMOTION_PROVENANCE_INVALID", "Canonical candidate readiness is unreadable.") from exc
    if not isinstance(readiness, dict):
        raise PromotionError("PROMOTION_PROVENANCE_INVALID", "Canonical candidate readiness is not an object.")
    return readiness


def _normalized_blockers(value: Any, label: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
        raise PromotionError("PROMOTION_PROVENANCE_INVALID", f"{label} blockers are invalid.")
    return sorted((dict(item) for item in value), key=lambda item: json.dumps(item, ensure_ascii=False, sort_keys=True))


def _validate_authoritative_readiness(manifest: dict[str, Any], candidate_readiness: dict[str, Any]) -> None:
    runtime = manifest.get("readiness")
    if not isinstance(runtime, dict):
        raise PromotionError("PROMOTION_MATERIALIZATION_NOT_VALID", "Runtime readiness is missing or invalid.")
    candidate_production = candidate_readiness.get("production_ready")
    candidate_publish = candidate_readiness.get("publish_allowed")
    if not isinstance(candidate_production, bool) or not isinstance(candidate_publish, bool):
        raise PromotionError("PROMOTION_PROVENANCE_INVALID", "Canonical candidate readiness flags are invalid.")
    if runtime.get("candidate_production_ready") is not candidate_production:
        raise PromotionError("PROMOTION_PROVENANCE_INVALID", "Materialized production readiness disagrees with candidate authority.")
    if runtime.get("candidate_publish_allowed") is not candidate_publish:
        raise PromotionError("PROMOTION_PROVENANCE_INVALID", "Materialized publish readiness disagrees with candidate authority.")
    candidate_blockers = _normalized_blockers(candidate_readiness.get("blockers"), "Candidate")
    runtime_blockers = _normalized_blockers(runtime.get("blockers"), "Runtime")
    candidate_counts = Counter(json.dumps(item, ensure_ascii=False, sort_keys=True) for item in candidate_blockers)
    runtime_counts = Counter(json.dumps(item, ensure_ascii=False, sort_keys=True) for item in runtime_blockers)
    if candidate_counts - runtime_counts:
        raise PromotionError("PROMOTION_PROVENANCE_INVALID", "Materialized readiness does not preserve candidate blockers.")
    remaining = runtime_counts - candidate_counts
    local_blockers = [json.loads(encoded) for encoded, count in remaining.items() for _ in range(count)]
    materialization_valid = runtime.get("materialization_valid") is True
    expected_production = candidate_production and materialization_valid and not any(
        bool(item.get("blocks_production", True)) for item in local_blockers
    )
    expected_publish = candidate_publish and materialization_valid and not any(
        bool(item.get("blocks_publish", True)) for item in local_blockers
    )
    if runtime.get("production_ready") is not expected_production:
        raise PromotionError("PROMOTION_PROVENANCE_INVALID", "Derived production readiness is not authoritative.")
    if runtime.get("publish_allowed") is not expected_publish:
        raise PromotionError("PROMOTION_PROVENANCE_INVALID", "Derived publish readiness is not authoritative.")


def _validate_provenance(manifest: dict[str, Any], provenance: dict[str, Any], root: Path) -> str:
    materializer = provenance.get("materializer")
    if materializer != {"contract_version": MATERIALIZER_CONTRACT_VERSION, "id": MATERIALIZER_ID}:
        raise PromotionError("PROMOTION_PROVENANCE_INVALID", "Canonical materializer identity or contract version is invalid.")
    if provenance.get("materialization_profile_id") != MATERIALIZATION_PROFILE_ID:
        raise PromotionError("PROMOTION_PROVENANCE_INVALID", "Materialization profile identity is invalid.")
    if provenance.get("materialization_policy_id") != MATERIALIZATION_POLICY_ID:
        raise PromotionError("PROMOTION_PROVENANCE_INVALID", "Materialization policy identity is invalid.")
    metadata = manifest.get("metadata")
    if not isinstance(metadata, dict) or metadata.get("generator") != MATERIALIZER_ID:
        raise PromotionError("PROMOTION_PROVENANCE_INVALID", "Manifest generator is not the canonical materializer.")
    if metadata.get("materialization_policy_id") != MATERIALIZATION_POLICY_ID:
        raise PromotionError("PROMOTION_PROVENANCE_INVALID", "Manifest materialization policy identity is invalid.")
    if manifest.get("build_profile") != MATERIALIZATION_PROFILE_ID:
        raise PromotionError("PROMOTION_PROVENANCE_INVALID", "Manifest materialization profile identity is invalid.")
    read_audit = provenance.get("read_audit")
    if not isinstance(read_audit, dict) or read_audit.get("candidate_only") is not True:
        raise PromotionError("PROMOTION_PROVENANCE_INVALID", "Canonical materialization must be candidate-only.")
    if read_audit.get("legacy_source_read_count") != 0:
        raise PromotionError("PROMOTION_PROVENANCE_INVALID", "Canonical materialization contains legacy source reads.")
    if read_audit.get("external_source_file_read_count") != 0:
        raise PromotionError("PROMOTION_PROVENANCE_INVALID", "Canonical materialization contains external source reads.")
    if provenance.get("candidate_verifier") != {"errors": [], "result": "PASS"}:
        raise PromotionError("PROMOTION_PROVENANCE_INVALID", "Canonical candidate verification did not pass.")
    if provenance.get("runtime_identity_domain") != RUNTIME_ID_DOMAIN:
        raise PromotionError("PROMOTION_PROVENANCE_INVALID", "Runtime identity domain is invalid.")
    source_components = provenance.get("source_components")
    if not isinstance(source_components, dict) or set(source_components) != CANONICAL_SOURCE_COMPONENTS:
        raise PromotionError("PROMOTION_PROVENANCE_INVALID", "Canonical source components must be exactly CARDDATABASE and REGISTRY.")
    manifest_components = manifest.get("source_components")
    if not isinstance(manifest_components, list):
        raise PromotionError("PROMOTION_PROVENANCE_INVALID", "Manifest source components are invalid.")
    manifest_component_map = {
        item.get("component_kind"): item.get("component_identity")
        for item in manifest_components
        if isinstance(item, dict)
    }
    provenance_component_map = {
        name: item.get("component_identity")
        for name, item in source_components.items()
        if isinstance(item, dict)
    }
    if set(manifest_component_map) != CANONICAL_SOURCE_COMPONENTS or manifest_component_map != provenance_component_map:
        raise PromotionError("PROMOTION_IDENTITY_MISMATCH", "Manifest and provenance source component identities disagree.")
    for name, item in source_components.items():
        if not isinstance(item, dict):
            raise PromotionError("PROMOTION_PROVENANCE_INVALID", f"Source component provenance is invalid: {name}")
        _require_identity(item.get("component_identity"), f"{name} component")
        _require_identity(item.get("content_hash"), f"{name} content")
    candidate_id = _require_identity(provenance.get("candidate_id"), "candidate")
    package_set_id = _require_identity(provenance.get("package_set_id"), "package-set")
    runtime_package_id = _require_identity(provenance.get("runtime_package_id"), "runtime-package")
    source_identity = manifest.get("source_identity")
    if source_identity != {"candidate_id": candidate_id, "package_set_id": package_set_id}:
        raise PromotionError("PROMOTION_IDENTITY_MISMATCH", "Manifest and provenance source identities disagree.")
    if manifest.get("runtime_package_id") != runtime_package_id or manifest.get("package_id") != runtime_package_id:
        raise PromotionError("PROMOTION_IDENTITY_MISMATCH", "Manifest and provenance runtime identities disagree.")
    payload_hashes = provenance.get("identity_payload_file_hashes")
    if not isinstance(payload_hashes, dict) or set(payload_hashes) != set(IDENTITY_PAYLOAD_FILES):
        raise PromotionError("PROMOTION_IDENTITY_MISMATCH", "Identity payload hash set is invalid.")
    if manifest.get("identity_payload_file_hashes") != payload_hashes:
        raise PromotionError("PROMOTION_IDENTITY_MISMATCH", "Manifest and provenance payload hashes disagree.")
    actual_payload_hashes = {name: _sha256_file(root / name) for name in IDENTITY_PAYLOAD_FILES}
    if payload_hashes != actual_payload_hashes:
        raise PromotionError("PROMOTION_IDENTITY_MISMATCH", "Identity payload hashes do not match package bytes.")
    if compute_runtime_package_id(candidate_id, package_set_id, payload_hashes) != runtime_package_id:
        raise PromotionError("PROMOTION_IDENTITY_MISMATCH", "Runtime package identity verification failed.")
    file_hashes = provenance.get("file_hashes")
    expected_hashed_files = set(OUTPUT_FILES) - {"provenance.json"}
    if not isinstance(file_hashes, dict) or set(file_hashes) != expected_hashed_files:
        raise PromotionError("PROMOTION_PROVENANCE_INVALID", "Provenance file-hash scope is invalid.")
    if any(_sha256_file(root / name) != digest for name, digest in file_hashes.items()):
        raise PromotionError("PROMOTION_PACKAGE_INVALID", "Provenance file hashes do not match package bytes.")
    if manifest.get("readiness") != provenance.get("readiness"):
        raise PromotionError("PROMOTION_PROVENANCE_INVALID", "Manifest and provenance readiness disagree.")
    return runtime_package_id


def _validate_materialization(manifest: dict[str, Any]) -> None:
    readiness = manifest.get("readiness")
    if not isinstance(readiness, dict):
        raise PromotionError("PROMOTION_MATERIALIZATION_NOT_VALID", "Runtime readiness is missing or invalid.")
    validation_summary = manifest.get("validation_summary")
    summary_valid = isinstance(validation_summary, dict) and validation_summary.get("materialization_valid") is True
    if readiness.get("materialization_valid") is not True or not summary_valid:
        raise PromotionError("PROMOTION_MATERIALIZATION_NOT_VALID", "Runtime materialization is not valid.")


def _validate_activation_readiness(manifest: dict[str, Any]) -> None:
    readiness = manifest["readiness"]
    if readiness.get("production_ready") is not True:
        raise PromotionError("PROMOTION_PRODUCTION_NOT_READY", "Canonical runtime package is not production-ready.")
    if readiness.get("publish_allowed") is not True:
        raise PromotionError("PROMOTION_NOT_ALLOWED", "Canonical runtime package is not allowed to publish.")


def _validate_package_contents(root: Path, repository_root: Path) -> tuple[str, int]:
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    actual_directories = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_dir()}
    if actual_files != set(OUTPUT_FILES) or actual_directories:
        raise PromotionError(
            "PROMOTION_INPUT_NOT_CANONICAL_MATERIALIZATION",
            "Canonical materializer file contract mismatch: "
            f"files={sorted(actual_files ^ set(OUTPUT_FILES))}, directories={sorted(actual_directories)}",
        )
    manifest = _read_json(root / "manifest.json")
    provenance = _read_json(root / "provenance.json")
    runtime_package_id = _validate_provenance(manifest, provenance, root)
    errors = validate_runtime_package(root)
    if errors:
        raise PromotionError("PROMOTION_PACKAGE_INVALID", "; ".join(errors))
    _validate_materialization(manifest)
    candidate_readiness = _read_candidate_authority(provenance["candidate_id"], repository_root)
    _validate_authoritative_readiness(manifest, candidate_readiness)
    _validate_activation_readiness(manifest)
    return runtime_package_id, len(actual_files)


def preflight(source_root: Path | str, repository_root: Path | str | None = None) -> PromotionResult:
    root = Path(repository_root).resolve() if repository_root is not None else _repository_root().resolve()
    if not root.is_dir():
        raise PromotionError("PROMOTION_TARGET_UNSAFE", f"Repository root is not a directory: {root}")
    source = _resolve_source(source_root, root)
    target = _resolve_target(root)
    before = _tree_hashes(source)
    runtime_package_id, file_count = _validate_package_contents(source, root)
    if _tree_hashes(source) != before:
        raise PromotionError("PROMOTION_PACKAGE_INVALID", "Source package changed during preflight.")
    return PromotionResult(source, target, runtime_package_id, file_count, False)


@contextmanager
def _promotion_lock(repository_root: Path) -> Iterator[None]:
    lock_path = repository_root / LOCK_RELATIVE_PATH
    try:
        resolved_temp = _resolved_temp_root(repository_root, "PROMOTION_ATOMIC_REPLACE_FAILED")
        if lock_path.parent.resolve() != resolved_temp:
            raise PromotionError("PROMOTION_ATOMIC_REPLACE_FAILED", "Promotion lock parent is outside governed TEMP/.")
        if lock_path.exists() and _is_reparse_point(lock_path):
            raise PromotionError("PROMOTION_ATOMIC_REPLACE_FAILED", "Promotion lock is a reparse point.")
        descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise PromotionError("PROMOTION_ATOMIC_REPLACE_FAILED", "Another runtime promotion transaction is active.") from exc
    except PromotionError:
        raise
    except OSError as exc:
        raise PromotionError("PROMOTION_ATOMIC_REPLACE_FAILED", f"Cannot acquire promotion lock: {exc}") from exc
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(f"pid={os.getpid()}\n")
        yield
    finally:
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass
        except OSError as exc:
            raise PromotionError("PROMOTION_ATOMIC_REPLACE_FAILED", f"Cannot release promotion lock: {exc}") from exc


def _rename_directory(source: Path, destination: Path) -> None:
    source.replace(destination)


def _create_transaction_root(repository_root: Path) -> Path:
    parent = repository_root / TRANSACTION_ROOT_RELATIVE_PATH
    try:
        _resolved_temp_root(repository_root, "PROMOTION_ATOMIC_REPLACE_FAILED")
        if parent.exists():
            if not parent.is_dir():
                raise PromotionError("PROMOTION_ATOMIC_REPLACE_FAILED", "Transaction parent is not a directory.")
            _validate_temp_storage_path(parent, repository_root, "PROMOTION_ATOMIC_REPLACE_FAILED")
        else:
            parent.mkdir()
            _validate_temp_storage_path(parent, repository_root, "PROMOTION_ATOMIC_REPLACE_FAILED")
        transaction_root = parent / uuid.uuid4().hex
        transaction_root.mkdir()
        return _validate_temp_storage_path(
            transaction_root,
            repository_root,
            "PROMOTION_ATOMIC_REPLACE_FAILED",
        )
    except PromotionError:
        raise
    except OSError as exc:
        raise PromotionError("PROMOTION_ATOMIC_REPLACE_FAILED", f"Cannot prepare promotion transaction storage: {exc}") from exc


def _rollback(
    target: Path,
    backup: Path,
    quarantine: Path,
    original_hashes: dict[str, str] | None,
) -> None:
    try:
        if target.exists():
            _rename_directory(target, quarantine)
        if original_hashes is not None:
            if not backup.exists():
                raise OSError("Promotion backup is missing.")
            _rename_directory(backup, target)
            if _tree_hashes(target) != original_hashes:
                raise OSError("Restored target hashes do not match the original target.")
        elif target.exists():
            raise OSError("Target should have been absent after rollback.")
    except (OSError, PromotionError) as exc:
        raise PromotionError(
            "PROMOTION_ROLLBACK_FAILED",
            f"Runtime promotion rollback failed; transaction evidence preserved at {backup.parent}: {exc}",
        ) from exc


def promote(source_root: Path | str, repository_root: Path | str | None = None) -> PromotionResult:
    root = Path(repository_root).resolve() if repository_root is not None else _repository_root().resolve()
    checked = preflight(source_root, root)
    source_hashes = _tree_hashes(checked.source_directory)
    try:
        transaction_root = _create_transaction_root(root)
    except PromotionError:
        raise
    except OSError as exc:
        raise PromotionError("PROMOTION_ATOMIC_REPLACE_FAILED", f"Cannot prepare promotion transaction: {exc}") from exc
    staging = transaction_root / "staging"
    backup = transaction_root / "backup"
    quarantine = transaction_root / "failed_target"
    try:
        shutil.copytree(checked.source_directory, staging)
        staged_id, staged_count = _validate_package_contents(staging, root)
        if staged_id != checked.runtime_package_id or staged_count != checked.file_count:
            raise PromotionError("PROMOTION_IDENTITY_MISMATCH", "Staging identity differs from the verified source.")
        if _tree_hashes(staging) != source_hashes:
            raise PromotionError("PROMOTION_IDENTITY_MISMATCH", "Staging bytes differ from the verified source.")
    except PromotionError:
        shutil.rmtree(transaction_root, ignore_errors=True)
        raise
    except OSError as exc:
        shutil.rmtree(transaction_root, ignore_errors=True)
        raise PromotionError("PROMOTION_ATOMIC_REPLACE_FAILED", f"Cannot stage runtime package: {exc}") from exc

    target = checked.target_directory
    with _promotion_lock(root):
        _resolve_target(root)
        if _tree_hashes(checked.source_directory) != source_hashes:
            shutil.rmtree(transaction_root, ignore_errors=True)
            raise PromotionError("PROMOTION_PACKAGE_INVALID", "Source package changed before promotion.")
        original_hashes = _tree_hashes(target) if target.exists() else None
        original_moved = False
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                _rename_directory(target, backup)
                original_moved = True
            _rename_directory(staging, target)
            try:
                target_id, target_count = _validate_package_contents(target, root)
            except PromotionError as exc:
                raise PromotionError("PROMOTION_POSTCOPY_VALIDATION_FAILED", str(exc)) from exc
            if target_id != checked.runtime_package_id or target_count != checked.file_count:
                raise PromotionError("PROMOTION_POSTCOPY_VALIDATION_FAILED", "Promoted package identity changed.")
            if _tree_hashes(target) != source_hashes:
                raise PromotionError("PROMOTION_POSTCOPY_VALIDATION_FAILED", "Promoted package bytes differ from source.")
        except PromotionError as exc:
            if original_moved or target.exists():
                _rollback(target, backup, quarantine, original_hashes)
            raise exc
        except OSError as exc:
            if original_moved or target.exists():
                _rollback(target, backup, quarantine, original_hashes)
            raise PromotionError("PROMOTION_ATOMIC_REPLACE_FAILED", f"Atomic runtime replacement failed: {exc}") from exc
    shutil.rmtree(transaction_root, ignore_errors=True)
    return PromotionResult(
        checked.source_directory,
        target,
        checked.runtime_package_id,
        checked.file_count,
        True,
    )
