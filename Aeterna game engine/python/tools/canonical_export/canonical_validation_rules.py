"""Pure static rule-record normalization, AST binding, and shape validation.

This module neither opens workbooks nor executes validation rules.
"""
from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, TypeAlias

try:  # Package import when the tools directory is on sys.path.
    from .canonical_validation_expr import (
        AstNode,
        BinaryOperation,
        Binding,
        Call,
        Identifier,
        ListLiteral,
        MapLiteral,
        MemberAccess,
        Sequence as AstSequence,
        TbdLiteral,
        UnaryOperation,
        ValidationExpressionDiagnostic,
        ValidationExpressionError,
        parse_validation_expression,
        semantic_ast_hash,
    )
except ImportError:  # Direct file loading used by the repository test suite.
    from canonical_validation_expr import (
        AstNode,
        BinaryOperation,
        Binding,
        Call,
        Identifier,
        ListLiteral,
        MapLiteral,
        MemberAccess,
        Sequence as AstSequence,
        TbdLiteral,
        UnaryOperation,
        ValidationExpressionDiagnostic,
        ValidationExpressionError,
        parse_validation_expression,
        semantic_ast_hash,
    )


VALIDATION_RULE_DUPLICATE_ID = "VALIDATION_RULE_DUPLICATE_ID"
VALIDATION_RULE_KIND_UNKNOWN = "VALIDATION_RULE_KIND_UNKNOWN"
VALIDATION_RULE_STAGE_UNKNOWN = "VALIDATION_RULE_STAGE_UNKNOWN"
VALIDATION_RULE_SEVERITY_UNKNOWN = "VALIDATION_RULE_SEVERITY_UNKNOWN"
VALIDATION_RULE_STATUS_INVALID = "VALIDATION_RULE_STATUS_INVALID"
VALIDATION_RULE_BLOCKING_INVALID = "VALIDATION_RULE_BLOCKING_INVALID"
VALIDATION_RULE_SHAPE_INVALID = "VALIDATION_RULE_SHAPE_INVALID"
VALIDATION_RULE_BINDING_FORWARD_REFERENCE = "VALIDATION_RULE_BINDING_FORWARD_REFERENCE"
VALIDATION_RULE_BINDING_REBIND = "VALIDATION_RULE_BINDING_REBIND"
VALIDATION_RULE_BINDING_RESERVED = "VALIDATION_RULE_BINDING_RESERVED"


RULE_RECORD_FIELDS = (
    "validation_rule_id",
    "rule_scope_id",
    "target_table_id",
    "target_field_id",
    "validation_kind_id",
    "condition_expression",
    "operator_id",
    "comparison_value",
    "minimum_value",
    "maximum_value",
    "reference_table_id",
    "reference_field_id",
    "severity_id",
    "blocking",
    "error_code",
    "message_key",
    "message",
    "validation_stage_id",
    "status",
    "source_id",
    "source_ref",
    "notes",
)

KNOWN_VALIDATION_KINDS = frozenset(
    {
        "allowed_value",
        "contract_field_invariant",
        "contract_instance_consistency",
        "cross_field_consistency",
        "custom_expression",
        "definition_invariant",
        "hierarchy_integrity",
        "normalized_uniqueness",
        "qualified_reference_match",
        "range",
        "reference_integrity",
        "target_group_membership",
        "uniqueness",
    }
)
KNOWN_VALIDATION_STAGES = frozenset(("pre_export", "production_export", "runtime_package_build", "runtime_load"))
KNOWN_SEVERITIES = frozenset({"critical", "error", "warning"})

_KNOWN_STATUSES = frozenset({"active"})
_KNOWN_RULE_SCOPES = frozenset(("field", "cross_table", "record", "table", "contract_instance"))
_SHAPE_FIELDS = (
    "target_table_id",
    "target_field_id",
    "condition_expression",
    "operator_id",
    "comparison_value",
    "minimum_value",
    "maximum_value",
    "reference_table_id",
    "reference_field_id",
)
_REQUIRED_TEXT_FIELDS = (
    "validation_rule_id",
    "rule_scope_id",
    "target_table_id",
    "validation_kind_id",
    "severity_id",
    "error_code",
    "message",
    "validation_stage_id",
    "status",
    "source_id",
    "source_ref",
)
_OPTIONAL_TEXT_FIELDS = (
    "target_field_id",
    "condition_expression",
    "operator_id",
    "reference_table_id",
    "reference_field_id",
    "message_key",
    "notes",
)
_UNIQUE_EXPRESSION_BUILTINS = frozenset({"unique_by", "unique_non_null_by"})

