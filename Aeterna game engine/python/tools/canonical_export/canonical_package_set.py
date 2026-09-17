"""Deterministic identity primitives for immutable AETERNA package sets.

This module deliberately has no workbook, exporter, publisher, or runtime
dependencies.  It defines the portable data and hash contract only.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Sequence


COMPONENT_CONTENT_DOMAIN = "aeterna-component-content-v1"
COMPONENT_IDENTITY_DOMAIN = "aeterna-component-v1"
PACKAGE_SET_IDENTITY_DOMAIN = "aeterna-package-set-v1"

COMPONENT_FORMAT_VERSION = "1"
PACKAGE_SET_FORMAT_VERSION = "1"
SUPPORTED_COMPONENT_FORMATS = frozenset({COMPONENT_FORMAT_VERSION})
SUPPORTED_PACKAGE_SET_FORMATS = frozenset({PACKAGE_SET_FORMAT_VERSION})

CONSUMER_REQUIRED = "required"
CONSUMER_OPTIONAL = "optional"
CONSUMER_REQUIREMENTS = frozenset({CONSUMER_REQUIRED, CONSUMER_OPTIONAL})
KNOWN_COMPONENT_KINDS = frozenset({"REGISTRY", "CARDDATABASE"})

INT64_MIN = -(2**63)
INT64_MAX = 2**63 - 1

_HASH_PATTERN = re.compile(r"sha256:[0-9a-f]{64}\Z")
_WINDOWS_DRIVE_PATTERN = re.compile(r"^[A-Za-z]:")


@dataclass(frozen=True)
class PackageSetDiagnostic:
    """Stable machine-readable validation failure."""

    code: str
    message: str
    context: Mapping[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "context": dict(self.context),
        }


class PackageSetContractError(ValueError):
    """Raised when a pure identity operation receives an invalid contract."""

    def __init__(self, diagnostics: Sequence[PackageSetDiagnostic]):
        self.diagnostics = tuple(diagnostics)
        super().__init__(
            "; ".join(f"{item.code}: {item.message}" for item in self.diagnostics)
        )


@dataclass(frozen=True)
class PackageSetVerification:
    diagnostics: tuple[PackageSetDiagnostic, ...]

    @property
    def is_valid(self) -> bool:
        return not self.diagnostics


@dataclass(frozen=True)
class FileDescriptor:
    relative_path: str
    size_bytes: int
    file_hash: str
    role: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "relative_path": canonical_relative_path(self.relative_path),
            "size_bytes": self.size_bytes,
            "file_hash": self.file_hash,
            "role": self.role,
        }


@dataclass(frozen=True)
class DependencyDescriptor:
    target_component_id: str
    target_component_kind: str
    target_package_id: str
    minimum_schema_version: str
    minimum_data_version: str
    bound_component_identity: str
    bound_content_hash: str

    def as_dict(self) -> dict[str, str]:
        return {
            "target_component_id": self.target_component_id,
            "target_component_kind": self.target_component_kind,
            "target_package_id": self.target_package_id,
            "minimum_schema_version": self.minimum_schema_version,
            "minimum_data_version": self.minimum_data_version,
            "bound_component_identity": self.bound_component_identity,
            "bound_content_hash": self.bound_content_hash,
        }


@dataclass(frozen=True)
class ComponentDescriptor:
    component_format_version: str
    component_identity: str
    component_id: str
    component_kind: str
    package_id: str
    schema_version: str
    data_version: str
    content_hash: str
    manifest_file: str
    manifest_hash: str
    dependencies: tuple[DependencyDescriptor, ...]
    consumer_requirement: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "component_format_version": self.component_format_version,
            "component_identity": self.component_identity,
            "component_id": self.component_id,
            "component_kind": self.component_kind,
            "package_id": self.package_id,
            "schema_version": self.schema_version,
            "data_version": self.data_version,
            "content_hash": self.content_hash,
            "manifest_file": canonical_relative_path(self.manifest_file),
            "manifest_hash": self.manifest_hash,
            "dependencies": [
                dependency.as_dict()
                for dependency in _sorted_dependencies(self.dependencies)
            ],
            "consumer_requirement": self.consumer_requirement,
        }


@dataclass(frozen=True)
class PackageSet:
    package_set_format_version: str
    package_set_id: str
    package_set_profile_id: str
    profile_contract_hash: str
    validation_policy_id: str
    components: tuple[ComponentDescriptor, ...]
    validation_ledger_file: str
    validation_ledger_hash: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "package_set_format_version": self.package_set_format_version,
            "package_set_id": self.package_set_id,
            "package_set_profile_id": self.package_set_profile_id,
            "profile_contract_hash": self.profile_contract_hash,
            "validation_policy_id": self.validation_policy_id,
            "components": [
                component.as_dict()
                for component in _sorted_components(self.components)
            ],
            "validation_ledger_file": canonical_relative_path(
                self.validation_ledger_file
            ),
            "validation_ledger_hash": self.validation_ledger_hash,
        }


def canonical_json_bytes(value: Any) -> bytes:
    """Serialize CanonicalValue to compact, byte-ordered UTF-8 JSON.

    CanonicalValue is null, boolean, signed 64-bit integer, Unicode scalar
    string, list<CanonicalValue>, or object<string, CanonicalValue>.
    """

    canonical_value = _canonicalize_value(
        value,
        path="$",
        active_container_ids=set(),
    )
    return json.dumps(
        canonical_value,
        ensure_ascii=False,
        sort_keys=False,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    """Return the only public hash representation used by this contract."""

    if not isinstance(value, bytes):
        _raise_contract(
            "PACKAGE_CANONICAL_VALUE_UNSUPPORTED",
            "sha256_bytes requires bytes.",
            value_type=type(value).__name__,
        )
    return f"sha256:{hashlib.sha256(value).hexdigest()}"


def is_sha256(value: Any) -> bool:
    return type(value) is str and _HASH_PATTERN.fullmatch(value) is not None


def utf8_sort_key(value: str) -> bytes:
    """Return the locale-independent ordering key for identity strings."""

    if type(value) is not str:
        _raise_contract(
            "PACKAGE_CANONICAL_VALUE_UNSUPPORTED",
            "An identity sorting value must be a string.",
            value_type=type(value).__name__,
        )
    _validate_unicode_scalar_string(value, path="$sort")
    return value.encode("utf-8")


def canonical_relative_path(value: str) -> str:
    """Return a platform-neutral package-relative path or fail explicitly."""

    if not isinstance(value, str) or not value or value != value.strip():
        _raise_contract(
            "PACKAGE_COMPONENT_MANIFEST_INVALID",
            "A relative path must be a non-empty, trimmed string.",
            path=value,
        )
    _validate_unicode_scalar_string(value, path="$path")
    if "\x00" in value or value.startswith(("/", "\\")):
        _raise_contract(
            "PACKAGE_COMPONENT_MANIFEST_INVALID",
            "Absolute paths are not allowed.",
            path=value,
        )
    normalized = value.replace("\\", "/")
    if _WINDOWS_DRIVE_PATTERN.match(normalized):
        _raise_contract(
            "PACKAGE_COMPONENT_MANIFEST_INVALID",
            "Drive-qualified paths are not allowed.",
            path=value,
        )
    segments = normalized.split("/")
    if any(segment in {"", ".", ".."} for segment in segments):
        _raise_contract(
            "PACKAGE_COMPONENT_MANIFEST_INVALID",
            "Empty, current-directory, and parent-directory path segments are not allowed.",
            path=value,
        )
    return "/".join(segments)


def component_content_preimage(files: Sequence[FileDescriptor]) -> bytes:
    """Return the exact canonical preimage used for component content hashing."""

    diagnostics: list[PackageSetDiagnostic] = []
    seen_paths: set[str] = set()
    normalized_files: list[dict[str, Any]] = []
    for descriptor in files:
        descriptor_diagnostics = _file_diagnostics(descriptor)
        diagnostics.extend(descriptor_diagnostics)
        if descriptor_diagnostics:
            continue
        item = descriptor.as_dict()
        path = item["relative_path"]
        if path in seen_paths:
            diagnostics.append(
                _diagnostic(
                    "PACKAGE_COMPONENT_MANIFEST_INVALID",
                    "A component contains a duplicate relative file path.",
                    relative_path=path,
                )
            )
        seen_paths.add(path)
        normalized_files.append(item)
    if diagnostics:
        raise PackageSetContractError(diagnostics)
    normalized_files.sort(key=lambda item: utf8_sort_key(item["relative_path"]))
    # Role is identity-relevant: changing a file's semantic package purpose must
    # not preserve the logical component content identity by accident.
    return canonical_json_bytes(
        {"domain": COMPONENT_CONTENT_DOMAIN, "files": normalized_files}
    )


def compute_component_content_hash(files: Sequence[FileDescriptor]) -> str:
    return sha256_bytes(component_content_preimage(files))


def component_identity_preimage(component: ComponentDescriptor) -> bytes:
    """Return the component preimage; stored component_identity is excluded."""

    diagnostics = _component_diagnostics(component, check_stored_identity=False)
    if diagnostics:
        raise PackageSetContractError(diagnostics)
    return canonical_json_bytes(
        {
            "domain": COMPONENT_IDENTITY_DOMAIN,
            "component_format_version": component.component_format_version,
            "component_id": component.component_id,
            "component_kind": component.component_kind,
            "package_id": component.package_id,
            "schema_version": component.schema_version,
            "data_version": component.data_version,
            "content_hash": component.content_hash,
            "dependencies": [
                dependency.as_dict()
                for dependency in _sorted_dependencies(component.dependencies)
            ],
        }
    )


def compute_component_identity(component: ComponentDescriptor) -> str:
    return sha256_bytes(component_identity_preimage(component))


def package_set_identity_preimage(package_set: PackageSet) -> bytes:
    """Return the set preimage; stored package_set_id is excluded."""

    if not isinstance(package_set, PackageSet):
        _raise_contract(
            "PACKAGE_SET_MANIFEST_INCOMPLETE",
            "package_set must be a PackageSet.",
            value_type=type(package_set).__name__,
        )
    diagnostics = _package_set_identity_input_diagnostics(package_set)
    components, component_diagnostics = _package_components(package_set)
    diagnostics.extend(component_diagnostics)
    if diagnostics:
        raise PackageSetContractError(diagnostics)
    return canonical_json_bytes(
        {
            "domain": PACKAGE_SET_IDENTITY_DOMAIN,
            "package_set_format_version": package_set.package_set_format_version,
            "package_set_profile_id": package_set.package_set_profile_id,
            "profile_contract_hash": package_set.profile_contract_hash,
            "validation_policy_id": package_set.validation_policy_id,
            "components": [
                component.as_dict()
                for component in _sorted_components(components)
            ],
            "validation_ledger_file": canonical_relative_path(
                package_set.validation_ledger_file
            ),
            "validation_ledger_hash": package_set.validation_ledger_hash,
        }
    )


def compute_package_set_identity(package_set: PackageSet) -> str:
    return sha256_bytes(package_set_identity_preimage(package_set))


def classify_component_support(
    component: ComponentDescriptor,
    supported_component_kinds: Iterable[str] = KNOWN_COMPONENT_KINDS,
) -> str:
    known = component.component_kind in frozenset(supported_component_kinds)
    requirement = component.consumer_requirement
    if requirement not in CONSUMER_REQUIREMENTS:
        _raise_contract(
            "PACKAGE_COMPONENT_MANIFEST_INVALID",
            "consumer_requirement must be required or optional.",
            component_id=component.component_id,
            consumer_requirement=requirement,
        )
    return f"{'known' if known else 'unknown'}_{requirement}"


def verify_package_set(
    package_set: PackageSet,
    supported_component_kinds: Iterable[str] = KNOWN_COMPONENT_KINDS,
) -> PackageSetVerification:
    """Validate schema and identities without reading from the filesystem."""

    diagnostics: list[PackageSetDiagnostic] = []
    if not isinstance(package_set, PackageSet):
        return PackageSetVerification(
            tuple(
                _canonical_diagnostics(
                    [
                        _diagnostic(
                            "PACKAGE_SET_MANIFEST_INCOMPLETE",
                            "package_set must be a PackageSet.",
                            value_type=type(package_set).__name__,
                        )
                    ]
                )
            )
        )

    try:
        supported_kind_values = tuple(supported_component_kinds)
    except (TypeError, ValueError):
        diagnostics.append(
            _diagnostic(
                "PACKAGE_SET_MANIFEST_INCOMPLETE",
                "supported_component_kinds must be an iterable of Unicode scalar strings.",
                field="supported_component_kinds",
            )
        )
        supported_kinds = frozenset()
    else:
        invalid_supported_kinds = [
            value for value in supported_kind_values if not _is_non_empty_string(value)
        ]
        if invalid_supported_kinds:
            diagnostics.append(
                _diagnostic(
                    "PACKAGE_SET_MANIFEST_INCOMPLETE",
                    "supported_component_kinds must contain only Unicode scalar strings.",
                    field="supported_component_kinds",
                )
            )
            supported_kinds = frozenset()
        else:
            supported_kinds = frozenset(supported_kind_values)

    diagnostics.extend(_package_set_identity_input_diagnostics(package_set))
    components, component_diagnostics = _package_components(package_set)
    diagnostics.extend(component_diagnostics)
    if not components:
        diagnostics.append(
            _diagnostic(
                "PACKAGE_SET_MANIFEST_INCOMPLETE",
                "A package set must contain at least one component.",
                field="components",
            )
        )
    if not is_sha256(package_set.package_set_id):
        diagnostics.append(
            _diagnostic(
                "PACKAGE_HASH_SET_MISMATCH",
                "package_set_id is not a canonical SHA-256 string.",
                field="package_set_id",
            )
        )

    seen_component_ids: set[str] = set()
    has_duplicate_component_id = False
    for component in components:
        if (
            _is_non_empty_string(component.component_id)
            and component.component_id in seen_component_ids
        ):
            has_duplicate_component_id = True
            diagnostics.append(
                _diagnostic(
                    "PACKAGE_COMPONENT_DUPLICATE_ID",
                    "A component_id occurs more than once in the package set.",
                    component_id=component.component_id,
                )
            )
        if _is_non_empty_string(component.component_id):
            seen_component_ids.add(component.component_id)

        if (
            _is_unicode_scalar_string(component.consumer_requirement)
            and component.consumer_requirement == CONSUMER_REQUIRED
            and _is_non_empty_string(component.component_kind)
            and component.component_kind not in supported_kinds
        ):
            diagnostics.append(
                _diagnostic(
                    "PACKAGE_COMPONENT_REQUIRED_KIND_UNSUPPORTED",
                    "A required component kind is not supported by this consumer.",
                    component_id=component.component_id,
                    component_kind=component.component_kind,
                )
            )

        try:
            expected_identity = compute_component_identity(component)
        except PackageSetContractError:
            pass
        else:
            if (
                is_sha256(component.component_identity)
                and component.component_identity != expected_identity
            ):
                diagnostics.append(
                    _diagnostic(
                        "PACKAGE_HASH_COMPONENT_MISMATCH",
                        "The stored component identity does not match its canonical preimage.",
                        component_id=component.component_id,
                        expected=expected_identity,
                        actual=component.component_identity,
                    )
                )

    if not has_duplicate_component_id:
        try:
            expected_set_id = compute_package_set_identity(package_set)
        except PackageSetContractError:
            pass
        else:
            if (
                is_sha256(package_set.package_set_id)
                and package_set.package_set_id != expected_set_id
            ):
                diagnostics.append(
                    _diagnostic(
                        "PACKAGE_SET_ID_MISMATCH",
                        "The stored package-set ID does not match its canonical preimage.",
                        expected=expected_set_id,
                        actual=package_set.package_set_id,
                    )
                )

    return PackageSetVerification(tuple(_canonical_diagnostics(diagnostics)))


def _canonicalize_value(
    value: Any, *, path: str, active_container_ids: set[int]
) -> Any:
    if value is None or type(value) is bool:
        return value
    if type(value) is int:
        if not INT64_MIN <= value <= INT64_MAX:
            _raise_contract(
                "PACKAGE_CANONICAL_VALUE_UNSUPPORTED",
                "Canonical integers must fit in a signed 64-bit integer.",
                path=path,
                value=str(value),
            )
        return value
    if type(value) is str:
        _validate_unicode_scalar_string(value, path=path)
        return value
    if type(value) is list:
        _enter_container(value, path, active_container_ids)
        try:
            return [
                _canonicalize_value(
                    item,
                    path=f"{path}[{index}]",
                    active_container_ids=active_container_ids,
                )
                for index, item in enumerate(value)
            ]
        finally:
            active_container_ids.remove(id(value))
    if type(value) is dict:
        _enter_container(value, path, active_container_ids)
        try:
            ordered: dict[str, Any] = {}
            for key in sorted(value, key=_canonical_object_key_sort_key):
                if type(key) is not str:
                    _raise_contract(
                        "PACKAGE_CANONICAL_VALUE_UNSUPPORTED",
                        "Canonical JSON object keys must be strings.",
                        path=path,
                        key_type=type(key).__name__,
                    )
                _validate_unicode_scalar_string(key, path=f"{path}.<key>")
                ordered[key] = _canonicalize_value(
                    value[key],
                    path=f"{path}.{key}",
                    active_container_ids=active_container_ids,
                )
            return ordered
        finally:
            active_container_ids.remove(id(value))
    _raise_contract(
        "PACKAGE_CANONICAL_VALUE_UNSUPPORTED",
        "The value type is not part of the canonical JSON contract.",
        path=path,
        value_type=type(value).__name__,
    )


def _canonical_object_key_sort_key(value: Any) -> tuple[int, bytes]:
    if type(value) is str and _is_unicode_scalar_string(value):
        return (0, value.encode("utf-8"))
    return (1, type(value).__name__.encode("utf-8"))


def _validate_unicode_scalar_string(value: str, *, path: str) -> None:
    for index, character in enumerate(value):
        code_point = ord(character)
        if 0xD800 <= code_point <= 0xDFFF:
            _raise_contract(
                "PACKAGE_CANONICAL_VALUE_UNSUPPORTED",
                "Canonical strings may contain Unicode scalar values only.",
                path=path,
                index=index,
                code_point=f"U+{code_point:04X}",
            )


def _is_unicode_scalar_string(value: Any) -> bool:
    return type(value) is str and not any(
        0xD800 <= ord(character) <= 0xDFFF for character in value
    )


def _enter_container(value: Any, path: str, active_container_ids: set[int]) -> None:
    if id(value) in active_container_ids:
        _raise_contract(
            "PACKAGE_CANONICAL_VALUE_UNSUPPORTED",
            "Cyclic containers are not supported.",
            path=path,
        )
    active_container_ids.add(id(value))


def _file_diagnostics(descriptor: Any) -> list[PackageSetDiagnostic]:
    if not isinstance(descriptor, FileDescriptor):
        return [
            _diagnostic(
                "PACKAGE_COMPONENT_MANIFEST_INVALID",
                "A file entry must be a FileDescriptor.",
                value_type=type(descriptor).__name__,
            )
        ]
    diagnostics: list[PackageSetDiagnostic] = []
    diagnostics.extend(_path_diagnostics(descriptor.relative_path, field_name="relative_path"))
    if (
        not isinstance(descriptor.size_bytes, int)
        or isinstance(descriptor.size_bytes, bool)
        or descriptor.size_bytes < 0
    ):
        diagnostics.append(
            _diagnostic(
                "PACKAGE_COMPONENT_MANIFEST_INVALID",
                "size_bytes must be a non-negative integer.",
                relative_path=descriptor.relative_path,
            )
        )
    if not is_sha256(descriptor.file_hash):
        diagnostics.append(
            _diagnostic(
                "PACKAGE_HASH_COMPONENT_MISMATCH",
                "file_hash is not a canonical SHA-256 string.",
                relative_path=descriptor.relative_path,
                field="file_hash",
            )
        )
    if not _is_non_empty_string(descriptor.role):
        diagnostics.append(
            _diagnostic(
                "PACKAGE_COMPONENT_MANIFEST_INVALID",
                "A file role must be a non-empty string.",
                relative_path=descriptor.relative_path,
                field="role",
            )
        )
    return diagnostics


def _component_diagnostics(
    component: Any, *, check_stored_identity: bool
) -> list[PackageSetDiagnostic]:
    if not isinstance(component, ComponentDescriptor):
        return [
            _diagnostic(
                "PACKAGE_COMPONENT_MANIFEST_INVALID",
                "A component entry must be a ComponentDescriptor.",
                value_type=type(component).__name__,
            )
        ]
    diagnostics: list[PackageSetDiagnostic] = []
    if (
        not _is_unicode_scalar_string(component.component_format_version)
        or component.component_format_version not in SUPPORTED_COMPONENT_FORMATS
    ):
        diagnostics.append(
            _diagnostic(
                "PACKAGE_SET_SCHEMA_UNSUPPORTED",
                "The component format version is not supported.",
                component_id=component.component_id,
                component_format_version=component.component_format_version,
            )
        )
    for field_name in (
        "component_id",
        "component_kind",
        "package_id",
        "schema_version",
        "data_version",
    ):
        if not _is_non_empty_string(getattr(component, field_name)):
            diagnostics.append(
                _diagnostic(
                    "PACKAGE_COMPONENT_MANIFEST_INVALID",
                    f"{field_name} must be a non-empty string.",
                    component_id=component.component_id,
                    field=field_name,
                )
            )
    if (
        not _is_unicode_scalar_string(component.consumer_requirement)
        or component.consumer_requirement not in CONSUMER_REQUIREMENTS
    ):
        diagnostics.append(
            _diagnostic(
                "PACKAGE_COMPONENT_MANIFEST_INVALID",
                "consumer_requirement must be required or optional.",
                component_id=component.component_id,
                field="consumer_requirement",
            )
        )
    diagnostics.extend(
        _path_diagnostics(
            component.manifest_file,
            field_name="manifest_file",
            component_id=component.component_id,
        )
    )
    for field_name in ("content_hash", "manifest_hash"):
        if not is_sha256(getattr(component, field_name)):
            diagnostics.append(
                _diagnostic(
                    "PACKAGE_HASH_COMPONENT_MISMATCH",
                    f"{field_name} is not a canonical SHA-256 string.",
                    component_id=component.component_id,
                    field=field_name,
                )
            )
    if check_stored_identity and not is_sha256(component.component_identity):
        diagnostics.append(
            _diagnostic(
                "PACKAGE_HASH_COMPONENT_MISMATCH",
                "component_identity is not a canonical SHA-256 string.",
                component_id=component.component_id,
                field="component_identity",
            )
        )

    if type(component.dependencies) is not tuple:
        diagnostics.append(
            _diagnostic(
                "PACKAGE_COMPONENT_MANIFEST_INVALID",
                "dependencies must be a tuple of DependencyDescriptor values.",
                component_id=component.component_id,
                field="dependencies",
            )
        )
        return diagnostics

    seen_targets: set[tuple[str, str, str]] = set()
    source_target = (
        component.package_id,
        component.component_kind,
        component.component_id,
    )
    source_is_canonical = all(_is_non_empty_string(value) for value in source_target)
    for dependency in component.dependencies:
        if not isinstance(dependency, DependencyDescriptor):
            diagnostics.append(
                _diagnostic(
                    "PACKAGE_COMPONENT_MANIFEST_INVALID",
                    "A dependency entry must be a DependencyDescriptor.",
                    component_id=component.component_id,
                    value_type=type(dependency).__name__,
                )
            )
            continue
        diagnostics.extend(_dependency_diagnostics(component, dependency))
        target = (
            dependency.target_package_id,
            dependency.target_component_kind,
            dependency.target_component_id,
        )
        target_is_canonical = all(_is_non_empty_string(value) for value in target)
        if target_is_canonical and target in seen_targets:
            diagnostics.append(
                _diagnostic(
                    "PACKAGE_COMPONENT_MANIFEST_INVALID",
                    "A dependency target occurs more than once.",
                    component_id=component.component_id,
                    target_package_id=dependency.target_package_id,
                    target_component_kind=dependency.target_component_kind,
                    target_component_id=dependency.target_component_id,
                    reason="duplicate_dependency_target",
                )
            )
        if target_is_canonical:
            seen_targets.add(target)
        if target_is_canonical and source_is_canonical and target == source_target:
            diagnostics.append(
                _diagnostic(
                    "PACKAGE_COMPONENT_MANIFEST_INVALID",
                    "A component cannot depend on itself.",
                    component_package_id=component.package_id,
                    component_kind=component.component_kind,
                    component_id=component.component_id,
                    reason="self_dependency",
                )
            )
    return diagnostics


def _dependency_diagnostics(
    owner: ComponentDescriptor, dependency: DependencyDescriptor
) -> list[PackageSetDiagnostic]:
    diagnostics: list[PackageSetDiagnostic] = []
    for field_name in (
        "target_component_id",
        "target_component_kind",
        "target_package_id",
    ):
        if not _is_non_empty_string(getattr(dependency, field_name)):
            diagnostics.append(
                _diagnostic(
                    "PACKAGE_DEPENDENCY_TARGET_MISSING",
                    f"{field_name} must be a non-empty string.",
                    component_id=owner.component_id,
                    field=field_name,
                )
            )
    for field_name in ("minimum_schema_version", "minimum_data_version"):
        if not _is_non_empty_string(getattr(dependency, field_name)):
            diagnostics.append(
                _diagnostic(
                    "PACKAGE_COMPONENT_MANIFEST_INVALID",
                    f"{field_name} must be a non-empty string.",
                    component_id=owner.component_id,
                    target_component_id=dependency.target_component_id,
                    field=field_name,
                )
            )
    for field_name in ("bound_component_identity", "bound_content_hash"):
        if not is_sha256(getattr(dependency, field_name)):
            diagnostics.append(
                _diagnostic(
                    "PACKAGE_DEPENDENCY_IDENTITY_MISMATCH",
                    f"{field_name} is not a canonical SHA-256 string.",
                    component_id=owner.component_id,
                    target_component_id=dependency.target_component_id,
                    field=field_name,
                )
            )
    return diagnostics


def _package_set_identity_input_diagnostics(
    package_set: PackageSet,
) -> list[PackageSetDiagnostic]:
    diagnostics: list[PackageSetDiagnostic] = []
    if (
        not _is_unicode_scalar_string(package_set.package_set_format_version)
        or package_set.package_set_format_version not in SUPPORTED_PACKAGE_SET_FORMATS
    ):
        diagnostics.append(
            _diagnostic(
                "PACKAGE_SET_SCHEMA_UNSUPPORTED",
                "The package-set format version is not supported.",
                package_set_format_version=package_set.package_set_format_version,
            )
        )
    for field_name in ("package_set_profile_id", "validation_policy_id"):
        if not _is_non_empty_string(getattr(package_set, field_name)):
            diagnostics.append(
                _diagnostic(
                    "PACKAGE_SET_MANIFEST_INCOMPLETE",
                    f"{field_name} must be a non-empty string.",
                    field=field_name,
                )
            )
    diagnostics.extend(
        _path_diagnostics(
            package_set.validation_ledger_file,
            field_name="validation_ledger_file",
        )
    )
    for field_name in ("profile_contract_hash", "validation_ledger_hash"):
        if not is_sha256(getattr(package_set, field_name)):
            diagnostics.append(
                _diagnostic(
                    "PACKAGE_HASH_SET_MISMATCH",
                    f"{field_name} is not a canonical SHA-256 string.",
                    field=field_name,
                )
            )
    return diagnostics


def _package_components(
    package_set: PackageSet,
) -> tuple[tuple[ComponentDescriptor, ...], list[PackageSetDiagnostic]]:
    if type(package_set.components) is not tuple:
        return (), [
            _diagnostic(
                "PACKAGE_SET_MANIFEST_INCOMPLETE",
                "components must be a tuple of ComponentDescriptor values.",
                field="components",
                value_type=type(package_set.components).__name__,
            )
        ]
    diagnostics: list[PackageSetDiagnostic] = []
    components: list[ComponentDescriptor] = []
    for component in package_set.components:
        component_diagnostics = _component_diagnostics(
            component,
            check_stored_identity=True,
        )
        diagnostics.extend(component_diagnostics)
        if isinstance(component, ComponentDescriptor):
            components.append(component)
    return tuple(components), diagnostics


def _path_diagnostics(
    value: Any, *, field_name: str, component_id: str | None = None
) -> list[PackageSetDiagnostic]:
    try:
        canonical_relative_path(value)
    except PackageSetContractError:
        context: dict[str, Any] = {"field": field_name, "path": value}
        if component_id is not None:
            context["component_id"] = component_id
        return [
            _diagnostic(
                "PACKAGE_COMPONENT_MANIFEST_INVALID",
                f"{field_name} is not a safe canonical relative path.",
                **context,
            )
        ]
    return []


def _sorted_dependencies(
    dependencies: Sequence[DependencyDescriptor],
) -> list[DependencyDescriptor]:
    return sorted(
        dependencies,
        key=lambda item: (
            utf8_sort_key(item.target_package_id),
            utf8_sort_key(item.target_component_kind),
            utf8_sort_key(item.target_component_id),
            utf8_sort_key(item.minimum_schema_version),
            utf8_sort_key(item.minimum_data_version),
            utf8_sort_key(item.bound_component_identity),
            utf8_sort_key(item.bound_content_hash),
        ),
    )


def _sorted_components(
    components: Sequence[ComponentDescriptor],
) -> list[ComponentDescriptor]:
    return sorted(
        components,
        key=lambda item: (
            utf8_sort_key(item.component_kind),
            utf8_sort_key(item.component_id),
        ),
    )


def _is_non_empty_string(value: Any) -> bool:
    return (
        _is_unicode_scalar_string(value)
        and bool(value)
        and value == value.strip()
    )


def _diagnostic(code: str, message: str, **context: Any) -> PackageSetDiagnostic:
    safe_context = {
        key: _diagnostic_context_value(value)
        for key, value in context.items()
    }
    return PackageSetDiagnostic(code=code, message=message, context=safe_context)


def _raise_contract(code: str, message: str, **context: Any) -> None:
    raise PackageSetContractError((_diagnostic(code, message, **context),))


def _diagnostic_context_value(value: Any) -> Any:
    if value is None or type(value) is bool:
        return value
    if type(value) is int and INT64_MIN <= value <= INT64_MAX:
        return value
    if _is_unicode_scalar_string(value):
        return value
    if type(value) is int:
        return str(value)
    if type(value) is str:
        invalid = sorted(
            {ord(character) for character in value if 0xD800 <= ord(character) <= 0xDFFF}
        )
        return "<invalid-unicode:" + ",".join(f"U+{item:04X}" for item in invalid) + ">"
    return f"<{type(value).__name__}>"


def _canonical_diagnostics(
    diagnostics: Sequence[PackageSetDiagnostic],
) -> list[PackageSetDiagnostic]:
    """Deduplicate and order by code, canonical context, then message UTF-8."""

    unique: dict[tuple[bytes, bytes, bytes], PackageSetDiagnostic] = {}
    for diagnostic in diagnostics:
        key = (
            utf8_sort_key(diagnostic.code),
            canonical_json_bytes(dict(diagnostic.context)),
            utf8_sort_key(diagnostic.message),
        )
        unique.setdefault(key, diagnostic)
    return [unique[key] for key in sorted(unique)]
