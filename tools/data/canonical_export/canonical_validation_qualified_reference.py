"""Execution for canonical qualified-reference expression rules."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

try:
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
    from .canonical_validation_expr_eval import (
        ValidationExpressionEvaluationError,
        ValidationExpressionUnsupportedError,
        evaluate_validation_expression,
    )
    from .canonical_validation_rules import ValidationRuleDefinition
except ImportError:
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
    from canonical_validation_expr_eval import (
        ValidationExpressionEvaluationError,
        ValidationExpressionUnsupportedError,
        evaluate_validation_expression,
    )
    from canonical_validation_rules import ValidationRuleDefinition


VALIDATION_QUALIFIED_REFERENCE_INVARIANT_FAILED = (
    "VALIDATION_QUALIFIED_REFERENCE_INVARIANT_FAILED"
)
VALIDATION_QUALIFIED_REFERENCE_TARGET_RECORD_INVALID = (
    "VALIDATION_QUALIFIED_REFERENCE_TARGET_RECORD_INVALID"
)
VALIDATION_QUALIFIED_REFERENCE_TARGET_TABLE_MISSING = (
    "VALIDATION_QUALIFIED_REFERENCE_TARGET_TABLE_MISSING"
)
VALIDATION_QUALIFIED_REFERENCE_RESOLUTION_INVALID = (
    "VALIDATION_QUALIFIED_REFERENCE_RESOLUTION_INVALID"
)

_ALLOWED_BINARY_OPERATORS = frozenset({"==", "!=", "and", "or", "in"})
_BUILTIN_ARITIES = {
    "exists": 3,
    "group_of": 1,
    "lookup": 4,
    "primary_key_of": 1,
    "value_of": 1,
    "when": 2,
}
_SCALAR_SCHEMA_TYPES = frozenset(
    {"boolean", "date", "integer", "language_tag", "string", "text", "version"}
)
_EXTERNAL_IDENTIFIER_POLICY = "namespace_colon_identifier"


@dataclass(frozen=True, slots=True)
class _ResolutionError(ValueError):
    reason: str
    source_namespace: str
    namespace: str | None
    table_id: str
    field_name: str | None = None
    observed_value: CanonicalScalar = None
    related_record_identities: tuple[str, ...] = ()

    def __str__(self) -> str:
        return self.reason


def execute_qualified_reference_match_rule(
    rule: ValidationRuleDefinition,
    data: ValidationDataContext,
) -> ValidationExecutionResult:
    """Execute one allowlisted qualified-reference expression."""
    if not isinstance(rule, ValidationRuleDefinition):
        raise TypeError("rule must be a ValidationRuleDefinition")
    if not isinstance(data, ValidationDataContext):
        raise TypeError("data must be a ValidationDataContext")

    unsupported_reason = _contract_reason(rule)
    if unsupported_reason is not None:
        return _single_result(
            rule,
            ValidationOutcome.UNSUPPORTED,
            VALIDATION_EXECUTOR_UNSUPPORTED,
            "The qualified-reference expression shape is not supported.",
            unsupported_reason,
            None,
        )

    namespace = data.namespace_for_component(rule.component_identity)
    if namespace is None:
        return _single_result(
            rule,
            ValidationOutcome.FAIL,
            VALIDATION_QUALIFIED_REFERENCE_TARGET_TABLE_MISSING,
            "The source component namespace binding is missing.",
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
            VALIDATION_QUALIFIED_REFERENCE_TARGET_TABLE_MISSING,
            "The target table schema could not be resolved.",
            "target_table_schema_unresolved",
            namespace,
        )

    field_contracts: list[tuple[str, FrozenRecord]] = []
    for name in sorted(rule.free_identifiers, key=_utf8):
        schema = _resolve_field_schema(
            data,
            rule.target_table_id,
            field_name=name,
            namespace=namespace,
        )
        if schema is None:
            return _single_result(
                rule,
                ValidationOutcome.FAIL,
                VALIDATION_QUALIFIED_REFERENCE_TARGET_RECORD_INVALID,
                "An expression identifier has no unique active target field.",
                f"identifier_field_schema_unresolved:{name}",
                namespace,
            )
        schema_reason = _field_schema_reason(schema)
        if schema_reason is not None:
            return _single_result(
                rule,
                ValidationOutcome.FAIL,
                VALIDATION_QUALIFIED_REFERENCE_TARGET_RECORD_INVALID,
                "An expression identifier has an invalid scalar schema.",
                f"{schema_reason}:{name}",
                namespace,
            )
        field_contracts.append((name, schema))

    records = _resolve_table(data, rule.target_table_id, namespace=namespace)
    if records is None:
        return _single_result(
            rule,
            ValidationOutcome.FAIL,
            VALIDATION_QUALIFIED_REFERENCE_TARGET_TABLE_MISSING,
            "The target table is missing from the source namespace.",
            "target_table_missing",
            namespace,
        )

    diagnostics: list[ValidationExecutionDiagnostic] = []
    expected = _expected_contract(rule, namespace)
    for record in sorted(
        records, key=lambda item: _record_sort_key(item, primary_key)
    ):
        identity = _safe_identity(record, primary_key)
        if not _valid_identity(record, primary_key):
            diagnostics.append(
                _diagnostic(
                    rule,
                    VALIDATION_QUALIFIED_REFERENCE_TARGET_RECORD_INVALID,
                    "The target record identity is invalid.",
                    "target_identity_invalid",
                    identity,
                    record.get(primary_key),
                    expected,
                )
            )
            continue
        environment, invalid = _record_environment(record, field_contracts)
        if invalid is not None:
            reason, observed = invalid
            diagnostics.append(
                _diagnostic(
                    rule,
                    VALIDATION_QUALIFIED_REFERENCE_TARGET_RECORD_INVALID,
                    "The target record violates its scalar field schema.",
                    reason,
                    identity,
                    observed,
                    expected,
                )
            )
            continue
        try:
            result = evaluate_validation_expression(
                rule.condition_ast,
                environment,
                exists_resolver=lambda table, field, value: _resolve_exists(
                    data, namespace, table, field, value
                ),
                lookup_resolver=lambda table, field, value, output: (
                    _resolve_scalar_lookup(
                        data, namespace, table, field, value, output
                    )
                ),
                registry_group_resolver=lambda registry_id: (
                    _resolve_registry_value(data, registry_id, "group_id")
                ),
                value_of_resolver=lambda registry_id: (
                    _resolve_registry_value(data, registry_id, "value_id")
                ),
                primary_key_resolver=lambda table: _resolve_primary_key_name(
                    data, namespace, table
                ),
            )
        except _ResolutionError as error:
            diagnostics.append(_resolution_diagnostic(rule, error, identity))
            continue
        except ValidationExpressionUnsupportedError as error:
            raise RuntimeError(
                "A statically accepted qualified-reference expression became unsupported."
            ) from error
        except ValidationExpressionEvaluationError as error:
            reason = dict(error.context).get("reason", "evaluation_error")
            diagnostics.append(
                _diagnostic(
                    rule,
                    VALIDATION_QUALIFIED_REFERENCE_TARGET_RECORD_INVALID,
                    "The qualified-reference expression could not be evaluated.",
                    f"expression_evaluation_error:{reason}",
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
                    VALIDATION_QUALIFIED_REFERENCE_TARGET_RECORD_INVALID,
                    "The qualified-reference expression did not return a boolean.",
                    "expression_result_not_boolean",
                    identity,
                    result if _is_scalar(result) else None,
                    expected,
                )
            )
        elif not result:
            diagnostics.append(
                _diagnostic(
                    rule,
                    VALIDATION_QUALIFIED_REFERENCE_INVARIANT_FAILED,
                    "The canonical record violates the qualified-reference invariant.",
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
        len(records),
        len(ordered),
    )


def _contract_reason(rule: ValidationRuleDefinition) -> str | None:
    if rule.validation_kind_id != "qualified_reference_match":
        return "validation_kind_not_qualified_reference_match"
    if rule.validation_stage_id != "pre_export":
        return "validation_stage_not_pre_export"
    if rule.rule_scope_id != "cross_table":
        return "rule_scope_not_cross_table"
    if (
        type(rule.condition_expression_source) is not str
        or not rule.condition_expression_source
        or rule.condition_ast is None
        or type(rule.condition_ast_hash) is not str
        or not rule.condition_ast_hash
    ):
        return "condition_expression_missing_or_invalid"
    return _ast_unsupported_reason(rule.condition_ast, top_level=True)


def _ast_unsupported_reason(node: object, *, top_level: bool = False) -> str | None:
    if isinstance(node, (Literal, Identifier)):
        return None
    if isinstance(node, ListLiteral):
        return next(
            (
                reason
                for item in node.items
                if (reason := _ast_unsupported_reason(item)) is not None
            ),
            None,
        )
    if isinstance(node, BinaryOperation):
        if node.operator not in _ALLOWED_BINARY_OPERATORS:
            return f"operator_not_supported:{node.operator}"
        return _ast_unsupported_reason(node.left) or _ast_unsupported_reason(
            node.right
        )
    if not isinstance(node, Call):
        return f"node_not_supported:{type(node).__name__}"
    if node.function not in _BUILTIN_ARITIES:
        return f"builtin_not_supported:{node.function}"
    if len(node.arguments) != _BUILTIN_ARITIES[node.function]:
        return f"{node.function}_arity_not_supported"
    if node.function == "when" and not top_level:
        return "when_not_top_level"
    if node.function == "lookup":
        for index in (0, 1, 3):
            token = node.arguments[index]
            if not (
                isinstance(token, Literal)
                and token.literal_kind == "string"
                and type(token.value) is str
                and bool(token.value)
            ):
                return f"lookup_token_not_string_literal:{index}"
    return next(
        (
            reason
            for argument in node.arguments
            if (reason := _ast_unsupported_reason(argument)) is not None
        ),
        None,
    )


def _resolve_table_identity(
    data: ValidationDataContext,
    source_namespace: str,
    table_source: str,
) -> tuple[str, str]:
    parts = table_source.split(":")
    if len(parts) == 1:
        namespace, table_id = source_namespace, parts[0]
    elif len(parts) == 2:
        namespace, table_id = parts
    else:
        namespace, table_id = None, table_source
    if not (
        namespace is not None
        and _is_logical_identifier(namespace)
        and _is_logical_identifier(table_id)
        and data.has_namespace(namespace)
    ):
        raise _resolution_error(
            "table_namespace_invalid",
            source_namespace,
            namespace,
            table_id,
            observed=table_source,
        )
    return namespace, table_id


def _resolve_primary_key_name(
    data: ValidationDataContext,
    source_namespace: str,
    table_source: str,
) -> str:
    namespace, table_id = _resolve_table_identity(
        data, source_namespace, table_source
    )
    schema_tables = _resolve_table(data, "schema_tables", namespace=namespace)
    if schema_tables is None:
        raise _resolution_error(
            "schema_tables_authority_missing",
            source_namespace,
            namespace,
            table_id,
            observed=table_source,
        )
    matches = tuple(
        record
        for record in schema_tables
        if record.get("table_id") == table_id
        and record.get("status") == "active"
    )
    if not matches:
        raise _resolution_error(
            "primary_key_table_unknown",
            source_namespace,
            namespace,
            table_id,
            observed=table_source,
        )
    if len(matches) > 1:
        related = tuple(sorted(
            (_safe_identity(record, "table_id") for record in matches),
            key=_utf8,
        ))
        raise _resolution_error(
            "primary_key_table_ambiguous",
            source_namespace,
            namespace,
            table_id,
            observed=table_source,
            related=related,
        )
    primary_key = matches[0].get("primary_key")
    if type(primary_key) is not str or not primary_key:
        raise _resolution_error(
            "primary_key_value_invalid",
            source_namespace,
            namespace,
            table_id,
            observed=(primary_key if _is_scalar(primary_key) else None),
        )
    schema = _resolve_field_schema(
        data,
        table_id,
        field_name=primary_key,
        namespace=namespace,
    )
    if schema is None or _field_schema_reason(schema) is not None:
        raise _resolution_error(
            "primary_key_field_schema_invalid",
            source_namespace,
            namespace,
            table_id,
            field_name=primary_key,
            observed=primary_key,
        )
    return primary_key


def _resolve_exists(
    data: ValidationDataContext,
    source_namespace: str,
    table_source: str,
    key_field_name: str,
    key_value: CanonicalScalar,
) -> bool:
    namespace, table_id, resolved_key_value = _resolve_key_location(
        data,
        source_namespace,
        table_source,
        key_field_name,
        key_value,
    )
    records = _resolve_table(data, table_id, namespace=namespace)
    if records is None:
        raise _resolution_error(
            "exists_table_missing",
            source_namespace,
            namespace,
            table_id,
            field_name=key_field_name,
            observed=key_value,
        )
    key_schema = _resolve_field_schema(
        data,
        table_id,
        field_name=key_field_name,
        namespace=namespace,
    )
    if key_schema is None or _field_schema_reason(key_schema) is not None:
        raise _resolution_error(
            "exists_key_field_schema_invalid",
            source_namespace,
            namespace,
            table_id,
            field_name=key_field_name,
            observed=key_value,
        )
    if resolved_key_value is None or _field_value_reason(
        resolved_key_value, key_schema
    ) is not None:
        raise _resolution_error(
            "exists_key_value_invalid",
            source_namespace,
            namespace,
            table_id,
            field_name=key_field_name,
            observed=key_value,
        )
    primary_key = _resolve_primary_key_name(
        data, source_namespace, f"{namespace}:{table_id}"
    )
    matched = False
    for record in sorted(
        records, key=lambda item: _record_sort_key(item, primary_key)
    ):
        identity = _safe_identity(record, primary_key)
        if not _valid_identity(record, primary_key):
            raise _resolution_error(
                "exists_candidate_identity_invalid",
                source_namespace,
                namespace,
                table_id,
                field_name=key_field_name,
                observed=key_value,
                related=(identity,),
            )
        if key_field_name not in record or _field_value_reason(
            record.get(key_field_name), key_schema
        ) is not None:
            raise _resolution_error(
                "exists_candidate_key_invalid",
                source_namespace,
                namespace,
                table_id,
                field_name=key_field_name,
                observed=key_value,
                related=(identity,),
            )
        matched = matched or _typed_equal(
            record[key_field_name], resolved_key_value
        )
    return matched


def _resolve_scalar_lookup(
    data: ValidationDataContext,
    source_namespace: str,
    table_source: str,
    key_field_name: str,
    key_value: CanonicalScalar,
    output_field_name: str,
) -> CanonicalScalar:
    namespace, table_id, resolved_key_value = _resolve_key_location(
        data,
        source_namespace,
        table_source,
        key_field_name,
        key_value,
    )
    records = _resolve_table(data, table_id, namespace=namespace)
    if records is None:
        raise _resolution_error(
            "lookup_table_missing",
            source_namespace,
            namespace,
            table_id,
            field_name=key_field_name,
            observed=key_value,
        )
    key_schema = _resolve_field_schema(
        data, table_id, field_name=key_field_name, namespace=namespace
    )
    output_schema = _resolve_field_schema(
        data, table_id, field_name=output_field_name, namespace=namespace
    )
    if key_schema is None or _field_schema_reason(key_schema) is not None:
        raise _resolution_error(
            "lookup_key_field_schema_invalid",
            source_namespace,
            namespace,
            table_id,
            field_name=key_field_name,
            observed=key_value,
        )
    if output_schema is None or _field_schema_reason(output_schema) is not None:
        raise _resolution_error(
            "lookup_output_field_schema_invalid",
            source_namespace,
            namespace,
            table_id,
            field_name=output_field_name,
            observed=key_value,
        )
    primary_key = _resolve_primary_key_name(
        data, source_namespace, f"{namespace}:{table_id}"
    )
    if primary_key != key_field_name:
        raise _resolution_error(
            "lookup_key_field_not_primary",
            source_namespace,
            namespace,
            table_id,
            field_name=key_field_name,
            observed=key_value,
        )
    if resolved_key_value is None or _field_value_reason(
        resolved_key_value, key_schema
    ) is not None:
        raise _resolution_error(
            "lookup_key_value_invalid",
            source_namespace,
            namespace,
            table_id,
            field_name=key_field_name,
            observed=key_value,
        )
    matches: list[FrozenRecord] = []
    for record in sorted(
        records, key=lambda item: _record_sort_key(item, primary_key)
    ):
        identity = _safe_identity(record, primary_key)
        if not _valid_identity(record, primary_key):
            raise _resolution_error(
                "lookup_candidate_identity_invalid",
                source_namespace,
                namespace,
                table_id,
                field_name=key_field_name,
                observed=key_value,
                related=(identity,),
            )
        if key_field_name not in record or _field_value_reason(
            record.get(key_field_name), key_schema
        ) is not None:
            raise _resolution_error(
                "lookup_candidate_key_invalid",
                source_namespace,
                namespace,
                table_id,
                field_name=key_field_name,
                observed=key_value,
                related=(identity,),
            )
        if _typed_equal(record[key_field_name], resolved_key_value):
            matches.append(record)
    if not matches:
        return None
    if len(matches) > 1:
        related = tuple(sorted(
            (_safe_identity(record, primary_key) for record in matches),
            key=_utf8,
        ))
        raise _resolution_error(
            "lookup_ambiguous",
            source_namespace,
            namespace,
            table_id,
            field_name=key_field_name,
            observed=key_value,
            related=related,
        )
    match = matches[0]
    identity = _safe_identity(match, primary_key)
    if output_field_name not in match or _field_value_reason(
        match.get(output_field_name), output_schema
    ) is not None:
        raise _resolution_error(
            "lookup_output_value_invalid",
            source_namespace,
            namespace,
            table_id,
            field_name=output_field_name,
            observed=key_value,
            related=(identity,),
        )
    return _project_lookup_output(
        data,
        source_namespace,
        namespace,
        output_schema,
        match[output_field_name],
        table_id,
        output_field_name,
    )


def _resolve_key_location(
    data: ValidationDataContext,
    source_namespace: str,
    table_source: str,
    key_field_name: str,
    key_value: CanonicalScalar,
) -> tuple[str, str, CanonicalScalar]:
    namespace, table_id = _resolve_table_identity(
        data, source_namespace, table_source
    )
    if type(key_value) is not str or ":" not in key_value:
        return namespace, table_id, key_value
    if data.namespace_policy(
        source_namespace, "external_reference_identifier_policy"
    ) != _EXTERNAL_IDENTIFIER_POLICY:
        raise _resolution_error(
            "qualified_key_policy_missing",
            source_namespace,
            namespace,
            table_id,
            field_name=key_field_name,
            observed=key_value,
        )
    parsed = _split_qualified_identifier(key_value)
    if parsed is None:
        raise _resolution_error(
            "qualified_key_malformed",
            source_namespace,
            None,
            table_id,
            field_name=key_field_name,
            observed=key_value,
        )
    key_namespace, local_key_value = parsed
    if not data.has_namespace(key_namespace):
        raise _resolution_error(
            "qualified_key_namespace_unknown",
            source_namespace,
            key_namespace,
            table_id,
            field_name=key_field_name,
            observed=key_value,
        )
    if ":" in table_source and key_namespace != namespace:
        raise _resolution_error(
            "qualified_key_namespace_mismatch",
            source_namespace,
            key_namespace,
            table_id,
            field_name=key_field_name,
            observed=key_value,
        )
    namespace = key_namespace
    primary_key = _resolve_primary_key_name(
        data, source_namespace, f"{namespace}:{table_id}"
    )
    if primary_key != key_field_name:
        raise _resolution_error(
            "qualified_key_field_not_primary",
            source_namespace,
            namespace,
            table_id,
            field_name=key_field_name,
            observed=key_value,
        )
    return namespace, table_id, local_key_value


def _project_lookup_output(
    data: ValidationDataContext,
    source_namespace: str,
    resolved_namespace: str,
    output_schema: FrozenRecord,
    value: CanonicalScalar,
    table_id: str,
    output_field_name: str,
) -> CanonicalScalar:
    if resolved_namespace == source_namespace or value is None:
        return value
    reference_table_id = output_schema.get("reference_table_id")
    reference_field_id = output_schema.get("reference_field_id")
    if reference_table_id is None and reference_field_id is None:
        return value
    if not (
        type(reference_table_id) is str
        and reference_table_id
        and type(reference_field_id) is str
        and reference_field_id
        and type(value) is str
        and value
    ):
        raise _resolution_error(
            "lookup_output_reference_contract_invalid",
            source_namespace,
            resolved_namespace,
            table_id,
            field_name=output_field_name,
            observed=value,
        )
    if data.namespace_policy(
        source_namespace, "external_reference_identifier_policy"
    ) != _EXTERNAL_IDENTIFIER_POLICY:
        raise _resolution_error(
            "lookup_output_projection_policy_missing",
            source_namespace,
            resolved_namespace,
            table_id,
            field_name=output_field_name,
            observed=value,
        )
    reference_schema = _resolve_field_schema(
        data,
        reference_table_id,
        field_id=reference_field_id,
        namespace=resolved_namespace,
    )
    if reference_schema is None or _field_schema_reason(reference_schema) is not None:
        raise _resolution_error(
            "lookup_output_reference_schema_invalid",
            source_namespace,
            resolved_namespace,
            reference_table_id,
            field_name=output_field_name,
            observed=value,
        )
    return f"{resolved_namespace}:{value}"


def _split_qualified_identifier(value: str) -> tuple[str, str] | None:
    parts = value.split(":")
    if (
        len(parts) != 2
        or not _is_logical_identifier(parts[0])
        or type(parts[1]) is not str
        or not parts[1]
    ):
        return None
    return parts[0], parts[1]


def _resolve_registry_value(
    data: ValidationDataContext,
    registry_value_id: str,
    output_field_name: str,
) -> str | None:
    if not data.has_namespace("registry"):
        raise _resolution_error(
            "value_registry_namespace_missing",
            "registry",
            None,
            "value_registry",
            field_name="registry_value_id",
            observed=registry_value_id,
        )
    value = _resolve_scalar_lookup(
        data,
        "registry",
        "registry:value_registry",
        "registry_value_id",
        registry_value_id,
        output_field_name,
    )
    if value is not None and (type(value) is not str or not value):
        raise _resolution_error(
            "value_registry_output_invalid",
            "registry",
            "registry",
            "value_registry",
            field_name=output_field_name,
            observed=(value if _is_scalar(value) else None),
        )
    return value


def _field_schema_reason(schema: FrozenRecord) -> str | None:
    if schema.get("data_type") not in _SCALAR_SCHEMA_TYPES:
        return "field_schema_type_invalid"
    nullable = schema.get("nullable")
    if type(nullable) is not bool:
        return "field_schema_nullable_invalid"
    expected_required = "conditional" if nullable else "always"
    if schema.get("required_mode") != expected_required:
        return "field_schema_required_mode_invalid"
    expected_null = "explicit_null" if nullable else "forbidden"
    if schema.get("null_handling") != expected_null:
        return "field_schema_null_handling_invalid"
    return None


def _field_value_reason(
    value: CanonicalScalar, schema: FrozenRecord
) -> str | None:
    if value is None:
        return None if schema.get("nullable") is True else "value_null"
    expected = {
        "boolean": bool,
        "date": str,
        "integer": int,
        "language_tag": str,
        "string": str,
        "text": str,
        "version": str,
    }.get(schema.get("data_type"))
    return None if expected is not None and type(value) is expected else "value_type_invalid"


def _record_environment(
    record: FrozenRecord,
    contracts: list[tuple[str, FrozenRecord]],
) -> tuple[dict[str, CanonicalScalar], tuple[str, CanonicalScalar] | None]:
    environment = {}
    for name, schema in contracts:
        if name not in record:
            return environment, (f"target_field_missing:{name}", None)
        value = record[name]
        reason = _field_value_reason(value, schema)
        if reason is not None:
            return environment, (f"{reason}:{name}", value)
        environment[name] = value
    return environment, None


def _typed_equal(left: CanonicalScalar, right: CanonicalScalar) -> bool:
    return type(left) is type(right) and left == right


def _safe_identity(record: FrozenRecord, primary_key: str) -> str:
    if _valid_identity(record, primary_key):
        return _record_identity(record, primary_key)
    digest = hashlib.sha256(
        _canonical_record_text(record).encode("utf-8")
    ).hexdigest()
    return f"canonical-record-sha256:{digest}"


def _resolution_error(
    reason: str,
    source_namespace: str,
    namespace: str | None,
    table_id: str,
    *,
    field_name: str | None = None,
    observed: CanonicalScalar = None,
    related: tuple[str, ...] = (),
) -> _ResolutionError:
    return _ResolutionError(
        reason,
        source_namespace,
        namespace,
        table_id,
        field_name,
        observed,
        related,
    )


def _resolution_diagnostic(
    rule: ValidationRuleDefinition,
    error: _ResolutionError,
    identity: str | None,
) -> ValidationExecutionDiagnostic:
    namespace = error.namespace or "<unresolved>"
    expected = (
        f"qualified reference source={error.source_namespace}; "
        f"target={namespace}:{error.table_id}; "
        f"field={error.field_name or '<dynamic>'}"
    )
    return ValidationExecutionDiagnostic(
        VALIDATION_QUALIFIED_REFERENCE_RESOLUTION_INVALID,
        "Qualified-reference authority resolution failed.",
        rule.rule_id,
        rule.target_table_id,
        rule.target_field_id,
        identity,
        error.observed_value,
        expected,
        error.reason,
        error.related_record_identities,
    )


def _expected_contract(rule: ValidationRuleDefinition, namespace: str) -> str:
    return (
        f"exact boolean qualified-reference predicate over "
        f"{namespace}:{rule.target_table_id}; ast={rule.condition_ast_hash}"
    )


def _diagnostic(
    rule: ValidationRuleDefinition,
    code: str,
    message: str,
    reason: str,
    identity: str | None,
    observed: CanonicalScalar,
    expected: str,
) -> ValidationExecutionDiagnostic:
    return ValidationExecutionDiagnostic(
        code,
        message,
        rule.rule_id,
        rule.target_table_id,
        rule.target_field_id,
        identity,
        observed,
        expected,
        reason,
    )


def _single_result(
    rule: ValidationRuleDefinition,
    outcome: ValidationOutcome,
    code: str,
    message: str,
    reason: str,
    namespace: str | None,
) -> ValidationExecutionResult:
    expected = (
        _expected_contract(rule, namespace)
        if namespace is not None
        else "bound namespace and qualified-reference predicate"
    )
    diagnostic = _diagnostic(
        rule, code, message, reason, None, None, expected
    )
    return ValidationExecutionResult(
        rule.rule_id,
        outcome,
        (diagnostic,),
        0,
        0 if outcome is ValidationOutcome.UNSUPPORTED else 1,
    )


def _is_scalar(value: object) -> bool:
    return value is None or type(value) in {bool, int, str}


__all__ = [
    "VALIDATION_QUALIFIED_REFERENCE_INVARIANT_FAILED",
    "VALIDATION_QUALIFIED_REFERENCE_RESOLUTION_INVALID",
    "VALIDATION_QUALIFIED_REFERENCE_TARGET_RECORD_INVALID",
    "VALIDATION_QUALIFIED_REFERENCE_TARGET_TABLE_MISSING",
    "execute_qualified_reference_match_rule",
]