DiagnosticValue: TypeAlias = str | int | float | bool
StructuredScalar: TypeAlias = str | int | float


@dataclass(frozen=True, slots=True)
class ValidationRuleInput:
    record: Mapping[str, object]
    component_identity: str | None = None
    source_row: int | None = None


@dataclass(frozen=True, slots=True)
class ValidationRuleDiagnostic:
    code: str
    message: str
    rule_id: str | None = None
    component_identity: str | None = None
    source_row: int | None = None
    field_name: str | None = None
    offset: int | None = None
    line: int | None = None
    column: int | None = None
    context: tuple[tuple[str, DiagnosticValue], ...] = ()
    expression_diagnostic: ValidationExpressionDiagnostic | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "rule_id": self.rule_id,
            "component_identity": self.component_identity,
            "source_row": self.source_row,
            "field_name": self.field_name,
            "offset": self.offset,
            "line": self.line,
            "column": self.column,
            "context": {key: value for key, value in self.context},
            "expression_diagnostic": (
                None
                if self.expression_diagnostic is None
                else self.expression_diagnostic.as_dict()
            ),
        }


@dataclass(frozen=True, slots=True)
class ValidationRuleShapeVariant:
    name: str
    populated_fields: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ValidationRuleKindContract:
    kind: str
    variants: tuple[ValidationRuleShapeVariant, ...]


def _shape(name: str, *fields: str) -> ValidationRuleShapeVariant:
    ordered = tuple(field for field in _SHAPE_FIELDS if field in fields)
    return ValidationRuleShapeVariant(name, ordered)


def _contract(
    kind: str, *variants: tuple[str, tuple[str, ...]]
) -> ValidationRuleKindContract:
    return ValidationRuleKindContract(
        kind, tuple(_shape(name, *fields) for name, fields in variants)
    )


_TARGET_TABLE = "target_table_id"
_TARGET_FIELD = "target_field_id"
_EXPRESSION = "condition_expression"
_OPERATOR = "operator_id"
_COMPARISON = "comparison_value"
_MINIMUM = "minimum_value"
_REFERENCE_TABLE = "reference_table_id"
_REFERENCE_FIELD = "reference_field_id"

