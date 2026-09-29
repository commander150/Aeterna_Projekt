"""Safe parser and immutable AST contract for AETERNA validation expressions.

This module intentionally stops at syntax, builtin signatures, canonical AST
projection, and semantic identity.  It does not evaluate validation rules and
does not dereference workbook, runtime, or Python objects.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, TypeAlias

try:  # Package import when the tools directory is on sys.path.
    from .canonical_package_set import canonical_json_bytes, sha256_bytes
except ImportError:  # Direct file loading used by the repository test suite.
    from canonical_package_set import canonical_json_bytes, sha256_bytes


EXPRESSION_LANGUAGE = "aeterna_validation_expr_v1"
AST_FORMAT_VERSION = "aeterna_validation_ast_v1"
AST_HASH_DOMAIN = "aeterna-validation-ast-v1"

WHEN_FALSE_GUARD_OUTCOME = "constraint_satisfied"
WHEN_PRODUCES_NOT_APPLICABLE = False
SEQUENCE_CONSTRAINT_COMBINATION = "conjunction"

INT64_MIN = -(2**63)
INT64_MAX = 2**63 - 1

LEXICAL_ERROR = "VALIDATION_EXPR_LEXICAL_ERROR"
SYNTAX_ERROR = "VALIDATION_EXPR_SYNTAX_ERROR"
LITERAL_INVALID = "VALIDATION_EXPR_LITERAL_INVALID"
INTEGER_RANGE = "VALIDATION_EXPR_INTEGER_RANGE"
UNKNOWN_BUILTIN = "VALIDATION_EXPR_UNKNOWN_BUILTIN"
ARITY_MISMATCH = "VALIDATION_EXPR_ARITY_MISMATCH"
UNSUPPORTED_SYNTAX = "VALIDATION_EXPR_UNSUPPORTED_SYNTAX"
LIMIT_EXCEEDED = "VALIDATION_EXPR_LIMIT_EXCEEDED"


@dataclass(frozen=True, slots=True)
class ParserLimits:
    max_source_length: int = 16_384
    max_tokens: int = 512
    max_nesting_depth: int = 64
    max_string_length: int = 8_192
    max_collection_items: int = 512
    max_sequence_statements: int = 256


DEFAULT_LIMITS = ParserLimits()


@dataclass(frozen=True, slots=True)
class ValidationExpressionDiagnostic:
    code: str
    message: str
    offset: int
    line: int
    column: int
    context: tuple[tuple[str, str | int], ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "offset": self.offset,
            "line": self.line,
            "column": self.column,
            "context": {key: value for key, value in self.context},
        }


class ValidationExpressionError(ValueError):
    """A deterministic, machine-readable validation-expression failure."""

    def __init__(self, diagnostics: tuple[ValidationExpressionDiagnostic, ...]):
        self.diagnostics = diagnostics
        super().__init__(
            "; ".join(f"{item.code}: {item.message}" for item in diagnostics)
        )


@dataclass(frozen=True, slots=True)
class Token:
    kind: str
    value: str | int | bool | None
    start: int
    end: int
    line: int
    column: int


@dataclass(frozen=True, slots=True)
class Literal:
    literal_kind: str
    value: str | int | bool | None


@dataclass(frozen=True, slots=True)
class TbdLiteral:
    pass


@dataclass(frozen=True, slots=True)
class Identifier:
    name: str


@dataclass(frozen=True, slots=True)
class ListLiteral:
    items: tuple["AstNode", ...]


@dataclass(frozen=True, slots=True)
class MapLiteral:
    items: tuple[tuple[str, str], ...]


@dataclass(frozen=True, slots=True)
class UnaryOperation:
    operator: str
    operand: "AstNode"


@dataclass(frozen=True, slots=True)
class BinaryOperation:
    operator: str
    left: "AstNode"
    right: "AstNode"


@dataclass(frozen=True, slots=True)
class Call:
    function: str
    arguments: tuple["AstNode", ...]


@dataclass(frozen=True, slots=True)
class MemberAccess:
    target: "AstNode"
    member: str


@dataclass(frozen=True, slots=True)
class Binding:
    name: str
    value: "AstNode"


@dataclass(frozen=True, slots=True)
class Sequence:
    statements: tuple["AstNode", ...]


AstNode: TypeAlias = (
    Literal
    | TbdLiteral
    | Identifier
    | ListLiteral
    | MapLiteral
    | UnaryOperation
    | BinaryOperation
    | Call
    | MemberAccess
    | Binding
    | Sequence
)


@dataclass(frozen=True, slots=True)
class BuiltinSignature:
    name: str
    allowed_arities: tuple[int, ...]
    result_category: str
    execution_domain: str
    semantic_status: str


@dataclass(frozen=True, slots=True)
class ValidationBuiltinCatalog:
    """Immutable allowlist of the signatures observed in the current corpus."""

    entries: tuple[BuiltinSignature, ...]

    def __post_init__(self) -> None:
        ordered = tuple(sorted(self.entries, key=lambda item: item.name.encode("utf-8")))
        if len({entry.name for entry in ordered}) != len(ordered):
            raise ValueError("Builtin catalog names must be unique.")
        object.__setattr__(self, "entries", ordered)

    @property
    def names(self) -> frozenset[str]:
        return frozenset(entry.name for entry in self.entries)

    def get(self, name: str) -> BuiltinSignature | None:
        return next((entry for entry in self.entries if entry.name == name), None)

    def __len__(self) -> int:
        return len(self.entries)


def _builtin(
    name: str,
    arities: int | tuple[int, ...],
    result: str,
    domain: str = "mixed",
    status: str = "execution_deferred",
) -> BuiltinSignature:
    allowed = (arities,) if isinstance(arities, int) else arities
    return BuiltinSignature(name, allowed, result, domain, status)


BUILTIN_CATALOG = ValidationBuiltinCatalog(
    (
        _builtin("all_non_null_controlled_values_resolve", 4, "boolean", "structural"),
        _builtin("all_non_null_references_resolve", 4, "boolean", "structural"),
        _builtin("all_non_null_references_resolve_namespaced", 4, "boolean", "structural"),
        _builtin("all_non_null_values_in_group", 3, "boolean", "structural"),
        _builtin("all_primary_keys_non_null_unique", 2, "boolean", "structural"),
        _builtin("all_required_contract_fields_present", 5, "boolean", "structural"),
        _builtin("all_required_contract_fields_present_for_template", 3, "boolean", "structural"),
        _builtin("all_required_fields_present", 1, "boolean", "structural"),
        _builtin("all_unique", 1, "boolean"),
        _builtin("at_least_one_non_null", 1, "boolean"),
        _builtin("at_most_one_non_null", 1, "boolean"),
        _builtin("contains_sentinel", 1, "boolean", "structural"),
        _builtin("count", (1, 2), "integer"),
        _builtin("count_distinct", 1, "integer"),
        _builtin("count_non_null", 1, "integer"),
        _builtin("count_rows", 0, "integer"),
        _builtin("current_schema_version", 1, "version", "structural"),
        _builtin("destination_parameter_context_valid", 4, "boolean", "structural"),
        _builtin("event_by_zone_transition_instance_id", 1, "record", "runtime"),
        _builtin("exists", 3, "boolean"),
        _builtin("export_order", 1, "integer", "structural"),
        _builtin("expression_is_reachable_only_from_target_filter", 4, "boolean", "structural"),
        _builtin("for_each_exported_table", 1, "boolean", "structural"),
        _builtin("for_each_group", 2, "boolean"),
        _builtin("for_each_schema_field", 2, "boolean", "structural"),
        _builtin("for_each_schema_table", 2, "boolean", "structural"),
        _builtin("group_of", 1, "string"),
        _builtin("headers_match_active_schema", 1, "boolean", "structural"),
        _builtin("hierarchy_is_acyclic", 2, "boolean", "structural"),
        _builtin("lookup", 4, "scalar"),
        _builtin("lookup_record", 3, "record"),
        _builtin("lookup_record_by", 3, "record"),
        _builtin("map", 2, "scalar"),
        _builtin("matches", 2, "boolean"),
        _builtin("no_self_reference", 2, "boolean", "structural"),
        _builtin("no_source_rows_for_template_nodes", 3, "boolean", "structural"),
        _builtin("normalize", 3, "string"),
        _builtin("normalize_search_name_hu", 1, "string"),
        _builtin("primary_key_of", 1, "scalar", "structural"),
        _builtin("prior_event", 3, "record", "runtime"),
        _builtin("range", 2, "collection"),
        _builtin("sorted_unique", 1, "collection"),
        _builtin("starts_with", 2, "boolean"),
        _builtin("sum", 3, "integer"),
        _builtin("template_argument_value_type_valid", 7, "boolean", "structural"),
        _builtin("template_binding_shape_valid", 4, "boolean", "structural"),
        _builtin("template_binding_value_type_valid", 8, "boolean", "structural"),
        _builtin("template_node_required_fields_materializable", 3, "boolean", "structural"),
        _builtin("trim", 1, "string"),
        _builtin("unique_by", 1, "boolean", "structural"),
        _builtin("unique_non_null_by", 1, "boolean", "structural"),
        _builtin("value_of", 1, "scalar"),
        _builtin("version_gte", 2, "boolean", "structural"),
        _builtin("when", 2, "boolean", "mixed", "confirmed"),
    )
)


_KEYWORDS = {
    "and": "AND",
    "or": "OR",
    "not": "NOT",
    "in": "IN",
    "true": "TRUE",
    "false": "FALSE",
    "null": "NULL",
    "tbd": "TBD",
}
_UNSUPPORTED_WORDS = frozenset({"lambda", "import", "def", "for", "while"})
_TWO_CHARACTER_TOKENS = {"!=": "NE", "<=": "LTE", ">=": "GTE", "==": "EQ"}
_ONE_CHARACTER_TOKENS = {
    "(": "LPAREN",
    ")": "RPAREN",
    "[": "LBRACKET",
    "]": "RBRACKET",
    "{": "LBRACE",
    "}": "RBRACE",
    ",": "COMMA",
    ".": "DOT",
    ":": "COLON",
    ";": "SEMICOLON",
    "+": "PLUS",
    "-": "MINUS",
    "<": "LT",
    ">": "GT",
    "=": "ASSIGN",
}


def tokenize_validation_expression(
    source: str, *, limits: ParserLimits = DEFAULT_LIMITS
) -> tuple[Token, ...]:
    if not isinstance(source, str):
        _raise_at(LEXICAL_ERROR, "Expression source must be a string.", 0, 1, 1)
    if len(source) > limits.max_source_length:
        _raise_at(
            LIMIT_EXCEEDED,
            "Expression source length exceeds the configured limit.",
            0,
            1,
            1,
            actual=len(source),
            limit=limits.max_source_length,
            limit_name="max_source_length",
        )
    for offset, character in enumerate(source):
        if 0xD800 <= ord(character) <= 0xDFFF:
            line, column = _line_column(source, offset)
            _raise_at(
                LITERAL_INVALID,
                "Expression source contains a lone Unicode surrogate.",
                offset,
                line,
                column,
            )

    tokens: list[Token] = []
    offset = 0
    line = 1
    column = 1

    def emit(kind: str, value: str | int | bool | None, start: int, start_line: int, start_column: int) -> None:
        if len(tokens) >= limits.max_tokens:
            _raise_at(
                LIMIT_EXCEEDED,
                "Token count exceeds the configured limit.",
                start,
                start_line,
                start_column,
                actual=len(tokens) + 1,
                limit=limits.max_tokens,
                limit_name="max_tokens",
            )
        tokens.append(Token(kind, value, start, offset, start_line, start_column))

    while offset < len(source):
        character = source[offset]
        if character in " \t\r\n":
            if character == "\n":
                line += 1
                column = 1
            else:
                column += 1
            offset += 1
            continue

        start, start_line, start_column = offset, line, column
        pair = source[offset : offset + 2]
        if pair in _TWO_CHARACTER_TOKENS:
            offset += 2
            column += 2
            emit(_TWO_CHARACTER_TOKENS[pair], pair, start, start_line, start_column)
            continue

        if character == '"':
            offset += 1
            column += 1
            while offset < len(source):
                current = source[offset]
                if current == '"':
                    offset += 1
                    column += 1
                    break
                if current == "\n" or current == "\r":
                    _raise_at(
                        LITERAL_INVALID,
                        "String literals cannot contain an unescaped line break.",
                        offset,
                        line,
                        column,
                    )
                if current == "\\":
                    offset += 1
                    column += 1
                    if offset >= len(source):
                        break
                offset += 1
                column += 1
            else:
                _raise_at(
                    LITERAL_INVALID,
                    "Unterminated string literal.",
                    start,
                    start_line,
                    start_column,
                )
            raw = source[start:offset]
            try:
                value = json.loads(raw)
            except (json.JSONDecodeError, UnicodeDecodeError) as error:
                _raise_at(
                    LITERAL_INVALID,
                    "String literal is not valid JSON string syntax.",
                    start,
                    start_line,
                    start_column,
                    detail=str(error),
                )
            if not isinstance(value, str):
                _raise_at(
                    LITERAL_INVALID,
                    "String literal must contain Unicode scalar values only.",
                    start,
                    start_line,
                    start_column,
                )
            value = _decode_json_surrogate_pairs(
                value, start, start_line, start_column
            )
            if len(value) > limits.max_string_length:
                _raise_at(
                    LIMIT_EXCEEDED,
                    "Decoded string length exceeds the configured limit.",
                    start,
                    start_line,
                    start_column,
                    actual=len(value),
                    limit=limits.max_string_length,
                    limit_name="max_string_length",
                )
            emit("STRING", value, start, start_line, start_column)
            continue

        if character.isascii() and (character.isalpha() or character == "_"):
            offset += 1
            column += 1
            while offset < len(source) and source[offset].isascii() and (
                source[offset].isalnum() or source[offset] == "_"
            ):
                offset += 1
                column += 1
            value = source[start:offset]
            if value in _UNSUPPORTED_WORDS:
                _raise_at(
                    UNSUPPORTED_SYNTAX,
                    f"The '{value}' syntax is not part of the validation language.",
                    start,
                    start_line,
                    start_column,
                    syntax=value,
                )
            emit(_KEYWORDS.get(value, "IDENTIFIER"), value, start, start_line, start_column)
            continue

        if character.isascii() and character.isdigit():
            offset += 1
            column += 1
            while offset < len(source) and source[offset].isascii() and source[offset].isdigit():
                offset += 1
                column += 1
            if offset < len(source) - 1 and source[offset] == "." and source[offset + 1].isdigit():
                _raise_at(
                    UNSUPPORTED_SYNTAX,
                    "Float literals are not part of the validation language.",
                    start,
                    start_line,
                    start_column,
                    syntax="float",
                )
            emit("INTEGER", source[start:offset], start, start_line, start_column)
            continue

        if character == "'":
            _raise_at(
                UNSUPPORTED_SYNTAX,
                "Single-quoted strings are not part of the validation language.",
                start,
                start_line,
                start_column,
                syntax="single_quoted_string",
            )
        if character in "*/%&|^~":
            _raise_at(
                UNSUPPORTED_SYNTAX,
                f"Operator '{character}' is not part of the validation language.",
                start,
                start_line,
                start_column,
                syntax=character,
            )
        kind = _ONE_CHARACTER_TOKENS.get(character)
        if kind is not None:
            offset += 1
            column += 1
            emit(kind, character, start, start_line, start_column)
            continue
        _raise_at(
            LEXICAL_ERROR,
            "Unexpected character in validation expression.",
            start,
            start_line,
            start_column,
            character=character,
        )

    tokens.append(Token("EOF", None, offset, offset, line, column))
    return tuple(tokens)


class _Parser:
    def __init__(self, tokens: tuple[Token, ...], limits: ParserLimits):
        self.tokens = tokens
        self.limits = limits
        self.index = 0
        self.nesting_depth = 0

    @property
    def current(self) -> Token:
        return self.tokens[self.index]

    def peek(self, distance: int = 1) -> Token:
        return self.tokens[min(self.index + distance, len(self.tokens) - 1)]

    def take(self, kind: str) -> Token:
        token = self.current
        if token.kind != kind:
            self.fail(SYNTAX_ERROR, f"Expected {kind}, found {token.kind}.", token)
        self.index += 1
        return token

    def enter_nesting(self, token: Token) -> None:
        self.nesting_depth += 1
        if self.nesting_depth > self.limits.max_nesting_depth:
            self.fail(
                LIMIT_EXCEEDED,
                "Nesting depth exceeds the configured limit.",
                token,
                actual=self.nesting_depth,
                limit=self.limits.max_nesting_depth,
                limit_name="max_nesting_depth",
            )

    def leave_nesting(self) -> None:
        self.nesting_depth -= 1

    def fail(self, code: str, message: str, token: Token, **context: str | int) -> None:
        _raise_at(code, message, token.start, token.line, token.column, **context)

    def parse(self) -> AstNode:
        if self.current.kind == "EOF":
            self.fail(SYNTAX_ERROR, "Expression source cannot be empty.", self.current)
        result = self.parse_sequence(frozenset({"EOF"}))
        if self.current.kind != "EOF":
            code = UNSUPPORTED_SYNTAX if self.current.kind == "ASSIGN" else SYNTAX_ERROR
            self.fail(code, f"Unexpected token {self.current.kind}.", self.current)
        return result

    def parse_sequence(self, stop_kinds: frozenset[str]) -> AstNode:
        statements = [self.parse_statement()]
        while self.current.kind == "SEMICOLON":
            separator = self.take("SEMICOLON")
            if self.current.kind in stop_kinds or self.current.kind == "EOF":
                self.fail(SYNTAX_ERROR, "A sequence cannot end with a semicolon.", separator)
            statements.append(self.parse_statement())
            if len(statements) > self.limits.max_sequence_statements:
                self.fail(
                    LIMIT_EXCEEDED,
                    "Sequence statement count exceeds the configured limit.",
                    separator,
                    actual=len(statements),
                    limit=self.limits.max_sequence_statements,
                    limit_name="max_sequence_statements",
                )
        return statements[0] if len(statements) == 1 else Sequence(tuple(statements))

    def parse_statement(self) -> AstNode:
        if self.current.kind == "IDENTIFIER" and self.peek().kind == "ASSIGN":
            name = str(self.take("IDENTIFIER").value)
            self.take("ASSIGN")
            return Binding(name, self.parse_or())
        return self.parse_or()

    def parse_or(self) -> AstNode:
        result = self.parse_and()
        while self.current.kind == "OR":
            self.take("OR")
            result = BinaryOperation("or", result, self.parse_and())
        return result

    def parse_and(self) -> AstNode:
        result = self.parse_comparison()
        while self.current.kind == "AND":
            self.take("AND")
            result = BinaryOperation("and", result, self.parse_comparison())
        return result

    def parse_comparison(self) -> AstNode:
        result = self.parse_additive()
        operators = {
            "EQ": "==",
            "NE": "!=",
            "LT": "<",
            "LTE": "<=",
            "GT": ">",
            "GTE": ">=",
            "IN": "in",
        }
        while True:
            if self.current.kind == "NOT" and self.peek().kind == "IN":
                self.take("NOT")
                self.take("IN")
                operator = "not in"
            elif self.current.kind in operators:
                operator = operators[self.current.kind]
                self.index += 1
            else:
                break
            result = BinaryOperation(operator, result, self.parse_additive())
        return result

    def parse_additive(self) -> AstNode:
        result = self.parse_unary()
        while self.current.kind in {"PLUS", "MINUS"}:
            operator = "+" if self.current.kind == "PLUS" else "-"
            self.index += 1
            result = BinaryOperation(operator, result, self.parse_unary())
        return result

    def parse_unary(self) -> AstNode:
        if self.current.kind == "NOT":
            self.take("NOT")
            return UnaryOperation("not", self.parse_unary())
        if self.current.kind in {"PLUS", "MINUS"}:
            sign_token = self.current
            sign = 1 if sign_token.kind == "PLUS" else -1
            self.index += 1
            if self.current.kind != "INTEGER":
                self.fail(
                    UNSUPPORTED_SYNTAX,
                    "Unary plus/minus is supported only as an integer sign.",
                    sign_token,
                )
            token = self.take("INTEGER")
            return self.integer_literal(str(token.value), sign, sign_token)
        return self.parse_postfix()

    def parse_postfix(self) -> AstNode:
        result = self.parse_primary()
        while True:
            if self.current.kind == "LPAREN":
                if not isinstance(result, Identifier):
                    self.fail(
                        UNSUPPORTED_SYNTAX,
                        "Only allowlisted builtin identifiers can be called.",
                        self.current,
                    )
                result = self.parse_call(result.name)
                continue
            if self.current.kind == "DOT":
                self.take("DOT")
                member = self.take("IDENTIFIER")
                name = str(member.value)
                if name.startswith("__"):
                    self.fail(
                        UNSUPPORTED_SYNTAX,
                        "Protected member access is not part of the validation language.",
                        member,
                        member=name,
                    )
                result = MemberAccess(result, name)
                continue
            if self.current.kind == "LBRACKET":
                self.fail(
                    UNSUPPORTED_SYNTAX,
                    "Indexing and slicing are not part of the validation language.",
                    self.current,
                )
            break
        return result

    def parse_primary(self) -> AstNode:
        token = self.current
        if token.kind == "INTEGER":
            self.index += 1
            return self.integer_literal(str(token.value), 1, token)
        if token.kind == "STRING":
            self.index += 1
            return Literal("string", str(token.value))
        if token.kind == "TRUE":
            self.index += 1
            return Literal("boolean", True)
        if token.kind == "FALSE":
            self.index += 1
            return Literal("boolean", False)
        if token.kind == "NULL":
            self.index += 1
            return Literal("null", None)
        if token.kind == "TBD":
            self.index += 1
            return TbdLiteral()
        if token.kind == "IDENTIFIER":
            self.index += 1
            name = str(token.value)
            if name.startswith("__"):
                self.fail(
                    UNSUPPORTED_SYNTAX,
                    "Protected identifiers are not part of the validation language.",
                    token,
                    identifier=name,
                )
            return Identifier(name)
        if token.kind == "LPAREN":
            opening = self.take("LPAREN")
            self.enter_nesting(opening)
            try:
                result = self.parse_sequence(frozenset({"RPAREN"}))
                self.take("RPAREN")
                return result
            finally:
                self.leave_nesting()
        if token.kind == "LBRACKET":
            return self.parse_list()
        if token.kind == "LBRACE":
            return self.parse_map()
        self.fail(SYNTAX_ERROR, f"Expected an expression, found {token.kind}.", token)

    def integer_literal(self, digits: str, sign: int, token: Token) -> Literal:
        value = int(digits) * sign
        if value < INT64_MIN or value > INT64_MAX:
            self.fail(
                INTEGER_RANGE,
                "Integer literal is outside the signed Int64 domain.",
                token,
                minimum=INT64_MIN,
                maximum=INT64_MAX,
            )
        return Literal("integer", value)

    def parse_call(self, function: str) -> Call:
        opening = self.take("LPAREN")
        self.enter_nesting(opening)
        arguments: list[AstNode] = []
        try:
            if self.current.kind != "RPAREN":
                while True:
                    arguments.append(
                        self.parse_sequence(frozenset({"COMMA", "RPAREN"}))
                    )
                    if len(arguments) > self.limits.max_collection_items:
                        self.fail(
                            LIMIT_EXCEEDED,
                            "Call argument count exceeds the configured limit.",
                            opening,
                            actual=len(arguments),
                            limit=self.limits.max_collection_items,
                            limit_name="max_collection_items",
                        )
                    if self.current.kind != "COMMA":
                        break
                    comma = self.take("COMMA")
                    if self.current.kind == "RPAREN":
                        self.fail(SYNTAX_ERROR, "Trailing call commas are not supported.", comma)
            self.take("RPAREN")
            return Call(function, tuple(arguments))
        finally:
            self.leave_nesting()

    def parse_list(self) -> ListLiteral:
        opening = self.take("LBRACKET")
        self.enter_nesting(opening)
        items: list[AstNode] = []
        try:
            if self.current.kind != "RBRACKET":
                while True:
                    items.append(self.parse_or())
                    if len(items) > self.limits.max_collection_items:
                        self.fail(
                            LIMIT_EXCEEDED,
                            "List item count exceeds the configured limit.",
                            opening,
                            actual=len(items),
                            limit=self.limits.max_collection_items,
                            limit_name="max_collection_items",
                        )
                    if self.current.kind != "COMMA":
                        break
                    comma = self.take("COMMA")
                    if self.current.kind == "RBRACKET":
                        self.fail(SYNTAX_ERROR, "Trailing list commas are not supported.", comma)
            self.take("RBRACKET")
            return ListLiteral(tuple(items))
        finally:
            self.leave_nesting()

    def parse_map(self) -> MapLiteral:
        opening = self.take("LBRACE")
        self.enter_nesting(opening)
        items: list[tuple[str, str]] = []
        seen: set[str] = set()
        try:
            if self.current.kind != "RBRACE":
                while True:
                    key_token = self.take("STRING")
                    self.take("COLON")
                    value_token = self.take("STRING")
                    key, value = str(key_token.value), str(value_token.value)
                    if key in seen:
                        self.fail(
                            LITERAL_INVALID,
                            "Map literal keys must be unique.",
                            key_token,
                            key=key,
                        )
                    seen.add(key)
                    items.append((key, value))
                    if len(items) > self.limits.max_collection_items:
                        self.fail(
                            LIMIT_EXCEEDED,
                            "Map item count exceeds the configured limit.",
                            opening,
                            actual=len(items),
                            limit=self.limits.max_collection_items,
                            limit_name="max_collection_items",
                        )
                    if self.current.kind != "COMMA":
                        break
                    comma = self.take("COMMA")
                    if self.current.kind == "RBRACE":
                        self.fail(SYNTAX_ERROR, "Trailing map commas are not supported.", comma)
            self.take("RBRACE")
            return MapLiteral(tuple(sorted(items, key=lambda item: item[0].encode("utf-8"))))
        finally:
            self.leave_nesting()


def parse_validation_expression(
    source: str,
    *,
    limits: ParserLimits = DEFAULT_LIMITS,
    validate_builtins: bool = True,
) -> AstNode:
    try:
        tokens = tokenize_validation_expression(source, limits=limits)
        root = _Parser(tokens, limits).parse()
        _validate_binding_placement(root, root_context=True)
        if validate_builtins:
            validate_builtin_signatures(root)
        return root
    except RecursionError:
        raise ValidationExpressionError(
            (
                _diagnostic(
                    LIMIT_EXCEEDED,
                    "Expression complexity exceeds the parser recursion safety boundary.",
                    0,
                    1,
                    1,
                    limit=limits.max_nesting_depth,
                    limit_name="python_recursion_boundary",
                ),
            )
        ) from None


def validate_builtin_signatures(
    root: AstNode, *, catalog: ValidationBuiltinCatalog = BUILTIN_CATALOG
) -> None:
    diagnostics: list[ValidationExpressionDiagnostic] = []
    for call in _walk_calls(root):
        signature = catalog.get(call.function)
        if signature is None:
            diagnostics.append(
                _diagnostic(
                    UNKNOWN_BUILTIN,
                    "Function name is not in the validation builtin catalog.",
                    0,
                    1,
                    1,
                    builtin=call.function,
                )
            )
        elif len(call.arguments) not in signature.allowed_arities:
            diagnostics.append(
                _diagnostic(
                    ARITY_MISMATCH,
                    "Builtin call arity does not match its catalog signature.",
                    0,
                    1,
                    1,
                    actual=len(call.arguments),
                    allowed=",".join(str(item) for item in signature.allowed_arities),
                    builtin=call.function,
                )
            )
    if diagnostics:
        raise ValidationExpressionError(tuple(diagnostics))


def called_builtin_names(root: AstNode) -> frozenset[str]:
    return frozenset(call.function for call in _walk_calls(root))


def canonical_ast_projection(root: AstNode) -> dict[str, Any]:
    return {
        "ast_format": AST_FORMAT_VERSION,
        "expression_language": EXPRESSION_LANGUAGE,
        "root": _project_node(root),
    }


def canonical_ast_bytes(root: AstNode) -> bytes:
    return canonical_json_bytes(canonical_ast_projection(root))


def semantic_ast_hash(root: AstNode) -> str:
    preimage = AST_HASH_DOMAIN.encode("utf-8") + b"\x00" + canonical_ast_bytes(root)
    return sha256_bytes(preimage)


def _project_node(node: AstNode) -> dict[str, Any]:
    if isinstance(node, Literal):
        return {"node": "literal", "kind": node.literal_kind, "value": node.value}
    if isinstance(node, TbdLiteral):
        return {"node": "tbd_literal"}
    if isinstance(node, Identifier):
        return {"node": "identifier", "name": node.name}
    if isinstance(node, ListLiteral):
        return {"node": "list", "items": [_project_node(item) for item in node.items]}
    if isinstance(node, MapLiteral):
        return {
            "node": "map",
            "items": [
                {"key": key, "value": value}
                for key, value in sorted(node.items, key=lambda item: item[0].encode("utf-8"))
            ],
        }
    if isinstance(node, UnaryOperation):
        return {"node": "unary", "operator": node.operator, "operand": _project_node(node.operand)}
    if isinstance(node, BinaryOperation):
        return {
            "node": "binary",
            "operator": node.operator,
            "left": _project_node(node.left),
            "right": _project_node(node.right),
        }
    if isinstance(node, Call):
        return {
            "node": "call",
            "function": node.function,
            "arguments": [_project_node(argument) for argument in node.arguments],
        }
    if isinstance(node, MemberAccess):
        return {"node": "member", "target": _project_node(node.target), "member": node.member}
    if isinstance(node, Binding):
        return {"node": "binding", "name": node.name, "value": _project_node(node.value)}
    if isinstance(node, Sequence):
        return {"node": "sequence", "statements": [_project_node(item) for item in node.statements]}
    raise TypeError(f"Unsupported AST node type: {type(node).__name__}")


def _walk_calls(root: AstNode) -> tuple[Call, ...]:
    calls: list[Call] = []

    def visit(node: AstNode) -> None:
        if isinstance(node, Call):
            calls.append(node)
            for argument in node.arguments:
                visit(argument)
        elif isinstance(node, (ListLiteral, Sequence)):
            for item in node.items if isinstance(node, ListLiteral) else node.statements:
                visit(item)
        elif isinstance(node, UnaryOperation):
            visit(node.operand)
        elif isinstance(node, BinaryOperation):
            visit(node.left)
            visit(node.right)
        elif isinstance(node, MemberAccess):
            visit(node.target)
        elif isinstance(node, Binding):
            visit(node.value)

    visit(root)
    return tuple(calls)


def _validate_binding_placement(node: AstNode, *, root_context: bool) -> None:
    def visit(current: AstNode, bindings_allowed: bool) -> None:
        if isinstance(current, Binding):
            if not bindings_allowed:
                _raise_at(
                    UNSUPPORTED_SYNTAX,
                    "Bindings are allowed only at sequence root or in a when constraint body.",
                    0,
                    1,
                    1,
                    binding=current.name,
                )
            visit(current.value, False)
        elif isinstance(current, Sequence):
            for statement in current.statements:
                visit(statement, bindings_allowed)
        elif isinstance(current, Call):
            for index, argument in enumerate(current.arguments):
                visit(argument, current.function == "when" and index == 1)
        elif isinstance(current, ListLiteral):
            for item in current.items:
                visit(item, False)
        elif isinstance(current, UnaryOperation):
            visit(current.operand, False)
        elif isinstance(current, BinaryOperation):
            visit(current.left, False)
            visit(current.right, False)
        elif isinstance(current, MemberAccess):
            visit(current.target, False)

    visit(node, root_context)


def _line_column(source: str, offset: int) -> tuple[int, int]:
    prefix = source[:offset]
    line = prefix.count("\n") + 1
    last_newline = prefix.rfind("\n")
    return line, offset + 1 if last_newline < 0 else offset - last_newline


def _decode_json_surrogate_pairs(
    value: str, offset: int, line: int, column: int
) -> str:
    scalars: list[str] = []
    index = 0
    while index < len(value):
        codepoint = ord(value[index])
        if 0xD800 <= codepoint <= 0xDBFF:
            if index + 1 >= len(value):
                _raise_at(
                    LITERAL_INVALID,
                    "String literal contains a lone Unicode surrogate.",
                    offset,
                    line,
                    column,
                )
            low = ord(value[index + 1])
            if not 0xDC00 <= low <= 0xDFFF:
                _raise_at(
                    LITERAL_INVALID,
                    "String literal contains a lone Unicode surrogate.",
                    offset,
                    line,
                    column,
                )
            scalars.append(chr(0x10000 + ((codepoint - 0xD800) << 10) + low - 0xDC00))
            index += 2
            continue
        if 0xDC00 <= codepoint <= 0xDFFF:
            _raise_at(
                LITERAL_INVALID,
                "String literal contains a lone Unicode surrogate.",
                offset,
                line,
                column,
            )
        scalars.append(value[index])
        index += 1
    return "".join(scalars)


def _diagnostic(
    code: str,
    message: str,
    offset: int,
    line: int,
    column: int,
    **context: str | int,
) -> ValidationExpressionDiagnostic:
    return ValidationExpressionDiagnostic(
        code,
        message,
        offset,
        line,
        column,
        tuple(sorted(context.items(), key=lambda item: item[0].encode("utf-8"))),
    )


def _raise_at(
    code: str,
    message: str,
    offset: int,
    line: int,
    column: int,
    **context: str | int,
) -> None:
    raise ValidationExpressionError(
        (_diagnostic(code, message, offset, line, column, **context),)
    )


__all__ = [
    "ARITY_MISMATCH", "AST_FORMAT_VERSION", "AST_HASH_DOMAIN", "AstNode",
    "BUILTIN_CATALOG", "Binding", "BinaryOperation", "BuiltinSignature", "Call",
    "DEFAULT_LIMITS", "EXPRESSION_LANGUAGE", "Identifier", "INTEGER_RANGE",
    "LEXICAL_ERROR", "LIMIT_EXCEEDED", "ListLiteral", "Literal", "LITERAL_INVALID",
    "MapLiteral", "MemberAccess", "ParserLimits", "SEQUENCE_CONSTRAINT_COMBINATION",
    "Sequence", "SYNTAX_ERROR", "TbdLiteral", "Token", "UNKNOWN_BUILTIN",
    "UNSUPPORTED_SYNTAX", "UnaryOperation", "ValidationBuiltinCatalog",
    "ValidationExpressionDiagnostic", "ValidationExpressionError",
    "WHEN_FALSE_GUARD_OUTCOME", "WHEN_PRODUCES_NOT_APPLICABLE",
    "called_builtin_names", "canonical_ast_bytes", "canonical_ast_projection",
    "parse_validation_expression", "semantic_ast_hash", "tokenize_validation_expression",
    "validate_builtin_signatures",
]
