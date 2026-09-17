"""Execution boundary for allowlisted definition-invariant rule shapes."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

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
        Binding,
        Call,
        Identifier,
        ListLiteral,
        Literal,
        MemberAccess,
        Sequence,
        UnaryOperation,
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
        Binding,
        Call,
        Identifier,
        ListLiteral,
        Literal,
        MemberAccess,
        Sequence,
        UnaryOperation,
    )
    from canonical_validation_expr_eval import (
        ValidationExpressionEvaluationError,
        ValidationExpressionUnsupportedError,
        evaluate_validation_expression,
    )
    from canonical_validation_rules import ValidationRuleDefinition


VALIDATION_DEFINITION_INVARIANT_FAILED = (
    "VALIDATION_DEFINITION_INVARIANT_FAILED"
)
VALIDATION_DEFINITION_TARGET_RECORD_INVALID = (
    "VALIDATION_DEFINITION_TARGET_RECORD_INVALID"
)
VALIDATION_DEFINITION_TARGET_TABLE_MISSING = (
    "VALIDATION_DEFINITION_TARGET_TABLE_MISSING"
)
VALIDATION_DEFINITION_LOOKUP_INVALID = (
    "VALIDATION_DEFINITION_LOOKUP_INVALID"
)

_BINARY_OPERATORS = frozenset(
    {"==", "!=", "<", ">", ">=", "and", "or", "in"}
)
_UNARY_OPERATORS = frozenset({"not"})
_COMPOUND_WHEN_UNARY_OPERATORS = frozenset()
_COMPOUND_WHEN_BINARY_OPERATORS = _BINARY_OPERATORS | {"not in"}
_SCALAR_SCHEMA_TYPES = frozenset(
    {"boolean", "date", "integer", "language_tag", "string", "text"}
)
_B3_BINARY_OPERATORS = frozenset({"==", "!=", "and", "or", "in"})
_BOOLEAN_CARDINALITY_BUILTINS = frozenset(
    {"at_least_one_non_null", "at_most_one_non_null"}
)
_DOMAIN_PRIMITIVE_ARITIES = {
    "group_of": 1,
    "normalize": 3,
    "normalize_search_name_hu": 1,
    "template_argument_value_type_valid": 7,
    "template_binding_shape_valid": 4,
    "template_binding_value_type_valid": 8,
}
_DOMAIN_PRIMITIVE_BUILTINS = frozenset(_DOMAIN_PRIMITIVE_ARITIES)
_TABLE_COUNT_BINARY_OPERATORS = _BINARY_OPERATORS | {"not in"}
_LOOKUP_EXACT = "EXACT"
_LOOKUP_ZERO = "ZERO"
_RESERVED_BINDING_NAMES = frozenset({"current"})
_TYPED_CONTRACT_TABLES = frozenset(
    {
        "registry:contract_fields",
        "registry:schema_fields",
        "registry:schema_tables",
        "carddatabase:schema_fields",
        "carddatabase:schema_tables",
    }
)


@dataclass(frozen=True, slots=True)
class _ScalarLookupDomain:
    source_namespace: str
    namespace: str
    table_id: str
    key_field_name: str
    output_field_name: str
    key_schema: FrozenRecord
    output_schema: FrozenRecord
    records: tuple[FrozenRecord, ...]


@dataclass(frozen=True, slots=True)
class _ScalarLookupResolution:
    state: str
    value: CanonicalScalar
    namespace: str
    table_id: str
    key_field_name: str
    output_field_name: str
    matched_record_identity: str | None = None


@dataclass(frozen=True, slots=True)
class _RecordLookupDomain:
    source_namespace: str
    namespace: str
    table_id: str
    key_field_name: str
    key_schema: FrozenRecord
    primary_key_name: str
    records: tuple[FrozenRecord, ...]


@dataclass(frozen=True, slots=True)
class _RecordLookupResolution:
    state: str
    value: FrozenRecord | None
    namespace: str
    table_id: str
    key_field_name: str
    matched_record_identity: str | None = None


@dataclass(frozen=True, slots=True)
class _CompositeRecordLookupDomain:
    source_namespace: str
    namespace: str
    table_id: str
    key_fields: tuple[tuple[str, FrozenRecord], ...]
    primary_key_name: str
    records: tuple[FrozenRecord, ...]


@dataclass(frozen=True, slots=True)
class _CountTableDomain:
    source_namespace: str
    namespace: str
    table_id: str
    field_contracts: tuple[tuple[str, FrozenRecord], ...]
    primary_key_name: str
    records: tuple[FrozenRecord, ...]


class _ScalarLookupFailure(ValueError):
    def __init__(
        self,
        reason: str,
        *,
        source_namespace: str,
        namespace: str | None,
        table_id: str,
        key_field_name: str,
        key_value: CanonicalScalar,
        output_field_name: str,
        related_record_identities: tuple[str, ...] = (),
        unsupported: bool = False,
    ) -> None:
        self.reason = reason
        self.source_namespace = source_namespace
        self.namespace = namespace
        self.table_id = table_id
        self.key_field_name = key_field_name
        self.key_value = key_value
        self.output_field_name = output_field_name
        self.related_record_identities = related_record_identities
        self.unsupported = unsupported
        super().__init__(reason)


def execute_definition_invariant_rule(
    rule: ValidationRuleDefinition,
    data: ValidationDataContext,
) -> ValidationExecutionResult:
    """Execute one allowlisted definition-invariant row predicate."""

    if not isinstance(rule, ValidationRuleDefinition):
        raise TypeError("rule must be a ValidationRuleDefinition")
    if not isinstance(data, ValidationDataContext):
        raise TypeError("data must be a ValidationDataContext")

    unsupported_reason = _definition_contract_reason(rule)
    if unsupported_reason is not None:
        return _single_result(
            rule,
            ValidationOutcome.UNSUPPORTED,
            VALIDATION_EXECUTOR_UNSUPPORTED,
            "The definition-invariant rule shape is not supported.",
            unsupported_reason,
            None,
        )

    namespace = data.namespace_for_component(rule.component_identity)
    if namespace is None:
        return _single_result(
            rule,
            ValidationOutcome.FAIL,
            VALIDATION_DEFINITION_TARGET_TABLE_MISSING,
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
            VALIDATION_DEFINITION_TARGET_TABLE_MISSING,
            "The active target-table schema could not be resolved.",
            "target_table_schema_unresolved",
            namespace,
        )

    assert rule.condition_ast is not None
    binding_collision = _source_field_binding_collision(
        rule.condition_ast, data, namespace, rule.target_table_id
    )
    if binding_collision is not None:
        return _single_result(
            rule,
            ValidationOutcome.UNSUPPORTED,
            VALIDATION_EXECUTOR_UNSUPPORTED,
            "A local binding collides with an active source field.",
            f"binding_name_collides_with_source_field:{binding_collision}",
            namespace,
        )
    identifiers = tuple(
        sorted(_outer_identifier_names(rule.condition_ast), key=_utf8)
    )
    field_contracts: list[tuple[str, FrozenRecord]] = []
    for identifier in identifiers:
        field_schema = _resolve_field_schema(
            data,
            rule.target_table_id,
            field_name=identifier,
            namespace=namespace,
        )
        if field_schema is None:
            return _single_result(
                rule,
                ValidationOutcome.FAIL,
                VALIDATION_DEFINITION_TARGET_RECORD_INVALID,
                "An expression identifier has no unique active target field.",
                f"identifier_field_schema_unresolved:{identifier}",
                namespace,
            )
        schema_reason = _field_schema_reason(field_schema)
        if schema_reason is not None:
            return _single_result(
                rule,
                ValidationOutcome.UNSUPPORTED,
                VALIDATION_EXECUTOR_UNSUPPORTED,
                "An expression identifier uses an unsupported schema type.",
                f"{schema_reason}:{identifier}",
                namespace,
            )
        field_contracts.append((identifier, field_schema))

    try:
        lookup_domains = _prepare_lookup_domains(
            rule.condition_ast, data, namespace
        )
        record_lookup_domains = _prepare_record_lookup_domains(
            rule.condition_ast, data, namespace
        )
        composite_record_lookup_domains = (
            _prepare_composite_record_lookup_domains(
                rule.condition_ast, data, namespace
            )
        )
        count_domains = _prepare_count_domains(
            rule.condition_ast, data, namespace
        )
        typed_contract_calls = any(
            _call_nodes(rule.condition_ast, builtin)
            for builtin in (
                "template_argument_value_type_valid",
                "template_binding_value_type_valid",
            )
        )
        registry_group_domain = (
            _prepare_registry_group_domain(data, namespace)
            if _call_nodes(rule.condition_ast, "group_of")
            or typed_contract_calls
            else None
        )
    except _ScalarLookupFailure as error:
        if error.unsupported:
            return _single_result(
                rule,
                ValidationOutcome.UNSUPPORTED,
                VALIDATION_EXECUTOR_UNSUPPORTED,
                "The scalar lookup contract is outside B3.",
                error.reason,
                namespace,
            )
        return _lookup_failure_result(rule, error, None, 0)

    target_records = _resolve_table(
        data, rule.target_table_id, namespace=namespace
    )
    if target_records is None:
        return _single_result(
            rule,
            ValidationOutcome.FAIL,
            VALIDATION_DEFINITION_TARGET_TABLE_MISSING,
            "The target table is missing from the source namespace.",
            "target_table_missing",
            namespace,
        )

    expected = _expected_contract(rule, namespace)
    diagnostics: list[ValidationExecutionDiagnostic] = []
    for record in sorted(
        target_records, key=lambda item: _record_sort_key(item, primary_key)
    ):
        identity = _safe_record_identity(record, primary_key)
        if not _valid_identity(record, primary_key):
            diagnostics.append(
                _diagnostic(
                    rule,
                    VALIDATION_DEFINITION_TARGET_RECORD_INVALID,
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
                    VALIDATION_DEFINITION_TARGET_RECORD_INVALID,
                    "The target record does not satisfy its active field schema.",
                    reason,
                    identity,
                    observed,
                    expected,
                )
            )
            continue

        try:
            evaluation_options = {}
            if lookup_domains:
                evaluation_options["lookup_resolver"] = (
                    lambda table, key, value, output: (
                        _resolve_scalar_lookup(
                            lookup_domains[(table, key, output)],
                            _project_explicit_namespace_key(
                                lookup_domains[(table, key, output)],
                                value,
                            ),
                        ).value
                    )
                )
            if record_lookup_domains:
                evaluation_options["record_lookup_resolver"] = (
                    lambda table, key, value: (
                        _resolve_record_lookup(
                            record_lookup_domains[(table, key)], value
                        ).value
                    )
                )
            if composite_record_lookup_domains:
                evaluation_options["record_lookup_by_resolver"] = (
                    lambda table, keys, values: (
                        _resolve_composite_record_lookup(
                            composite_record_lookup_domains[(table, keys)],
                            values,
                        ).value
                    )
                )
            if _call_nodes(rule.condition_ast, "current_schema_version"):
                evaluation_options["schema_version_resolver"] = (
                    lambda component_id: _resolve_component_schema_version(
                        data, component_id
                    )
                )
            if count_domains or typed_contract_calls:
                evaluation_options["table_resolver"] = (
                    lambda table: (
                        _validated_count_records(count_domains[table])
                        if table in count_domains
                        else _resolve_typed_contract_table(data, table)
                        if typed_contract_calls
                        else None
                    )
                )
            if count_domains:
                environment["current"] = record
            if registry_group_domain is not None:
                evaluation_options["registry_group_resolver"] = (
                    lambda registry_value_id: _resolve_scalar_lookup(
                        registry_group_domain, registry_value_id
                    ).value
                )
            result = evaluate_validation_expression(
                rule.condition_ast,
                environment,
                **evaluation_options,
            )
        except _ScalarLookupFailure as error:
            diagnostics.append(
                _lookup_diagnostic(rule, error, identity)
            )
            continue
        except ValidationExpressionUnsupportedError as error:
            raise RuntimeError(
                "The statically accepted definition expression became unsupported."
            ) from error
        except ValidationExpressionEvaluationError as error:
            reason = dict(error.context).get("reason", "evaluation_error")
            diagnostics.append(
                _diagnostic(
                    rule,
                    VALIDATION_DEFINITION_TARGET_RECORD_INVALID,
                    "The direct row predicate could not be evaluated.",
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
                    VALIDATION_DEFINITION_TARGET_RECORD_INVALID,
                    "The direct row predicate did not produce an exact boolean.",
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
                    VALIDATION_DEFINITION_INVARIANT_FAILED,
                    "The canonical record violates the definition invariant.",
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


def _definition_contract_reason(
    rule: ValidationRuleDefinition,
) -> str | None:
    if rule.validation_kind_id != "definition_invariant":
        return "validation_kind_not_definition_invariant"
    if rule.validation_stage_id != "pre_export":
        return "validation_stage_not_pre_export"
    if rule.rule_scope_id != "record":
        return "rule_scope_not_record"
    if (
        type(rule.condition_expression_source) is not str
        or not rule.condition_expression_source
        or rule.condition_ast is None
        or type(rule.condition_ast_hash) is not str
        or not rule.condition_ast_hash
    ):
        return "condition_expression_missing_or_invalid"
    return _ast_unsupported_reason(rule.condition_ast)


def _ast_unsupported_reason(node: object) -> str | None:
    if _is_supported_cardinality_shape(node):
        return None
    if _record_binding_unsupported_reason(node) is None:
        return None
    if _table_count_unsupported_reason(node) is None:
        return None
    if _domain_primitive_unsupported_reason(node) is None:
        return None
    if _binding_sequence_unsupported_reason(node) is None:
        return None
    direct_reason = _call_free_unsupported_reason(node)
    if direct_reason is None:
        return None
    guarded_reason = _guarded_equality_unsupported_reason(
        node, direct_reason
    )
    if guarded_reason is None:
        return None
    compound_reason = _guarded_compound_when_unsupported_reason(
        node, direct_reason
    )
    if compound_reason is None:
        return None
    sequence_reason = _sequence_when_unsupported_reason(node, direct_reason)
    if sequence_reason is None:
        return None
    if _b3_unsupported_reason(node) is None:
        return None
    return sequence_reason if isinstance(node, Sequence) else compound_reason


def _record_binding_unsupported_reason(node: object) -> str | None:
    if isinstance(node, Sequence):
        return _record_binding_sequence_unsupported_reason(node)
    if not (
        isinstance(node, Call)
        and node.function == "when"
        and len(node.arguments) == 2
    ):
        return "record_binding_root_not_supported"
    guard, constraint = node.arguments
    guard_reason = _call_free_unsupported_reason(guard)
    if guard_reason is not None:
        return f"record_binding_guard_{guard_reason}"
    if not isinstance(constraint, Sequence):
        return "record_binding_constraint_not_sequence"
    return _record_binding_sequence_unsupported_reason(constraint)


def _table_count_unsupported_reason(node: object) -> str | None:
    if not _call_nodes(node, "count"):
        return "count_missing"
    return _table_count_node_reason(
        node,
        record_names=frozenset(),
        in_count_predicate=False,
        top_level=True,
    )


def _domain_primitive_unsupported_reason(node: object) -> str | None:
    if not any(
        _call_nodes(node, builtin)
        for builtin in _DOMAIN_PRIMITIVE_BUILTINS
    ):
        return "domain_primitive_missing"
    return _domain_primitive_node_reason(node, top_level=True)


def _domain_primitive_node_reason(
    node: object, *, top_level: bool = False
) -> str | None:
    if isinstance(node, (Literal, Identifier)):
        return None
    if isinstance(node, ListLiteral):
        return next(
            (
                reason
                for item in node.items
                if (
                    reason := _domain_primitive_node_reason(item)
                )
                is not None
            ),
            None,
        )
    if isinstance(node, UnaryOperation):
        if node.operator not in _UNARY_OPERATORS:
            return f"operator_not_supported:{node.operator}"
        return _domain_primitive_node_reason(node.operand)
    if isinstance(node, BinaryOperation):
        if node.operator not in _BINARY_OPERATORS:
            return f"operator_not_supported:{node.operator}"
        return _domain_primitive_node_reason(
            node.left
        ) or _domain_primitive_node_reason(node.right)
    if isinstance(node, Sequence):
        if not top_level:
            return "domain_primitive_sequence_not_top_level"
        if not node.statements:
            return "domain_primitive_sequence_empty"
        binding_names = tuple(
            statement.name
            for statement in node.statements
            if isinstance(statement, Binding)
        )
        if any(
            type(name) is not str
            or not name
            or name in _RESERVED_BINDING_NAMES
            for name in binding_names
        ):
            return "domain_primitive_binding_name_invalid"
        if len(set(binding_names)) != len(binding_names):
            return "domain_primitive_binding_name_rebound"
        future = set(binding_names)
        predicate_seen = False
        for statement in node.statements:
            if isinstance(statement, Binding):
                if predicate_seen:
                    return "domain_primitive_binding_after_predicate"
                if _identifier_names(statement.value) & future:
                    return "domain_primitive_binding_forward_reference"
                reason = _domain_primitive_node_reason(statement.value)
                if reason is not None:
                    return f"domain_primitive_binding_rhs_{reason}"
                future.remove(statement.name)
                continue
            predicate_seen = True
            reason = _domain_primitive_node_reason(statement)
            if reason is not None:
                return reason
        return (
            None
            if predicate_seen
            else "domain_primitive_boolean_statement_missing"
        )
    if not isinstance(node, Call):
        return f"node_not_supported:{type(node).__name__}"
    if node.function == "when":
        if not top_level:
            return "domain_primitive_when_not_top_level"
        if len(node.arguments) != 2:
            return "domain_primitive_when_arity_not_supported"
        return _domain_primitive_node_reason(
            node.arguments[0]
        ) or _domain_primitive_node_reason(node.arguments[1])
    if node.function == "lookup":
        return _scalar_binding_rhs_unsupported_reason(node)
    if node.function not in _DOMAIN_PRIMITIVE_BUILTINS:
        return f"builtin_not_supported:{node.function}"
    expected_arity = _DOMAIN_PRIMITIVE_ARITIES[node.function]
    if len(node.arguments) != expected_arity:
        return f"{node.function}_arity_not_supported"
    return next(
        (
            reason
            for argument in node.arguments
            if (reason := _domain_primitive_node_reason(argument))
            is not None
        ),
        None,
    )


def _table_count_node_reason(
    node: object,
    *,
    record_names: frozenset[str],
    in_count_predicate: bool,
    top_level: bool = False,
) -> str | None:
    if isinstance(node, Literal):
        return None
    if isinstance(node, Identifier):
        if in_count_predicate and node.name == "current":
            return "current_record_requires_member"
        return None
    if isinstance(node, ListLiteral):
        return next(
            (
                reason
                for item in node.items
                if (
                    reason := _table_count_node_reason(
                        item,
                        record_names=record_names,
                        in_count_predicate=in_count_predicate,
                    )
                )
                is not None
            ),
            None,
        )
    if isinstance(node, UnaryOperation):
        if node.operator not in _UNARY_OPERATORS:
            return f"operator_not_supported:{node.operator}"
        return _table_count_node_reason(
            node.operand,
            record_names=record_names,
            in_count_predicate=in_count_predicate,
        )
    if isinstance(node, MemberAccess):
        if not isinstance(node.target, Identifier):
            return "nested_member_access_not_supported"
        if type(node.member) is not str or not node.member:
            return "member_name_invalid"
        if in_count_predicate and node.target.name == "current":
            return None
        if node.target.name in record_names:
            return None
        return "member_base_not_supported"
    if isinstance(node, BinaryOperation):
        if node.operator not in _TABLE_COUNT_BINARY_OPERATORS:
            return f"operator_not_supported:{node.operator}"
        raw_record_left = (
            isinstance(node.left, Identifier)
            and node.left.name in record_names
        )
        raw_record_right = (
            isinstance(node.right, Identifier)
            and node.right.name in record_names
        )
        if raw_record_left or raw_record_right:
            other = node.right if raw_record_left else node.left
            if not (
                raw_record_left != raw_record_right
                and node.operator in {"==", "!="}
                and isinstance(other, Literal)
                and other.literal_kind == "null"
                and other.value is None
            ):
                return "record_value_comparison_not_supported"
        return _table_count_node_reason(
            node.left,
            record_names=record_names,
            in_count_predicate=in_count_predicate,
        ) or _table_count_node_reason(
            node.right,
            record_names=record_names,
            in_count_predicate=in_count_predicate,
        )
    if isinstance(node, Sequence):
        if in_count_predicate:
            return "count_predicate_sequence_not_supported"
        if not node.statements:
            return "count_sequence_empty"
        local_records = set(record_names)
        local_names: set[str] = set()
        future_names = {
            statement.name
            for statement in node.statements
            if isinstance(statement, Binding)
        }
        predicate_seen = False
        for statement in node.statements:
            if isinstance(statement, Binding):
                if predicate_seen:
                    return "count_binding_after_predicate"
                if (
                    type(statement.name) is not str
                    or not statement.name
                    or statement.name in _RESERVED_BINDING_NAMES
                    or statement.name in local_names
                ):
                    return "count_binding_name_invalid"
                if _identifier_names(statement.value) & future_names:
                    return "count_binding_forward_or_self_reference"
                if (
                    isinstance(statement.value, Call)
                    and statement.value.function == "lookup_record"
                ):
                    reason = _record_lookup_rhs_unsupported_reason(
                        statement.value, frozenset(local_records)
                    )
                    if reason is None:
                        local_records.add(statement.name)
                else:
                    reason = _scalar_binding_rhs_unsupported_reason(
                        statement.value
                    )
                if reason is not None:
                    return f"count_binding_rhs_{reason}"
                local_names.add(statement.name)
                future_names.remove(statement.name)
                continue
            predicate_seen = True
            reason = _table_count_node_reason(
                statement,
                record_names=frozenset(local_records),
                in_count_predicate=False,
            )
            if reason is not None:
                return reason
        return None if predicate_seen else "count_sequence_predicate_missing"
    if not isinstance(node, Call):
        return f"node_not_supported:{type(node).__name__}"
    if node.function == "when":
        if not top_level or in_count_predicate:
            return "when_position_not_supported"
        if len(node.arguments) != 2:
            return "when_arity_not_supported"
        return _table_count_node_reason(
            node.arguments[0],
            record_names=record_names,
            in_count_predicate=False,
        ) or _table_count_node_reason(
            node.arguments[1],
            record_names=record_names,
            in_count_predicate=False,
        )
    if node.function == "count":
        if in_count_predicate:
            return "nested_count_not_supported"
        if len(node.arguments) != 2:
            return "count_arity_not_supported"
        table = node.arguments[0]
        if not (
            isinstance(table, Literal)
            and table.literal_kind == "string"
            and type(table.value) is str
            and bool(table.value)
        ):
            return "count_table_token_not_string_literal"
        return _table_count_node_reason(
            node.arguments[1],
            record_names=record_names,
            in_count_predicate=True,
        )
    if node.function == "lookup":
        reason = _scalar_binding_rhs_unsupported_reason(node)
        return None if reason is None else f"count_{reason}"
    if node.function == "normalize":
        if len(node.arguments) != 3:
            return "normalize_arity_not_supported"
        return next(
            (
                reason
                for argument in node.arguments
                if (
                    reason := _table_count_node_reason(
                        argument,
                        record_names=record_names,
                        in_count_predicate=in_count_predicate,
                    )
                )
                is not None
            ),
            None,
        )
    return f"builtin_not_supported:{node.function}"


def _record_binding_sequence_unsupported_reason(
    node: Sequence,
) -> str | None:
    if not node.statements:
        return "record_binding_sequence_empty"
    bindings = tuple(
        statement for statement in node.statements
        if isinstance(statement, Binding)
    )
    if not bindings:
        return "record_binding_missing"
    names = tuple(binding.name for binding in bindings)
    if any(type(name) is not str or not name for name in names):
        return "record_binding_name_invalid"
    if any(name in _RESERVED_BINDING_NAMES for name in names):
        return "record_binding_name_reserved"
    if len(set(names)) != len(names):
        return "record_binding_name_rebound"

    future = set(names)
    record_names: set[str] = set()
    predicate_seen = False
    record_binding_seen = False
    for statement in node.statements:
        if isinstance(statement, Binding):
            if predicate_seen:
                return "record_binding_after_boolean_statement"
            if _identifier_names(statement.value) & future:
                return "record_binding_forward_reference"
            if isinstance(statement.value, Call) and statement.value.function in {
                "lookup_record",
                "lookup_record_by",
            }:
                reason = (
                    _record_lookup_rhs_unsupported_reason(
                        statement.value, frozenset(record_names)
                    )
                    if statement.value.function == "lookup_record"
                    else _record_lookup_by_rhs_unsupported_reason(
                        statement.value, frozenset(record_names)
                    )
                )
                record_binding_seen = True
                record_names.add(statement.name)
            else:
                reason = _record_sequence_scalar_rhs_unsupported_reason(
                    statement.value, frozenset(record_names)
                )
            if reason is not None:
                return f"record_binding_rhs_{reason}"
            future.remove(statement.name)
            continue

        predicate_seen = True
        reason = _record_predicate_unsupported_reason(
            statement, frozenset(record_names)
        )
        if reason is not None:
            return f"record_binding_predicate_{reason}"

    if not record_binding_seen:
        return "record_binding_lookup_missing"
    if not predicate_seen:
        return "record_binding_boolean_statement_missing"
    return None


def _record_lookup_rhs_unsupported_reason(
    node: Call, record_names: frozenset[str]
) -> str | None:
    if len(node.arguments) != 3:
        return "lookup_record_arity_not_supported"
    for index in (0, 1):
        argument = node.arguments[index]
        if not (
            isinstance(argument, Literal)
            and argument.literal_kind == "string"
            and type(argument.value) is str
            and bool(argument.value)
        ):
            return f"lookup_record_token_not_string_literal:{index}"
    key = node.arguments[2]
    if isinstance(key, (Literal, Identifier)):
        return None
    if isinstance(key, MemberAccess):
        return _record_member_unsupported_reason(key, record_names)
    return f"lookup_record_key_not_scalar:{type(key).__name__}"


def _record_lookup_by_rhs_unsupported_reason(
    node: Call, record_names: frozenset[str]
) -> str | None:
    if len(node.arguments) != 3:
        return "lookup_record_by_arity_not_supported"
    table, key_fields, key_values = node.arguments
    if not (
        isinstance(table, Literal)
        and table.literal_kind == "string"
        and type(table.value) is str
        and bool(table.value)
    ):
        return "lookup_record_by_table_token_not_string_literal"
    values = key_values.items if isinstance(key_values, ListLiteral) else (
        key_values,
    )
    for value in values:
        if isinstance(value, (Literal, Identifier)):
            continue
        if isinstance(value, MemberAccess):
            reason = _record_member_unsupported_reason(value, record_names)
            if reason is not None:
                return f"lookup_record_by_key_value_{reason}"
            continue
        if isinstance(value, ListLiteral):
            continue
        return (
            "lookup_record_by_key_value_not_scalar:"
            f"{type(value).__name__}"
        )
    return None


def _record_sequence_scalar_rhs_unsupported_reason(
    node: object, record_names: frozenset[str]
) -> str | None:
    if (
        isinstance(node, Call)
        and node.function == "count_non_null"
        and _is_canonical_cardinality_call(node)
    ):
        if any(
            isinstance(item, Identifier) and item.name in record_names
            for item in node.arguments[0].items
        ):
            return "cardinality_record_item_not_supported"
        return None
    return _scalar_binding_rhs_unsupported_reason(node)


def _record_predicate_unsupported_reason(
    node: object, record_names: frozenset[str]
) -> str | None:
    if isinstance(node, (Literal, Identifier)):
        return None
    if isinstance(node, MemberAccess):
        return _record_member_unsupported_reason(node, record_names)
    if isinstance(node, ListLiteral):
        return next(
            (
                reason
                for item in node.items
                if (
                    reason := _record_predicate_unsupported_reason(
                        item, record_names
                    )
                )
                is not None
            ),
            None,
        )
    if isinstance(node, UnaryOperation):
        if node.operator not in _UNARY_OPERATORS:
            return f"operator_not_supported:{node.operator}"
        return _record_predicate_unsupported_reason(
            node.operand, record_names
        )
    if isinstance(node, Call):
        if node.function == "lookup":
            return _record_scalar_lookup_unsupported_reason(
                node, record_names
            )
        return _version_gte_unsupported_reason(node, record_names)
    if not isinstance(node, BinaryOperation):
        return f"node_not_supported:{type(node).__name__}"
    if node.operator not in _BINARY_OPERATORS:
        return f"operator_not_supported:{node.operator}"
    raw_record_left = (
        isinstance(node.left, Identifier)
        and node.left.name in record_names
    )
    raw_record_right = (
        isinstance(node.right, Identifier)
        and node.right.name in record_names
    )
    if raw_record_left or raw_record_right:
        other = node.right if raw_record_left else node.left
        if not (
            raw_record_left != raw_record_right
            and node.operator in {"==", "!="}
            and isinstance(other, Literal)
            and other.literal_kind == "null"
            and other.value is None
        ):
            return "record_value_comparison_not_supported"
    return _record_predicate_unsupported_reason(
        node.left, record_names
    ) or _record_predicate_unsupported_reason(node.right, record_names)


def _version_gte_unsupported_reason(
    node: Call, record_names: frozenset[str]
) -> str | None:
    if node.function != "version_gte":
        return f"builtin_not_supported:{node.function}"
    if len(node.arguments) != 2:
        return "version_gte_arity_not_supported"
    for index, argument in enumerate(node.arguments):
        reason = _version_value_unsupported_reason(argument, record_names)
        if reason is not None:
            return f"version_gte_argument_{index}_{reason}"
    return None


def _record_scalar_lookup_unsupported_reason(
    node: Call, record_names: frozenset[str]
) -> str | None:
    if len(node.arguments) != 4:
        return "lookup_arity_not_supported"
    for index in (0, 1, 3):
        argument = node.arguments[index]
        if not (
            isinstance(argument, Literal)
            and argument.literal_kind == "string"
            and type(argument.value) is str
            and bool(argument.value)
        ):
            return f"lookup_token_not_string_literal:{index}"
    key = node.arguments[2]
    if isinstance(key, (Literal, Identifier)):
        return None
    if isinstance(key, MemberAccess):
        return _record_member_unsupported_reason(key, record_names)
    return f"lookup_key_not_scalar:{type(key).__name__}"


def _version_value_unsupported_reason(
    node: object, record_names: frozenset[str]
) -> str | None:
    if isinstance(node, Literal):
        return None if (
            node.literal_kind == "string"
            and type(node.value) is str
            and bool(node.value)
        ) else "literal_not_string"
    if isinstance(node, Identifier):
        return (
            "record_value_not_scalar"
            if node.name in record_names
            else None
        )
    if isinstance(node, MemberAccess):
        return _record_member_unsupported_reason(node, record_names)
    if not isinstance(node, Call):
        return f"node_not_supported:{type(node).__name__}"
    if node.function != "current_schema_version":
        return f"builtin_not_supported:{node.function}"
    if len(node.arguments) != 1:
        return "current_schema_version_arity_not_supported"
    component = node.arguments[0]
    if not (
        isinstance(component, Literal)
        and component.literal_kind == "string"
        and type(component.value) is str
        and bool(component.value)
    ):
        return "current_schema_version_component_not_string_literal"
    return None


def _record_member_unsupported_reason(
    node: MemberAccess, record_names: frozenset[str]
) -> str | None:
    if not isinstance(node.target, Identifier):
        return "nested_member_access_not_supported"
    if node.target.name not in record_names:
        return "member_base_not_record_binding"
    if type(node.member) is not str or not node.member:
        return "member_name_invalid"
    return None


def _binding_sequence_unsupported_reason(node: object) -> str | None:
    if not isinstance(node, Sequence):
        return "binding_root_not_sequence"
    if not node.statements:
        return "binding_sequence_empty"

    bindings = tuple(
        statement for statement in node.statements
        if isinstance(statement, Binding)
    )
    if not bindings:
        return "binding_missing"

    binding_names = tuple(binding.name for binding in bindings)
    if any(type(name) is not str or not name for name in binding_names):
        return "binding_name_invalid"
    if any(name in _RESERVED_BINDING_NAMES for name in binding_names):
        return "binding_name_reserved"
    if len(set(binding_names)) != len(binding_names):
        return "binding_name_rebound"

    future = set(binding_names)
    predicate_seen = False
    for statement in node.statements:
        if isinstance(statement, Binding):
            if predicate_seen:
                return "binding_after_boolean_statement"
            if _identifier_names(statement.value) & future:
                return "binding_forward_reference"
            rhs_reason = _scalar_binding_rhs_unsupported_reason(
                statement.value
            )
            if rhs_reason is not None:
                return f"binding_rhs_{rhs_reason}"
            future.remove(statement.name)
            continue

        predicate_seen = True
        reason = _call_free_unsupported_reason(statement)
        if reason is not None:
            return f"binding_predicate_{reason}"

    if not predicate_seen:
        return "binding_boolean_statement_missing"
    return None


def _scalar_binding_rhs_unsupported_reason(node: object) -> str | None:
    if isinstance(node, Literal):
        expected_types = {
            "null": type(None),
            "boolean": bool,
            "integer": int,
            "string": str,
        }
        expected_type = expected_types.get(node.literal_kind)
        if expected_type is None or type(node.value) is not expected_type:
            return "literal_invalid"
        return None
    if isinstance(node, Identifier):
        return None
    if not isinstance(node, Call):
        return f"node_not_supported:{type(node).__name__}"
    if node.function != "lookup":
        return f"builtin_not_supported:{node.function}"
    if len(node.arguments) != 4:
        return "lookup_arity_not_supported"
    for index in (0, 1, 3):
        argument = node.arguments[index]
        if not (
            isinstance(argument, Literal)
            and argument.literal_kind == "string"
            and type(argument.value) is str
            and bool(argument.value)
        ):
            return f"lookup_token_not_string_literal:{index}"
    return _scalar_binding_rhs_unsupported_reason(node.arguments[2])


def _is_supported_cardinality_shape(node: object) -> bool:
    if (
        isinstance(node, Call)
        and node.function in _BOOLEAN_CARDINALITY_BUILTINS
    ):
        return _is_canonical_cardinality_call(node)
    if isinstance(node, BinaryOperation):
        return (
            node.operator == "=="
            and isinstance(node.left, Call)
            and node.left.function == "count_non_null"
            and _is_canonical_cardinality_call(node.left)
            and isinstance(node.right, Literal)
            and node.right.literal_kind == "integer"
            and type(node.right.value) is int
            and node.right.value == 1
        )
    if not (
        isinstance(node, Call)
        and node.function == "when"
        and len(node.arguments) == 2
    ):
        return False
    guard, constraint = node.arguments
    return (
        isinstance(guard, Call)
        and guard.function == "at_least_one_non_null"
        and _is_canonical_cardinality_call(guard)
        and _equality_constraint_reason(constraint) is None
    )


def _is_canonical_cardinality_call(node: Call) -> bool:
    return (
        len(node.arguments) == 1
        and isinstance(node.arguments[0], ListLiteral)
        and all(
            isinstance(item, (Identifier, Literal))
            for item in node.arguments[0].items
        )
    )


def _guarded_equality_unsupported_reason(
    node: object, direct_reason: str
) -> str | None:
    if not isinstance(node, Call):
        return direct_reason
    if node.function != "when":
        return f"builtin_not_supported:{node.function}"
    if len(node.arguments) != 2:
        return "when_arity_not_supported"
    guard_reason = _call_free_unsupported_reason(node.arguments[0])
    if guard_reason is not None:
        return f"when_guard_{guard_reason}"
    return _equality_constraint_reason(node.arguments[1])


def _guarded_compound_when_unsupported_reason(
    node: object, direct_reason: str
) -> str | None:
    if not isinstance(node, Call):
        return direct_reason
    if node.function != "when":
        return f"builtin_not_supported:{node.function}"
    if len(node.arguments) != 2:
        return "when_arity_not_supported"
    for role, argument in zip(("guard", "constraint"), node.arguments):
        reason = _call_free_unsupported_reason(
            argument,
            binary_operators=_COMPOUND_WHEN_BINARY_OPERATORS,
            unary_operators=_COMPOUND_WHEN_UNARY_OPERATORS,
        )
        if reason is not None:
            return f"when_{role}_{reason}"
    return None


def _sequence_when_unsupported_reason(
    node: object, direct_reason: str
) -> str | None:
    if not isinstance(node, Sequence):
        return direct_reason
    if not node.statements:
        return "sequence_empty"
    for statement in node.statements:
        reason = _guarded_compound_when_unsupported_reason(
            statement,
            f"node_not_supported:{type(statement).__name__}",
        )
        if reason is not None:
            return direct_reason
    return None


def _b3_unsupported_reason(node: object) -> str | None:
    found_lookup = [False]
    reason = _b3_node_reason(node, node, found_lookup)
    if reason is not None:
        return reason
    return None if found_lookup[0] else "lookup_missing"


def _b3_node_reason(
    node: object, root: object, found_lookup: list[bool]
) -> str | None:
    if isinstance(node, (Literal, Identifier)):
        return None
    if isinstance(node, ListLiteral):
        return next(
            (
                reason
                for item in node.items
                if (
                    reason := _b3_node_reason(item, root, found_lookup)
                )
                is not None
            ),
            None,
        )
    if isinstance(node, BinaryOperation):
        if node.operator not in _B3_BINARY_OPERATORS:
            return f"b3_operator_not_supported:{node.operator}"
        return _b3_node_reason(
            node.left, root, found_lookup
        ) or _b3_node_reason(node.right, root, found_lookup)
    if not isinstance(node, Call):
        return f"b3_node_not_supported:{type(node).__name__}"
    if node.function == "when":
        if node is not root:
            return "b3_when_not_top_level"
        if len(node.arguments) != 2:
            return "b3_when_arity_not_supported"
        return _b3_node_reason(
            node.arguments[0], root, found_lookup
        ) or _b3_node_reason(node.arguments[1], root, found_lookup)
    if node.function != "lookup":
        return f"b3_builtin_not_supported:{node.function}"
    found_lookup[0] = True
    if len(node.arguments) != 4:
        return "b3_lookup_arity_not_supported"
    for index in (0, 1, 3):
        argument = node.arguments[index]
        if not (
            isinstance(argument, Literal)
            and argument.literal_kind == "string"
            and type(argument.value) is str
            and bool(argument.value)
        ):
            return f"b3_lookup_token_not_string_literal:{index}"
    return _b3_node_reason(node.arguments[2], root, found_lookup)


def _call_free_unsupported_reason(
    node: object,
    *,
    binary_operators: frozenset[str] = _BINARY_OPERATORS,
    unary_operators: frozenset[str] = _UNARY_OPERATORS,
) -> str | None:
    if isinstance(node, (Literal, Identifier)):
        return None
    if isinstance(node, ListLiteral):
        return next(
            (
                reason
                for item in node.items
                if (
                    reason := _call_free_unsupported_reason(
                        item,
                        binary_operators=binary_operators,
                        unary_operators=unary_operators,
                    )
                )
                is not None
            ),
            None,
        )
    if isinstance(node, UnaryOperation):
        if node.operator not in unary_operators:
            return f"operator_not_supported:{node.operator}"
        return _call_free_unsupported_reason(
            node.operand,
            binary_operators=binary_operators,
            unary_operators=unary_operators,
        )
    if isinstance(node, BinaryOperation):
        if node.operator not in binary_operators:
            return f"operator_not_supported:{node.operator}"
        return _call_free_unsupported_reason(
            node.left,
            binary_operators=binary_operators,
            unary_operators=unary_operators,
        ) or _call_free_unsupported_reason(
            node.right,
            binary_operators=binary_operators,
            unary_operators=unary_operators,
        )
    return f"node_not_supported:{type(node).__name__}"


def _equality_constraint_reason(node: object) -> str | None:
    if not isinstance(node, BinaryOperation):
        return "when_constraint_not_equality"
    if node.operator not in {"==", "!="}:
        return f"when_constraint_operator_not_supported:{node.operator}"
    for operand in (node.left, node.right):
        if not isinstance(operand, (Identifier, Literal)):
            return (
                "when_constraint_operand_not_scalar:"
                f"{type(operand).__name__}"
            )
    return None


def _identifier_names(
    node: object, bound_names: frozenset[str] = frozenset()
) -> frozenset[str]:
    if isinstance(node, Identifier):
        return (
            frozenset()
            if node.name in bound_names
            else frozenset({node.name})
        )
    if isinstance(node, ListLiteral):
        return frozenset().union(
            *(_identifier_names(item, bound_names) for item in node.items)
        )
    if isinstance(node, UnaryOperation):
        return _identifier_names(node.operand, bound_names)
    if isinstance(node, BinaryOperation):
        return _identifier_names(
            node.left, bound_names
        ) | _identifier_names(node.right, bound_names)
    if isinstance(node, Call):
        return frozenset().union(
            *(
                _identifier_names(argument, bound_names)
                for argument in node.arguments
            )
        )
    if isinstance(node, MemberAccess):
        return _identifier_names(node.target, bound_names)
    if isinstance(node, Binding):
        return _identifier_names(node.value, bound_names)
    if isinstance(node, Sequence):
        identifiers: set[str] = set()
        local_names = set(bound_names)
        for statement in node.statements:
            identifiers.update(
                _identifier_names(statement, frozenset(local_names))
            )
            if isinstance(statement, Binding):
                local_names.add(statement.name)
        return frozenset(identifiers)
    return frozenset()


def _outer_identifier_names(
    node: object, bound_names: frozenset[str] = frozenset()
) -> frozenset[str]:
    if isinstance(node, Identifier):
        return (
            frozenset()
            if node.name in bound_names or node.name == "current"
            else frozenset({node.name})
        )
    if isinstance(node, ListLiteral):
        return frozenset().union(
            *(
                _outer_identifier_names(item, bound_names)
                for item in node.items
            )
        )
    if isinstance(node, UnaryOperation):
        return _outer_identifier_names(node.operand, bound_names)
    if isinstance(node, BinaryOperation):
        return _outer_identifier_names(
            node.left, bound_names
        ) | _outer_identifier_names(node.right, bound_names)
    if isinstance(node, Call):
        if node.function == "count" and len(node.arguments) == 2:
            return _count_outer_identifier_names(
                node.arguments[1], bound_names
            )
        return frozenset().union(
            *(
                _outer_identifier_names(argument, bound_names)
                for argument in node.arguments
            )
        )
    if isinstance(node, MemberAccess):
        if (
            isinstance(node.target, Identifier)
            and node.target.name == "current"
        ):
            return frozenset({node.member})
        return _outer_identifier_names(node.target, bound_names)
    if isinstance(node, Binding):
        return _outer_identifier_names(node.value, bound_names)
    if isinstance(node, Sequence):
        identifiers: set[str] = set()
        local_names = set(bound_names)
        for statement in node.statements:
            identifiers.update(
                _outer_identifier_names(
                    statement, frozenset(local_names)
                )
            )
            if isinstance(statement, Binding):
                local_names.add(statement.name)
        return frozenset(identifiers)
    return frozenset()


def _count_outer_identifier_names(
    node: object, bound_names: frozenset[str]
) -> frozenset[str]:
    if isinstance(node, (Literal, Identifier)):
        return frozenset()
    if isinstance(node, ListLiteral):
        return frozenset().union(
            *(
                _count_outer_identifier_names(item, bound_names)
                for item in node.items
            )
        )
    if isinstance(node, UnaryOperation):
        return _count_outer_identifier_names(node.operand, bound_names)
    if isinstance(node, BinaryOperation):
        return _count_outer_identifier_names(
            node.left, bound_names
        ) | _count_outer_identifier_names(node.right, bound_names)
    if isinstance(node, Call):
        return frozenset().union(
            *(
                _count_outer_identifier_names(argument, bound_names)
                for argument in node.arguments
            )
        )
    if isinstance(node, MemberAccess):
        if (
            isinstance(node.target, Identifier)
            and node.target.name == "current"
        ):
            return frozenset({node.member})
        return frozenset()
    return frozenset()


def _source_field_binding_collision(
    node: object,
    data: ValidationDataContext,
    namespace: str,
    target_table_id: str,
) -> str | None:
    sequences: tuple[Sequence, ...]
    if isinstance(node, Sequence):
        sequences = (node,)
    elif (
        isinstance(node, Call)
        and node.function == "when"
        and len(node.arguments) == 2
        and isinstance(node.arguments[1], Sequence)
    ):
        sequences = (node.arguments[1],)
    else:
        return None
    binding_names = {
        statement.name
        for sequence in sequences
        for statement in sequence.statements
        if isinstance(statement, Binding)
    }
    if not binding_names:
        return None
    schema = data.table("schema_fields", namespace=namespace)
    if schema is None:
        return None
    collisions = sorted(
        {
            field.get("field_name")
            for field in schema
            if field.get("table_id") == target_table_id
            and field.get("status") == "active"
            and field.get("field_name") in binding_names
        },
        key=_utf8,
    )
    return collisions[0] if collisions else None


def _prepare_lookup_domains(
    node: object,
    data: ValidationDataContext,
    source_namespace: str,
) -> dict[tuple[str, str, str], _ScalarLookupDomain]:
    domains: dict[tuple[str, str, str], _ScalarLookupDomain] = {}
    for lookup in _lookup_nodes(node):
        table = lookup.arguments[0]
        key = lookup.arguments[1]
        output = lookup.arguments[3]
        assert isinstance(table, Literal) and isinstance(table.value, str)
        assert isinstance(key, Literal) and isinstance(key.value, str)
        assert isinstance(output, Literal) and isinstance(output.value, str)
        domain_key = (table.value, key.value, output.value)
        if domain_key not in domains:
            domains[domain_key] = _resolve_lookup_domain(
                data,
                source_namespace,
                table.value,
                key.value,
                output.value,
            )
    return domains


def _prepare_registry_group_domain(
    data: ValidationDataContext,
    source_namespace: str,
) -> _ScalarLookupDomain:
    return _resolve_lookup_domain(
        data,
        source_namespace,
        "registry:value_registry",
        "registry_value_id",
        "group_id",
    )


def _resolve_typed_contract_table(
    data: ValidationDataContext, table_token: str
) -> tuple[FrozenRecord, ...] | None:
    if type(table_token) is not str or table_token not in _TYPED_CONTRACT_TABLES:
        return None
    namespace, table_id = table_token.split(":")
    if not data.has_namespace(namespace):
        return None
    return _resolve_table(data, table_id, namespace=namespace)


def _prepare_count_domains(
    node: object,
    data: ValidationDataContext,
    source_namespace: str,
) -> dict[str, _CountTableDomain]:
    fields_by_table: dict[str, set[str]] = {}
    for count_call, bound_names in _count_nodes_with_bindings(node):
        table = count_call.arguments[0]
        assert isinstance(table, Literal) and isinstance(table.value, str)
        fields_by_table.setdefault(table.value, set()).update(
            _count_candidate_identifier_names(
                count_call.arguments[1], bound_names
            )
        )
    return {
        table_token: _resolve_count_domain(
            data,
            source_namespace,
            table_token,
            tuple(sorted(field_names, key=_utf8)),
        )
        for table_token, field_names in sorted(
            fields_by_table.items(), key=lambda item: _utf8(item[0])
        )
    }


def _count_nodes_with_bindings(
    node: object,
) -> tuple[tuple[Call, frozenset[str]], ...]:
    result: list[tuple[Call, frozenset[str]]] = []

    def visit(candidate: object, bound_names: frozenset[str]) -> None:
        if isinstance(candidate, Call):
            if candidate.function == "count":
                result.append((candidate, bound_names))
            for argument in candidate.arguments:
                visit(argument, bound_names)
        elif isinstance(candidate, BinaryOperation):
            visit(candidate.left, bound_names)
            visit(candidate.right, bound_names)
        elif isinstance(candidate, UnaryOperation):
            visit(candidate.operand, bound_names)
        elif isinstance(candidate, ListLiteral):
            for item in candidate.items:
                visit(item, bound_names)
        elif isinstance(candidate, Sequence):
            local_names = set(bound_names)
            for statement in candidate.statements:
                visit(statement, frozenset(local_names))
                if isinstance(statement, Binding):
                    local_names.add(statement.name)
        elif isinstance(candidate, Binding):
            visit(candidate.value, bound_names)
        elif isinstance(candidate, MemberAccess):
            visit(candidate.target, bound_names)

    visit(node, frozenset())
    return tuple(result)


def _count_candidate_identifier_names(
    node: object,
    bound_names: frozenset[str],
) -> frozenset[str]:
    if isinstance(node, Identifier):
        return (
            frozenset()
            if node.name == "current" or node.name in bound_names
            else frozenset({node.name})
        )
    if isinstance(node, ListLiteral):
        return frozenset().union(
            *(
                _count_candidate_identifier_names(item, bound_names)
                for item in node.items
            )
        )
    if isinstance(node, UnaryOperation):
        return _count_candidate_identifier_names(node.operand, bound_names)
    if isinstance(node, BinaryOperation):
        return _count_candidate_identifier_names(
            node.left, bound_names
        ) | _count_candidate_identifier_names(node.right, bound_names)
    if isinstance(node, Call):
        return frozenset().union(
            *(
                _count_candidate_identifier_names(argument, bound_names)
                for argument in node.arguments
            )
        )
    if isinstance(node, MemberAccess):
        return frozenset()
    return frozenset()


def _resolve_count_domain(
    data: ValidationDataContext,
    source_namespace: str,
    table_token: str,
    field_names: tuple[str, ...],
) -> _CountTableDomain:
    namespace, table_id = _count_table_identity(
        data, source_namespace, table_token
    )
    records = _resolve_table(data, table_id, namespace=namespace)
    if records is None:
        raise _lookup_failure(
            "count_table_missing",
            source_namespace,
            namespace,
            table_id,
            "<predicate>",
            None,
            "<count>",
        )
    primary_key = _resolve_primary_key(
        data, table_id, namespace=namespace
    )
    if primary_key is None:
        raise _lookup_failure(
            "count_table_schema_unresolved",
            source_namespace,
            namespace,
            table_id,
            "<predicate>",
            None,
            "<count>",
        )
    field_contracts = []
    for field_name in field_names:
        field_schema = _resolve_field_schema(
            data,
            table_id,
            field_name=field_name,
            namespace=namespace,
        )
        if (
            field_schema is None
            or _field_schema_reason(field_schema) is not None
        ):
            raise _lookup_failure(
                "count_predicate_field_unresolved",
                source_namespace,
                namespace,
                table_id,
                field_name,
                None,
                "<count>",
            )
        field_contracts.append((field_name, field_schema))
    return _CountTableDomain(
        source_namespace,
        namespace,
        table_id,
        tuple(field_contracts),
        primary_key,
        records,
    )


def _count_table_identity(
    data: ValidationDataContext,
    source_namespace: str,
    table_token: str,
) -> tuple[str, str]:
    parts = table_token.split(":")
    if len(parts) == 1:
        namespace, table_id = source_namespace, parts[0]
    elif len(parts) == 2:
        namespace, table_id = parts
    else:
        namespace, table_id = None, table_token
    if not (
        namespace is not None
        and _is_logical_identifier(namespace)
        and _is_logical_identifier(table_id)
        and data.has_namespace(namespace)
    ):
        raise _lookup_failure(
            "count_namespace_invalid",
            source_namespace,
            namespace,
            table_id,
            "<predicate>",
            None,
            "<count>",
        )
    return namespace, table_id


def _validated_count_records(
    domain: _CountTableDomain,
) -> tuple[FrozenRecord, ...]:
    ordered = tuple(
        sorted(
            domain.records,
            key=lambda item: _record_sort_key(
                item, domain.primary_key_name
            ),
        )
    )
    for record in ordered:
        if not _valid_identity(record, domain.primary_key_name):
            raise ValidationExpressionEvaluationError(
                node_type="Call",
                builtin="count",
                reason="count_candidate_identity_invalid",
            )
        for field_name, field_schema in domain.field_contracts:
            if field_name not in record:
                raise ValidationExpressionEvaluationError(
                    node_type="Call",
                    builtin="count",
                    identifier=field_name,
                    reason="count_candidate_field_missing",
                )
            if _field_value_reason(record[field_name], field_schema) is not None:
                raise ValidationExpressionEvaluationError(
                    node_type="Call",
                    builtin="count",
                    identifier=field_name,
                    reason="count_candidate_field_value_invalid",
                )
    return ordered


def _prepare_record_lookup_domains(
    node: object,
    data: ValidationDataContext,
    source_namespace: str,
) -> dict[tuple[str, str], _RecordLookupDomain]:
    domains: dict[tuple[str, str], _RecordLookupDomain] = {}
    for lookup in _record_lookup_nodes(node):
        table = lookup.arguments[0]
        key = lookup.arguments[1]
        assert isinstance(table, Literal) and isinstance(table.value, str)
        assert isinstance(key, Literal) and isinstance(key.value, str)
        domain_key = (table.value, key.value)
        if domain_key not in domains:
            domains[domain_key] = _resolve_record_lookup_domain(
                data,
                source_namespace,
                table.value,
                key.value,
            )
    return domains


def _prepare_composite_record_lookup_domains(
    node: object,
    data: ValidationDataContext,
    source_namespace: str,
) -> dict[tuple[str, tuple[str, ...]], _CompositeRecordLookupDomain]:
    domains: dict[
        tuple[str, tuple[str, ...]], _CompositeRecordLookupDomain
    ] = {}
    for lookup in _call_nodes(node, "lookup_record_by"):
        table = lookup.arguments[0]
        fields = lookup.arguments[1]
        assert isinstance(table, Literal) and isinstance(table.value, str)
        if not isinstance(fields, ListLiteral):
            raise _lookup_failure(
                "lookup_record_by_key_fields_collection_required",
                source_namespace,
                None,
                table.value,
                "<composite>",
                None,
                "<record>",
            )
        key_fields: list[str] = []
        for field in fields.items:
            if not (
                isinstance(field, Literal)
                and field.literal_kind == "string"
                and type(field.value) is str
                and bool(field.value)
            ):
                raise _lookup_failure(
                    "lookup_record_by_key_field_invalid",
                    source_namespace,
                    None,
                    table.value,
                    "<composite>",
                    None,
                    "<record>",
                )
            key_fields.append(field.value)
        if not key_fields:
            raise _lookup_failure(
                "lookup_record_by_key_fields_empty",
                source_namespace,
                None,
                table.value,
                "<composite>",
                None,
                "<record>",
            )
        if len(set(key_fields)) != len(key_fields):
            raise _lookup_failure(
                "lookup_record_by_key_field_duplicate",
                source_namespace,
                None,
                table.value,
                ",".join(key_fields),
                None,
                "<record>",
            )
        key = (table.value, tuple(key_fields))
        if key not in domains:
            domains[key] = _resolve_composite_record_lookup_domain(
                data,
                source_namespace,
                table.value,
                tuple(key_fields),
            )
    return domains


def _lookup_nodes(node: object) -> tuple[Call, ...]:
    return _call_nodes(node, "lookup")


def _record_lookup_nodes(node: object) -> tuple[Call, ...]:
    return _call_nodes(node, "lookup_record")


def _call_nodes(node: object, function: str) -> tuple[Call, ...]:
    result: list[Call] = []

    def visit(candidate: object) -> None:
        if isinstance(candidate, Call):
            if candidate.function == function:
                result.append(candidate)
            for argument in candidate.arguments:
                visit(argument)
        elif isinstance(candidate, BinaryOperation):
            visit(candidate.left)
            visit(candidate.right)
        elif isinstance(candidate, UnaryOperation):
            visit(candidate.operand)
        elif isinstance(candidate, ListLiteral):
            for item in candidate.items:
                visit(item)
        elif isinstance(candidate, Sequence):
            for statement in candidate.statements:
                visit(statement)
        elif isinstance(candidate, Binding):
            visit(candidate.value)
        elif isinstance(candidate, MemberAccess):
            visit(candidate.target)

    visit(node)
    return tuple(result)


def _resolve_lookup_domain(
    data: ValidationDataContext,
    source_namespace: str,
    table_token: str,
    key_field_name: str,
    output_field_name: str,
) -> _ScalarLookupDomain:
    namespace, table_id = _lookup_table_identity(
        data, source_namespace, table_token, key_field_name,
        output_field_name,
    )
    records = _resolve_table(data, table_id, namespace=namespace)
    if records is None:
        raise _lookup_failure(
            "lookup_table_missing", source_namespace, namespace, table_id,
            key_field_name, None, output_field_name,
        )
    key_schema = _resolve_field_schema(
        data,
        table_id,
        field_name=key_field_name,
        namespace=namespace,
    )
    if key_schema is None or _lookup_schema_reason(
        key_schema, key_field=True
    ) is not None:
        raise _lookup_failure(
            "lookup_key_field_unresolved", source_namespace, namespace,
            table_id, key_field_name, None, output_field_name,
        )
    primary_key = _resolve_primary_key(
        data, table_id, namespace=namespace
    )
    if primary_key != key_field_name:
        raise _lookup_failure(
            "lookup_key_field_not_primary", source_namespace, namespace,
            table_id, key_field_name, None, output_field_name,
            unsupported=True,
        )
    output_schema = _resolve_field_schema(
        data,
        table_id,
        field_name=output_field_name,
        namespace=namespace,
    )
    if output_schema is None or _lookup_schema_reason(
        output_schema, key_field=False
    ) is not None:
        raise _lookup_failure(
            "lookup_output_field_unresolved", source_namespace, namespace,
            table_id, key_field_name, None, output_field_name,
        )
    return _ScalarLookupDomain(
        source_namespace,
        namespace,
        table_id,
        key_field_name,
        output_field_name,
        key_schema,
        output_schema,
        records,
    )


def _resolve_record_lookup_domain(
    data: ValidationDataContext,
    source_namespace: str,
    table_token: str,
    key_field_name: str,
) -> _RecordLookupDomain:
    namespace, table_id = _lookup_table_identity(
        data,
        source_namespace,
        table_token,
        key_field_name,
        "<record>",
    )
    records = _resolve_table(data, table_id, namespace=namespace)
    if records is None:
        raise _lookup_failure(
            "lookup_table_missing",
            source_namespace,
            namespace,
            table_id,
            key_field_name,
            None,
            "<record>",
        )
    key_schema = _resolve_field_schema(
        data,
        table_id,
        field_name=key_field_name,
        namespace=namespace,
    )
    if key_schema is None or _lookup_schema_reason(
        key_schema, key_field=False
    ) is not None:
        raise _lookup_failure(
            "lookup_key_field_unresolved",
            source_namespace,
            namespace,
            table_id,
            key_field_name,
            None,
            "<record>",
        )
    primary_key = _resolve_primary_key(
        data, table_id, namespace=namespace
    )
    if primary_key is None:
        raise _lookup_failure(
            "lookup_record_identity_invalid",
            source_namespace,
            namespace,
            table_id,
            key_field_name,
            None,
            "<record>",
        )
    return _RecordLookupDomain(
        source_namespace,
        namespace,
        table_id,
        key_field_name,
        key_schema,
        primary_key,
        records,
    )


def _resolve_composite_record_lookup_domain(
    data: ValidationDataContext,
    source_namespace: str,
    table_token: str,
    key_field_names: tuple[str, ...],
) -> _CompositeRecordLookupDomain:
    key_text = ",".join(key_field_names)
    namespace, table_id = _lookup_table_identity(
        data,
        source_namespace,
        table_token,
        key_text,
        "<record>",
    )
    records = _resolve_table(data, table_id, namespace=namespace)
    if records is None:
        raise _lookup_failure(
            "lookup_table_missing",
            source_namespace,
            namespace,
            table_id,
            key_text,
            None,
            "<record>",
        )
    key_fields: list[tuple[str, FrozenRecord]] = []
    for field_name in key_field_names:
        field_schema = _resolve_field_schema(
            data,
            table_id,
            field_name=field_name,
            namespace=namespace,
        )
        if field_schema is None or _lookup_schema_reason(
            field_schema, key_field=False
        ) is not None:
            raise _lookup_failure(
                "lookup_key_field_unresolved",
                source_namespace,
                namespace,
                table_id,
                field_name,
                None,
                "<record>",
            )
        key_fields.append((field_name, field_schema))
    primary_key = _resolve_primary_key(
        data, table_id, namespace=namespace
    )
    if primary_key is None:
        raise _lookup_failure(
            "lookup_record_identity_invalid",
            source_namespace,
            namespace,
            table_id,
            key_text,
            None,
            "<record>",
        )
    return _CompositeRecordLookupDomain(
        source_namespace,
        namespace,
        table_id,
        tuple(key_fields),
        primary_key,
        records,
    )


def _resolve_component_schema_version(
    data: ValidationDataContext, component_id: str
) -> str:
    metadata_found = False
    matches: list[tuple[str, tuple[FrozenRecord, ...]]] = []
    for namespace in data.namespaces:
        metadata = data.table("meta", namespace=namespace)
        if metadata is None:
            continue
        metadata_found = True
        identity_rows = tuple(
            record
            for record in metadata
            if record.get("key") == "export_directory_name"
        )
        if len(identity_rows) != 1:
            raise ValidationExpressionEvaluationError(
                node_type="Call",
                builtin="current_schema_version",
                reason="component_metadata_identity_invalid",
            )
        if identity_rows[0].get("value") == component_id:
            matches.append((namespace, metadata))

    if not metadata_found:
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="current_schema_version",
            reason="component_metadata_missing",
        )
    if not matches:
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="current_schema_version",
            reason="component_unknown",
        )
    if len(matches) != 1:
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="current_schema_version",
            reason="component_identity_ambiguous",
        )

    metadata = matches[0][1]
    version_rows = tuple(
        record for record in metadata
        if record.get("key") == "schema_version"
    )
    if len(version_rows) != 1:
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="current_schema_version",
            reason="component_schema_version_missing",
        )
    version = version_rows[0].get("value")
    if type(version) is not str:
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="current_schema_version",
            reason="component_schema_version_type_invalid",
        )
    return version


def _lookup_table_identity(
    data: ValidationDataContext,
    source_namespace: str,
    table_token: str,
    key_field_name: str,
    output_field_name: str,
) -> tuple[str, str]:
    parts = table_token.split(":")
    if len(parts) == 1:
        namespace, table_id = source_namespace, parts[0]
    elif len(parts) == 2:
        namespace, table_id = parts
    else:
        namespace, table_id = None, table_token
    if not (
        namespace is not None
        and _is_logical_identifier(namespace)
        and _is_logical_identifier(table_id)
        and data.has_namespace(namespace)
    ):
        raise _lookup_failure(
            "lookup_namespace_invalid", source_namespace, namespace,
            table_id, key_field_name, None, output_field_name,
        )
    return namespace, table_id


def _lookup_schema_reason(
    field_schema: FrozenRecord, *, key_field: bool
) -> str | None:
    reason = _field_schema_reason(field_schema)
    if reason is not None:
        return reason
    nullable = field_schema.get("nullable")
    expected_required = "conditional" if nullable else "always"
    if field_schema.get("required_mode") != expected_required:
        return "lookup_field_required_mode_invalid"
    if key_field and nullable:
        return "lookup_key_field_nullable"
    return None


def _resolve_scalar_lookup(
    domain: _ScalarLookupDomain,
    key_value: CanonicalScalar,
) -> _ScalarLookupResolution:
    if key_value is None:
        raise _lookup_failure_from_domain(
            domain, "lookup_null_key", key_value
        )
    if _field_value_reason(key_value, domain.key_schema) is not None:
        raise _lookup_failure_from_domain(
            domain, "lookup_key_type_invalid", key_value
        )

    matches: list[FrozenRecord] = []
    for record in sorted(
        domain.records,
        key=lambda item: _record_sort_key(
            item, domain.key_field_name
        ),
    ):
        if not _valid_identity(record, domain.key_field_name):
            raise _lookup_failure_from_domain(
                domain,
                "lookup_record_identity_invalid",
                key_value,
                related=(_safe_record_identity(
                    record, domain.key_field_name
                ),),
            )
        record_key = record[domain.key_field_name]
        if _field_value_reason(record_key, domain.key_schema) is not None:
            raise _lookup_failure_from_domain(
                domain,
                "lookup_record_identity_invalid",
                key_value,
                related=(_safe_record_identity(
                    record, domain.key_field_name
                ),),
            )
        if _typed_scalar_equal(record_key, key_value):
            matches.append(record)

    if not matches:
        return _ScalarLookupResolution(
            _LOOKUP_ZERO,
            None,
            domain.namespace,
            domain.table_id,
            domain.key_field_name,
            domain.output_field_name,
        )
    if len(matches) > 1:
        related = tuple(sorted(
            (
                _safe_record_identity(record, domain.key_field_name)
                for record in matches
            ),
            key=_utf8,
        ))
        raise _lookup_failure_from_domain(
            domain,
            "lookup_ambiguous",
            key_value,
            related=related,
        )

    match = matches[0]
    identity = _safe_record_identity(match, domain.key_field_name)
    if domain.output_field_name not in match:
        raise _lookup_failure_from_domain(
            domain,
            "lookup_output_value_invalid",
            key_value,
            related=(identity,),
        )
    value = match[domain.output_field_name]
    if _field_value_reason(value, domain.output_schema) is not None:
        raise _lookup_failure_from_domain(
            domain,
            "lookup_output_value_invalid",
            key_value,
            related=(identity,),
        )
    return _ScalarLookupResolution(
        _LOOKUP_EXACT,
        value,
        domain.namespace,
        domain.table_id,
        domain.key_field_name,
        domain.output_field_name,
        identity,
    )


def _project_explicit_namespace_key(
    domain: _ScalarLookupDomain,
    key_value: CanonicalScalar,
) -> CanonicalScalar:
    if (
        type(key_value) is not str
        or domain.namespace == domain.source_namespace
    ):
        return key_value
    parts = key_value.split(":")
    if (
        len(parts) == 2
        and parts[0] == domain.namespace
        and _is_logical_identifier(parts[1])
    ):
        return parts[1]
    return key_value


def _resolve_record_lookup(
    domain: _RecordLookupDomain,
    key_value: CanonicalScalar,
) -> _RecordLookupResolution:
    if key_value is None:
        raise _lookup_failure_from_record_domain(
            domain, "lookup_null_key", key_value
        )
    if _field_value_reason(key_value, domain.key_schema) is not None:
        raise _lookup_failure_from_record_domain(
            domain, "lookup_key_type_invalid", key_value
        )

    matches: list[FrozenRecord] = []
    for record in sorted(
        domain.records,
        key=lambda item: _record_sort_key(item, domain.primary_key_name),
    ):
        if not _valid_identity(record, domain.primary_key_name):
            raise _lookup_failure_from_record_domain(
                domain,
                "lookup_record_identity_invalid",
                key_value,
                related=(
                    _safe_record_identity(record, domain.primary_key_name),
                ),
            )
        if domain.key_field_name not in record:
            raise _lookup_failure_from_record_domain(
                domain,
                "lookup_record_key_value_invalid",
                key_value,
                related=(
                    _safe_record_identity(record, domain.primary_key_name),
                ),
            )
        record_key = record[domain.key_field_name]
        if _field_value_reason(record_key, domain.key_schema) is not None:
            raise _lookup_failure_from_record_domain(
                domain,
                "lookup_record_key_value_invalid",
                key_value,
                related=(
                    _safe_record_identity(record, domain.primary_key_name),
                ),
            )
        if _typed_scalar_equal(record_key, key_value):
            matches.append(record)

    if not matches:
        return _RecordLookupResolution(
            _LOOKUP_ZERO,
            None,
            domain.namespace,
            domain.table_id,
            domain.key_field_name,
        )
    if len(matches) > 1:
        related = tuple(sorted(
            (
                _safe_record_identity(record, domain.primary_key_name)
                for record in matches
            ),
            key=_utf8,
        ))
        raise _lookup_failure_from_record_domain(
            domain,
            "lookup_ambiguous",
            key_value,
            related=related,
        )

    match = matches[0]
    identity = _safe_record_identity(match, domain.primary_key_name)
    copied = {
        name: match[name]
        for name in sorted(match, key=_utf8)
    }
    return _RecordLookupResolution(
        _LOOKUP_EXACT,
        MappingProxyType(copied),
        domain.namespace,
        domain.table_id,
        domain.key_field_name,
        identity,
    )


def _resolve_composite_record_lookup(
    domain: _CompositeRecordLookupDomain,
    key_values: tuple[CanonicalScalar, ...],
) -> _RecordLookupResolution:
    field_names = tuple(name for name, _ in domain.key_fields)
    key_text = _canonical_record_text({
        name: value
        for (name, _), value in zip(domain.key_fields, key_values)
    })
    if len(key_values) != len(domain.key_fields):
        raise _lookup_failure_from_composite_domain(
            domain, "lookup_record_by_key_arity_mismatch", key_text
        )
    for (_, field_schema), key_value in zip(
        domain.key_fields, key_values
    ):
        if key_value is None:
            raise _lookup_failure_from_composite_domain(
                domain, "lookup_record_by_null_key_value", key_text
            )
        if _field_value_reason(key_value, field_schema) is not None:
            raise _lookup_failure_from_composite_domain(
                domain, "lookup_key_type_invalid", key_text
            )

    matches: list[FrozenRecord] = []
    for record in sorted(
        domain.records,
        key=lambda item: _record_sort_key(item, domain.primary_key_name),
    ):
        identity = _safe_record_identity(record, domain.primary_key_name)
        if not _valid_identity(record, domain.primary_key_name):
            raise _lookup_failure_from_composite_domain(
                domain,
                "lookup_record_identity_invalid",
                key_text,
                related=(identity,),
            )
        candidate_values: list[CanonicalScalar] = []
        for field_name, field_schema in domain.key_fields:
            if field_name not in record:
                raise _lookup_failure_from_composite_domain(
                    domain,
                    "lookup_record_key_value_invalid",
                    key_text,
                    related=(identity,),
                )
            candidate_value = record[field_name]
            if _field_value_reason(candidate_value, field_schema) is not None:
                raise _lookup_failure_from_composite_domain(
                    domain,
                    "lookup_record_key_value_invalid",
                    key_text,
                    related=(identity,),
                )
            candidate_values.append(candidate_value)
        if all(
            _typed_scalar_equal(candidate, expected)
            for candidate, expected in zip(candidate_values, key_values)
        ):
            matches.append(record)

    key_field_text = ",".join(field_names)
    if not matches:
        return _RecordLookupResolution(
            _LOOKUP_ZERO,
            None,
            domain.namespace,
            domain.table_id,
            key_field_text,
        )
    if len(matches) > 1:
        related = tuple(sorted(
            (
                _safe_record_identity(record, domain.primary_key_name)
                for record in matches
            ),
            key=_utf8,
        ))
        raise _lookup_failure_from_composite_domain(
            domain,
            "lookup_ambiguous",
            key_text,
            related=related,
        )

    match = matches[0]
    identity = _safe_record_identity(match, domain.primary_key_name)
    copied = {name: match[name] for name in sorted(match, key=_utf8)}
    return _RecordLookupResolution(
        _LOOKUP_EXACT,
        MappingProxyType(copied),
        domain.namespace,
        domain.table_id,
        key_field_text,
        identity,
    )


def _typed_scalar_equal(
    left: CanonicalScalar, right: CanonicalScalar
) -> bool:
    return type(left) is type(right) and left == right


def _lookup_failure(
    reason: str,
    source_namespace: str,
    namespace: str | None,
    table_id: str,
    key_field_name: str,
    key_value: CanonicalScalar,
    output_field_name: str,
    *,
    related: tuple[str, ...] = (),
    unsupported: bool = False,
) -> _ScalarLookupFailure:
    return _ScalarLookupFailure(
        reason,
        source_namespace=source_namespace,
        namespace=namespace,
        table_id=table_id,
        key_field_name=key_field_name,
        key_value=key_value,
        output_field_name=output_field_name,
        related_record_identities=related,
        unsupported=unsupported,
    )


def _lookup_failure_from_domain(
    domain: _ScalarLookupDomain,
    reason: str,
    key_value: CanonicalScalar,
    *,
    related: tuple[str, ...] = (),
) -> _ScalarLookupFailure:
    return _lookup_failure(
        reason,
        domain.source_namespace,
        domain.namespace,
        domain.table_id,
        domain.key_field_name,
        key_value,
        domain.output_field_name,
        related=related,
    )


def _lookup_failure_from_record_domain(
    domain: _RecordLookupDomain,
    reason: str,
    key_value: CanonicalScalar,
    *,
    related: tuple[str, ...] = (),
) -> _ScalarLookupFailure:
    return _lookup_failure(
        reason,
        domain.source_namespace,
        domain.namespace,
        domain.table_id,
        domain.key_field_name,
        key_value,
        "<record>",
        related=related,
    )


def _lookup_failure_from_composite_domain(
    domain: _CompositeRecordLookupDomain,
    reason: str,
    key_text: str,
    *,
    related: tuple[str, ...] = (),
) -> _ScalarLookupFailure:
    return _lookup_failure(
        reason,
        domain.source_namespace,
        domain.namespace,
        domain.table_id,
        ",".join(name for name, _ in domain.key_fields),
        key_text,
        "<record>",
        related=related,
    )


def _field_schema_reason(field_schema: FrozenRecord) -> str | None:
    if field_schema.get("data_type") not in _SCALAR_SCHEMA_TYPES:
        return "identifier_schema_type_not_supported"
    nullable = field_schema.get("nullable")
    if type(nullable) is not bool:
        return "identifier_schema_nullable_invalid"
    expected_null_handling = "explicit_null" if nullable else "forbidden"
    if field_schema.get("null_handling") != expected_null_handling:
        return "identifier_schema_null_contract_invalid"
    return None


def _record_environment(
    record: FrozenRecord,
    field_contracts: list[tuple[str, FrozenRecord]],
) -> tuple[dict[str, CanonicalScalar], tuple[str, CanonicalScalar] | None]:
    environment: dict[str, CanonicalScalar] = {}
    for identifier, field_schema in field_contracts:
        if identifier not in record:
            return environment, (f"target_field_missing:{identifier}", None)
        value = record[identifier]
        reason = _field_value_reason(value, field_schema)
        if reason is not None:
            return environment, (f"{reason}:{identifier}", value)
        environment[identifier] = value
    return environment, None


def _field_value_reason(
    value: CanonicalScalar,
    field_schema: FrozenRecord,
) -> str | None:
    if value is None:
        return None if field_schema.get("nullable") is True else "target_value_null"
    data_type = field_schema.get("data_type")
    expected_type = {
        "boolean": bool,
        "date": str,
        "integer": int,
        "language_tag": str,
        "string": str,
        "text": str,
    }[data_type]
    return None if type(value) is expected_type else "target_value_type_invalid"


def _expected_contract(rule: ValidationRuleDefinition, namespace: str) -> str:
    return (
        f"exact boolean direct row predicate over {namespace}:"
        f"{rule.target_table_id}; ast={rule.condition_ast_hash}"
    )


def _safe_record_identity(record: FrozenRecord, primary_key: str) -> str:
    if _valid_identity(record, primary_key):
        return _record_identity(record, primary_key)
    digest = hashlib.sha256(
        _canonical_record_text(record).encode("utf-8")
    ).hexdigest()
    return f"canonical-record-sha256:{digest}"


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


def _lookup_diagnostic(
    rule: ValidationRuleDefinition,
    error: _ScalarLookupFailure,
    record_identity: str | None,
) -> ValidationExecutionDiagnostic:
    namespace = error.namespace or "<unresolved>"
    key_text = _canonical_record_text({"key": error.key_value})
    expected = (
        f"scalar lookup source={error.source_namespace}; "
        f"target={namespace}:{error.table_id}; "
        f"key_field={error.key_field_name}; key={key_text}; "
        f"output_field={error.output_field_name}"
    )
    return ValidationExecutionDiagnostic(
        VALIDATION_DEFINITION_LOOKUP_INVALID,
        "Scalar lookup validation failed.",
        rule.rule_id,
        rule.target_table_id,
        rule.target_field_id,
        record_identity,
        error.key_value,
        expected,
        error.reason,
        error.related_record_identities,
    )


def _lookup_failure_result(
    rule: ValidationRuleDefinition,
    error: _ScalarLookupFailure,
    record_identity: str | None,
    evaluated_record_count: int,
) -> ValidationExecutionResult:
    diagnostic = _lookup_diagnostic(rule, error, record_identity)
    return ValidationExecutionResult(
        rule.rule_id,
        ValidationOutcome.FAIL,
        (diagnostic,),
        evaluated_record_count,
        1,
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
        else "bound source namespace and exact boolean direct row predicate"
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


def _is_diagnostic_scalar(value: object) -> bool:
    return value is None or type(value) in {bool, int, float, str}


__all__ = [
    "VALIDATION_DEFINITION_INVARIANT_FAILED",
    "VALIDATION_DEFINITION_TARGET_RECORD_INVALID",
    "VALIDATION_DEFINITION_TARGET_TABLE_MISSING",
    "execute_definition_invariant_rule",
]