RULE_KIND_CONTRACTS = (
    _contract(
        "allowed_value",
        ("structured_allowed_value", (_TARGET_TABLE, _TARGET_FIELD, _OPERATOR, _COMPARISON)),
    ),
    _contract(
        "contract_field_invariant",
        ("field_expression", (_TARGET_TABLE, _TARGET_FIELD, _EXPRESSION)),
    ),
    _contract(
        "contract_instance_consistency",
        ("contract_schema_expression", (_TARGET_TABLE, _EXPRESSION, _COMPARISON)),
    ),
    _contract(
        "cross_field_consistency",
        (
            "cross_field_reference_expression",
            (_TARGET_TABLE, _TARGET_FIELD, _EXPRESSION, _REFERENCE_TABLE, _REFERENCE_FIELD),
        ),
    ),
    _contract(
        "custom_expression",
        ("table_expression", (_TARGET_TABLE, _EXPRESSION)),
        ("field_expression", (_TARGET_TABLE, _TARGET_FIELD, _EXPRESSION)),
        (
            "field_reference_expression",
            (_TARGET_TABLE, _TARGET_FIELD, _EXPRESSION, _REFERENCE_TABLE, _REFERENCE_FIELD),
        ),
    ),
    _contract(
        "definition_invariant",
        ("field_expression", (_TARGET_TABLE, _TARGET_FIELD, _EXPRESSION)),
        (
            "field_reference_expression",
            (_TARGET_TABLE, _TARGET_FIELD, _EXPRESSION, _REFERENCE_TABLE, _REFERENCE_FIELD),
        ),
    ),
    _contract(
        "hierarchy_integrity",
        ("hierarchy_expression", (_TARGET_TABLE, _TARGET_FIELD, _EXPRESSION)),
    ),
    _contract(
        "normalized_uniqueness",
        ("normalized_expression", (_TARGET_TABLE, _TARGET_FIELD, _EXPRESSION)),
    ),
    _contract(
        "qualified_reference_match",
        ("qualified_expression", (_TARGET_TABLE, _TARGET_FIELD, _EXPRESSION)),
        (
            "qualified_reference_expression",
            (_TARGET_TABLE, _TARGET_FIELD, _EXPRESSION, _REFERENCE_TABLE, _REFERENCE_FIELD),
        ),
    ),
    _contract(
        "range",
        (
            "structured_lower_bound",
            (_TARGET_TABLE, _TARGET_FIELD, _OPERATOR, _COMPARISON, _MINIMUM),
        ),
    ),
    _contract(
        "reference_integrity",
        (
            "structured_reference",
            (_TARGET_TABLE, _TARGET_FIELD, _REFERENCE_TABLE, _REFERENCE_FIELD),
        ),
        (
            "guarded_reference",
            (_TARGET_TABLE, _TARGET_FIELD, _EXPRESSION, _REFERENCE_TABLE, _REFERENCE_FIELD),
        ),
    ),
    _contract(
        "target_group_membership",
        (
            "mapped_reference_expression",
            (_TARGET_TABLE, _TARGET_FIELD, _EXPRESSION, _REFERENCE_TABLE, _REFERENCE_FIELD),
        ),
    ),
    _contract(
        "uniqueness",
        ("structured_field_uniqueness", (_TARGET_TABLE, _TARGET_FIELD)),
        ("explicit_uniqueness_expression", (_TARGET_TABLE, _TARGET_FIELD, _EXPRESSION)),
    ),
)


@dataclass(frozen=True, slots=True)
class ValidationRuleDefinition:
    rule_id: str
    rule_scope_id: str
    status: str
    validation_kind_id: str
    validation_stage_id: str
    severity_id: str
    blocking: bool
    target_table_id: str
    target_field_id: str | None
    condition_expression_source: str | None
    condition_ast: AstNode | None
    condition_ast_hash: str | None
    operator_id: str | None
    comparison_value: StructuredScalar | None
    minimum_value: StructuredScalar | None
    maximum_value: StructuredScalar | None
    reference_table_id: str | None
    reference_field_id: str | None
    error_code: str
    message_key: str | None
    message: str
    source_id: str
    source_ref: str
    notes: str | None
    free_identifiers: tuple[str, ...]
    local_bindings: tuple[str, ...]
    component_identity: str | None
    source_row: int | None


@dataclass(frozen=True, slots=True)
class ValidationRuleCatalog:
    rules: tuple[ValidationRuleDefinition, ...]

    def __post_init__(self) -> None:
        ordered = tuple(sorted(self.rules, key=lambda item: _utf8(item.rule_id)))
        if len({item.rule_id for item in ordered}) != len(ordered):
            raise ValueError("Validation rule IDs must be unique.")
        object.__setattr__(self, "rules", ordered)

    def __len__(self) -> int:
        return len(self.rules)

    def get(self, rule_id: str) -> ValidationRuleDefinition | None:
        return next((rule for rule in self.rules if rule.rule_id == rule_id), None)

    def by_kind(self, kind: str) -> tuple[ValidationRuleDefinition, ...]:
        return tuple(rule for rule in self.rules if rule.validation_kind_id == kind)

    def by_stage(self, stage: str) -> tuple[ValidationRuleDefinition, ...]:
        return tuple(rule for rule in self.rules if rule.validation_stage_id == stage)

    @property
    def expression_rules(self) -> tuple[ValidationRuleDefinition, ...]:
        return tuple(rule for rule in self.rules if rule.condition_ast is not None)

    @property
    def structured_only_rules(self) -> tuple[ValidationRuleDefinition, ...]:
        return tuple(rule for rule in self.rules if rule.condition_ast is None)

    @property
    def kind_counts(self) -> tuple[tuple[str, int], ...]:
        counts = Counter(rule.validation_kind_id for rule in self.rules)
        return tuple(sorted(counts.items(), key=lambda item: _utf8(item[0])))

    @property
    def stage_counts(self) -> tuple[tuple[str, int], ...]:
        counts = Counter(rule.validation_stage_id for rule in self.rules)
        return tuple(sorted(counts.items(), key=lambda item: _utf8(item[0])))


