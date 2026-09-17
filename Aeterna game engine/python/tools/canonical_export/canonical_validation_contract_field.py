"""Execution for canonical CONTRACT_FIELDS definition invariants."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

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
    from .canonical_validation_expr import (
        ValidationExpressionError,
        parse_validation_expression,
        semantic_ast_hash,
    )
    from .canonical_validation_expr_eval import (
        ValidationExpressionEvaluationError,
        ValidationExpressionUnsupportedError,
        evaluate_validation_expression,
    )
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
    from canonical_validation_expr import (
        ValidationExpressionError,
        parse_validation_expression,
        semantic_ast_hash,
    )
    from canonical_validation_expr_eval import (
        ValidationExpressionEvaluationError,
        ValidationExpressionUnsupportedError,
        evaluate_validation_expression,
    )
    from canonical_validation_rules import ValidationRuleDefinition


VALIDATION_CONTRACT_FIELD_INVARIANT_FAILED = (
    "VALIDATION_CONTRACT_FIELD_INVARIANT_FAILED"
)
VALIDATION_CONTRACT_FIELD_TARGET_RECORD_INVALID = (
    "VALIDATION_CONTRACT_FIELD_TARGET_RECORD_INVALID"
)
VALIDATION_CONTRACT_FIELD_TARGET_TABLE_MISSING = (
    "VALIDATION_CONTRACT_FIELD_TARGET_TABLE_MISSING"
)

_CONTRACT_FIELDS_TABLE = "contract_fields"


@dataclass(frozen=True, slots=True)
class _ContractShape:
    name: str
    guard_field: str
    field_roles: tuple[tuple[str, str], ...]

    @property
    def identifiers(self) -> tuple[str, ...]:
        return tuple(field for field, _role in self.field_roles)


_SUPPORTED_SHAPES = (
    (
        parse_validation_expression(
            'when(required_mode == "always", nullable == false and '
            'null_handling == "forbidden")'
        ),
        _ContractShape(
            "always_required",
            "required_mode",
            (
                ("required_mode", "required_string"),
                ("nullable", "required_boolean"),
                ("null_handling", "required_string"),
            ),
        ),
    ),
    (
        parse_validation_expression(
            'when(is_collection == true, (min_items == null or min_items >= 0) '
            'and (max_items == null or (min_items == null or '
            'max_items >= min_items)))'
        ),
        _ContractShape(
            "collection_bounds",
            "is_collection",
            (
                ("is_collection", "required_boolean"),
                ("min_items", "nullable_integer"),
                ("max_items", "nullable_integer"),
            ),
        ),
    ),
    (
        parse_validation_expression(
            "when(is_collection == false, min_items == null and "
            "max_items == null)"
        ),
        _ContractShape(
            "scalar_bounds",
            "is_collection",
            (
                ("is_collection", "required_boolean"),
                ("min_items", "nullable_integer"),
                ("max_items", "nullable_integer"),
            ),
        ),
    ),
)


def execute_contract_field_invariant_rule(
    rule: ValidationRuleDefinition,
    data: ValidationDataContext,
) -> ValidationExecutionResult:
    """Execute one supported static CONTRACT_FIELDS row invariant."""

    if not isinstance(rule, ValidationRuleDefinition):
        raise TypeError("rule must be a ValidationRuleDefinition")
    if not isinstance(data, ValidationDataContext):
        raise TypeError("data must be a ValidationDataContext")

    shape, reason = _contract_field_shape(rule)
    if reason is not None or shape is None:
        return _single_result(
            rule,
            ValidationOutcome.UNSUPPORTED,
            VALIDATION_EXECUTOR_UNSUPPORTED,
            reason or "contract_field_expression_invalid",
            None,
        )

    namespace = data.namespace_for_component(rule.component_identity)
    if namespace is None:
        return _single_result(
            rule,
            ValidationOutcome.FAIL,
            VALIDATION_CONTRACT_FIELD_TARGET_TABLE_MISSING,
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
            VALIDATION_CONTRACT_FIELD_TARGET_TABLE_MISSING,
            "target_table_schema_unresolved",
            namespace,
        )

    field_contracts: list[tuple[str, FrozenRecord]] = []
    for field_name, role in shape.field_roles:
        field_schema = _resolve_field_schema(
            data,
            rule.target_table_id,
            field_name=field_name,
            namespace=namespace,
        )
        if field_schema is None:
            return _single_result(
                rule,
                ValidationOutcome.FAIL,
                VALIDATION_CONTRACT_FIELD_TARGET_RECORD_INVALID,
                f"identifier_field_schema_unresolved:{field_name}",
                namespace,
            )
        schema_reason = _field_schema_reason(field_schema, role)
        if schema_reason is not None:
            return _single_result(
                rule,
                ValidationOutcome.UNSUPPORTED,
                VALIDATION_EXECUTOR_UNSUPPORTED,
                f"{schema_reason}:{field_name}",
                namespace,
            )
        field_contracts.append((field_name, field_schema))

    guard_schema = next(
        schema
        for name, schema in field_contracts
        if name == shape.guard_field
    )
    if guard_schema.get("field_id") != rule.target_field_id:
        return _single_result(
            rule,
            ValidationOutcome.UNSUPPORTED,
            VALIDATION_EXECUTOR_UNSUPPORTED,
            "target_field_not_guard_field",
            namespace,
        )

    target_records = _resolve_table(
        data, rule.target_table_id, namespace=namespace
    )
    if target_records is None:
        return _single_result(
            rule,
            ValidationOutcome.FAIL,
            VALIDATION_CONTRACT_FIELD_TARGET_TABLE_MISSING,
            "target_table_missing",
            namespace,
        )

    expected = _expected_contract(rule, namespace, shape.name)
    diagnostics: list[ValidationExecutionDiagnostic] = []
    for record in sorted(
        target_records,
        key=lambda item: _record_sort_key(item, primary_key),
    ):
        identity = _safe_record_identity(record, primary_key)
        if not _valid_identity(record, primary_key):
            diagnostics.append(
                _diagnostic(
                    rule,
                    VALIDATION_CONTRACT_FIELD_TARGET_RECORD_INVALID,
                    "target_identity_invalid",
                    identity,
                    record.get(primary_key),
                    expected,
                )
            )
            continue

        environment, invalid = _record_environment(record, field_contracts)
        if invalid is not None:
            reason, observed, field_id = invalid
            diagnostics.append(
                _diagnostic(
                    rule,
                    VALIDATION_CONTRACT_FIELD_TARGET_RECORD_INVALID,
                    reason,
                    identity,
                    observed,
                    expected,
                    field_id,
                )
            )
            continue

        try:
            result = evaluate_validation_expression(
                rule.condition_ast,
                environment,
            )
        except ValidationExpressionUnsupportedError as error:
            raise RuntimeError(
                "A statically accepted contract-field expression became unsupported."
            ) from error
        except ValidationExpressionEvaluationError as error:
            evaluation_reason = dict(error.context).get(
                "reason", "evaluation_error"
            )
            diagnostics.append(
                _diagnostic(
                    rule,
                    VALIDATION_CONTRACT_FIELD_TARGET_RECORD_INVALID,
                    f"expression_evaluation_error:{evaluation_reason}",
                    identity,
                    None,
                    expected,
                )
            )
            continue

        if type(result) is not bool:
            diagnostics.append(
                _diagnostic(
                    rule,
                    VALIDATION_CONTRACT_FIELD_TARGET_RECORD_INVALID,
                    "expression_result_not_boolean",
                    identity,
                    result if _is_diagnostic_scalar(result) else None,
                    expected,
                )
            )
        elif not result:
            diagnostics.append(
                _diagnostic(
                    rule,
                    VALIDATION_CONTRACT_FIELD_INVARIANT_FAILED,
                    "predicate_false",
                    identity,
                    False,
                    expected,
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


def _contract_field_shape(
    rule: ValidationRuleDefinition,
) -> tuple[_ContractShape | None, str | None]:
    if rule.validation_kind_id != "contract_field_invariant":
        return None, "validation_kind_not_contract_field_invariant"
    if rule.validation_stage_id != "pre_export":
        return None, "validation_stage_not_pre_export"
    if rule.rule_scope_id != "record":
        return None, "rule_scope_not_record"
    if rule.target_table_id != _CONTRACT_FIELDS_TABLE:
        return None, "target_table_not_contract_fields"
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
    try:
        parsed = parse_validation_expression(rule.condition_expression_source)
    except ValidationExpressionError:
        return None, "condition_expression_source_invalid"
    if (
        parsed != rule.condition_ast
        or semantic_ast_hash(rule.condition_ast) != rule.condition_ast_hash
    ):
        return None, "condition_expression_ast_mismatch"

    shape = next(
        (
            candidate_shape
            for candidate_ast, candidate_shape in _SUPPORTED_SHAPES
            if rule.condition_ast == candidate_ast
        ),
        None,
    )
    if shape is None:
        return None, "contract_field_ast_shape_not_supported"
    expected_identifiers = tuple(sorted(shape.identifiers, key=_utf8))
    if (
        rule.local_bindings
        or rule.free_identifiers != expected_identifiers
    ):
        return None, "condition_identifier_inventory_mismatch"
    return shape, None


def _field_schema_reason(field_schema: FrozenRecord, role: str) -> str | None:
    expected = {
        "required_boolean": ("boolean", "always", False, "forbidden"),
        "required_string": ("string", "always", False, "forbidden"),
        "nullable_integer": ("integer", "conditional", True, "explicit_null"),
    }[role]
    actual = (
        field_schema.get("data_type"),
        field_schema.get("required_mode"),
        field_schema.get("nullable"),
        field_schema.get("null_handling"),
    )
    return None if actual == expected else f"identifier_schema_role_invalid:{role}"


def _record_environment(
    record: FrozenRecord,
    field_contracts: list[tuple[str, FrozenRecord]],
) -> tuple[
    dict[str, CanonicalScalar],
    tuple[str, CanonicalScalar, str | None] | None,
]:
    environment: dict[str, CanonicalScalar] = {}
    for field_name, field_schema in field_contracts:
        field_id = field_schema.get("field_id")
        canonical_field_id = field_id if isinstance(field_id, str) else None
        if field_name not in record:
            return environment, (
                f"target_field_missing:{field_name}",
                None,
                canonical_field_id,
            )
        value = record[field_name]
        reason = _field_value_reason(value, field_schema)
        if reason is not None:
            return environment, (
                f"{reason}:{field_name}",
                value,
                canonical_field_id,
            )
        environment[field_name] = value
    return environment, None


def _field_value_reason(
    value: CanonicalScalar,
    field_schema: FrozenRecord,
) -> str | None:
    if value is None:
        return (
            None
            if field_schema.get("nullable") is True
            else "target_value_null_forbidden"
        )
    expected_type = {
        "boolean": bool,
        "integer": int,
        "string": str,
    }[field_schema["data_type"]]
    return None if type(value) is expected_type else "target_value_type_invalid"


def _safe_record_identity(record: FrozenRecord, primary_key: str) -> str:
    if _valid_identity(record, primary_key):
        return _record_identity(record, primary_key)
    digest = hashlib.sha256(
        _canonical_record_text(record).encode("utf-8")
    ).hexdigest()
    return f"canonical-record-sha256:{digest}"


def _expected_contract(
    rule: ValidationRuleDefinition,
    namespace: str,
    shape_name: str,
) -> str:
    return (
        f"exact boolean {shape_name} CONTRACT_FIELDS predicate over "
        f"{namespace}:{rule.target_table_id}; ast={rule.condition_ast_hash}"
    )


def _diagnostic(
    rule: ValidationRuleDefinition,
    code: str,
    reason: str,
    identity: str | None,
    observed: CanonicalScalar,
    expected: str,
    field_id: str | None = None,
) -> ValidationExecutionDiagnostic:
    return ValidationExecutionDiagnostic(
        code,
        "Canonical contract-field definition validation failed.",
        rule.rule_id,
        rule.target_table_id,
        field_id or rule.target_field_id,
        identity,
        observed,
        expected,
        reason,
    )


def _single_result(
    rule: ValidationRuleDefinition,
    outcome: ValidationOutcome,
    code: str,
    reason: str,
    namespace: str | None,
) -> ValidationExecutionResult:
    expected = (
        f"exact supported CONTRACT_FIELDS predicate over "
        f"{namespace}:{rule.target_table_id}"
        if namespace is not None
        else "bound source namespace and supported CONTRACT_FIELDS predicate"
    )
    diagnostic = _diagnostic(
        rule,
        code,
        reason,
        None,
        None,
        expected,
    )
    return ValidationExecutionResult(
        rule.rule_id,
        outcome,
        (diagnostic,),
        0,
        0 if outcome is ValidationOutcome.UNSUPPORTED else 1,
    )


def _is_diagnostic_scalar(value: object) -> bool:
    return value is None or type(value) in {bool, int, float, str}


__all__ = [
    "VALIDATION_CONTRACT_FIELD_INVARIANT_FAILED",
    "VALIDATION_CONTRACT_FIELD_TARGET_RECORD_INVALID",
    "VALIDATION_CONTRACT_FIELD_TARGET_TABLE_MISSING",
    "execute_contract_field_invariant_rule",
]
