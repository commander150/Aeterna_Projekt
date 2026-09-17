"""Pure, allowlisted evaluation for the minimal validation-expression surface."""

from __future__ import annotations

import unicodedata
from collections.abc import Callable, Mapping, Sequence
from types import MappingProxyType
from typing import TypeAlias

try:  # Package import when the tools directory is on sys.path.
    from . import canonical_validation_expr as expression_ast
except ImportError:  # Direct file loading used by the repository test suite.
    import canonical_validation_expr as expression_ast


CanonicalScalar: TypeAlias = None | bool | int | str
CanonicalRecord: TypeAlias = Mapping[str, CanonicalScalar]
EvaluationAtom: TypeAlias = CanonicalScalar | CanonicalRecord
EvaluationValue: TypeAlias = EvaluationAtom | tuple["EvaluationValue", ...]
LookupResolver: TypeAlias = Callable[
    [str, str, CanonicalScalar, str], CanonicalScalar
]
RecordLookupResolver: TypeAlias = Callable[
    [str, str, CanonicalScalar], CanonicalRecord | None
]
RecordLookupByResolver: TypeAlias = Callable[
    [str, tuple[str, ...], tuple[CanonicalScalar, ...]],
    CanonicalRecord | None,
]
SchemaVersionResolver: TypeAlias = Callable[[str], str]
TableResolver: TypeAlias = Callable[
    [str], Sequence[CanonicalRecord] | None
]
RegistryGroupResolver: TypeAlias = Callable[[str], str | None]
ExistsResolver: TypeAlias = Callable[[str, str, CanonicalScalar], bool]
ValueOfResolver: TypeAlias = Callable[[str], str | None]
PrimaryKeyResolver: TypeAlias = Callable[[str], str]
_CARDINALITY_BUILTINS = frozenset(
    {
        "at_least_one_non_null",
        "at_most_one_non_null",
        "count_non_null",
    }
)
_RESERVED_BINDING_NAMES = frozenset({"current"})
_TEXT_LIKE_DATA_TYPES = frozenset(
    {"string", "text", "date", "version", "language_tag"}
)
_TEMPLATE_ARGUMENT_BUILTIN = "template_argument_value_type_valid"
_TEMPLATE_BINDING_BUILTIN = "template_binding_value_type_valid"
MATCHES_MAX_INPUT_LENGTH = 4096
MATCHES_MAX_PATTERN_LENGTH = 256
_SCALAR_STRING_BUILTINS = frozenset({"matches", "starts_with", "trim"})
_MATCHES_FORBIDDEN_LITERAL_CHARACTERS = frozenset("^$[]()|?*{}.+\\")


class _EvaluationEnvironment(Mapping[str, EvaluationAtom]):
    __slots__ = (
        "_values",
        "exists_resolver",
        "primary_key_resolver",
        "protected_names",
        "record_lookup_by_resolver",
        "registry_group_resolver",
        "table_resolver",
        "value_of_resolver",
    )

    def __init__(
        self,
        values: Mapping[str, EvaluationAtom],
        *,
        exists_resolver: ExistsResolver | None = None,
        primary_key_resolver: PrimaryKeyResolver | None = None,
        protected_names: frozenset[str] = frozenset(),
        record_lookup_by_resolver: RecordLookupByResolver | None = None,
        registry_group_resolver: RegistryGroupResolver | None = None,
        table_resolver: TableResolver | None = None,
        value_of_resolver: ValueOfResolver | None = None,
    ) -> None:
        self._values = MappingProxyType(dict(values))
        self.exists_resolver = exists_resolver
        self.primary_key_resolver = primary_key_resolver
        self.protected_names = protected_names
        self.record_lookup_by_resolver = record_lookup_by_resolver
        self.registry_group_resolver = registry_group_resolver
        self.table_resolver = table_resolver
        self.value_of_resolver = value_of_resolver

    def __getitem__(self, key: str) -> EvaluationAtom:
        return self._values[key]

    def __iter__(self):
        return iter(self._values)

    def __len__(self) -> int:
        return len(self._values)


class ValidationExpressionEvaluationError(ValueError):
    """A supported expression could not be evaluated under the value contract."""

    def __init__(
        self,
        *,
        node_type: str,
        reason: str,
        operator: str | None = None,
        builtin: str | None = None,
        identifier: str | None = None,
    ) -> None:
        details = {
            "node_type": node_type,
            "reason": reason,
        }
        if operator is not None:
            details["operator"] = operator
        if builtin is not None:
            details["builtin"] = builtin
        if identifier is not None:
            details["identifier"] = identifier
        self.context = tuple(
            sorted(details.items(), key=lambda item: item[0].encode("utf-8"))
        )
        message = ", ".join(f"{key}={value}" for key, value in self.context)
        super().__init__(f"Validation expression evaluation failed: {message}.")


class ValidationExpressionUnsupportedError(ValidationExpressionEvaluationError):
    """The expression uses syntax outside the evaluator's explicit allowlist."""


def evaluate_validation_expression(
    expression: object,
    identifiers: Mapping[str, EvaluationAtom],
    *,
    lookup_resolver: LookupResolver | None = None,
    record_lookup_resolver: RecordLookupResolver | None = None,
    record_lookup_by_resolver: RecordLookupByResolver | None = None,
    exists_resolver: ExistsResolver | None = None,
    value_of_resolver: ValueOfResolver | None = None,
    primary_key_resolver: PrimaryKeyResolver | None = None,
    schema_version_resolver: SchemaVersionResolver | None = None,
    table_resolver: TableResolver | None = None,
    registry_group_resolver: RegistryGroupResolver | None = None,
) -> EvaluationValue:
    """Evaluate an AST against a copied, read-only identifier environment."""
    if not isinstance(identifiers, Mapping):
        raise ValidationExpressionEvaluationError(
            node_type="Environment",
            reason="identifiers_not_mapping",
        )
    environment_copy = dict(identifiers)
    if any(type(name) is not str for name in environment_copy):
        raise ValidationExpressionEvaluationError(
            node_type="Environment",
            reason="identifier_name_not_string",
        )
    if lookup_resolver is not None and not callable(lookup_resolver):
        raise ValidationExpressionEvaluationError(
            node_type="Environment",
            reason="lookup_resolver_not_callable",
        )
    if record_lookup_resolver is not None and not callable(
        record_lookup_resolver
    ):
        raise ValidationExpressionEvaluationError(
            node_type="Environment",
            reason="record_lookup_resolver_not_callable",
        )
    if record_lookup_by_resolver is not None and not callable(
        record_lookup_by_resolver
    ):
        raise ValidationExpressionEvaluationError(
            node_type="Environment",
            reason="record_lookup_by_resolver_not_callable",
        )
    for resolver, reason in (
        (exists_resolver, "exists_resolver_not_callable"),
        (value_of_resolver, "value_of_resolver_not_callable"),
        (primary_key_resolver, "primary_key_resolver_not_callable"),
    ):
        if resolver is not None and not callable(resolver):
            raise ValidationExpressionEvaluationError(
                node_type="Environment",
                reason=reason,
            )
    if schema_version_resolver is not None and not callable(
        schema_version_resolver
    ):
        raise ValidationExpressionEvaluationError(
            node_type="Environment",
            reason="schema_version_resolver_not_callable",
        )
    if table_resolver is not None and not callable(table_resolver):
        raise ValidationExpressionEvaluationError(
            node_type="Environment",
            reason="table_resolver_not_callable",
        )
    if registry_group_resolver is not None and not callable(
        registry_group_resolver
    ):
        raise ValidationExpressionEvaluationError(
            node_type="Environment",
            reason="registry_group_resolver_not_callable",
        )
    environment = _EvaluationEnvironment(
        environment_copy,
        exists_resolver=exists_resolver,
        primary_key_resolver=primary_key_resolver,
        record_lookup_by_resolver=record_lookup_by_resolver,
        registry_group_resolver=registry_group_resolver,
        table_resolver=table_resolver,
        value_of_resolver=value_of_resolver,
    )
    if isinstance(expression, expression_ast.Sequence):
        return _evaluate_sequence(
            expression,
            environment,
            lookup_resolver,
            record_lookup_resolver,
            schema_version_resolver,
            bindings_allowed=True,
        )
    return _evaluate_node(
        expression,
        environment,
        lookup_resolver,
        record_lookup_resolver,
        schema_version_resolver,
    )