@dataclass(frozen=True, slots=True)
class ValidationRuleCatalogResult:
    catalog: ValidationRuleCatalog | None
    diagnostics: tuple[ValidationRuleDiagnostic, ...]

    @property
    def is_valid(self) -> bool:
        return self.catalog is not None and not self.diagnostics


@dataclass(frozen=True, slots=True)
class _SymbolIssue:
    code: str
    name: str


@dataclass(frozen=True, slots=True)
class _SymbolInventory:
    free_identifiers: tuple[str, ...]
    local_bindings: tuple[str, ...]
    issues: tuple[_SymbolIssue, ...]


def build_validation_rule_catalog(
    inputs: Sequence[Mapping[str, object] | ValidationRuleInput],
) -> ValidationRuleCatalogResult:
    normalized_inputs = tuple(_coerce_input(item) for item in inputs)
    ordered_inputs = tuple(sorted(normalized_inputs, key=_input_sort_key))
    diagnostics: list[ValidationRuleDiagnostic] = []
    definitions: list[ValidationRuleDefinition] = []

    id_counts = Counter(
        raw_id
        for item in ordered_inputs
        if isinstance(
            (raw_id := item.record.get("validation_rule_id")), str
        )
        and raw_id
        and raw_id != "#NULL"
    )
    for rule_id, count in sorted(id_counts.items(), key=lambda item: _utf8(item[0])):
        if count > 1:
            diagnostics.append(
                _diagnostic(
                    VALIDATION_RULE_DUPLICATE_ID,
                    "Validation rule ID occurs more than once.",
                    rule_id=rule_id,
                    duplicate_count=count,
                )
            )

    for item in ordered_inputs:
        record_diagnostics, definition = _normalize_rule(item)
        diagnostics.extend(record_diagnostics)
        if definition is not None:
            definitions.append(definition)

    ordered_diagnostics = tuple(sorted(diagnostics, key=_diagnostic_sort_key))
    if ordered_diagnostics:
        return ValidationRuleCatalogResult(None, ordered_diagnostics)
    return ValidationRuleCatalogResult(
        ValidationRuleCatalog(tuple(definitions)),
        (),
    )


def _coerce_input(
    item: Mapping[str, object] | ValidationRuleInput,
) -> ValidationRuleInput:
    if isinstance(item, ValidationRuleInput):
        return ValidationRuleInput(dict(item.record), item.component_identity, item.source_row)
    if not isinstance(item, Mapping):
        raise TypeError("Validation rule inputs must be mappings or ValidationRuleInput values.")
    return ValidationRuleInput(dict(item))


def _input_sort_key(item: ValidationRuleInput) -> tuple[bytes, bytes, int]:
    raw_id = item.record.get("validation_rule_id")
    rule_id = raw_id if isinstance(raw_id, str) and raw_id != "#NULL" else ""
    return (
        _utf8(rule_id),
        _utf8(item.component_identity or ""),
        item.source_row if isinstance(item.source_row, int) else -1,
    )


