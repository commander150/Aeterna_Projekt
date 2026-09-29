"""Filesystem-independent canonical validation family execution."""

from __future__ import annotations

import math
from dataclasses import dataclass

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
        _is_logical_identifier,
        _record_identity,
        _record_sort_key,
        _resolve_field_schema,
        _resolve_primary_key,
        _resolve_table,
        _utf8,
        _valid_identity,
    )
    from .canonical_validation_expr import (
        BinaryOperation,
        Call,
        Identifier,
        ListLiteral,
        Literal,
    )
    from .canonical_validation_definition import (
        VALIDATION_DEFINITION_INVARIANT_FAILED,
        VALIDATION_DEFINITION_TARGET_RECORD_INVALID,
        VALIDATION_DEFINITION_TARGET_TABLE_MISSING,
        execute_definition_invariant_rule,
    )
    from .canonical_validation_contract_field import (
        VALIDATION_CONTRACT_FIELD_INVARIANT_FAILED,
        VALIDATION_CONTRACT_FIELD_TARGET_RECORD_INVALID,
        VALIDATION_CONTRACT_FIELD_TARGET_TABLE_MISSING,
        execute_contract_field_invariant_rule,
    )
    from .canonical_validation_custom_expression import (
        VALIDATION_CONTIGUOUS_EVALUATION_ERROR,
        VALIDATION_CONTIGUOUS_ORDER_FAILED,
        VALIDATION_CUSTOM_EXPRESSION_EVALUATION_ERROR,
        VALIDATION_CUSTOM_EXPRESSION_FAILED,
        contiguous_ordering_capability_reason,
        execute_contiguous_ordering_rule,
        execute_scalar_string_pattern_custom_expression_rule,
        execute_supported_custom_expression_rule,
        scalar_string_pattern_capability_reason,
    )
    from .canonical_validation_hierarchy import (
        VALIDATION_HIERARCHY_INTEGRITY_FAILED,
        VALIDATION_HIERARCHY_TARGET_RECORD_INVALID,
        VALIDATION_HIERARCHY_TARGET_TABLE_MISSING,
        execute_hierarchy_integrity_rule,
    )
    from .canonical_validation_qualified_reference import (
        VALIDATION_QUALIFIED_REFERENCE_INVARIANT_FAILED,
        VALIDATION_QUALIFIED_REFERENCE_RESOLUTION_INVALID,
        VALIDATION_QUALIFIED_REFERENCE_TARGET_RECORD_INVALID,
        VALIDATION_QUALIFIED_REFERENCE_TARGET_TABLE_MISSING,
        execute_qualified_reference_match_rule,
    )
    from .canonical_validation_normalized_uniqueness import (
        VALIDATION_NORMALIZED_UNIQUENESS_CONFLICT,
        VALIDATION_NORMALIZED_UNIQUENESS_EVALUATION_ERROR,
        execute_normalized_uniqueness_rule,
    )
    from .canonical_validation_reference_constraints import (
        VALIDATION_CROSS_FIELD_CONSISTENCY_FAILED,
        VALIDATION_REFERENCE_CONSTRAINT_EVALUATION_ERROR,
        VALIDATION_TARGET_GROUP_MEMBERSHIP_FAILED,
        execute_cross_field_consistency_rule,
        execute_target_group_membership_rule,
    )
    from .canonical_validation_rules import ValidationRuleDefinition
    from .canonical_validation_uniqueness import (
        VALIDATION_UNIQUENESS_DUPLICATE,
        VALIDATION_UNIQUENESS_TARGET_FIELD_MISSING,
        VALIDATION_UNIQUENESS_TARGET_RECORD_INVALID,
        VALIDATION_UNIQUENESS_TARGET_TABLE_MISSING,
        execute_uniqueness_rule,
    )
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
        _is_logical_identifier,
        _record_identity,
        _record_sort_key,
        _resolve_field_schema,
        _resolve_primary_key,
        _resolve_table,
        _utf8,
        _valid_identity,
    )
    from canonical_validation_expr import (
        BinaryOperation,
        Call,
        Identifier,
        ListLiteral,
        Literal,
    )
    from canonical_validation_definition import (
        VALIDATION_DEFINITION_INVARIANT_FAILED,
        VALIDATION_DEFINITION_TARGET_RECORD_INVALID,
        VALIDATION_DEFINITION_TARGET_TABLE_MISSING,
        execute_definition_invariant_rule,
    )
    from canonical_validation_contract_field import (
        VALIDATION_CONTRACT_FIELD_INVARIANT_FAILED,
        VALIDATION_CONTRACT_FIELD_TARGET_RECORD_INVALID,
        VALIDATION_CONTRACT_FIELD_TARGET_TABLE_MISSING,
        execute_contract_field_invariant_rule,
    )
    from canonical_validation_custom_expression import (
        VALIDATION_CONTIGUOUS_EVALUATION_ERROR,
        VALIDATION_CONTIGUOUS_ORDER_FAILED,
        VALIDATION_CUSTOM_EXPRESSION_EVALUATION_ERROR,
        VALIDATION_CUSTOM_EXPRESSION_FAILED,
        contiguous_ordering_capability_reason,
        execute_contiguous_ordering_rule,
        execute_scalar_string_pattern_custom_expression_rule,
        execute_supported_custom_expression_rule,
        scalar_string_pattern_capability_reason,
    )
    from canonical_validation_hierarchy import (
        VALIDATION_HIERARCHY_INTEGRITY_FAILED,
        VALIDATION_HIERARCHY_TARGET_RECORD_INVALID,
        VALIDATION_HIERARCHY_TARGET_TABLE_MISSING,
        execute_hierarchy_integrity_rule,
    )
    from canonical_validation_qualified_reference import (
        VALIDATION_QUALIFIED_REFERENCE_INVARIANT_FAILED,
        VALIDATION_QUALIFIED_REFERENCE_RESOLUTION_INVALID,
        VALIDATION_QUALIFIED_REFERENCE_TARGET_RECORD_INVALID,
        VALIDATION_QUALIFIED_REFERENCE_TARGET_TABLE_MISSING,
        execute_qualified_reference_match_rule,
    )
    from canonical_validation_normalized_uniqueness import (
        VALIDATION_NORMALIZED_UNIQUENESS_CONFLICT,
        VALIDATION_NORMALIZED_UNIQUENESS_EVALUATION_ERROR,
        execute_normalized_uniqueness_rule,
    )
    from canonical_validation_reference_constraints import (
        VALIDATION_CROSS_FIELD_CONSISTENCY_FAILED,
        VALIDATION_REFERENCE_CONSTRAINT_EVALUATION_ERROR,
        VALIDATION_TARGET_GROUP_MEMBERSHIP_FAILED,
        execute_cross_field_consistency_rule,
        execute_target_group_membership_rule,
    )
    from canonical_validation_rules import ValidationRuleDefinition
    from canonical_validation_uniqueness import (
        VALIDATION_UNIQUENESS_DUPLICATE,
        VALIDATION_UNIQUENESS_TARGET_FIELD_MISSING,
        VALIDATION_UNIQUENESS_TARGET_RECORD_INVALID,
        VALIDATION_UNIQUENESS_TARGET_TABLE_MISSING,
        execute_uniqueness_rule,
    )


