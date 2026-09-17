import hashlib
import sys
import unittest
from collections import Counter
from dataclasses import replace
from pathlib import Path
from types import MappingProxyType

import test_canonical_validation_execution as execution_tests


PYTHON_ROOT = Path(__file__).resolve().parents[1]
MODULE_DIRECTORY = PYTHON_ROOT / "tools" / "canonical_export"
DEFINITION_PATH = MODULE_DIRECTORY / "canonical_validation_definition.py"

execution = execution_tests.execution
rules = execution_tests.rules
validation = execution_tests.validation_expr
definition = sys.modules[
    execution.execute_definition_invariant_rule.__module__
]


def make_definition_rule(
    expression='value == "alpha"',
    *,
    ast=None,
    rule_id="definition_test_rule",
    table_id="items",
    target_field_id="fld_items_value",
    component="registry-component",
    **overrides,
):
    ast = ast or validation.parse_validation_expression(expression)
    return replace(
        execution_tests.make_rule(),
        rule_id=rule_id,
        rule_scope_id="record",
        validation_kind_id="definition_invariant",
        validation_stage_id="pre_export",
        target_table_id=table_id,
        target_field_id=target_field_id,
        condition_expression_source=expression,
        condition_ast=ast,
        condition_ast_hash=validation.semantic_ast_hash(ast),
        operator_id=None,
        comparison_value=None,
        minimum_value=None,
        maximum_value=None,
        reference_table_id=None,
        reference_field_id=None,
        component_identity=component,
        **overrides,
    )


def schema_field(
    name="value",
    data_type="string",
    *,
    nullable=False,
    field_id=None,
):
    return {
        "field_id": field_id or f"fld_items_{name}",
        "table_id": "items",
        "field_name": name,
        "data_type": data_type,
        "required_mode": "conditional" if nullable else "always",
        "nullable": nullable,
        "null_handling": "explicit_null" if nullable else "forbidden",
        "status": "active",
    }


def table_field(
    table,
    name,
    data_type="string",
    *,
    nullable=False,
    field_id=None,
):
    return {
        "field_id": field_id or f"fld_{table}_{name}",
        "table_id": table,
        "field_name": name,
        "data_type": data_type,
        "required_mode": "conditional" if nullable else "always",
        "nullable": nullable,
        "null_handling": "explicit_null" if nullable else "forbidden",
        "status": "active",
    }


def namespace_tables(
    records=(),
    *,
    fields=None,
    include_target=True,
    include_table_schema=True,
):
    tables = {
        "schema_tables": (
            {
                "table_id": "items",
                "primary_key": "item_id",
                "status": "active",
            },
        )
        if include_table_schema
        else (),
        "schema_fields": tuple(fields or (schema_field(),)),
    }
    if include_target:
        tables["items"] = tuple(records)
    return tables


def make_context(
    records=(),
    *,
    fields=None,
    include_target=True,
    bindings=None,
    registry_tables=None,
    carddatabase_tables=None,
):
    registry = registry_tables or namespace_tables(
        records,
        fields=fields,
        include_target=include_target,
    )
    carddatabase = carddatabase_tables or namespace_tables(
        ({"item_id": "cdb-1", "value": "carddatabase"},)
    )
    return execution.ValidationDataContext(
        namespaced_tables={
            "registry": registry,
            "carddatabase": carddatabase,
        },
        component_namespaces=(
            {"registry-component": "registry"}
            if bindings is None
            else bindings
        ),
    )


def execute(rule=None, records=(), **context_options):
    return execution.execute_definition_invariant_rule(
        rule or make_definition_rule(),
        make_context(records, **context_options),
    )


class TestDefinitionModuleBoundary(unittest.TestCase):
    def test_public_boundary_and_facade_identity_are_exact(self):
        self.assertEqual(
            definition.__all__,
            [
                "VALIDATION_DEFINITION_INVARIANT_FAILED",
                "VALIDATION_DEFINITION_TARGET_RECORD_INVALID",
                "VALIDATION_DEFINITION_TARGET_TABLE_MISSING",
                "execute_definition_invariant_rule",
            ],
        )
        self.assertIs(
            execution.execute_definition_invariant_rule,
            definition.execute_definition_invariant_rule,
        )

    def test_family_module_is_pure_and_has_no_rule_specific_dispatch(self):
        source = DEFINITION_PATH.read_text(encoding="utf-8")
        for forbidden in (
            "openpyxl",
            "load_workbook",
            "canonical_validation_stage",
            "if rule.rule_id",
            "cdb_val_",
            "val_modifier_",
        ):
            self.assertNotIn(forbidden, source)

    def test_family_reuses_the_b0_evaluator(self):
        source = DEFINITION_PATH.read_text(encoding="utf-8")
        self.assertIn("evaluate_validation_expression", source)
        for duplicate in ("_typed_equal", "_evaluate_binary", "_evaluate_call"):
            self.assertNotIn(duplicate, source)

    def test_argument_contract_is_explicit(self):
        with self.assertRaises(TypeError):
            execution.execute_definition_invariant_rule(
                object(), make_context()
            )
        with self.assertRaises(TypeError):
            execution.execute_definition_invariant_rule(
                make_definition_rule(), object()
            )

    def test_unexpected_evaluator_exception_propagates(self):
        original = definition.evaluate_validation_expression
        try:
            def crash(*_):
                raise RuntimeError("synthetic programming failure")

            definition.evaluate_validation_expression = crash
            with self.assertRaisesRegex(RuntimeError, "synthetic programming failure"):
                execute(records=({"item_id": "item-1", "value": "alpha"},))
        finally:
            definition.evaluate_validation_expression = original


class TestSupportedShape(unittest.TestCase):
    def assert_passes(self, expression, record, *, fields=None):
        result = execute(
            make_definition_rule(expression),
            (record,),
            fields=fields,
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.PASS)
        self.assertEqual(result.evaluated_record_count, 1)
        self.assertEqual(result.violation_count, 0)

    def test_direct_equality_and_inequality(self):
        self.assert_passes(
            'value == "alpha"',
            {"item_id": "item-1", "value": "alpha"},
        )
        self.assert_passes(
            'value != "blocked"',
            {"item_id": "item-1", "value": "alpha"},
        )

    def test_membership(self):
        self.assert_passes(
            'value in ["alpha","beta"]',
            {"item_id": "item-1", "value": "beta"},
        )

    def test_integer_greater_than_or_equal(self):
        self.assert_passes(
            "count >= 1",
            {"item_id": "item-1", "count": 2},
            fields=(schema_field("count", "integer"),),
        )

    def test_boolean_and_or_not(self):
        fields = tuple(
            schema_field(name, "boolean")
            for name in ("enabled", "blocked", "override")
        )
        self.assert_passes(
            "enabled and not blocked or override",
            {
                "item_id": "item-1",
                "enabled": True,
                "blocked": False,
                "override": False,
            },
            fields=fields,
        )


class TestCardinalityDefinitionShape(unittest.TestCase):
    FIELDS = (
        schema_field("first", "boolean", nullable=True),
        schema_field("second", "integer", nullable=True),
        schema_field("kind", "string", nullable=True),
    )

    def run_cardinality(self, expression, record):
        return execute(
            make_definition_rule(expression),
            (record,),
            fields=self.FIELDS,
        )

    def test_direct_boolean_cardinality_calls_are_exact_predicates(self):
        cases = (
            (
                "at_least_one_non_null([first,second])",
                {"first": None, "second": 0, "kind": None},
                execution.ValidationOutcome.PASS,
            ),
            (
                "at_least_one_non_null([first,second])",
                {"first": None, "second": None, "kind": None},
                execution.ValidationOutcome.FAIL,
            ),
            (
                "at_most_one_non_null([first,second])",
                {"first": False, "second": None, "kind": None},
                execution.ValidationOutcome.PASS,
            ),
            (
                "at_most_one_non_null([first,second])",
                {"first": False, "second": 0, "kind": None},
                execution.ValidationOutcome.FAIL,
            ),
        )
        for expression, values, expected in cases:
            with self.subTest(expression=expression, values=values):
                result = self.run_cardinality(
                    expression, {"item_id": "item-1", **values}
                )
                self.assertIs(result.outcome, expected)
                self.assertEqual(result.evaluated_record_count, 1)
                self.assertEqual(
                    result.violation_count,
                    0 if expected is execution.ValidationOutcome.PASS else 1,
                )

    def test_count_equality_and_guarded_cardinality_shapes_execute(self):
        record = {
            "item_id": "item-1",
            "first": None,
            "second": 0,
            "kind": "integer",
        }
        expressions = (
            "count_non_null([first,second]) == 1",
            "when(at_least_one_non_null([first,second]), kind != null)",
        )
        for expression in expressions:
            with self.subTest(expression=expression):
                result = self.run_cardinality(expression, record)
                self.assertIs(result.outcome, execution.ValidationOutcome.PASS)
                self.assertEqual(
                    (result.evaluated_record_count, result.violation_count),
                    (1, 0),
                )

        false_guard = self.run_cardinality(
            "when(at_least_one_non_null([first,second]), kind != null)",
            {
                "item_id": "item-1",
                "first": None,
                "second": None,
                "kind": None,
            },
        )
        self.assertIs(false_guard.outcome, execution.ValidationOutcome.PASS)
        self.assertEqual(
            (false_guard.evaluated_record_count, false_guard.violation_count),
            (1, 0),
        )

    def test_nearby_cardinality_shapes_remain_unsupported(self):
        expressions = (
            "count_non_null([first,second])",
            "count_non_null([first,second]) != 1",
            "1 == count_non_null([first,second])",
            "count_non_null(first) == 1",
            "at_least_one_non_null(first)",
            "when(at_most_one_non_null([first,second]), kind != null)",
            "at_most_one_non_null([first == null,second])",
        )
        for expression in expressions:
            with self.subTest(expression=expression):
                result = self.run_cardinality(
                    expression,
                    {
                        "item_id": "item-1",
                        "first": None,
                        "second": 0,
                        "kind": "integer",
                    },
                )
                self.assertIs(
                    result.outcome, execution.ValidationOutcome.UNSUPPORTED
                )
                self.assertEqual(
                    (result.evaluated_record_count, result.violation_count),
                    (0, 0),
                )


