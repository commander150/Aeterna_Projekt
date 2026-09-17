"""Fail-closed execution for the E2 scalar/string/pattern expression slice."""

from __future__ import annotations

try:  # Package import when the tools directory is on sys.path.
    from .canonical_validation_execution_core import (
        VALIDATION_RULE_FAILED,
        ValidationDataContext,
        ValidationExecutionDiagnostic,
        ValidationExecutionResult,
        ValidationOutcome,
        _diagnostic_sort_key,
        _record_identity,
        _record_sort_key,
        _resolve_primary_key,
        _resolve_table,
    )
    from .canonical_validation_expr import (
        BinaryOperation,
        Call,
        Identifier,
        ListLiteral,
        Literal,
    )
    from .canonical_validation_expr_eval import (
        ValidationExpressionEvaluationError,
        evaluate_validation_expression,
    )
    from .canonical_validation_contiguous_order import (
        VALIDATION_CONTIGUOUS_EVALUATION_ERROR,
        VALIDATION_CONTIGUOUS_ORDER_FAILED,
        contiguous_ordering_capability_reason,
        execute_contiguous_ordering_rule,
    )
    from .canonical_validation_rules import ValidationRuleDefinition
except ImportError:  # Direct file loading used by the repository test suite.
    from canonical_validation_execution_core import (
        VALIDATION_RULE_FAILED,
        ValidationDataContext,
        ValidationExecutionDiagnostic,
        ValidationExecutionResult,
        ValidationOutcome,
        _diagnostic_sort_key,
        _record_identity,
        _record_sort_key,
        _resolve_primary_key,
        _resolve_table,
    )
    from canonical_validation_expr import (
        BinaryOperation,
        Call,
        Identifier,
        ListLiteral,
        Literal,
    )
    from canonical_validation_expr_eval import (
        ValidationExpressionEvaluationError,
        evaluate_validation_expression,
    )
    from canonical_validation_contiguous_order import (
        VALIDATION_CONTIGUOUS_EVALUATION_ERROR,
        VALIDATION_CONTIGUOUS_ORDER_FAILED,
        contiguous_ordering_capability_reason,
        execute_contiguous_ordering_rule,
    )
    from canonical_validation_rules import ValidationRuleDefinition


VALIDATION_CUSTOM_EXPRESSION_FAILED = "VALIDATION_CUSTOM_EXPRESSION_FAILED"
VALIDATION_CUSTOM_EXPRESSION_EVALUATION_ERROR = (
    "VALIDATION_CUSTOM_EXPRESSION_EVALUATION_ERROR"
)
VALIDATION_EXECUTOR_NOT_REGISTERED = "VALIDATION_EXECUTOR_NOT_REGISTERED"

_E2_BUILTINS = frozenset({"matches", "starts_with", "trim"})
_ALLOWED_BUILTINS = _E2_BUILTINS | frozenset({"when"})
_ALLOWED_BINARY_OPERATORS = frozenset({"==", "!=", "and", "in", "not in"})
_BUILTIN_ARITY = {"matches": 2, "starts_with": 2, "trim": 1, "when": 2}
_EXPECTED_CONTRACT = "E2 expression evaluates to exact boolean true"


def scalar_string_pattern_capability_reason(
    rule: ValidationRuleDefinition,
) -> str | None:
    """Return None only for the narrow E2 AST capability surface."""

    if not isinstance(rule, ValidationRuleDefinition):
        raise TypeError("rule must be a ValidationRuleDefinition")
    if rule.validation_kind_id != "custom_expression":
        return "validation_kind_not_custom_expression"
    if rule.rule_scope_id not in {"field", "record"}:
        return "rule_scope_not_row"
    if rule.target_field_id is None:
        return "target_field_missing"
    if rule.condition_ast is None or rule.condition_expression_source is None:
        return "condition_expression_missing"
    supported, uses_e2_builtin = _analyze_capability(rule.condition_ast)
    if not supported:
        return "expression_shape_not_supported"
    if not uses_e2_builtin:
        return "e2_builtin_not_used"
    return None