def _normalize_rule(
    item: ValidationRuleInput,
) -> tuple[tuple[ValidationRuleDiagnostic, ...], ValidationRuleDefinition | None]:
    raw = item.record
    string_keys = frozenset(key for key in raw if isinstance(key, str))
    expected = frozenset(RULE_RECORD_FIELDS)
    raw_rule_id = raw.get("validation_rule_id")
    rule_id = (
        raw_rule_id
        if isinstance(raw_rule_id, str) and raw_rule_id not in {"", "#NULL"}
        else None
    )
    diagnostics: list[ValidationRuleDiagnostic] = []

    non_string_key_count = sum(1 for key in raw if not isinstance(key, str))
    if non_string_key_count:
        diagnostics.append(
            _item_diagnostic(
                item,
                VALIDATION_RULE_SHAPE_INVALID,
                "Validation rule record keys must be strings.",
                rule_id,
                field_name="record",
                non_string_key_count=non_string_key_count,
            )
        )
    missing = tuple(sorted(expected - string_keys, key=_utf8))
    unexpected = tuple(sorted(string_keys - expected, key=_utf8))
    if missing:
        diagnostics.append(
            _item_diagnostic(
                item,
                VALIDATION_RULE_SHAPE_INVALID,
                "Validation rule record is missing schema fields.",
                rule_id,
                field_name="record",
                missing_fields=",".join(missing),
            )
        )
    if unexpected:
        diagnostics.append(
            _item_diagnostic(
                item,
                VALIDATION_RULE_SHAPE_INVALID,
                "Validation rule record contains unknown schema fields.",
                rule_id,
                field_name="record",
                unexpected_fields=",".join(unexpected),
            )
        )

    values = {
        field: _normalize_cell(raw.get(field))
        for field in RULE_RECORD_FIELDS
    }
    for field in _REQUIRED_TEXT_FIELDS:
        value = values[field]
        if not isinstance(value, str) or not value:
            diagnostics.append(
                _item_diagnostic(
                    item,
                    VALIDATION_RULE_SHAPE_INVALID,
                    "Required rule field must be a non-empty string.",
                    rule_id,
                    field_name=field,
                    actual_type=type(value).__name__,
                )
            )
    for field in _OPTIONAL_TEXT_FIELDS:
        value = values[field]
        if value is not None and (not isinstance(value, str) or not value):
            diagnostics.append(
                _item_diagnostic(
                    item,
                    VALIDATION_RULE_SHAPE_INVALID,
                    "Optional rule field must be absent or a non-empty string.",
                    rule_id,
                    field_name=field,
                    actual_type=type(value).__name__,
                )
            )
    for field in ("comparison_value", "minimum_value", "maximum_value"):
        value = values[field]
        if value is not None and (
            isinstance(value, bool) or not isinstance(value, (str, int, float))
        ):
            diagnostics.append(
                _item_diagnostic(
                    item,
                    VALIDATION_RULE_SHAPE_INVALID,
                    "Structured scalar must be a string or non-boolean number.",
                    rule_id,
                    field_name=field,
                    actual_type=type(value).__name__,
                )
            )

    status = values["status"]
    kind = values["validation_kind_id"]
    stage = values["validation_stage_id"]
    severity = values["severity_id"]
    blocking = values["blocking"]
    if not isinstance(status, str) or status not in _KNOWN_STATUSES:
        diagnostics.append(
            _item_diagnostic(
                item,
                VALIDATION_RULE_STATUS_INVALID,
                "Validation rule status is not allowlisted.",
                rule_id,
                field_name="status",
                actual=status if isinstance(status, str) else type(status).__name__,
            )
        )
    if not isinstance(kind, str) or kind not in KNOWN_VALIDATION_KINDS:
        diagnostics.append(
            _item_diagnostic(
                item,
                VALIDATION_RULE_KIND_UNKNOWN,
                "Validation rule kind is not allowlisted.",
                rule_id,
                field_name="validation_kind_id",
                actual=kind if isinstance(kind, str) else type(kind).__name__,
            )
        )
    if not isinstance(stage, str) or stage not in KNOWN_VALIDATION_STAGES:
        diagnostics.append(
            _item_diagnostic(
                item,
                VALIDATION_RULE_STAGE_UNKNOWN,
                "Validation rule stage is not allowlisted.",
                rule_id,
                field_name="validation_stage_id",
                actual=stage if isinstance(stage, str) else type(stage).__name__,
            )
        )
    if not isinstance(severity, str) or severity not in KNOWN_SEVERITIES:
        diagnostics.append(
            _item_diagnostic(
                item,
                VALIDATION_RULE_SEVERITY_UNKNOWN,
                "Validation rule severity is not allowlisted.",
                rule_id,
                field_name="severity_id",
                actual=severity if isinstance(severity, str) else type(severity).__name__,
            )
        )
    if type(blocking) is not bool:
        diagnostics.append(
            _item_diagnostic(
                item,
                VALIDATION_RULE_BLOCKING_INVALID,
                "Validation rule blocking must be a boolean.",
                rule_id,
                field_name="blocking",
                actual_type=type(blocking).__name__,
            )
        )
    scope = values["rule_scope_id"]
    if isinstance(scope, str) and scope not in _KNOWN_RULE_SCOPES:
        diagnostics.append(
            _item_diagnostic(
                item,
                VALIDATION_RULE_SHAPE_INVALID,
                "Validation rule scope is not allowlisted.",
                rule_id,
                field_name="rule_scope_id",
                actual=scope,
            )
        )

    if isinstance(kind, str) and kind in KNOWN_VALIDATION_KINDS:
        diagnostics.extend(_validate_shape(item, rule_id, kind, values))

    expression = values["condition_expression"]
    condition_ast: AstNode | None = None
    condition_hash: str | None = None
    symbol_inventory = _SymbolInventory((), (), ())
    if isinstance(expression, str) and expression:
        try:
            condition_ast = parse_validation_expression(expression)
        except ValidationExpressionError as error:
            diagnostics.extend(
                _expression_diagnostic(item, rule_id, diagnostic)
                for diagnostic in error.diagnostics
            )
        else:
            condition_hash = semantic_ast_hash(condition_ast)
            symbol_inventory = _analyze_symbols(condition_ast)
            diagnostics.extend(
                _item_diagnostic(
                    item,
                    issue.code,
                    _symbol_message(issue.code),
                    rule_id,
                    field_name="condition_expression",
                    identifier=issue.name,
                )
                for issue in symbol_inventory.issues
            )
            if kind == "uniqueness" and not (
                isinstance(condition_ast, Call)
                and condition_ast.function in _UNIQUE_EXPRESSION_BUILTINS
            ):
                diagnostics.append(
                    _item_diagnostic(
                        item,
                        VALIDATION_RULE_SHAPE_INVALID,
                        "Uniqueness expression must use an allowlisted uniqueness builtin.",
                        rule_id,
                        field_name="condition_expression",
                    )
                )

    if diagnostics:
        return tuple(diagnostics), None

    return (), ValidationRuleDefinition(
        rule_id=_required_text(values, "validation_rule_id"),
        rule_scope_id=_required_text(values, "rule_scope_id"),
        status=_required_text(values, "status"),
        validation_kind_id=_required_text(values, "validation_kind_id"),
        validation_stage_id=_required_text(values, "validation_stage_id"),
        severity_id=_required_text(values, "severity_id"),
        blocking=blocking,
        target_table_id=_required_text(values, "target_table_id"),
        target_field_id=_optional_text(values, "target_field_id"),
        condition_expression_source=_optional_text(values, "condition_expression"),
        condition_ast=condition_ast,
        condition_ast_hash=condition_hash,
        operator_id=_optional_text(values, "operator_id"),
        comparison_value=_structured_scalar(values, "comparison_value"),
        minimum_value=_structured_scalar(values, "minimum_value"),
        maximum_value=_structured_scalar(values, "maximum_value"),
        reference_table_id=_optional_text(values, "reference_table_id"),
        reference_field_id=_optional_text(values, "reference_field_id"),
        error_code=_required_text(values, "error_code"),
        message_key=_optional_text(values, "message_key"),
        message=_required_text(values, "message"),
        source_id=_required_text(values, "source_id"),
        source_ref=_required_text(values, "source_ref"),
        notes=_optional_text(values, "notes"),
        free_identifiers=symbol_inventory.free_identifiers,
        local_bindings=symbol_inventory.local_bindings,
        component_identity=item.component_identity,
        source_row=item.source_row,
    )


