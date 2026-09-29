"""Narrow, table-scoped normalized uniqueness with typed nullable group keys."""

from __future__ import annotations

import json
import math
from collections.abc import Mapping, Sequence
from typing import TypeAlias

try:  # Package import when the tools directory is on sys.path.
    from .canonical_validation_execution_core import (
        VALIDATION_EXECUTOR_UNSUPPORTED,
        VALIDATION_RULE_FAILED,
        CanonicalScalar,
        FrozenRecord,
        ValidationDataContext,
        ValidationExecutionDiagnostic,
        ValidationExecutionResult,
        ValidationOutcome,
        _diagnostic_sort_key,
        _record_identity,
        _record_sort_key,
        _resolve_field_schema,
        _resolve_primary_key,
        _resolve_table,
        _utf8,
        _valid_identity,
    )
    from .canonical_validation_expr import BinaryOperation, Call, Identifier, ListLiteral, Literal
    from .canonical_validation_expr_eval import (
        ValidationExpressionEvaluationError,
        evaluate_validation_expression,
    )
    from .canonical_validation_rules import ValidationRuleDefinition
except ImportError:  # Direct file loading used by the repository test suite.
    from canonical_validation_execution_core import (
        VALIDATION_EXECUTOR_UNSUPPORTED,
        VALIDATION_RULE_FAILED,
        CanonicalScalar,
        FrozenRecord,
        ValidationDataContext,
        ValidationExecutionDiagnostic,
        ValidationExecutionResult,
        ValidationOutcome,
        _diagnostic_sort_key,
        _record_identity,
        _record_sort_key,
        _resolve_field_schema,
        _resolve_primary_key,
        _resolve_table,
        _utf8,
        _valid_identity,
    )
    from canonical_validation_expr import BinaryOperation, Call, Identifier, ListLiteral, Literal
    from canonical_validation_expr_eval import (
        ValidationExpressionEvaluationError,
        evaluate_validation_expression,
    )
    from canonical_validation_rules import ValidationRuleDefinition


VALIDATION_NORMALIZED_UNIQUENESS_CONFLICT = "VALIDATION_NORMALIZED_UNIQUENESS_CONFLICT"
VALIDATION_NORMALIZED_UNIQUENESS_EVALUATION_ERROR = (
    "VALIDATION_NORMALIZED_UNIQUENESS_EVALUATION_ERROR"
)
TypedScalar: TypeAlias = tuple[str, CanonicalScalar]
CompositeGroupKey: TypeAlias = tuple[TypedScalar, ...]