def _evaluate_node(
    node: object,
    identifiers: Mapping[str, EvaluationAtom],
    lookup_resolver: LookupResolver | None,
    record_lookup_resolver: RecordLookupResolver | None,
    schema_version_resolver: SchemaVersionResolver | None,
) -> EvaluationValue:
    if isinstance(node, expression_ast.Literal):
        return _evaluate_literal(node)

    if isinstance(node, expression_ast.Identifier):
        if node.name not in identifiers:
            raise ValidationExpressionEvaluationError(
                node_type="Identifier",
                identifier=node.name,
                reason="identifier_missing",
            )
        value = identifiers[node.name]
        if not _is_evaluation_atom(value):
            raise ValidationExpressionEvaluationError(
                node_type="Identifier",
                identifier=node.name,
                reason="identifier_value_type_unsupported",
            )
        return value

    if isinstance(node, expression_ast.ListLiteral):
        return tuple(
            _evaluate_node(
                item,
                identifiers,
                lookup_resolver,
                record_lookup_resolver,
                schema_version_resolver,
            )
            for item in node.items
        )

    if isinstance(node, expression_ast.UnaryOperation):
        if node.operator != "not":
            raise ValidationExpressionUnsupportedError(
                node_type="UnaryOperation",
                operator=node.operator,
                reason="operator_not_allowlisted",
            )
        operand = _evaluate_node(
            node.operand,
            identifiers,
            lookup_resolver,
            record_lookup_resolver,
            schema_version_resolver,
        )
        _require_bool(operand, node_type="UnaryOperation", operator=node.operator)
        return not operand

    if isinstance(node, expression_ast.BinaryOperation):
        return _evaluate_binary(
            node,
            identifiers,
            lookup_resolver,
            record_lookup_resolver,
            schema_version_resolver,
        )

    if isinstance(node, expression_ast.Call):
        return _evaluate_call(
            node,
            identifiers,
            lookup_resolver,
            record_lookup_resolver,
            schema_version_resolver,
        )

    if isinstance(node, expression_ast.MemberAccess):
        return _evaluate_member_access(
            node,
            identifiers,
            lookup_resolver,
            record_lookup_resolver,
            schema_version_resolver,
        )

    if isinstance(node, expression_ast.Sequence):
        return _evaluate_sequence(
            node,
            identifiers,
            lookup_resolver,
            record_lookup_resolver,
            schema_version_resolver,
            bindings_allowed=False,
        )

    if isinstance(
        node,
        (
            expression_ast.TbdLiteral,
            expression_ast.MapLiteral,
            expression_ast.Binding,
        ),
    ):
        raise ValidationExpressionUnsupportedError(
            node_type=type(node).__name__,
            reason="node_not_allowlisted",
        )

    raise ValidationExpressionUnsupportedError(
        node_type=type(node).__name__,
        reason="node_not_allowlisted",
    )


def _evaluate_sequence(
    node: expression_ast.Sequence,
    source_identifiers: Mapping[str, EvaluationAtom],
    lookup_resolver: LookupResolver | None,
    record_lookup_resolver: RecordLookupResolver | None,
    schema_version_resolver: SchemaVersionResolver | None,
    *,
    bindings_allowed: bool,
) -> bool:
    if not node.statements:
        raise ValidationExpressionEvaluationError(
            node_type="Sequence",
            reason="sequence_must_not_be_empty",
        )
    local_bindings: dict[str, EvaluationAtom] = {}
    boolean_statement_seen = False
    for statement in node.statements:
        inherited_protected = getattr(
            source_identifiers, "protected_names", frozenset()
        )
        environment = _EvaluationEnvironment(
            {**source_identifiers, **local_bindings},
            exists_resolver=getattr(
                source_identifiers, "exists_resolver", None
            ),
            primary_key_resolver=getattr(
                source_identifiers, "primary_key_resolver", None
            ),
            protected_names=(
                inherited_protected | frozenset(local_bindings)
            ),
            record_lookup_by_resolver=getattr(
                source_identifiers, "record_lookup_by_resolver", None
            ),
            registry_group_resolver=getattr(
                source_identifiers, "registry_group_resolver", None
            ),
            table_resolver=getattr(
                source_identifiers, "table_resolver", None
            ),
            value_of_resolver=getattr(
                source_identifiers, "value_of_resolver", None
            ),
        )
        if isinstance(statement, expression_ast.Binding):
            if not bindings_allowed:
                raise ValidationExpressionUnsupportedError(
                    node_type="Binding",
                    identifier=statement.name,
                    reason="binding_scope_not_allowlisted",
                )
            if boolean_statement_seen:
                raise ValidationExpressionUnsupportedError(
                    node_type="Binding",
                    identifier=statement.name,
                    reason="binding_after_boolean_statement",
                )
            _validate_binding_name(
                statement.name, source_identifiers, local_bindings
            )
            value = _evaluate_node(
                statement.value,
                environment,
                lookup_resolver,
                record_lookup_resolver,
                schema_version_resolver,
            )
            if not _is_evaluation_atom(value):
                raise ValidationExpressionEvaluationError(
                    node_type="Binding",
                    identifier=statement.name,
                    reason="binding_value_type_unsupported",
                )
            local_bindings[statement.name] = value
            continue
        boolean_statement_seen = True
        result = _evaluate_node(
            statement,
            environment,
            lookup_resolver,
            record_lookup_resolver,
            schema_version_resolver,
        )
        _require_bool(result, node_type="Sequence")
        if not result:
            return False
    if local_bindings and not boolean_statement_seen:
        raise ValidationExpressionEvaluationError(
            node_type="Sequence",
            reason="sequence_boolean_statement_required",
        )
    return True


def _validate_binding_name(
    name: object,
    source_identifiers: Mapping[str, EvaluationAtom],
    local_bindings: Mapping[str, EvaluationAtom],
) -> None:
    if type(name) is not str or not name:
        raise ValidationExpressionEvaluationError(
            node_type="Binding",
            reason="binding_name_invalid",
        )
    if name in _RESERVED_BINDING_NAMES:
        raise ValidationExpressionUnsupportedError(
            node_type="Binding",
            identifier=name,
            reason="binding_name_reserved",
        )
    if name in source_identifiers:
        raise ValidationExpressionEvaluationError(
            node_type="Binding",
            identifier=name,
            reason="binding_name_collides_with_source_identifier",
        )
    if name in local_bindings:
        raise ValidationExpressionEvaluationError(
            node_type="Binding",
            identifier=name,
            reason="binding_name_already_defined",
        )


def _evaluate_literal(node: expression_ast.Literal) -> CanonicalScalar:
    expected_types = {
        "null": (type(None),),
        "boolean": (bool,),
        "integer": (int,),
        "string": (str,),
    }
    allowed_types = expected_types.get(node.literal_kind)
    if allowed_types is None or type(node.value) not in allowed_types:
        raise ValidationExpressionEvaluationError(
            node_type="Literal",
            reason="literal_kind_or_value_invalid",
        )
    return node.value


def _evaluate_binary(
    node: expression_ast.BinaryOperation,
    identifiers: Mapping[str, EvaluationAtom],
    lookup_resolver: LookupResolver | None,
    record_lookup_resolver: RecordLookupResolver | None,
    schema_version_resolver: SchemaVersionResolver | None,
) -> EvaluationValue:
    operator = node.operator
    if operator == "and":
        left = _evaluate_node(
            node.left,
            identifiers,
            lookup_resolver,
            record_lookup_resolver,
            schema_version_resolver,
        )
        _require_bool(left, node_type="BinaryOperation", operator=operator)
        if not left:
            return False
        right = _evaluate_node(
            node.right,
            identifiers,
            lookup_resolver,
            record_lookup_resolver,
            schema_version_resolver,
        )
        _require_bool(right, node_type="BinaryOperation", operator=operator)
        return right

    if operator == "or":
        left = _evaluate_node(
            node.left,
            identifiers,
            lookup_resolver,
            record_lookup_resolver,
            schema_version_resolver,
        )
        _require_bool(left, node_type="BinaryOperation", operator=operator)
        if left:
            return True
        right = _evaluate_node(
            node.right,
            identifiers,
            lookup_resolver,
            record_lookup_resolver,
            schema_version_resolver,
        )
        _require_bool(right, node_type="BinaryOperation", operator=operator)
        return right

    if operator not in {"==", "!=", "<", ">", ">=", "in", "not in"}:
        raise ValidationExpressionUnsupportedError(
            node_type="BinaryOperation",
            operator=operator,
            reason="operator_not_allowlisted",
        )

    left = _evaluate_node(
        node.left,
        identifiers,
        lookup_resolver,
        record_lookup_resolver,
        schema_version_resolver,
    )
    right = _evaluate_node(
        node.right,
        identifiers,
        lookup_resolver,
        record_lookup_resolver,
        schema_version_resolver,
    )
    if operator == "==":
        return _typed_equal(left, right)
    if operator == "!=":
        return not _typed_equal(left, right)
    if operator in {"<", ">", ">="}:
        if type(left) is not int or type(right) is not int:
            raise ValidationExpressionEvaluationError(
                node_type="BinaryOperation",
                operator=operator,
                reason="integer_operands_required",
            )
        if operator == "<":
            return left < right
        return left > right if operator == ">" else left >= right
    if not isinstance(right, tuple):
        raise ValidationExpressionEvaluationError(
            node_type="BinaryOperation",
            operator=operator,
            reason="list_right_operand_required",
        )
    membership = any(_typed_equal(left, item) for item in right)
    return membership if operator == "in" else not membership