VALIDATION_ALLOWED_VALUE_INVALID = "VALIDATION_ALLOWED_VALUE_INVALID"
VALIDATION_ALLOWED_VALUE_GROUP_MISSING = "VALIDATION_ALLOWED_VALUE_GROUP_MISSING"
VALIDATION_RANGE_INVALID = "VALIDATION_RANGE_INVALID"
VALIDATION_RANGE_VALUE_TYPE_INVALID = "VALIDATION_RANGE_VALUE_TYPE_INVALID"
VALIDATION_REFERENCE_TARGET_TABLE_MISSING = "VALIDATION_REFERENCE_TARGET_TABLE_MISSING"
VALIDATION_REFERENCE_TARGET_FIELD_MISSING = "VALIDATION_REFERENCE_TARGET_FIELD_MISSING"
VALIDATION_REFERENCE_TARGET_RECORD_INVALID = "VALIDATION_REFERENCE_TARGET_RECORD_INVALID"
VALIDATION_REFERENCE_TABLE_MISSING = "VALIDATION_REFERENCE_TABLE_MISSING"
VALIDATION_REFERENCE_FIELD_MISSING = "VALIDATION_REFERENCE_FIELD_MISSING"
VALIDATION_REFERENCE_VALUE_INVALID = "VALIDATION_REFERENCE_VALUE_INVALID"
VALIDATION_REFERENCE_MISSING = "VALIDATION_REFERENCE_MISSING"
VALIDATION_REFERENCE_AMBIGUOUS = "VALIDATION_REFERENCE_AMBIGUOUS"
VALIDATION_REFERENCE_GUARD_UNSUPPORTED = "VALIDATION_REFERENCE_GUARD_UNSUPPORTED"
VALIDATION_REFERENCE_NAMESPACE_INVALID = "VALIDATION_REFERENCE_NAMESPACE_INVALID"

_TABLE_IDENTITY_POLICY = "export_namespace_colon_table_id"
_EXTERNAL_IDENTIFIER_POLICY = "namespace_colon_identifier"


