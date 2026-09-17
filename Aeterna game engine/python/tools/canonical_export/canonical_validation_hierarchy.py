"""Deterministic execution for the canonical hierarchy-integrity family."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import TypeAlias

try:  # Package import when the tools directory is on sys.path.
    from .canonical_validation_execution_core import (
        VALIDATION_EXECUTOR_UNSUPPORTED,
        CanonicalScalar,
        FrozenRecord,
        ValidationDataContext,
        ValidationExecutionDiagnostic,
        ValidationExecutionResult,
        ValidationOutcome,
        _canonical_record_text,
        _diagnostic_sort_key,
        _record_identity,
        _record_sort_key,
        _resolve_field_schema,
        _resolve_primary_key,
        _resolve_table,
        _utf8,
        _valid_identity,
    )
    from .canonical_validation_expr import BinaryOperation, Call, Literal
    from .canonical_validation_rules import ValidationRuleDefinition
except ImportError:  # Direct file loading used by the repository test suite.
    from canonical_validation_execution_core import (
        VALIDATION_EXECUTOR_UNSUPPORTED,
        CanonicalScalar,
        FrozenRecord,
        ValidationDataContext,
        ValidationExecutionDiagnostic,
        ValidationExecutionResult,
        ValidationOutcome,
        _canonical_record_text,
        _diagnostic_sort_key,
        _record_identity,
        _record_sort_key,
        _resolve_field_schema,
        _resolve_primary_key,
        _resolve_table,
        _utf8,
        _valid_identity,
    )
    from canonical_validation_expr import BinaryOperation, Call, Literal
    from canonical_validation_rules import ValidationRuleDefinition


VALIDATION_HIERARCHY_INTEGRITY_FAILED = (
    "VALIDATION_HIERARCHY_INTEGRITY_FAILED"
)
VALIDATION_HIERARCHY_TARGET_RECORD_INVALID = (
    "VALIDATION_HIERARCHY_TARGET_RECORD_INVALID"
)
VALIDATION_HIERARCHY_TARGET_TABLE_MISSING = (
    "VALIDATION_HIERARCHY_TARGET_TABLE_MISSING"
)

TypedNodeId: TypeAlias = tuple[str, str | int]


@dataclass(frozen=True, slots=True)
class _HierarchyRecord:
    node_id: TypedNodeId
    node_value: str | int
    parent_id: TypedNodeId | None
    parent_value: str | int | None
    record_identity: str


def execute_hierarchy_integrity_rule(
    rule: ValidationRuleDefinition,
    data: ValidationDataContext,
) -> ValidationExecutionResult:
    """Execute one exact no-self-reference and acyclic-parent contract."""
    if not isinstance(rule, ValidationRuleDefinition):
        raise TypeError("rule must be a ValidationRuleDefinition")
    if not isinstance(data, ValidationDataContext):
        raise TypeError("data must be a ValidationDataContext")

    fields, reason = _hierarchy_expression_contract(rule)
    if reason is not None or fields is None:
        return _single_result(
            rule,
            ValidationOutcome.UNSUPPORTED,
            VALIDATION_EXECUTOR_UNSUPPORTED,
            reason or "hierarchy_expression_invalid",
            None,
        )
    node_field, parent_field = fields

    namespace = data.namespace_for_component(rule.component_identity)
    if namespace is None:
        return _single_result(
            rule,
            ValidationOutcome.FAIL,
            VALIDATION_HIERARCHY_TARGET_TABLE_MISSING,
            "source_namespace_missing",
            None,
        )
    primary_key = _resolve_primary_key(
        data, rule.target_table_id, namespace=namespace
    )
    if primary_key is None:
        return _single_result(
            rule,
            ValidationOutcome.FAIL,
            VALIDATION_HIERARCHY_TARGET_TABLE_MISSING,
            "target_table_schema_unresolved",
            namespace,
        )

    node_schema = _resolve_field_schema(
        data,
        rule.target_table_id,
        field_name=node_field,
        namespace=namespace,
    )
    parent_schema = _resolve_field_schema(
        data,
        rule.target_table_id,
        field_name=parent_field,
        namespace=namespace,
    )
    schema_reason = _hierarchy_schema_reason(
        rule,
        primary_key,
        node_field,
        parent_field,
        node_schema,
        parent_schema,
    )
    if schema_reason is not None:
        unsupported = schema_reason in {
            "node_field_not_primary_key",
            "target_field_not_parent_field",
        }
        return _single_result(
            rule,
            (
                ValidationOutcome.UNSUPPORTED
                if unsupported
                else ValidationOutcome.FAIL
            ),
            (
                VALIDATION_EXECUTOR_UNSUPPORTED
                if unsupported
                else VALIDATION_HIERARCHY_TARGET_RECORD_INVALID
            ),
            schema_reason,
            namespace,
            node_field,
            parent_field,
        )
    assert node_schema is not None and parent_schema is not None

    target_records = _resolve_table(
        data, rule.target_table_id, namespace=namespace
    )
    if target_records is None:
        return _single_result(
            rule,
            ValidationOutcome.FAIL,
            VALIDATION_HIERARCHY_TARGET_TABLE_MISSING,
            "target_table_missing",
            namespace,
            node_field,
            parent_field,
        )

    expected = _expected_contract(
        namespace, rule.target_table_id, node_field, parent_field
    )
    diagnostics: list[ValidationExecutionDiagnostic] = []
    valid_records: list[_HierarchyRecord] = []
    for record in sorted(
        target_records,
        key=lambda item: _record_sort_key(item, primary_key),
    ):
        candidate, diagnostic = _validate_record(
            rule,
            record,
            primary_key,
            node_field,
            parent_field,
            node_schema,
            parent_schema,
            expected,
        )
        if diagnostic is not None:
            diagnostics.append(diagnostic)
        else:
            assert candidate is not None
            valid_records.append(candidate)

    groups: dict[TypedNodeId, list[_HierarchyRecord]] = {}
    for record in valid_records:
        groups.setdefault(record.node_id, []).append(record)

    unique: dict[TypedNodeId, _HierarchyRecord] = {}
    for node_id in sorted(groups, key=_node_sort_key):
        group = groups[node_id]
        identities = tuple(
            sorted(
                (record.record_identity for record in group),
                key=_utf8,
            )
        )
        if len(group) > 1:
            diagnostics.append(
                _diagnostic(
                    rule,
                    VALIDATION_HIERARCHY_INTEGRITY_FAILED,
                    "duplicate_node_id",
                    identities[0],
                    _typed_node_text(node_id),
                    expected,
                    identities,
                    node_schema.get("field_id"),
                )
            )
        else:
            unique[node_id] = group[0]

    edges: dict[TypedNodeId, TypedNodeId] = {}
    for node_id in sorted(unique, key=_node_sort_key):
        record = unique[node_id]
        if record.parent_id is None:
            continue
        if record.parent_id == node_id:
            diagnostics.append(
                _diagnostic(
                    rule,
                    VALIDATION_HIERARCHY_INTEGRITY_FAILED,
                    "self_reference",
                    record.record_identity,
                    record.parent_value,
                    expected,
                    (record.record_identity,),
                    parent_schema.get("field_id"),
                )
            )
            continue
        if record.parent_id in unique:
            edges[node_id] = record.parent_id

    for cycle in _find_cycles(edges):
        cycle_records = tuple(unique[node_id] for node_id in cycle)
        related = tuple(
            sorted(
                (record.record_identity for record in cycle_records),
                key=_utf8,
            )
        )
        diagnostics.append(
            _diagnostic(
                rule,
                VALIDATION_HIERARCHY_INTEGRITY_FAILED,
                "cycle",
                cycle_records[0].record_identity,
                _cycle_text(cycle),
                expected,
                related,
                parent_schema.get("field_id"),
            )
        )

    ordered = tuple(sorted(diagnostics, key=_diagnostic_sort_key))
    return ValidationExecutionResult(
        rule.rule_id,
        ValidationOutcome.FAIL if ordered else ValidationOutcome.PASS,
        ordered,
        len(target_records),
        len(ordered),
    )


def _hierarchy_expression_contract(
    rule: ValidationRuleDefinition,
) -> tuple[tuple[str, str] | None, str | None]:
    if rule.validation_kind_id != "hierarchy_integrity":
        return None, "validation_kind_not_hierarchy_integrity"
    if rule.validation_stage_id != "pre_export":
        return None, "validation_stage_not_pre_export"
    if rule.rule_scope_id != "table":
        return None, "rule_scope_not_table"
    if rule.target_field_id is None:
        return None, "target_field_missing"
    if any(
        value is not None
        for value in (
            rule.operator_id,
            rule.comparison_value,
            rule.minimum_value,
            rule.maximum_value,
            rule.reference_table_id,
            rule.reference_field_id,
        )
    ):
        return None, "structured_shape_not_supported"
    if (
        type(rule.condition_expression_source) is not str
        or not rule.condition_expression_source
        or rule.condition_ast is None
        or type(rule.condition_ast_hash) is not str
        or not rule.condition_ast_hash
    ):
        return None, "condition_expression_missing_or_invalid"

    root = rule.condition_ast
    if not isinstance(root, BinaryOperation) or root.operator != "and":
        return None, "hierarchy_root_not_exact_and"
    calls = (root.left, root.right)
    if not (
        isinstance(calls[0], Call)
        and calls[0].function == "no_self_reference"
        and isinstance(calls[1], Call)
        and calls[1].function == "hierarchy_is_acyclic"
    ):
        return None, "hierarchy_builtin_order_or_name_invalid"

    tokens: list[tuple[str, str]] = []
    for call in calls:
        assert isinstance(call, Call)
        if len(call.arguments) != 2:
            return None, f"{call.function}_arity_invalid"
        if any(
            not isinstance(argument, Literal)
            or argument.literal_kind != "string"
            or type(argument.value) is not str
            or not argument.value
            for argument in call.arguments
        ):
            return None, f"{call.function}_field_token_invalid"
        tokens.append(tuple(argument.value for argument in call.arguments))
    if tokens[0] != tokens[1]:
        return None, "hierarchy_field_tokens_disagree"
    if tokens[0][0] == tokens[0][1]:
        return None, "hierarchy_fields_not_distinct"
    return tokens[0], None


def _hierarchy_schema_reason(
    rule: ValidationRuleDefinition,
    primary_key: str,
    node_field: str,
    parent_field: str,
    node_schema: FrozenRecord | None,
    parent_schema: FrozenRecord | None,
) -> str | None:
    if node_schema is None:
        return "node_field_schema_unresolved"
    if parent_schema is None:
        return "parent_field_schema_unresolved"
    if primary_key != node_field:
        return "node_field_not_primary_key"
    if parent_schema.get("field_id") != rule.target_field_id:
        return "target_field_not_parent_field"
    if node_schema.get("data_type") not in {"string", "integer"}:
        return "node_field_type_not_identity_scalar"
    if not (
        node_schema.get("nullable") is False
        and node_schema.get("required_mode") == "always"
        and node_schema.get("null_handling") == "forbidden"
    ):
        return "node_field_null_contract_invalid"
    if parent_schema.get("data_type") != node_schema.get("data_type"):
        return "parent_field_type_mismatch"
    nullable = parent_schema.get("nullable")
    if nullable is True:
        if not (
            parent_schema.get("required_mode") == "conditional"
            and parent_schema.get("null_handling") == "explicit_null"
        ):
            return "parent_field_null_contract_invalid"
    elif nullable is False:
        if not (
            parent_schema.get("required_mode") == "always"
            and parent_schema.get("null_handling") == "forbidden"
        ):
            return "parent_field_null_contract_invalid"
    else:
        return "parent_field_nullable_invalid"
    if not (
        parent_schema.get("reference_table_id") == rule.target_table_id
        and parent_schema.get("reference_field_id")
        == node_schema.get("field_id")
    ):
        return "parent_field_domain_mismatch"
    return None


def _validate_record(
    rule: ValidationRuleDefinition,
    record: FrozenRecord,
    primary_key: str,
    node_field: str,
    parent_field: str,
    node_schema: FrozenRecord,
    parent_schema: FrozenRecord,
    expected: str,
) -> tuple[_HierarchyRecord | None, ValidationExecutionDiagnostic | None]:
    identity = _safe_record_identity(record, primary_key)
    if node_field not in record:
        return None, _record_diagnostic(
            rule, "node_field_missing", identity, None, expected,
            node_schema.get("field_id"),
        )
    node_value = record[node_field]
    expected_type = str if node_schema.get("data_type") == "string" else int
    if node_value is None:
        return None, _record_diagnostic(
            rule, "node_value_null_forbidden", identity, node_value, expected,
            node_schema.get("field_id"),
        )
    if type(node_value) is not expected_type:
        return None, _record_diagnostic(
            rule, "node_value_type_invalid", identity, node_value, expected,
            node_schema.get("field_id"),
        )
    if not _valid_identity(record, primary_key):
        return None, _record_diagnostic(
            rule, "node_identity_invalid", identity, node_value, expected,
            node_schema.get("field_id"),
        )
    if parent_field not in record:
        return None, _record_diagnostic(
            rule, "parent_field_missing", identity, None, expected,
            parent_schema.get("field_id"),
        )
    parent_value = record[parent_field]
    if parent_value is None:
        if parent_schema.get("nullable") is not True:
            return None, _record_diagnostic(
                rule, "parent_value_null_forbidden", identity, None, expected,
                parent_schema.get("field_id"),
            )
        parent_id = None
    elif type(parent_value) is not expected_type:
        return None, _record_diagnostic(
            rule, "parent_value_type_invalid", identity, parent_value, expected,
            parent_schema.get("field_id"),
        )
    elif type(parent_value) is str and not parent_value:
        return None, _record_diagnostic(
            rule, "parent_value_blank", identity, parent_value, expected,
            parent_schema.get("field_id"),
        )
    else:
        parent_id = (node_schema["data_type"], parent_value)

    assert type(node_value) in {str, int}
    return _HierarchyRecord(
        (node_schema["data_type"], node_value),
        node_value,
        parent_id,
        parent_value,
        _record_identity(record, primary_key),
    ), None


def _find_cycles(
    edges: dict[TypedNodeId, TypedNodeId],
) -> tuple[tuple[TypedNodeId, ...], ...]:
    finished: set[TypedNodeId] = set()
    cycles: list[tuple[TypedNodeId, ...]] = []
    for start in sorted(edges, key=_node_sort_key):
        if start in finished:
            continue
        path: list[TypedNodeId] = []
        positions: dict[TypedNodeId, int] = {}
        current = start
        while (
            current in edges
            and current not in finished
            and current not in positions
        ):
            positions[current] = len(path)
            path.append(current)
            current = edges[current]
        if current in positions:
            cycle = tuple(path[positions[current]:])
            if len(cycle) > 1:
                cycles.append(_canonical_cycle(cycle))
        finished.update(path)
    return tuple(sorted(cycles, key=lambda cycle: _utf8(_cycle_text(cycle))))


def _canonical_cycle(cycle: tuple[TypedNodeId, ...]) -> tuple[TypedNodeId, ...]:
    start = min(range(len(cycle)), key=lambda index: _node_sort_key(cycle[index]))
    return cycle[start:] + cycle[:start]


def _node_sort_key(node_id: TypedNodeId) -> bytes:
    return _utf8(_typed_node_text(node_id))


def _typed_node_text(node_id: TypedNodeId) -> str:
    return json.dumps(node_id, ensure_ascii=False, separators=(",", ":"))


def _cycle_text(cycle: tuple[TypedNodeId, ...]) -> str:
    return json.dumps(
        [value for _data_type, value in cycle],
        ensure_ascii=False,
        separators=(",", ":"),
    )


def _safe_record_identity(record: FrozenRecord, primary_key: str) -> str:
    if _valid_identity(record, primary_key):
        return _record_identity(record, primary_key)
    digest = hashlib.sha256(
        _canonical_record_text(record).encode("utf-8")
    ).hexdigest()
    return f"canonical-record-sha256:{digest}"


def _expected_contract(
    namespace: str,
    table_id: str,
    node_field: str,
    parent_field: str,
) -> str:
    return (
        f"exact typed acyclic parent graph {namespace}:{table_id}; "
        f"node_field={node_field}; parent_field={parent_field}"
    )


def _record_diagnostic(
    rule: ValidationRuleDefinition,
    reason: str,
    identity: str,
    observed: CanonicalScalar,
    expected: str,
    field_id: object,
) -> ValidationExecutionDiagnostic:
    return _diagnostic(
        rule,
        VALIDATION_HIERARCHY_TARGET_RECORD_INVALID,
        reason,
        identity,
        observed,
        expected,
        field_id=field_id,
    )


def _diagnostic(
    rule: ValidationRuleDefinition,
    code: str,
    reason: str,
    identity: str | None,
    observed: CanonicalScalar,
    expected: str,
    related: tuple[str, ...] = (),
    field_id: object = None,
) -> ValidationExecutionDiagnostic:
    return ValidationExecutionDiagnostic(
        code,
        "Canonical hierarchy validation failed.",
        rule.rule_id,
        rule.target_table_id,
        field_id if isinstance(field_id, str) else rule.target_field_id,
        identity,
        observed,
        expected,
        reason,
        related,
    )


def _single_result(
    rule: ValidationRuleDefinition,
    outcome: ValidationOutcome,
    code: str,
    reason: str,
    namespace: str | None,
    node_field: str | None = None,
    parent_field: str | None = None,
) -> ValidationExecutionResult:
    expected = (
        _expected_contract(
            namespace, rule.target_table_id, node_field, parent_field
        )
        if namespace is not None
        and node_field is not None
        and parent_field is not None
        else "bound source namespace and exact hierarchy-integrity expression"
    )
    diagnostic = _diagnostic(
        rule, code, reason, None, None, expected
    )
    return ValidationExecutionResult(
        rule.rule_id,
        outcome,
        (diagnostic,),
        0,
        0 if outcome is ValidationOutcome.UNSUPPORTED else 1,
    )


__all__ = [
    "VALIDATION_HIERARCHY_INTEGRITY_FAILED",
    "VALIDATION_HIERARCHY_TARGET_RECORD_INVALID",
    "VALIDATION_HIERARCHY_TARGET_TABLE_MISSING",
    "execute_hierarchy_integrity_rule",
]