def _evaluate_call(
    node: expression_ast.Call,
    identifiers: Mapping[str, EvaluationAtom],
    lookup_resolver: LookupResolver | None,
    record_lookup_resolver: RecordLookupResolver | None,
    schema_version_resolver: SchemaVersionResolver | None,
) -> EvaluationValue:
    if node.function in _SCALAR_STRING_BUILTINS:
        return _evaluate_scalar_string_builtin(
            node,
            identifiers,
            lookup_resolver,
            record_lookup_resolver,
            schema_version_resolver,
        )
    if node.function == _TEMPLATE_ARGUMENT_BUILTIN:
        return _evaluate_template_argument_value_type_valid(
            node,
            identifiers,
            lookup_resolver,
            record_lookup_resolver,
            schema_version_resolver,
        )
    if node.function == _TEMPLATE_BINDING_BUILTIN:
        return _evaluate_template_binding_value_type_valid(
            node,
            identifiers,
            lookup_resolver,
            record_lookup_resolver,
            schema_version_resolver,
        )
    if node.function == "template_binding_shape_valid":
        return _evaluate_template_binding_shape_valid(
            node,
            identifiers,
            lookup_resolver,
            record_lookup_resolver,
            schema_version_resolver,
        )
    if node.function == "count":
        return _evaluate_count(
            node,
            identifiers,
            lookup_resolver,
            record_lookup_resolver,
            schema_version_resolver,
        )
    if node.function == "normalize":
        return _evaluate_normalize(
            node,
            identifiers,
            lookup_resolver,
            record_lookup_resolver,
            schema_version_resolver,
        )
    if node.function == "normalize_search_name_hu":
        return _evaluate_normalize_search_name_hu(
            node,
            identifiers,
            lookup_resolver,
            record_lookup_resolver,
            schema_version_resolver,
        )
    if node.function == "group_of":
        return _evaluate_group_of(
            node,
            identifiers,
            lookup_resolver,
            record_lookup_resolver,
            schema_version_resolver,
        )
    if node.function in _CARDINALITY_BUILTINS:
        return _evaluate_cardinality(
            node,
            identifiers,
            lookup_resolver,
            record_lookup_resolver,
            schema_version_resolver,
        )
    if node.function == "lookup":
        return _evaluate_lookup(
            node,
            identifiers,
            lookup_resolver,
            record_lookup_resolver,
            schema_version_resolver,
        )
    if node.function == "exists":
        return _evaluate_exists(
            node,
            identifiers,
            lookup_resolver,
            record_lookup_resolver,
            schema_version_resolver,
        )
    if node.function == "value_of":
        return _evaluate_value_of(
            node,
            identifiers,
            lookup_resolver,
            record_lookup_resolver,
            schema_version_resolver,
        )
    if node.function == "primary_key_of":
        return _evaluate_primary_key_of(
            node,
            identifiers,
            lookup_resolver,
            record_lookup_resolver,
            schema_version_resolver,
        )
    if node.function == "lookup_record":
        return _evaluate_record_lookup(
            node,
            identifiers,
            lookup_resolver,
            record_lookup_resolver,
            schema_version_resolver,
        )
    if node.function == "lookup_record_by":
        return _evaluate_record_lookup_by(
            node,
            identifiers,
            lookup_resolver,
            record_lookup_resolver,
            schema_version_resolver,
        )
    if node.function == "current_schema_version":
        return _evaluate_current_schema_version(
            node,
            identifiers,
            lookup_resolver,
            record_lookup_resolver,
            schema_version_resolver,
        )
    if node.function == "version_gte":
        return _evaluate_version_gte(
            node,
            identifiers,
            lookup_resolver,
            record_lookup_resolver,
            schema_version_resolver,
        )
    if node.function != "when":
        raise ValidationExpressionUnsupportedError(
            node_type="Call",
            builtin=node.function,
            reason="builtin_not_allowlisted",
        )
    if len(node.arguments) != 2:
        raise ValidationExpressionUnsupportedError(
            node_type="Call",
            builtin=node.function,
            reason="builtin_arity_not_supported",
        )
    condition = _evaluate_node(
        node.arguments[0],
        identifiers,
        lookup_resolver,
        record_lookup_resolver,
        schema_version_resolver,
    )
    _require_bool(condition, node_type="Call", builtin=node.function)
    if not condition:
        return True
    constraint_node = node.arguments[1]
    constraint = (
        _evaluate_sequence(
            constraint_node,
            identifiers,
            lookup_resolver,
            record_lookup_resolver,
            schema_version_resolver,
            bindings_allowed=True,
        )
        if isinstance(constraint_node, expression_ast.Sequence)
        else _evaluate_node(
            constraint_node,
            identifiers,
            lookup_resolver,
            record_lookup_resolver,
            schema_version_resolver,
        )
    )
    _require_bool(constraint, node_type="Call", builtin=node.function)
    return constraint


def _evaluate_scalar_string_builtin(
    node: expression_ast.Call,
    identifiers: Mapping[str, EvaluationAtom],
    lookup_resolver: LookupResolver | None,
    record_lookup_resolver: RecordLookupResolver | None,
    schema_version_resolver: SchemaVersionResolver | None,
) -> str | bool:
    expected_arity = 1 if node.function == "trim" else 2
    if len(node.arguments) != expected_arity:
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin=node.function,
            reason="builtin_arity_invalid",
        )
    values = tuple(
        _evaluate_node(
            argument,
            identifiers,
            lookup_resolver,
            record_lookup_resolver,
            schema_version_resolver,
        )
        for argument in node.arguments
    )
    if any(type(value) is not str for value in values):
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin=node.function,
            reason="string_argument_type_invalid",
        )
    if node.function == "trim":
        return values[0].strip()
    if node.function == "starts_with":
        return values[0].startswith(values[1])
    return _matches_restricted_pattern(values[0], values[1])


def _matches_restricted_pattern(value: str, pattern: str) -> bool:
    if len(value) > MATCHES_MAX_INPUT_LENGTH:
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="matches",
            reason="matches_input_length_exceeded",
        )
    if len(pattern) > MATCHES_MAX_PATTERN_LENGTH:
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="matches",
            reason="matches_pattern_length_exceeded",
        )
    tokens = _parse_restricted_pattern(pattern)
    reachable = frozenset({0})
    for matcher, repeated in tokens:
        next_positions: set[int] = set()
        # At most pattern_length * input_length steps; never invoke a regex engine.
        for position, character in enumerate(value):
            if (position in reachable or (repeated and position in next_positions)) and matcher(character):
                next_positions.add(position + 1)
        reachable = frozenset(next_positions)
        if not reachable:
            return False
    return len(value) in reachable


def _parse_restricted_pattern(
    pattern: str,
) -> tuple[tuple[Callable[[str], bool], bool], ...]:
    if len(pattern) < 2 or not pattern.startswith("^") or not pattern.endswith("$"):
        _matches_pattern_error("matches_pattern_must_be_whole_string_anchored")
    body = pattern[1:-1]
    tokens: list[tuple[Callable[[str], bool], bool]] = []
    index = 0
    while index < len(body):
        character = body[index]
        if character == "\\":
            if index + 1 >= len(body) or body[index + 1].isalnum():
                _matches_pattern_error("matches_escape_not_supported")
            literal = body[index + 1]
            matcher = lambda candidate, expected=literal: candidate == expected
            index += 2
        elif character == "[":
            close = body.find("]", index + 1)
            if close < 0:
                _matches_pattern_error("matches_character_class_malformed")
            matcher = _character_class_matcher(body[index + 1:close])
            index = close + 1
        elif character in _MATCHES_FORBIDDEN_LITERAL_CHARACTERS:
            _matches_pattern_error("matches_construct_not_supported")
        else:
            matcher = lambda candidate, expected=character: candidate == expected
            index += 1
        repeated = index < len(body) and body[index] == "+"
        if repeated:
            index += 1
        tokens.append((matcher, repeated))
    return tuple(tokens)