def execute_allowed_value_rule(
    rule: ValidationRuleDefinition,
    data: ValidationDataContext,
) -> ValidationExecutionResult:
    """Execute one typed structured allowed-value rule deterministically."""

    if not isinstance(rule, ValidationRuleDefinition):
        raise TypeError("rule must be a ValidationRuleDefinition")
    if not isinstance(data, ValidationDataContext):
        raise TypeError("data must be a ValidationDataContext")

    unsupported_reason = _unsupported_reason(rule)
    if unsupported_reason is not None:
        return _single_diagnostic_result(
            rule,
            ValidationOutcome.UNSUPPORTED,
            VALIDATION_EXECUTOR_UNSUPPORTED,
            "The rule contract is not supported by the allowed-value executor.",
            unsupported_reason,
            0,
        )

    source_namespace, namespace_reason = _resolve_local_namespace(
        data, rule.component_identity
    )
    if namespace_reason is not None:
        return _single_diagnostic_result(
            rule,
            ValidationOutcome.FAIL,
            VALIDATION_RULE_FAILED,
            "The source component namespace binding is missing.",
            namespace_reason,
            0,
        )

    field_schema = _resolve_field_schema(
        data,
        rule.target_table_id,
        field_id=rule.target_field_id,
        namespace=source_namespace,
    )
    if field_schema is None:
        return _single_diagnostic_result(
            rule,
            ValidationOutcome.FAIL,
            VALIDATION_RULE_FAILED,
            "The target field definition is missing, inactive, ambiguous, or mismatched.",
            "target_field_unresolved",
            0,
        )
    field_name = field_schema["field_name"]
    assert isinstance(field_name, str)

    target_records = _resolve_table(
        data, rule.target_table_id, namespace=source_namespace
    )
    if target_records is None:
        return _single_diagnostic_result(
            rule,
            ValidationOutcome.FAIL,
            VALIDATION_RULE_FAILED,
            "The target table is missing from the validation data context.",
            "target_table_missing",
            0,
        )

    group_id = rule.comparison_value
    assert isinstance(group_id, str)
    allowed_values = _resolve_active_group_values(
        group_id, data, namespace=source_namespace
    )
    if allowed_values is None:
        return _single_diagnostic_result(
            rule,
            ValidationOutcome.FAIL,
            VALIDATION_ALLOWED_VALUE_GROUP_MISSING,
            "The active allowed-value group could not be resolved.",
            "allowed_group_unresolved",
            0,
        )

    primary_key = _resolve_primary_key(
        data, rule.target_table_id, namespace=source_namespace
    )
    expected = f"active VALUE_REGISTRY.value_id in group {group_id}"
    diagnostics: list[ValidationExecutionDiagnostic] = []
    ordered_records = sorted(
        target_records,
        key=lambda record: _record_sort_key(record, primary_key),
    )
    for record in ordered_records:
        identity = _record_identity(record, primary_key)
        if field_name not in record:
            diagnostics.append(
                ValidationExecutionDiagnostic(
                    VALIDATION_RULE_FAILED,
                    "The target field is missing from the canonical record.",
                    rule.rule_id,
                    rule.target_table_id,
                    rule.target_field_id,
                    identity,
                    expected_contract=expected,
                    reason="target_field_missing",
                )
            )
            continue
        observed = record[field_name]
        if not isinstance(observed, str) or observed not in allowed_values:
            diagnostics.append(
                ValidationExecutionDiagnostic(
                    VALIDATION_ALLOWED_VALUE_INVALID,
                    "The target value is not an active canonical member of the allowed group.",
                    rule.rule_id,
                    rule.target_table_id,
                    rule.target_field_id,
                    identity,
                    observed,
                    expected,
                    "canonical_membership_failed",
                )
            )

    ordered_diagnostics = tuple(sorted(diagnostics, key=_diagnostic_sort_key))
    return ValidationExecutionResult(
        rule.rule_id,
        ValidationOutcome.FAIL if ordered_diagnostics else ValidationOutcome.PASS,
        ordered_diagnostics,
        len(target_records),
        len(ordered_diagnostics),
    )


def execute_range_rule(
    rule: ValidationRuleDefinition,
    data: ValidationDataContext,
) -> ValidationExecutionResult:
    """Execute one typed lower-bounded integer range rule deterministically."""

    if not isinstance(rule, ValidationRuleDefinition):
        raise TypeError("rule must be a ValidationRuleDefinition")
    if not isinstance(data, ValidationDataContext):
        raise TypeError("data must be a ValidationDataContext")

    unsupported_reason, boundary = _range_contract(rule)
    if unsupported_reason is not None or boundary is None:
        return _range_single_diagnostic_result(
            rule,
            ValidationOutcome.UNSUPPORTED,
            VALIDATION_EXECUTOR_UNSUPPORTED,
            "The rule contract is not supported by the range executor.",
            unsupported_reason or "range_boundary_invalid",
            0,
            None,
        )

    source_namespace, namespace_reason = _resolve_local_namespace(
        data, rule.component_identity
    )
    if namespace_reason is not None:
        return _range_single_diagnostic_result(
            rule,
            ValidationOutcome.FAIL,
            VALIDATION_RULE_FAILED,
            "The source component namespace binding is missing.",
            namespace_reason,
            0,
            boundary,
        )

    field_schema = _resolve_field_schema(
        data,
        rule.target_table_id,
        field_id=rule.target_field_id,
        namespace=source_namespace,
    )
    if field_schema is None:
        return _range_single_diagnostic_result(
            rule,
            ValidationOutcome.FAIL,
            VALIDATION_RULE_FAILED,
            "The target field definition is missing, inactive, ambiguous, or mismatched.",
            "target_field_unresolved",
            0,
            boundary,
        )
    if not _is_required_integer_field(field_schema):
        return _range_single_diagnostic_result(
            rule,
            ValidationOutcome.UNSUPPORTED,
            VALIDATION_EXECUTOR_UNSUPPORTED,
            "The target schema is not the supported required-integer contract.",
            "target_schema_not_required_integer",
            0,
            boundary,
        )

    target_records = _resolve_table(
        data, rule.target_table_id, namespace=source_namespace
    )
    if target_records is None:
        return _range_single_diagnostic_result(
            rule,
            ValidationOutcome.FAIL,
            VALIDATION_RULE_FAILED,
            "The target table is missing from the validation data context.",
            "target_table_missing",
            0,
            boundary,
        )

    field_name = field_schema["field_name"]
    assert isinstance(field_name, str)
    primary_key = _resolve_primary_key(
        data, rule.target_table_id, namespace=source_namespace
    )
    expected = f"canonical integer value >= {boundary}"
    diagnostics: list[ValidationExecutionDiagnostic] = []
    ordered_records = sorted(
        target_records,
        key=lambda record: _record_sort_key(record, primary_key),
    )
    for record in ordered_records:
        identity = _record_identity(record, primary_key)
        if field_name not in record:
            diagnostics.append(
                ValidationExecutionDiagnostic(
                    VALIDATION_RULE_FAILED,
                    "The target field is missing from the canonical record.",
                    rule.rule_id,
                    rule.target_table_id,
                    rule.target_field_id,
                    identity,
                    expected_contract=expected,
                    reason="target_field_missing",
                )
            )
            continue
        observed = record[field_name]
        if type(observed) is not int:
            diagnostics.append(
                ValidationExecutionDiagnostic(
                    VALIDATION_RANGE_VALUE_TYPE_INVALID,
                    "The target value is not a canonical integer.",
                    rule.rule_id,
                    rule.target_table_id,
                    rule.target_field_id,
                    identity,
                    observed,
                    expected,
                    "target_value_not_integer",
                )
            )
            continue
        if observed < boundary:
            diagnostics.append(
                ValidationExecutionDiagnostic(
                    VALIDATION_RANGE_INVALID,
                    "The target value is below the inclusive lower boundary.",
                    rule.rule_id,
                    rule.target_table_id,
                    rule.target_field_id,
                    identity,
                    observed,
                    expected,
                    "lower_boundary_failed",
                )
            )

    ordered_diagnostics = tuple(sorted(diagnostics, key=_diagnostic_sort_key))
    return ValidationExecutionResult(
        rule.rule_id,
        ValidationOutcome.FAIL if ordered_diagnostics else ValidationOutcome.PASS,
        ordered_diagnostics,
        len(target_records),
        len(ordered_diagnostics),
    )