def execute_normalized_uniqueness_rule(
    rule: ValidationRuleDefinition,
    data: ValidationDataContext,
) -> ValidationExecutionResult:
    """Execute only the E4 shape; report each invalid row or violating group."""
    if not isinstance(rule, ValidationRuleDefinition):
        raise TypeError("rule must be a ValidationRuleDefinition")
    if not isinstance(data, ValidationDataContext):
        raise TypeError("data must be a ValidationDataContext")
    reason = _unsupported_reason(rule)
    if reason is not None:
        diagnostic = _diagnostic(rule, VALIDATION_EXECUTOR_UNSUPPORTED, reason)
        return ValidationExecutionResult(
            rule.rule_id, ValidationOutcome.UNSUPPORTED, (diagnostic,), 0, 0
        )

    group_expression, predicate = rule.condition_ast.arguments
    normalized = next(item for item in group_expression.items if isinstance(item, Call))
    namespace = data.namespace_for_component(rule.component_identity)
    if data.namespaces and namespace is None:
        return _failure(rule, "source_namespace_missing")
    schema = _resolve_field_schema(
        data, rule.target_table_id, field_id=rule.target_field_id, namespace=namespace
    )
    if schema is None or schema.get("field_name") != normalized.arguments[0].name:
        return _failure(rule, "target_normalized_field_unresolved")
    primary_key = _resolve_primary_key(data, rule.target_table_id, namespace=namespace)
    if primary_key is None:
        return _failure(rule, "target_table_schema_unresolved")
    records = _resolve_table(data, rule.target_table_id, namespace=namespace)
    if records is None:
        return _failure(rule, "target_table_missing")

    groups: dict[CompositeGroupKey, list[FrozenRecord]] = {}
    diagnostics: list[ValidationExecutionDiagnostic] = []
    for record in sorted(records, key=lambda item: _record_sort_key(item, primary_key)):
        identity = _record_identity(record, primary_key)
        try:
            if not _valid_identity(record, primary_key):
                _evaluation_error("record", "source_record_identity_invalid")
            key = composite_group_key(group_expression, record)
        except ValidationExpressionEvaluationError as error:
            diagnostics.append(_diagnostic(
                rule, VALIDATION_NORMALIZED_UNIQUENESS_EVALUATION_ERROR,
                str(error), identity=identity,
            ))
            continue
        groups.setdefault(key, []).append(record)

    for key in sorted(groups, key=lambda value: _utf8(_json_text(value))):
        group = groups[key]
        identities = tuple(sorted(
            (_record_identity(record, primary_key) for record in group), key=_utf8
        ))
        try:
            targets = _distinct_group_values(predicate.left, group)
        except ValidationExpressionEvaluationError as error:
            diagnostics.append(_diagnostic(
                rule, VALIDATION_NORMALIZED_UNIQUENESS_EVALUATION_ERROR,
                str(error), observed=_json_text({"group_key": key}), related=identities,
            ))
            continue
        count = len(targets)
        passed = count == 1 if predicate.operator == "==" else count <= 1
        if not passed:
            diagnostics.append(_diagnostic(
                rule, VALIDATION_NORMALIZED_UNIQUENESS_CONFLICT,
                "distinct_non_null_target_count_violates_predicate",
                observed=_json_text({"group_key": key, "non_null_targets": targets}),
                related=identities,
            ))
    ordered = tuple(sorted(diagnostics, key=_diagnostic_sort_key))
    return ValidationExecutionResult(
        rule.rule_id, ValidationOutcome.FAIL if ordered else ValidationOutcome.PASS,
        ordered, len(records), len(ordered),
    )


def composite_group_key(expression: object, record: Mapping[str, object]) -> CompositeGroupKey:
    """Evaluate one ordered key, interpreting string tokens as field names."""
    if not isinstance(expression, ListLiteral) or not 1 <= len(expression.items) <= 3:
        _evaluation_error("for_each_group", "composite_key_arity_invalid")
    if not isinstance(record, Mapping):
        _evaluation_error("for_each_group", "source_record_invalid")
    components = []
    for item in expression.items:
        if _field_token(item):
            value = _scalar_expression(Identifier(item.value), record)
        elif _normalize_shape(item):
            value = _scalar_expression(item.arguments[0], record)
            if value is None:
                # Validate mode and case through the existing normalize contract,
                # while preserving null only on this family's group-key surface.
                probe = Call("normalize", (Literal("string", ""), *item.arguments[1:]))
                evaluate_validation_expression(probe, record)
            else:
                value = evaluate_validation_expression(item, record)
        else:
            _evaluation_error("for_each_group", "group_component_not_supported")
        components.append(_typed_scalar(value))
    return tuple(components)


def evaluate_count_distinct(expression: object, records: Sequence[Mapping[str, object]]) -> int:
    """Count exact typed non-null scalar values under explicit group scope."""
    return len(_distinct_group_values(expression, records))


def _distinct_group_values(
    expression: object, records: Sequence[Mapping[str, object]],
) -> tuple[TypedScalar, ...]:
    if not isinstance(expression, Call) or expression.function != "count_distinct":
        _evaluation_error("count_distinct", "count_distinct_call_required")
    if len(expression.arguments) != 1:
        _evaluation_error("count_distinct", "builtin_arity_invalid")
    if isinstance(records, (str, bytes, bytearray)) or not isinstance(records, Sequence):
        _evaluation_error("count_distinct", "group_context_missing_or_invalid")
    values: set[TypedScalar] = set()
    for record in records:
        if not isinstance(record, Mapping):
            _evaluation_error("count_distinct", "source_record_invalid")
        value = _scalar_expression(expression.arguments[0], record)
        if value is not None:
            values.add(_typed_scalar(value))
    return tuple(sorted(values, key=lambda value: _utf8(_json_text(value))))


def _scalar_expression(expression: object, record: Mapping[str, object]) -> CanonicalScalar:
    if isinstance(expression, Identifier):
        if expression.name not in record:
            _evaluation_error("scalar", "identifier_missing", expression.name)
        value = record[expression.name]
    elif isinstance(expression, Literal):
        value = evaluate_validation_expression(expression, {})
    else:
        _evaluation_error("scalar", "scalar_expression_not_supported")
    _typed_scalar(value)
    return value