def _character_class_matcher(source: str) -> Callable[[str], bool]:
    if not source or any(character in "[]\\^" for character in source):
        _matches_pattern_error("matches_character_class_malformed")
    literals: set[str] = set()
    ranges: list[tuple[int, int]] = []
    index = 0
    while index < len(source):
        if index + 1 < len(source) and source[index + 1] == "-":
            if index + 2 >= len(source) or source[index] == "-" or source[index + 2] == "-":
                _matches_pattern_error("matches_character_class_malformed")
            start, end = ord(source[index]), ord(source[index + 2])
            if start > end:
                _matches_pattern_error("matches_character_class_range_invalid")
            ranges.append((start, end))
            index += 3
            continue
        if source[index] == "-":
            _matches_pattern_error("matches_character_class_malformed")
        literals.add(source[index])
        index += 1
    frozen_literals = frozenset(literals)
    frozen_ranges = tuple(ranges)
    return lambda candidate: (
        candidate in frozen_literals
        or any(start <= ord(candidate) <= end for start, end in frozen_ranges)
    )


def _matches_pattern_error(reason: str) -> None:
    raise ValidationExpressionEvaluationError(
        node_type="Call",
        builtin="matches",
        reason=reason,
    )


def _evaluate_template_binding_shape_valid(
    node: expression_ast.Call,
    identifiers: Mapping[str, EvaluationAtom],
    lookup_resolver: LookupResolver | None,
    record_lookup_resolver: RecordLookupResolver | None,
    schema_version_resolver: SchemaVersionResolver | None,
) -> bool:
    if len(node.arguments) != 4:
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="template_binding_shape_valid",
            reason="template_binding_shape_arity_invalid",
        )
    (
        binding_kind_id,
        parameter_contract_field_id,
        source_node_key,
        fixed_values,
    ) = tuple(
        _evaluate_node(
            argument,
            identifiers,
            lookup_resolver,
            record_lookup_resolver,
            schema_version_resolver,
        )
        for argument in node.arguments
    )
    if type(binding_kind_id) is not str:
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="template_binding_shape_valid",
            reason="template_binding_shape_kind_type_invalid",
        )
    if parameter_contract_field_id is not None and (
        type(parameter_contract_field_id) is not str
    ):
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="template_binding_shape_valid",
            reason="template_binding_shape_parameter_type_invalid",
        )
    if source_node_key is not None and type(source_node_key) is not str:
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="template_binding_shape_valid",
            reason="template_binding_shape_source_type_invalid",
        )
    if type(fixed_values) is not tuple:
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="template_binding_shape_valid",
            reason="template_binding_shape_fixed_values_container_invalid",
        )
    if len(fixed_values) != 5:
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="template_binding_shape_valid",
            reason="template_binding_shape_fixed_values_length_invalid",
        )
    if any(
        type(value) not in {type(None), bool, int, str}
        for value in fixed_values
    ):
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="template_binding_shape_valid",
            reason="template_binding_shape_fixed_value_type_invalid",
        )

    fixed_count = sum(value is not None for value in fixed_values)
    parameter_present = parameter_contract_field_id is not None
    source_present = source_node_key is not None
    if binding_kind_id == "fixed_value":
        return fixed_count == 1 and not parameter_present and not source_present
    if binding_kind_id == "template_parameter":
        return parameter_present and not source_present and fixed_count == 0
    if binding_kind_id == "generated_node_id":
        return source_present and not parameter_present and fixed_count == 0
    if binding_kind_id == "explicit_null":
        return not parameter_present and not source_present and fixed_count == 0
    return False


def _evaluate_template_argument_value_type_valid(
    node: expression_ast.Call,
    identifiers: Mapping[str, EvaluationAtom],
    lookup_resolver: LookupResolver | None,
    record_lookup_resolver: RecordLookupResolver | None,
    schema_version_resolver: SchemaVersionResolver | None,
) -> bool:
    if len(node.arguments) != 7:
        _typed_contract_error(
            _TEMPLATE_ARGUMENT_BUILTIN,
            "template_argument_value_type_arity_invalid",
        )
    values = tuple(
        _evaluate_node(
            argument,
            identifiers,
            lookup_resolver,
            record_lookup_resolver,
            schema_version_resolver,
        )
        for argument in node.arguments
    )
    contract_field_id = values[0]
    channels = values[1:]
    if type(contract_field_id) is not str or not contract_field_id:
        _typed_contract_error(
            _TEMPLATE_ARGUMENT_BUILTIN,
            "template_argument_contract_field_id_invalid",
        )
    if any(not _is_canonical_scalar(value) for value in channels):
        _typed_contract_error(
            _TEMPLATE_ARGUMENT_BUILTIN,
            "template_argument_channel_value_invalid",
        )

    populated = tuple(
        index for index, value in enumerate(channels) if value is not None
    )
    if len(populated) != 1:
        return False
    contract = _resolve_unique_active_authority_record(
        identifiers,
        "registry:contract_fields",
        "contract_field_id",
        contract_field_id,
        _TEMPLATE_ARGUMENT_BUILTIN,
        "template_argument_contract_field",
    )
    if contract is None:
        return False
    contract_kind = _contract_field_kind(
        contract, _TEMPLATE_ARGUMENT_BUILTIN, "template_argument_contract"
    )
    channel_index = populated[0]
    value = channels[channel_index]

    if contract_kind == "ambiguous":
        return False
    if channel_index == 5:
        return (
            type(value) is str
            and (
                contract_kind != "scalar"
                or _scalar_type_class(contract["data_type"]) is not None
            )
        )
    if contract.get("is_collection") is True:
        return False
    if contract_kind == "controlled":
        return (
            channel_index == 3
            and type(value) is str
            and _registry_group_of(
                identifiers, value, _TEMPLATE_ARGUMENT_BUILTIN
            )
            == contract["allowed_group_id"]
        )
    if contract_kind == "reference":
        return channel_index == 4 and type(value) is str
    return _scalar_channel_matches(contract["data_type"], channel_index, value)


def _evaluate_template_binding_value_type_valid(
    node: expression_ast.Call,
    identifiers: Mapping[str, EvaluationAtom],
    lookup_resolver: LookupResolver | None,
    record_lookup_resolver: RecordLookupResolver | None,
    schema_version_resolver: SchemaVersionResolver | None,
) -> bool:
    if len(node.arguments) != 8:
        _typed_contract_error(
            _TEMPLATE_BINDING_BUILTIN,
            "template_binding_value_type_arity_invalid",
        )
    values = tuple(
        _evaluate_node(
            argument,
            identifiers,
            lookup_resolver,
            record_lookup_resolver,
            schema_version_resolver,
        )
        for argument in node.arguments
    )
    target_field_id, binding_kind_id, parameter_contract_field_id = values[:3]
    fixed_values = values[3:]
    if type(target_field_id) is not str or not target_field_id:
        _typed_contract_error(
            _TEMPLATE_BINDING_BUILTIN,
            "template_binding_target_field_id_invalid",
        )
    if type(binding_kind_id) is not str:
        _typed_contract_error(
            _TEMPLATE_BINDING_BUILTIN,
            "template_binding_kind_id_invalid",
        )
    if parameter_contract_field_id is not None and (
        type(parameter_contract_field_id) is not str
    ):
        _typed_contract_error(
            _TEMPLATE_BINDING_BUILTIN,
            "template_binding_parameter_contract_field_id_invalid",
        )
    if any(not _is_canonical_scalar(value) for value in fixed_values):
        _typed_contract_error(
            _TEMPLATE_BINDING_BUILTIN,
            "template_binding_fixed_channel_value_invalid",
        )

    target = _resolve_unique_active_authority_record(
        identifiers,
        "carddatabase:schema_fields",
        "field_id",
        target_field_id,
        _TEMPLATE_BINDING_BUILTIN,
        "template_binding_target_field",
    )
    if target is None:
        return False
    target_kind = _schema_field_kind(
        target, _TEMPLATE_BINDING_BUILTIN, "template_binding_target"
    )
    fixed_count = sum(value is not None for value in fixed_values)

    if binding_kind_id == "fixed_value":
        if parameter_contract_field_id is not None or fixed_count != 1:
            return False
        channel_index = next(
            index for index, value in enumerate(fixed_values)
            if value is not None
        )
        value = fixed_values[channel_index]
        if target_kind == "controlled":
            return (
                channel_index == 3
                and type(value) is str
                and _registry_group_of(
                    identifiers, value, _TEMPLATE_BINDING_BUILTIN
                )
                == target["allowed_group_id"]
            )
        if target_kind == "physical_reference":
            reference = _physical_reference_target(
                identifiers, target, _TEMPLATE_BINDING_BUILTIN
            )
            if reference is None:
                return False
            reference_namespace, reference_table_id = reference
            if (
                reference_namespace == "registry"
                and reference_table_id == "value_registry"
            ):
                return (
                    channel_index == 3
                    and type(value) is str
                    and _registry_group_of(
                        identifiers, value, _TEMPLATE_BINDING_BUILTIN
                    )
                    is not None
                )
            return channel_index == 4 and type(value) is str
        return _scalar_channel_matches(
            target["data_type"], channel_index, value
        )

    if binding_kind_id == "template_parameter":
        if (
            type(parameter_contract_field_id) is not str
            or not parameter_contract_field_id
            or fixed_count != 0
        ):
            return False
        contract = _resolve_unique_active_authority_record(
            identifiers,
            "registry:contract_fields",
            "contract_field_id",
            parameter_contract_field_id,
            _TEMPLATE_BINDING_BUILTIN,
            "template_binding_parameter_contract",
        )
        if contract is None:
            return False
        contract_kind = _contract_field_kind(
            contract,
            _TEMPLATE_BINDING_BUILTIN,
            "template_binding_parameter_contract",
        )
        if contract.get("is_collection") is True or contract_kind == "ambiguous":
            return False
        if contract_kind == "controlled":
            return (
                target_kind == "controlled"
                and target.get("allowed_group_id")
                == contract.get("allowed_group_id")
            )
        if contract_kind == "reference":
            return False
        return (
            target_kind == "scalar"
            and _scalar_type_class(target["data_type"])
            == _scalar_type_class(contract["data_type"])
            and _scalar_type_class(contract["data_type"]) is not None
        )

    if binding_kind_id == "generated_node_id":
        return (
            parameter_contract_field_id is None
            and fixed_count == 0
            and target_kind == "physical_reference"
            and _physical_reference_target(
                identifiers, target, _TEMPLATE_BINDING_BUILTIN
            )
            is not None
        )

    if binding_kind_id == "explicit_null":
        return (
            parameter_contract_field_id is None
            and fixed_count == 0
            and target.get("nullable") is True
            and target.get("null_handling") != "forbidden"
        )
    return False


