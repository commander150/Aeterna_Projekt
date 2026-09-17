"""Shared, filesystem-independent canonical validation execution foundation."""

from __future__ import annotations

import json
import math
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, TypeAlias


VALIDATION_EXECUTOR_UNSUPPORTED = "VALIDATION_EXECUTOR_UNSUPPORTED"
VALIDATION_RULE_FAILED = "VALIDATION_RULE_FAILED"

_LOGICAL_IDENTIFIER = re.compile(r"[a-z][a-z0-9_]*\Z")

CanonicalScalar: TypeAlias = str | int | float | bool | None
FrozenRecord: TypeAlias = Mapping[str, CanonicalScalar]


class ValidationOutcome(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    UNSUPPORTED = "UNSUPPORTED"
    NOT_EXECUTED = "NOT_EXECUTED"


@dataclass(frozen=True, slots=True)
class ValidationExecutionDiagnostic:
    code: str
    message: str
    rule_id: str
    table_id: str
    field_id: str | None
    record_identity: str | None = None
    observed_value: CanonicalScalar = None
    expected_contract: str | None = None
    reason: str | None = None
    related_record_identities: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "rule_id": self.rule_id,
            "table_id": self.table_id,
            "field_id": self.field_id,
            "record_identity": self.record_identity,
            "observed_value": self.observed_value,
            "expected_contract": self.expected_contract,
            "reason": self.reason,
            "related_record_identities": list(self.related_record_identities),
        }


@dataclass(frozen=True, slots=True)
class ValidationExecutionResult:
    rule_id: str
    outcome: ValidationOutcome
    diagnostics: tuple[ValidationExecutionDiagnostic, ...]
    evaluated_record_count: int
    violation_count: int