def _validate_shape(
    item: ValidationRuleInput,
    rule_id: str | None,
    kind: str,
    values: Mapping[str, object],
) -> tuple[ValidationRuleDiagnostic, ...]:
    diagnostics: list[ValidationRuleDiagnostic] = []
    reference_table = values["reference_table_id"]
    reference_field = values["reference_field_id"]
    if (reference_table is None) != (reference_field is None):
        diagnostics.append(
            _item_diagnostic(
                item,
                VALIDATION_RULE_SHAPE_INVALID,
                "Reference table and field must both be present or both be absent.",
                rule_id,
                field_name="reference_table_id,reference_field_id",
            )
        )

    populated = tuple(field for field in _SHAPE_FIELDS if values[field] is not None)
    contract = next(entry for entry in RULE_KIND_CONTRACTS if entry.kind == kind)
    if not any(variant.populated_fields == populated for variant in contract.variants):
        diagnostics.append(
            _item_diagnostic(
                item,
                VALIDATION_RULE_SHAPE_INVALID,
                "Populated fields do not match an allowlisted rule-kind shape.",
                rule_id,
                field_name="shape",
                actual_fields=",".join(populated),
                allowed_variants=",".join(variant.name for variant in contract.variants),
            )
        )

    comparison = values["comparison_value"]
    minimum = values["minimum_value"]
    if kind in {"allowed_value", "contract_instance_consistency"} and (
        comparison is not None and (not isinstance(comparison, str) or not comparison)
    ):
        diagnostics.append(
            _item_diagnostic(
                item,
                VALIDATION_RULE_SHAPE_INVALID,
                "This rule kind requires a non-empty string comparison value.",
                rule_id,
                field_name="comparison_value",
                actual_type=type(comparison).__name__,
            )
        )
    if kind == "range":
        for field, value in (("comparison_value", comparison), ("minimum_value", minimum)):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                diagnostics.append(
                    _item_diagnostic(
                        item,
                        VALIDATION_RULE_SHAPE_INVALID,
                        "Range shape requires a non-boolean numeric value.",
                        rule_id,
                        field_name=field,
                        actual_type=type(value).__name__,
                    )
                )
    return tuple(diagnostics)