def _typed_contract_error(builtin: str, reason: str) -> None:
    raise ValidationExpressionEvaluationError(
        node_type="Call", builtin=builtin, reason=reason
    )


def _authority_table(
    identifiers: Mapping[str, EvaluationAtom],
    table_token: str,
    builtin: str,
) -> tuple[Mapping[str, CanonicalScalar], ...]:
    resolver = getattr(identifiers, "table_resolver", None)
    if resolver is None:
        raise ValidationExpressionUnsupportedError(
            node_type="Call",
            builtin=builtin,
            reason="typed_contract_table_resolver_missing",
        )
    try:
        records = resolver(table_token)
    except ValidationExpressionEvaluationError:
        raise
    except Exception as error:
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin=builtin,
            reason="typed_contract_table_resolution_failed",
        ) from error
    if records is None:
        _typed_contract_error(builtin, "typed_contract_authority_table_missing")
    if isinstance(records, (str, bytes, bytearray)) or not isinstance(
        records, Sequence
    ):
        _typed_contract_error(builtin, "typed_contract_authority_table_invalid")
    copied = []
    for record in records:
        if (
            not isinstance(record, Mapping)
            or any(type(name) is not str or not name for name in record)
            or any(not _is_canonical_scalar(value) for value in record.values())
        ):
            _typed_contract_error(
                builtin, "typed_contract_authority_record_invalid"
            )
        copied.append(record)
    return tuple(copied)


def _resolve_unique_active_authority_record(
    identifiers: Mapping[str, EvaluationAtom],
    table_token: str,
    key_field: str,
    key_value: str,
    builtin: str,
    reason_prefix: str,
) -> Mapping[str, CanonicalScalar] | None:
    records = _authority_table(identifiers, table_token, builtin)
    exact = tuple(record for record in records if record.get(key_field) == key_value)
    for record in exact:
        if type(record.get("status")) is not str:
            _typed_contract_error(builtin, f"{reason_prefix}_status_invalid")
    active = tuple(record for record in exact if record.get("status") == "active")
    if not active:
        return None
    if len(active) != 1:
        _typed_contract_error(builtin, f"{reason_prefix}_ambiguous")
    return active[0]


def _contract_field_kind(
    record: Mapping[str, CanonicalScalar],
    builtin: str,
    reason_prefix: str,
) -> str:
    required = (
        "contract_field_id",
        "data_type",
        "nullable",
        "null_handling",
        "allowed_group_id",
        "reference_type_id",
        "is_collection",
    )
    if any(name not in record for name in required):
        _typed_contract_error(builtin, f"{reason_prefix}_metadata_missing")
    if type(record["contract_field_id"]) is not str or not record["contract_field_id"]:
        _typed_contract_error(builtin, f"{reason_prefix}_identity_invalid")
    if type(record["data_type"]) is not str or not record["data_type"]:
        _typed_contract_error(builtin, f"{reason_prefix}_data_type_invalid")
    if type(record["nullable"]) is not bool:
        _typed_contract_error(builtin, f"{reason_prefix}_nullable_invalid")
    expected_null_handling = (
        "explicit_null" if record["nullable"] else "forbidden"
    )
    if record["null_handling"] != expected_null_handling:
        _typed_contract_error(builtin, f"{reason_prefix}_null_handling_invalid")
    if type(record["is_collection"]) is not bool:
        _typed_contract_error(builtin, f"{reason_prefix}_is_collection_invalid")
    for name in ("allowed_group_id", "reference_type_id"):
        value = record[name]
        if value is not None and (type(value) is not str or not value):
            _typed_contract_error(builtin, f"{reason_prefix}_{name}_invalid")
    if record["allowed_group_id"] is not None and record["reference_type_id"] is not None:
        return "ambiguous"
    if record["allowed_group_id"] is not None:
        return "controlled"
    if record["reference_type_id"] is not None:
        return "reference"
    return "scalar"


def _schema_field_kind(
    record: Mapping[str, CanonicalScalar],
    builtin: str,
    reason_prefix: str,
) -> str:
    required = (
        "field_id",
        "field_name",
        "table_id",
        "data_type",
        "nullable",
        "null_handling",
        "allowed_group_id",
        "reference_table_id",
        "reference_field_id",
    )
    if any(name not in record for name in required):
        _typed_contract_error(builtin, f"{reason_prefix}_metadata_missing")
    for name in ("field_id", "field_name", "table_id", "data_type"):
        if type(record[name]) is not str or not record[name]:
            _typed_contract_error(builtin, f"{reason_prefix}_{name}_invalid")
    if type(record["nullable"]) is not bool:
        _typed_contract_error(builtin, f"{reason_prefix}_nullable_invalid")
    if record["null_handling"] not in {
        "forbidden", "explicit_null", "blank_is_null"
    }:
        _typed_contract_error(builtin, f"{reason_prefix}_null_handling_invalid")
    for name in ("allowed_group_id", "reference_table_id", "reference_field_id"):
        value = record[name]
        if value is not None and (type(value) is not str or not value):
            _typed_contract_error(builtin, f"{reason_prefix}_{name}_invalid")
    if (record["reference_table_id"] is None) != (
        record["reference_field_id"] is None
    ):
        _typed_contract_error(builtin, f"{reason_prefix}_reference_pair_invalid")
    if record["allowed_group_id"] is not None:
        return "controlled"
    if record["reference_table_id"] is not None:
        return "physical_reference"
    return "scalar"


def _physical_reference_target(
    identifiers: Mapping[str, EvaluationAtom],
    target: Mapping[str, CanonicalScalar],
    builtin: str,
) -> tuple[str, str] | None:
    table_token = target["reference_table_id"]
    field_token = target["reference_field_id"]
    assert isinstance(table_token, str) and isinstance(field_token, str)
    table_parts = table_token.split(":")
    if len(table_parts) == 1:
        namespace, table_id = "carddatabase", table_parts[0]
        if ":" in field_token:
            return None
        field_id = field_token
    elif len(table_parts) == 2:
        namespace, table_id = table_parts
        field_parts = field_token.split(":")
        if len(field_parts) != 2 or field_parts[0] != namespace:
            return None
        field_id = field_parts[1]
    else:
        return None
    if not all(
        _typed_contract_logical_identifier(value)
        for value in (namespace, table_id, field_id)
    ):
        return None
    referenced_field = _resolve_unique_active_authority_record(
        identifiers,
        f"{namespace}:schema_fields",
        "field_id",
        field_id,
        builtin,
        "template_binding_reference_field",
    )
    if referenced_field is None:
        return None
    _schema_field_kind(
        referenced_field, builtin, "template_binding_reference_field"
    )
    if referenced_field.get("table_id") != table_id:
        return None
    schema_table = _resolve_unique_active_authority_record(
        identifiers,
        f"{namespace}:schema_tables",
        "table_id",
        table_id,
        builtin,
        "template_binding_reference_table",
    )
    if schema_table is None:
        return None
    primary_key = schema_table.get("primary_key")
    if type(primary_key) is not str or not primary_key:
        _typed_contract_error(
            builtin, "template_binding_reference_primary_key_invalid"
        )
    if referenced_field.get("field_name") != primary_key:
        return None
    return namespace, table_id


