"""Fail-closed, group-scoped execution for the H7 contiguous-ordering shape."""

from __future__ import annotations

import json
import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from itertools import zip_longest
from types import MappingProxyType

try:  # Package import when the tools directory is on sys.path.
    from .canonical_validation_execution_core import (
        VALIDATION_RULE_FAILED,
        FrozenRecord,
        ValidationDataContext,
        ValidationExecutionDiagnostic,
        ValidationExecutionResult,
        ValidationOutcome,
        _resolve_field_schema,
        _resolve_table,
    )
    from .canonical_validation_expr import (
        BinaryOperation,
        Call,
        Identifier,
        Literal,
    )
    from .canonical_validation_expr_eval import ValidationExpressionEvaluationError
    from .canonical_validation_rules import ValidationRuleDefinition
except ImportError:  # Direct file loading used by the repository test suite.
    from canonical_validation_execution_core import (
        VALIDATION_RULE_FAILED,
        FrozenRecord,
        ValidationDataContext,
        ValidationExecutionDiagnostic,
        ValidationExecutionResult,
        ValidationOutcome,
        _resolve_field_schema,
        _resolve_table,
    )
    from canonical_validation_expr import BinaryOperation, Call, Identifier, Literal
    from canonical_validation_expr_eval import ValidationExpressionEvaluationError
    from canonical_validation_rules import ValidationRuleDefinition


VALIDATION_CONTIGUOUS_ORDER_FAILED = "VALIDATION_CONTIGUOUS_ORDER_FAILED"
VALIDATION_CONTIGUOUS_EVALUATION_ERROR = "VALIDATION_CONTIGUOUS_EVALUATION_ERROR"
VALIDATION_EXECUTOR_NOT_REGISTERED = "VALIDATION_EXECUTOR_NOT_REGISTERED"
_EXPECTED_CONTRACT = "each group's order values are exactly 1 through its row count"


@dataclass(frozen=True, slots=True)
class GroupEvaluationContext:
    """One immutable typed group, never an implicit first-row binding."""

    group_field: str
    group_value: object
    records: tuple[FrozenRecord, ...]

    def __post_init__(self) -> None:
        if type(self.group_field) is not str or not self.group_field:
            _evaluation_error("group_context", "group_field_name_invalid")
        if (
            self.group_value is not None
            and type(self.group_value) not in {bool, int, float, str}
        ) or (
            type(self.group_value) is float and not math.isfinite(self.group_value)
        ):
            _evaluation_error("group_context", "group_value_type_invalid")
        if type(self.records) is not tuple or not self.records:
            _evaluation_error("group_context", "group_records_invalid")
        if any(not isinstance(record, Mapping) for record in self.records):
            _evaluation_error("group_context", "group_record_invalid")
        object.__setattr__(
            self,
            "records",
            tuple(MappingProxyType(dict(record)) for record in self.records),
        )


def contiguous_ordering_capability_reason(
    rule: ValidationRuleDefinition,
) -> str | None:
    """Accept only the exact H7 AST shape, independent of rule identity."""

    if not isinstance(rule, ValidationRuleDefinition):
        raise TypeError("rule must be a ValidationRuleDefinition")
    if rule.validation_kind_id != "custom_expression":
        return "validation_kind_not_custom_expression"
    if rule.rule_scope_id != "table":
        return "rule_scope_not_table"
    if rule.target_field_id is None:
        return "target_field_missing"
    if _contiguous_shape(rule.condition_ast) is None:
        return "expression_shape_not_contiguous_ordering"
    return None