@dataclass(frozen=True, slots=True)
class ReferenceGuardEvaluator:
    """The deliberately small predicate evaluator for current reference guards."""
    target_identifier: str
    def __post_init__(self) -> None:
        if not isinstance(self.target_identifier, str) or not self.target_identifier:
            raise ValueError("The guard target identifier must be a non-empty string.")

    def unsupported_reason(self, node: object) -> str | None:
        return _guard_reason(node, self.target_identifier)

    def evaluate(self, node: object, record: FrozenRecord) -> bool:
        reason = self.unsupported_reason(node)
        if reason:
            raise ValueError(reason)
        result = _guard_value(node, record, self.target_identifier)
        if type(result) is not bool:
            raise ValueError("guard_result_not_boolean")
        return result

@dataclass(frozen=True, slots=True)
class _ReferenceDomain:
    namespace: str
    table_id: str
    field_id: str | None
    field_name: str

def execute_reference_integrity_rule(
    rule: ValidationRuleDefinition, data: ValidationDataContext
) -> ValidationExecutionResult:
    """Execute current direct and guarded exact-reference contracts."""
    if not isinstance(rule, ValidationRuleDefinition):
        raise TypeError("rule must be a ValidationRuleDefinition")
    if not isinstance(data, ValidationDataContext):
        raise TypeError("data must be a ValidationDataContext")
    reason = _reference_contract_reason(rule)
    if reason:
        return _reference_result(rule, ValidationOutcome.UNSUPPORTED,
                                 VALIDATION_REFERENCE_GUARD_UNSUPPORTED, reason)
    source = data.namespace_for_component(rule.component_identity)
    if source is None:
        return _reference_result(rule, ValidationOutcome.FAIL,
                                 VALIDATION_REFERENCE_NAMESPACE_INVALID,
                                 "source_namespace_missing")
    target, error = _target_contract(rule, data, source)
    if error:
        return _reference_result(rule, ValidationOutcome.FAIL, *error)
    assert target is not None
    target_field, target_pk, target_records = target
    domain, error = _declared_reference_domain(rule, data, source)
    if error:
        return _reference_result(rule, ValidationOutcome.FAIL, *error)
    assert domain is not None
    guard, reason = _reference_guard(rule, target_field, domain.field_name)
    if reason:
        return _reference_result(rule, ValidationOutcome.UNSUPPORTED,
                                 VALIDATION_REFERENCE_GUARD_UNSUPPORTED, reason)
    base_index, errors = _reference_index(rule, data, domain)
    if errors:
        return ValidationExecutionResult(
            rule.rule_id, ValidationOutcome.FAIL,
            tuple(sorted(errors, key=_diagnostic_sort_key)), 0, len(errors))
    assert base_index is not None
    cache = {_domain_key(domain): base_index}
    diagnostics: list[ValidationExecutionDiagnostic] = []
    evaluated = 0
    for record in sorted(target_records,
                         key=lambda item: _record_sort_key(item, target_pk)):
        identity = _record_identity(record, target_pk)
        expected = _reference_expected(domain)
        if not _valid_identity(record, target_pk):
            diagnostics.append(_reference_diagnostic(
                rule, VALIDATION_REFERENCE_TARGET_RECORD_INVALID,
                "target_primary_key_invalid", identity, None, expected))
            continue
        if target_field not in record:
            diagnostics.append(_reference_diagnostic(
                rule, VALIDATION_REFERENCE_TARGET_RECORD_INVALID,
                "target_field_missing", identity, None, expected))
            continue
        observed = record[target_field]
        if observed is not None and (not isinstance(observed, str) or not observed):
            diagnostics.append(_reference_diagnostic(
                rule, VALIDATION_REFERENCE_TARGET_RECORD_INVALID,
                "target_value_invalid", identity, observed, expected))
            continue
        if guard is None and observed is None:
            diagnostics.append(_reference_diagnostic(
                rule, VALIDATION_REFERENCE_TARGET_RECORD_INVALID,
                "target_value_null", identity, observed, expected))
            continue
        if guard is not None and not guard.evaluate(
            rule.condition_ast.arguments[0], record
        ):
            continue
        assert isinstance(observed, str)
        evaluated += 1
        candidate, value, reason = _reference_candidate(data, source, domain, observed)
        if candidate is None:
            diagnostics.append(_reference_diagnostic(
                rule, VALIDATION_REFERENCE_NAMESPACE_INVALID,
                reason or "qualified_namespace_invalid",
                identity, observed, expected))
            continue
        key = _domain_key(candidate)
        if key not in cache:
            cache[key], new_errors = _reference_index(rule, data, candidate)
            diagnostics.extend(new_errors)
        index = cache[key]
        if index is None:
            continue
        matches = _index_matches(index, value)
        expected = _reference_expected(candidate)
        if not matches:
            diagnostics.append(_reference_diagnostic(
                rule, VALIDATION_REFERENCE_MISSING, "reference_missing",
                identity, observed, expected))
        elif len(matches) > 1:
            diagnostics.append(_reference_diagnostic(
                rule, VALIDATION_REFERENCE_AMBIGUOUS, "reference_ambiguous",
                identity, observed, expected, matches))
    ordered = tuple(sorted(diagnostics, key=_diagnostic_sort_key))
    return ValidationExecutionResult(
        rule.rule_id, ValidationOutcome.FAIL if ordered else ValidationOutcome.PASS,
        ordered, evaluated, len(ordered))