def _registry_group_of(
    identifiers: Mapping[str, EvaluationAtom], value: str, builtin: str
) -> str | None:
    resolver = getattr(identifiers, "registry_group_resolver", None)
    if resolver is None:
        raise ValidationExpressionUnsupportedError(
            node_type="Call",
            builtin=builtin,
            reason="registry_group_resolver_missing",
        )
    try:
        group_id = resolver(value)
    except ValidationExpressionEvaluationError:
        raise
    except Exception as error:
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin=builtin,
            reason="registry_group_resolution_failed",
        ) from error
    if group_id is not None and (type(group_id) is not str or not group_id):
        _typed_contract_error(builtin, "registry_group_result_invalid")
    return group_id


def _scalar_type_class(data_type: object) -> str | None:
    if data_type == "boolean":
        return "boolean"
    if data_type == "integer":
        return "integer"
    if data_type in _TEXT_LIKE_DATA_TYPES:
        return "text"
    return None


def _typed_contract_logical_identifier(value: object) -> bool:
    return (
        type(value) is str
        and bool(value)
        and "a" <= value[0] <= "z"
        and all(
            "a" <= character <= "z"
            or "0" <= character <= "9"
            or character == "_"
            for character in value
        )
    )


def _scalar_channel_matches(
    data_type: object, channel_index: int, value: object
) -> bool:
    kind = _scalar_type_class(data_type)
    if kind == "boolean":
        return channel_index == 0 and type(value) is bool
    if kind == "integer":
        return channel_index == 1 and type(value) is int
    if kind == "text":
        return channel_index == 2 and type(value) is str
    return False


def _evaluate_count(
    node: expression_ast.Call,
    identifiers: Mapping[str, EvaluationAtom],
    lookup_resolver: LookupResolver | None,
    record_lookup_resolver: RecordLookupResolver | None,
    schema_version_resolver: SchemaVersionResolver | None,
) -> int:
    if len(node.arguments) != 2:
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="count",
            reason="count_arity_invalid",
        )
    table_token = _evaluate_node(
        node.arguments[0],
        identifiers,
        lookup_resolver,
        record_lookup_resolver,
        schema_version_resolver,
    )
    if type(table_token) is not str or not table_token:
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="count",
            reason="count_table_token_invalid",
        )
    table_resolver = getattr(identifiers, "table_resolver", None)
    if table_resolver is None:
        raise ValidationExpressionUnsupportedError(
            node_type="Call",
            builtin="count",
            reason="table_resolver_missing",
        )
    try:
        resolved_records = table_resolver(table_token)
    except ValidationExpressionEvaluationError:
        raise
    except Exception as error:
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="count",
            reason="count_table_resolution_failed",
        ) from error
    if resolved_records is None:
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="count",
            reason="count_table_missing",
        )
    if isinstance(resolved_records, (str, bytes)) or not isinstance(
        resolved_records, Sequence
    ):
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="count",
            reason="count_table_result_type_invalid",
        )

    records = []
    for record in resolved_records:
        if not _is_canonical_record(record):
            raise ValidationExpressionEvaluationError(
                node_type="Call",
                builtin="count",
                reason="count_candidate_record_invalid",
            )
        records.append(_freeze_record(record))

    matches = 0
    predicate = node.arguments[1]
    protected_names = (
        getattr(identifiers, "protected_names", frozenset())
        | frozenset({"current"})
    )
    for record in sorted(records, key=_canonical_record_sort_key):
        nested_values = dict(identifiers)
        nested_values.update(
            (name, value)
            for name, value in record.items()
            if name not in protected_names
        )
        nested_environment = _EvaluationEnvironment(
            nested_values,
            exists_resolver=getattr(identifiers, "exists_resolver", None),
            primary_key_resolver=getattr(
                identifiers, "primary_key_resolver", None
            ),
            protected_names=protected_names,
            record_lookup_by_resolver=getattr(
                identifiers, "record_lookup_by_resolver", None
            ),
            registry_group_resolver=getattr(
                identifiers, "registry_group_resolver", None
            ),
            table_resolver=table_resolver,
            value_of_resolver=getattr(
                identifiers, "value_of_resolver", None
            ),
        )
        result = _evaluate_node(
            predicate,
            nested_environment,
            lookup_resolver,
            record_lookup_resolver,
            schema_version_resolver,
        )
        _require_bool(result, node_type="Call", builtin="count")
        if result:
            matches += 1
    return matches


def _evaluate_normalize_search_name_hu(
    node: expression_ast.Call,
    identifiers: Mapping[str, EvaluationAtom],
    lookup_resolver: LookupResolver | None,
    record_lookup_resolver: RecordLookupResolver | None,
    schema_version_resolver: SchemaVersionResolver | None,
) -> str:
    if len(node.arguments) != 1:
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="normalize_search_name_hu",
            reason="normalize_search_name_hu_arity_invalid",
        )
    value = _evaluate_node(
        node.arguments[0],
        identifiers,
        lookup_resolver,
        record_lookup_resolver,
        schema_version_resolver,
    )
    if type(value) is not str:
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="normalize_search_name_hu",
            reason="normalize_search_name_hu_input_type_invalid",
        )
    normalized = unicodedata.normalize("NFKC", value).lower()
    return " ".join(normalized.split())


def _evaluate_normalize(
    node: expression_ast.Call,
    identifiers: Mapping[str, EvaluationAtom],
    lookup_resolver: LookupResolver | None,
    record_lookup_resolver: RecordLookupResolver | None,
    schema_version_resolver: SchemaVersionResolver | None,
) -> str:
    if len(node.arguments) != 3:
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="normalize",
            reason="normalize_arity_invalid",
        )
    value, normalization_mode, case_sensitive = tuple(
        _evaluate_node(
            argument,
            identifiers,
            lookup_resolver,
            record_lookup_resolver,
            schema_version_resolver,
        )
        for argument in node.arguments
    )
    if type(value) is not str:
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="normalize",
            reason="normalize_value_type_invalid",
        )
    if type(normalization_mode) is not str:
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="normalize",
            reason="normalize_mode_type_invalid",
        )
    if type(case_sensitive) is not bool:
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="normalize",
            reason="normalize_case_sensitive_type_invalid",
        )
    if normalization_mode == "exact":
        if case_sensitive is not True:
            raise ValidationExpressionEvaluationError(
                node_type="Call",
                builtin="normalize",
                reason="normalize_mode_case_sensitive_invalid",
            )
        return value
    if normalization_mode == "trim_casefold":
        if case_sensitive is not False:
            raise ValidationExpressionEvaluationError(
                node_type="Call",
                builtin="normalize",
                reason="normalize_mode_case_sensitive_invalid",
            )
        return value.strip().casefold()
    raise ValidationExpressionEvaluationError(
        node_type="Call",
        builtin="normalize",
        reason="normalize_mode_unknown",
    )


def _evaluate_group_of(
    node: expression_ast.Call,
    identifiers: Mapping[str, EvaluationAtom],
    lookup_resolver: LookupResolver | None,
    record_lookup_resolver: RecordLookupResolver | None,
    schema_version_resolver: SchemaVersionResolver | None,
) -> str | None:
    if len(node.arguments) != 1:
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="group_of",
            reason="group_of_arity_invalid",
        )
    registry_value_id = _evaluate_node(
        node.arguments[0],
        identifiers,
        lookup_resolver,
        record_lookup_resolver,
        schema_version_resolver,
    )
    if type(registry_value_id) is not str or not registry_value_id:
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="group_of",
            reason="group_of_registry_value_id_invalid",
        )
    resolver = getattr(identifiers, "registry_group_resolver", None)
    if resolver is None:
        raise ValidationExpressionUnsupportedError(
            node_type="Call",
            builtin="group_of",
            reason="registry_group_resolver_missing",
        )
    group_id = resolver(registry_value_id)
    if group_id is not None and (
        type(group_id) is not str or not group_id
    ):
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="group_of",
            reason="group_of_result_invalid",
        )
    return group_id