def _analyze_symbols(root: AstNode) -> _SymbolInventory:
    free: set[str] = set()
    locals_seen: set[str] = set()
    issues: list[_SymbolIssue] = []

    def analyze_scope(
        node: AstNode,
        outer_bound: frozenset[str],
        outer_future: frozenset[str] = frozenset(),
    ) -> None:
        statements = node.statements if isinstance(node, AstSequence) else (node,)
        direct_names = tuple(
            statement.name for statement in statements if isinstance(statement, Binding)
        )
        future = Counter(direct_names)
        bound = set(outer_bound)
        local_defined: set[str] = set()
        for statement in statements:
            remaining = frozenset(future) | outer_future
            if isinstance(statement, Binding):
                analyze_node(statement.value, frozenset(bound), remaining)
                future[statement.name] -= 1
                if future[statement.name] <= 0:
                    del future[statement.name]
                if statement.name in local_defined:
                    issues.append(
                        _SymbolIssue(VALIDATION_RULE_BINDING_REBIND, statement.name)
                    )
                else:
                    local_defined.add(statement.name)
                    locals_seen.add(statement.name)
                    bound.add(statement.name)
            else:
                analyze_node(statement, frozenset(bound), remaining)

    def analyze_node(
        node: AstNode,
        bound: frozenset[str],
        future: frozenset[str],
    ) -> None:
        if isinstance(node, Identifier):
            if node.name in bound:
                return
            if node.name in future:
                issues.append(
                    _SymbolIssue(
                        VALIDATION_RULE_BINDING_FORWARD_REFERENCE,
                        node.name,
                    )
                )
                return
            free.add(node.name)
        elif isinstance(node, ListLiteral):
            for item in node.items:
                analyze_node(item, bound, future)
        elif isinstance(node, UnaryOperation):
            analyze_node(node.operand, bound, future)
        elif isinstance(node, BinaryOperation):
            analyze_node(node.left, bound, future)
            analyze_node(node.right, bound, future)
        elif isinstance(node, Call):
            for argument in node.arguments:
                if isinstance(argument, (AstSequence, Binding)):
                    analyze_scope(argument, bound, future)
                else:
                    analyze_node(argument, bound, future)
        elif isinstance(node, MemberAccess):
            analyze_node(node.target, bound, future)
        elif isinstance(node, Binding):
            analyze_scope(node, bound, future)
        elif isinstance(node, AstSequence):
            analyze_scope(node, bound, future)
        elif isinstance(node, (MapLiteral, TbdLiteral)):
            return

    analyze_scope(root, frozenset())
    return _SymbolInventory(
        tuple(sorted(free, key=_utf8)),
        tuple(sorted(locals_seen, key=_utf8)),
        tuple(issues),
    )