def _reference_contract_reason(rule: ValidationRuleDefinition) -> str | None:
    if rule.validation_kind_id != "reference_integrity":
        return "validation_kind_not_reference_integrity"
    if rule.rule_scope_id not in {"field", "cross_table"}:
        return "rule_scope_not_supported"
    if rule.target_field_id is None:
        return "target_field_missing"
    if rule.reference_table_id is None or rule.reference_field_id is None:
        return "reference_contract_missing"
    if any(value is not None for value in (
        rule.operator_id, rule.comparison_value,
        rule.minimum_value, rule.maximum_value,
    )):
        return "structured_shape_not_supported"
    if (rule.condition_expression_source is None) != (rule.condition_ast is None):
        return "condition_source_ast_mismatch"
    return None

def _target_contract(rule, data, namespace):
    schema = _resolve_field_schema(
        data,
        rule.target_table_id,
        field_id=rule.target_field_id,
        namespace=namespace,
        allow_empty_resolved_name=True,
    )
    if schema is None:
        return None, (VALIDATION_REFERENCE_TARGET_FIELD_MISSING,
                      "target_field_schema_unresolved")
    expected = (("conditional", True, "explicit_null")
                if rule.condition_ast is not None
                else ("always", False, "forbidden"))
    actual = (schema.get("required_mode"), schema.get("nullable"),
              schema.get("null_handling"))
    if schema.get("data_type") != "string" or actual != expected:
        return None, (VALIDATION_REFERENCE_TARGET_FIELD_MISSING,
                      "target_field_schema_invalid")
    primary_key = _resolve_primary_key(
        data, rule.target_table_id, namespace=namespace
    )
    if primary_key is None:
        return None, (VALIDATION_REFERENCE_TARGET_TABLE_MISSING,
                      "target_table_schema_unresolved")
    records = _resolve_table(data, rule.target_table_id, namespace=namespace)
    if records is None:
        return None, (VALIDATION_REFERENCE_TARGET_TABLE_MISSING,
                      "target_table_missing")
    return (schema["field_name"], primary_key, records), None

def _declared_reference_domain(rule, data, source):
    assert rule.reference_table_id and rule.reference_field_id
    namespace, table_id, reason = _declared_identifier(
        rule.reference_table_id, source, source, data)
    if reason:
        return None, (VALIDATION_REFERENCE_NAMESPACE_INVALID, reason)
    field_namespace, field_id, reason = _declared_identifier(
        rule.reference_field_id, namespace, source, data)
    if reason or field_namespace != namespace:
        return None, (VALIDATION_REFERENCE_NAMESPACE_INVALID,
                      reason or "reference_table_field_namespace_mismatch")
    schema = _resolve_field_schema(
        data,
        table_id,
        field_id=field_id,
        namespace=namespace,
        allow_empty_resolved_name=True,
    )
    if schema is None:
        return None, (VALIDATION_REFERENCE_FIELD_MISSING,
                      "reference_field_schema_unresolved")
    return _ReferenceDomain(
        namespace, table_id, field_id, schema["field_name"]), None

def _declared_identifier(value, default_namespace, policy_namespace, data):
    if ":" not in value:
        return ((default_namespace, value, None) if _is_logical_identifier(value)
                else (None, None, "declared_identifier_malformed"))
    if data.namespace_policy(
        policy_namespace, "external_reference_identifier_policy"
    ) != _EXTERNAL_IDENTIFIER_POLICY:
        return None, None, "qualified_identifier_policy_missing"
    parsed = _split_qualified_identifier(value)
    if parsed is None:
        return None, None, "qualified_identifier_malformed"
    if not data.has_namespace(parsed[0]):
        return None, None, "qualified_namespace_unknown"
    return parsed[0], parsed[1], None

def _reference_guard(rule, target_field, reference_field):
    if rule.condition_ast is None:
        return None, None
    node = rule.condition_ast
    if not isinstance(node, Call) or node.function != "when":
        return None, "top_level_not_when"
    if len(node.arguments) != 2:
        return None, "when_arity_invalid"
    predicate, consequent = node.arguments
    if not isinstance(consequent, Call) or consequent.function != "exists":
        return None, "when_consequent_not_exists"
    if len(consequent.arguments) != 3:
        return None, "exists_arity_invalid"
    table, field, value = consequent.arguments
    if not _string_literal_is(table, rule.reference_table_id):
        return None, "exists_table_contract_mismatch"
    if not _string_literal_is(field, reference_field):
        return None, "exists_field_contract_mismatch"
    if not _identifier_is(value, target_field):
        return None, "exists_target_identifier_mismatch"
    if rule.free_identifiers != (target_field,) or rule.local_bindings:
        return None, "guard_symbol_contract_mismatch"
    evaluator = ReferenceGuardEvaluator(target_field)
    reason = evaluator.unsupported_reason(predicate)
    return (None, reason) if reason else (evaluator, None)