def execute_contiguous_ordering_rule(
    rule: ValidationRuleDefinition,
    data: ValidationDataContext,
) -> ValidationExecutionResult:
    """Evaluate the table-level H7 rule once, with one rule-level violation."""

    if not isinstance(rule, ValidationRuleDefinition):
        raise TypeError("rule must be a ValidationRuleDefinition")
    if not isinstance(data, ValidationDataContext):
        raise TypeError("data must be a ValidationDataContext")
    reason = contiguous_ordering_capability_reason(rule)
    if reason is not None:
        return _result(
            rule,
            ValidationOutcome.NOT_EXECUTED,
            VALIDATION_EXECUTOR_NOT_REGISTERED,
            "The custom expression is outside the H7 capability gate.",
            reason,
        )

    namespace = data.namespace_for_component(rule.component_identity)
    if data.namespaces and namespace is None:
        return _result(
            rule, ValidationOutcome.FAIL, VALIDATION_RULE_FAILED,
            "The source component namespace binding is missing.",
            "source_namespace_missing",
        )
    records = _resolve_table(data, rule.target_table_id, namespace=namespace)
    if records is None:
        return _result(
            rule, ValidationOutcome.FAIL, VALIDATION_RULE_FAILED,
            "The target table is missing from the validation data context.",
            "target_table_missing",
        )
    _, order_field = _contiguous_shape(rule.condition_ast)
    field_schema = _resolve_field_schema(
        data, rule.target_table_id,
        field_id=rule.target_field_id, namespace=namespace,
    )
    if field_schema is None or field_schema.get("field_name") != order_field:
        return _result(
            rule, ValidationOutcome.FAIL, VALIDATION_RULE_FAILED,
            "The declared target field does not resolve to the H7 order field.",
            "target_order_field_unresolved",
        )
    try:
        passed = evaluate_contiguous_expression(rule.condition_ast, records)
    except ValidationExpressionEvaluationError as error:
        details = ";".join(f"{key}={value}" for key, value in error.context)
        return _result(
            rule, ValidationOutcome.FAIL, VALIDATION_CONTIGUOUS_EVALUATION_ERROR,
            "The H7 expression could not be evaluated.",
            f"expression_evaluation_error:{details}",
            evaluated_record_count=len(records),
        )
    if not passed:
        return _result(
            rule, ValidationOutcome.FAIL, VALIDATION_CONTIGUOUS_ORDER_FAILED,
            "The target table violates its contiguous-ordering contract.",
            "expression_evaluated_false",
            evaluated_record_count=len(records),
        )
    return ValidationExecutionResult(
        rule.rule_id, ValidationOutcome.PASS, (), len(records), 0
    )


def evaluate_contiguous_expression(
    expression: object,
    records: Sequence[Mapping[str, object]],
) -> bool:
    """Evaluate for_each_group over every row, with no lifecycle filtering."""

    if not isinstance(expression, Call) or expression.function != "for_each_group":
        _evaluation_error("for_each_group", "outer_call_required")
    if len(expression.arguments) != 2:
        _evaluation_error("for_each_group", "builtin_arity_invalid")
    group_node, predicate = expression.arguments
    if not (
        isinstance(group_node, Literal)
        and group_node.literal_kind == "string"
        and type(group_node.value) is str
        and group_node.value
    ):
        _evaluation_error("for_each_group", "group_field_name_invalid")
    if isinstance(records, (str, bytes, bytearray)) or not isinstance(records, Sequence):
        _evaluation_error("for_each_group", "target_records_invalid")

    groups: dict[tuple[type, object], list[FrozenRecord]] = {}
    for record in records:
        if not isinstance(record, Mapping):
            _evaluation_error("for_each_group", "target_record_invalid")
        if group_node.value not in record:
            _evaluation_error("for_each_group", "group_field_missing")
        value = record[group_node.value]
        if (
            value is not None and type(value) not in {bool, int, float, str}
        ) or (type(value) is float and not math.isfinite(value)):
            _evaluation_error("for_each_group", "group_value_type_invalid")
        groups.setdefault((type(value), value), []).append(record)

    passed = True
    for (_, value), grouped_records in sorted(
        groups.items(), key=lambda item: _group_sort_key(item[0])
    ):
        context = GroupEvaluationContext(
            group_node.value, value, tuple(grouped_records)
        )
        group_result = evaluate_group_expression(predicate, context)
        if type(group_result) is not bool:
            _evaluation_error("for_each_group", "predicate_result_not_boolean")
        passed = passed and group_result
    return passed


