"""Isolated target-group mapping and technical-version consistency execution."""

from __future__ import annotations

from collections.abc import Mapping

try:
    from .canonical_validation_execution_core import (
        VALIDATION_EXECUTOR_UNSUPPORTED,
        VALIDATION_RULE_FAILED,
        CanonicalScalar,
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
        _valid_identity,
    )
    from .canonical_validation_expr import (
        BinaryOperation, Binding, Call, Identifier, Literal, MapLiteral, Sequence,
    )
    from .canonical_validation_expr_eval import (
        ValidationExpressionEvaluationError, evaluate_validation_expression,
    )
    from .canonical_validation_qualified_reference import (
        _ResolutionError, _resolve_registry_value, _resolve_scalar_lookup,
    )
    from .canonical_validation_rules import ValidationRuleDefinition
except ImportError:
    from canonical_validation_execution_core import (
        VALIDATION_EXECUTOR_UNSUPPORTED,
        VALIDATION_RULE_FAILED,
        CanonicalScalar,
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
        _valid_identity,
    )
    from canonical_validation_expr import (
        BinaryOperation, Binding, Call, Identifier, Literal, MapLiteral, Sequence,
    )
    from canonical_validation_expr_eval import (
        ValidationExpressionEvaluationError, evaluate_validation_expression,
    )
    from canonical_validation_qualified_reference import (
        _ResolutionError, _resolve_registry_value, _resolve_scalar_lookup,
    )
    from canonical_validation_rules import ValidationRuleDefinition


VALIDATION_TARGET_GROUP_MEMBERSHIP_FAILED = "VALIDATION_TARGET_GROUP_MEMBERSHIP_FAILED"
VALIDATION_CROSS_FIELD_CONSISTENCY_FAILED = "VALIDATION_CROSS_FIELD_CONSISTENCY_FAILED"
VALIDATION_REFERENCE_CONSTRAINT_EVALUATION_ERROR = "VALIDATION_REFERENCE_CONSTRAINT_EVALUATION_ERROR"

_TECHNICAL_VERSION_SHAPE = Call("when", (
    BinaryOperation("and",
        BinaryOperation("==", Identifier("authority_level"), Literal("string", "canonical_technical_source")),
        BinaryOperation("==", Identifier("status"), Literal("string", "active")),
    ),
    BinaryOperation("==", Identifier("version"), Call("lookup", (
        Literal("string", "meta"), Literal("string", "key"),
        Literal("string", "schema_version"), Literal("string", "value"),
    ))),
))


def execute_target_group_membership_rule(
    rule: ValidationRuleDefinition, data: ValidationDataContext,
) -> ValidationExecutionResult:
    return _execute(rule, data, "target_group_membership")


def execute_cross_field_consistency_rule(
    rule: ValidationRuleDefinition, data: ValidationDataContext,
) -> ValidationExecutionResult:
    return _execute(rule, data, "cross_field_consistency")


def _execute(
    rule: ValidationRuleDefinition, data: ValidationDataContext, kind: str,
) -> ValidationExecutionResult:
    if not isinstance(rule, ValidationRuleDefinition):
        raise TypeError("rule must be a ValidationRuleDefinition")
    if not isinstance(data, ValidationDataContext):
        raise TypeError("data must be a ValidationDataContext")
    reason = _contract_reason(rule, kind)
    if reason is not None:
        return _single_result(rule, ValidationOutcome.UNSUPPORTED, VALIDATION_EXECUTOR_UNSUPPORTED, reason)
    namespace = data.namespace_for_component(rule.component_identity)
    if namespace is None:
        return _single_result(rule, ValidationOutcome.FAIL, VALIDATION_RULE_FAILED, "source_namespace_missing")
    target_name = (
        _target_group_shape(rule.condition_ast)
        if kind == "target_group_membership" else "version"
    )
    schema = _resolve_field_schema(data, rule.target_table_id, field_id=rule.target_field_id, namespace=namespace)
    if schema is None or schema.get("field_name") != target_name:
        return _single_result(rule, ValidationOutcome.FAIL, VALIDATION_RULE_FAILED, "target_field_unresolved")
    primary_key = _resolve_primary_key(data, rule.target_table_id, namespace=namespace)
    if primary_key is None:
        return _single_result(rule, ValidationOutcome.FAIL, VALIDATION_RULE_FAILED, "target_table_schema_unresolved")
    records = _resolve_table(data, rule.target_table_id, namespace=namespace)
    if records is None:
        return _single_result(rule, ValidationOutcome.FAIL, VALIDATION_RULE_FAILED, "target_table_missing")

    diagnostics = []
    for record in sorted(records, key=lambda row: _record_sort_key(row, primary_key)):
        identity = _record_identity(record, primary_key)
        try:
            if not _valid_identity(record, primary_key):
                _evaluation_error("source_record_identity_invalid")
            if kind == "target_group_membership":
                binding, predicate = rule.condition_ast.statements
                if binding.name in record:
                    _evaluation_error("binding_source_identifier_collision")
                expected_group = evaluate_group_mapping(binding.value, record)
                passed = evaluate_validation_expression(
                    predicate, {**record, binding.name: expected_group},
                    registry_group_resolver=lambda registry_id: _resolve_registry_value(data, registry_id, "group_id"),
                )
            else:
                passed = evaluate_validation_expression(
                    rule.condition_ast, record,
                    lookup_resolver=lambda table, key, value, output: _resolve_scalar_lookup(
                        data, namespace, table, key, value, output
                    ),
                )
            if type(passed) is not bool:
                _evaluation_error("predicate_result_not_boolean")
        except _ResolutionError as error:
            diagnostics.append(_diagnostic(
                rule, VALIDATION_REFERENCE_CONSTRAINT_EVALUATION_ERROR,
                error.reason, identity, error.observed_value, error.related_record_identities,
            ))
            continue
        except ValidationExpressionEvaluationError as error:
            diagnostics.append(_diagnostic(
                rule, VALIDATION_REFERENCE_CONSTRAINT_EVALUATION_ERROR, str(error), identity,
            ))
            continue
        if not passed:
            code = (
                VALIDATION_TARGET_GROUP_MEMBERSHIP_FAILED
                if kind == "target_group_membership" else VALIDATION_CROSS_FIELD_CONSISTENCY_FAILED
            )
            diagnostics.append(_diagnostic(rule, code, "predicate_false", identity, False))
    ordered = tuple(sorted(diagnostics, key=_diagnostic_sort_key))
    return ValidationExecutionResult(
        rule.rule_id, ValidationOutcome.FAIL if ordered else ValidationOutcome.PASS,
        ordered, len(records), len(ordered),
    )