def _guard_reason(node, identifier):
    if _not_null_guard(node, identifier) or _legacy_guard(node, identifier):
        return None
    if (isinstance(node, BinaryOperation) and node.operator == "and"
            and _not_null_guard(node.left, identifier)
            and _starts_with_guard(node.right, identifier)):
        return None
    return "guard_predicate_shape_not_supported"

def _guard_value(node, record, identifier):
    if isinstance(node, BinaryOperation):
        if node.operator == "and":
            return bool(_guard_value(node.left, record, identifier)) and bool(
                _guard_value(node.right, record, identifier))
        value = record[identifier]
        if node.operator == "!=":
            return value is not None
        return value not in tuple(item.value for item in node.right.items)
    value, prefix = record[identifier], node.arguments[1]
    return value.startswith(prefix.value)

def _not_null_guard(node, identifier):
    return (isinstance(node, BinaryOperation) and node.operator == "!="
            and _identifier_is(node.left, identifier)
            and isinstance(node.right, Literal)
            and node.right.literal_kind == "null" and node.right.value is None)

def _legacy_guard(node, identifier):
    return (isinstance(node, BinaryOperation) and node.operator == "not in"
            and _identifier_is(node.left, identifier)
            and isinstance(node.right, ListLiteral)
            and tuple(item.value for item in node.right.items) == (None, "#TBD")
            and all(_guard_literal(item) for item in node.right.items))

def _starts_with_guard(node, identifier):
    return (isinstance(node, Call) and node.function == "starts_with"
            and len(node.arguments) == 2
            and _identifier_is(node.arguments[0], identifier)
            and _string_literal_is(node.arguments[1], "chg_"))

def _identifier_is(node, expected):
    return isinstance(node, Identifier) and node.name == expected

def _string_literal_is(node, expected):
    return (isinstance(node, Literal) and node.literal_kind == "string"
            and node.value == expected)

def _guard_literal(node):
    return isinstance(node, Literal) and (
        (node.literal_kind == "null" and node.value is None)
        or (node.literal_kind == "string" and isinstance(node.value, str)))

def _reference_candidate(data, source, base, observed):
    identity_domain = (
        base.table_id == "schema_tables" and base.field_name == "table_id"
        and data.namespace_policy(source, "table_identity_policy")
        == _TABLE_IDENTITY_POLICY)
    if not identity_domain or ":" not in observed:
        return base, observed, None
    if data.namespace_policy(
        source, "external_reference_identifier_policy"
    ) != _EXTERNAL_IDENTIFIER_POLICY:
        return None, observed, "qualified_identifier_policy_missing"
    parsed = _split_qualified_identifier(observed)
    if parsed is None:
        return None, observed, "qualified_identifier_malformed"
    namespace, identifier = parsed
    if not data.has_namespace(namespace):
        return None, observed, "qualified_namespace_unknown"
    if data.namespace_policy(
        namespace, "table_identity_policy"
    ) != _TABLE_IDENTITY_POLICY:
        return None, observed, "qualified_table_identity_policy_missing"
    return _ReferenceDomain(
        namespace, base.table_id, None, base.field_name), identifier, None

def _split_qualified_identifier(value):
    parts = value.split(":")
    return (parts[0], parts[1]) if (
        len(parts) == 2 and all(_is_logical_identifier(part) for part in parts)
    ) else None

def _reference_index(rule, data, domain):
    table_name = f"{domain.namespace}:{domain.table_id}"
    expected = _reference_expected(domain)
    records = _resolve_table(data, domain.table_id, namespace=domain.namespace)
    if records is None:
        return None, (_reference_diagnostic(
            rule, VALIDATION_REFERENCE_TABLE_MISSING, "reference_table_missing",
            None, None, expected, table_id=table_name,
            field_id=domain.field_id),)
    schema = _resolve_field_schema(
        data,
        domain.table_id,
        field_id=domain.field_id,
        field_name=None if domain.field_id else domain.field_name,
        namespace=domain.namespace,
        allow_empty_resolved_name=True,
    )
    required = ("string", "always", False, "forbidden")
    actual = None if schema is None else (
        schema.get("data_type"), schema.get("required_mode"),
        schema.get("nullable"), schema.get("null_handling"))
    if actual != required:
        return None, (_reference_diagnostic(
            rule, VALIDATION_REFERENCE_FIELD_MISSING,
            "reference_field_schema_unresolved", None, None, expected,
            table_id=table_name, field_id=domain.field_id),)
    field_name = schema["field_name"]
    primary_key = _resolve_primary_key(
        data, domain.table_id, namespace=domain.namespace
    )
    if primary_key != field_name:
        return None, (_reference_diagnostic(
            rule, VALIDATION_REFERENCE_FIELD_MISSING,
            "reference_field_not_primary_key", None, None, expected,
            table_id=table_name, field_id=domain.field_id),)
    values, diagnostics = {}, []
    for record in sorted(records, key=lambda item: _record_sort_key(item, primary_key)):
        identity, value = _record_identity(record, primary_key), record.get(field_name)
        if field_name not in record or not isinstance(value, str) or not value:
            diagnostics.append(_reference_diagnostic(
                rule, VALIDATION_REFERENCE_VALUE_INVALID,
                "reference_record_key_invalid", identity, value, expected,
                table_id=table_name, field_id=domain.field_id))
        else:
            values.setdefault(value, []).append(identity)
    for value, identities in values.items():
        if len(identities) > 1:
            related = tuple(sorted(identities, key=_utf8))
            diagnostics.append(_reference_diagnostic(
                rule, VALIDATION_REFERENCE_AMBIGUOUS,
                "reference_key_duplicated", related[0], value, expected,
                related, table_name, domain.field_id))
    if diagnostics:
        return None, tuple(sorted(diagnostics, key=_diagnostic_sort_key))
    return tuple(
        (value, tuple(sorted(ids, key=_utf8)))
        for value, ids in sorted(values.items(), key=lambda item: _utf8(item[0]))
    ), ()