def evaluate_group_expression(
    expression: object,
    group: GroupEvaluationContext | None,
) -> object:
    """Evaluate only H7 group operators and builtins under explicit scope."""

    if isinstance(expression, Literal):
        accepted = {
            "integer": int,
            "string": str,
            "boolean": bool,
            "null": type(None),
        }
        if accepted.get(expression.literal_kind) is not type(expression.value):
            _evaluation_error("literal", "literal_kind_or_value_invalid")
        return expression.value
    if isinstance(expression, BinaryOperation):
        left = evaluate_group_expression(expression.left, group)
        right = evaluate_group_expression(expression.right, group)
        if expression.operator == "+":
            if type(left) is not int or type(right) is not int:
                _evaluation_error("+", "integer_operands_required")
            return left + right
        if expression.operator == "==":
            if type(left) is not tuple or type(right) is not range:
                _evaluation_error("==", "sequence_operands_required")
            return _sequence_equal(left, right)
        _evaluation_error(expression.operator, "operator_not_allowlisted")
    if not isinstance(expression, Call):
        _evaluation_error("group_expression", "node_not_allowlisted")
    if expression.function == "count_rows":
        if expression.arguments:
            _evaluation_error("count_rows", "builtin_arity_invalid")
        if group is None:
            _evaluation_error("count_rows", "group_context_missing")
        return len(group.records)
    if expression.function == "sorted_unique":
        if len(expression.arguments) != 1:
            _evaluation_error("sorted_unique", "builtin_arity_invalid")
        if group is None:
            _evaluation_error("sorted_unique", "group_context_missing")
        field = expression.arguments[0]
        if not isinstance(field, Identifier) or not field.name:
            _evaluation_error("sorted_unique", "field_identifier_required")
        values: list[int] = []
        for record in group.records:
            if field.name not in record:
                _evaluation_error("sorted_unique", "order_field_missing")
            value = record[field.name]
            if type(value) is not int:
                _evaluation_error("sorted_unique", "order_value_not_integer")
            values.append(value)
        return tuple(sorted(set(values)))
    if expression.function == "range":
        if len(expression.arguments) != 2:
            _evaluation_error("range", "builtin_arity_invalid")
        start, end = (
            evaluate_group_expression(argument, group)
            for argument in expression.arguments
        )
        if type(start) is not int or type(end) is not int:
            _evaluation_error("range", "integer_arguments_required")
        return range(start, end)
    _evaluation_error(expression.function, "builtin_not_allowlisted")


def _contiguous_shape(expression: object) -> tuple[str, str] | None:
    if not (
        isinstance(expression, Call)
        and expression.function == "for_each_group"
        and len(expression.arguments) == 2
    ):
        return None
    group, predicate = expression.arguments
    if not (
        isinstance(group, Literal)
        and group.literal_kind == "string"
        and type(group.value) is str
        and group.value
        and isinstance(predicate, BinaryOperation)
        and predicate.operator == "=="
    ):
        return None
    ordered, expected = predicate.left, predicate.right
    if not (
        isinstance(ordered, Call)
        and ordered.function == "sorted_unique"
        and len(ordered.arguments) == 1
        and isinstance(ordered.arguments[0], Identifier)
        and ordered.arguments[0].name
        and isinstance(expected, Call)
        and expected.function == "range"
        and len(expected.arguments) == 2
    ):
        return None
    start, end = expected.arguments
    if not (
        _integer_literal_is_one(start)
        and isinstance(end, BinaryOperation)
        and end.operator == "+"
        and isinstance(end.left, Call)
        and end.left.function == "count_rows"
        and not end.left.arguments
        and _integer_literal_is_one(end.right)
    ):
        return None
    return group.value, ordered.arguments[0].name


def _integer_literal_is_one(node: object) -> bool:
    return (
        isinstance(node, Literal)
        and node.literal_kind == "integer"
        and type(node.value) is int
        and node.value == 1
    )


def _sequence_equal(
    left: Sequence[object], right: Sequence[object]
) -> bool:
    sentinel = object()
    return all(
        a is not sentinel
        and b is not sentinel
        and type(a) is type(b)
        and a == b
        for a, b in zip_longest(left, right, fillvalue=sentinel)
    )


def _group_sort_key(key: tuple[type, object]) -> tuple[bytes, bytes]:
    value_type, value = key
    return (
        value_type.__name__.encode("ascii"),
        json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8"),
    )


def _evaluation_error(builtin: str, reason: str) -> None:
    raise ValidationExpressionEvaluationError(
        node_type="Call", builtin=builtin, reason=reason
    )


def _result(
    rule: ValidationRuleDefinition,
    outcome: ValidationOutcome,
    code: str,
    message: str,
    reason: str,
    *,
    evaluated_record_count: int = 0,
) -> ValidationExecutionResult:
    diagnostic = ValidationExecutionDiagnostic(
        code,
        message,
        rule.rule_id,
        rule.target_table_id,
        rule.target_field_id,
        expected_contract=_EXPECTED_CONTRACT,
        reason=reason,
    )
    return ValidationExecutionResult(
        rule.rule_id,
        outcome,
        (diagnostic,),
        evaluated_record_count,
        0 if outcome is ValidationOutcome.NOT_EXECUTED else 1,
    )


__all__ = [
    "GroupEvaluationContext",
    "VALIDATION_CONTIGUOUS_EVALUATION_ERROR",
    "VALIDATION_CONTIGUOUS_ORDER_FAILED",
    "contiguous_ordering_capability_reason",
    "evaluate_contiguous_expression",
    "evaluate_group_expression",
    "execute_contiguous_ordering_rule",
]