def _typed_scalar(value: object) -> TypedScalar:
    if value is None:
        return "null", None
    if type(value) not in {bool, int, float, str} or (
        type(value) is float and not math.isfinite(value)
    ):
        _evaluation_error("scalar", "non_scalar_or_non_finite_value")
    return type(value).__name__, value


def _unsupported_reason(rule: ValidationRuleDefinition) -> str | None:
    if rule.validation_kind_id != "normalized_uniqueness":
        return "validation_kind_not_normalized_uniqueness"
    if rule.rule_scope_id != "table":
        return "rule_scope_not_table"
    if rule.validation_stage_id != "pre_export":
        return "validation_stage_not_pre_export"
    if rule.target_field_id is None:
        return "target_field_missing"
    if any(value is not None for value in (
        rule.operator_id, rule.comparison_value, rule.minimum_value, rule.maximum_value,
        rule.reference_table_id, rule.reference_field_id,
    )):
        return "structured_shape_not_supported"
    root = rule.condition_ast
    if not isinstance(root, Call) or root.function != "for_each_group" or len(root.arguments) != 2:
        return "expression_shape_not_supported"
    key, predicate = root.arguments
    if not isinstance(key, ListLiteral) or not 1 <= len(key.items) <= 3:
        return "composite_key_shape_not_supported"
    if sum(_normalize_shape(item) for item in key.items) != 1 or any(
        not _field_token(item) and not _normalize_shape(item) for item in key.items
    ):
        return "normalized_key_shape_not_supported"
    if not (
        isinstance(predicate, BinaryOperation) and predicate.operator in {"==", "<="}
        and isinstance(predicate.right, Literal) and predicate.right.literal_kind == "integer"
        and type(predicate.right.value) is int and predicate.right.value == 1
        and isinstance(predicate.left, Call) and predicate.left.function == "count_distinct"
        and len(predicate.left.arguments) == 1
        and isinstance(predicate.left.arguments[0], Identifier)
        and predicate.left.arguments[0].name
    ):
        return "distinct_predicate_shape_not_supported"
    return None


def _field_token(node: object) -> bool:
    return (
        isinstance(node, Literal) and node.literal_kind == "string"
        and type(node.value) is str and bool(node.value)
    )


def _normalize_shape(node: object) -> bool:
    if not isinstance(node, Call) or node.function != "normalize" or len(node.arguments) != 3:
        return False
    value, mode, case = node.arguments
    return (
        isinstance(value, Identifier) and bool(value.name)
        and (isinstance(mode, Identifier) and bool(mode.name) or _field_token(mode))
        and (
            isinstance(case, Identifier) and bool(case.name)
            or isinstance(case, Literal) and case.literal_kind == "boolean" and type(case.value) is bool
        )
    )


def _json_text(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _evaluation_error(builtin: str, reason: str, identifier: str | None = None) -> None:
    raise ValidationExpressionEvaluationError(
        node_type="Call", builtin=builtin, reason=reason, identifier=identifier
    )


def _diagnostic(
    rule: ValidationRuleDefinition, code: str, reason: str, *, identity: str | None = None,
    observed: CanonicalScalar = None, related: tuple[str, ...] = (),
) -> ValidationExecutionDiagnostic:
    return ValidationExecutionDiagnostic(
        code, "Normalized uniqueness validation could not satisfy its group contract.",
        rule.rule_id, rule.target_table_id, rule.target_field_id,
        identity, observed, rule.condition_expression_source, reason, related,
    )


def _failure(rule: ValidationRuleDefinition, reason: str) -> ValidationExecutionResult:
    return ValidationExecutionResult(
        rule.rule_id, ValidationOutcome.FAIL,
        (_diagnostic(rule, VALIDATION_RULE_FAILED, reason),), 0, 1,
    )


__all__ = [
    "VALIDATION_NORMALIZED_UNIQUENESS_CONFLICT",
    "VALIDATION_NORMALIZED_UNIQUENESS_EVALUATION_ERROR",
    "composite_group_key",
    "evaluate_count_distinct",
    "execute_normalized_uniqueness_rule",
]