def _index_matches(index, value):
    return next((ids for candidate, ids in index if candidate == value), ())

def _reference_expected(domain):
    return ("one exact canonical string match in "
            f"{domain.namespace}:{domain.table_id}.{domain.field_name}")

def _domain_key(domain):
    return domain.namespace, domain.table_id, domain.field_name

def _reference_diagnostic(
    rule, code, reason, identity, observed, expected, related=(),
    table_id=None, field_id=None,
):
    return ValidationExecutionDiagnostic(
        code, "Reference integrity validation failed.", rule.rule_id,
        table_id or rule.target_table_id,
        field_id if table_id is not None else rule.target_field_id,
        identity, observed, expected, reason, related)

def _reference_result(rule, outcome, code, reason):
    diagnostic = _reference_diagnostic(
        rule, code, reason, None, None, "unique exact canonical reference")
    return ValidationExecutionResult(
        rule.rule_id, outcome, (diagnostic,), 0,
        0 if outcome is ValidationOutcome.UNSUPPORTED else 1)


def _unsupported_reason(rule: ValidationRuleDefinition) -> str | None:
    if rule.validation_kind_id != "allowed_value":
        return "validation_kind_not_allowed_value"
    if rule.rule_scope_id != "field":
        return "rule_scope_not_field"
    if rule.operator_id != "op_in":
        return "operator_not_op_in"
    if rule.target_field_id is None:
        return "target_field_missing"
    if not isinstance(rule.comparison_value, str) or not rule.comparison_value:
        return "comparison_group_invalid"
    if any(
        value is not None
        for value in (
            rule.condition_expression_source,
            rule.condition_ast,
            rule.minimum_value,
            rule.maximum_value,
            rule.reference_table_id,
            rule.reference_field_id,
        )
    ):
        return "structured_shape_not_supported"
    return None


def _range_contract(
    rule: ValidationRuleDefinition,
) -> tuple[str | None, int | None]:
    if rule.validation_kind_id != "range":
        return "validation_kind_not_range", None
    if rule.rule_scope_id != "field":
        return "rule_scope_not_field", None
    if rule.operator_id != "op_greater_than_or_equal":
        return "operator_not_greater_than_or_equal", None
    if rule.target_field_id is None:
        return "target_field_missing", None
    if any(
        value is not None
        for value in (
            rule.condition_expression_source,
            rule.condition_ast,
            rule.maximum_value,
            rule.reference_table_id,
            rule.reference_field_id,
        )
    ):
        return "structured_shape_not_supported", None
    comparison = _canonical_integer_literal(rule.comparison_value)
    minimum = _canonical_integer_literal(rule.minimum_value)
    if comparison is None or minimum is None:
        return "integer_boundary_invalid", None
    if comparison != minimum:
        return "comparison_minimum_mismatch", None
    return None, comparison


def _canonical_integer_literal(value: object) -> int | None:
    if type(value) is int:
        return value
    if type(value) is float and math.isfinite(value) and value.is_integer():
        return int(value)
    return None


def _is_required_integer_field(field_schema: FrozenRecord) -> bool:
    return (
        field_schema.get("data_type") == "integer"
        and field_schema.get("required_mode") == "always"
        and field_schema.get("nullable") is False
        and field_schema.get("null_handling") == "forbidden"
    )


def _resolve_local_namespace(
    data: ValidationDataContext,
    component_identity: str | None,
) -> tuple[str | None, str | None]:
    """Resolve explicit component provenance, retaining legacy context support."""

    namespace = data.namespace_for_component(component_identity)
    if namespace is not None:
        return namespace, None
    if not data.namespaces:
        return None, None
    return None, "source_namespace_missing"


def _resolve_active_group_values(
    group_id: str,
    data: ValidationDataContext,
    *,
    namespace: str | None = None,
) -> frozenset[str] | None:
    groups = _resolve_table(data, "value_groups", namespace=namespace)
    registry = _resolve_table(data, "value_registry", namespace=namespace)
    if groups is None or registry is None:
        return None
    matching_groups = [
        record
        for record in groups
        if record.get("group_id") == group_id and record.get("status") == "active"
    ]
    if len(matching_groups) != 1:
        return None
    values: set[str] = set()
    for record in registry:
        if record.get("group_id") != group_id:
            continue
        if record.get("lifecycle_status") != "active":
            continue
        value_id = record.get("value_id")
        if not isinstance(value_id, str) or not value_id:
            return None
        values.add(value_id)
    return frozenset(values)