def evaluate_group_mapping(expression: object, record: Mapping[str, object]) -> str | None:
    """Evaluate only the family's string-to-group MapLiteral, without generic bindings."""
    if not _map_shape(expression):
        _evaluation_error("map_shape_invalid")
    key = evaluate_validation_expression(expression.arguments[0], record)
    if type(key) is not str or not key:
        _evaluation_error("map_key_invalid")
    return dict(expression.arguments[1].items).get(key)


def _map_shape(node: object) -> bool:
    if not (
        isinstance(node, Call) and node.function == "map" and len(node.arguments) == 2
        and isinstance(node.arguments[0], Identifier) and node.arguments[0].name
        and isinstance(node.arguments[1], MapLiteral)
    ):
        return False
    items = node.arguments[1].items
    if type(items) is not tuple or any(
        type(item) is not tuple or len(item) != 2
        or any(type(value) is not str or not value for value in item)
        for item in items
    ):
        return False
    keys = tuple(key for key, _ in items)
    return len(keys) == len(set(keys))


def _target_group_shape(node: object) -> str | None:
    if not isinstance(node, Sequence) or len(node.statements) != 2:
        return None
    binding, predicate = node.statements
    if not isinstance(binding, Binding) or not binding.name or not _map_shape(binding.value):
        return None
    if not (
        isinstance(predicate, BinaryOperation) and isinstance(predicate.right, BinaryOperation)
        and isinstance(predicate.right.left, Call) and len(predicate.right.left.arguments) == 1
        and isinstance(predicate.right.left.arguments[0], Identifier)
    ):
        return None
    target = predicate.right.left.arguments[0]
    if not target.name or binding.name in {binding.value.arguments[0].name, target.name, "current"}:
        return None
    expected = BinaryOperation("or",
        BinaryOperation("==", Identifier(binding.name), Literal("null", None)),
        BinaryOperation("==", Call("group_of", (target,)), Identifier(binding.name)),
    )
    return target.name if predicate == expected else None


def _contract_reason(rule: ValidationRuleDefinition, kind: str) -> str | None:
    if rule.validation_kind_id != kind:
        return "validation_kind_not_supported_by_executor"
    if rule.validation_stage_id != "pre_export":
        return "validation_stage_not_pre_export"
    if rule.target_field_id is None:
        return "target_field_missing"
    if any(value is not None for value in (
        rule.operator_id, rule.comparison_value, rule.minimum_value, rule.maximum_value,
    )):
        return "structured_shape_not_supported"
    if kind == "target_group_membership":
        scope, reference = "record", ("value_registry", "fld_value_registry_registry_value_id")
        supported = _target_group_shape(rule.condition_ast) is not None
    else:
        scope, reference = "cross_table", ("meta", "fld_meta_value")
        supported = rule.condition_ast == _TECHNICAL_VERSION_SHAPE
    if rule.rule_scope_id != scope:
        return "rule_scope_not_supported"
    if (rule.reference_table_id, rule.reference_field_id) != reference:
        return "reference_contract_not_supported"
    return None if supported else "expression_shape_not_supported"


def _evaluation_error(reason: str) -> None:
    raise ValidationExpressionEvaluationError(node_type="Call", reason=reason)


def _diagnostic(
    rule: ValidationRuleDefinition, code: str, reason: str,
    identity: str | None = None, observed: CanonicalScalar = None, related: tuple[str, ...] = (),
) -> ValidationExecutionDiagnostic:
    return ValidationExecutionDiagnostic(
        code, "The reference constraint could not be satisfied.",
        rule.rule_id, rule.target_table_id, rule.target_field_id, identity, observed,
        rule.condition_expression_source, reason, related,
    )


def _single_result(
    rule: ValidationRuleDefinition, outcome: ValidationOutcome, code: str, reason: str,
) -> ValidationExecutionResult:
    return ValidationExecutionResult(
        rule.rule_id, outcome, (_diagnostic(rule, code, reason),), 0,
        0 if outcome is ValidationOutcome.UNSUPPORTED else 1,
    )


__all__ = [
    "VALIDATION_TARGET_GROUP_MEMBERSHIP_FAILED",
    "VALIDATION_CROSS_FIELD_CONSISTENCY_FAILED",
    "VALIDATION_REFERENCE_CONSTRAINT_EVALUATION_ERROR",
    "evaluate_group_mapping",
    "execute_target_group_membership_rule",
    "execute_cross_field_consistency_rule",
]
