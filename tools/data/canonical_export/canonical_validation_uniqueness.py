"""Single-field and explicit composite uniqueness validation execution."""

from __future__ import annotations

import json
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
        _diagnostic_sort_key,
        _record_identity,
        _record_sort_key,
        _resolve_field_schema,
        _resolve_primary_key,
        _resolve_table,
        _utf8,
        _valid_identity,
    )
    from .canonical_validation_expr import Call, ListLiteral, Literal
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
        _diagnostic_sort_key,
        _record_identity,
        _record_sort_key,
        _resolve_field_schema,
        _resolve_primary_key,
        _resolve_table,
        _utf8,
        _valid_identity,
    )
    from canonical_validation_expr import Call, ListLiteral, Literal
    from canonical_validation_rules import ValidationRuleDefinition


VALIDATION_UNIQUENESS_DUPLICATE = "VALIDATION_UNIQUENESS_DUPLICATE"
VALIDATION_UNIQUENESS_TARGET_RECORD_INVALID = (
    "VALIDATION_UNIQUENESS_TARGET_RECORD_INVALID"
)
VALIDATION_UNIQUENESS_TARGET_TABLE_MISSING = (
    "VALIDATION_UNIQUENESS_TARGET_TABLE_MISSING"
)
VALIDATION_UNIQUENESS_TARGET_FIELD_MISSING = (
    "VALIDATION_UNIQUENESS_TARGET_FIELD_MISSING"
)

TypedConstituent: TypeAlias = tuple[str, CanonicalScalar]
TypedUniquenessKey: TypeAlias = tuple[TypedConstituent, ...]