@dataclass(frozen=True, slots=True, init=False)
class ValidationDataContext:
    """Deeply immutable snapshot of materialized legacy or namespaced tables."""
    _tables: tuple[tuple[str, tuple[FrozenRecord, ...]], ...]
    _namespaced_tables: tuple[tuple[str, tuple[tuple[str, tuple[FrozenRecord, ...]], ...]], ...]
    _component_namespaces: tuple[tuple[str, str], ...]
    _namespace_policies: tuple[tuple[str, tuple[tuple[str, str], ...]], ...]
    _legacy_mode: bool
    def __init__(
        self,
        tables: Mapping[str, Sequence[Mapping[str, CanonicalScalar]]] | None = None,
        *,
        namespaced_tables: Mapping[str, Mapping[str, Sequence[Mapping[str, CanonicalScalar]]]] | None = None,
        component_namespaces: Mapping[str, str] | None = None,
        namespace_policies: Mapping[str, Mapping[str, str]] | None = None,
    ) -> None:
        if (tables is None) == (namespaced_tables is None):
            raise ValueError("Provide either legacy or namespaced validation tables.")
        mappings = (tables, namespaced_tables, component_namespaces, namespace_policies)
        if any(value is not None and not isinstance(value, Mapping) for value in mappings):
            raise ValueError("Validation context inputs must be mappings.")
        namespace_items = []
        if namespaced_tables is not None:
            for namespace, values in namespaced_tables.items():
                if not _is_logical_identifier(namespace):
                    raise ValueError("Export namespaces must be canonical identifiers.")
                namespace_items.append((namespace, _freeze_tables(values)))
        namespaces = tuple(sorted(namespace_items, key=lambda item: _utf8(item[0])))
        available = {namespace for namespace, _ in namespaces}
        bindings = tuple(sorted(
            (component_namespaces or {}).items(), key=lambda item: _utf8(item[0])
        ))
        if any(
            not isinstance(component, str) or not component
            or not _is_logical_identifier(namespace)
            or namespace not in available
            for component, namespace in bindings
        ):
            raise ValueError("A component namespace binding is invalid.")
        bound = tuple(namespace for _, namespace in bindings)
        if len(bound) != len(set(bound)):
            raise ValueError("An export namespace has duplicate component bindings.")
        policy_items = []
        for namespace, values in (namespace_policies or {}).items():
            if namespace not in available or not isinstance(values, Mapping):
                raise ValueError("A namespace policy binding is invalid.")
            if any(
                not isinstance(key, str) or not key or not isinstance(value, str)
                for key, value in values.items()
            ):
                raise ValueError("Namespace policies must map strings to strings.")
            policy_items.append((namespace, tuple(sorted(
                values.items(), key=lambda item: _utf8(item[0])
            ))))
        object.__setattr__(self, "_tables", _freeze_tables(tables) if tables else ())
        object.__setattr__(self, "_namespaced_tables", namespaces)
        object.__setattr__(self, "_component_namespaces", bindings)
        object.__setattr__(self, "_namespace_policies", tuple(sorted(
            policy_items, key=lambda item: _utf8(item[0])
        )))
        object.__setattr__(self, "_legacy_mode", tables is not None)

    def table(
        self, table_id: str, *, namespace: str | None = None
    ) -> tuple[FrozenRecord, ...] | None:
        if namespace is not None:
            tables = next((
                values for candidate, values in self._namespaced_tables
                if candidate == namespace
            ), ())
            return _table_from_frozen(tables, table_id)
        if self._legacy_mode:
            return _table_from_frozen(self._tables, table_id)
        if len(self._namespaced_tables) != 1:
            return None
        return _table_from_frozen(self._namespaced_tables[0][1], table_id)

    def namespace_for_component(self, component: str | None) -> str | None:
        return next((
            namespace for candidate, namespace in self._component_namespaces
            if candidate == component
        ), None)

    def has_namespace(self, namespace: str) -> bool:
        return any(candidate == namespace for candidate, _ in self._namespaced_tables)

    def namespace_policy(self, namespace: str, key: str) -> str | None:
        values = next((
            value for candidate, value in self._namespace_policies
            if candidate == namespace
        ), ())
        return next((value for candidate, value in values if candidate == key), None)

    @property
    def namespaces(self) -> tuple[str, ...]:
        return tuple(namespace for namespace, _ in self._namespaced_tables)

    @property
    def table_ids(self) -> tuple[str, ...]:
        if self._legacy_mode:
            return tuple(table_id for table_id, _ in self._tables)
        if len(self._namespaced_tables) == 1:
            return tuple(table_id for table_id, _ in self._namespaced_tables[0][1])
        return tuple(
            f"{namespace}:{table_id}"
            for namespace, values in self._namespaced_tables
            for table_id, _ in values
        )


def _resolve_table(
    data: ValidationDataContext, table_id: str, *, namespace: str | None = None,
) -> tuple[FrozenRecord, ...] | None:
    return data.table(table_id, namespace=namespace)


def _resolve_field_schema(
    data: ValidationDataContext,
    table_id: str,
    *,
    field_id: str | None = None,
    field_name: str | None = None,
    namespace: str | None = None,
    allow_empty_resolved_name: bool = False,
) -> FrozenRecord | None:
    records = _resolve_table(data, "schema_fields", namespace=namespace)
    if records is None or (field_id is None) == (field_name is None):
        return None
    matches = [
        record
        for record in records
        if record.get("table_id") == table_id
        and record.get("status") == "active"
        and (
            record.get("field_id") == field_id
            if field_id is not None
            else record.get("field_name") == field_name
        )
    ]
    if len(matches) != 1:
        return None
    resolved_name = matches[0].get("field_name")
    return matches[0] if (
        isinstance(resolved_name, str)
        and (allow_empty_resolved_name or resolved_name)
    ) else None


def _resolve_primary_key(
    data: ValidationDataContext, table_id: str, *, namespace: str | None = None,
) -> str | None:
    records = _resolve_table(data, "schema_tables", namespace=namespace)
    matches = [] if records is None else [
        record for record in records
        if record.get("table_id") == table_id and record.get("status") == "active"
    ]
    if len(matches) != 1:
        return None
    value = matches[0].get("primary_key")
    return value if isinstance(value, str) and value else None