class TestGuardedWhenShapeAndSemantics(unittest.TestCase):
    FIELDS = (
        schema_field("enabled", "boolean"),
        schema_field("value", "string", nullable=True),
    )

    def run_when(self, expression, record, *, fields=None, ast=None):
        return execute(
            make_definition_rule(expression, ast=ast),
            (record,),
            fields=fields or self.FIELDS,
        )

    def test_valid_top_level_when_equality(self):
        result = self.run_when(
            'when(enabled == true, value == "alpha")',
            {"item_id": "item-1", "enabled": True, "value": "alpha"},
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.PASS)
        self.assertEqual((result.evaluated_record_count, result.violation_count), (1, 0))

    def test_false_guard_is_pass_equivalent_not_not_applicable(self):
        result = self.run_when(
            'when(enabled == true, value == "alpha")',
            {"item_id": "item-1", "enabled": False, "value": "beta"},
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.PASS)
        self.assertEqual((result.evaluated_record_count, result.violation_count), (1, 0))

    def test_true_guard_true_and_false_constraints(self):
        passing = self.run_when(
            'when(enabled == true, value != "blocked")',
            {"item_id": "item-1", "enabled": True, "value": "alpha"},
        )
        failing = self.run_when(
            'when(enabled == true, value != "blocked")',
            {"item_id": "item-1", "enabled": True, "value": "blocked"},
        )
        self.assertIs(passing.outcome, execution.ValidationOutcome.PASS)
        self.assertIs(failing.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(failing.violation_count, 1)
        self.assertEqual(failing.diagnostics[0].reason, "predicate_false")

    def test_false_guard_short_circuits_invalid_constraint_literal(self):
        ast = validation.Call(
            "when",
            (
                validation.Identifier("enabled"),
                validation.BinaryOperation(
                    "==",
                    validation.Literal("integer", "invalid"),
                    validation.Literal("integer", 1),
                ),
            ),
        )
        false_guard = self.run_when(
            "synthetic short-circuit",
            {"item_id": "item-1", "enabled": False},
            fields=(schema_field("enabled", "boolean"),),
            ast=ast,
        )
        true_guard = self.run_when(
            "synthetic evaluated constraint",
            {"item_id": "item-1", "enabled": True},
            fields=(schema_field("enabled", "boolean"),),
            ast=ast,
        )
        self.assertIs(false_guard.outcome, execution.ValidationOutcome.PASS)
        self.assertIs(true_guard.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(
            true_guard.diagnostics[0].reason,
            "expression_evaluation_error:literal_kind_or_value_invalid",
        )

    def test_missing_constraint_schema_is_not_hidden_by_false_guard(self):
        result = self.run_when(
            'when(enabled, missing == "value")',
            {"item_id": "item-1", "enabled": False},
            fields=(schema_field("enabled", "boolean"),),
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(result.evaluated_record_count, 0)
        self.assertEqual(
            result.diagnostics[0].reason,
            "identifier_field_schema_unresolved:missing",
        )

    def test_non_boolean_guard_is_record_invalid(self):
        result = self.run_when(
            'when(mode, value == "alpha")',
            {"item_id": "item-1", "mode": "active", "value": "alpha"},
            fields=(
                schema_field("mode", "string"),
                schema_field("value", "string"),
            ),
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(
            result.diagnostics[0].reason,
            "expression_evaluation_error:boolean_operand_required",
        )

    def test_non_boolean_when_result_is_record_invalid(self):
        original = definition.evaluate_validation_expression
        try:
            definition.evaluate_validation_expression = lambda *_: "not-boolean"
            result = self.run_when(
                'when(enabled, value == "alpha")',
                {"item_id": "item-1", "enabled": True, "value": "alpha"},
            )
        finally:
            definition.evaluate_validation_expression = original
        self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(
            result.diagnostics[0].reason, "expression_result_not_boolean"
        )

    def test_type_aware_bool_int_and_case_sensitive_equality(self):
        bool_int = self.run_when(
            "when(enabled, flag == 1)",
            {"item_id": "item-1", "enabled": True, "flag": True},
            fields=(
                schema_field("enabled", "boolean"),
                schema_field("flag", "boolean"),
            ),
        )
        string_case = self.run_when(
            'when(enabled, value == "A")',
            {"item_id": "item-1", "enabled": True, "value": "a"},
        )
        self.assertIs(bool_int.outcome, execution.ValidationOutcome.FAIL)
        self.assertIs(string_case.outcome, execution.ValidationOutcome.FAIL)

    def test_nullable_equality(self):
        result = self.run_when(
            "when(enabled, value == null)",
            {"item_id": "item-1", "enabled": True, "value": None},
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.PASS)


class TestCompoundWhenShapeAndSemantics(unittest.TestCase):
    @staticmethod
    def run_compound(expression, records, fields):
        return execute(
            make_definition_rule(expression),
            records,
            fields=fields,
        )

    def test_multiple_equality_and_boolean_flag_conjunction(self):
        fields = (
            schema_field("mode"),
            schema_field("value"),
            schema_field("enabled", "boolean"),
            schema_field("blocked", "boolean"),
        )
        expression = (
            'when(mode == "active", value == "alpha" '
            "and enabled == true and blocked == false)"
        )
        passing = self.run_compound(
            expression,
            ({
                "item_id": "item-1",
                "mode": "active",
                "value": "alpha",
                "enabled": True,
                "blocked": False,
            },),
            fields,
        )
        failing = self.run_compound(
            expression,
            ({
                "item_id": "item-1",
                "mode": "active",
                "value": "alpha",
                "enabled": False,
                "blocked": False,
            },),
            fields,
        )
        self.assertIs(passing.outcome, execution.ValidationOutcome.PASS)
        self.assertIs(failing.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(failing.diagnostics[0].reason, "predicate_false")

    def test_nested_or_and_positive_membership_are_exact(self):
        fields = (
            schema_field("enabled", "boolean"),
            schema_field("mode"),
            schema_field("state"),
        )
        expression = (
            'when(enabled == true, (mode == "alpha" or mode == "beta") '
            'and state in ["ready","active"])'
        )
        passing = self.run_compound(
            expression,
            ({
                "item_id": "item-1",
                "enabled": True,
                "mode": "beta",
                "state": "active",
            },),
            fields,
        )
        case_mismatch = self.run_compound(
            expression,
            ({
                "item_id": "item-1",
                "enabled": True,
                "mode": "beta",
                "state": "Active",
            },),
            fields,
        )
        self.assertIs(passing.outcome, execution.ValidationOutcome.PASS)
        self.assertIs(case_mismatch.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(case_mismatch.diagnostics[0].reason, "predicate_false")

    def test_exact_integer_lower_bound(self):
        result = self.run_compound(
            'when(mode == "active", count >= 1)',
            ({"item_id": "item-1", "mode": "active", "count": 2},),
            (schema_field("mode"), schema_field("count", "integer")),
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.PASS)

    def test_false_when_skips_nullable_numeric_constraint(self):
        result = self.run_compound(
            "when(enabled == true, count >= 1)",
            ({"item_id": "item-1", "enabled": False, "count": None},),
            (
                schema_field("enabled", "boolean"),
                schema_field("count", "integer", nullable=True),
            ),
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.PASS)
        self.assertEqual((result.evaluated_record_count, result.violation_count), (1, 0))

    def test_non_null_check_short_circuits_lower_bound(self):
        result = self.run_compound(
            "when(enabled == true, count != null and count >= 1)",
            ({"item_id": "item-1", "enabled": True, "count": None},),
            (
                schema_field("enabled", "boolean"),
                schema_field("count", "integer", nullable=True),
            ),
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(result.diagnostics[0].code, execution.VALIDATION_DEFINITION_INVARIANT_FAILED)
        self.assertEqual(result.diagnostics[0].reason, "predicate_false")

    def test_applicable_nullable_numeric_is_controlled_record_failure(self):
        result = self.run_compound(
            "when(enabled == true, count >= 1)",
            ({"item_id": "item-1", "enabled": True, "count": None},),
            (
                schema_field("enabled", "boolean"),
                schema_field("count", "integer", nullable=True),
            ),
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(
            result.diagnostics[0].code,
            execution.VALIDATION_DEFINITION_TARGET_RECORD_INVALID,
        )
        self.assertEqual(
            result.diagnostics[0].reason,
            "expression_evaluation_error:integer_operands_required",
        )

    def test_multiple_false_rows_are_deterministic_when_reversed(self):
        fields = (
            schema_field("enabled", "boolean"),
            schema_field("value"),
            schema_field("blocked", "boolean"),
        )
        expression = (
            'when(enabled == true, value == "alpha" and blocked == false)'
        )
        records = (
            {"item_id": "item-3", "enabled": True, "value": "beta", "blocked": False},
            {"item_id": "item-1", "enabled": True, "value": "alpha", "blocked": False},
            {"item_id": "item-2", "enabled": True, "value": "alpha", "blocked": True},
        )
        forward = self.run_compound(expression, records, fields)
        reverse = self.run_compound(expression, tuple(reversed(records)), fields)
        self.assertEqual(forward, reverse)
        self.assertEqual((forward.evaluated_record_count, forward.violation_count), (3, 2))
        self.assertEqual(
            tuple(item.record_identity for item in forward.diagnostics),
            ("item-2", "item-3"),
        )


class TestNegatedMembershipWhenShapeAndSemantics(unittest.TestCase):
    FIELDS = (
        schema_field("enabled", "boolean"),
        schema_field("value", nullable=True),
    )
    EXPRESSION = 'when(enabled == true, value not in [null,"#TBD"])'

    @classmethod
    def execute(cls, records):
        return execute(
            make_definition_rule(cls.EXPRESSION),
            records,
            fields=cls.FIELDS,
        )

    def test_simple_guarded_not_in_is_exact_and_case_sensitive(self):
        for value, expected in (
            ("alpha", execution.ValidationOutcome.PASS),
            ("#TBD", execution.ValidationOutcome.FAIL),
            ("#tbd", execution.ValidationOutcome.PASS),
        ):
            with self.subTest(value=value):
                result = self.execute(({
                    "item_id": "item-1",
                    "enabled": True,
                    "value": value,
                },))
                self.assertIs(result.outcome, expected)

    def test_applicable_none_is_predicate_false(self):
        result = self.execute(({
            "item_id": "item-1",
            "enabled": True,
            "value": None,
        },))
        self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(
            result.diagnostics[0].code,
            execution.VALIDATION_DEFINITION_INVARIANT_FAILED,
        )
        self.assertEqual(result.diagnostics[0].reason, "predicate_false")

    def test_false_when_guard_short_circuits_constraint(self):
        result = self.execute(({
            "item_id": "item-1",
            "enabled": False,
            "value": None,
        },))
        self.assertIs(result.outcome, execution.ValidationOutcome.PASS)
        self.assertEqual(
            (result.evaluated_record_count, result.violation_count), (1, 0)
        )

    def test_multiple_false_rows_are_deterministic_when_reversed(self):
        records = (
            {"item_id": "item-3", "enabled": True, "value": "alpha"},
            {"item_id": "item-1", "enabled": True, "value": None},
            {"item_id": "item-2", "enabled": True, "value": "#TBD"},
        )
        forward = self.execute(records)
        reverse = self.execute(tuple(reversed(records)))
        self.assertEqual(forward, reverse)
        self.assertEqual(
            (forward.evaluated_record_count, forward.violation_count), (3, 2)
        )
        self.assertEqual(
            tuple(item.record_identity for item in forward.diagnostics),
            ("item-1", "item-2"),
        )


class TestSequenceWhenShapeAndSemantics(unittest.TestCase):
    FIELDS = (
        schema_field("enabled", "boolean"),
        schema_field("value", nullable=True),
        schema_field("count", "integer", nullable=True),
    )
    EXPRESSION = (
        'when(enabled == true,value not in [null,"#TBD"]); '
        "when(value != null,count >= 1)"
    )

    @classmethod
    def execute(cls, records, *, ast=None):
        return execute(
            make_definition_rule(
                cls.EXPRESSION if ast is None else "synthetic sequence",
                ast=ast,
            ),
            records,
            fields=cls.FIELDS,
        )

    def test_multiple_when_predicates_are_conjoined(self):
        passing = self.execute(({
            "item_id": "item-1",
            "enabled": True,
            "value": "alpha",
            "count": 1,
        },))
        failing = self.execute(({
            "item_id": "item-1",
            "enabled": True,
            "value": "alpha",
            "count": 0,
        },))
        self.assertIs(passing.outcome, execution.ValidationOutcome.PASS)
        self.assertIs(failing.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(failing.diagnostics[0].reason, "predicate_false")

    def test_false_when_guards_contribute_true_with_nullable_values(self):
        result = self.execute(({
            "item_id": "item-1",
            "enabled": False,
            "value": None,
            "count": None,
        },))
        self.assertIs(result.outcome, execution.ValidationOutcome.PASS)
        self.assertEqual(
            (result.evaluated_record_count, result.violation_count), (1, 0)
        )

    def test_false_statement_short_circuits_later_when(self):
        ast = validation.Sequence((
            validation.Call(
                "when",
                (
                    validation.Literal("boolean", True),
                    validation.Literal("boolean", False),
                ),
            ),
            validation.Call(
                "when",
                (
                    validation.Literal("boolean", True),
                    validation.BinaryOperation(
                        ">=",
                        validation.Identifier("count"),
                        validation.Literal("integer", 1),
                    ),
                ),
            ),
        ))
        result = self.execute(({
            "item_id": "item-1",
            "enabled": True,
            "value": "alpha",
            "count": None,
        },), ast=ast)
        self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(result.diagnostics[0].reason, "predicate_false")

    def test_multiple_false_records_are_deterministic_when_reversed(self):
        records = (
            {"item_id": "item-3", "enabled": True, "value": "alpha", "count": 1},
            {"item_id": "item-1", "enabled": True, "value": None, "count": None},
            {"item_id": "item-2", "enabled": True, "value": "#TBD", "count": 1},
        )
        forward = self.execute(records)
        reverse = self.execute(tuple(reversed(records)))
        self.assertEqual(forward, reverse)
        self.assertEqual(
            (forward.evaluated_record_count, forward.violation_count), (3, 2)
        )
        self.assertEqual(
            tuple(item.record_identity for item in forward.diagnostics),
            ("item-1", "item-2"),
        )

    def test_nested_empty_and_non_when_sequences_are_rejected(self):
        valid_when = validation.Call(
            "when",
            (
                validation.Literal("boolean", True),
                validation.Literal("boolean", True),
            ),
        )
        cases = (
            validation.Sequence(()),
            validation.Sequence((
                validation.Sequence((valid_when, valid_when)),
                valid_when,
            )),
            validation.Sequence((
                validation.Literal("boolean", True),
                valid_when,
            )),
        )
        for ast in cases:
            with self.subTest(ast=ast):
                result = self.execute((), ast=ast)
                self.assertIs(
                    result.outcome, execution.ValidationOutcome.UNSUPPORTED
                )
                self.assertEqual(
                    (result.evaluated_record_count, result.violation_count),
                    (0, 0),
                )

    def test_binding_member_map_and_tbd_sequence_children_are_rejected(self):
        unsupported = (
            validation.Binding("copy", validation.Identifier("value")),
            validation.MemberAccess(validation.Identifier("record"), "value"),
            validation.MapLiteral((('key', 'value'),)),
            validation.TbdLiteral(),
        )
        valid_when = validation.Call(
            "when",
            (
                validation.Literal("boolean", True),
                validation.Literal("boolean", True),
            ),
        )
        for child in unsupported:
            with self.subTest(node=type(child).__name__):
                result = self.execute(
                    (), ast=validation.Sequence((child, valid_when))
                )
                self.assertIs(
                    result.outcome, execution.ValidationOutcome.UNSUPPORTED
                )

    def test_lookup_bearing_sequence_is_rejected(self):
        result = self.execute(
            (),
            ast=validation.parse_validation_expression(
                'when(true,lookup("items","item_id",value,"value") == value); '
                'when(true,value == "alpha")'
            ),
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.UNSUPPORTED)
        self.assertEqual(
            (result.evaluated_record_count, result.violation_count), (0, 0)
        )


class TestTextSchemaAdmission(unittest.TestCase):
    @staticmethod
    def run_text(expression, records, *, nullable=False, field=None):
        return execute(
            make_definition_rule(expression),
            records,
            fields=(
                field
                or schema_field("value", "text", nullable=nullable),
            ),
        )

    def test_exact_string_is_accepted_without_normalization_or_coercion(self):
        cases = (
            ('value == "Ă©"', "Ă©", execution.ValidationOutcome.PASS),
            ('value == "Ă©"', "e\u0301", execution.ValidationOutcome.FAIL),
            ('value == "alpha"', "Alpha", execution.ValidationOutcome.FAIL),
            ('value == "alpha"', " alpha", execution.ValidationOutcome.FAIL),
        )
        for expression, value, expected in cases:
            with self.subTest(expression=expression, value=value):
                result = self.run_text(
                    expression,
                    ({"item_id": "item-1", "value": value},),
                )
                self.assertIs(result.outcome, expected)

    def test_only_exact_str_runtime_values_are_accepted(self):
        text_field = schema_field("value", "text")
        for value in (True, 1, 1.0, [], {}):
            with self.subTest(value_type=type(value).__name__):
                self.assertEqual(
                    definition._field_value_reason(value, text_field),
                    "target_value_type_invalid",
                )
        for value in (True, 1, 1.0):
            with self.subTest(canonical_value_type=type(value).__name__):
                result = self.run_text(
                    'value == "alpha"',
                    ({"item_id": "item-1", "value": value},),
                )
                self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
                self.assertEqual(
                    result.diagnostics[0].reason,
                    "target_value_type_invalid:value",
                )

    def test_none_requires_nullable_and_missing_is_distinct(self):
        nullable = self.run_text(
            "value == null",
            ({"item_id": "item-1", "value": None},),
            nullable=True,
        )
        required = self.run_text(
            "value == null",
            ({"item_id": "item-1", "value": None},),
        )
        missing = self.run_text(
            "value == null",
            ({"item_id": "item-1"},),
            nullable=True,
        )
        self.assertIs(nullable.outcome, execution.ValidationOutcome.PASS)
        self.assertIs(required.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(
            required.diagnostics[0].reason, "target_value_null:value"
        )
        self.assertIs(missing.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(
            missing.diagnostics[0].reason, "target_field_missing:value"
        )

    def test_malformed_text_schema_metadata_fails_closed(self):
        invalid_nullable = schema_field("value", "text")
        invalid_nullable["nullable"] = "false"
        invalid_null_handling = schema_field("value", "text")
        invalid_null_handling["null_handling"] = "explicit_null"
        for field, reason in (
            (
                invalid_nullable,
                "identifier_schema_nullable_invalid:value",
            ),
            (
                invalid_null_handling,
                "identifier_schema_null_contract_invalid:value",
            ),
        ):
            with self.subTest(reason=reason):
                result = self.run_text(
                    'value == "alpha"',
                    ({"item_id": "item-1", "value": "alpha"},),
                    field=field,
                )
                self.assertIs(
                    result.outcome, execution.ValidationOutcome.UNSUPPORTED
                )
                self.assertEqual(result.diagnostics[0].reason, reason)


class TestLanguageTagSchemaAdmission(unittest.TestCase):
    @staticmethod
    def fields(*, nullable=False):
        return (
            schema_field("enabled", "boolean"),
            schema_field("language", "language_tag", nullable=nullable),
        )

    @classmethod
    def run_language(cls, expression, records, *, nullable=False):
        return execute(
            make_definition_rule(expression),
            records,
            fields=cls.fields(nullable=nullable),
        )

    def test_exact_string_is_accepted_without_case_or_unicode_normalization(self):
        cases = (
            ('when(enabled, language == "hu")', "hu", True),
            ('when(enabled, language == "HU")', "HU", True),
            ('when(enabled, language == "hu")', "HU", False),
            ('when(enabled, language == "hu")', " hu", False),
            ('when(enabled, language == "é")', "e\u0301", False),
        )
        for expression, value, passes in cases:
            with self.subTest(expression=expression, value=value):
                result = self.run_language(
                    expression,
                    ({"item_id": "item-1", "enabled": True, "language": value},),
                )
                self.assertIs(
                    result.outcome,
                    execution.ValidationOutcome.PASS
                    if passes
                    else execution.ValidationOutcome.FAIL,
                )

    def test_bool_int_and_float_are_rejected_without_coercion(self):
        for value in (True, 1, 1.0):
            with self.subTest(value=value, value_type=type(value).__name__):
                result = self.run_language(
                    'when(enabled, language == "hu")',
                    ({"item_id": "item-1", "enabled": True, "language": value},),
                )
                self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
                self.assertEqual(
                    result.diagnostics[0].reason,
                    "target_value_type_invalid:language",
                )

    def test_none_is_accepted_only_by_nullable_language_schema(self):
        nullable = self.run_language(
            "when(enabled, language == null)",
            ({"item_id": "item-1", "enabled": True, "language": None},),
            nullable=True,
        )
        required = self.run_language(
            "when(enabled, language == null)",
            ({"item_id": "item-1", "enabled": True, "language": None},),
        )
        self.assertIs(nullable.outcome, execution.ValidationOutcome.PASS)
        self.assertIs(required.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(
            required.diagnostics[0].reason, "target_value_null:language"
        )

    def test_missing_language_is_not_explicit_none(self):
        result = self.run_language(
            "when(enabled, language == null)",
            ({"item_id": "item-1", "enabled": True},),
            nullable=True,
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(
            result.diagnostics[0].reason, "target_field_missing:language"
        )

    def test_language_diagnostics_are_record_order_deterministic(self):
        records = (
            {"item_id": "item-3", "enabled": True, "language": "HU"},
            {"item_id": "item-1", "enabled": True, "language": "hu"},
            {"item_id": "item-2", "enabled": True, "language": "en"},
        )
        forward = self.run_language(
            'when(enabled, language == "hu")', records
        )
        reverse = self.run_language(
            'when(enabled, language == "hu")', tuple(reversed(records))
        )
        self.assertEqual(forward, reverse)
        self.assertEqual(
            tuple(item.record_identity for item in forward.diagnostics),
            ("item-2", "item-3"),
        )

    def test_malformed_language_schema_metadata_fails_closed(self):
        invalid_nullable = schema_field("language", "language_tag")
        invalid_nullable["nullable"] = "false"
        invalid_null_handling = schema_field("language", "language_tag")
        invalid_null_handling["null_handling"] = "explicit_null"
        cases = (
            (
                schema_field("language", "language"),
                "identifier_schema_type_not_supported:language",
            ),
            (
                invalid_nullable,
                "identifier_schema_nullable_invalid:language",
            ),
            (
                invalid_null_handling,
                "identifier_schema_null_contract_invalid:language",
            ),
        )
        for language_field, reason in cases:
            with self.subTest(reason=reason):
                result = execute(
                    make_definition_rule('language == "hu"'),
                    ({"item_id": "item-1", "language": "hu"},),
                    fields=(language_field,),
                )
                self.assertIs(
                    result.outcome, execution.ValidationOutcome.UNSUPPORTED
                )
                self.assertEqual(result.diagnostics[0].reason, reason)


class TestScalarLookupExecution(unittest.TestCase):
    EXPRESSION = (
        'lookup("references","reference_id",reference_id,"value") '
        '== expected'
    )

    @staticmethod
    def tables(
        target_records=(),
        lookup_records=(),
        *,
        include_lookup=True,
        key_field="reference_id",
        key_type="string",
        output_field="value",
        output_nullable=False,
        target_key_type="string",
        target_key_nullable=False,
    ):
        fields = [
            table_field(
                "items",
                "reference_id",
                target_key_type,
                nullable=target_key_nullable,
            ),
            table_field("items", "expected", nullable=True),
            table_field("references", "reference_id"),
            table_field("references", key_field, key_type),
            table_field(
                "references",
                output_field,
                nullable=output_nullable,
            ),
        ]
        unique_fields = {
            (field["table_id"], field["field_name"]): field
            for field in fields
        }
        tables = {
            "schema_tables": (
                {
                    "table_id": "items",
                    "primary_key": "item_id",
                    "status": "active",
                },
                {
                    "table_id": "references",
                    "primary_key": "reference_id",
                    "status": "active",
                },
            ),
            "schema_fields": tuple(unique_fields.values()),
            "items": tuple(target_records),
        }
        if include_lookup:
            tables["references"] = tuple(lookup_records)
        return tables

    def context(
        self,
        target_records=(),
        lookup_records=(),
        *,
        registry_options=None,
        carddatabase_options=None,
    ):
        registry = self.tables(
            target_records,
            lookup_records,
            **(registry_options or {}),
        )
        carddatabase = self.tables(
            (),
            (),
            **(carddatabase_options or {}),
        )
        return execution.ValidationDataContext(
            namespaced_tables={
                "registry": registry,
                "carddatabase": carddatabase,
            },
            component_namespaces={"registry-component": "registry"},
        )

    def execute_lookup(
        self,
        expression=None,
        *,
        target_records=None,
        lookup_records=None,
        context=None,
    ):
        if target_records is None:
            target_records = (
                {
                    "item_id": "item-1",
                    "reference_id": "alpha",
                    "expected": "A",
                },
            )
        if lookup_records is None:
            lookup_records = (
                {"reference_id": "alpha", "value": "A"},
            )
        return execution.execute_definition_invariant_rule(
            make_definition_rule(expression or self.EXPRESSION),
            context or self.context(target_records, lookup_records),
        )

    def assert_lookup_failure(self, result, reason):
        self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
        diagnostic = result.diagnostics[0]
        self.assertEqual(
            diagnostic.code,
            definition.VALIDATION_DEFINITION_LOOKUP_INVALID,
        )
        self.assertEqual(diagnostic.reason, reason)
        self.assertIn("source=registry", diagnostic.expected_contract)
        self.assertIn("key_field=", diagnostic.expected_contract)
        self.assertIn("output_field=", diagnostic.expected_contract)
        return diagnostic

    def test_local_exact_lookup_and_lookup_equals_identifier(self):
        result = self.execute_lookup()
        self.assertIs(result.outcome, execution.ValidationOutcome.PASS)
        self.assertEqual((result.evaluated_record_count, result.violation_count), (1, 0))

    def test_qualified_lookup_uses_explicit_namespace(self):
        registry = self.tables(
            ({"item_id": "item-1", "reference_id": "alpha", "expected": "C"},),
            ({"reference_id": "alpha", "value": "R"},),
        )
        carddatabase = self.tables(
            (), ({"reference_id": "alpha", "value": "C"},)
        )
        context = execution.ValidationDataContext(
            namespaced_tables={
                "registry": registry,
                "carddatabase": carddatabase,
            },
            component_namespaces={"registry-component": "registry"},
        )
        result = self.execute_lookup(
            'lookup("carddatabase:references","reference_id",'
            'reference_id,"value") == expected',
            context=context,
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.PASS)

    def test_explicit_namespace_projects_only_its_qualified_key(self):
        registry = self.tables(
            (
                {
                    "item_id": "item-1",
                    "reference_id": "carddatabase:alpha",
                    "expected": "C",
                },
            ),
            (),
        )
        carddatabase = self.tables(
            (), ({"reference_id": "alpha", "value": "C"},)
        )
        context = execution.ValidationDataContext(
            namespaced_tables={
                "registry": registry,
                "carddatabase": carddatabase,
            },
            component_namespaces={"registry-component": "registry"},
        )
        expression = (
            'lookup("references","reference_id",reference_id,"value") '
            "== expected or "
            'lookup("carddatabase:references","reference_id",'
            'reference_id,"value") == expected'
        )
        result = self.execute_lookup(expression, context=context)
        self.assertIs(result.outcome, execution.ValidationOutcome.PASS)

        wrong_registry = self.tables(
            (
                {
                    "item_id": "item-1",
                    "reference_id": "other:alpha",
                    "expected": "C",
                },
            ),
            (),
        )
        wrong_context = execution.ValidationDataContext(
            namespaced_tables={
                "registry": wrong_registry,
                "carddatabase": carddatabase,
            },
            component_namespaces={"registry-component": "registry"},
        )
        wrong_namespace = self.execute_lookup(
            'lookup("carddatabase:references","reference_id",'
            'reference_id,"value") == expected',
            context=wrong_context,
        )
        self.assertIs(
            wrong_namespace.outcome, execution.ValidationOutcome.FAIL
        )
        self.assertEqual(
            wrong_namespace.diagnostics[0].code,
            definition.VALIDATION_DEFINITION_INVARIANT_FAILED,
        )

    def test_zero_and_exact_nullable_none_have_distinct_internal_states(self):
        context = self.context(
            lookup_records=({"reference_id": "alpha", "value": None},),
            registry_options={"output_nullable": True},
        )
        domain = definition._resolve_lookup_domain(
            context,
            "registry",
            "references",
            "reference_id",
            "value",
        )
        zero = definition._resolve_scalar_lookup(domain, "missing")
        exact = definition._resolve_scalar_lookup(domain, "alpha")
        self.assertEqual(zero.state, "ZERO")
        self.assertEqual(exact.state, "EXACT")
        self.assertIsNone(zero.value)
        self.assertIsNone(exact.value)
        self.assertIsNone(zero.matched_record_identity)
        self.assertEqual(exact.matched_record_identity, "alpha")

    def test_zero_match_is_scalar_none_not_a_lookup_diagnostic(self):
        result = self.execute_lookup(
            'lookup("references","reference_id",reference_id,"value") '
            '== null',
            target_records=(
                {"item_id": "item-1", "reference_id": "missing"},
            ),
            lookup_records=(),
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.PASS)
        self.assertEqual(result.diagnostics, ())

    def test_zero_match_false_predicate_uses_invariant_diagnostic(self):
        result = self.execute_lookup(
            'lookup("references","reference_id",reference_id,"value") '
            '!= null',
            target_records=(
                {"item_id": "item-1", "reference_id": "missing"},
            ),
            lookup_records=(),
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(
            result.diagnostics[0].code,
            definition.VALIDATION_DEFINITION_INVARIANT_FAILED,
        )
        self.assertEqual(result.diagnostics[0].reason, "predicate_false")

    def test_exact_nullable_output_none_is_legitimate(self):
        context = self.context(
            ({"item_id": "item-1", "reference_id": "alpha"},),
            ({"reference_id": "alpha", "value": None},),
            registry_options={"output_nullable": True},
        )
        result = self.execute_lookup(
            'lookup("references","reference_id",reference_id,"value") '
            '== null',
            context=context,
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.PASS)

    def test_nested_lookup_lookup_equality_and_membership(self):
        lookup_records = (
            {"reference_id": "start", "value": "finish"},
            {"reference_id": "finish", "value": "done"},
            {"reference_id": "other", "value": "finish"},
        )
        target = ({"item_id": "item-1", "reference_id": "start"},)
        expressions = (
            'lookup("references","reference_id",'
            'lookup("references","reference_id",reference_id,"value"),'
            '"value") == "done"',
            'lookup("references","reference_id",reference_id,"value") '
            '== lookup("references","reference_id","other","value")',
            'lookup("references","reference_id",reference_id,"value") '
            'in ["finish","alternate"]',
        )
        for expression in expressions:
            with self.subTest(expression=expression):
                result = self.execute_lookup(
                    expression,
                    target_records=target,
                    lookup_records=lookup_records,
                )
                self.assertIs(result.outcome, execution.ValidationOutcome.PASS)

    def test_nested_zero_result_becomes_invalid_outer_null_key(self):
        result = self.execute_lookup(
            'lookup("references","reference_id",'
            'lookup("references","reference_id",reference_id,"value"),'
            '"value") == null',
            target_records=(
                {"item_id": "item-1", "reference_id": "missing"},
            ),
            lookup_records=(),
        )
        self.assert_lookup_failure(result, "lookup_null_key")

    def test_missing_namespace_table_and_fields_fail_closed(self):
        cases = (
            (
                'lookup("missing:references","reference_id",'
                'reference_id,"value") == expected',
                self.context(),
                "lookup_namespace_invalid",
            ),
            (
                self.EXPRESSION,
                self.context(registry_options={"include_lookup": False}),
                "lookup_table_missing",
            ),
            (
                'lookup("references","missing",reference_id,"value") '
                '== expected',
                self.context(),
                "lookup_key_field_unresolved",
            ),
            (
                'lookup("references","reference_id",reference_id,'
                '"missing") == expected',
                self.context(),
                "lookup_output_field_unresolved",
            ),
        )
        for expression, context, reason in cases:
            with self.subTest(reason=reason):
                result = self.execute_lookup(expression, context=context)
                self.assert_lookup_failure(result, reason)
                self.assertEqual(result.evaluated_record_count, 0)

    def test_non_primary_key_lookup_is_statically_unsupported(self):
        context = self.context(
            registry_options={"key_field": "alias_id"}
        )
        result = self.execute_lookup(
            'lookup("references","alias_id",reference_id,"value") '
            '== expected',
            context=context,
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.UNSUPPORTED)
        self.assertEqual((result.evaluated_record_count, result.violation_count), (0, 0))
        self.assertEqual(
            result.diagnostics[0].reason,
            "lookup_key_field_not_primary",
        )

    def test_wrong_type_and_invoked_null_key_are_lookup_failures(self):
        wrong_type_context = self.context(
            ({"item_id": "item-1", "reference_id": 1, "expected": "A"},),
            ({"reference_id": "1", "value": "A"},),
            registry_options={"target_key_type": "integer"},
        )
        wrong_type = self.execute_lookup(context=wrong_type_context)
        self.assert_lookup_failure(wrong_type, "lookup_key_type_invalid")

        null_context = self.context(
            ({"item_id": "item-1", "reference_id": None},),
            (),
            registry_options={"target_key_nullable": True},
        )
        null_key = self.execute_lookup(
            'lookup("references","reference_id",reference_id,"value") '
            '== null',
            context=null_context,
        )
        self.assert_lookup_failure(null_key, "lookup_null_key")

    def test_missing_source_field_is_target_invalid_not_lookup_zero_or_null(self):
        result = self.execute_lookup(
            target_records=({"item_id": "item-1", "expected": "A"},),
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(
            result.diagnostics[0].code,
            definition.VALIDATION_DEFINITION_TARGET_RECORD_INVALID,
        )
        self.assertEqual(
            result.diagnostics[0].reason,
            "target_field_missing:reference_id",
        )

    def test_false_guard_does_not_invoke_null_key_lookup(self):
        context = self.context(
            ({"item_id": "item-1", "reference_id": None, "enabled": False},),
            (),
            registry_options={"target_key_nullable": True},
        )
        registry = {
            table: context.table(table, namespace="registry")
            for table in ("schema_tables", "schema_fields", "items", "references")
        }
        registry["schema_fields"] += (
            table_field("items", "enabled", "boolean"),
        )
        context = execution.ValidationDataContext(
            namespaced_tables={
                "registry": registry,
                "carddatabase": self.tables(),
            },
            component_namespaces={"registry-component": "registry"},
        )
        original = definition._resolve_scalar_lookup
        try:
            definition._resolve_scalar_lookup = lambda *_: (_ for _ in ()).throw(
                AssertionError("short-circuited lookup was invoked")
            )
            result = self.execute_lookup(
                'when(enabled,lookup("references","reference_id",'
                'reference_id,"value") == null)',
                context=context,
            )
        finally:
            definition._resolve_scalar_lookup = original
        self.assertIs(result.outcome, execution.ValidationOutcome.PASS)

    def test_duplicate_match_is_fail_closed_and_order_independent(self):
        records = (
            {"reference_id": "alpha", "value": "A"},
            {"reference_id": "alpha", "value": "B"},
        )
        forward = self.execute_lookup(lookup_records=records)
        reverse = self.execute_lookup(lookup_records=tuple(reversed(records)))
        self.assertEqual(forward, reverse)
        diagnostic = self.assert_lookup_failure(
            forward, "lookup_ambiguous"
        )
        self.assertEqual(
            diagnostic.related_record_identities,
            ("alpha", "alpha"),
        )

    def test_success_is_independent_of_target_and_lookup_record_order(self):
        targets = (
            {"item_id": "item-2", "reference_id": "beta", "expected": "B"},
            {"item_id": "item-1", "reference_id": "alpha", "expected": "A"},
        )
        lookups = (
            {"reference_id": "alpha", "value": "A"},
            {"reference_id": "beta", "value": "B"},
        )
        forward = self.execute_lookup(
            target_records=targets, lookup_records=lookups
        )
        reverse = self.execute_lookup(
            target_records=tuple(reversed(targets)),
            lookup_records=tuple(reversed(lookups)),
        )
        self.assertEqual(forward, reverse)
        self.assertIs(forward.outcome, execution.ValidationOutcome.PASS)

    def test_invalid_output_and_record_identity_fail_closed(self):
        cases = (
            (
                ({"reference_id": "alpha"},),
                "lookup_output_value_invalid",
            ),
            (
                ({"reference_id": "alpha", "value": 1},),
                "lookup_output_value_invalid",
            ),
            (
                (
                    {"reference_id": None, "value": "invalid"},
                    {"reference_id": "alpha", "value": "A"},
                ),
                "lookup_record_identity_invalid",
            ),
        )
        for records, reason in cases:
            with self.subTest(reason=reason, records=records):
                result = self.execute_lookup(lookup_records=records)
                diagnostic = self.assert_lookup_failure(result, reason)
                self.assertTrue(diagnostic.related_record_identities)
                self.assertTrue(
                    all("{" not in item for item in diagnostic.related_record_identities)
                )

    def test_unqualified_lookup_never_falls_back_to_other_namespace(self):
        registry = self.tables(
            ({"item_id": "item-1", "reference_id": "alpha", "expected": "C"},),
            (),
            include_lookup=False,
        )
        carddatabase = self.tables(
            (), ({"reference_id": "alpha", "value": "C"},)
        )
        context = execution.ValidationDataContext(
            namespaced_tables={
                "registry": registry,
                "carddatabase": carddatabase,
            },
            component_namespaces={"registry-component": "registry"},
        )
        result = self.execute_lookup(context=context)
        self.assert_lookup_failure(result, "lookup_table_missing")


class TestRecordLookupExecution(unittest.TestCase):
    EXPRESSION = (
        'row = lookup_record("references","reference_id",reference_id); '
        "row != null and row.value == expected"
    )

    @staticmethod
    def context(
        target_records=(),
        lookup_records=(),
        *,
        registry_options=None,
        carddatabase_options=None,
    ):
        registry = TestScalarLookupExecution.tables(
            target_records,
            lookup_records,
            **(registry_options or {}),
        )
        carddatabase = TestScalarLookupExecution.tables(
            (), (), **(carddatabase_options or {})
        )
        return execution.ValidationDataContext(
            namespaced_tables={
                "registry": registry,
                "carddatabase": carddatabase,
            },
            component_namespaces={"registry-component": "registry"},
        )

    def execute_record(
        self,
        expression=None,
        *,
        target_records=None,
        lookup_records=None,
        context=None,
    ):
        if target_records is None:
            target_records = ({
                "item_id": "item-1",
                "reference_id": "alpha",
                "expected": "A",
            },)
        if lookup_records is None:
            lookup_records = ({"reference_id": "alpha", "value": "A"},)
        return execution.execute_definition_invariant_rule(
            make_definition_rule(expression or self.EXPRESSION),
            context or self.context(target_records, lookup_records),
        )

    def assert_lookup_failure(self, result, reason):
        self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(
            result.diagnostics[0].code,
            definition.VALIDATION_DEFINITION_LOOKUP_INVALID,
        )
        self.assertEqual(result.diagnostics[0].reason, reason)
        return result.diagnostics[0]

    def test_zero_is_none_and_one_is_copied_immutable_record(self):
        context = self.context(
            ({"item_id": "item-1", "reference_id": "alpha"},),
            ({"reference_id": "alpha", "value": "A"},),
        )
        domain = definition._resolve_record_lookup_domain(
            context, "registry", "references", "reference_id"
        )
        zero = definition._resolve_record_lookup(domain, "missing")
        one = definition._resolve_record_lookup(domain, "alpha")
        self.assertEqual(zero.state, "ZERO")
        self.assertIsNone(zero.value)
        self.assertEqual(one.state, "EXACT")
        self.assertIsInstance(one.value, MappingProxyType)
        self.assertIsNot(one.value, domain.records[0])
        self.assertEqual(dict(one.value), dict(domain.records[0]))
        with self.assertRaises(TypeError):
            one.value["value"] = "changed"

        result = self.execute_record(
            'row = lookup_record("references","reference_id",'
            "reference_id); row == null",
            target_records=(
                {"item_id": "item-1", "reference_id": "missing"},
            ),
            lookup_records=(),
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.PASS)

    def test_primary_key_one_match_member_value_is_exact(self):
        result = self.execute_record()
        self.assertIs(result.outcome, execution.ValidationOutcome.PASS)
        self.assertEqual(
            (result.evaluated_record_count, result.violation_count), (1, 0)
        )

    def test_non_primary_key_zero_and_one_follow_actual_multiplicity(self):
        lookup_records = ({
            "reference_id": "record-A",
            "kind": "unique-kind",
            "value": "A",
        },)
        options = {"key_field": "kind"}
        zero = self.execute_record(
            'row = lookup_record("references","kind",reference_id); '
            "row == null",
            context=self.context(
                ({
                    "item_id": "item-zero",
                    "reference_id": "missing-kind",
                },),
                lookup_records,
                registry_options=options,
            ),
        )
        one = self.execute_record(
            'row = lookup_record("references","kind",reference_id); '
            "row != null and row.value == expected",
            context=self.context(
                ({
                    "item_id": "item-one",
                    "reference_id": "unique-kind",
                    "expected": "A",
                },),
                lookup_records,
                registry_options=options,
            ),
        )
        self.assertIs(zero.outcome, execution.ValidationOutcome.PASS)
        self.assertIs(one.outcome, execution.ValidationOutcome.PASS)
        self.assertEqual(
            (zero.evaluated_record_count, zero.violation_count), (1, 0)
        )
        self.assertEqual(
            (one.evaluated_record_count, one.violation_count), (1, 0)
        )

    def test_non_primary_key_multiple_matches_are_deterministically_ambiguous(self):
        records = (
            {"reference_id": "record-B", "kind": "x", "value": "B"},
            {"reference_id": "record-A", "kind": "x", "value": "A"},
        )
        expression = (
            'row = lookup_record("references","kind",reference_id); '
            "row != null"
        )
        target = ({
            "item_id": "item-1",
            "reference_id": "x",
        },)
        forward = self.execute_record(
            expression,
            context=self.context(
                target,
                records,
                registry_options={"key_field": "kind"},
            ),
        )
        reverse = self.execute_record(
            expression,
            context=self.context(
                target,
                tuple(reversed(records)),
                registry_options={"key_field": "kind"},
            ),
        )
        self.assertEqual(forward, reverse)
        diagnostic = self.assert_lookup_failure(
            forward, "lookup_ambiguous"
        )
        self.assertEqual(
            diagnostic.related_record_identities,
            ("record-A", "record-B"),
        )

    def test_nonexistent_record_key_field_is_a_controlled_error(self):
        result = self.execute_record(
            'row = lookup_record("references","missing",reference_id); '
            "row == null"
        )
        diagnostic = self.assert_lookup_failure(
            result, "lookup_key_field_unresolved"
        )
        self.assertEqual(result.evaluated_record_count, 0)
        self.assertIn("key_field=missing", diagnostic.expected_contract)

    def test_missing_non_primary_key_value_is_a_controlled_error(self):
        result = self.execute_record(
            'row = lookup_record("references","kind",reference_id); '
            "row == null",
            context=self.context(
                ({
                    "item_id": "item-1",
                    "reference_id": "x",
                },),
                ({"reference_id": "record-A", "value": "A"},),
                registry_options={"key_field": "kind"},
            ),
        )
        diagnostic = self.assert_lookup_failure(
            result, "lookup_record_key_value_invalid"
        )
        self.assertEqual(
            diagnostic.related_record_identities, ("record-A",)
        )

    def test_ambiguity_is_fail_closed_and_record_order_deterministic(self):
        records = (
            {"reference_id": "alpha", "value": "A"},
            {"reference_id": "alpha", "value": "B"},
        )
        forward = self.execute_record(lookup_records=records)
        reverse = self.execute_record(
            lookup_records=tuple(reversed(records))
        )
        self.assertEqual(forward, reverse)
        diagnostic = self.assert_lookup_failure(forward, "lookup_ambiguous")
        self.assertEqual(
            diagnostic.related_record_identities, ("alpha", "alpha")
        )

    def test_null_key_and_missing_source_fail_closed(self):
        null_context = self.context(
            ({"item_id": "item-1", "reference_id": None},),
            (),
            registry_options={"target_key_nullable": True},
        )
        null_result = self.execute_record(
            'row = lookup_record("references","reference_id",'
            "reference_id); row == null",
            context=null_context,
        )
        self.assert_lookup_failure(null_result, "lookup_null_key")

        missing_context = self.context(
            registry_options={"include_lookup": False}
        )
        missing = self.execute_record(context=missing_context)
        self.assert_lookup_failure(missing, "lookup_table_missing")
        self.assertEqual(missing.evaluated_record_count, 0)

    def test_namespace_is_exact_and_never_falls_back(self):
        registry = TestScalarLookupExecution.tables(
            ({
                "item_id": "item-1",
                "reference_id": "alpha",
                "expected": "C",
            },),
            (),
            include_lookup=False,
        )
        carddatabase = TestScalarLookupExecution.tables(
            (), ({"reference_id": "alpha", "value": "C"},)
        )
        context = execution.ValidationDataContext(
            namespaced_tables={
                "registry": registry,
                "carddatabase": carddatabase,
            },
            component_namespaces={"registry-component": "registry"},
        )
        qualified = self.execute_record(
            'row = lookup_record("carddatabase:references",'
            '"reference_id",reference_id); row.value == expected',
            context=context,
        )
        self.assertIs(qualified.outcome, execution.ValidationOutcome.PASS)
        unqualified = self.execute_record(context=context)
        self.assert_lookup_failure(unqualified, "lookup_table_missing")

        invalid_namespace = self.execute_record(
            'row = lookup_record("missing:references","reference_id",'
            "reference_id); row != null",
            context=context,
        )
        self.assert_lookup_failure(
            invalid_namespace, "lookup_namespace_invalid"
        )

    def test_member_missing_and_none_member_are_controlled_record_failures(self):
        missing = self.execute_record(
            'row = lookup_record("references","reference_id",'
            "reference_id); row.missing == null"
        )
        self.assertIs(missing.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(
            missing.diagnostics[0].reason,
            "expression_evaluation_error:member_missing",
        )
        none_member = self.execute_record(
            'row = lookup_record("references","reference_id",'
            "reference_id); row.value == null",
            target_records=(
                {"item_id": "item-1", "reference_id": "missing"},
            ),
            lookup_records=(),
        )
        self.assertIs(none_member.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(
            none_member.diagnostics[0].reason,
            "expression_evaluation_error:member_access_base_is_none",
        )

    def test_chained_member_key_and_context_immutability(self):
        targets = (
            {"item_id": "item-2", "reference_id": "start", "expected": "done"},
            {"item_id": "item-1", "reference_id": "start", "expected": "done"},
        )
        lookups = (
            {"reference_id": "finish", "value": "done"},
            {"reference_id": "start", "value": "finish"},
        )
        context = self.context(targets, lookups)
        before = tuple(
            tuple(dict(record).items())
            for record in context.table("references", namespace="registry")
        )
        expression = (
            'first = lookup_record("references","reference_id",reference_id); '
            'second = lookup_record("references","reference_id",first.value); '
            "second.value == expected"
        )
        forward = self.execute_record(expression, context=context)
        reverse = self.execute_record(
            expression,
            context=self.context(
                tuple(reversed(targets)), tuple(reversed(lookups))
            ),
        )
        after = tuple(
            tuple(dict(record).items())
            for record in context.table("references", namespace="registry")
        )
        self.assertEqual(forward, reverse)
        self.assertIs(forward.outcome, execution.ValidationOutcome.PASS)
        self.assertEqual(before, after)

    def test_false_when_guard_does_not_resolve_record(self):
        context = self.context(
            ({
                "item_id": "item-1",
                "reference_id": None,
                "expected": None,
                "enabled": False,
            },),
            (),
            registry_options={"target_key_nullable": True},
        )
        registry = {
            table: context.table(table, namespace="registry")
            for table in (
                "schema_tables", "schema_fields", "items", "references"
            )
        }
        registry["schema_fields"] += (
            table_field("items", "enabled", "boolean"),
        )
        guarded_context = execution.ValidationDataContext(
            namespaced_tables={
                "registry": registry,
                "carddatabase": TestScalarLookupExecution.tables(),
            },
            component_namespaces={"registry-component": "registry"},
        )
        expression = (
            "when(enabled,row = lookup_record("
            '"references","reference_id",reference_id); row != null)'
        )
        original = definition._resolve_record_lookup
        try:
            definition._resolve_record_lookup = lambda *_: (_ for _ in ()).throw(
                AssertionError("false guard invoked record lookup")
            )
            result = self.execute_record(
                expression, context=guarded_context
            )
        finally:
            definition._resolve_record_lookup = original
        self.assertIs(result.outcome, execution.ValidationOutcome.PASS)

    def test_lookup_record_by_and_nested_member_remain_unsupported(self):
        expression = (
            'row = lookup_record("references","reference_id",reference_id); '
            "row.nested.value == expected"
        )
        result = self.execute_record(expression)
        self.assertIs(result.outcome, execution.ValidationOutcome.UNSUPPORTED)


class TestCompositeRecordLookupExecution(unittest.TestCase):
    EXPRESSION = (
        'row = lookup_record_by("references",["kind","ordinal"],'
        "[kind,ordinal]); row != null and row.value == expected"
    )

    @staticmethod
    def tables(
        target_records=(),
        lookup_records=(),
        *,
        include_lookup=True,
        include_reference_table_schema=True,
        reference_fields=None,
        target_ordinal_type="integer",
        target_ordinal_nullable=False,
    ):
        fields = [
            table_field("items", "kind"),
            table_field(
                "items",
                "ordinal",
                target_ordinal_type,
                nullable=target_ordinal_nullable,
            ),
            table_field("items", "expected", nullable=True),
            table_field("references", "reference_id"),
            table_field("references", "kind"),
            table_field("references", "ordinal", "integer"),
            table_field("references", "enabled", "boolean"),
            table_field("references", "region"),
            table_field("references", "value"),
        ]
        if reference_fields is not None:
            fields = [
                field for field in fields
                if field["table_id"] != "references"
            ] + list(reference_fields)
        schema_tables = [
            {"table_id": "items", "primary_key": "item_id", "status": "active"},
        ]
        if include_reference_table_schema:
            schema_tables.append({
                "table_id": "references",
                "primary_key": "reference_id",
                "status": "active",
            })
        result = {
            "schema_tables": tuple(schema_tables),
            "schema_fields": tuple(fields),
            "items": tuple(target_records),
        }
        if include_lookup:
            result["references"] = tuple(lookup_records)
        return result

    @classmethod
    def context(cls, target_records=(), lookup_records=(), **options):
        return execution.ValidationDataContext(
            namespaced_tables={
                "registry": cls.tables(
                    target_records, lookup_records, **options
                ),
                "carddatabase": cls.tables(),
            },
            component_namespaces={"registry-component": "registry"},
        )

    @classmethod
    def execute_lookup_by(
        cls, expression=None, target_records=None, lookup_records=None, **options
    ):
        target_records = target_records if target_records is not None else ({
            "item_id": "item-1",
            "kind": "alpha",
            "ordinal": 2,
            "expected": "A",
        },)
        lookup_records = lookup_records if lookup_records is not None else ({
            "reference_id": "ref-A",
            "kind": "alpha",
            "ordinal": 2,
            "enabled": True,
            "region": "eu",
            "value": "A",
        },)
        return execution.execute_definition_invariant_rule(
            make_definition_rule(expression or cls.EXPRESSION),
            cls.context(target_records, lookup_records, **options),
        )

    def assert_lookup_failure(self, result, reason):
        self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(
            result.diagnostics[0].code,
            definition.VALIDATION_DEFINITION_LOOKUP_INVALID,
        )
        self.assertEqual(result.diagnostics[0].reason, reason)
        return result.diagnostics[0]

    def test_single_composite_and_three_field_resolution(self):
        single = self.execute_lookup_by(
            'row = lookup_record_by("references",["kind"],[kind]); '
            "row != null",
        )
        composite = self.execute_lookup_by()
        three = self.execute_lookup_by(
            'row = lookup_record_by("references",'
            '["kind","ordinal","region"],[kind,ordinal,"eu"]); '
            "row != null and row.value == expected",
        )
        self.assertTrue(all(
            result.outcome is execution.ValidationOutcome.PASS
            for result in (single, composite, three)
        ))

        context = self.context(
            ({"item_id": "item-1", "kind": "missing", "ordinal": 2},),
            (),
        )
        domain = definition._resolve_composite_record_lookup_domain(
            context, "registry", "references", ("kind", "ordinal")
        )
        zero = definition._resolve_composite_record_lookup(
            domain, ("missing", 2)
        )
        self.assertEqual(zero.state, "ZERO")
        self.assertIsNone(zero.value)

    def test_exact_types_do_not_coerce_bool_int_or_string(self):
        bool_expression = (
            'row = lookup_record_by("references",["enabled"],[ordinal]); '
            "row == null"
        )
        bool_vs_int = self.execute_lookup_by(
            bool_expression,
            target_records=({
                "item_id": "item-1", "kind": "x", "ordinal": 1
            },),
        )
        string_vs_int = self.execute_lookup_by(
            'row = lookup_record_by("references",["ordinal"],[kind]); '
            "row == null",
            target_records=({
                "item_id": "item-1", "kind": "2", "ordinal": 2
            },),
        )
        self.assertTrue(all(
            result.outcome is execution.ValidationOutcome.FAIL
            and result.diagnostics[0].reason == "lookup_key_type_invalid"
            for result in (bool_vs_int, string_vs_int)
        ))

    def test_qualified_namespace_and_unqualified_no_fallback(self):
        registry = self.tables(
            ({
                "item_id": "item-1", "kind": "alpha", "ordinal": 2,
                "expected": "C",
            },),
            (),
            include_lookup=False,
        )
        carddatabase = self.tables(
            (),
            ({
                "reference_id": "ref-C", "kind": "alpha", "ordinal": 2,
                "enabled": True, "region": "eu", "value": "C",
            },),
        )
        context = execution.ValidationDataContext(
            namespaced_tables={
                "registry": registry,
                "carddatabase": carddatabase,
            },
            component_namespaces={"registry-component": "registry"},
        )
        qualified = execution.execute_definition_invariant_rule(
            make_definition_rule(self.EXPRESSION.replace(
                '"references"', '"carddatabase:references"'
            )),
            context,
        )
        unqualified = execution.execute_definition_invariant_rule(
            make_definition_rule(self.EXPRESSION), context
        )
        unknown = execution.execute_definition_invariant_rule(
            make_definition_rule(self.EXPRESSION.replace(
                '"references"', '"missing:references"'
            )),
            context,
        )
        self.assertIs(qualified.outcome, execution.ValidationOutcome.PASS)
        self.assert_lookup_failure(unqualified, "lookup_table_missing")
        self.assert_lookup_failure(unknown, "lookup_namespace_invalid")

    def test_malformed_contracts_fail_closed(self):
        expressions = (
            ('row = lookup_record_by("references",kind,[kind]); '
             'row == null',
             "lookup_record_by_key_fields_collection_required"),
            ('row = lookup_record_by("references",[],[]); row == null',
             "lookup_record_by_key_fields_empty"),
            ('row = lookup_record_by("references",["kind","kind"],'
             '[kind,kind]); row == null',
             "lookup_record_by_key_field_duplicate"),
            ('row = lookup_record_by("references",[null],[kind]); '
             'row == null', "lookup_record_by_key_field_invalid"),
            ('row = lookup_record_by("references",["missing"],[kind]); '
             'row == null', "lookup_key_field_unresolved"),
        )
        for expression, reason in expressions:
            with self.subTest(reason=reason):
                self.assert_lookup_failure(
                    self.execute_lookup_by(expression), reason
                )

        evaluation_cases = (
            ('row = lookup_record_by("references",["kind"],kind); '
             'row == null',
             "lookup_record_by_key_values_collection_required"),
            ('row = lookup_record_by("references",["kind"],[]); '
             'row == null', "lookup_record_by_key_arity_mismatch"),
            ('row = lookup_record_by("references",["kind"],[null]); '
             'row == null', "lookup_record_by_null_key_value"),
            ('row = lookup_record_by("references",["kind"],[[kind]]); '
             'row == null', "lookup_record_by_key_value_type_unsupported"),
            ('base = lookup_record("references","reference_id","ref-A"); '
             'row = lookup_record_by("references",["kind"],[base]); '
             'row == null', "lookup_record_by_key_value_type_unsupported"),
        )
        for expression, reason in evaluation_cases:
            with self.subTest(reason=reason):
                result = self.execute_lookup_by(expression)
                self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
                self.assertEqual(
                    result.diagnostics[0].reason,
                    f"expression_evaluation_error:{reason}",
                )

    def test_missing_or_malformed_candidate_and_table_authority_fail_closed(self):
        missing_field = self.execute_lookup_by(
            lookup_records=({
                "reference_id": "ref-A", "ordinal": 2, "enabled": True,
                "region": "eu", "value": "A",
            },),
        )
        self.assert_lookup_failure(
            missing_field, "lookup_record_key_value_invalid"
        )
        missing_table = self.execute_lookup_by(include_lookup=False)
        self.assert_lookup_failure(missing_table, "lookup_table_missing")
        malformed_authority = self.execute_lookup_by(
            include_reference_table_schema=False
        )
        self.assert_lookup_failure(
            malformed_authority, "lookup_record_identity_invalid"
        )

    def test_ambiguity_and_reversed_source_order_are_deterministic(self):
        records = (
            {
                "reference_id": "ref-B", "kind": "alpha", "ordinal": 2,
                "enabled": True, "region": "eu", "value": "B",
            },
            {
                "reference_id": "ref-A", "kind": "alpha", "ordinal": 2,
                "enabled": False, "region": "eu", "value": "A",
            },
        )
        forward = self.execute_lookup_by(lookup_records=records)
        reverse = self.execute_lookup_by(
            lookup_records=tuple(reversed(records))
        )
        self.assertEqual(forward, reverse)
        diagnostic = self.assert_lookup_failure(forward, "lookup_ambiguous")
        self.assertEqual(
            diagnostic.related_record_identities, ("ref-A", "ref-B")
        )


class TestGeneratedNodeDefinitionExecution(unittest.TestCase):
    EXPRESSION = (
        'when(binding_kind_id == "generated_node_id",'
        'current_node = lookup_record("ability_template_nodes",'
        '"template_node_id",template_node_id); '
        'source = lookup_record_by("ability_template_nodes",'
        '["ability_template_id","node_key"],'
        '[current_node.ability_template_id,source_node_key]); '
        'target_field = lookup_record("carddatabase:schema_fields",'
        '"field_id",target_field_id); '
        'source != null and target_field != null and '
        'source.node_order < current_node.node_order and '
        'target_field.reference_table_id == source.output_table_id and '
        'target_field.reference_field_id != null and '
        'lookup("carddatabase:schema_fields","field_id",'
        'target_field.reference_field_id,"table_id") == '
        'source.output_table_id and '
        'lookup("carddatabase:schema_fields","field_id",'
        'target_field.reference_field_id,"field_name") == '
        'lookup("carddatabase:schema_tables","table_id",'
        'source.output_table_id,"primary_key"))'
    )

    @staticmethod
    def binding(**changes):
        row = {
            "template_binding_id": "binding-1",
            "binding_kind_id": "generated_node_id",
            "template_node_id": "node-current",
            "source_node_key": "source",
            "target_field_id": "target-field",
        }
        row.update(changes)
        return row

    @staticmethod
    def nodes():
        return (
            {
                "template_node_id": "node-source",
                "ability_template_id": "template-1",
                "node_key": "source",
                "node_order": 1,
                "output_table_id": "ability_targets",
            },
            {
                "template_node_id": "node-current",
                "ability_template_id": "template-1",
                "node_key": "current",
                "node_order": 2,
                "output_table_id": "ability_effects",
            },
        )

    @classmethod
    def context(
        cls,
        *,
        bindings=None,
        nodes=None,
        target_field=None,
        referenced_field=None,
        referenced_tables=None,
    ):
        bindings = tuple(bindings or (cls.binding(),))
        nodes = tuple(nodes if nodes is not None else cls.nodes())
        registry_fields = (
            table_field("ability_template_bindings", "binding_kind_id"),
            table_field("ability_template_bindings", "template_node_id"),
            table_field(
                "ability_template_bindings", "source_node_key", nullable=True
            ),
            table_field("ability_template_bindings", "target_field_id"),
            table_field("ability_template_nodes", "template_node_id"),
            table_field("ability_template_nodes", "ability_template_id"),
            table_field("ability_template_nodes", "node_key"),
            table_field("ability_template_nodes", "node_order", "integer"),
            table_field("ability_template_nodes", "output_table_id"),
        )
        registry = {
            "schema_tables": (
                {
                    "table_id": "ability_template_bindings",
                    "primary_key": "template_binding_id",
                    "status": "active",
                },
                {
                    "table_id": "ability_template_nodes",
                    "primary_key": "template_node_id",
                    "status": "active",
                },
            ),
            "schema_fields": registry_fields,
            "ability_template_bindings": bindings,
            "ability_template_nodes": nodes,
        }
        target_field = target_field or {
            "field_id": "target-field",
            "table_id": "ability_effects",
            "field_name": "target_id",
            "reference_table_id": "ability_targets",
            "reference_field_id": "target-pk-field",
            "status": "active",
        }
        referenced_field = referenced_field or {
            "field_id": "target-pk-field",
            "table_id": "ability_targets",
            "field_name": "target_id",
            "reference_table_id": None,
            "reference_field_id": None,
            "status": "active",
        }
        schema_contracts = (
            table_field("schema_fields", "field_id"),
            table_field("schema_fields", "table_id"),
            table_field("schema_fields", "field_name"),
            table_field("schema_tables", "table_id"),
            table_field("schema_tables", "primary_key"),
        )
        schema_tables = (
            {
                "table_id": "schema_fields",
                "primary_key": "field_id",
                "status": "active",
            },
            {
                "table_id": "schema_tables",
                "primary_key": "table_id",
                "status": "active",
            },
            {
                "table_id": "ability_effects",
                "primary_key": "effect_id",
                "status": "active",
            },
        ) + tuple(referenced_tables or ({
            "table_id": "ability_targets",
            "primary_key": "target_id",
            "status": "active",
        },))
        carddatabase = {
            "schema_tables": schema_tables,
            "schema_fields": schema_contracts
            + (target_field, referenced_field),
        }
        return execution.ValidationDataContext(
            namespaced_tables={
                "registry": registry,
                "carddatabase": carddatabase,
            },
            component_namespaces={"registry-component": "registry"},
        )

    @classmethod
    def execute_generated(cls, **context_options):
        return execution.execute_definition_invariant_rule(
            make_definition_rule(
                cls.EXPRESSION,
                rule_id="generated_node_synthetic",
                table_id="ability_template_bindings",
                target_field_id=None,
            ),
            cls.context(**context_options),
        )

    def assert_predicate_failure(self, result):
        self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(
            result.diagnostics[0].code,
            definition.VALIDATION_DEFINITION_INVARIANT_FAILED,
        )
        self.assertEqual(result.diagnostics[0].reason, "predicate_false")

    def test_full_contract_passes_and_false_guard_skips_body(self):
        passed = self.execute_generated()
        guarded = self.execute_generated(bindings=(self.binding(
            binding_kind_id="fixed_value",
            template_node_id="missing",
            source_node_key=None,
            target_field_id="missing",
        ),), nodes=())
        for result in (passed, guarded):
            self.assertIs(result.outcome, execution.ValidationOutcome.PASS)
            self.assertEqual(
                (result.evaluated_record_count, result.violation_count),
                (1, 0),
            )
            self.assertEqual(result.diagnostics, ())

    def test_source_absent_same_later_and_wrong_template_are_violations(self):
        absent = self.execute_generated(nodes=(self.nodes()[1],))
        same_order_nodes = (
            {**self.nodes()[0], "node_order": 2}, self.nodes()[1]
        )
        later_nodes = (
            {**self.nodes()[0], "node_order": 3}, self.nodes()[1]
        )
        wrong_template_nodes = (
            {**self.nodes()[0], "ability_template_id": "template-2"},
            self.nodes()[1],
        )
        for result in (
            absent,
            self.execute_generated(nodes=same_order_nodes),
            self.execute_generated(nodes=later_nodes),
            self.execute_generated(nodes=wrong_template_nodes),
        ):
            self.assert_predicate_failure(result)

    def test_reference_table_null_field_wrong_table_and_non_pk_are_violations(self):
        wrong_reference_table = self.execute_generated(target_field={
            "field_id": "target-field",
            "table_id": "ability_effects",
            "field_name": "target_id",
            "reference_table_id": "other_table",
            "reference_field_id": "target-pk-field",
            "status": "active",
        })
        null_reference = self.execute_generated(target_field={
            "field_id": "target-field",
            "table_id": "ability_effects",
            "field_name": "target_id",
            "reference_table_id": "ability_targets",
            "reference_field_id": None,
            "status": "active",
        })
        wrong_field_table = self.execute_generated(referenced_field={
            "field_id": "target-pk-field",
            "table_id": "other_table",
            "field_name": "target_id",
            "reference_table_id": None,
            "reference_field_id": None,
            "status": "active",
        })
        non_pk = self.execute_generated(referenced_field={
            "field_id": "target-pk-field",
            "table_id": "ability_targets",
            "field_name": "display_name",
            "reference_table_id": None,
            "reference_field_id": None,
            "status": "active",
        })
        for result in (
            wrong_reference_table, null_reference, wrong_field_table, non_pk
        ):
            self.assert_predicate_failure(result)

    def test_missing_current_malformed_target_and_ambiguous_source_are_controlled(self):
        missing_current = self.execute_generated(nodes=(self.nodes()[0],))
        malformed_target = self.execute_generated(target_field={
            "field_id": "target-field",
            "table_id": "ability_effects",
            "field_name": "target_id",
            "reference_field_id": "target-pk-field",
            "status": "active",
        })
        ambiguous = self.execute_generated(nodes=(
            self.nodes()[0],
            {**self.nodes()[0], "template_node_id": "node-source-2"},
            self.nodes()[1],
        ))
        self.assertEqual(
            missing_current.diagnostics[0].reason,
            "expression_evaluation_error:member_access_base_is_none",
        )
        self.assertEqual(
            malformed_target.diagnostics[0].reason,
            "expression_evaluation_error:member_missing",
        )
        self.assertEqual(
            ambiguous.diagnostics[0].reason, "lookup_ambiguous"
        )
        self.assertEqual(
            ambiguous.diagnostics[0].related_record_identities,
            ("node-source", "node-source-2"),
        )

    def test_malformed_schema_table_authority_is_controlled(self):
        result = self.execute_generated(referenced_tables=(
            {
                "table_id": "ability_targets",
                "primary_key": "target_id",
                "status": "active",
            },
            {
                "table_id": "ability_targets",
                "primary_key": "other_id",
                "status": "active",
            },
        ))
        self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(result.diagnostics[0].reason, "lookup_ambiguous")


class TestImmutableScalarBindingDefinition(unittest.TestCase):
    @staticmethod
    def lookup_context(target_records=None, lookup_records=None):
        helper = TestScalarLookupExecution()
        return helper.context(
            target_records
            or ({
                "item_id": "item-1",
                "reference_id": "alpha",
                "expected": "A",
            },),
            lookup_records
            or ({"reference_id": "alpha", "value": "A"},),
        )

    @staticmethod
    def execute_expression(expression, context):
        return execution.execute_definition_invariant_rule(
            make_definition_rule(expression), context
        )

    def test_literal_binding_is_structurally_supported_and_passes(self):
        result = execute(
            make_definition_rule("local = 1; local == 1"),
            ({"item_id": "item-1"},),
            fields=(),
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.PASS)
        self.assertEqual(
            (result.evaluated_record_count, result.violation_count), (1, 0)
        )

    def test_scalar_and_nested_lookup_bindings_pass(self):
        scalar = self.execute_expression(
            'local = lookup("references","reference_id",reference_id,'
            '"value"); local == expected',
            self.lookup_context(),
        )
        self.assertIs(scalar.outcome, execution.ValidationOutcome.PASS)

        nested_records = (
            {"reference_id": "start", "value": "finish"},
            {"reference_id": "finish", "value": "done"},
        )
        nested = self.execute_expression(
            'local = lookup("references","reference_id",'
            'lookup("references","reference_id",reference_id,"value"),'
            '"value"); local == "done"',
            self.lookup_context(
                ({"item_id": "item-1", "reference_id": "start"},),
                nested_records,
            ),
        )
        self.assertIs(nested.outcome, execution.ValidationOutcome.PASS)

    def test_source_field_collision_is_statically_fail_closed(self):
        result = execute(
            make_definition_rule("value = 1; value == 1"),
            ({"item_id": "item-1", "value": "unchanged"},),
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.UNSUPPORTED)
        self.assertEqual(
            result.diagnostics[0].reason,
            "binding_name_collides_with_source_field:value",
        )

    def test_binding_matcher_rejects_non_d2c_shapes(self):
        cases = {
            "binding_name_rebound": "x = 1; x = 2; x == 1",
            "binding_forward_reference": "x = y; y = 1; x == y",
            "binding_name_reserved": "current = 1; current == 1",
            "binding_rhs_node_not_supported:ListLiteral": "x = [1]; true",
            "binding_predicate_node_not_supported:MemberAccess": (
                "x = 1; record.value == x"
            ),
            "binding_after_boolean_statement": "true; x = 1; x == 1",
        }
        for reason, expression in cases.items():
            with self.subTest(reason=reason):
                ast = validation.parse_validation_expression(expression)
                self.assertEqual(
                    definition._binding_sequence_unsupported_reason(ast),
                    reason,
                )
                self.assertIsNotNone(definition._ast_unsupported_reason(ast))

        nested = validation.Sequence((
            validation.Binding(
                "outer",
                validation.Sequence((
                    validation.Binding(
                        "inner", validation.Literal("integer", 1)
                    ),
                    validation.Literal("boolean", True),
                )),
            ),
            validation.Literal("boolean", True),
        ))
        self.assertEqual(
            definition._binding_sequence_unsupported_reason(nested),
            "binding_rhs_node_not_supported:Sequence",
        )

    def test_binding_execution_is_record_order_deterministic(self):
        targets = (
            {"item_id": "item-2", "reference_id": "beta", "expected": "B"},
            {"item_id": "item-1", "reference_id": "alpha", "expected": "A"},
        )
        lookups = (
            {"reference_id": "alpha", "value": "A"},
            {"reference_id": "beta", "value": "B"},
        )
        expression = (
            'local = lookup("references","reference_id",reference_id,'
            '"value"); local == expected'
        )
        forward = self.execute_expression(
            expression, self.lookup_context(targets, lookups)
        )
        reverse = self.execute_expression(
            expression,
            self.lookup_context(
                tuple(reversed(targets)), tuple(reversed(lookups))
            ),
        )
        self.assertEqual(forward, reverse)
        self.assertIs(forward.outcome, execution.ValidationOutcome.PASS)


class TestUnsupportedShape(unittest.TestCase):
    def assert_unsupported(self, expression):
        result = execute(rule=make_definition_rule(expression))
        self.assertIs(result.outcome, execution.ValidationOutcome.UNSUPPORTED)
        self.assertEqual(result.evaluated_record_count, 0)
        self.assertEqual(result.violation_count, 0)
        self.assertEqual(
            result.diagnostics[0].code,
            execution.VALIDATION_EXECUTOR_UNSUPPORTED,
        )
        return result

    def test_lookup_with_dynamic_output_token_remains_unsupported(self):
        self.assert_unsupported(
            'lookup("items","item_id","value",value) == "alpha"'
        )

    def test_binding_remains_unsupported(self):
        self.assert_unsupported("copy = value")

    def test_sequence_with_non_when_statement_remains_unsupported(self):
        self.assert_unsupported('true; when(true,value != "beta")')

    def test_member_access_remains_unsupported(self):
        self.assert_unsupported('record.value == "alpha"')

    def test_static_rejection_precedes_table_or_record_access(self):
        result = execution.execute_definition_invariant_rule(
            make_definition_rule(
                'when(true,when(true,value == "alpha"))'
            ),
            make_context(include_target=False),
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.UNSUPPORTED)
        self.assertEqual(result.evaluated_record_count, 0)

    def test_lookup_in_guard_and_constraint_remains_unsupported(self):
        expressions = (
            'when(lookup("items","item_id","value",value) == "alpha", '
            'value == "alpha")',
            'when(true, lookup("items","item_id","value",value) == "alpha")',
        )
        for expression in expressions:
            with self.subTest(expression=expression):
                self.assert_unsupported(expression)

    def test_unknown_operator_remains_unsupported(self):
        self.assert_unsupported("when(true, count <= 1)")

    def test_language_schema_name_remains_unsupported(self):
        result = execute(
            make_definition_rule('when(enabled, language == "hu")'),
            ({"item_id": "item-1", "enabled": True, "language": "hu"},),
            fields=(
                schema_field("enabled", "boolean"),
                schema_field("language", "language"),
            ),
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.UNSUPPORTED)
        self.assertEqual(
            result.diagnostics[0].reason,
            "identifier_schema_type_not_supported:language",
        )

    def test_binding_and_member_access_inside_when_remain_unsupported(self):
        binding = validation.Call(
            "when",
            (
                validation.Literal("boolean", True),
                validation.Binding("copy", validation.Identifier("value")),
            ),
        )
        cases = (
            make_definition_rule("synthetic binding", ast=binding),
            make_definition_rule('when(true, record.value == "alpha")'),
        )
        for rule in cases:
            with self.subTest(expression=rule.condition_expression_source):
                result = execute(rule=rule)
                self.assertIs(
                    result.outcome, execution.ValidationOutcome.UNSUPPORTED
                )
                self.assertEqual(
                    (result.evaluated_record_count, result.violation_count),
                    (0, 0),
                )

    def test_non_when_call_remains_unsupported(self):
        self.assert_unsupported("count(value)")

    def test_domain_and_record_builtins_remain_unsupported(self):
        expressions = (
            'lookup_record("items","item_id",value) == null',
            'map(value,{"a":"b"}) == "b"',
        )
        for expression in expressions:
            with self.subTest(expression=expression):
                self.assert_unsupported(expression)

    def test_map_and_tbd_literals_remain_unsupported(self):
        for ast in (
            validation.MapLiteral((("a", "b"),)),
            validation.TbdLiteral(),
        ):
            with self.subTest(node=type(ast).__name__):
                result = execute(
                    rule=make_definition_rule("synthetic unsupported", ast=ast)
                )
                self.assertIs(
                    result.outcome, execution.ValidationOutcome.UNSUPPORTED
                )
                self.assertEqual(
                    (result.evaluated_record_count, result.violation_count),
                    (0, 0),
                )

    def test_wrong_when_arity_is_unsupported(self):
        for arguments in ((), (validation.Literal("boolean", True),)):
            ast = validation.Call("when", arguments)
            result = execute(
                rule=make_definition_rule("synthetic when arity", ast=ast)
            )
            self.assertIs(result.outcome, execution.ValidationOutcome.UNSUPPORTED)
            self.assertEqual(result.evaluated_record_count, 0)
            self.assertEqual(result.violation_count, 0)

    def test_non_definition_scope_stage_and_missing_expression_are_unsupported(self):
        base = make_definition_rule()
        cases = (
            replace(base, validation_kind_id="range"),
            replace(base, rule_scope_id="table"),
            replace(base, validation_stage_id="runtime"),
            replace(
                base,
                condition_expression_source=None,
                condition_ast=None,
                condition_ast_hash=None,
            ),
        )
        for rule in cases:
            with self.subTest(rule=rule):
                result = execution.execute_definition_invariant_rule(
                    rule, make_context()
                )
                self.assertIs(
                    result.outcome, execution.ValidationOutcome.UNSUPPORTED
                )
                self.assertEqual(result.evaluated_record_count, 0)
                self.assertEqual(result.violation_count, 0)


class TestRecordEvaluation(unittest.TestCase):
    def test_true_record_passes(self):
        result = execute(
            records=({"item_id": "item-1", "value": "alpha"},)
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.PASS)
        self.assertEqual((result.evaluated_record_count, result.violation_count), (1, 0))

    def test_false_record_has_one_deterministic_violation(self):
        result = execute(
            records=({"item_id": "item-1", "value": "beta"},)
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual((result.evaluated_record_count, result.violation_count), (1, 1))
        diagnostic = result.diagnostics[0]
        self.assertEqual(
            diagnostic.code,
            execution.VALIDATION_DEFINITION_INVARIANT_FAILED,
        )
        self.assertEqual(diagnostic.record_identity, "item-1")
        self.assertEqual(diagnostic.reason, "predicate_false")
        self.assertIn("registry:items", diagnostic.expected_contract)
        self.assertIn("ast=sha256:", diagnostic.expected_contract)

    def test_several_false_records_have_one_violation_each(self):
        records = tuple(
            {"item_id": f"item-{number}", "value": "beta"}
            for number in (3, 1, 2)
        )
        result = execute(records=records)
        self.assertEqual((result.evaluated_record_count, result.violation_count), (3, 3))
        self.assertEqual(
            tuple(item.record_identity for item in result.diagnostics),
            ("item-1", "item-2", "item-3"),
        )

    def test_empty_existing_table_passes(self):
        result = execute(records=())
        self.assertIs(result.outcome, execution.ValidationOutcome.PASS)
        self.assertEqual((result.evaluated_record_count, result.violation_count), (0, 0))

    def test_missing_target_table_fails_closed(self):
        result = execute(include_target=False)
        self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual((result.evaluated_record_count, result.violation_count), (0, 1))
        self.assertEqual(
            result.diagnostics[0].code,
            execution.VALIDATION_DEFINITION_TARGET_TABLE_MISSING,
        )
        self.assertEqual(result.diagnostics[0].reason, "target_table_missing")

    def test_missing_row_field_fails_closed(self):
        result = execute(records=({"item_id": "item-1"},))
        self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual((result.evaluated_record_count, result.violation_count), (1, 1))
        self.assertEqual(
            result.diagnostics[0].code,
            execution.VALIDATION_DEFINITION_TARGET_RECORD_INVALID,
        )
        self.assertEqual(
            result.diagnostics[0].reason, "target_field_missing:value"
        )

    def test_schema_invalid_runtime_types_fail_without_bool_int_coercion(self):
        rule = make_definition_rule("count >= 1")
        records = (
            {"item_id": "item-1", "count": True},
            {"item_id": "item-2", "count": 1.0},
        )
        result = execute(
            rule,
            records,
            fields=(schema_field("count", "integer"),),
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual((result.evaluated_record_count, result.violation_count), (2, 2))
        self.assertTrue(
            all(
                diagnostic.reason == "target_value_type_invalid:count"
                for diagnostic in result.diagnostics
            )
        )

    def test_non_boolean_expression_result_fails_closed(self):
        result = execute(
            make_definition_rule("value"),
            ({"item_id": "item-1", "value": "alpha"},),
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(
            result.diagnostics[0].reason, "expression_result_not_boolean"
        )

    def test_evaluator_type_error_is_a_record_failure(self):
        result = execute(
            make_definition_rule("enabled and value"),
            ({"item_id": "item-1", "enabled": True, "value": "alpha"},),
            fields=(
                schema_field("enabled", "boolean"),
                schema_field("value", "string"),
            ),
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(
            result.diagnostics[0].reason,
            "expression_evaluation_error:boolean_operand_required",
        )

    def test_invalid_identity_is_hashed_not_record_dumped(self):
        result = execute(records=({"value": "beta"},))
        diagnostic = result.diagnostics[0]
        self.assertEqual(diagnostic.reason, "target_identity_invalid")
        self.assertRegex(
            diagnostic.record_identity,
            r"\Acanonical-record-sha256:[0-9a-f]{64}\Z",
        )
        self.assertNotIn("value", diagnostic.record_identity)

    def test_nullable_schema_allows_explicit_null(self):
        result = execute(
            make_definition_rule("value == null"),
            ({"item_id": "item-1", "value": None},),
            fields=(schema_field(nullable=True),),
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.PASS)


class TestNamespaceResolution(unittest.TestCase):
    def test_same_table_id_uses_only_bound_source_namespace(self):
        context = make_context(
            registry_tables=namespace_tables(
                ({"item_id": "registry-1", "value": "registry"},)
            ),
            carddatabase_tables=namespace_tables(
                ({"item_id": "cdb-1", "value": "carddatabase"},)
            ),
        )
        result = execution.execute_definition_invariant_rule(
            make_definition_rule('value == "registry"'), context
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.PASS)
        self.assertEqual(result.evaluated_record_count, 1)

    def test_missing_component_binding_fails_closed(self):
        result = execution.execute_definition_invariant_rule(
            make_definition_rule(), make_context(bindings={})
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(result.diagnostics[0].reason, "source_namespace_missing")

    def test_wrong_binding_does_not_cross_search_other_namespace(self):
        context = make_context(
            bindings={"registry-component": "registry"},
            registry_tables=namespace_tables(include_target=False),
            carddatabase_tables=namespace_tables(
                ({"item_id": "cdb-1", "value": "alpha"},)
            ),
        )
        result = execution.execute_definition_invariant_rule(
            make_definition_rule(), context
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(result.diagnostics[0].reason, "target_table_missing")

    def test_identifier_schema_must_resolve_exactly_once(self):
        duplicate = schema_field(field_id="fld_items_value_duplicate")
        result = execute(
            fields=(schema_field(), duplicate),
            records=({"item_id": "item-1", "value": "alpha"},),
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(
            result.diagnostics[0].reason,
            "identifier_field_schema_unresolved:value",
        )


class TestTableCountDefinition(unittest.TestCase):
    @staticmethod
    def tables(candidates=(), *, include_candidates=True):
        tables = {
            "schema_tables": (
                {
                    "table_id": "items",
                    "primary_key": "item_id",
                    "status": "active",
                },
                {
                    "table_id": "candidates",
                    "primary_key": "candidate_id",
                    "status": "active",
                },
            ),
            "schema_fields": (
                table_field("items", "item_id"),
                table_field("items", "group"),
                table_field("candidates", "candidate_id"),
                table_field("candidates", "group"),
                table_field("candidates", "status"),
            ),
            "items": ({"item_id": "outer-1", "group": "alpha"},),
        }
        if include_candidates:
            tables["candidates"] = tuple(candidates)
        return tables

    @classmethod
    def context(
        cls,
        registry_candidates=(),
        *,
        registry_has_candidates=True,
        carddatabase_candidates=(),
    ):
        return execution.ValidationDataContext(
            namespaced_tables={
                "registry": cls.tables(
                    registry_candidates,
                    include_candidates=registry_has_candidates,
                ),
                "carddatabase": cls.tables(carddatabase_candidates),
            },
            component_namespaces={"registry-component": "registry"},
        )

    @staticmethod
    def rule(expression):
        return make_definition_rule(
            expression,
            target_field_id="fld_items_group",
        )

    def test_unqualified_and_qualified_tables_use_exact_namespaces(self):
        context = self.context(
            ({"candidate_id": "r-1", "group": "alpha", "status": "active"},),
            carddatabase_candidates=(
                {"candidate_id": "c-1", "group": "alpha", "status": "active"},
                {"candidate_id": "c-2", "group": "alpha", "status": "inactive"},
            ),
        )
        local = execution.execute_definition_invariant_rule(
            self.rule(
                'count("candidates",group == current.group) == 1'
            ),
            context,
        )
        qualified = execution.execute_definition_invariant_rule(
            self.rule(
                'count("carddatabase:candidates",'
                "group == current.group) == 2"
            ),
            context,
        )
        self.assertIs(local.outcome, execution.ValidationOutcome.PASS)
        self.assertIs(qualified.outcome, execution.ValidationOutcome.PASS)

    def test_unqualified_table_never_falls_back_to_other_namespace(self):
        context = self.context(
            registry_has_candidates=False,
            carddatabase_candidates=(
                {"candidate_id": "c-1", "group": "alpha", "status": "active"},
            ),
        )
        result = execution.execute_definition_invariant_rule(
            self.rule('count("candidates",true) == 1'), context
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(result.diagnostics[0].reason, "count_table_missing")

    def test_unknown_namespace_is_a_controlled_failure(self):
        result = execution.execute_definition_invariant_rule(
            self.rule('count("missing:candidates",true) == 0'),
            self.context(),
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(
            result.diagnostics[0].reason, "count_namespace_invalid"
        )

    def test_candidate_schema_and_values_fail_closed(self):
        for candidates, reason in (
            (
                ({"candidate_id": "c-1", "status": "active"},),
                "expression_evaluation_error:count_candidate_field_missing",
            ),
            (
                (
                    {
                        "candidate_id": "c-1",
                        "group": 1,
                        "status": "active",
                    },
                ),
                "expression_evaluation_error:count_candidate_field_value_invalid",
            ),
        ):
            with self.subTest(reason=reason):
                result = execution.execute_definition_invariant_rule(
                    self.rule(
                        'count("candidates",group == current.group) == 1'
                    ),
                    self.context(candidates),
                )
                self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
                self.assertEqual(result.diagnostics[0].reason, reason)

    def test_lifecycle_filter_is_explicit_and_order_is_deterministic(self):
        candidates = (
            {"candidate_id": "c-2", "group": "alpha", "status": "inactive"},
            {"candidate_id": "c-1", "group": "alpha", "status": "active"},
        )
        unfiltered_rule = self.rule('count("candidates",true) == 2')
        filtered_rule = self.rule(
            'count("candidates",status == "active") == 1'
        )
        forward = self.context(candidates)
        reverse = self.context(tuple(reversed(candidates)))
        for rule in (unfiltered_rule, filtered_rule):
            first = execution.execute_definition_invariant_rule(rule, forward)
            second = execution.execute_definition_invariant_rule(rule, reverse)
            self.assertEqual(first, second)
            self.assertIs(first.outcome, execution.ValidationOutcome.PASS)


class TestPureDomainPrimitiveDefinition(unittest.TestCase):
    @staticmethod
    def context(
        registry_values=(),
        *,
        target_records=None,
        include_group_schema=True,
        reverse=False,
        carddatabase_registry_values=(),
    ):
        registry_fields = [
            table_field("value_registry", "registry_value_id"),
        ]
        if include_group_schema:
            registry_fields.append(
                table_field("value_registry", "group_id")
            )
        registry = {
            "schema_tables": (
                {
                    "table_id": "value_registry",
                    "primary_key": "registry_value_id",
                    "status": "active",
                },
            ),
            "schema_fields": tuple(registry_fields),
            "value_registry": tuple(
                reversed(registry_values)
                if reverse
                else registry_values
            ),
        }
        targets = tuple(target_records or (
            {
                "item_id": "item-1",
                "value_id": "keyword_speed",
                "expected_group": "keyword",
            },
        ))
        carddatabase = {
            "schema_tables": (
                {
                    "table_id": "items",
                    "primary_key": "item_id",
                    "status": "active",
                },
                {
                    "table_id": "value_registry",
                    "primary_key": "registry_value_id",
                    "status": "active",
                },
            ),
            "schema_fields": (
                table_field("items", "item_id"),
                table_field("items", "value_id"),
                table_field(
                    "items", "expected_group", nullable=True
                ),
                table_field("value_registry", "registry_value_id"),
                table_field("value_registry", "group_id"),
            ),
            "items": tuple(reversed(targets)) if reverse else targets,
            "value_registry": tuple(carddatabase_registry_values),
        }
        return execution.ValidationDataContext(
            namespaced_tables={
                "registry": registry,
                "carddatabase": carddatabase,
            },
            component_namespaces={
                "carddatabase-component": "carddatabase"
            },
        )

    @staticmethod
    def rule(expression='group_of(value_id) == expected_group'):
        return make_definition_rule(
            expression,
            table_id="items",
            target_field_id="fld_items_value_id",
            component="carddatabase-component",
        )

    def test_normalization_executes_as_general_definition_primitive(self):
        result = execute(
            make_definition_rule(
                'normalized == normalize_search_name_hu(source)'
            ),
            ({
                "item_id": "item-1",
                "normalized": "árvíztűrő tükörfúrógép",
                "source": "  ÁRVÍZTŰRŐ\tTÜKÖRFÚRÓGÉP  ",
            },),
            fields=(
                schema_field("normalized"),
                schema_field("source"),
            ),
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.PASS)
        self.assertEqual((result.evaluated_record_count, result.violation_count), (1, 0))

    def test_group_of_resolves_any_group_and_unknowns_are_none(self):
        registry_values = (
            {
                "registry_value_id": "keyword_speed",
                "group_id": "keyword",
                "status": "inactive",
            },
            {
                "registry_value_id": "damage_kind_direct",
                "group_id": "damage_kind",
            },
        )
        targets = (
            {
                "item_id": "item-1",
                "value_id": "keyword_speed",
                "expected_group": "keyword",
            },
            {
                "item_id": "item-2",
                "value_id": "damage_kind_direct",
                "expected_group": "damage_kind",
            },
            {
                "item_id": "item-3",
                "value_id": "unknown_full_id",
                "expected_group": None,
            },
            {
                "item_id": "item-4",
                "value_id": "speed",
                "expected_group": None,
            },
            {
                "item_id": "item-5",
                "value_id": "gyorsaság",
                "expected_group": None,
            },
        )
        forward = execution.execute_definition_invariant_rule(
            self.rule(), self.context(registry_values, target_records=targets)
        )
        reverse = execution.execute_definition_invariant_rule(
            self.rule(),
            self.context(
                registry_values,
                target_records=targets,
                reverse=True,
            ),
        )
        self.assertEqual(forward, reverse)
        self.assertIs(forward.outcome, execution.ValidationOutcome.PASS)
        self.assertEqual(
            (forward.evaluated_record_count, forward.violation_count),
            (5, 0),
        )

    def test_duplicate_registry_id_is_deterministic_ambiguity(self):
        records = (
            {
                "registry_value_id": "keyword_speed",
                "group_id": "keyword",
            },
            {
                "registry_value_id": "keyword_speed",
                "group_id": "other_group",
            },
        )
        forward = execution.execute_definition_invariant_rule(
            self.rule(), self.context(records)
        )
        reverse = execution.execute_definition_invariant_rule(
            self.rule(), self.context(records, reverse=True)
        )
        self.assertEqual(forward, reverse)
        self.assertIs(forward.outcome, execution.ValidationOutcome.FAIL)
        diagnostic = forward.diagnostics[0]
        self.assertEqual(diagnostic.reason, "lookup_ambiguous")
        self.assertEqual(
            diagnostic.related_record_identities,
            tuple(sorted(diagnostic.related_record_identities)),
        )

    def test_malformed_registry_rows_and_missing_group_schema_fail_closed(self):
        cases = (
            (
                ({"registry_value_id": "keyword_speed"},),
                True,
                "lookup_output_value_invalid",
            ),
            (
                ({"registry_value_id": False, "group_id": "keyword"},),
                True,
                "lookup_record_identity_invalid",
            ),
            (
                ({
                    "registry_value_id": "keyword_speed",
                    "group_id": "keyword",
                },),
                False,
                "lookup_output_field_unresolved",
            ),
        )
        for records, include_schema, reason in cases:
            with self.subTest(reason=reason):
                result = execution.execute_definition_invariant_rule(
                    self.rule(),
                    self.context(
                        records, include_group_schema=include_schema
                    ),
                )
                self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
                self.assertEqual(result.diagnostics[0].reason, reason)

    def test_group_of_uses_explicit_registry_namespace_without_fallback(self):
        conflicting = ({
            "registry_value_id": "keyword_speed",
            "group_id": "wrong_namespace_group",
        },)
        target = ({
            "item_id": "item-1",
            "value_id": "keyword_speed",
            "expected_group": None,
        },)
        result = execution.execute_definition_invariant_rule(
            self.rule(),
            self.context(
                (),
                target_records=target,
                carddatabase_registry_values=conflicting,
            ),
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.PASS)
        self.assertEqual(result.violation_count, 0)


class TestDefinitionDeterminism(unittest.TestCase):
    def test_reversed_record_and_mapping_order_is_identical(self):
        forward_records = (
            {"item_id": "item-3", "value": "bad"},
            {"item_id": "item-1", "value": "alpha"},
            {"item_id": "item-2", "value": "bad"},
        )
        reverse_records = tuple(
            dict(reversed(tuple(record.items())))
            for record in reversed(forward_records)
        )
        forward = execute(records=forward_records)
        reverse = execute(records=reverse_records)
        self.assertEqual(forward, reverse)
        self.assertEqual(
            tuple(item.record_identity for item in forward.diagnostics),
            ("item-2", "item-3"),
        )


class TestCurrentDefinitionCorpus(unittest.TestCase):
    B1_RESULTS = {
        "cdb_val_abilities_template_mode_contract": ("abilities", 26),
        "cdb_val_card_keywords_parameter_exclusive": ("card_keywords", 399),
        "cdb_val_card_relations_not_self": ("card_relations", 0),
        "cdb_val_cards_holding_set_not_introduced": ("cards", 814),
        "cdb_val_choices_count_bounds": ("ability_choices", 0),
        "cdb_val_costs_amount_exclusive": ("ability_costs", 0),
        "cdb_val_costs_amount_nonnegative": ("ability_costs", 0),
        "cdb_val_durations_maximum_positive": ("ability_durations", 7),
        "cdb_val_targets_count_bounds": ("ability_targets", 17),
        "cdb_val_usage_limits_maximum_positive": ("ability_usage_limits", 0),
        "val_ability_template_nodes_output_table_allowed": (
            "ability_template_nodes",
            22,
        ),
        "val_modifier_types_duration_invariant": ("modifier_types", 3),
        "val_modifier_types_fixed_field_invariant": ("modifier_types", 3),
        "val_restriction_types_duration_invariant": ("restriction_types", 11),
    }
    B2_RESULTS = {
        "cdb_val_card_printings_reprint_not_self": (
            "card_printings", 814, 814, 0
        ),
        "cdb_val_choices_optional_minimum": ("ability_choices", 0, 0, 0),
        "cdb_val_expressions_aggregate_reference_required": (
            "ability_expressions", 9, 8, 1
        ),
        "cdb_val_expressions_field_reference_required": (
            "ability_expressions", 9, 6, 3
        ),
        "cdb_val_sets_holding_release_date_null": ("sets", 3, 2, 1),
        "cdb_val_targets_activity_state_object_contract": (
            "ability_targets", 17, 15, 2
        ),
        "cdb_val_targets_optional_minimum": (
            "ability_targets", 17, 15, 2
        ),
        "val_aliases_legacy_term_requires_audit": (
            "aliases", 95, 93, 2
        ),
        "val_modifier_types_additive_integer_type": (
            "modifier_types", 3, 0, 3
        ),
        "val_restriction_phase_completion_kind": (
            "restriction_types", 11, 9, 2
        ),
    }
    B3_RESULTS = {
        "cdb_val_abilities_parent_same_card": ("abilities", 26, 26, 0),
        "cdb_val_choice_options_condition_same_ability": (
            "ability_choice_options", 0, 0, 0
        ),
        "cdb_val_choice_options_effect_same_ability": (
            "ability_choice_options", 0, 0, 0
        ),
        "cdb_val_choice_options_target_same_ability": (
            "ability_choice_options", 0, 0, 0
        ),
        "cdb_val_conditions_expressions_same_ability": (
            "ability_conditions", 4, 0, 8
        ),
        "cdb_val_conditions_parent_same_ability": (
            "ability_conditions", 4, 4, 0
        ),
        "cdb_val_costs_condition_same_ability": ("ability_costs", 0, 0, 0),
        "cdb_val_costs_expression_same_ability": ("ability_costs", 0, 0, 0),
        "cdb_val_costs_target_same_ability": ("ability_costs", 0, 0, 0),
        "cdb_val_durations_condition_same_ability": (
            "ability_durations", 7, 7, 0
        ),
        "cdb_val_durations_direct_graph_parent_contract": (
            "ability_durations", 7, 0, 35
        ),
        "cdb_val_effect_parameter_expression_same_ability": (
            "ability_effect_parameters", 14, 14, 0
        ),
        "cdb_val_effect_parameters_direct_graph_parent_contract": (
            "ability_effect_parameters", 14, 0, 70
        ),
        "cdb_val_effect_tags_effect_same_ability": ("effect_tags", 0, 0, 0),
        "cdb_val_effects_condition_same_ability": (
            "ability_effects", 21, 20, 1
        ),
        "cdb_val_effects_expression_same_ability": (
            "ability_effects", 21, 21, 0
        ),
        "cdb_val_effects_parent_same_ability": (
            "ability_effects", 21, 21, 0
        ),
        "cdb_val_effects_target_same_ability": (
            "ability_effects", 21, 0, 21
        ),
        "cdb_val_expressions_parent_same_ability": (
            "ability_expressions", 9, 8, 1
        ),
        "cdb_val_expressions_target_binding_required_for_target_results": (
            "ability_expressions", 9, 8, 1
        ),
        "cdb_val_expressions_target_reference_matches_primitive": (
            "ability_expressions", 9, 8, 2
        ),
        "cdb_val_expressions_target_same_ability": (
            "ability_expressions", 9, 8, 1
        ),
        "cdb_val_targets_filter_same_ability": ("ability_targets", 17, 14, 3),
        "cdb_val_template_arguments_expression_same_ability": (
            "ability_template_arguments", 13, 13, 0
        ),
        "cdb_val_template_arguments_template_instance_only": (
            "ability_template_arguments", 13, 0, 13
        ),
        "cdb_val_triggers_direct_graph_ability_mode": (
            "ability_triggers", 5, 0, 15
        ),
        "cdb_val_triggers_filter_same_ability": (
            "ability_triggers", 5, 5, 0
        ),
    }
    D1B_RESULTS = {
        "cdb_val_all_matching_target_contract": (
            "ability_targets", 17, 14, 3, 0
        ),
        "cdb_val_card_keywords_harmonization_value": (
            "card_keywords", 399, 371, 28, 0
        ),
        "cdb_val_card_keywords_resonance_value": (
            "card_keywords", 399, 355, 44, 0
        ),
        "cdb_val_card_keywords_unparameterized_values": (
            "card_keywords", 399, 72, 327, 0
        ),
        "cdb_val_choose_cards_zero_or_more_target_contract": (
            "ability_targets", 17, 15, 2, 0
        ),
        "cdb_val_choose_one_card_target_contract": (
            "ability_targets", 17, 8, 9, 0
        ),
        "cdb_val_effect_parameter_deal_damage_amount_positive": (
            "ability_effect_parameters", 14, 8, 6, 0
        ),
        "cdb_val_effect_parameter_heal_entity_amount_positive": (
            "ability_effect_parameters", 14, 13, 1, 0
        ),
        "cdb_val_printings_holding_status_alignment": (
            "card_printings", 814, 812, 2, 0
        ),
        "cdb_val_self_entered_play_trigger_contract": (
            "ability_triggers", 5, 0, 5, 0
        ),
        "cdb_val_target_reference_ability_source_card_contract": (
            "ability_targets", 17, 15, 2, 0
        ),
        "cdb_val_template_buff_atk_bonus_positive": (
            "ability_template_arguments", 13, 11, 2, 0
        ),
        "cdb_val_template_buff_max_hp_bonus_positive": (
            "ability_template_arguments", 13, 11, 2, 0
        ),
        "cdb_val_template_damage_all_horizont_amount_positive": (
            "ability_template_arguments", 13, 10, 3, 0
        ),
        "cdb_val_template_draw_cards_amount_positive": (
            "ability_template_arguments", 13, 12, 1, 0
        ),
        "cdb_val_template_echo_damage_amount_positive": (
            "ability_template_arguments", 13, 11, 2, 0
        ),
        "cdb_val_template_return_max_magnitude_positive": (
            "ability_template_arguments", 13, 10, 3, 0
        ),
        "val_reference_target_candidate_scope": (
            "reference_types", 21, 20, 1, 0
        ),
        "val_restriction_entity_cannot_initiate_attack_contract": (
            "restriction_types", 11, 10, 1, 0
        ),
        "val_rule_registry_runtime_module_required": (
            "rule_registry", 23, 0, 23, 0
        ),
        "val_target_all_matching_cards_contract": (
            "target_primitives", 9, 8, 1, 0
        ),
        "val_target_reference_ability_source_card_contract": (
            "target_primitives", 9, 8, 1, 0
        ),
    }
    D1C_RESULTS = {
        "val_migration_map_manual_semantic_invariant": (
            "migration_map", 85, 70, 15, 0
        ),
        "val_migration_map_auto_mapping_resolved": (
            "migration_map", 85, 17, 68, 0
        ),
        "val_migration_map_parameterized_alias_invariant": (
            "migration_map", 85, 83, 2, 0
        ),
    }
    D1C_VIOLATION_IDENTITIES = {
        "val_migration_map_auto_mapping_resolved": (),
        "val_migration_map_manual_semantic_invariant": (),
        "val_migration_map_parameterized_alias_invariant": (),
    }
    D1D_RESULTS = {
        "cdb_val_cards_type_stat_invariant": ("cards", 814, 2),
        "cdb_val_export_manifest_enabled_fields": (
            "export_manifest", 30, 2
        ),
        "val_aliases_casefold_case_sensitive_consistency": (
            "aliases", 95, 2
        ),
        "val_export_manifest_enabled_fields": (
            "export_manifest", 30, 2
        ),
        "val_source_registry_authority_kind_compatibility": (
            "source_registry", 21, 4
        ),
    }
    D1E_RESULTS = {
        "cdb_val_printings_legacy_normalization": (
            "card_printings", 814, 0, 814, 0
        ),
    }
    D2B_RESULTS = {
        "cdb_val_choice_options_output_required": (
            "ability_choice_options", 0, None, None, 0
        ),
        "cdb_val_effect_parameter_value_exclusive": (
            "ability_effect_parameters", 14, None, None, 0
        ),
        "cdb_val_effects_value_representation_exclusive": (
            "ability_effects", 21, None, None, 0
        ),
        "cdb_val_expressions_literal_exclusive": (
            "ability_expressions", 9, None, None, 0
        ),
        "cdb_val_expressions_literal_type_required": (
            "ability_expressions", 9, 5, 4, 0
        ),
        "cdb_val_template_arguments_value_exclusive": (
            "ability_template_arguments", 13, None, None, 0
        ),
    }
    D2C_RESULTS = {
        "cdb_val_effect_parameter_collection_index": (
            "ability_effect_parameters", 14
        ),
        "cdb_val_effect_parameter_contract_match": (
            "ability_effect_parameters", 14
        ),
    }
    D2D_RESULTS = {
        "cdb_val_costs_component_definition": (
            "ability_costs", 0, None, None, 0, 0
        ),
        "cdb_val_deck_entries_card_contract": (
            "deck_entries", 32, 0, 32, 64, 238
        ),
        "cdb_val_durations_policy_definition": (
            "ability_durations", 7, None, None, 7, 21
        ),
        "cdb_val_effect_modifier_value_contract": (
            "ability_effects", 21, 18, 3, 3, 3
        ),
        "cdb_val_effects_action_definition": (
            "ability_effects", 21, None, None, 21, 231
        ),
        "cdb_val_effects_direct_graph_ability_mode": (
            "ability_effects", 21, 0, 21, 21, 42
        ),
        "cdb_val_targets_direct_graph_ability_mode": (
            "ability_targets", 17, 0, 17, 17, 34
        ),
        "cdb_val_template_arguments_collection_index": (
            "ability_template_arguments", 13, None, None, 13, 26
        ),
        "cdb_val_template_arguments_contract_match": (
            "ability_template_arguments", 13, None, None, 39, 39
        ),
        "cdb_val_usage_limits_policy_definition": (
            "ability_usage_limits", 0, None, None, 0, 0
        ),
        "val_ability_template_bindings_parameter_schema": (
            "ability_template_bindings", 125, 119, 6, 18, 18
        ),
        "val_ability_template_bindings_target_field_matches_node": (
            "ability_template_bindings", 125, None, None, 250, 250
        ),
        "val_ability_templates_parameter_schema_kind": (
            "ability_templates", 5, None, None, 5, 10
        ),
    }
    D2D_DOMAINS = {
        "cdb_val_costs_component_definition": Counter(),
        "cdb_val_deck_entries_card_contract": Counter({
            ("carddatabase", "cards", "card_id"): 32,
            ("carddatabase", "decks", "deck_id"): 32,
        }),
        "cdb_val_durations_policy_definition": Counter({
            ("registry", "duration_policies", "duration_policy_id"): 7,
        }),
        "cdb_val_effect_modifier_value_contract": Counter({
            ("registry", "modifier_types", "modifier_type_id"): 3,
        }),
        "cdb_val_effects_action_definition": Counter({
            ("registry", "effect_action_types", "effect_action_type_id"): 21,
        }),
        "cdb_val_effects_direct_graph_ability_mode": Counter({
            ("carddatabase", "abilities", "ability_id"): 21,
        }),
        "cdb_val_targets_direct_graph_ability_mode": Counter({
            ("carddatabase", "abilities", "ability_id"): 17,
        }),
        "cdb_val_template_arguments_collection_index": Counter({
            ("registry", "contract_fields", "contract_field_id"): 13,
        }),
        "cdb_val_template_arguments_contract_match": Counter({
            ("carddatabase", "abilities", "ability_id"): 13,
            ("registry", "ability_templates", "ability_template_id"): 13,
            ("registry", "contract_fields", "contract_field_id"): 13,
        }),
        "cdb_val_usage_limits_policy_definition": Counter(),
        "val_ability_template_bindings_parameter_schema": Counter({
            ("registry", "ability_template_nodes", "template_node_id"): 6,
            ("registry", "ability_templates", "ability_template_id"): 6,
            ("registry", "contract_fields", "contract_field_id"): 6,
        }),
        "val_ability_template_bindings_target_field_matches_node": Counter({
            ("registry", "ability_template_nodes", "template_node_id"): 125,
            ("carddatabase", "schema_fields", "field_id"): 125,
        }),
        "val_ability_templates_parameter_schema_kind": Counter({
            ("registry", "contract_schemas", "contract_schema_id"): 5,
        }),
    }
    D2E_RESULTS = {
        "cdb_val_abilities_template_compatibility": (
            "abilities", 26, 15, 11
        ),
    }
    PRE_D2E_UNSUPPORTED = {
        "cdb_val_abilities_template_compatibility",
        "cdb_val_card_localization_search_name_normalized",
        "cdb_val_decks_clan_realm_contract",
        "cdb_val_effect_parameter_value_contract",
        "cdb_val_effects_duration_supported",
        "cdb_val_effects_modifier_definition",
        "cdb_val_effects_restriction_definition",
        "cdb_val_keyword_grant_value_contract",
        "cdb_val_template_arguments_value_contract",
        "val_ability_template_bindings_generated_node",
        "val_ability_template_bindings_shape",
        "val_ability_template_bindings_value_type",
        "val_migration_map_alias_resolution_invariant",
    }
    D2F_RESULTS = {
        "cdb_val_decks_clan_realm_contract": ("decks", 2, 0, 2, 4),
        "cdb_val_effects_duration_supported": (
            "ability_effects", 21, 14, 7, 21
        ),
        "cdb_val_effects_modifier_definition": (
            "ability_effects", 21, 18, 3, 3
        ),
        "cdb_val_effects_restriction_definition": (
            "ability_effects", 21, 20, 1, 1
        ),
    }
    PRE_D2F_UNSUPPORTED = PRE_D2E_UNSUPPORTED - set(D2E_RESULTS)
    D2G_RESULTS = {
        "cdb_val_card_localization_search_name_normalized": (
            "card_localization", 814
        ),
        "cdb_val_effect_parameter_value_contract": (
            "ability_effect_parameters", 14
        ),
        "cdb_val_keyword_grant_value_contract": (
            "ability_effects", 21
        ),
    }
    PRE_D2G_UNSUPPORTED = PRE_D2F_UNSUPPORTED - set(D2F_RESULTS)
    D2H_RESULTS = {
        "val_migration_map_alias_resolution_invariant": (
            "migration_map", 85, 67, 18, 0
        ),
    }
    PRE_D2H_UNSUPPORTED = PRE_D2G_UNSUPPORTED - set(D2G_RESULTS)
    D2I_RESULTS = {
        "val_ability_template_bindings_shape": (
            "ability_template_bindings", 125
        ),
    }
    PRE_D2I_UNSUPPORTED = PRE_D2H_UNSUPPORTED - set(D2H_RESULTS)
    D2J_RESULTS = {
        "cdb_val_template_arguments_value_contract": (
            "ability_template_arguments", 13
        ),
        "val_ability_template_bindings_value_type": (
            "ability_template_bindings", 125
        ),
    }
    PRE_D2J_UNSUPPORTED = PRE_D2I_UNSUPPORTED - set(D2I_RESULTS)
    D2K_RESULTS = {
        "val_ability_template_bindings_generated_node": (
            "ability_template_bindings", 125
        ),
    }
    PRE_D2K_UNSUPPORTED = PRE_D2J_UNSUPPORTED - set(D2J_RESULTS)

    @property
    def supported_results(self):
        return {
            **self.B1_RESULTS,
            **{
                rule_id: (table_id, record_count)
                for rule_id, (
                    table_id, record_count, _guard_false, _guard_true
                ) in self.B2_RESULTS.items()
            },
            **{
                rule_id: (table_id, record_count)
                for rule_id, (
                    table_id, record_count, _guard_false, _lookup_calls
                ) in self.B3_RESULTS.items()
            },
            **{
                rule_id: (table_id, record_count)
                for rule_id, (
                    table_id,
                    record_count,
                    _guard_false,
                    _guard_true,
                    _violations,
                ) in self.D1B_RESULTS.items()
            },
            **{
                rule_id: (table_id, record_count)
                for rule_id, (
                    table_id,
                    record_count,
                    _guard_false,
                    _guard_true,
                    _violations,
                ) in self.D1C_RESULTS.items()
            },
            **{
                rule_id: (table_id, record_count)
                for rule_id, (
                    table_id, record_count, _statement_count
                ) in self.D1D_RESULTS.items()
            },
            **{
                rule_id: (table_id, record_count)
                for rule_id, (
                    table_id,
                    record_count,
                    _guard_false,
                    _guard_true,
                    _violations,
                ) in self.D1E_RESULTS.items()
            },
            **{
                rule_id: (table_id, record_count)
                for rule_id, (
                    table_id,
                    record_count,
                    _guard_false,
                    _guard_true,
                    _violations,
                ) in self.D2B_RESULTS.items()
            },
            **self.D2C_RESULTS,
            **{
                rule_id: (table_id, record_count)
                for rule_id, (
                    table_id,
                    record_count,
                    _guard_false,
                    _guard_true,
                    _lookup_calls,
                    _member_calls,
                ) in self.D2D_RESULTS.items()
            },
            **{
                rule_id: (table_id, record_count)
                for rule_id, (
                    table_id,
                    record_count,
                    _guard_false,
                    _guard_true,
                ) in self.D2E_RESULTS.items()
            },
            **{
                rule_id: (table_id, record_count)
                for rule_id, (
                    table_id,
                    record_count,
                    _guard_false,
                    _guard_true,
                    _count_calls,
                ) in self.D2F_RESULTS.items()
            },
            **self.D2G_RESULTS,
            **{
                rule_id: (table_id, record_count)
                for rule_id, (
                    table_id,
                    record_count,
                    _guard_false,
                    _guard_true,
                    _violations,
                ) in self.D2H_RESULTS.items()
            },
            **self.D2I_RESULTS,
            **self.D2J_RESULTS,
            **self.D2K_RESULTS,
        }

    def test_current_family_is_exactly_116_supported_and_none_unsupported(self):
        before = {
            path: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in execution_tests.WORKBOOKS
        }
        catalog, context = execution_tests.current_corpus_catalog_and_context()
        definitions = tuple(
            rule
            for rule in catalog.by_stage("pre_export")
            if rule.validation_kind_id == "definition_invariant"
        )
        results = tuple(
            execution.execute_definition_invariant_rule(rule, context)
            for rule in definitions
        )
        supported = tuple(
            (rule, result)
            for rule, result in zip(definitions, results)
            if result.outcome is not execution.ValidationOutcome.UNSUPPORTED
        )

        self.assertEqual(len(definitions), 116)
        self.assertEqual(len(supported), 116)
        self.assertEqual(
            Counter(result.outcome for result in results),
            {
                execution.ValidationOutcome.PASS: 116,
            },
        )
        self.assertEqual(
            {rule.rule_id for rule, _ in supported},
            set(self.supported_results),
        )
        compound_results = {
            **self.D1B_RESULTS,
            **self.D1C_RESULTS,
            **self.D1E_RESULTS,
            **self.D2B_RESULTS,
            **self.D2H_RESULTS,
        }
        for rule, result in supported:
            with self.subTest(rule=rule.rule_id):
                table_id, record_count = self.supported_results[rule.rule_id]
                expected_violations = compound_results.get(
                    rule.rule_id, (None, None, None, None, 0)
                )[4]
                self.assertEqual(rule.target_table_id, table_id)
                self.assertIs(
                    result.outcome,
                    execution.ValidationOutcome.FAIL
                    if expected_violations
                    else execution.ValidationOutcome.PASS,
                )
                self.assertEqual(result.evaluated_record_count, record_count)
                self.assertEqual(result.violation_count, expected_violations)

        after = {
            path: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in execution_tests.WORKBOOKS
        }
        self.assertEqual(before, after)

    def test_b1_14_rule_regression_remains_pass(self):
        catalog, context = execution_tests.current_corpus_catalog_and_context()
        for rule_id in sorted(self.B1_RESULTS):
            result = execution.execute_definition_invariant_rule(
                catalog.get(rule_id), context
            )
            with self.subTest(rule=rule_id):
                self.assertIs(result.outcome, execution.ValidationOutcome.PASS)
                self.assertEqual(result.violation_count, 0)

    def test_all_identifier_contracts_resolve_uniquely_in_source_namespace(self):
        catalog, context = execution_tests.current_corpus_catalog_and_context()
        resolved = []
        for rule_id in sorted(self.supported_results):
            rule = catalog.get(rule_id)
            namespace = context.namespace_for_component(rule.component_identity)
            schema = context.table("schema_fields", namespace=namespace)
            identifiers = definition._outer_identifier_names(
                rule.condition_ast
            )
            for identifier in identifiers:
                matches = tuple(
                    record
                    for record in schema
                    if record.get("table_id") == rule.target_table_id
                    and record.get("field_name") == identifier
                    and record.get("status") == "active"
                )
                self.assertEqual(len(matches), 1, (rule_id, identifier))
                resolved.append((rule_id, identifier))
        self.assertEqual(len(resolved), 386)

    def test_d1b_shape_inventory_and_current_results_are_exact(self):
        catalog, context = execution_tests.current_corpus_catalog_and_context()
        previous = set(self.B1_RESULTS) | set(self.B2_RESULTS) | set(self.B3_RESULTS)
        definitions = tuple(
            rule
            for rule in catalog.by_stage("pre_export")
            if rule.validation_kind_id == "definition_invariant"
        )
        executed = {
            rule.rule_id: execution.execute_definition_invariant_rule(
                rule, context
            )
            for rule in definitions
        }
        newly_supported = {
            rule_id
            for rule_id, result in executed.items()
            if result.outcome is not execution.ValidationOutcome.UNSUPPORTED
            and rule_id not in previous
            and rule_id not in self.D1C_RESULTS
            and rule_id not in self.D1D_RESULTS
            and rule_id not in self.D1E_RESULTS
            and rule_id not in self.D2B_RESULTS
            and rule_id not in self.D2C_RESULTS
            and rule_id not in self.D2D_RESULTS
            and rule_id not in self.D2E_RESULTS
            and rule_id not in self.D2F_RESULTS
            and rule_id not in self.D2G_RESULTS
            and rule_id not in self.D2H_RESULTS
            and rule_id not in self.D2I_RESULTS
            and rule_id not in self.D2J_RESULTS
            and rule_id not in self.D2K_RESULTS
        }
        self.assertEqual(newly_supported, set(self.D1B_RESULTS))

        total_violations = 0
        for rule_id, expected in sorted(self.D1B_RESULTS.items()):
            rule = catalog.get(rule_id)
            root = rule.condition_ast
            self.assertIsInstance(root, validation.Call)
            self.assertEqual((root.function, len(root.arguments)), ("when", 2))
            self.assertEqual(
                {
                    node.function
                    for node in self._walk(root)
                    if isinstance(node, validation.Call)
                },
                {"when"},
            )
            self.assertTrue(
                all(
                    node.operator in {"==", "!=", ">=", "and", "or", "in"}
                    for node in self._walk(root)
                    if isinstance(node, validation.BinaryOperation)
                )
            )

            namespace = context.namespace_for_component(rule.component_identity)
            schema = context.table("schema_fields", namespace=namespace)
            for identifier in rule.free_identifiers:
                matches = tuple(
                    field
                    for field in schema
                    if field.get("table_id") == rule.target_table_id
                    and field.get("field_name") == identifier
                    and field.get("status") == "active"
                )
                self.assertEqual(len(matches), 1, (rule_id, identifier))
                self.assertIsNone(definition._field_schema_reason(matches[0]))

            records = context.table(rule.target_table_id, namespace=namespace)
            guard = root.arguments[0]
            guard_results = tuple(
                definition.evaluate_validation_expression(
                    guard,
                    {name: record[name] for name in rule.free_identifiers},
                )
                for record in records
            )
            table_id, record_count, guard_false, guard_true, violations = expected
            result = executed[rule_id]
            with self.subTest(rule=rule_id):
                self.assertEqual(rule.target_table_id, table_id)
                self.assertEqual(len(records), record_count)
                self.assertEqual(guard_results.count(False), guard_false)
                self.assertEqual(guard_results.count(True), guard_true)
                self.assertEqual(result.evaluated_record_count, record_count)
                self.assertEqual(result.violation_count, violations)
                self.assertIs(
                    result.outcome,
                    execution.ValidationOutcome.FAIL
                    if violations
                    else execution.ValidationOutcome.PASS,
                )
            total_violations += violations
        self.assertEqual(total_violations, 0)

    def test_d1c_shape_inventory_and_current_results_are_exact(self):
        catalog, context = execution_tests.current_corpus_catalog_and_context()
        reverse_catalog, reverse_context = (
            execution_tests.current_corpus_catalog_and_context(reverse=True)
        )
        previous = set(self.supported_results) - set(self.D1C_RESULTS)
        definitions = tuple(
            rule
            for rule in catalog.by_stage("pre_export")
            if rule.validation_kind_id == "definition_invariant"
        )
        executed = {
            rule.rule_id: execution.execute_definition_invariant_rule(
                rule, context
            )
            for rule in definitions
        }
        newly_supported = {
            rule_id
            for rule_id, result in executed.items()
            if result.outcome is not execution.ValidationOutcome.UNSUPPORTED
            and rule_id not in previous
        }
        self.assertEqual(newly_supported, set(self.D1C_RESULTS))

        total_violations = 0
        for rule_id, expected in sorted(self.D1C_RESULTS.items()):
            rule = catalog.get(rule_id)
            root = rule.condition_ast
            self.assertIsInstance(root, validation.Call)
            self.assertEqual((root.function, len(root.arguments)), ("when", 2))
            operators = {
                node.operator
                for node in self._walk(root)
                if isinstance(node, validation.BinaryOperation)
            }
            self.assertIn("not in", operators)
            self.assertLessEqual(
                operators, {"==", "!=", ">=", "and", "or", "in", "not in"}
            )

            namespace = context.namespace_for_component(rule.component_identity)
            schema = context.table("schema_fields", namespace=namespace)
            for identifier in rule.free_identifiers:
                matches = tuple(
                    field
                    for field in schema
                    if field.get("table_id") == rule.target_table_id
                    and field.get("field_name") == identifier
                    and field.get("status") == "active"
                )
                self.assertEqual(len(matches), 1, (rule_id, identifier))
                self.assertIsNone(definition._field_schema_reason(matches[0]))

            records = context.table(rule.target_table_id, namespace=namespace)
            guard = root.arguments[0]
            guard_results = tuple(
                definition.evaluate_validation_expression(
                    guard,
                    {name: record[name] for name in rule.free_identifiers},
                )
                for record in records
            )
            table_id, record_count, guard_false, guard_true, violations = expected
            result = executed[rule_id]
            reverse_result = execution.execute_definition_invariant_rule(
                reverse_catalog.get(rule_id), reverse_context
            )
            with self.subTest(rule=rule_id):
                self.assertEqual(rule.target_table_id, table_id)
                self.assertEqual(len(records), record_count)
                self.assertEqual(guard_results.count(False), guard_false)
                self.assertEqual(guard_results.count(True), guard_true)
                self.assertEqual(result, reverse_result)
                self.assertIs(
                    result.outcome,
                    execution.ValidationOutcome.FAIL
                    if violations
                    else execution.ValidationOutcome.PASS,
                )
                self.assertEqual(result.evaluated_record_count, record_count)
                self.assertEqual(result.violation_count, violations)
                self.assertEqual(
                    tuple(
                        item.record_identity for item in result.diagnostics
                    ),
                    self.D1C_VIOLATION_IDENTITIES[rule_id],
                )
                if violations:
                    self.assertEqual(
                        tuple(
                            (item.code, item.reason, item.record_identity)
                            for item in result.diagnostics
                        ),
                        ((
                            execution.VALIDATION_DEFINITION_TARGET_RECORD_INVALID,
                            "target_value_type_invalid:target_value",
                            "mig_cdb_printing_is_default",
                        ),),
                    )
                else:
                    self.assertEqual(result.diagnostics, ())
            total_violations += violations
        self.assertEqual(total_violations, 0)

    def test_d1d_shape_inventory_and_current_results_are_exact(self):
        catalog, context = execution_tests.current_corpus_catalog_and_context()
        reverse_catalog, reverse_context = (
            execution_tests.current_corpus_catalog_and_context(reverse=True)
        )
        previous = set(self.supported_results) - set(self.D1D_RESULTS)
        definitions = tuple(
            rule
            for rule in catalog.by_stage("pre_export")
            if rule.validation_kind_id == "definition_invariant"
        )
        executed = {
            rule.rule_id: execution.execute_definition_invariant_rule(
                rule, context
            )
            for rule in definitions
        }
        newly_supported = {
            rule_id
            for rule_id, result in executed.items()
            if result.outcome is not execution.ValidationOutcome.UNSUPPORTED
            and rule_id not in previous
        }
        self.assertEqual(newly_supported, set(self.D1D_RESULTS))

        total_records = 0
        total_statements = 0
        for rule_id, expected in sorted(self.D1D_RESULTS.items()):
            rule = catalog.get(rule_id)
            root = rule.condition_ast
            self.assertIsInstance(root, validation.Sequence)
            self.assertTrue(root.statements)
            self.assertTrue(
                all(
                    isinstance(statement, validation.Call)
                    and statement.function == "when"
                    and len(statement.arguments) == 2
                    for statement in root.statements
                )
            )
            self.assertFalse(definition._lookup_nodes(root))
            self.assertIsNone(definition._ast_unsupported_reason(root))

            namespace = context.namespace_for_component(rule.component_identity)
            schema = context.table("schema_fields", namespace=namespace)
            for identifier in rule.free_identifiers:
                matches = tuple(
                    field
                    for field in schema
                    if field.get("table_id") == rule.target_table_id
                    and field.get("field_name") == identifier
                    and field.get("status") == "active"
                )
                self.assertEqual(len(matches), 1, (rule_id, identifier))
                self.assertIsNone(definition._field_schema_reason(matches[0]))

            table_id, record_count, statement_count = expected
            result = executed[rule_id]
            reverse_result = execution.execute_definition_invariant_rule(
                reverse_catalog.get(rule_id), reverse_context
            )
            with self.subTest(rule=rule_id):
                self.assertEqual(rule.target_table_id, table_id)
                self.assertEqual(len(root.statements), statement_count)
                self.assertEqual(result, reverse_result)
                self.assertIs(result.outcome, execution.ValidationOutcome.PASS)
                self.assertEqual(result.evaluated_record_count, record_count)
                self.assertEqual(result.violation_count, 0)
                self.assertEqual(result.diagnostics, ())
            total_records += record_count
            total_statements += statement_count
        self.assertEqual(total_records, 990)
        self.assertEqual(total_statements, 12)

    def test_d1e_shape_schema_delta_and_current_result_are_exact(self):
        catalog, context = execution_tests.current_corpus_catalog_and_context()
        reverse_catalog, reverse_context = (
            execution_tests.current_corpus_catalog_and_context(reverse=True)
        )
        definitions = tuple(
            rule
            for rule in catalog.by_stage("pre_export")
            if rule.validation_kind_id == "definition_invariant"
        )
        executed = {
            rule.rule_id: execution.execute_definition_invariant_rule(
                rule, context
            )
            for rule in definitions
        }
        previous = set(self.supported_results) - set(self.D1E_RESULTS)
        newly_supported = {
            rule_id
            for rule_id, result in executed.items()
            if result.outcome is not execution.ValidationOutcome.UNSUPPORTED
            and rule_id not in previous
        }
        self.assertEqual(newly_supported, set(self.D1E_RESULTS))

        rule_id = next(iter(self.D1E_RESULTS))
        rule = catalog.get(rule_id)
        root = rule.condition_ast
        self.assertIsInstance(root, validation.Call)
        self.assertEqual((root.function, len(root.arguments)), ("when", 2))
        nodes = tuple(self._walk(root))
        self.assertFalse(
            any(
                isinstance(
                    node,
                    (
                        validation.Sequence,
                        validation.Binding,
                        validation.MemberAccess,
                        validation.MapLiteral,
                        validation.TbdLiteral,
                    ),
                )
                for node in nodes
            )
        )
        self.assertEqual(
            {
                node.function
                for node in nodes
                if isinstance(node, validation.Call)
            },
            {"when"},
        )
        self.assertEqual(
            {
                node.operator
                for node in nodes
                if isinstance(node, validation.BinaryOperation)
            },
            {"==", "and"},
        )
        self.assertFalse(definition._lookup_nodes(root))
        self.assertIsNone(definition._ast_unsupported_reason(root))

        namespace = context.namespace_for_component(rule.component_identity)
        schema = context.table("schema_fields", namespace=namespace)
        language_fields = tuple(
            field
            for field in schema
            if field.get("table_id") == rule.target_table_id
            and field.get("field_name") == "language"
            and field.get("status") == "active"
        )
        self.assertEqual(len(language_fields), 1)
        self.assertEqual(language_fields[0].get("data_type"), "language_tag")
        self.assertIsNone(definition._field_schema_reason(language_fields[0]))
        active_schema_types = Counter(
            field.get("data_type")
            for source_namespace in ("registry", "carddatabase")
            for field in context.table(
                "schema_fields", namespace=source_namespace
            )
            if field.get("status") == "active"
        )
        self.assertEqual(active_schema_types["language_tag"], 4)
        self.assertEqual(active_schema_types["language"], 0)

        records = context.table(rule.target_table_id, namespace=namespace)
        guard_results = tuple(
            definition.evaluate_validation_expression(
                root.arguments[0],
                {name: record[name] for name in rule.free_identifiers},
            )
            for record in records
        )
        table_id, record_count, guard_false, guard_true, violations = (
            self.D1E_RESULTS[rule_id]
        )
        result = executed[rule_id]
        reverse_result = execution.execute_definition_invariant_rule(
            reverse_catalog.get(rule_id), reverse_context
        )
        self.assertEqual(rule.target_table_id, table_id)
        self.assertEqual(len(records), record_count)
        self.assertEqual(guard_results.count(False), guard_false)
        self.assertEqual(guard_results.count(True), guard_true)
        self.assertEqual(result, reverse_result)
        self.assertIs(result.outcome, execution.ValidationOutcome.PASS)
        self.assertEqual(
            (result.evaluated_record_count, result.violation_count),
            (record_count, violations),
        )
        self.assertEqual(result.diagnostics, ())

        identities = tuple(
            sorted(
                (record["printing_id"] for record in records),
                key=lambda value: value.encode("utf-8"),
            )
        )
        self.assertEqual(
            (len(identities), identities[0], identities[-1]),
            (
                814,
                "CORE01-AET-FGS-001-C-NF-A1-V1",
                "TMP_HOLD01-AQU-ART-047-C-NF-A1-V1",
            ),
        )
        self.assertEqual(
            hashlib.sha256("\n".join(identities).encode("utf-8")).hexdigest(),
            "57a272bda91b3ef58bec9ccffbca54fc90079c88ce3afb50ac424d76649148fc",
        )

    @staticmethod
    def _pre_d2b_ast_unsupported_reason(node):
        direct_reason = definition._call_free_unsupported_reason(node)
        if direct_reason is None:
            return None
        guarded_reason = definition._guarded_equality_unsupported_reason(
            node, direct_reason
        )
        if guarded_reason is None:
            return None
        compound_reason = definition._guarded_compound_when_unsupported_reason(
            node, direct_reason
        )
        if compound_reason is None:
            return None
        sequence_reason = definition._sequence_when_unsupported_reason(
            node, direct_reason
        )
        if sequence_reason is None:
            return None
        if definition._b3_unsupported_reason(node) is None:
            return None
        return (
            sequence_reason
            if isinstance(node, validation.Sequence)
            else compound_reason
        )

    def test_d2b_text_schema_cardinality_delta_and_results_are_exact(self):
        catalog, context = execution_tests.current_corpus_catalog_and_context()
        reverse_catalog, reverse_context = (
            execution_tests.current_corpus_catalog_and_context(reverse=True)
        )
        definitions = tuple(
            rule
            for rule in catalog.by_stage("pre_export")
            if rule.validation_kind_id == "definition_invariant"
        )
        legacy_ast_unsupported = {
            rule.rule_id
            for rule in definitions
            if self._pre_d2b_ast_unsupported_reason(rule.condition_ast)
            is not None
        }
        self.assertEqual(len(legacy_ast_unsupported), 34)
        self.assertTrue(set(self.D2B_RESULTS) <= legacy_ast_unsupported)

        executed = {
            rule.rule_id: execution.execute_definition_invariant_rule(
                rule, context
            )
            for rule in definitions
        }
        previous = set(self.supported_results) - set(self.D2B_RESULTS)
        newly_supported = {
            rule_id
            for rule_id, result in executed.items()
            if result.outcome is not execution.ValidationOutcome.UNSUPPORTED
            and rule_id not in previous
        }
        self.assertEqual(newly_supported, set(self.D2B_RESULTS))

        cardinality_calls = []
        total_records = 0
        total_violations = 0
        text_fields = []
        for rule_id, expected in sorted(self.D2B_RESULTS.items()):
            rule = catalog.get(rule_id)
            root = rule.condition_ast
            nodes = tuple(self._walk(root))
            cardinality_calls.extend(
                node
                for node in nodes
                if isinstance(node, validation.Call)
                and node.function
                in {
                    "at_least_one_non_null",
                    "at_most_one_non_null",
                    "count_non_null",
                }
            )
            self.assertIsNone(definition._ast_unsupported_reason(root))
            self.assertFalse(definition._lookup_nodes(root))

            namespace = context.namespace_for_component(rule.component_identity)
            schema = context.table("schema_fields", namespace=namespace)
            for identifier in rule.free_identifiers:
                matches = tuple(
                    field
                    for field in schema
                    if field.get("table_id") == rule.target_table_id
                    and field.get("field_name") == identifier
                    and field.get("status") == "active"
                )
                self.assertEqual(len(matches), 1, (rule_id, identifier))
                self.assertIsNone(definition._field_schema_reason(matches[0]))
                if identifier in {"value_text", "literal_text"}:
                    self.assertEqual(matches[0].get("data_type"), "text")
                    text_fields.append((rule_id, identifier))

            table_id, record_count, guard_false, guard_true, violations = expected
            records = context.table(rule.target_table_id, namespace=namespace)
            result = executed[rule_id]
            reverse_result = execution.execute_definition_invariant_rule(
                reverse_catalog.get(rule_id), reverse_context
            )
            with self.subTest(rule=rule_id):
                self.assertEqual(rule.target_table_id, table_id)
                self.assertEqual(len(records), record_count)
                self.assertEqual(result, reverse_result)
                self.assertIs(result.outcome, execution.ValidationOutcome.PASS)
                self.assertEqual(result.evaluated_record_count, record_count)
                self.assertEqual(result.violation_count, violations)
                self.assertEqual(result.diagnostics, ())

            if guard_false is not None:
                self.assertIsInstance(root, validation.Call)
                self.assertEqual(root.function, "when")
                guard_results = tuple(
                    definition.evaluate_validation_expression(
                        root.arguments[0],
                        {
                            name: record[name]
                            for name in rule.free_identifiers
                        },
                    )
                    for record in records
                )
                self.assertEqual(guard_results.count(False), guard_false)
                self.assertEqual(guard_results.count(True), guard_true)
            total_records += record_count
            total_violations += result.violation_count

        self.assertEqual(
            Counter(call.function for call in cardinality_calls),
            {
                "at_least_one_non_null": 2,
                "at_most_one_non_null": 2,
                "count_non_null": 2,
            },
        )
        self.assertTrue(
            all(
                len(call.arguments) == 1
                and isinstance(call.arguments[0], validation.ListLiteral)
                and all(
                    isinstance(item, validation.Identifier)
                    for item in call.arguments[0].items
                )
                for call in cardinality_calls
            )
        )
        self.assertEqual(len(text_fields), 5)
        self.assertEqual(total_records, 66)
        self.assertEqual(total_violations, 0)

    @classmethod
    def _pre_d2c_ast_unsupported_reason(cls, node):
        if definition._is_supported_cardinality_shape(node):
            return None
        return cls._pre_d2b_ast_unsupported_reason(node)

    def test_d2c_binding_delta_execution_and_lookup_evidence_are_exact(self):
        catalog, context = execution_tests.current_corpus_catalog_and_context()
        reverse_catalog, reverse_context = (
            execution_tests.current_corpus_catalog_and_context(reverse=True)
        )
        definitions = tuple(
            rule
            for rule in catalog.by_stage("pre_export")
            if rule.validation_kind_id == "definition_invariant"
        )
        legacy_unsupported = {
            rule.rule_id
            for rule in definitions
            if self._pre_d2c_ast_unsupported_reason(rule.condition_ast)
            is not None
        }
        self.assertEqual(len(legacy_unsupported), 28)
        self.assertTrue(set(self.D2C_RESULTS) <= legacy_unsupported)

        executed = {
            rule.rule_id: execution.execute_definition_invariant_rule(
                rule, context
            )
            for rule in definitions
        }
        previous = set(self.supported_results) - set(self.D2C_RESULTS)
        newly_supported = {
            rule_id
            for rule_id, result in executed.items()
            if result.outcome is not execution.ValidationOutcome.UNSUPPORTED
            and rule_id not in previous
        }
        self.assertEqual(newly_supported, set(self.D2C_RESULTS))

        expected_evidence = {
            "cdb_val_effect_parameter_collection_index": {
                "binding_names": ("field_is_collection",),
                "free_identifiers": ("contract_field_id", "item_index"),
                "lookup_nodes": 1,
                "calls": 14,
                "domains": Counter({
                    ("registry", "contract_fields", "is_collection"): 14,
                }),
                "nullable_outputs": {
                    ("registry", "contract_fields", "is_collection"): False,
                },
            },
            "cdb_val_effect_parameter_contract_match": {
                "binding_names": ("action_schema_id", "field_schema_id"),
                "free_identifiers": ("contract_field_id", "effect_id"),
                "lookup_nodes": 3,
                "calls": 42,
                "domains": Counter({
                    (
                        "carddatabase",
                        "ability_effects",
                        "effect_action_type_id",
                    ): 14,
                    (
                        "registry",
                        "effect_action_types",
                        "parameter_schema_id",
                    ): 14,
                    (
                        "registry",
                        "contract_fields",
                        "contract_schema_id",
                    ): 14,
                }),
                "nullable_outputs": {
                    (
                        "carddatabase",
                        "ability_effects",
                        "effect_action_type_id",
                    ): False,
                    (
                        "registry",
                        "effect_action_types",
                        "parameter_schema_id",
                    ): True,
                    (
                        "registry",
                        "contract_fields",
                        "contract_schema_id",
                    ): False,
                },
            },
        }

        original = definition._resolve_scalar_lookup
        total_records = 0
        total_calls = 0
        for rule_id, expected in expected_evidence.items():
            rule = catalog.get(rule_id)
            root = rule.condition_ast
            self.assertIsInstance(root, validation.Sequence)
            bindings = tuple(
                statement
                for statement in root.statements
                if isinstance(statement, validation.Binding)
            )
            self.assertEqual(
                root.statements[:len(bindings)], bindings
            )
            self.assertEqual(
                tuple(binding.name for binding in bindings),
                expected["binding_names"],
            )
            self.assertEqual(rule.local_bindings, expected["binding_names"])
            self.assertEqual(
                rule.free_identifiers, expected["free_identifiers"]
            )
            self.assertIsNone(definition._ast_unsupported_reason(root))
            self.assertEqual(
                len(definition._lookup_nodes(root)), expected["lookup_nodes"]
            )

            namespace = context.namespace_for_component(
                rule.component_identity
            )
            records = context.table(
                rule.target_table_id, namespace=namespace
            )
            domains = definition._prepare_lookup_domains(
                root, context, namespace
            )
            self.assertEqual(
                {
                    (
                        domain.namespace,
                        domain.table_id,
                        domain.output_field_name,
                    ): domain.output_schema.get("nullable")
                    for domain in domains.values()
                },
                expected["nullable_outputs"],
            )

            evidence = {
                "calls": 0,
                "exact": 0,
                "zero": 0,
                "ambiguous": 0,
                "null_keys": 0,
                "none_outputs": 0,
                "domains": Counter(),
            }

            def observe(domain, key):
                evidence["calls"] += 1
                evidence["null_keys"] += key is None
                evidence["domains"][(
                    domain.namespace,
                    domain.table_id,
                    domain.output_field_name,
                )] += 1
                try:
                    resolved = original(domain, key)
                except definition._ScalarLookupFailure as error:
                    evidence["ambiguous"] += error.reason == "lookup_ambiguous"
                    raise
                evidence["exact"] += resolved.state == "EXACT"
                evidence["zero"] += resolved.state == "ZERO"
                evidence["none_outputs"] += resolved.value is None
                return resolved

            try:
                definition._resolve_scalar_lookup = observe
                result = execution.execute_definition_invariant_rule(
                    rule, context
                )
            finally:
                definition._resolve_scalar_lookup = original

            reverse_result = execution.execute_definition_invariant_rule(
                reverse_catalog.get(rule_id), reverse_context
            )
            resolver = lambda table, key, value, output: original(
                domains[(table, key, output)], value
            ).value
            predicate_results = tuple(
                definition.evaluate_validation_expression(
                    root,
                    {
                        name: record[name]
                        for name in rule.free_identifiers
                    },
                    lookup_resolver=resolver,
                )
                for record in records
            )

            with self.subTest(rule=rule_id):
                self.assertEqual(result, reverse_result)
                self.assertIs(result.outcome, execution.ValidationOutcome.PASS)
                self.assertEqual(
                    (result.evaluated_record_count, result.violation_count),
                    (14, 0),
                )
                self.assertEqual(Counter(predicate_results), {True: 14})
                self.assertEqual(evidence["calls"], expected["calls"])
                self.assertEqual(evidence["exact"], expected["calls"])
                self.assertEqual(evidence["zero"], 0)
                self.assertEqual(evidence["ambiguous"], 0)
                self.assertEqual(evidence["null_keys"], 0)
                self.assertEqual(evidence["none_outputs"], 0)
                self.assertEqual(evidence["domains"], expected["domains"])
            total_records += len(records)
            total_calls += evidence["calls"]

        self.assertEqual(total_records, 28)
        self.assertEqual(total_calls, 56)

    @classmethod
    def _pre_d2d_ast_unsupported_reason(cls, node):
        if definition._binding_sequence_unsupported_reason(node) is None:
            return None
        return cls._pre_d2c_ast_unsupported_reason(node)

    def test_d2d_record_binding_delta_and_execution_evidence_are_exact(self):
        catalog, context = execution_tests.current_corpus_catalog_and_context()
        reverse_catalog, reverse_context = (
            execution_tests.current_corpus_catalog_and_context(reverse=True)
        )
        definitions = tuple(
            rule
            for rule in catalog.by_stage("pre_export")
            if rule.validation_kind_id == "definition_invariant"
        )
        legacy_unsupported = {
            rule.rule_id
            for rule in definitions
            if self._pre_d2d_ast_unsupported_reason(rule.condition_ast)
            is not None
        }
        self.assertEqual(len(legacy_unsupported), 26)
        self.assertTrue(set(self.D2D_RESULTS) <= legacy_unsupported)

        executed = {
            rule.rule_id: execution.execute_definition_invariant_rule(
                rule, context
            )
            for rule in definitions
        }
        previous = set(self.supported_results) - set(self.D2D_RESULTS)
        newly_supported = {
            rule_id
            for rule_id, result in executed.items()
            if result.outcome is not execution.ValidationOutcome.UNSUPPORTED
            and rule_id not in previous
        }
        self.assertEqual(newly_supported, set(self.D2D_RESULTS))

        self.assertFalse(any(
            result.outcome is execution.ValidationOutcome.UNSUPPORTED
            for result in executed.values()
        ))

        evaluator_globals = (
            definition.evaluate_validation_expression.__globals__
        )
        evaluation_error = evaluator_globals[
            "ValidationExpressionEvaluationError"
        ]
        original_lookup = definition._resolve_record_lookup
        original_member = evaluator_globals["_evaluate_member_access"]
        total_records = 0
        total_lookups = 0
        total_members = 0
        total_guard_false = 0
        total_guard_true = 0
        total_domains = Counter()
        for rule_id, expected in sorted(self.D2D_RESULTS.items()):
            rule = catalog.get(rule_id)
            root = rule.condition_ast
            if isinstance(root, validation.Call):
                self.assertEqual((root.function, len(root.arguments)), ("when", 2))
                sequence = root.arguments[1]
            else:
                sequence = root
            self.assertIsInstance(sequence, validation.Sequence)
            bindings = tuple(
                statement
                for statement in sequence.statements
                if isinstance(statement, validation.Binding)
            )
            self.assertTrue(bindings)
            self.assertEqual(sequence.statements[:len(bindings)], bindings)
            self.assertTrue(
                any(
                    isinstance(binding.value, validation.Call)
                    and binding.value.function == "lookup_record"
                    for binding in bindings
                )
            )
            self.assertIsNone(definition._ast_unsupported_reason(root))
            record_lookups = definition._record_lookup_nodes(root)
            self.assertTrue(record_lookups)
            member_nodes = tuple(
                node
                for node in self._walk(root)
                if isinstance(node, validation.MemberAccess)
            )
            self.assertTrue(member_nodes)
            self.assertTrue(
                all(
                    isinstance(node.target, validation.Identifier)
                    for node in member_nodes
                )
            )

            namespace = context.namespace_for_component(
                rule.component_identity
            )
            records = context.table(rule.target_table_id, namespace=namespace)
            domains = definition._prepare_record_lookup_domains(
                root, context, namespace
            )
            self.assertEqual(len(domains), len(set(domains)))
            self.assertTrue(
                all(
                    domain.key_field_name == domain.primary_key_name
                    for domain in domains.values()
                )
            )

            (
                table_id,
                record_count,
                expected_guard_false,
                expected_guard_true,
                expected_lookups,
                expected_members,
            ) = expected
            if expected_guard_false is None:
                self.assertNotIsInstance(root, validation.Call)
            else:
                guard_results = tuple(
                    definition.evaluate_validation_expression(
                        root.arguments[0],
                        {
                            name: record[name]
                            for name in rule.free_identifiers
                        },
                    )
                    for record in records
                )
                self.assertEqual(
                    (
                        guard_results.count(False),
                        guard_results.count(True),
                    ),
                    (expected_guard_false, expected_guard_true),
                )
                total_guard_false += expected_guard_false
                total_guard_true += expected_guard_true

            evidence = {
                "calls": 0,
                "exact": 0,
                "zero": 0,
                "ambiguous": 0,
                "null_keys": 0,
                "missing_source": 0,
                "domains": Counter(),
                "members": 0,
                "member_missing": 0,
                "none_member": 0,
                "scalar_member": 0,
            }

            def observe_lookup(domain, key):
                evidence["calls"] += 1
                evidence["null_keys"] += key is None
                identity = (
                    domain.namespace,
                    domain.table_id,
                    domain.key_field_name,
                )
                evidence["domains"][identity] += 1
                try:
                    resolved = original_lookup(domain, key)
                except definition._ScalarLookupFailure as error:
                    evidence["ambiguous"] += error.reason == "lookup_ambiguous"
                    evidence["missing_source"] += error.reason in {
                        "lookup_namespace_invalid",
                        "lookup_table_missing",
                    }
                    raise
                evidence["exact"] += resolved.state == "EXACT"
                evidence["zero"] += resolved.state == "ZERO"
                return resolved

            def observe_member(
                node,
                identifiers,
                lookup_resolver,
                record_lookup_resolver,
                schema_version_resolver,
            ):
                evidence["members"] += 1
                try:
                    return original_member(
                        node,
                        identifiers,
                        lookup_resolver,
                        record_lookup_resolver,
                        schema_version_resolver,
                    )
                except evaluation_error as error:
                    reason = dict(error.context).get("reason")
                    evidence["member_missing"] += reason == "member_missing"
                    evidence["none_member"] += (
                        reason == "member_access_base_is_none"
                    )
                    evidence["scalar_member"] += (
                        reason == "member_access_base_not_record"
                    )
                    raise

            try:
                definition._resolve_record_lookup = observe_lookup
                evaluator_globals["_evaluate_member_access"] = observe_member
                result = execution.execute_definition_invariant_rule(
                    rule, context
                )
            finally:
                definition._resolve_record_lookup = original_lookup
                evaluator_globals["_evaluate_member_access"] = original_member

            reverse_result = execution.execute_definition_invariant_rule(
                reverse_catalog.get(rule_id), reverse_context
            )
            with self.subTest(rule=rule_id):
                self.assertEqual(rule.target_table_id, table_id)
                self.assertEqual(len(records), record_count)
                self.assertEqual(result, reverse_result)
                self.assertIs(result.outcome, execution.ValidationOutcome.PASS)
                self.assertEqual(
                    (result.evaluated_record_count, result.violation_count),
                    (record_count, 0),
                )
                self.assertEqual(result.diagnostics, ())
                self.assertEqual(evidence["calls"], expected_lookups)
                self.assertEqual(evidence["exact"], expected_lookups)
                self.assertEqual(evidence["zero"], 0)
                self.assertEqual(evidence["ambiguous"], 0)
                self.assertEqual(evidence["null_keys"], 0)
                self.assertEqual(evidence["missing_source"], 0)
                self.assertEqual(
                    evidence["domains"], self.D2D_DOMAINS[rule_id]
                )
                self.assertEqual(evidence["members"], expected_members)
                self.assertEqual(evidence["member_missing"], 0)
                self.assertEqual(evidence["none_member"], 0)
                self.assertEqual(evidence["scalar_member"], 0)
            total_records += record_count
            total_lookups += evidence["calls"]
            total_members += evidence["members"]
            total_domains.update(evidence["domains"])

        self.assertEqual(total_records, 400)
        self.assertEqual(total_lookups, 458)
        self.assertEqual(total_members, 912)
        self.assertEqual((total_guard_false, total_guard_true), (137, 79))
        self.assertEqual(sum(total_domains.values()), 458)

    def test_d2e_version_helper_delta_and_execution_are_exact(self):
        target_rule_id = "cdb_val_abilities_template_compatibility"
        catalog, context = execution_tests.current_corpus_catalog_and_context()
        reverse_catalog, reverse_context = (
            execution_tests.current_corpus_catalog_and_context(reverse=True)
        )
        definitions = tuple(
            rule
            for rule in catalog.by_stage("pre_export")
            if rule.validation_kind_id == "definition_invariant"
        )
        executed = {
            rule.rule_id: execution.execute_definition_invariant_rule(
                rule, context
            )
            for rule in definitions
        }
        current_unsupported = {
            rule_id
            for rule_id, result in executed.items()
            if result.outcome is execution.ValidationOutcome.UNSUPPORTED
        }
        pre_d2e_supported = (
            {rule.rule_id for rule in definitions}
            - self.PRE_D2E_UNSUPPORTED
        )
        current_supported = {
            rule_id
            for rule_id, result in executed.items()
            if result.outcome is not execution.ValidationOutcome.UNSUPPORTED
        }

        self.assertEqual(len(self.PRE_D2E_UNSUPPORTED), 13)
        self.assertEqual(
            current_unsupported
            | set(self.D2F_RESULTS)
            | set(self.D2G_RESULTS)
            | set(self.D2H_RESULTS)
            | set(self.D2I_RESULTS)
            | set(self.D2J_RESULTS)
            | set(self.D2K_RESULTS),
            self.PRE_D2E_UNSUPPORTED - {target_rule_id},
        )
        self.assertEqual(
            (
                current_supported
                - set(self.D2F_RESULTS)
                - set(self.D2G_RESULTS)
                - set(self.D2H_RESULTS)
                - set(self.D2I_RESULTS)
                - set(self.D2J_RESULTS)
                - set(self.D2K_RESULTS)
            ) - pre_d2e_supported,
            {target_rule_id},
        )
        self.assertEqual(set(self.D2E_RESULTS), {target_rule_id})

        rule = catalog.get(target_rule_id)
        root = rule.condition_ast
        self.assertIsInstance(root, validation.Call)
        self.assertEqual((root.function, len(root.arguments)), ("when", 2))
        guard, constraint = root.arguments
        self.assertIsInstance(constraint, validation.Sequence)
        self.assertEqual(len(constraint.statements), 2)
        binding = constraint.statements[0]
        self.assertIsInstance(binding, validation.Binding)
        self.assertEqual(binding.name, "template")
        self.assertIsInstance(binding.value, validation.Call)
        self.assertEqual(binding.value.function, "lookup_record")
        self.assertEqual(
            {
                node.function
                for node in self._walk(root)
                if isinstance(node, validation.Call)
            },
            {
                "when",
                "lookup_record",
                "version_gte",
                "current_schema_version",
            },
        )
        self.assertIsNone(definition._ast_unsupported_reason(root))

        self.assertEqual(
            definition._resolve_component_schema_version(
                context, "CARDDATABASE"
            ),
            "0.7.0",
        )
        self.assertEqual(
            definition._resolve_component_schema_version(context, "REGISTRY"),
            "0.5.1",
        )
        templates = tuple(
            record
            for record in context.table(
                "ability_templates", namespace="registry"
            )
            if record.get("status") == "active"
        )
        self.assertEqual(len(templates), 5)
        self.assertEqual(
            Counter(
                record.get("minimum_carddatabase_schema_version")
                for record in templates
            ),
            {"0.4.0": 5},
        )

        namespace = context.namespace_for_component(rule.component_identity)
        records = context.table(rule.target_table_id, namespace=namespace)
        guard_results = tuple(
            definition.evaluate_validation_expression(
                guard,
                {
                    name: record[name]
                    for name in rule.free_identifiers
                },
            )
            for record in records
        )
        table_id, record_count, guard_false, guard_true = self.D2E_RESULTS[
            target_rule_id
        ]
        self.assertEqual(rule.target_table_id, table_id)
        self.assertEqual(len(records), record_count)
        self.assertEqual(
            (guard_results.count(False), guard_results.count(True)),
            (guard_false, guard_true),
        )

        original_resolver = definition._resolve_component_schema_version
        resolver_calls = []

        def observe_schema_version(data, component_id):
            value = original_resolver(data, component_id)
            resolver_calls.append((component_id, value))
            return value

        try:
            definition._resolve_component_schema_version = (
                observe_schema_version
            )
            result = execution.execute_definition_invariant_rule(rule, context)
        finally:
            definition._resolve_component_schema_version = original_resolver

        reverse_result = execution.execute_definition_invariant_rule(
            reverse_catalog.get(target_rule_id), reverse_context
        )
        self.assertEqual(result, reverse_result)
        self.assertIs(result.outcome, execution.ValidationOutcome.PASS)
        self.assertEqual(
            (result.evaluated_record_count, result.violation_count),
            (record_count, 0),
        )
        self.assertEqual(result.diagnostics, ())
        self.assertEqual(
            resolver_calls,
            [("CARDDATABASE", "0.7.0")] * guard_true,
        )

    def test_d2f_table_count_delta_and_execution_evidence_are_exact(self):
        catalog, context = execution_tests.current_corpus_catalog_and_context()
        reverse_catalog, reverse_context = (
            execution_tests.current_corpus_catalog_and_context(reverse=True)
        )
        definitions = tuple(
            rule
            for rule in catalog.by_stage("pre_export")
            if rule.validation_kind_id == "definition_invariant"
        )
        executed = {
            rule.rule_id: execution.execute_definition_invariant_rule(
                rule, context
            )
            for rule in definitions
        }
        current_unsupported = {
            rule_id
            for rule_id, result in executed.items()
            if result.outcome is execution.ValidationOutcome.UNSUPPORTED
        }
        pre_d2f_supported = (
            {rule.rule_id for rule in definitions}
            - self.PRE_D2F_UNSUPPORTED
        )
        current_supported = {
            rule_id
            for rule_id, result in executed.items()
            if result.outcome is not execution.ValidationOutcome.UNSUPPORTED
        }
        self.assertEqual(len(self.PRE_D2F_UNSUPPORTED), 12)
        self.assertEqual(
            current_unsupported
            | set(self.D2G_RESULTS)
            | set(self.D2H_RESULTS)
            | set(self.D2I_RESULTS)
            | set(self.D2J_RESULTS)
            | set(self.D2K_RESULTS),
            self.PRE_D2F_UNSUPPORTED - set(self.D2F_RESULTS),
        )
        self.assertEqual(
            (
                current_supported
                - set(self.D2G_RESULTS)
                - set(self.D2H_RESULTS)
                - set(self.D2I_RESULTS)
                - set(self.D2J_RESULTS)
                - set(self.D2K_RESULTS)
            )
            - pre_d2f_supported,
            set(self.D2F_RESULTS),
        )

        evaluator_globals = (
            definition.evaluate_validation_expression.__globals__
        )
        original_count = evaluator_globals["_evaluate_count"]
        evidence_by_rule = {}
        expected_outer_identifiers = {
            "cdb_val_decks_clan_realm_contract": frozenset({
                "primary_clan_id",
                "realm_id",
                "secondary_clan_id",
                "status",
            }),
            "cdb_val_effects_duration_supported": frozenset({
                "effect_action_type_id",
                "effect_id",
            }),
            "cdb_val_effects_modifier_definition": frozenset({
                "effect_id",
                "field_id",
                "modifier_type_id",
            }),
            "cdb_val_effects_restriction_definition": frozenset({
                "condition_id",
                "effect_id",
                "restriction_type_id",
            }),
        }
        for rule_id, expected in sorted(self.D2F_RESULTS.items()):
            rule = catalog.get(rule_id)
            root = rule.condition_ast
            self.assertIsInstance(root, validation.Call)
            self.assertEqual((root.function, len(root.arguments)), ("when", 2))
            self.assertIsNone(definition._ast_unsupported_reason(root))
            self.assertTrue(definition._call_nodes(root, "count"))
            self.assertEqual(
                definition._outer_identifier_names(root),
                expected_outer_identifiers[rule_id],
            )

            evidence = []

            def observe_count(
                node,
                identifiers,
                lookup_resolver,
                record_lookup_resolver,
                schema_version_resolver,
            ):
                result = original_count(
                    node,
                    identifiers,
                    lookup_resolver,
                    record_lookup_resolver,
                    schema_version_resolver,
                )
                current = identifiers["current"]
                identity = current.get("deck_id") or current.get("effect_id")
                evidence.append((identity, node.arguments[0].value, result))
                return result

            try:
                evaluator_globals["_evaluate_count"] = observe_count
                result = execution.execute_definition_invariant_rule(
                    rule, context
                )
            finally:
                evaluator_globals["_evaluate_count"] = original_count

            reverse_result = execution.execute_definition_invariant_rule(
                reverse_catalog.get(rule_id), reverse_context
            )
            table_id, record_count, guard_false, guard_true, count_calls = (
                expected
            )
            source_namespace = context.namespace_for_component(
                rule.component_identity
            )
            target_records = context.table(
                rule.target_table_id, namespace=source_namespace
            )
            primary_key = definition._resolve_primary_key(
                context,
                rule.target_table_id,
                namespace=source_namespace,
            )
            ordered_records = sorted(
                target_records,
                key=lambda record: definition._record_sort_key(
                    record, primary_key
                ),
            )
            if rule_id == "cdb_val_effects_duration_supported":
                observed_guard_counts = (
                    sum(value == 0 for _, _, value in evidence),
                    sum(value > 0 for _, _, value in evidence),
                )
            else:
                guard_results = tuple(
                    definition.evaluate_validation_expression(
                        root.arguments[0], dict(record)
                    )
                    for record in ordered_records
                )
                observed_guard_counts = (
                    guard_results.count(False),
                    guard_results.count(True),
                )
            with self.subTest(rule=rule_id):
                self.assertEqual(rule.target_table_id, table_id)
                self.assertEqual(result, reverse_result)
                self.assertIs(result.outcome, execution.ValidationOutcome.PASS)
                self.assertEqual(
                    (result.evaluated_record_count, result.violation_count),
                    (record_count, 0),
                )
                self.assertEqual(result.diagnostics, ())
                self.assertEqual(len(evidence), count_calls)
                self.assertEqual(
                    observed_guard_counts, (guard_false, guard_true)
                )
            evidence_by_rule[rule_id] = (
                evidence,
                *observed_guard_counts,
            )

        deck_evidence, deck_false, deck_true = evidence_by_rule[
            "cdb_val_decks_clan_realm_contract"
        ]
        self.assertEqual((deck_false, deck_true), (0, 2))
        self.assertEqual(
            deck_evidence,
            [
                ("DECK-AQU-MOR-VS1-001", "cards", 58),
                ("DECK-AQU-MOR-VS1-001", "cards", 60),
                ("DECK-IGN-HAM-VS1-001", "cards", 58),
                ("DECK-IGN-HAM-VS1-001", "cards", 58),
            ],
        )

        duration_evidence, duration_false, duration_true = evidence_by_rule[
            "cdb_val_effects_duration_supported"
        ]
        self.assertEqual((duration_false, duration_true), (14, 7))
        self.assertEqual(
            Counter(result for _, _, result in duration_evidence),
            {0: 14, 1: 7},
        )

        modifier_evidence, modifier_false, modifier_true = evidence_by_rule[
            "cdb_val_effects_modifier_definition"
        ]
        self.assertEqual((modifier_false, modifier_true), (18, 3))
        self.assertEqual(
            Counter(result for _, _, result in modifier_evidence), {1: 3}
        )

        restriction_evidence, restriction_false, restriction_true = (
            evidence_by_rule["cdb_val_effects_restriction_definition"]
        )
        self.assertEqual((restriction_false, restriction_true), (20, 1))
        self.assertEqual(
            Counter(result for _, _, result in restriction_evidence), {1: 1}
        )

    def test_d2g_domain_primitive_delta_and_corpus_evidence_are_exact(self):
        catalog, context = execution_tests.current_corpus_catalog_and_context()
        reverse_catalog, reverse_context = (
            execution_tests.current_corpus_catalog_and_context(reverse=True)
        )
        definitions = tuple(
            rule
            for rule in catalog.by_stage("pre_export")
            if rule.validation_kind_id == "definition_invariant"
        )
        executed = {
            rule.rule_id: execution.execute_definition_invariant_rule(
                rule, context
            )
            for rule in definitions
        }
        current_unsupported = {
            rule_id
            for rule_id, result in executed.items()
            if result.outcome is execution.ValidationOutcome.UNSUPPORTED
        }
        pre_d2g_supported = (
            {rule.rule_id for rule in definitions}
            - self.PRE_D2G_UNSUPPORTED
        )
        current_supported = {
            rule_id
            for rule_id, result in executed.items()
            if result.outcome is not execution.ValidationOutcome.UNSUPPORTED
        }
        self.assertEqual(len(self.PRE_D2G_UNSUPPORTED), 8)
        self.assertEqual(
            current_unsupported
            | set(self.D2H_RESULTS)
            | set(self.D2I_RESULTS)
            | set(self.D2J_RESULTS)
            | set(self.D2K_RESULTS),
            self.PRE_D2G_UNSUPPORTED - set(self.D2G_RESULTS),
        )
        self.assertEqual(
            (
                current_supported
                - set(self.D2H_RESULTS)
                - set(self.D2I_RESULTS)
                - set(self.D2J_RESULTS)
                - set(self.D2K_RESULTS)
            )
            - pre_d2g_supported,
            set(self.D2G_RESULTS),
        )

        expected_calls = {
            "cdb_val_card_localization_search_name_normalized": {
                "normalize_search_name_hu",
            },
            "cdb_val_effect_parameter_value_contract": {
                "group_of",
                "lookup",
            },
            "cdb_val_keyword_grant_value_contract": {
                "group_of",
                "when",
            },
        }
        expected_outer_identifiers = {
            "cdb_val_card_localization_search_name_normalized": frozenset({
                "card_name",
                "search_name",
            }),
            "cdb_val_effect_parameter_value_contract": frozenset({
                "contract_field_id",
                "value_boolean",
                "value_expression_id",
                "value_integer",
                "value_reference_id",
                "value_registry_value_id",
                "value_text",
            }),
            "cdb_val_keyword_grant_value_contract": frozenset({
                "effect_action_type_id",
                "modifier_type_id",
                "restriction_type_id",
                "value_expression_id",
                "value_number",
                "value_registry_value_id",
                "value_text",
                "value_type_id",
            }),
        }
        evaluator_globals = (
            definition.evaluate_validation_expression.__globals__
        )
        original_normalize = evaluator_globals[
            "_evaluate_normalize_search_name_hu"
        ]
        original_lookup = definition._resolve_scalar_lookup
        evidence_by_rule = {}

        for rule_id, (table_id, record_count) in sorted(
            self.D2G_RESULTS.items()
        ):
            rule = catalog.get(rule_id)
            root = rule.condition_ast
            self.assertIsNone(definition._ast_unsupported_reason(root))
            self.assertEqual(
                {
                    node.function
                    for node in self._walk(root)
                    if isinstance(node, validation.Call)
                },
                expected_calls[rule_id],
            )
            self.assertEqual(
                definition._outer_identifier_names(root),
                expected_outer_identifiers[rule_id],
            )
            evidence = {"normalizations": [], "groups": []}

            def observe_normalize(
                node,
                identifiers,
                lookup_resolver,
                record_lookup_resolver,
                schema_version_resolver,
            ):
                result = original_normalize(
                    node,
                    identifiers,
                    lookup_resolver,
                    record_lookup_resolver,
                    schema_version_resolver,
                )
                evidence["normalizations"].append(result)
                return result

            def observe_lookup(domain, key):
                try:
                    resolved = original_lookup(domain, key)
                except definition._ScalarLookupFailure as error:
                    if (
                        domain.namespace == "registry"
                        and domain.table_id == "value_registry"
                        and domain.output_field_name == "group_id"
                    ):
                        evidence["groups"].append(
                            (key, error.reason, None)
                        )
                    raise
                if (
                    domain.namespace == "registry"
                    and domain.table_id == "value_registry"
                    and domain.output_field_name == "group_id"
                ):
                    evidence["groups"].append(
                        (key, resolved.state, resolved.value)
                    )
                return resolved

            try:
                evaluator_globals[
                    "_evaluate_normalize_search_name_hu"
                ] = observe_normalize
                definition._resolve_scalar_lookup = observe_lookup
                result = execution.execute_definition_invariant_rule(
                    rule, context
                )
            finally:
                evaluator_globals[
                    "_evaluate_normalize_search_name_hu"
                ] = original_normalize
                definition._resolve_scalar_lookup = original_lookup

            reverse_result = execution.execute_definition_invariant_rule(
                reverse_catalog.get(rule_id), reverse_context
            )
            with self.subTest(rule=rule_id):
                self.assertEqual(rule.target_table_id, table_id)
                self.assertEqual(result, reverse_result)
                self.assertIs(result.outcome, execution.ValidationOutcome.PASS)
                self.assertEqual(
                    (result.evaluated_record_count, result.violation_count),
                    (record_count, 0),
                )
                self.assertEqual(result.diagnostics, ())
            evidence_by_rule[rule_id] = evidence

        normalization = evidence_by_rule[
            "cdb_val_card_localization_search_name_normalized"
        ]
        self.assertEqual(len(normalization["normalizations"]), 814)
        self.assertEqual(normalization["groups"], [])

        parameter_groups = evidence_by_rule[
            "cdb_val_effect_parameter_value_contract"
        ]["groups"]
        self.assertEqual(len(parameter_groups), 6)
        self.assertEqual(
            Counter(state for _, state, _ in parameter_groups),
            {"EXACT": 6},
        )
        self.assertEqual(
            Counter(group for _, _, group in parameter_groups),
            {"damage_kind": 6},
        )
        self.assertEqual(
            Counter(value for value, _, _ in parameter_groups),
            {"damage_kind_direct": 6},
        )

        contract_fields = {
            record["contract_field_id"]: record
            for record in context.table(
                "contract_fields", namespace="registry"
            )
        }
        parameter_branches = Counter()
        for record in context.table(
            "ability_effect_parameters", namespace="carddatabase"
        ):
            field = contract_fields[record["contract_field_id"]]
            if record.get("value_expression_id") is not None:
                branch = "expression"
            elif (
                field.get("allowed_group_id") is not None
                and record.get("value_registry_value_id") is not None
            ):
                branch = "registry_group"
            elif (
                field.get("allowed_group_id") is None
                and field.get("reference_type_id") is not None
                and record.get("value_reference_id") is not None
            ):
                branch = "reference"
            else:
                branch = field.get("data_type")
            parameter_branches[branch] += 1
        self.assertEqual(
            parameter_branches,
            {"boolean": 1, "integer": 7, "registry_group": 6},
        )

        keyword_groups = evidence_by_rule[
            "cdb_val_keyword_grant_value_contract"
        ]["groups"]
        self.assertEqual(len(keyword_groups), 3)
        self.assertEqual(
            Counter(state for _, state, _ in keyword_groups),
            {"EXACT": 3},
        )
        self.assertEqual(
            Counter(group for _, _, group in keyword_groups),
            {"keyword": 3},
        )
        self.assertEqual(
            Counter(value for value, _, _ in keyword_groups),
            {"keyword_cleave": 2, "keyword_ward": 1},
        )
        keyword_rule = catalog.get(
            "cdb_val_keyword_grant_value_contract"
        )
        guard = keyword_rule.condition_ast.arguments[0]
        keyword_records = context.table(
            "ability_effects", namespace="carddatabase"
        )
        guard_results = tuple(
            definition.evaluate_validation_expression(
                guard,
                {
                    name: record[name]
                    for name in keyword_rule.free_identifiers
                },
            )
            for record in keyword_records
        )
        self.assertEqual(
            (guard_results.count(False), guard_results.count(True)),
            (18, 3),
        )

    def test_d2h_alias_normalize_count_delta_and_corpus_are_exact(self):
        target_rule_id = "val_migration_map_alias_resolution_invariant"
        catalog, context = execution_tests.current_corpus_catalog_and_context()
        reverse_catalog, reverse_context = (
            execution_tests.current_corpus_catalog_and_context(reverse=True)
        )
        definitions = tuple(
            rule
            for rule in catalog.by_stage("pre_export")
            if rule.validation_kind_id == "definition_invariant"
        )
        executed = {
            rule.rule_id: execution.execute_definition_invariant_rule(
                rule, context
            )
            for rule in definitions
        }
        current_unsupported = {
            rule_id
            for rule_id, result in executed.items()
            if result.outcome is execution.ValidationOutcome.UNSUPPORTED
        }
        current_supported = {
            rule_id
            for rule_id, result in executed.items()
            if result.outcome is not execution.ValidationOutcome.UNSUPPORTED
        }
        pre_d2h_supported = (
            {rule.rule_id for rule in definitions}
            - self.PRE_D2H_UNSUPPORTED
        )
        self.assertEqual(len(self.PRE_D2H_UNSUPPORTED), 5)
        self.assertEqual(
            current_unsupported
            | set(self.D2I_RESULTS)
            | set(self.D2J_RESULTS)
            | set(self.D2K_RESULTS),
            self.PRE_D2H_UNSUPPORTED - set(self.D2H_RESULTS),
        )
        self.assertEqual(
            (
                current_supported
                - set(self.D2I_RESULTS)
                - set(self.D2J_RESULTS)
                - set(self.D2K_RESULTS)
            )
            - pre_d2h_supported,
            set(self.D2H_RESULTS),
        )
        self.assertEqual(current_unsupported, set())

        rule = catalog.get(target_rule_id)
        root = rule.condition_ast
        self.assertIsInstance(root, validation.Call)
        self.assertEqual((root.function, len(root.arguments)), ("when", 2))
        self.assertEqual(
            {
                node.function
                for node in self._walk(root)
                if isinstance(node, validation.Call)
            },
            {"count", "lookup", "normalize", "when"},
        )
        self.assertIsNone(definition._ast_unsupported_reason(root))
        self.assertEqual(
            definition._outer_identifier_names(root),
            frozenset({
                "auto_migratable",
                "legacy_group",
                "legacy_value",
                "migration_type_id",
                "requires_manual_review",
                "target_field_id",
                "target_record_id",
                "target_table_id",
                "target_value",
                "transformation_rule",
            }),
        )

        namespace = context.namespace_for_component(rule.component_identity)
        records = context.table(rule.target_table_id, namespace=namespace)
        outer_names = definition._outer_identifier_names(root)
        guard = root.arguments[0]
        guard_results = tuple(
            definition.evaluate_validation_expression(
                guard, {name: record[name] for name in outer_names}
            )
            for record in records
        )
        self.assertEqual(len(records), 85)
        self.assertEqual(
            (guard_results.count(False), guard_results.count(True)),
            (67, 18),
        )
        alias_resolution = tuple(
            record
            for record, applies in zip(records, guard_results)
            if applies
        )
        pinned = tuple(
            record
            for record in alias_resolution
            if record.get("legacy_value") is not None
        )
        dynamic = tuple(
            record
            for record in alias_resolution
            if record.get("legacy_value") is None
        )
        self.assertEqual((len(pinned), len(dynamic)), (9, 9))

        aliases = tuple(
            record
            for record in context.table("aliases", namespace="registry")
            if record.get("status") == "active"
        )
        self.assertEqual(len(aliases), 95)
        self.assertEqual(
            Counter(
                (record.get("normalization_mode"), record.get("case_sensitive"))
                for record in aliases
            ),
            {("trim_casefold", False): 94, ("exact", True): 1},
        )

        normalize_ast = validation.parse_validation_expression(
            "normalize(value,mode,case_sensitive)"
        )
        pinned_evidence = []
        for record in pinned:
            matches = []
            for alias in aliases:
                normalized_alias = definition.evaluate_validation_expression(
                    normalize_ast,
                    {
                        "value": alias.get("alias_value"),
                        "mode": alias.get("normalization_mode"),
                        "case_sensitive": alias.get("case_sensitive"),
                    },
                )
                normalized_legacy = definition.evaluate_validation_expression(
                    normalize_ast,
                    {
                        "value": record.get("legacy_value"),
                        "mode": alias.get("normalization_mode"),
                        "case_sensitive": alias.get("case_sensitive"),
                    },
                )
                if (
                    alias.get("group_id") == record.get("legacy_group")
                    and normalized_alias == normalized_legacy
                    and alias.get("canonical_registry_value_id")
                    == record.get("target_record_id")
                    and alias.get("requires_audit")
                    == record.get("requires_manual_review")
                ):
                    matches.append((
                        alias.get("alias_id"),
                        alias.get("normalization_mode"),
                        alias.get("case_sensitive"),
                        normalized_alias,
                        normalized_legacy,
                    ))
            self.assertEqual(len(matches), 1, record.get("migration_id"))
            pinned_evidence.append((record.get("migration_id"), matches[0]))
        self.assertEqual(len(pinned_evidence), 9)
        self.assertTrue(
            all(item[1][3] == item[1][4] for item in pinned_evidence)
        )

        lookup_domains = definition._prepare_lookup_domains(
            root, context, "registry"
        )
        local_key = ("schema_fields", "field_id", "allowed_group_id")
        external_key = (
            "carddatabase:schema_fields",
            "field_id",
            "allowed_group_id",
        )
        dynamic_evidence = []
        for record in dynamic:
            target_field_id = record.get("target_field_id")
            local_domain = lookup_domains[local_key]
            external_domain = lookup_domains[external_key]
            local = definition._resolve_scalar_lookup(
                local_domain,
                definition._project_explicit_namespace_key(
                    local_domain, target_field_id
                ),
            )
            external = definition._resolve_scalar_lookup(
                external_domain,
                definition._project_explicit_namespace_key(
                    external_domain, target_field_id
                ),
            )
            active_group_aliases = tuple(
                alias
                for alias in aliases
                if alias.get("group_id") == record.get("legacy_group")
            )
            audit_aliases = tuple(
                alias
                for alias in active_group_aliases
                if alias.get("requires_audit") is True
            )
            self.assertEqual(local.state, "ZERO")
            self.assertEqual(external.state, "EXACT")
            self.assertEqual(
                external.value, record.get("legacy_group")
            )
            self.assertGreaterEqual(len(active_group_aliases), 1)
            self.assertEqual(
                bool(audit_aliases),
                record.get("requires_manual_review"),
            )
            dynamic_evidence.append((
                record.get("migration_id"),
                "carddatabase:schema_fields",
                external.matched_record_identity,
                external.value,
                len(active_group_aliases),
                len(audit_aliases),
            ))
        self.assertEqual(len(dynamic_evidence), 9)
        self.assertEqual(
            Counter(item[1] for item in dynamic_evidence),
            {"carddatabase:schema_fields": 9},
        )

        result = executed[target_rule_id]
        reverse_result = execution.execute_definition_invariant_rule(
            reverse_catalog.get(target_rule_id), reverse_context
        )
        self.assertEqual(result, reverse_result)
        self.assertIs(result.outcome, execution.ValidationOutcome.PASS)
        self.assertEqual(
            (result.evaluated_record_count, result.violation_count),
            (85, 0),
        )
        self.assertEqual(result.diagnostics, ())

    def test_d2i_template_binding_shape_delta_and_corpus_are_exact(self):
        target_rule_id = "val_ability_template_bindings_shape"
        catalog, context = execution_tests.current_corpus_catalog_and_context()
        reverse_catalog, reverse_context = (
            execution_tests.current_corpus_catalog_and_context(reverse=True)
        )
        definitions = tuple(
            rule
            for rule in catalog.by_stage("pre_export")
            if rule.validation_kind_id == "definition_invariant"
        )
        executed = {
            rule.rule_id: execution.execute_definition_invariant_rule(
                rule, context
            )
            for rule in definitions
        }
        current_unsupported = {
            rule_id
            for rule_id, result in executed.items()
            if result.outcome is execution.ValidationOutcome.UNSUPPORTED
        }
        current_supported = {
            rule_id
            for rule_id, result in executed.items()
            if result.outcome is not execution.ValidationOutcome.UNSUPPORTED
        }
        pre_d2i_supported = (
            {rule.rule_id for rule in definitions}
            - self.PRE_D2I_UNSUPPORTED
        )
        self.assertEqual(len(self.PRE_D2I_UNSUPPORTED), 4)
        self.assertEqual(
            current_unsupported
            | set(self.D2J_RESULTS)
            | set(self.D2K_RESULTS),
            self.PRE_D2I_UNSUPPORTED - set(self.D2I_RESULTS),
        )
        self.assertEqual(
            (
                current_supported
                - set(self.D2J_RESULTS)
                - set(self.D2K_RESULTS)
            )
            - pre_d2i_supported,
            set(self.D2I_RESULTS),
        )
        self.assertEqual(current_unsupported, set())

        rule = catalog.get(target_rule_id)
        root = rule.condition_ast
        self.assertIsInstance(root, validation.Call)
        self.assertEqual(
            (root.function, len(root.arguments)),
            ("template_binding_shape_valid", 4),
        )
        self.assertEqual(
            {
                node.function
                for node in self._walk(root)
                if isinstance(node, validation.Call)
            },
            {"template_binding_shape_valid"},
        )
        self.assertIsNone(definition._ast_unsupported_reason(root))
        outer_names = definition._outer_identifier_names(root)
        self.assertEqual(
            outer_names,
            frozenset({
                "binding_kind_id",
                "parameter_contract_field_id",
                "source_node_key",
                "fixed_boolean",
                "fixed_integer",
                "fixed_text",
                "fixed_registry_value_id",
                "fixed_reference_id",
            }),
        )

        schema = tuple(
            field
            for field in context.table(
                "schema_fields", namespace="registry"
            )
            if field.get("table_id") == "ability_template_bindings"
            and field.get("status") == "active"
        )
        fields = {field.get("field_name"): field for field in schema}
        expected_fixed_types = {
            "fixed_boolean": "boolean",
            "fixed_integer": "integer",
            "fixed_text": "text",
            "fixed_registry_value_id": "string",
            "fixed_reference_id": "string",
        }
        for field_name, data_type in expected_fixed_types.items():
            with self.subTest(field=field_name):
                self.assertEqual(fields[field_name].get("data_type"), data_type)
                self.assertIs(fields[field_name].get("nullable"), True)
                self.assertEqual(
                    fields[field_name].get("required_mode"), "conditional"
                )

        records = context.table(
            "ability_template_bindings", namespace="registry"
        )
        distribution = Counter(
            record.get("binding_kind_id") for record in records
        )
        self.assertEqual(
            distribution,
            {
                "fixed_value": 103,
                "generated_node_id": 16,
                "template_parameter": 6,
            },
        )
        outcomes = []
        for record in records:
            value = definition.evaluate_validation_expression(
                root, {name: record[name] for name in outer_names}
            )
            self.assertIs(type(value), bool)
            outcomes.append((
                record.get("template_binding_id"),
                record.get("binding_kind_id"),
                value,
            ))
        failures = tuple(item for item in outcomes if not item[2])
        self.assertEqual(failures, ())
        self.assertEqual(
            Counter(kind for _, kind, passed in outcomes if passed),
            distribution,
        )

        result = executed[target_rule_id]
        reverse_result = execution.execute_definition_invariant_rule(
            reverse_catalog.get(target_rule_id), reverse_context
        )
        self.assertEqual(result, reverse_result)
        self.assertIs(result.outcome, execution.ValidationOutcome.PASS)
        self.assertEqual(
            (result.evaluated_record_count, result.violation_count),
            (125, 0),
        )
        self.assertEqual(result.diagnostics, ())

    def test_d2j_typed_template_contract_delta_and_corpora_are_exact(self):
        target_rule_ids = set(self.D2J_RESULTS)
        catalog, context = execution_tests.current_corpus_catalog_and_context()
        reverse_catalog, reverse_context = (
            execution_tests.current_corpus_catalog_and_context(reverse=True)
        )
        definitions = tuple(
            rule
            for rule in catalog.by_stage("pre_export")
            if rule.validation_kind_id == "definition_invariant"
        )
        executed = {
            rule.rule_id: execution.execute_definition_invariant_rule(
                rule, context
            )
            for rule in definitions
        }
        current_unsupported = {
            rule_id
            for rule_id, result in executed.items()
            if result.outcome is execution.ValidationOutcome.UNSUPPORTED
        }
        current_supported = {
            rule_id
            for rule_id, result in executed.items()
            if result.outcome is not execution.ValidationOutcome.UNSUPPORTED
        }
        pre_d2j_supported = (
            {rule.rule_id for rule in definitions}
            - self.PRE_D2J_UNSUPPORTED
        )
        self.assertEqual(len(self.PRE_D2J_UNSUPPORTED), 3)
        self.assertEqual(
            current_unsupported | set(self.D2K_RESULTS),
            self.PRE_D2J_UNSUPPORTED - target_rule_ids,
        )
        self.assertEqual(
            (current_supported - set(self.D2K_RESULTS))
            - pre_d2j_supported,
            target_rule_ids,
        )
        self.assertEqual(current_unsupported, set())

        expected_calls = {
            "cdb_val_template_arguments_value_contract": (
                "template_argument_value_type_valid",
                7,
                frozenset({
                    "contract_field_id",
                    "value_boolean",
                    "value_integer",
                    "value_text",
                    "value_registry_value_id",
                    "value_reference_id",
                    "value_expression_id",
                }),
            ),
            "val_ability_template_bindings_value_type": (
                "template_binding_value_type_valid",
                8,
                frozenset({
                    "target_field_id",
                    "binding_kind_id",
                    "parameter_contract_field_id",
                    "fixed_boolean",
                    "fixed_integer",
                    "fixed_text",
                    "fixed_registry_value_id",
                    "fixed_reference_id",
                }),
            ),
        }
        for rule_id, (function, arity, identifiers) in expected_calls.items():
            rule = catalog.get(rule_id)
            self.assertIsInstance(rule.condition_ast, validation.Call)
            self.assertEqual(
                (rule.condition_ast.function, len(rule.condition_ast.arguments)),
                (function, arity),
            )
            self.assertEqual(
                definition._outer_identifier_names(rule.condition_ast),
                identifiers,
            )
            self.assertIsNone(
                definition._ast_unsupported_reason(rule.condition_ast)
            )

        contract_fields = tuple(
            row for row in context.table(
                "contract_fields", namespace="registry"
            )
            if row.get("status") == "active"
        )
        contract_by_id = {
            row["contract_field_id"]: row for row in contract_fields
        }
        self.assertEqual(len(contract_by_id), len(contract_fields))
        arguments = context.table(
            "ability_template_arguments", namespace="carddatabase"
        )
        argument_channels = (
            "value_boolean",
            "value_integer",
            "value_text",
            "value_registry_value_id",
            "value_reference_id",
            "value_expression_id",
        )
        self.assertEqual(len(arguments), 13)
        self.assertEqual(
            Counter(
                next(
                    name for name in argument_channels
                    if row.get(name) is not None
                )
                for row in arguments
            ),
            {"value_integer": 13},
        )
        referenced_contracts = {
            row["contract_field_id"] for row in arguments
        }
        self.assertEqual(len(referenced_contracts), 6)
        self.assertEqual(
            Counter(
                contract_by_id[row["contract_field_id"]]["data_type"]
                for row in arguments
            ),
            {"integer": 13},
        )
        self.assertEqual(
            sum(
                contract_by_id[row["contract_field_id"]]["allowed_group_id"]
                is not None
                for row in arguments
            ),
            0,
        )
        self.assertEqual(
            sum(
                contract_by_id[row["contract_field_id"]]["reference_type_id"]
                is not None
                for row in arguments
            ),
            0,
        )
        self.assertEqual(
            sum(row["value_expression_id"] is not None for row in arguments),
            0,
        )

        binding_rows = context.table(
            "ability_template_bindings", namespace="registry"
        )
        self.assertEqual(len(binding_rows), 125)
        self.assertEqual(
            Counter(row["binding_kind_id"] for row in binding_rows),
            {
                "fixed_value": 103,
                "generated_node_id": 16,
                "template_parameter": 6,
            },
        )
        schema_fields = tuple(
            row for row in context.table(
                "schema_fields", namespace="carddatabase"
            )
            if row.get("status") == "active"
        )
        schema_by_id = {row["field_id"]: row for row in schema_fields}
        target_ids = {row["target_field_id"] for row in binding_rows}
        self.assertEqual(len(target_ids), 42)
        self.assertTrue(target_ids <= set(schema_by_id))
        fixed_channels = (
            "fixed_boolean",
            "fixed_integer",
            "fixed_text",
            "fixed_registry_value_id",
            "fixed_reference_id",
        )
        fixed_evidence = Counter()
        for row in binding_rows:
            if row["binding_kind_id"] != "fixed_value":
                continue
            target = schema_by_id[row["target_field_id"]]
            if target["allowed_group_id"] is not None:
                classification = "controlled"
            elif target["reference_table_id"] is not None:
                classification = "physical_reference"
            elif target["data_type"] == "boolean":
                classification = "boolean"
            elif target["data_type"] == "integer":
                classification = "integer"
            else:
                classification = "text_like"
            channel = next(
                name for name in fixed_channels if row[name] is not None
            )
            fixed_evidence[(classification, channel)] += 1
        self.assertEqual(
            fixed_evidence,
            {
                ("controlled", "fixed_registry_value_id"): 44,
                ("physical_reference", "fixed_reference_id"): 35,
                ("physical_reference", "fixed_registry_value_id"): 3,
                ("integer", "fixed_integer"): 15,
                ("boolean", "fixed_boolean"): 6,
            },
        )

        parameter_rows = tuple(
            row for row in binding_rows
            if row["binding_kind_id"] == "template_parameter"
        )
        self.assertEqual(len(parameter_rows), 6)
        for row in parameter_rows:
            contract = contract_by_id[row["parameter_contract_field_id"]]
            target = schema_by_id[row["target_field_id"]]
            self.assertEqual(contract["data_type"], "integer")
            self.assertIsNone(contract["allowed_group_id"])
            self.assertIsNone(contract["reference_type_id"])
            self.assertIs(contract["is_collection"], False)
            self.assertEqual(target["data_type"], "integer")
            self.assertIsNone(target["allowed_group_id"])
            self.assertIsNone(target["reference_table_id"])

        generated_rows = tuple(
            row for row in binding_rows
            if row["binding_kind_id"] == "generated_node_id"
        )
        self.assertEqual(len(generated_rows), 16)
        generated_proofs = []
        for row in generated_rows:
            target = schema_by_id[row["target_field_id"]]
            reference_table_id = target["reference_table_id"]
            reference_field_id = target["reference_field_id"]
            self.assertIsInstance(reference_table_id, str)
            self.assertIsInstance(reference_field_id, str)
            namespace, table_id = (
                reference_table_id.split(":", 1)
                if ":" in reference_table_id
                else ("carddatabase", reference_table_id)
            )
            field_id = (
                reference_field_id.split(":", 1)[1]
                if ":" in reference_field_id
                else reference_field_id
            )
            referenced_fields = tuple(
                field for field in context.table(
                    "schema_fields", namespace=namespace
                )
                if field.get("field_id") == field_id
                and field.get("status") == "active"
            )
            schema_tables = tuple(
                table for table in context.table(
                    "schema_tables", namespace=namespace
                )
                if table.get("table_id") == table_id
                and table.get("status") == "active"
            )
            self.assertEqual(len(referenced_fields), 1)
            self.assertEqual(len(schema_tables), 1)
            self.assertEqual(referenced_fields[0]["table_id"], table_id)
            self.assertEqual(
                referenced_fields[0]["field_name"],
                schema_tables[0]["primary_key"],
            )
            generated_proofs.append((
                row["template_binding_id"],
                namespace,
                table_id,
                field_id,
            ))
        self.assertEqual(len(generated_proofs), 16)

        for rule_id, (table_id, record_count) in self.D2J_RESULTS.items():
            result = executed[rule_id]
            reverse_result = execution.execute_definition_invariant_rule(
                reverse_catalog.get(rule_id), reverse_context
            )
            with self.subTest(rule=rule_id):
                self.assertEqual(result, reverse_result)
                self.assertIs(
                    result.outcome, execution.ValidationOutcome.PASS
                )
                self.assertEqual(
                    (result.evaluated_record_count, result.violation_count),
                    (record_count, 0),
                )
                self.assertEqual(result.diagnostics, ())
                self.assertEqual(catalog.get(rule_id).target_table_id, table_id)

    def test_d2k_generated_node_delta_and_current_corpus_are_exact(self):
        target_rule_id = "val_ability_template_bindings_generated_node"
        catalog, context = execution_tests.current_corpus_catalog_and_context()
        reverse_catalog, reverse_context = (
            execution_tests.current_corpus_catalog_and_context(reverse=True)
        )
        definitions = tuple(
            rule
            for rule in catalog.by_stage("pre_export")
            if rule.validation_kind_id == "definition_invariant"
        )
        executed = {
            rule.rule_id: execution.execute_definition_invariant_rule(
                rule, context
            )
            for rule in definitions
        }
        current_supported = {
            rule_id
            for rule_id, result in executed.items()
            if result.outcome is not execution.ValidationOutcome.UNSUPPORTED
        }
        current_unsupported = {
            rule_id
            for rule_id, result in executed.items()
            if result.outcome is execution.ValidationOutcome.UNSUPPORTED
        }
        pre_d2k_supported = (
            {rule.rule_id for rule in definitions}
            - self.PRE_D2K_UNSUPPORTED
        )
        self.assertEqual(
            self.PRE_D2K_UNSUPPORTED, {target_rule_id}
        )
        self.assertEqual(
            current_supported - pre_d2k_supported,
            set(self.D2K_RESULTS),
        )
        self.assertEqual(current_unsupported, set())

        rule = catalog.get(target_rule_id)
        root = rule.condition_ast
        self.assertIsNone(definition._ast_unsupported_reason(root))
        self.assertEqual(
            {
                node.function
                for node in self._walk(root)
                if isinstance(node, validation.Call)
            },
            {"lookup", "lookup_record", "lookup_record_by", "when"},
        )
        self.assertEqual(
            definition._outer_identifier_names(root),
            frozenset({
                "binding_kind_id",
                "source_node_key",
                "target_field_id",
                "template_node_id",
            }),
        )

        bindings = context.table(
            "ability_template_bindings", namespace="registry"
        )
        nodes = context.table("ability_template_nodes", namespace="registry")
        self.assertEqual((len(bindings), len(nodes)), (125, 22))
        node_pairs = tuple(
            (row["ability_template_id"], row["node_key"])
            for row in nodes
        )
        self.assertEqual(len(node_pairs), len(set(node_pairs)))
        guard = root.arguments[0]
        guard_results = tuple(
            definition.evaluate_validation_expression(
                guard,
                {
                    name: row[name]
                    for name in definition._outer_identifier_names(guard)
                },
            )
            for row in bindings
        )
        self.assertEqual(
            (guard_results.count(False), guard_results.count(True)),
            (109, 16),
        )

        original = definition._resolve_composite_record_lookup
        evidence = []

        def observe(domain, values):
            resolved = original(domain, values)
            evidence.append((values, resolved))
            return resolved

        try:
            definition._resolve_composite_record_lookup = observe
            result = execution.execute_definition_invariant_rule(rule, context)
        finally:
            definition._resolve_composite_record_lookup = original
        reverse_result = execution.execute_definition_invariant_rule(
            reverse_catalog.get(target_rule_id), reverse_context
        )
        self.assertEqual(result, reverse_result)
        self.assertIs(result.outcome, execution.ValidationOutcome.PASS)
        self.assertEqual(
            (result.evaluated_record_count, result.violation_count),
            (125, 0),
        )
        self.assertEqual(result.diagnostics, ())
        self.assertEqual(len(evidence), 16)
        self.assertTrue(all(
            resolved.state == "EXACT" and resolved.value is not None
            for _, resolved in evidence
        ))
        self.assertTrue(all(
            values in node_pairs for values, _ in evidence
        ))

    def test_component_schema_version_failures_are_controlled(self):
        cases = (
            (
                execution.ValidationDataContext(
                    namespaced_tables={"registry": {}}
                ),
                "CARDDATABASE",
                "component_metadata_missing",
            ),
            (
                execution.ValidationDataContext(
                    namespaced_tables={
                        "registry": {
                            "meta": (
                                {
                                    "key": "export_directory_name",
                                    "value": "REGISTRY",
                                },
                                {"key": "schema_version", "value": "0.5.1"},
                            )
                        }
                    }
                ),
                "CARDDATABASE",
                "component_unknown",
            ),
            (
                execution.ValidationDataContext(
                    namespaced_tables={
                        "carddatabase": {
                            "meta": (
                                {
                                    "key": "export_directory_name",
                                    "value": "CARDDATABASE",
                                },
                            )
                        }
                    }
                ),
                "CARDDATABASE",
                "component_schema_version_missing",
            ),
        )
        for context, component_id, reason in cases:
            with self.subTest(reason=reason):
                with self.assertRaises(
                    definition.ValidationExpressionEvaluationError
                ) as raised:
                    definition._resolve_component_schema_version(
                        context, component_id
                    )
                self.assertEqual(
                    dict(raised.exception.context),
                    {
                        "builtin": "current_schema_version",
                        "node_type": "Call",
                        "reason": reason,
                    },
                )

    def test_d1_compound_cohort_is_closed_with_exact_current_findings(self):
        catalog, context = execution_tests.current_corpus_catalog_and_context()
        cohort_ids = (
            set(self.D1B_RESULTS)
            | set(self.D1C_RESULTS)
            | set(self.D1D_RESULTS)
            | set(self.D1E_RESULTS)
        )
        self.assertEqual(len(cohort_ids), 31)
        results = tuple(
            execution.execute_definition_invariant_rule(
                catalog.get(rule_id), context
            )
            for rule_id in sorted(cohort_ids)
        )
        self.assertEqual(
            Counter(result.outcome for result in results),
            {
                execution.ValidationOutcome.PASS: 31,
            },
        )
        self.assertEqual(
            {
                result.rule_id
                for result in results
                if result.outcome is execution.ValidationOutcome.FAIL
            },
            set(),
        )
        self.assertEqual(sum(result.violation_count for result in results), 0)

    def test_corrected_auto_mapping_is_now_a_clean_pass(self):
        catalog, context = execution_tests.current_corpus_catalog_and_context()
        result = execution.execute_definition_invariant_rule(
            catalog.get("val_migration_map_auto_mapping_resolved"),
            context,
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.PASS)
        self.assertEqual(
            (result.evaluated_record_count, result.violation_count), (85, 0)
        )
        self.assertEqual(result.diagnostics, ())

    def test_b2_shape_inventory_and_current_guard_counts_are_exact(self):
        catalog, context = execution_tests.current_corpus_catalog_and_context()
        identifier_occurrences = 0
        guard_operators = set()
        constraint_operators = set()
        for rule_id, expected in sorted(self.B2_RESULTS.items()):
            rule = catalog.get(rule_id)
            root = rule.condition_ast
            self.assertIsInstance(root, validation.Call)
            self.assertEqual(root.function, "when")
            self.assertEqual(len(root.arguments), 2)
            guard, constraint = root.arguments
            self.assertFalse(
                any(isinstance(node, validation.Call) for node in self._walk(guard))
            )
            self.assertIsInstance(constraint, validation.BinaryOperation)
            self.assertIn(constraint.operator, {"==", "!="})
            guard_operators.update(
                node.operator
                for node in self._walk(guard)
                if isinstance(node, validation.BinaryOperation)
            )
            constraint_operators.add(constraint.operator)
            self.assertTrue(
                all(
                    isinstance(operand, (validation.Identifier, validation.Literal))
                    for operand in (constraint.left, constraint.right)
                )
            )

            namespace = context.namespace_for_component(rule.component_identity)
            records = context.table(rule.target_table_id, namespace=namespace)
            identifiers = tuple(sorted(set(rule.free_identifiers)))
            guard_results = tuple(
                definition.evaluate_validation_expression(
                    guard, {name: record[name] for name in identifiers}
                )
                for record in records
            )
            table_id, record_count, guard_false, guard_true = expected
            self.assertEqual(rule.target_table_id, table_id)
            self.assertEqual(len(records), record_count)
            self.assertEqual(guard_results.count(False), guard_false)
            self.assertEqual(guard_results.count(True), guard_true)
            identifier_occurrences += sum(
                isinstance(node, validation.Identifier)
                for node in self._walk(root)
            )
        self.assertEqual(identifier_occurrences, 21)
        self.assertEqual(guard_operators, {"==", "!="})
        self.assertEqual(constraint_operators, {"==", "!="})

    def test_b3_shape_inventory_execution_and_lookup_counts_are_exact(self):
        catalog, context = execution_tests.current_corpus_catalog_and_context()
        definitions = tuple(
            rule
            for rule in catalog.by_stage("pre_export")
            if rule.validation_kind_id == "definition_invariant"
        )
        cohort = tuple(
            rule
            for rule in definitions
            if definition._lookup_nodes(rule.condition_ast)
            and definition._ast_unsupported_reason(rule.condition_ast) is None
            and not definition._call_nodes(rule.condition_ast, "count")
            and not any(
                isinstance(node, validation.Binding)
                for node in self._walk(rule.condition_ast)
            )
        )
        self.assertEqual(len(cohort), 27)
        self.assertEqual({rule.rule_id for rule in cohort}, set(self.B3_RESULTS))

        lookup_nodes = tuple(
            lookup
            for rule in cohort
            for lookup in definition._lookup_nodes(rule.condition_ast)
        )
        self.assertEqual(len(lookup_nodes), 44)
        self.assertEqual(
            Counter(type(lookup.arguments[2]).__name__ for lookup in lookup_nodes),
            {"Identifier": 39, "Call": 5},
        )

        original = definition._resolve_scalar_lookup
        total_calls = 0
        total_zero = 0
        total_ambiguous = 0
        for rule in cohort:
            namespace = context.namespace_for_component(rule.component_identity)
            records = context.table(rule.target_table_id, namespace=namespace)
            domains = definition._prepare_lookup_domains(
                rule.condition_ast, context, namespace
            )
            resolver = lambda table, key, value, output: original(
                domains[(table, key, output)], value
            ).value
            guard_false = 0
            if (
                isinstance(rule.condition_ast, validation.Call)
                and rule.condition_ast.function == "when"
            ):
                guard = rule.condition_ast.arguments[0]
                for record in records:
                    environment = {
                        name: record[name] for name in rule.free_identifiers
                    }
                    if not definition.evaluate_validation_expression(
                        guard,
                        environment,
                        lookup_resolver=resolver,
                    ):
                        guard_false += 1

            evidence = {"calls": 0, "zero": 0, "ambiguous": 0}

            def observe(domain, key):
                evidence["calls"] += 1
                try:
                    resolved = original(domain, key)
                except definition._ScalarLookupFailure as error:
                    if error.reason == "lookup_ambiguous":
                        evidence["ambiguous"] += 1
                    raise
                if resolved.state == "ZERO":
                    evidence["zero"] += 1
                return resolved

            try:
                definition._resolve_scalar_lookup = observe
                result = execution.execute_definition_invariant_rule(rule, context)
            finally:
                definition._resolve_scalar_lookup = original

            table_id, record_count, expected_guard_false, lookup_calls = (
                self.B3_RESULTS[rule.rule_id]
            )
            with self.subTest(rule=rule.rule_id):
                self.assertEqual(rule.target_table_id, table_id)
                self.assertEqual(len(records), record_count)
                self.assertEqual(guard_false, expected_guard_false)
                self.assertEqual(evidence["calls"], lookup_calls)
                self.assertEqual(evidence["zero"], 0)
                self.assertEqual(evidence["ambiguous"], 0)
                self.assertIs(result.outcome, execution.ValidationOutcome.PASS)
                self.assertEqual(result.violation_count, 0)
            total_calls += evidence["calls"]
            total_zero += evidence["zero"]
            total_ambiguous += evidence["ambiguous"]

        self.assertEqual(total_calls, 171)
        self.assertEqual(total_zero, 0)
        self.assertEqual(total_ambiguous, 0)

    def test_advanced_lookup_candidate_support_status_is_exact(self):
        catalog, context = execution_tests.current_corpus_catalog_and_context()
        target_rule_id = "val_ability_template_bindings_generated_node"
        candidates = tuple(
            rule
            for rule in catalog.by_stage("pre_export")
            if rule.validation_kind_id == "definition_invariant"
            and rule.blocking
            and "lookup(" in rule.condition_expression_source
        )
        self.assertEqual(len(candidates), 33)
        self.assertEqual(
            {rule.rule_id for rule in candidates},
            set(self.B3_RESULTS)
            | set(self.D2C_RESULTS)
            | {"cdb_val_effects_duration_supported"}
            | {"cdb_val_effect_parameter_value_contract"}
            | set(self.D2H_RESULTS)
            | {target_rule_id},
        )
        rule = catalog.get(target_rule_id)
        self.assertIsNone(
            definition._ast_unsupported_reason(rule.condition_ast)
        )
        result = execution.execute_definition_invariant_rule(rule, context)
        self.assertIs(result.outcome, execution.ValidationOutcome.PASS)
        self.assertEqual(
            (result.evaluated_record_count, result.violation_count),
            (125, 0),
        )
        self.assertEqual(result.diagnostics, ())

    @classmethod
    def _walk(cls, node):
        yield node
        for attribute in ("operand", "left", "right", "target"):
            child = getattr(node, attribute, None)
            if child is not None:
                yield from cls._walk(child)
        if isinstance(node, validation.Binding):
            yield from cls._walk(node.value)
        for child in getattr(node, "items", ()):
            yield from cls._walk(child)
        for child in getattr(node, "arguments", ()):
            yield from cls._walk(child)
        for child in getattr(node, "statements", ()):
            yield from cls._walk(child)


if __name__ == "__main__":
    unittest.main()