def execute_uniqueness_rule(
    rule: ValidationRuleDefinition,
    data: ValidationDataContext,
) -> ValidationExecutionResult:
    """Execute one of the three allowlisted uniqueness rule shapes."""

    if not isinstance(rule, ValidationRuleDefinition):
        raise TypeError("rule must be a ValidationRuleDefinition")
    if not isinstance(data, ValidationDataContext):
        raise TypeError("data must be a ValidationDataContext")

    field_names, exclude_null_keys, unsupported_reason = _uniqueness_contract(rule)
    if unsupported_reason is not None:
        return _uniqueness_single_result(
            rule,
            ValidationOutcome.UNSUPPORTED,
            VALIDATION_EXECUTOR_UNSUPPORTED,
            unsupported_reason,
            None,
        )

    namespace = data.namespace_for_component(rule.component_identity)
    if namespace is None:
        return _uniqueness_single_result(
            rule,
            ValidationOutcome.FAIL,
            VALIDATION_UNIQUENESS_TARGET_TABLE_MISSING,
            "source_namespace_missing",
            None,
        )

    field_schema = _resolve_field_schema(
        data,
        rule.target_table_id,
        field_id=rule.target_field_id,
        namespace=namespace,
        allow_empty_resolved_name=True,
    )
    if field_schema is None:
        return _uniqueness_single_result(
            rule,
            ValidationOutcome.FAIL,
            VALIDATION_UNIQUENESS_TARGET_FIELD_MISSING,
            "target_field_schema_unresolved",
            namespace,
        )
    field_name = field_schema.get("field_name")
    if not isinstance(field_name, str) or not field_name:
        return _uniqueness_single_result(
            rule,
            ValidationOutcome.FAIL,
            VALIDATION_UNIQUENESS_TARGET_FIELD_MISSING,
            "target_field_schema_malformed",
            namespace,
        )
    if field_names is None and not _is_required_string_field(field_schema):
        return _uniqueness_single_result(
            rule,
            ValidationOutcome.UNSUPPORTED,
            VALIDATION_EXECUTOR_UNSUPPORTED,
            "target_schema_not_required_string",
            namespace,
            field_name,
        )

    field_contracts: tuple[tuple[str, FrozenRecord], ...]
    if field_names is None:
        field_contracts = ((field_name, field_schema),)
    else:
        expression_name = (
            "unique_non_null_by" if exclude_null_keys else "unique_by"
        )
        resolved_fields: list[tuple[str, FrozenRecord]] = []
        for composite_field_name in field_names:
            composite_schema = _resolve_field_schema(
                data,
                rule.target_table_id,
                field_name=composite_field_name,
                namespace=namespace,
            )
            if composite_schema is None:
                return _uniqueness_single_result(
                    rule,
                    ValidationOutcome.UNSUPPORTED,
                    VALIDATION_EXECUTOR_UNSUPPORTED,
                    f"{expression_name}_field_unresolved:{composite_field_name}",
                    namespace,
                    field_name,
                )
            if not _is_supported_composite_field(composite_schema):
                return _uniqueness_single_result(
                    rule,
                    ValidationOutcome.UNSUPPORTED,
                    VALIDATION_EXECUTOR_UNSUPPORTED,
                    f"{expression_name}_field_schema_unsupported:{composite_field_name}",
                    namespace,
                    field_name,
                )
            resolved_fields.append((composite_field_name, composite_schema))
        field_contracts = tuple(resolved_fields)

    primary_key = _resolve_primary_key(
        data, rule.target_table_id, namespace=namespace
    )
    if primary_key is None:
        return _uniqueness_single_result(
            rule,
            ValidationOutcome.FAIL,
            VALIDATION_UNIQUENESS_TARGET_TABLE_MISSING,
            "target_table_schema_unresolved",
            namespace,
            field_name,
        )
    target_records = _resolve_table(
        data, rule.target_table_id, namespace=namespace
    )
    if target_records is None:
        return _uniqueness_single_result(
            rule,
            ValidationOutcome.FAIL,
            VALIDATION_UNIQUENESS_TARGET_TABLE_MISSING,
            "target_table_missing",
            namespace,
            field_name,
        )

    expected = (
        _uniqueness_expected(namespace, rule.target_table_id, field_name)
        if field_names is None
        else _composite_expected(
            namespace, rule.target_table_id, field_names, exclude_null_keys
        )
    )
    diagnostics: list[ValidationExecutionDiagnostic] = []
    groups: dict[TypedUniquenessKey, list[str]] = {}
    ordered_records = sorted(
        target_records,
        key=lambda record: _record_sort_key(record, primary_key),
    )
    for record in ordered_records:
        if field_names is None:
            identity, observed, invalid_reason = _uniqueness_record_value(
                record, primary_key, field_name
            )
            key = (
                (("string", observed),)
                if invalid_reason is None
                else None
            )
        else:
            identity, key, observed, invalid_reason = _composite_record_key(
                record, primary_key, field_contracts
            )
        if invalid_reason is not None:
            diagnostics.append(
                _shape_diagnostic(
                    rule, field_names,
                    VALIDATION_UNIQUENESS_TARGET_RECORD_INVALID,
                    invalid_reason, identity, observed, expected,
                )
            )
            continue
        assert key is not None
        if exclude_null_keys and any(value is None for _, value in key):
            continue
        groups.setdefault(key, []).append(identity)

    for key in sorted(groups, key=lambda item: _utf8(_typed_key_text(item))):
        identities = tuple(sorted(groups[key], key=_utf8))
        if len(identities) <= 1:
            continue
        diagnostics.append(
            _shape_diagnostic(
                rule, field_names, VALIDATION_UNIQUENESS_DUPLICATE,
                "duplicate_value" if field_names is None else "duplicate_composite_key",
                None,
                key[0][1] if field_names is None else _typed_key_text(key),
                expected, identities,
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


def _uniqueness_contract(
    rule: ValidationRuleDefinition,
) -> tuple[tuple[str, ...] | None, bool, str | None]:
    if rule.validation_kind_id != "uniqueness":
        return None, False, "validation_kind_not_uniqueness"
    if rule.rule_scope_id != "table":
        return None, False, "rule_scope_not_table"
    if rule.validation_stage_id != "pre_export":
        return None, False, "validation_stage_not_pre_export"
    if rule.target_field_id is None:
        return None, False, "target_field_missing"
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
        return None, False, "structured_shape_not_supported"

    expression_contract = (
        rule.condition_expression_source,
        rule.condition_ast,
        rule.condition_ast_hash,
    )
    if all(value is None for value in expression_contract):
        return None, False, None
    if any(value is None for value in expression_contract):
        return None, False, "structured_shape_not_supported"
    if (
        type(rule.condition_expression_source) is not str
        or not rule.condition_expression_source
        or type(rule.condition_ast_hash) is not str
        or not rule.condition_ast_hash
    ):
        return None, False, "structured_shape_not_supported"
    if not isinstance(rule.condition_ast, Call):
        return None, False, "structured_shape_not_supported"
    expression_name = rule.condition_ast.function
    if expression_name not in {"unique_by", "unique_non_null_by"}:
        return None, False, "structured_shape_not_supported"
    if len(rule.condition_ast.arguments) != 1:
        return None, False, f"{expression_name}_shape_not_supported"
    field_list = rule.condition_ast.arguments[0]
    if not isinstance(field_list, ListLiteral) or not field_list.items:
        return None, False, f"{expression_name}_shape_not_supported"
    if any(
        not isinstance(item, Literal)
        or item.literal_kind != "string"
        or type(item.value) is not str
        or not item.value
        for item in field_list.items
    ):
        return None, False, f"{expression_name}_shape_not_supported"
    field_names = tuple(item.value for item in field_list.items)
    if len(field_names) != len(set(field_names)):
        return None, False, f"{expression_name}_shape_not_supported"
    return field_names, expression_name == "unique_non_null_by", None


def _is_required_string_field(field_schema: FrozenRecord) -> bool:
    return (
        field_schema.get("data_type") == "string"
        and field_schema.get("required_mode") == "always"
        and field_schema.get("nullable") is False
        and field_schema.get("null_handling") == "forbidden"
    )


def _is_supported_composite_field(field_schema: FrozenRecord) -> bool:
    if field_schema.get("data_type") not in {"string", "integer", "language_tag"}:
        return False
    nullable = field_schema.get("nullable")
    if nullable is False:
        return (
            field_schema.get("required_mode") == "always"
            and field_schema.get("null_handling") == "forbidden"
        )
    return (
        nullable is True
        and field_schema.get("required_mode") == "conditional"
        and field_schema.get("null_handling") == "explicit_null"
    )


def _uniqueness_record_value(
    record: FrozenRecord,
    primary_key: str,
    field_name: str,
) -> tuple[str, CanonicalScalar, str | None]:
    identity = _record_identity(record, primary_key)
    if not _valid_identity(record, primary_key):
        return identity, record.get(primary_key), "target_identity_invalid"
    if field_name not in record:
        return identity, None, "target_field_missing"
    observed = record[field_name]
    if observed is None:
        return identity, observed, "target_value_null_forbidden"
    if type(observed) is not str:
        return identity, observed, "target_value_not_string"
    if not observed.strip():
        return identity, observed, "target_value_blank"
    return identity, observed, None


def _composite_record_key(
    record: FrozenRecord,
    primary_key: str,
    fields: tuple[tuple[str, FrozenRecord], ...],
) -> tuple[str, TypedUniquenessKey | None, CanonicalScalar, str | None]:
    identity = _record_identity(record, primary_key)
    if not _valid_identity(record, primary_key):
        return identity, None, record.get(primary_key), "target_identity_invalid"

    key: list[TypedConstituent] = []
    for field_name, field_schema in fields:
        if field_name not in record:
            return identity, None, None, f"target_field_missing:{field_name}"
        observed = record[field_name]
        data_type = field_schema["data_type"]
        if observed is None:
            if (
                field_schema.get("nullable") is True
                and field_schema.get("null_handling") == "explicit_null"
            ):
                key.append((data_type, None))
                continue
            return (
                identity, None, observed,
                f"target_value_null_forbidden:{field_name}",
            )
        if data_type == "integer":
            if type(observed) is not int:
                return (
                    identity, None, observed,
                    f"target_value_type_invalid:{field_name}",
                )
        elif type(observed) is not str:
            return (
                identity, None, observed,
                f"target_value_type_invalid:{field_name}",
            )
        elif not observed.strip():
            return identity, None, observed, f"target_value_blank:{field_name}"
        key.append((data_type, observed))
    return identity, tuple(key), None, None


def _typed_key_text(key: TypedUniquenessKey) -> str:
    return json.dumps(key, ensure_ascii=False, separators=(",", ":"))


def _uniqueness_expected(
    namespace: str, table_id: str, field_name: str
) -> str:
    return (
        "one exact required canonical string value per record in "
        f"{namespace}:{table_id}.{field_name}"
    )


def _composite_expected(
    namespace: str,
    table_id: str,
    field_names: tuple[str, ...],
    exclude_null_keys: bool = False,
) -> str:
    field_list = json.dumps(field_names, ensure_ascii=False, separators=(",", ":"))
    applicability = " non-null" if exclude_null_keys else ""
    return (
        f"one exact typed{applicability} composite key per applicable record for "
        f"{namespace}:{table_id}.{field_list}"
    )


def _uniqueness_diagnostic(
    rule: ValidationRuleDefinition,
    code: str,
    reason: str,
    identity: str | None,
    observed: CanonicalScalar,
    expected: str,
    related: tuple[str, ...] = (),
) -> ValidationExecutionDiagnostic:
    return ValidationExecutionDiagnostic(
        code,
        "Single-field uniqueness validation failed.",
        rule.rule_id,
        rule.target_table_id,
        rule.target_field_id,
        identity,
        observed,
        expected,
        reason,
        related,
    )


def _shape_diagnostic(
    rule: ValidationRuleDefinition,
    field_names: tuple[str, ...] | None,
    code: str,
    reason: str,
    identity: str | None,
    observed: CanonicalScalar,
    expected: str,
    related: tuple[str, ...] = (),
) -> ValidationExecutionDiagnostic:
    if field_names is None:
        return _uniqueness_diagnostic(
            rule, code, reason, identity, observed, expected, related
        )
    return ValidationExecutionDiagnostic(
        code,
        "Composite uniqueness validation failed.",
        rule.rule_id,
        rule.target_table_id,
        rule.target_field_id,
        identity,
        observed,
        expected,
        reason,
        related,
    )


def _uniqueness_single_result(
    rule: ValidationRuleDefinition,
    outcome: ValidationOutcome,
    code: str,
    reason: str,
    namespace: str | None,
    field_name: str | None = None,
) -> ValidationExecutionResult:
    expected = (
        _uniqueness_expected(namespace, rule.target_table_id, field_name)
        if namespace is not None and field_name is not None
        else "explicit source namespace and structured required-string uniqueness contract"
    )
    diagnostic = _uniqueness_diagnostic(
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
    "VALIDATION_UNIQUENESS_DUPLICATE",
    "VALIDATION_UNIQUENESS_TARGET_FIELD_MISSING",
    "VALIDATION_UNIQUENESS_TARGET_RECORD_INVALID",
    "VALIDATION_UNIQUENESS_TARGET_TABLE_MISSING",
    "execute_uniqueness_rule",
]