def execute_scalar_string_pattern_custom_expression_rule(
    rule: ValidationRuleDefinition,
    data: ValidationDataContext,
) -> ValidationExecutionResult:
    """Execute one row-scoped E2 expression without implicit applicability filters."""

    if not isinstance(rule, ValidationRuleDefinition):
        raise TypeError("rule must be a ValidationRuleDefinition")
    if not isinstance(data, ValidationDataContext):
        raise TypeError("data must be a ValidationDataContext")

    capability_reason = scalar_string_pattern_capability_reason(rule)
    if capability_reason is not None:
        return _single_result(
            rule,
            ValidationOutcome.NOT_EXECUTED,
            VALIDATION_EXECUTOR_NOT_REGISTERED,
            "The active custom expression is outside the E2 capability gate.",
            capability_reason,
        )

    namespace = data.namespace_for_component(rule.component_identity)
    if data.namespaces and namespace is None:
        return _single_result(
            rule,
            ValidationOutcome.FAIL,
            VALIDATION_RULE_FAILED,
            "The source component namespace binding is missing.",
            "source_namespace_missing",
        )
    target_records = _resolve_table(
        data, rule.target_table_id, namespace=namespace
    )
    if target_records is None:
        return _single_result(
            rule,
            ValidationOutcome.FAIL,
            VALIDATION_RULE_FAILED,
            "The target table is missing from the validation data context.",
            "target_table_missing",
        )

    primary_key = _resolve_primary_key(
        data, rule.target_table_id, namespace=namespace
    )
    diagnostics: list[ValidationExecutionDiagnostic] = []
    for record in sorted(
        target_records,
        key=lambda candidate: _record_sort_key(candidate, primary_key),
    ):
        identity = _record_identity(record, primary_key)
        try:
            result = evaluate_validation_expression(rule.condition_ast, record)
        except ValidationExpressionEvaluationError as error:
            diagnostics.append(
                ValidationExecutionDiagnostic(
                    VALIDATION_CUSTOM_EXPRESSION_EVALUATION_ERROR,
                    "The E2 custom expression could not be evaluated.",
                    rule.rule_id,
                    rule.target_table_id,
                    rule.target_field_id,
                    identity,
                    expected_contract=_EXPECTED_CONTRACT,
                    reason=_evaluation_error_reason(error),
                )
            )
            continue
        if type(result) is not bool:
            diagnostics.append(
                ValidationExecutionDiagnostic(
                    VALIDATION_CUSTOM_EXPRESSION_EVALUATION_ERROR,
                    "The E2 custom expression did not return an exact boolean.",
                    rule.rule_id,
                    rule.target_table_id,
                    rule.target_field_id,
                    identity,
                    expected_contract=_EXPECTED_CONTRACT,
                    reason="expression_result_not_boolean",
                )
            )
        elif not result:
            diagnostics.append(
                ValidationExecutionDiagnostic(
                    VALIDATION_CUSTOM_EXPRESSION_FAILED,
                    "The canonical record violates the E2 custom expression.",
                    rule.rule_id,
                    rule.target_table_id,
                    rule.target_field_id,
                    identity,
                    False,
                    _EXPECTED_CONTRACT,
                    "expression_evaluated_false",
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


def execute_supported_custom_expression_rule(
    rule: ValidationRuleDefinition,
    data: ValidationDataContext,
) -> ValidationExecutionResult:
    """Dispatch only E2 or exact H7 shapes; leave every other custom rule untouched."""

    if scalar_string_pattern_capability_reason(rule) is None:
        return execute_scalar_string_pattern_custom_expression_rule(rule, data)
    if contiguous_ordering_capability_reason(rule) is None:
        return execute_contiguous_ordering_rule(rule, data)
    return execute_scalar_string_pattern_custom_expression_rule(rule, data)


def _analyze_capability(node: object) -> tuple[bool, bool]:
    if isinstance(node, (Literal, Identifier)):
        return True, False
    if isinstance(node, ListLiteral):
        return _combine_capabilities(node.items)
    if isinstance(node, BinaryOperation):
        if node.operator not in _ALLOWED_BINARY_OPERATORS:
            return False, False
        return _combine_capabilities((node.left, node.right))
    if isinstance(node, Call):
        if (
            node.function not in _ALLOWED_BUILTINS
            or len(node.arguments) != _BUILTIN_ARITY[node.function]
        ):
            return False, False
        supported, uses_e2_builtin = _combine_capabilities(node.arguments)
        return supported, uses_e2_builtin or node.function in _E2_BUILTINS
    return False, False


def _combine_capabilities(nodes: tuple[object, ...]) -> tuple[bool, bool]:
    analyses = tuple(_analyze_capability(node) for node in nodes)
    return all(supported for supported, _ in analyses), any(
        uses_e2_builtin for _, uses_e2_builtin in analyses
    )


def _evaluation_error_reason(error: ValidationExpressionEvaluationError) -> str:
    details = ";".join(f"{key}={value}" for key, value in error.context)
    return f"expression_evaluation_error:{details}"


def _single_result(
    rule: ValidationRuleDefinition,
    outcome: ValidationOutcome,
    code: str,
    message: str,
    reason: str,
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
        0,
        0 if outcome is ValidationOutcome.NOT_EXECUTED else 1,
    )


__all__ = [
    "VALIDATION_CONTIGUOUS_EVALUATION_ERROR",
    "VALIDATION_CONTIGUOUS_ORDER_FAILED",
    "VALIDATION_CUSTOM_EXPRESSION_EVALUATION_ERROR",
    "VALIDATION_CUSTOM_EXPRESSION_FAILED",
    "contiguous_ordering_capability_reason",
    "execute_contiguous_ordering_rule",
    "execute_scalar_string_pattern_custom_expression_rule",
    "execute_supported_custom_expression_rule",
    "scalar_string_pattern_capability_reason",
]