def _record_identity(record: FrozenRecord, primary_key: str | None) -> str:
    if primary_key is not None:
        value = record.get(primary_key)
        if isinstance(value, (str, int)) and not isinstance(value, bool):
            return str(value)
    return "canonical-record:" + _canonical_record_text(record)


def _valid_identity(record: FrozenRecord, primary_key: str) -> bool:
    value = record.get(primary_key)
    return (
        primary_key in record
        and isinstance(value, (str, int))
        and not isinstance(value, bool)
        and value != ""
    )


def _record_sort_key(
    record: FrozenRecord,
    primary_key: str | None,
) -> tuple[bytes, bytes]:
    return (
        _utf8(_record_identity(record, primary_key)),
        _utf8(_canonical_record_text(record)),
    )


def _diagnostic_sort_key(
    diagnostic: ValidationExecutionDiagnostic,
) -> tuple[bytes, bytes, bytes, bytes]:
    return (
        _utf8(diagnostic.record_identity or ""),
        _utf8(diagnostic.code),
        _utf8(_scalar_text(diagnostic.observed_value)),
        _utf8(diagnostic.reason or ""),
    )


def _canonical_record_text(record: FrozenRecord) -> str:
    return json.dumps(
        dict(record),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _scalar_text(value: CanonicalScalar) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _freeze_tables(
    tables: Mapping[str, Sequence[Mapping[str, CanonicalScalar]]],
) -> tuple[tuple[str, tuple[FrozenRecord, ...]], ...]:
    if not isinstance(tables, Mapping):
        raise ValueError("Validation tables must be a mapping.")
    frozen_tables: list[tuple[str, tuple[FrozenRecord, ...]]] = []
    for table_id, records in tables.items():
        if not isinstance(table_id, str) or not table_id:
            raise ValueError("Validation table IDs must be non-empty strings.")
        if isinstance(records, (str, bytes, bytearray)) or not isinstance(records, Sequence):
            raise ValueError("Validation table records must be a sequence.")
        frozen_records: list[FrozenRecord] = []
        for record in records:
            if not isinstance(record, Mapping):
                raise ValueError("Each validation record must be a mapping.")
            copied: dict[str, CanonicalScalar] = {}
            for field_name, value in record.items():
                if not isinstance(field_name, str) or not field_name:
                    raise ValueError("Record field names must be non-empty strings.")
                if not _is_canonical_scalar(value):
                    raise ValueError("Record values must be finite canonical scalar values.")
                copied[field_name] = value
            ordered = dict(sorted(copied.items(), key=lambda item: _utf8(item[0])))
            frozen_records.append(MappingProxyType(ordered))
        frozen_tables.append((table_id, tuple(frozen_records)))
    return tuple(sorted(frozen_tables, key=lambda item: _utf8(item[0])))


def _table_from_frozen(tables, table_id) -> tuple[FrozenRecord, ...] | None:
    return next((rows for candidate, rows in tables if candidate == table_id), None)


def _is_logical_identifier(value: object) -> bool:
    return isinstance(value, str) and _LOGICAL_IDENTIFIER.fullmatch(value) is not None


def _is_canonical_scalar(value: object) -> bool:
    if value is None or isinstance(value, (str, bool, int)):
        return True
    return isinstance(value, float) and math.isfinite(value)


def _utf8(value: str) -> bytes:
    return value.encode("utf-8")


__all__ = [
    "CanonicalScalar",
    "FrozenRecord",
    "VALIDATION_EXECUTOR_UNSUPPORTED",
    "VALIDATION_RULE_FAILED",
    "ValidationDataContext",
    "ValidationExecutionDiagnostic",
    "ValidationExecutionResult",
    "ValidationOutcome",
]