def _single_diagnostic_result(
    rule: ValidationRuleDefinition,
    outcome: ValidationOutcome,
    code: str,
    message: str,
    reason: str,
    evaluated_record_count: int,
) -> ValidationExecutionResult:
    diagnostic = ValidationExecutionDiagnostic(
        code,
        message,
        rule.rule_id,
        rule.target_table_id,
        rule.target_field_id,
        expected_contract=(
            f"active VALUE_REGISTRY.value_id in group {rule.comparison_value}"
            if isinstance(rule.comparison_value, str)
            else "structured allowed_value contract"
        ),
        reason=reason,
    )
    return ValidationExecutionResult(
        rule.rule_id,
        outcome,
        (diagnostic,),
        evaluated_record_count,
        0 if outcome is ValidationOutcome.UNSUPPORTED else 1,
    )


def _range_single_diagnostic_result(
    rule: ValidationRuleDefinition,
    outcome: ValidationOutcome,
    code: str,
    message: str,
    reason: str,
    evaluated_record_count: int,
    boundary: int | None,
) -> ValidationExecutionResult:
    diagnostic = ValidationExecutionDiagnostic(
        code,
        message,
        rule.rule_id,
        rule.target_table_id,
        rule.target_field_id,
        expected_contract=(
            f"canonical integer value >= {boundary}"
            if boundary is not None
            else "structured lower-bounded integer range contract"
        ),
        reason=reason,
    )
    return ValidationExecutionResult(
        rule.rule_id,
        outcome,
        (diagnostic,),
        evaluated_record_count,
        0 if outcome is ValidationOutcome.UNSUPPORTED else 1,
    )

__all__ = [
    "VALIDATION_ALLOWED_VALUE_GROUP_MISSING",
    "VALIDATION_ALLOWED_VALUE_INVALID",
    "VALIDATION_CONTRACT_FIELD_INVARIANT_FAILED",
    "VALIDATION_CONTRACT_FIELD_TARGET_RECORD_INVALID",
    "VALIDATION_CONTRACT_FIELD_TARGET_TABLE_MISSING",
    "VALIDATION_CONTIGUOUS_EVALUATION_ERROR",
    "VALIDATION_CONTIGUOUS_ORDER_FAILED",
    "VALIDATION_DEFINITION_INVARIANT_FAILED",
    "VALIDATION_DEFINITION_TARGET_RECORD_INVALID",
    "VALIDATION_DEFINITION_TARGET_TABLE_MISSING",
    "VALIDATION_CUSTOM_EXPRESSION_EVALUATION_ERROR",
    "VALIDATION_CUSTOM_EXPRESSION_FAILED",
    "VALIDATION_EXECUTOR_UNSUPPORTED",
    "VALIDATION_HIERARCHY_INTEGRITY_FAILED",
    "VALIDATION_HIERARCHY_TARGET_RECORD_INVALID",
    "VALIDATION_HIERARCHY_TARGET_TABLE_MISSING",
    "VALIDATION_NORMALIZED_UNIQUENESS_CONFLICT",
    "VALIDATION_NORMALIZED_UNIQUENESS_EVALUATION_ERROR",
    "VALIDATION_CROSS_FIELD_CONSISTENCY_FAILED",
    "VALIDATION_REFERENCE_CONSTRAINT_EVALUATION_ERROR",
    "VALIDATION_TARGET_GROUP_MEMBERSHIP_FAILED",
    "VALIDATION_RANGE_INVALID",
    "VALIDATION_RANGE_VALUE_TYPE_INVALID",
    "VALIDATION_QUALIFIED_REFERENCE_INVARIANT_FAILED",
    "VALIDATION_QUALIFIED_REFERENCE_RESOLUTION_INVALID",
    "VALIDATION_QUALIFIED_REFERENCE_TARGET_RECORD_INVALID",
    "VALIDATION_QUALIFIED_REFERENCE_TARGET_TABLE_MISSING",
    "VALIDATION_REFERENCE_AMBIGUOUS",
    "VALIDATION_REFERENCE_FIELD_MISSING",
    "VALIDATION_REFERENCE_GUARD_UNSUPPORTED",
    "VALIDATION_REFERENCE_MISSING",
    "VALIDATION_REFERENCE_NAMESPACE_INVALID",
    "VALIDATION_REFERENCE_TABLE_MISSING",
    "VALIDATION_REFERENCE_TARGET_FIELD_MISSING",
    "VALIDATION_REFERENCE_TARGET_RECORD_INVALID",
    "VALIDATION_REFERENCE_TARGET_TABLE_MISSING",
    "VALIDATION_REFERENCE_VALUE_INVALID",
    "VALIDATION_RULE_FAILED",
    "VALIDATION_UNIQUENESS_DUPLICATE",
    "VALIDATION_UNIQUENESS_TARGET_FIELD_MISSING",
    "VALIDATION_UNIQUENESS_TARGET_RECORD_INVALID",
    "VALIDATION_UNIQUENESS_TARGET_TABLE_MISSING",
    "ReferenceGuardEvaluator",
    "ValidationDataContext",
    "ValidationExecutionDiagnostic",
    "ValidationExecutionResult",
    "ValidationOutcome",
    "execute_allowed_value_rule",
    "contiguous_ordering_capability_reason",
    "execute_contract_field_invariant_rule",
    "execute_contiguous_ordering_rule",
    "execute_scalar_string_pattern_custom_expression_rule",
    "execute_supported_custom_expression_rule",
    "execute_definition_invariant_rule",
    "execute_hierarchy_integrity_rule",
    "execute_normalized_uniqueness_rule",
    "execute_cross_field_consistency_rule",
    "execute_target_group_membership_rule",
    "execute_qualified_reference_match_rule",
    "execute_range_rule",
    "execute_reference_integrity_rule",
    "execute_uniqueness_rule",
    "scalar_string_pattern_capability_reason",
]