def _evaluate_cardinality(
    node: expression_ast.Call,
    identifiers: Mapping[str, EvaluationAtom],
    lookup_resolver: LookupResolver | None,
    record_lookup_resolver: RecordLookupResolver | None,
    schema_version_resolver: SchemaVersionResolver | None,
) -> int | bool:
    if len(node.arguments) != 1:
        raise ValidationExpressionUnsupportedError(
            node_type="Call",
            builtin=node.function,
            reason="builtin_arity_not_supported",
        )
    collection = _evaluate_node(
        node.arguments[0],
        identifiers,
        lookup_resolver,
        record_lookup_resolver,
        schema_version_resolver,
    )
    if type(collection) is not tuple:
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin=node.function,
            reason="collection_argument_required",
        )
    non_null_count = sum(item is not None for item in collection)
    if node.function == "count_non_null":
        return non_null_count
    if node.function == "at_least_one_non_null":
        return non_null_count >= 1
    return non_null_count <= 1


def _evaluate_lookup(
    node: expression_ast.Call,
    identifiers: Mapping[str, EvaluationAtom],
    lookup_resolver: LookupResolver | None,
    record_lookup_resolver: RecordLookupResolver | None,
    schema_version_resolver: SchemaVersionResolver | None,
) -> CanonicalScalar:
    if lookup_resolver is None:
        raise ValidationExpressionUnsupportedError(
            node_type="Call",
            builtin="lookup",
            reason="lookup_resolver_missing",
        )
    if len(node.arguments) != 4:
        raise ValidationExpressionUnsupportedError(
            node_type="Call",
            builtin="lookup",
            reason="builtin_arity_not_supported",
        )
    table, key_field, key_expression, output_field = node.arguments
    tokens = (
        (table, "lookup_table_token_not_string_literal"),
        (key_field, "lookup_key_field_not_string_literal"),
        (output_field, "lookup_output_field_not_string_literal"),
    )
    for token, reason in tokens:
        if not (
            isinstance(token, expression_ast.Literal)
            and token.literal_kind == "string"
            and type(token.value) is str
            and bool(token.value)
        ):
            raise ValidationExpressionUnsupportedError(
                node_type="Call",
                builtin="lookup",
                reason=reason,
            )
    key_value = _evaluate_node(
        key_expression,
        identifiers,
        lookup_resolver,
        record_lookup_resolver,
        schema_version_resolver,
    )
    if not _is_canonical_scalar(key_value):
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="lookup",
            reason="lookup_key_value_type_unsupported",
        )
    result = lookup_resolver(
        table.value,
        key_field.value,
        key_value,
        output_field.value,
    )
    if not _is_canonical_scalar(result):
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="lookup",
            reason="lookup_result_type_unsupported",
        )
    return result


def _evaluate_exists(
    node: expression_ast.Call,
    identifiers: Mapping[str, EvaluationAtom],
    lookup_resolver: LookupResolver | None,
    record_lookup_resolver: RecordLookupResolver | None,
    schema_version_resolver: SchemaVersionResolver | None,
) -> bool:
    resolver = getattr(identifiers, "exists_resolver", None)
    if resolver is None:
        raise ValidationExpressionUnsupportedError(
            node_type="Call",
            builtin="exists",
            reason="exists_resolver_missing",
        )
    if len(node.arguments) != 3:
        raise ValidationExpressionUnsupportedError(
            node_type="Call",
            builtin="exists",
            reason="builtin_arity_not_supported",
        )
    table_source, key_field, key_value = tuple(
        _evaluate_node(
            argument,
            identifiers,
            lookup_resolver,
            record_lookup_resolver,
            schema_version_resolver,
        )
        for argument in node.arguments
    )
    if type(table_source) is not str or not table_source:
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="exists",
            reason="exists_table_source_invalid",
        )
    if type(key_field) is not str or not key_field:
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="exists",
            reason="exists_key_field_invalid",
        )
    if key_value is None:
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="exists",
            reason="exists_null_key_value",
        )
    if not _is_canonical_scalar(key_value):
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="exists",
            reason="exists_key_value_type_unsupported",
        )
    result = resolver(table_source, key_field, key_value)
    if type(result) is not bool:
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="exists",
            reason="exists_result_type_invalid",
        )
    return result


def _evaluate_value_of(
    node: expression_ast.Call,
    identifiers: Mapping[str, EvaluationAtom],
    lookup_resolver: LookupResolver | None,
    record_lookup_resolver: RecordLookupResolver | None,
    schema_version_resolver: SchemaVersionResolver | None,
) -> str | None:
    resolver = getattr(identifiers, "value_of_resolver", None)
    if resolver is None:
        raise ValidationExpressionUnsupportedError(
            node_type="Call",
            builtin="value_of",
            reason="value_of_resolver_missing",
        )
    if len(node.arguments) != 1:
        raise ValidationExpressionUnsupportedError(
            node_type="Call",
            builtin="value_of",
            reason="builtin_arity_not_supported",
        )
    registry_value_id = _evaluate_node(
        node.arguments[0],
        identifiers,
        lookup_resolver,
        record_lookup_resolver,
        schema_version_resolver,
    )
    if type(registry_value_id) is not str or not registry_value_id:
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="value_of",
            reason="value_of_registry_value_id_invalid",
        )
    result = resolver(registry_value_id)
    if result is not None and (type(result) is not str or not result):
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="value_of",
            reason="value_of_result_invalid",
        )
    return result


def _evaluate_primary_key_of(
    node: expression_ast.Call,
    identifiers: Mapping[str, EvaluationAtom],
    lookup_resolver: LookupResolver | None,
    record_lookup_resolver: RecordLookupResolver | None,
    schema_version_resolver: SchemaVersionResolver | None,
) -> str:
    resolver = getattr(identifiers, "primary_key_resolver", None)
    if resolver is None:
        raise ValidationExpressionUnsupportedError(
            node_type="Call",
            builtin="primary_key_of",
            reason="primary_key_resolver_missing",
        )
    if len(node.arguments) != 1:
        raise ValidationExpressionUnsupportedError(
            node_type="Call",
            builtin="primary_key_of",
            reason="builtin_arity_not_supported",
        )
    table_source = _evaluate_node(
        node.arguments[0],
        identifiers,
        lookup_resolver,
        record_lookup_resolver,
        schema_version_resolver,
    )
    if type(table_source) is not str or not table_source:
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="primary_key_of",
            reason="primary_key_table_source_invalid",
        )
    result = resolver(table_source)
    if type(result) is not str or not result:
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="primary_key_of",
            reason="primary_key_result_invalid",
        )
    return result


def _evaluate_record_lookup(
    node: expression_ast.Call,
    identifiers: Mapping[str, EvaluationAtom],
    lookup_resolver: LookupResolver | None,
    record_lookup_resolver: RecordLookupResolver | None,
    schema_version_resolver: SchemaVersionResolver | None,
) -> CanonicalRecord | None:
    if record_lookup_resolver is None:
        raise ValidationExpressionUnsupportedError(
            node_type="Call",
            builtin="lookup_record",
            reason="record_lookup_resolver_missing",
        )
    if len(node.arguments) != 3:
        raise ValidationExpressionUnsupportedError(
            node_type="Call",
            builtin="lookup_record",
            reason="builtin_arity_not_supported",
        )
    table, key_field, key_expression = node.arguments
    tokens = (
        (table, "lookup_record_table_token_not_string_literal"),
        (key_field, "lookup_record_key_field_not_string_literal"),
    )
    for token, reason in tokens:
        if not (
            isinstance(token, expression_ast.Literal)
            and token.literal_kind == "string"
            and type(token.value) is str
            and bool(token.value)
        ):
            raise ValidationExpressionUnsupportedError(
                node_type="Call",
                builtin="lookup_record",
                reason=reason,
            )
    key_value = _evaluate_node(
        key_expression,
        identifiers,
        lookup_resolver,
        record_lookup_resolver,
        schema_version_resolver,
    )
    if not _is_canonical_scalar(key_value):
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="lookup_record",
            reason="lookup_record_key_value_type_unsupported",
        )
    result = record_lookup_resolver(
        table.value, key_field.value, key_value
    )
    if result is None:
        return None
    if not _is_canonical_record(result):
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="lookup_record",
            reason="lookup_record_result_type_unsupported",
        )
    return _freeze_record(result)