def _expression_diagnostic(
    item: ValidationRuleInput,
    rule_id: str | None,
    diagnostic: ValidationExpressionDiagnostic,
) -> ValidationRuleDiagnostic:
    return ValidationRuleDiagnostic(
        diagnostic.code,
        diagnostic.message,
        rule_id,
        item.component_identity,
        item.source_row,
        "condition_expression",
        diagnostic.offset,
        diagnostic.line,
        diagnostic.column,
        diagnostic.context,
        diagnostic,
    )


def _symbol_message(code: str) -> str:
    if code == VALIDATION_RULE_BINDING_FORWARD_REFERENCE:
        return "Local identifier is referenced before its binding."
    if code == VALIDATION_RULE_BINDING_REBIND:
        return "Local identifier is bound more than once in the same scope."
    return "Local binding uses a reserved context identifier."


def _item_diagnostic(
    item: ValidationRuleInput,
    code: str,
    message: str,
    rule_id: str | None,
    field_name: str | None = None,
    **context: DiagnosticValue,
) -> ValidationRuleDiagnostic:
    return ValidationRuleDiagnostic(
        code,
        message,
        rule_id,
        item.component_identity,
        item.source_row,
        field_name,
        context=tuple(sorted(context.items(), key=lambda entry: _utf8(entry[0]))),
    )


def _diagnostic(
    code: str,
    message: str,
    rule_id: str | None = None,
    **context: DiagnosticValue,
) -> ValidationRuleDiagnostic:
    return ValidationRuleDiagnostic(
        code,
        message,
        rule_id,
        context=tuple(sorted(context.items(), key=lambda entry: _utf8(entry[0]))),
    )


def _diagnostic_sort_key(
    diagnostic: ValidationRuleDiagnostic,
) -> tuple[bytes, bytes, bytes, bytes, int, int, bytes]:
    return (
        _utf8(diagnostic.rule_id or ""),
        _utf8(diagnostic.code),
        _utf8(diagnostic.field_name or ""),
        _utf8(diagnostic.component_identity or ""),
        diagnostic.source_row if diagnostic.source_row is not None else -1,
        diagnostic.offset if diagnostic.offset is not None else -1,
        _utf8(diagnostic.message),
    )


def _normalize_cell(value: object) -> object:
    return None if value == "#NULL" else value


def _required_text(values: Mapping[str, object], field: str) -> str:
    value = values[field]
    if not isinstance(value, str) or not value:
        raise AssertionError(f"Validated field {field} is not a required string.")
    return value


def _optional_text(values: Mapping[str, object], field: str) -> str | None:
    value = values[field]
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise AssertionError(f"Validated field {field} is not an optional string.")
    return value


def _structured_scalar(
    values: Mapping[str, object], field: str
) -> StructuredScalar | None:
    value = values[field]
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise AssertionError(f"Validated field {field} is not a structured scalar.")
    return value


def _utf8(value: str) -> bytes:
    return value.encode("utf-8")


__all__ = [
    "KNOWN_SEVERITIES",
    "KNOWN_VALIDATION_KINDS",
    "KNOWN_VALIDATION_STAGES",
    "RULE_KIND_CONTRACTS",
    "RULE_RECORD_FIELDS",
    "VALIDATION_RULE_BINDING_FORWARD_REFERENCE",
    "VALIDATION_RULE_BINDING_REBIND",
    "VALIDATION_RULE_BINDING_RESERVED",
    "VALIDATION_RULE_BLOCKING_INVALID",
    "VALIDATION_RULE_DUPLICATE_ID",
    "VALIDATION_RULE_KIND_UNKNOWN",
    "VALIDATION_RULE_SEVERITY_UNKNOWN",
    "VALIDATION_RULE_SHAPE_INVALID",
    "VALIDATION_RULE_STAGE_UNKNOWN",
    "VALIDATION_RULE_STATUS_INVALID",
    "ValidationRuleCatalog",
    "ValidationRuleCatalogResult",
    "ValidationRuleDefinition",
    "ValidationRuleDiagnostic",
    "ValidationRuleInput",
    "ValidationRuleKindContract",
    "ValidationRuleShapeVariant",
    "build_validation_rule_catalog",
]