def _evaluate_record_lookup_by(
    node: expression_ast.Call,
    identifiers: Mapping[str, EvaluationAtom],
    lookup_resolver: LookupResolver | None,
    record_lookup_resolver: RecordLookupResolver | None,
    schema_version_resolver: SchemaVersionResolver | None,
) -> CanonicalRecord | None:
    resolver = getattr(identifiers, "record_lookup_by_resolver", None)
    if resolver is None:
        raise ValidationExpressionUnsupportedError(
            node_type="Call",
            builtin="lookup_record_by",
            reason="record_lookup_by_resolver_missing",
        )
    if len(node.arguments) != 3:
        raise ValidationExpressionUnsupportedError(
            node_type="Call",
            builtin="lookup_record_by",
            reason="builtin_arity_not_supported",
        )
    table, key_fields_expression, key_values_expression = node.arguments
    if not (
        isinstance(table, expression_ast.Literal)
        and table.literal_kind == "string"
        and type(table.value) is str
        and bool(table.value)
    ):
        raise ValidationExpressionUnsupportedError(
            node_type="Call",
            builtin="lookup_record_by",
            reason="lookup_record_by_table_token_not_string_literal",
        )
    key_fields = _evaluate_node(
        key_fields_expression,
        identifiers,
        lookup_resolver,
        record_lookup_resolver,
        schema_version_resolver,
    )
    key_values = _evaluate_node(
        key_values_expression,
        identifiers,
        lookup_resolver,
        record_lookup_resolver,
        schema_version_resolver,
    )
    if not isinstance(key_fields, tuple):
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="lookup_record_by",
            reason="lookup_record_by_key_fields_collection_required",
        )
    if not key_fields:
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="lookup_record_by",
            reason="lookup_record_by_key_fields_empty",
        )
    if any(type(field) is not str or not field for field in key_fields):
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="lookup_record_by",
            reason="lookup_record_by_key_field_invalid",
        )
    if len(set(key_fields)) != len(key_fields):
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="lookup_record_by",
            reason="lookup_record_by_key_field_duplicate",
        )
    if not isinstance(key_values, tuple):
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="lookup_record_by",
            reason="lookup_record_by_key_values_collection_required",
        )
    if len(key_values) != len(key_fields):
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="lookup_record_by",
            reason="lookup_record_by_key_arity_mismatch",
        )
    for value in key_values:
        if value is None:
            raise ValidationExpressionEvaluationError(
                node_type="Call",
                builtin="lookup_record_by",
                reason="lookup_record_by_null_key_value",
            )
        if not _is_canonical_scalar(value):
            raise ValidationExpressionEvaluationError(
                node_type="Call",
                builtin="lookup_record_by",
                reason="lookup_record_by_key_value_type_unsupported",
            )
    result = resolver(table.value, key_fields, key_values)
    if result is None:
        return None
    if not _is_canonical_record(result):
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="lookup_record_by",
            reason="lookup_record_by_result_type_unsupported",
        )
    return _freeze_record(result)


def _evaluate_current_schema_version(
    node: expression_ast.Call,
    identifiers: Mapping[str, EvaluationAtom],
    lookup_resolver: LookupResolver | None,
    record_lookup_resolver: RecordLookupResolver | None,
    schema_version_resolver: SchemaVersionResolver | None,
) -> str:
    if schema_version_resolver is None:
        raise ValidationExpressionUnsupportedError(
            node_type="Call",
            builtin="current_schema_version",
            reason="schema_version_resolver_missing",
        )
    if len(node.arguments) != 1:
        raise ValidationExpressionUnsupportedError(
            node_type="Call",
            builtin="current_schema_version",
            reason="builtin_arity_not_supported",
        )
    component_id = _evaluate_node(
        node.arguments[0],
        identifiers,
        lookup_resolver,
        record_lookup_resolver,
        schema_version_resolver,
    )
    if type(component_id) is not str or not component_id:
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="current_schema_version",
            reason="component_identifier_invalid",
        )
    try:
        version = schema_version_resolver(component_id)
    except ValidationExpressionEvaluationError:
        raise
    except Exception as error:
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="current_schema_version",
            reason="schema_version_resolution_failed",
        ) from error
    if type(version) is not str:
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin="current_schema_version",
            reason="schema_version_result_type_invalid",
        )
    _parse_canonical_version(
        version,
        builtin="current_schema_version",
        reason="schema_version_malformed",
    )
    return version


def _evaluate_version_gte(
    node: expression_ast.Call,
    identifiers: Mapping[str, EvaluationAtom],
    lookup_resolver: LookupResolver | None,
    record_lookup_resolver: RecordLookupResolver | None,
    schema_version_resolver: SchemaVersionResolver | None,
) -> bool:
    if len(node.arguments) != 2:
        raise ValidationExpressionUnsupportedError(
            node_type="Call",
            builtin="version_gte",
            reason="builtin_arity_not_supported",
        )
    values = tuple(
        _evaluate_node(
            argument,
            identifiers,
            lookup_resolver,
            record_lookup_resolver,
            schema_version_resolver,
        )
        for argument in node.arguments
    )
    parsed = []
    for index, value in enumerate(values):
        if type(value) is not str:
            raise ValidationExpressionEvaluationError(
                node_type="Call",
                builtin="version_gte",
                reason=f"version_argument_{index}_type_invalid",
            )
        parsed.append(
            _parse_canonical_version(
                value,
                builtin="version_gte",
                reason=f"version_argument_{index}_malformed",
            )
        )
    return parsed[0] >= parsed[1]


def _parse_canonical_version(
    value: str,
    *,
    builtin: str,
    reason: str,
) -> tuple[tuple[int, str], tuple[int, str], tuple[int, str]]:
    components = value.split(".")
    if (
        len(components) != 3
        or any(
            not component
            or any(character < "0" or character > "9" for character in component)
            or (len(component) > 1 and component.startswith("0"))
            for component in components
        )
    ):
        raise ValidationExpressionEvaluationError(
            node_type="Call",
            builtin=builtin,
            reason=reason,
        )
    return tuple((len(component), component) for component in components)


def _evaluate_member_access(
    node: expression_ast.MemberAccess,
    identifiers: Mapping[str, EvaluationAtom],
    lookup_resolver: LookupResolver | None,
    record_lookup_resolver: RecordLookupResolver | None,
    schema_version_resolver: SchemaVersionResolver | None,
) -> CanonicalScalar:
    target = _evaluate_node(
        node.target,
        identifiers,
        lookup_resolver,
        record_lookup_resolver,
        schema_version_resolver,
    )
    if target is None:
        raise ValidationExpressionEvaluationError(
            node_type="MemberAccess",
            identifier=node.member,
            reason="member_access_base_is_none",
        )
    if not _is_canonical_record(target):
        raise ValidationExpressionEvaluationError(
            node_type="MemberAccess",
            identifier=node.member,
            reason="member_access_base_not_record",
        )
    if type(node.member) is not str or not node.member:
        raise ValidationExpressionEvaluationError(
            node_type="MemberAccess",
            reason="member_name_invalid",
        )
    if node.member not in target:
        raise ValidationExpressionEvaluationError(
            node_type="MemberAccess",
            identifier=node.member,
            reason="member_missing",
        )
    value = target[node.member]
    if not _is_canonical_scalar(value):
        raise ValidationExpressionEvaluationError(
            node_type="MemberAccess",
            identifier=node.member,
            reason="member_value_type_unsupported",
        )
    return value


def _require_bool(
    value: EvaluationValue,
    *,
    node_type: str,
    operator: str | None = None,
    builtin: str | None = None,
) -> None:
    if type(value) is not bool:
        raise ValidationExpressionEvaluationError(
            node_type=node_type,
            operator=operator,
            builtin=builtin,
            reason="boolean_operand_required",
        )


def _typed_equal(left: EvaluationValue, right: EvaluationValue) -> bool:
    if type(left) is not type(right):
        return False
    if isinstance(left, tuple):
        return len(left) == len(right) and all(
            _typed_equal(left_item, right_item)
            for left_item, right_item in zip(left, right)
        )
    return left == right


def _is_canonical_scalar(value: object) -> bool:
    return value is None or type(value) in {bool, int, str}


def _is_canonical_record(value: object) -> bool:
    return (
        isinstance(value, MappingProxyType)
        and all(type(name) is str and bool(name) for name in value)
        and all(_is_canonical_scalar(item) for item in value.values())
    )


def _is_evaluation_atom(value: object) -> bool:
    return _is_canonical_scalar(value) or _is_canonical_record(value)


def _freeze_record(record: CanonicalRecord) -> CanonicalRecord:
    copied = {
        name: record[name]
        for name in sorted(record, key=lambda item: item.encode("utf-8"))
    }
    return MappingProxyType(copied)


def _canonical_record_sort_key(
    record: CanonicalRecord,
) -> tuple[tuple[bytes, int, bytes], ...]:
    def scalar_key(value: CanonicalScalar) -> tuple[int, bytes]:
        if value is None:
            return 0, b""
        if type(value) is bool:
            return 1, b"1" if value else b"0"
        if type(value) is int:
            return 2, str(value).encode("ascii")
        return 3, value.encode("utf-8")

    return tuple(
        (name.encode("utf-8"), *scalar_key(record[name]))
        for name in sorted(record, key=lambda item: item.encode("utf-8"))
    )


__all__ = [
    "ValidationExpressionEvaluationError",
    "ValidationExpressionUnsupportedError",
    "evaluate_validation_expression",
]
