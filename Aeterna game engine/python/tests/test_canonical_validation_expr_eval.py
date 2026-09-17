import sys
import unittest
from pathlib import Path
from types import MappingProxyType

import test_canonical_validation_execution as execution_tests


PYTHON_ROOT = Path(__file__).resolve().parents[1]
MODULE_DIRECTORY = PYTHON_ROOT / "tools" / "canonical_export"
EVALUATOR_PATH = MODULE_DIRECTORY / "canonical_validation_expr_eval.py"

validation = execution_tests.validation_expr
# Share the evaluator already loaded by the execution harness so its exception
# classes retain the same identity in executor and evaluator tests.
evaluator = sys.modules["canonical_validation_expr_eval"]


def literal(kind, value):
    return validation.Literal(kind, value)


def frozen_record(**values):
    return MappingProxyType(dict(values))


def parse(source):
    return validation.parse_validation_expression(source)


def evaluate(
    source_or_ast,
    identifiers=None,
    *,
    lookup_resolver=None,
    exists_resolver=None,
    value_of_resolver=None,
    primary_key_resolver=None,
    record_lookup_resolver=None,
    record_lookup_by_resolver=None,
    schema_version_resolver=None,
    table_resolver=None,
    registry_group_resolver=None,
):
    ast = parse(source_or_ast) if isinstance(source_or_ast, str) else source_or_ast
    return evaluator.evaluate_validation_expression(
        ast,
        identifiers or {},
        lookup_resolver=lookup_resolver,
        exists_resolver=exists_resolver,
        value_of_resolver=value_of_resolver,
        primary_key_resolver=primary_key_resolver,
        record_lookup_resolver=record_lookup_resolver,
        record_lookup_by_resolver=record_lookup_by_resolver,
        schema_version_resolver=schema_version_resolver,
        table_resolver=table_resolver,
        registry_group_resolver=registry_group_resolver,
    )


class EvaluatorTestCase(unittest.TestCase):
    def assert_evaluation_error(self, ast, identifiers=None, **expected):
        with self.assertRaises(
            evaluator.ValidationExpressionEvaluationError
        ) as raised:
            evaluate(ast, identifiers)
        self.assertNotIsInstance(
            raised.exception, evaluator.ValidationExpressionUnsupportedError
        )
        context = dict(raised.exception.context)
        for key, value in expected.items():
            self.assertEqual(context.get(key), value)
        return raised.exception

    def assert_unsupported(self, ast, **expected):
        with self.assertRaises(
            evaluator.ValidationExpressionUnsupportedError
        ) as raised:
            evaluate(ast)
        context = dict(raised.exception.context)
        for key, value in expected.items():
            self.assertEqual(context.get(key), value)
        return raised.exception


class TestLiteralAndIdentifier(EvaluatorTestCase):
    def test_canonical_literals(self):
        cases = (
            (literal("null", None), None),
            (literal("boolean", True), True),
            (literal("boolean", False), False),
            (literal("integer", 17), 17),
            (literal("string", "Őrző"), "Őrző"),
        )
        for ast, expected in cases:
            with self.subTest(ast=ast):
                self.assertEqual(evaluate(ast), expected)

    def test_identifier_found(self):
        self.assertEqual(evaluate(validation.Identifier("count"), {"count": 3}), 3)

    def test_identifier_missing_is_explicit(self):
        self.assert_evaluation_error(
            validation.Identifier("missing"),
            node_type="Identifier",
            identifier="missing",
            reason="identifier_missing",
        )

    def test_float_identifier_value_is_rejected_without_coercion(self):
        self.assert_evaluation_error(
            validation.Identifier("value"),
            {"value": 1.0},
            identifier="value",
            reason="identifier_value_type_unsupported",
        )

    def test_invalid_literal_runtime_type_is_rejected(self):
        self.assert_evaluation_error(
            literal("integer", 1.0),
            node_type="Literal",
            reason="literal_kind_or_value_invalid",
        )

    def test_environment_is_copied_and_not_modified(self):
        identifiers = {"first": 1, "second": "two"}
        before = dict(identifiers)
        self.assertEqual(evaluate(validation.Identifier("first"), identifiers), 1)
        self.assertEqual(identifiers, before)

    def test_environment_insertion_order_does_not_affect_result(self):
        ast = parse("first == 1 and second == 2")
        first = evaluator.evaluate_validation_expression(
            ast, {"first": 1, "second": 2}
        )
        second = evaluator.evaluate_validation_expression(
            ast, {"second": 2, "first": 1}
        )
        self.assertIs(first, True)
        self.assertEqual(first, second)


class TestExactEqualityAndLists(EvaluatorTestCase):
    def test_scalar_equality_is_type_aware(self):
        cases = (
            (None, None, True),
            (1, 1, True),
            (True, True, True),
            ("A", "A", True),
            (1, 2, False),
            (True, 1, False),
            (False, 0, False),
            ("1", 1, False),
            ("A", "a", False),
        )
        ast = validation.BinaryOperation(
            "==", validation.Identifier("left"), validation.Identifier("right")
        )
        for left, right, expected in cases:
            with self.subTest(left=left, right=right):
                self.assertIs(evaluate(ast, {"left": left, "right": right}), expected)

    def test_not_equal_is_exact_negation_of_typed_equality(self):
        self.assertIs(evaluate("left != right", {"left": True, "right": 1}), True)
        self.assertIs(evaluate("left != right", {"left": "A", "right": "A"}), False)

    def test_list_literal_returns_immutable_evaluator_value(self):
        self.assertEqual(evaluate('[1,true,"A",null]'), (1, True, "A", None))

    def test_list_equality_is_recursive_and_type_aware(self):
        self.assertIs(evaluate("[1,[true]] == [1,[true]]"), True)
        self.assertIs(evaluate("[1,[true]] == [1,[1]]"), False)
        self.assertIs(evaluate("[1] == [1,1]"), False)

    def test_nested_unsupported_list_item_is_rejected(self):
        ast = validation.ListLiteral((validation.MapLiteral((("a", "b"),)),))
        self.assert_unsupported(ast, node_type="MapLiteral")


class TestMembership(EvaluatorTestCase):
    def test_scalar_membership(self):
        self.assertIs(evaluate('value in ["A","B"]', {"value": "B"}), True)
        self.assertIs(evaluate('value in ["A","B"]', {"value": "C"}), False)

    def test_membership_avoids_bool_int_collision(self):
        self.assertIs(evaluate("value in [true]", {"value": 1}), False)
        self.assertIs(evaluate("value in [1]", {"value": True}), False)

    def test_membership_is_case_sensitive(self):
        self.assertIs(evaluate('value in ["A"]', {"value": "A"}), True)
        self.assertIs(evaluate('value in ["a"]', {"value": "A"}), False)

    def test_membership_requires_list_right_operand(self):
        self.assert_evaluation_error(
            parse("value in other"),
            {"value": 1, "other": 1},
            operator="in",
            reason="list_right_operand_required",
        )

    def test_negated_membership_is_exact_typed_negation(self):
        cases = (
            ('value not in ["a","b"]', {"value": "x"}, True),
            ('value not in ["a","b"]', {"value": "a"}, False),
            ('value not in [null,"#TBD"]', {"value": None}, False),
            ('value not in [null,"#TBD"]', {"value": "x"}, True),
            ("value not in [1]", {"value": True}, True),
            ("value not in [true]", {"value": 1}, True),
            ('value not in ["a"]', {"value": "A"}, True),
            ('value not in ["A"]', {"value": "A"}, False),
        )
        for expression, environment, expected in cases:
            with self.subTest(expression=expression, environment=environment):
                self.assertIs(evaluate(expression, environment), expected)

    def test_negated_membership_requires_list_right_operand(self):
        self.assert_evaluation_error(
            parse("value not in other"),
            {"value": 1, "other": 1},
            operator="not in",
            reason="list_right_operand_required",
        )

    def test_membership_and_negation_are_order_independent(self):
        environment = {"value": "B"}
        self.assertIs(evaluate('value in ["A","B"]', environment), True)
        self.assertIs(evaluate('value in ["B","A"]', environment), True)
        self.assertIs(
            evaluate('value not in ["A","B"]', environment), False
        )
        self.assertIs(
            evaluate('value not in ["B","A"]', environment), False
        )


class TestBooleanAndShortCircuit(EvaluatorTestCase):
    def test_exact_boolean_operators(self):
        self.assertIs(evaluate("true and false"), False)
        self.assertIs(evaluate("false or true"), True)
        self.assertIs(evaluate("not false"), True)

    def test_non_boolean_operands_are_rejected(self):
        for ast in (
            validation.BinaryOperation("and", literal("integer", 1), literal("boolean", True)),
            validation.BinaryOperation("or", literal("string", ""), literal("boolean", False)),
            validation.UnaryOperation("not", literal("integer", 0)),
        ):
            with self.subTest(ast=ast):
                self.assert_evaluation_error(ast, reason="boolean_operand_required")

    def test_false_and_does_not_evaluate_missing_right(self):
        ast = validation.BinaryOperation(
            "and", literal("boolean", False), validation.Identifier("missing")
        )
        self.assertIs(evaluate(ast), False)

    def test_true_or_does_not_evaluate_unsupported_right(self):
        ast = validation.BinaryOperation(
            "or", literal("boolean", True), validation.TbdLiteral()
        )
        self.assertIs(evaluate(ast), True)

    def test_required_boolean_branch_is_evaluated(self):
        with self.assertRaises(evaluator.ValidationExpressionEvaluationError):
            evaluate("true and missing")
        with self.assertRaises(evaluator.ValidationExpressionEvaluationError):
            evaluate("false or missing")


class TestIntegerComparison(EvaluatorTestCase):
    def test_integer_greater_than_or_equal(self):
        self.assertIs(evaluate("value >= 1", {"value": 1}), True)
        self.assertIs(evaluate("value >= 1", {"value": 0}), False)

    def test_bool_is_not_an_integer_operand(self):
        self.assert_evaluation_error(
            parse("value >= 1"),
            {"value": True},
            operator=">=",
            reason="integer_operands_required",
        )

    def test_string_comparison_is_rejected(self):
        self.assert_evaluation_error(
            parse('value >= "A"'),
            {"value": "B"},
            operator=">=",
            reason="integer_operands_required",
        )

    def test_integer_greater_than_is_strict(self):
        self.assertIs(evaluate("2 > 1"), True)
        self.assertIs(evaluate("1 > 2"), False)
        self.assertIs(evaluate("1 > 1"), False)

    def test_greater_than_rejects_bool_string_and_null_without_coercion(self):
        for value in (True, "2", None):
            with self.subTest(value=value):
                self.assert_evaluation_error(
                    parse("value > 1"),
                    {"value": value},
                    operator=">",
                    reason="integer_operands_required",
                )


class TestCollectionCardinality(EvaluatorTestCase):
    def test_count_non_null_uses_exact_none_semantics(self):
        cases = (
            ("count_non_null([])", 0),
            ("count_non_null([null,null])", 0),
            ('count_non_null([null,"x"])', 1),
            ('count_non_null([false,0,"",null])', 3),
            ('count_non_null([false,0,"",[],null])', 4),
        )
        for expression, expected in cases:
            with self.subTest(expression=expression):
                result = evaluate(expression)
                self.assertIs(type(result), int)
                self.assertEqual(result, expected)
        self.assertIs(evaluate("count_non_null([]) == 0"), True)

    def test_boolean_cardinality_empty_and_boundary_semantics(self):
        cases = (
            ("at_least_one_non_null([])", False),
            ("at_least_one_non_null([null])", False),
            ("at_least_one_non_null([null,0])", True),
            ("at_most_one_non_null([])", True),
            ('at_most_one_non_null([null,"x"])', True),
            ('at_most_one_non_null(["x",0])', False),
        )
        for expression, expected in cases:
            with self.subTest(expression=expression):
                result = evaluate(expression)
                self.assertIs(type(result), bool)
                self.assertIs(result, expected)

    def test_only_evaluated_list_literal_tuple_is_accepted(self):
        for expression in (
            'count_non_null("value")',
            "at_least_one_non_null(0)",
            "at_most_one_non_null(null)",
        ):
            with self.subTest(expression=expression):
                self.assert_evaluation_error(
                    parse(expression),
                    builtin=parse(expression).function,
                    reason="collection_argument_required",
                )

        class ArbitraryIterable:
            def __iter__(self):
                return iter((None, "value"))

        for value in ([], {}, set(), (None,), ArbitraryIterable()):
            with self.subTest(value_type=type(value).__name__):
                self.assert_evaluation_error(
                    parse("count_non_null(collection)"),
                    {"collection": value},
                    identifier="collection",
                    reason="identifier_value_type_unsupported",
                )

    def test_wrong_arity_is_statically_unsupported(self):
        empty = validation.ListLiteral(())
        for ast in (
            validation.Call("count_non_null", ()),
            validation.Call("at_least_one_non_null", (empty, empty)),
            validation.Call("at_most_one_non_null", (empty, empty)),
        ):
            with self.subTest(builtin=ast.function):
                self.assert_unsupported(
                    ast,
                    builtin=ast.function,
                    reason="builtin_arity_not_supported",
                )

    def test_missing_identifier_remains_a_controlled_error(self):
        self.assert_evaluation_error(
            parse("count_non_null([missing])"),
            identifier="missing",
            reason="identifier_missing",
        )

    def test_cardinality_is_deterministic_and_does_not_mutate_environment(self):
        identifiers = {"first": None, "second": "value"}
        before = dict(identifiers)
        ast = parse("count_non_null([first,second])")
        first = evaluate(ast, identifiers)
        second = evaluate(ast, dict(reversed(tuple(identifiers.items()))))
        self.assertEqual((first, second), (1, 1))
        self.assertEqual(identifiers, before)


class TestWhen(EvaluatorTestCase):
    def test_true_guard_returns_boolean_constraint(self):
        self.assertIs(evaluate("when(true,true)"), True)
        self.assertIs(evaluate("when(true,false)"), False)

    def test_false_guard_is_true_and_skips_missing_constraint(self):
        self.assertIs(evaluate("when(false,missing)"), True)

    def test_false_guard_skips_unsupported_constraint(self):
        ast = validation.Call(
            "when", (literal("boolean", False), validation.MapLiteral(()))
        )
        self.assertIs(evaluate(ast), True)

    def test_non_boolean_condition_is_rejected(self):
        self.assert_evaluation_error(
            parse("when(1,true)"), builtin="when", reason="boolean_operand_required"
        )

    def test_non_boolean_constraint_is_rejected_when_guard_is_true(self):
        self.assert_evaluation_error(
            parse("when(true,1)"), builtin="when", reason="boolean_operand_required"
        )

    def test_bad_arity_is_unsupported(self):
        for arguments in ((), (literal("boolean", True),)):
            with self.subTest(arguments=arguments):
                self.assert_unsupported(
                    validation.Call("when", arguments),
                    builtin="when",
                    reason="builtin_arity_not_supported",
                )


class TestSequenceConjunction(EvaluatorTestCase):
    def test_two_true_predicates_are_true(self):
        self.assertIs(evaluate("true; true"), True)

    def test_true_then_false_is_false(self):
        self.assertIs(evaluate("true; false"), False)

    def test_false_statement_short_circuits_remaining_sequence(self):
        ast = validation.Sequence((
            literal("boolean", False),
            validation.Identifier("missing"),
        ))
        self.assertIs(evaluate(ast), False)

    def test_multiple_when_predicates_are_conjoined_in_source_order(self):
        self.assertIs(
            evaluate("when(true,true); when(false,missing); when(true,true)"),
            True,
        )
        self.assertIs(
            evaluate("when(true,true); when(true,false); when(true,missing)"),
            False,
        )

    def test_nullable_values_keep_existing_exact_semantics(self):
        expression = (
            "when(value != null,value >= 1); "
            "when(value == null,true)"
        )
        self.assertIs(evaluate(expression, {"value": None}), True)
        self.assertIs(evaluate(expression, {"value": 2}), True)

    def test_non_boolean_child_is_controlled_evaluation_error(self):
        self.assert_evaluation_error(
            validation.Sequence((
                literal("boolean", True),
                literal("integer", 1),
            )),
            node_type="Sequence",
            reason="boolean_operand_required",
        )

    def test_empty_sequence_fails_closed(self):
        self.assert_evaluation_error(
            validation.Sequence(()),
            node_type="Sequence",
            reason="sequence_must_not_be_empty",
        )


class TestImmutableScalarBinding(EvaluatorTestCase):
    @staticmethod
    def resolver(table, key_field, key_value, output_field):
        rows = {
            ("inner", "inner_id", "alpha", "outer_id"): "outer-1",
            ("outer", "outer_id", "outer-1", "value"): "resolved",
            ("items", "item_id", "item-1", "value"): 7,
        }
        return rows.get((table, key_field, key_value, output_field))

    def test_exact_scalar_literal_values_can_be_bound(self):
        cases = (
            ("null", "bound == null"),
            ("false", "bound == false"),
            ("0", "bound == 0"),
            ('""', 'bound == ""'),
        )
        for literal_source, predicate in cases:
            with self.subTest(literal=literal_source):
                self.assertIs(
                    evaluate(f"bound = {literal_source}; {predicate}"),
                    True,
                )

    def test_multiple_bindings_resolve_left_to_right(self):
        self.assertIs(
            evaluate("first = 1; second = first; second == 1"),
            True,
        )

    def test_scalar_lookup_value_can_be_bound(self):
        self.assertIs(
            evaluate(
                'bound = lookup("items","item_id",item_id,"value"); '
                "bound == 7",
                {"item_id": "item-1"},
                lookup_resolver=self.resolver,
            ),
            True,
        )

    def test_nested_scalar_lookup_is_evaluated_inner_first(self):
        calls = []

        def observe(table, key_field, key_value, output_field):
            calls.append((table, key_field, key_value, output_field))
            return self.resolver(table, key_field, key_value, output_field)

        result = evaluate(
            'bound = lookup("outer","outer_id",'
            'lookup("inner","inner_id",source,"outer_id"),"value"); '
            'bound == "resolved"',
            {"source": "alpha"},
            lookup_resolver=observe,
        )
        self.assertIs(result, True)
        self.assertEqual(
            calls,
            [
                ("inner", "inner_id", "alpha", "outer_id"),
                ("outer", "outer_id", "outer-1", "value"),
            ],
        )

    def test_rebinding_forward_reference_and_missing_identifier_fail_closed(self):
        cases = (
            (
                "x = 1; x = 2; x == 1",
                "Binding",
                "binding_name_already_defined",
            ),
            ("x = y; y = 1; x == y", "Identifier", "identifier_missing"),
            ("x = missing; x == 1", "Identifier", "identifier_missing"),
        )
        for source, node_type, reason in cases:
            with self.subTest(source=source):
                self.assert_evaluation_error(
                    parse(source), node_type=node_type, reason=reason
                )

    def test_source_identifier_collision_is_rejected_without_mutation(self):
        source = {"bound": 9}
        before = dict(source)
        self.assert_evaluation_error(
            parse("bound = 1; bound == 1"),
            source,
            node_type="Binding",
            identifier="bound",
            reason="binding_name_collides_with_source_identifier",
        )
        self.assertEqual(source, before)

    def test_record_collection_and_map_rhs_are_rejected(self):
        record_ast = validation.Sequence((
            validation.Binding("bound", validation.Identifier("record")),
            literal("boolean", True),
        ))
        self.assert_evaluation_error(
            record_ast,
            {"record": {"value": 1}},
            node_type="Identifier",
            reason="identifier_value_type_unsupported",
        )
        self.assert_evaluation_error(
            parse("bound = [1]; true"),
            node_type="Binding",
            reason="binding_value_type_unsupported",
        )
        map_ast = validation.Sequence((
            validation.Binding(
                "bound", validation.MapLiteral((("value", 1),))
            ),
            literal("boolean", True),
        ))
        self.assert_unsupported(map_ast, node_type="MapLiteral")

    def test_binding_has_no_boolean_contribution_and_predicates_require_bool(self):
        self.assertIs(evaluate("bound = false; true"), True)
        self.assert_evaluation_error(
            parse("bound = 1; bound"),
            node_type="Sequence",
            reason="boolean_operand_required",
        )
        self.assert_evaluation_error(
            validation.Sequence((
                validation.Binding("bound", literal("integer", 1)),
            )),
            node_type="Sequence",
            reason="sequence_boolean_statement_required",
        )

    def test_false_predicate_short_circuits_and_locals_do_not_leak(self):
        self.assertIs(evaluate("bound = false; bound; missing"), False)
        source = {"source": 1}
        self.assertIs(evaluate("bound = source; bound == 1", source), True)
        self.assertEqual(source, {"source": 1})
        self.assert_evaluation_error(
            validation.Identifier("bound"),
            source,
            identifier="bound",
            reason="identifier_missing",
        )

    def test_binding_scope_position_and_reserved_name_are_rejected(self):
        self.assert_unsupported(
            validation.Binding("bound", literal("integer", 1)),
            node_type="Binding",
            reason="node_not_allowlisted",
        )
        self.assert_unsupported(
            validation.Sequence((
                literal("boolean", True),
                validation.Binding("bound", literal("integer", 1)),
            )),
            node_type="Binding",
            reason="binding_after_boolean_statement",
        )
        self.assert_unsupported(
            parse("current = 1; current == 1"),
            node_type="Binding",
            identifier="current",
            reason="binding_name_reserved",
        )
        nested = validation.Sequence((
            validation.Binding(
                "outer",
                validation.Sequence((
                    validation.Binding("inner", literal("integer", 1)),
                    literal("boolean", True),
                )),
            ),
            literal("boolean", True),
        ))
        self.assert_unsupported(
            nested,
            node_type="Binding",
            identifier="inner",
            reason="binding_scope_not_allowlisted",
        )


class TestScalarLookup(EvaluatorTestCase):
    EXPRESSION = 'lookup("items","item_id",key,"value")'

    @staticmethod
    def resolver(table, key_field, key_value, output_field):
        if (table, key_field, output_field) != (
            "items", "item_id", "value"
        ):
            raise AssertionError("lookup contract changed")
        return {"alpha": "A", "beta": "B"}.get(key_value)

    def test_lookup_without_resolver_is_unsupported(self):
        with self.assertRaises(
            evaluator.ValidationExpressionUnsupportedError
        ) as raised:
            evaluate(self.EXPRESSION, {"key": "alpha"})
        self.assertEqual(
            dict(raised.exception.context),
            {
                "builtin": "lookup",
                "node_type": "Call",
                "reason": "lookup_resolver_missing",
            },
        )

    def test_lookup_returns_exact_scalar_and_zero_none(self):
        self.assertEqual(
            evaluate(
                self.EXPRESSION,
                {"key": "alpha"},
                lookup_resolver=self.resolver,
            ),
            "A",
        )
        self.assertIsNone(
            evaluate(
                self.EXPRESSION,
                {"key": "missing"},
                lookup_resolver=self.resolver,
            )
        )

    def test_lookup_participates_in_equality_and_membership(self):
        self.assertIs(
            evaluate(
                self.EXPRESSION + ' == "A"',
                {"key": "alpha"},
                lookup_resolver=self.resolver,
            ),
            True,
        )
        self.assertIs(
            evaluate(
                self.EXPRESSION + ' in ["A","B"]',
                {"key": "beta"},
                lookup_resolver=self.resolver,
            ),
            True,
        )

    def test_nested_lookup_result_is_outer_key(self):
        calls = []

        def resolve(table, key_field, key_value, output_field):
            calls.append((table, key_field, key_value, output_field))
            return {
                ("inner", "id", "start", "next_id"): "finish",
                ("outer", "id", "finish", "value"): "done",
            }[(table, key_field, key_value, output_field)]

        result = evaluate(
            'lookup("outer","id",'
            'lookup("inner","id",start,"next_id"),"value")',
            {"start": "start"},
            lookup_resolver=resolve,
        )
        self.assertEqual(result, "done")
        self.assertEqual(
            calls,
            [
                ("inner", "id", "start", "next_id"),
                ("outer", "id", "finish", "value"),
            ],
        )

    def test_short_circuit_never_calls_lookup_resolver(self):
        calls = []

        def resolve(*arguments):
            calls.append(arguments)
            return True

        expressions = (
            ('when(false,lookup("items","item_id",null,"value"))', True),
            ('false and lookup("items","item_id",null,"value")', False),
            ('true or lookup("items","item_id",null,"value")', True),
        )
        for expression, expected in expressions:
            with self.subTest(expression=expression):
                calls.clear()
                self.assertIs(
                    evaluate(expression, lookup_resolver=resolve), expected
                )
                self.assertEqual(calls, [])

    def test_invalid_arity_is_unsupported_with_resolver(self):
        for arguments in ((), (literal("string", "items"),)):
            with self.subTest(arguments=arguments):
                with self.assertRaises(
                    evaluator.ValidationExpressionUnsupportedError
                ) as raised:
                    evaluate(
                        validation.Call("lookup", arguments),
                        lookup_resolver=self.resolver,
                    )
                self.assertEqual(
                    dict(raised.exception.context)["reason"],
                    "builtin_arity_not_supported",
                )

    def test_table_key_and_output_tokens_are_nonempty_string_literals(self):
        valid = (
            literal("string", "items"),
            literal("string", "item_id"),
            literal("string", "alpha"),
            literal("string", "value"),
        )
        cases = (
            (0, validation.Identifier("items")),
            (0, literal("string", "")),
            (1, literal("integer", 1)),
            (3, validation.Identifier("value")),
        )
        for index, invalid in cases:
            with self.subTest(index=index, invalid=invalid):
                arguments = list(valid)
                arguments[index] = invalid
                with self.assertRaises(
                    evaluator.ValidationExpressionUnsupportedError
                ):
                    evaluate(
                        validation.Call("lookup", tuple(arguments)),
                        lookup_resolver=self.resolver,
                    )

    def test_resolver_exception_propagates_unchanged(self):
        class ResolverFailure(RuntimeError):
            pass

        failure = ResolverFailure("evidence")

        def resolve(*_):
            raise failure

        with self.assertRaises(ResolverFailure) as raised:
            evaluate(
                self.EXPRESSION,
                {"key": "alpha"},
                lookup_resolver=resolve,
            )
        self.assertIs(raised.exception, failure)

    def test_environment_and_resolver_state_are_not_mutated(self):
        identifiers = {"key": "alpha"}
        resolver_state = {"alpha": "A"}
        identifiers_before = dict(identifiers)
        resolver_before = dict(resolver_state)

        def resolve(_table, _key, value, _output):
            return resolver_state.get(value)

        self.assertEqual(
            evaluate(
                self.EXPRESSION,
                identifiers,
                lookup_resolver=resolve,
            ),
            "A",
        )
        self.assertEqual(identifiers, identifiers_before)
        self.assertEqual(resolver_state, resolver_before)

    def test_non_scalar_resolver_result_is_rejected(self):
        with self.assertRaises(
            evaluator.ValidationExpressionEvaluationError
        ) as raised:
            evaluate(
                self.EXPRESSION,
                {"key": "alpha"},
                lookup_resolver=lambda *_: ("not", "a", "scalar"),
            )
        self.assertNotIsInstance(
            raised.exception,
            evaluator.ValidationExpressionUnsupportedError,
        )
        self.assertEqual(
            dict(raised.exception.context),
            {
                "builtin": "lookup",
                "node_type": "Call",
                "reason": "lookup_result_type_unsupported",
            },
        )


class TestRecordLookupAndMemberAccess(EvaluatorTestCase):
    LOOKUP = 'lookup_record("items","item_id",key)'

    @staticmethod
    def frozen(**values):
        return MappingProxyType(dict(values))

    def test_zero_is_none_and_one_is_an_immutable_independent_copy(self):
        source = {"item_id": "one", "value": "original"}

        def resolve(_table, _key_field, key):
            return MappingProxyType(source) if key == "one" else None

        zero = evaluate(
            self.LOOKUP,
            {"key": "missing"},
            record_lookup_resolver=resolve,
        )
        record = evaluate(
            self.LOOKUP,
            {"key": "one"},
            record_lookup_resolver=resolve,
        )
        self.assertIsNone(zero)
        self.assertIsInstance(record, MappingProxyType)
        self.assertEqual(dict(record), source)
        with self.assertRaises(TypeError):
            record["value"] = "mutated"
        source["value"] = "changed-after-resolution"
        self.assertEqual(record["value"], "original")

    def test_record_binding_and_exact_scalar_members(self):
        record = self.frozen(
            item_id="one",
            none_value=None,
            bool_value=False,
            int_value=0,
            text_value="",
        )
        resolver = lambda *_: record
        expression = (
            f"row = {self.LOOKUP}; "
            "row != null and row.none_value == null and "
            "row.bool_value == false and row.int_value == 0 and "
            'row.text_value == ""'
        )
        self.assertIs(
            evaluate(
                expression,
                {"key": "one"},
                record_lookup_resolver=resolver,
            ),
            True,
        )

    def test_zero_match_can_be_bound_but_member_access_fails(self):
        resolver = lambda *_: None
        self.assertIs(
            evaluate(
                f"row = {self.LOOKUP}; row == null",
                {"key": "missing"},
                record_lookup_resolver=resolver,
            ),
            True,
        )
        with self.assertRaises(
            evaluator.ValidationExpressionEvaluationError
        ) as raised:
            evaluate(
                f"row = {self.LOOKUP}; row.value == null",
                {"key": "missing"},
                record_lookup_resolver=resolver,
            )
        self.assertEqual(
            dict(raised.exception.context)["reason"],
            "member_access_base_is_none",
        )

    def test_missing_member_none_base_and_scalar_base_are_controlled(self):
        cases = (
            (
                validation.MemberAccess(validation.Identifier("row"), "missing"),
                {"row": self.frozen(value=1)},
                "member_missing",
            ),
            (
                validation.MemberAccess(validation.Identifier("row"), "value"),
                {"row": None},
                "member_access_base_is_none",
            ),
            (
                validation.MemberAccess(validation.Identifier("row"), "value"),
                {"row": "scalar"},
                "member_access_base_not_record",
            ),
        )
        for ast, identifiers, reason in cases:
            with self.subTest(reason=reason):
                self.assert_evaluation_error(
                    ast,
                    identifiers,
                    node_type="MemberAccess",
                    reason=reason,
                )

    def test_chained_record_binding_uses_member_as_later_key(self):
        calls = []
        records = {
            ("first", "first_id", "start"): self.frozen(
                first_id="start", next_id="finish"
            ),
            ("second", "second_id", "finish"): self.frozen(
                second_id="finish", status="active"
            ),
        }

        def resolve(table, key_field, key):
            calls.append((table, key_field, key))
            return records.get((table, key_field, key))

        expression = (
            'first_row = lookup_record("first","first_id",source); '
            'second_row = lookup_record("second","second_id",'
            "first_row.next_id); second_row.status == \"active\""
        )
        self.assertIs(
            evaluate(
                expression,
                {"source": "start"},
                record_lookup_resolver=resolve,
            ),
            True,
        )
        self.assertEqual(
            calls,
            [
                ("first", "first_id", "start"),
                ("second", "second_id", "finish"),
            ],
        )

    def test_false_when_guard_skips_record_lookup(self):
        calls = []
        expression = (
            'when(false,row = lookup_record("items","item_id",key); '
            "row != null)"
        )
        self.assertIs(
            evaluate(
                expression,
                {"key": None},
                record_lookup_resolver=lambda *args: calls.append(args),
            ),
            True,
        )
        self.assertEqual(calls, [])

    def test_when_constraint_binding_scope_does_not_leak(self):
        record = self.frozen(item_id="one")
        ast = validation.Sequence((
            parse(
                'when(true,row = lookup_record("items","item_id",key); '
                "row != null)"
            ),
            validation.BinaryOperation(
                "!=",
                validation.Identifier("row"),
                literal("null", None),
            ),
        ))
        with self.assertRaises(
            evaluator.ValidationExpressionEvaluationError
        ) as raised:
            evaluate(
                ast,
                {"key": "one"},
                record_lookup_resolver=lambda *_: record,
            )
        self.assertNotIsInstance(
            raised.exception,
            evaluator.ValidationExpressionUnsupportedError,
        )
        self.assertEqual(
            dict(raised.exception.context),
            {
                "identifier": "row",
                "node_type": "Identifier",
                "reason": "identifier_missing",
            },
        )
        self.assertEqual(record["item_id"], "one")

    def test_record_locals_do_not_leak_between_evaluations(self):
        record = self.frozen(item_id="one")
        expression = f"row = {self.LOOKUP}; row.item_id == key"
        source = {"key": "one"}
        self.assertIs(
            evaluate(
                expression,
                source,
                record_lookup_resolver=lambda *_: record,
            ),
            True,
        )
        self.assertEqual(source, {"key": "one"})
        self.assert_evaluation_error(
            validation.Identifier("row"),
            source,
            identifier="row",
            reason="identifier_missing",
        )

    def test_record_rebind_source_collision_and_reserved_name_are_rejected(self):
        record = self.frozen(item_id="one")
        resolver = lambda *_: record
        cases = (
            (
                f"row = {self.LOOKUP}; row = {self.LOOKUP}; true",
                {"key": "one"},
                "binding_name_already_defined",
            ),
            (
                f"row = {self.LOOKUP}; true",
                {"key": "one", "row": "source"},
                "binding_name_collides_with_source_identifier",
            ),
        )
        for expression, identifiers, reason in cases:
            with self.subTest(reason=reason):
                with self.assertRaises(
                    evaluator.ValidationExpressionEvaluationError
                ) as raised:
                    evaluate(
                        expression,
                        identifiers,
                        record_lookup_resolver=resolver,
                    )
                self.assertEqual(dict(raised.exception.context)["reason"], reason)
        with self.assertRaises(
            evaluator.ValidationExpressionUnsupportedError
        ) as raised:
            evaluate(
                f"current = {self.LOOKUP}; true",
                {"key": "one"},
                record_lookup_resolver=resolver,
            )
        self.assertEqual(
            dict(raised.exception.context)["reason"],
            "binding_name_reserved",
        )

    def test_invalid_record_result_is_rejected(self):
        with self.assertRaises(
            evaluator.ValidationExpressionEvaluationError
        ) as raised:
            evaluate(
                self.LOOKUP,
                {"key": "one"},
                record_lookup_resolver=lambda *_: {"item_id": "one"},
            )
        self.assertEqual(
            dict(raised.exception.context)["reason"],
            "lookup_record_result_type_unsupported",
        )


class TestCompositeRecordLookup(EvaluatorTestCase):
    EXPRESSION = (
        'lookup_record_by("items",["kind","index"],[kind,index])'
    )

    def test_zero_one_and_immutable_independent_result(self):
        source = {"item_id": "item-1", "kind": "alpha", "index": 2}
        calls = []

        def resolve(table, fields, values):
            calls.append((table, fields, values))
            return MappingProxyType(source) if values == ("alpha", 2) else None

        self.assertIsNone(evaluate(
            self.EXPRESSION,
            {"kind": "missing", "index": 2},
            record_lookup_by_resolver=resolve,
        ))
        record = evaluate(
            self.EXPRESSION,
            {"kind": "alpha", "index": 2},
            record_lookup_by_resolver=resolve,
        )
        self.assertIsInstance(record, MappingProxyType)
        self.assertEqual(dict(record), source)
        with self.assertRaises(TypeError):
            record["kind"] = "changed"
        source["kind"] = "changed-after-resolution"
        self.assertEqual(record["kind"], "alpha")
        self.assertEqual(
            calls,
            [
                ("items", ("kind", "index"), ("missing", 2)),
                ("items", ("kind", "index"), ("alpha", 2)),
            ],
        )

    def test_single_and_three_field_lists_are_forwarded_exactly(self):
        calls = []
        resolver = lambda *args: calls.append(args)
        self.assertIsNone(evaluate(
            'lookup_record_by("items",["kind"],[kind])',
            {"kind": True},
            record_lookup_by_resolver=resolver,
        ))
        self.assertIsNone(evaluate(
            'lookup_record_by("other:items",["a","b","c"],[a,b,c])',
            {"a": "x", "b": 1, "c": False},
            record_lookup_by_resolver=resolver,
        ))
        self.assertEqual(
            calls,
            [
                ("items", ("kind",), (True,)),
                ("other:items", ("a", "b", "c"), ("x", 1, False)),
            ],
        )

    def test_false_when_guard_skips_composite_lookup(self):
        calls = []
        self.assertIs(
            evaluate(
                'when(false,row = lookup_record_by("items",["kind"],'
                "[missing]); row != null)",
                record_lookup_by_resolver=lambda *args: calls.append(args),
            ),
            True,
        )
        self.assertEqual(calls, [])

    def test_malformed_field_and_value_collections_fail_closed(self):
        cases = (
            (
                'lookup_record_by("items",[],[])',
                "lookup_record_by_key_fields_empty",
            ),
            (
                'lookup_record_by("items",["kind","kind"],[1,1])',
                "lookup_record_by_key_field_duplicate",
            ),
            (
                'lookup_record_by("items",[null],[1])',
                "lookup_record_by_key_field_invalid",
            ),
            (
                'lookup_record_by("items",[1],[1])',
                "lookup_record_by_key_field_invalid",
            ),
            (
                'lookup_record_by("items",["kind"],[])',
                "lookup_record_by_key_arity_mismatch",
            ),
            (
                'lookup_record_by("items",["kind"],[null])',
                "lookup_record_by_null_key_value",
            ),
            (
                'lookup_record_by("items",["kind"],[[1]])',
                "lookup_record_by_key_value_type_unsupported",
            ),
        )
        for expression, reason in cases:
            with self.subTest(reason=reason):
                with self.assertRaises(
                    evaluator.ValidationExpressionEvaluationError
                ) as raised:
                    evaluate(
                        expression,
                        record_lookup_by_resolver=lambda *_: None,
                    )
                self.assertNotIsInstance(
                    raised.exception,
                    evaluator.ValidationExpressionUnsupportedError,
                )
                self.assertEqual(
                    dict(raised.exception.context)["reason"], reason
                )

    def test_missing_resolver_bad_arity_and_bad_result_are_controlled(self):
        with self.assertRaises(
            evaluator.ValidationExpressionUnsupportedError
        ) as missing:
            evaluate(
                'lookup_record_by("items",["kind"],["alpha"])'
            )
        self.assertEqual(
            dict(missing.exception.context)["reason"],
            "record_lookup_by_resolver_missing",
        )
        with self.assertRaises(
            evaluator.ValidationExpressionUnsupportedError
        ) as arity:
            evaluate(
                validation.Call(
                    "lookup_record_by",
                    (
                        literal("string", "items"),
                        validation.ListLiteral((literal("string", "kind"),)),
                    ),
                ),
                record_lookup_by_resolver=lambda *_: None,
            )
        self.assertEqual(
            dict(arity.exception.context)["reason"],
            "builtin_arity_not_supported",
        )
        with self.assertRaises(
            evaluator.ValidationExpressionEvaluationError
        ) as bad_result:
            evaluate(
                'lookup_record_by("items",["kind"],["alpha"])',
                record_lookup_by_resolver=lambda *_: {"item_id": "one"},
            )
        self.assertEqual(
            dict(bad_result.exception.context)["reason"],
            "lookup_record_by_result_type_unsupported",
        )


class TestPureDomainPrimitives(EvaluatorTestCase):
    def test_normalize_exact_preserves_every_character(self):
        vectors = (
            "aeterna",
            "UPPERCASE",
            "  padded\t",
            "punctuation-!?.,",
            "\u0150rz\u0151 \u00c1rv\u00edzt\u0171r\u0151",
            "",
        )
        for source in vectors:
            with self.subTest(source=source):
                self.assertEqual(
                    evaluate(
                        "normalize(value,mode,case_sensitive)",
                        {
                            "value": source,
                            "mode": "exact",
                            "case_sensitive": True,
                        },
                    ),
                    source,
                )
        source = {"value": "  Repeat!  ", "mode": "exact", "case": True}
        expression = "normalize(value,mode,case)"
        self.assertEqual(
            (evaluate(expression, source), evaluate(expression, dict(source))),
            ("  Repeat!  ", "  Repeat!  "),
        )

    def test_normalize_trim_casefold_is_unicode_and_does_not_collapse(self):
        vectors = (
            ("UPPERCASE", "uppercase"),
            ("  padded  ", "padded"),
            ("\tLine\n", "line"),
            ("inner  whitespace", "inner  whitespace"),
            ("  punctuation-!?.,  ", "punctuation-!?.,"),
            ("\u00c1RV\u00cdZT\u0170R\u0150", "\u00e1rv\u00edzt\u0171r\u0151"),
            ("Stra\u00dfe", "strasse"),
            ("", ""),
        )
        for source, expected in vectors:
            with self.subTest(source=source):
                result = evaluate(
                    "normalize(value,mode,case_sensitive)",
                    {
                        "value": source,
                        "mode": "trim_casefold",
                        "case_sensitive": False,
                    },
                )
                self.assertEqual(result, expected)
                self.assertEqual(
                    evaluate(
                        "normalize(value,mode,case_sensitive)",
                        {
                            "case_sensitive": False,
                            "mode": "trim_casefold",
                            "value": source,
                        },
                    ),
                    expected,
                )

    def test_normalize_rejects_invalid_modes_types_and_arity(self):
        invalid = (
            (
                {"value": "x", "mode": "unknown", "case": True},
                "normalize_mode_unknown",
            ),
            (
                {"value": "x", "mode": "exact", "case": False},
                "normalize_mode_case_sensitive_invalid",
            ),
            (
                {"value": "x", "mode": "trim_casefold", "case": True},
                "normalize_mode_case_sensitive_invalid",
            ),
            (
                {"value": None, "mode": "exact", "case": True},
                "normalize_value_type_invalid",
            ),
            (
                {"value": False, "mode": "exact", "case": True},
                "normalize_value_type_invalid",
            ),
            (
                {"value": 1, "mode": "exact", "case": True},
                "normalize_value_type_invalid",
            ),
            (
                {"value": "x", "mode": None, "case": True},
                "normalize_mode_type_invalid",
            ),
            (
                {"value": "x", "mode": 1, "case": True},
                "normalize_mode_type_invalid",
            ),
            (
                {"value": "x", "mode": "exact", "case": 1},
                "normalize_case_sensitive_type_invalid",
            ),
            (
                {"value": "x", "mode": "exact", "case": None},
                "normalize_case_sensitive_type_invalid",
            ),
        )
        expression = "normalize(value,mode,case)"
        for identifiers, reason in invalid:
            with self.subTest(identifiers=identifiers):
                with self.assertRaises(
                    evaluator.ValidationExpressionEvaluationError
                ) as raised:
                    evaluate(expression, identifiers)
                self.assertNotIsInstance(
                    raised.exception,
                    evaluator.ValidationExpressionUnsupportedError,
                )
                self.assertEqual(
                    dict(raised.exception.context)["reason"], reason
                )
        for arguments in (
            (),
            (literal("string", "x"),),
            (
                literal("string", "x"),
                literal("string", "exact"),
            ),
            (
                literal("string", "x"),
                literal("string", "exact"),
                literal("boolean", True),
                literal("string", "extra"),
            ),
        ):
            with self.subTest(arguments=arguments):
                with self.assertRaises(
                    evaluator.ValidationExpressionEvaluationError
                ) as raised:
                    evaluate(validation.Call("normalize", arguments))
                self.assertEqual(
                    dict(raised.exception.context)["reason"],
                    "normalize_arity_invalid",
                )

    def test_normalize_search_name_hu_authoritative_vectors(self):
        vectors = (
            ("aeterna", "aeterna"),
            ("ÁRVÍZTŰRŐ TÜKÖRFÚRÓGÉP", "árvíztűrő tükörfúrógép"),
            ("ÁÉÍÓÖŐÚÜŰ", "áéíóöőúüű"),
            ("  Árnyék  ", "árnyék"),
            ("Több     belső   szó", "több belső szó"),
            ("\tElső\nMásodik\u00a0Harmadik\r\n", "első második harmadik"),
            ("ＡＥＴＥＲＮＡ", "aeterna"),
            ("Árnyék, láng!", "árnyék, láng!"),
            ("Tűz-víz", "tűz-víz"),
            ("", ""),
            (" \t\n\u00a0", ""),
        )
        for source, expected in vectors:
            with self.subTest(source=source):
                result = evaluate(
                    "normalize_search_name_hu(value)", {"value": source}
                )
                self.assertIs(type(result), str)
                self.assertEqual(result, expected)

    def test_normalize_search_name_hu_rejects_non_strings_without_coercion(self):
        invalid = (
            None,
            False,
            1,
            frozen_record(value="name"),
        )
        ast = validation.Call(
            "normalize_search_name_hu", (validation.Identifier("value"),)
        )
        for value in invalid:
            with self.subTest(value=value):
                with self.assertRaises(
                    evaluator.ValidationExpressionEvaluationError
                ) as raised:
                    evaluate(ast, {"value": value})
                self.assertNotIsInstance(
                    raised.exception,
                    evaluator.ValidationExpressionUnsupportedError,
                )
                self.assertEqual(
                    dict(raised.exception.context)["reason"],
                    "normalize_search_name_hu_input_type_invalid",
                )
        with self.assertRaises(
            evaluator.ValidationExpressionEvaluationError
        ) as collection:
            evaluate('normalize_search_name_hu(["name"])')
        self.assertEqual(
            dict(collection.exception.context)["reason"],
            "normalize_search_name_hu_input_type_invalid",
        )

    def test_normalize_search_name_hu_arity_and_determinism_are_explicit(self):
        for arguments in (
            (),
            (literal("string", "one"), literal("string", "two")),
        ):
            with self.subTest(arguments=arguments):
                with self.assertRaises(
                    evaluator.ValidationExpressionEvaluationError
                ) as raised:
                    evaluate(
                        validation.Call(
                            "normalize_search_name_hu", arguments
                        )
                    )
                self.assertEqual(
                    dict(raised.exception.context)["reason"],
                    "normalize_search_name_hu_arity_invalid",
                )
        expression = "normalize_search_name_hu(value)"
        source = {"value": "  ŐRZŐ\t- Jel!  "}
        first = evaluate(expression, source)
        second = evaluate(expression, dict(reversed(tuple(source.items()))))
        self.assertEqual((first, second), ("őrző - jel!", "őrző - jel!"))
        self.assertEqual(source, {"value": "  ŐRZŐ\t- Jel!  "})

    def test_group_of_exact_resolution_zero_and_multiple_groups(self):
        calls = []
        values = {
            "keyword_speed": "keyword",
            "damage_kind_direct": "damage_kind",
        }

        def resolve(registry_value_id):
            calls.append(registry_value_id)
            return values.get(registry_value_id)

        self.assertEqual(
            evaluate(
                "group_of(value)",
                {"value": "keyword_speed"},
                registry_group_resolver=resolve,
            ),
            "keyword",
        )
        self.assertEqual(
            evaluate(
                "group_of(value)",
                {"value": "damage_kind_direct"},
                registry_group_resolver=resolve,
            ),
            "damage_kind",
        )
        self.assertIsNone(
            evaluate(
                "group_of(value)",
                {"value": "unknown_full_id"},
                registry_group_resolver=resolve,
            )
        )
        self.assertEqual(
            calls,
            ["keyword_speed", "damage_kind_direct", "unknown_full_id"],
        )

    def test_group_of_does_not_guess_short_ids_or_resolve_aliases(self):
        values = {"keyword_speed": "keyword"}
        resolver = values.get
        for value in ("speed", "gyorsaság"):
            with self.subTest(value=value):
                self.assertIsNone(
                    evaluate(
                        "group_of(value)",
                        {"value": value},
                        registry_group_resolver=resolver,
                    )
                )

    def test_group_of_rejects_invalid_input_arity_and_result(self):
        invalid = (
            None,
            False,
            1,
            "",
            frozen_record(registry_value_id="keyword_speed"),
        )
        for value in invalid:
            with self.subTest(value=value):
                with self.assertRaises(
                    evaluator.ValidationExpressionEvaluationError
                ) as raised:
                    evaluate(
                        "group_of(value)",
                        {"value": value},
                        registry_group_resolver=lambda _: "keyword",
                    )
                self.assertEqual(
                    dict(raised.exception.context)["reason"],
                    "group_of_registry_value_id_invalid",
                )
        with self.assertRaises(
            evaluator.ValidationExpressionEvaluationError
        ) as collection:
            evaluate(
                'group_of(["keyword_speed"])',
                registry_group_resolver=lambda _: "keyword",
            )
        self.assertEqual(
            dict(collection.exception.context)["reason"],
            "group_of_registry_value_id_invalid",
        )
        for arguments in (
            (),
            (literal("string", "one"), literal("string", "two")),
        ):
            with self.subTest(arguments=arguments):
                with self.assertRaises(
                    evaluator.ValidationExpressionEvaluationError
                ) as raised:
                    evaluate(
                        validation.Call("group_of", arguments),
                        registry_group_resolver=lambda _: None,
                    )
                self.assertEqual(
                    dict(raised.exception.context)["reason"],
                    "group_of_arity_invalid",
                )
        for result in (False, 1, "", frozen_record(group_id="keyword")):
            with self.subTest(result=result):
                with self.assertRaises(
                    evaluator.ValidationExpressionEvaluationError
                ) as raised:
                    evaluate(
                        'group_of("keyword_speed")',
                        registry_group_resolver=lambda _, result=result: result,
                    )
                self.assertEqual(
                    dict(raised.exception.context)["reason"],
                    "group_of_result_invalid",
                )

    def test_group_of_requires_resolver_and_survives_sequence_scope(self):
        with self.assertRaises(
            evaluator.ValidationExpressionUnsupportedError
        ) as missing:
            evaluate('group_of("keyword_speed")')
        self.assertEqual(
            dict(missing.exception.context)["reason"],
            "registry_group_resolver_missing",
        )
        calls = []
        self.assertIs(
            evaluate(
                'expected = "keyword"; group_of(value) == expected',
                {"value": "keyword_speed"},
                registry_group_resolver=lambda value: (
                    calls.append(value) or "keyword"
                ),
            ),
            True,
        )
        self.assertEqual(calls, ["keyword_speed"])


class TestQualifiedReferenceBuiltins(EvaluatorTestCase):
    def test_exists_accepts_runtime_table_and_key_field_values(self):
        calls = []

        def resolve(table_source, key_field, key_value):
            calls.append((table_source, key_field, key_value))
            return table_source == "cards" and key_field == "card_id"

        self.assertIs(
            evaluate(
                "exists(table_source,primary_key_of(table_source),record_id)",
                {
                    "table_source": "cards",
                    "record_id": "IGN-HAM-044",
                },
                exists_resolver=resolve,
                primary_key_resolver=lambda table: (
                    "card_id" if table == "cards" else "unexpected"
                ),
            ),
            True,
        )
        self.assertEqual(calls, [("cards", "card_id", "IGN-HAM-044")])

    def test_value_of_exact_results_and_short_circuit(self):
        calls = []
        values = {
            "event_kind_resolve": "resolve",
            "modifier_kind_add": "add",
        }

        def resolve(registry_value_id):
            calls.append(registry_value_id)
            return values.get(registry_value_id)

        for registry_id, expected in (
            ("event_kind_resolve", "resolve"),
            ("modifier_kind_add", "add"),
            ("unknown", None),
            ("resolve", None),
            ("feloldas", None),
        ):
            with self.subTest(registry_id=registry_id):
                self.assertEqual(
                    evaluate(
                        "value_of(value)",
                        {"value": registry_id},
                        value_of_resolver=resolve,
                    ),
                    expected,
                )
        self.assertIs(
            evaluate(
                "when(false,value_of(value) == null)",
                {"value": "not_evaluated"},
                value_of_resolver=resolve,
            ),
            True,
        )
        self.assertNotIn("not_evaluated", calls)

    def test_primary_key_of_returns_exact_field_name_and_survives_sequence(self):
        calls = []

        def resolve(table_source):
            calls.append(table_source)
            return {
                "cards": "card_id",
                "carddatabase:abilities": "ability_id",
            }[table_source]

        self.assertEqual(
            evaluate(
                "primary_key_of(table_source)",
                {"table_source": "cards"},
                primary_key_resolver=resolve,
            ),
            "card_id",
        )
        self.assertIs(
            evaluate(
                'expected = "ability_id"; '
                "primary_key_of(table_source) == expected",
                {"table_source": "carddatabase:abilities"},
                primary_key_resolver=resolve,
            ),
            True,
        )
        self.assertEqual(calls, ["cards", "carddatabase:abilities"])

    def test_missing_resolvers_are_unsupported(self):
        cases = (
            ('exists("items","item_id","one")', "exists_resolver_missing"),
            ('value_of("group_value")', "value_of_resolver_missing"),
            ('primary_key_of("items")', "primary_key_resolver_missing"),
        )
        for expression, reason in cases:
            with self.subTest(expression=expression):
                with self.assertRaises(
                    evaluator.ValidationExpressionUnsupportedError
                ) as raised:
                    evaluate(expression)
                self.assertEqual(dict(raised.exception.context)["reason"], reason)

    def test_inputs_arity_and_results_fail_closed_without_coercion(self):
        invalid_values = (None, False, 1, "", frozen_record(value="x"))
        for value in invalid_values:
            with self.subTest(builtin="value_of", value=value):
                with self.assertRaises(
                    evaluator.ValidationExpressionEvaluationError
                ) as raised:
                    evaluate(
                        "value_of(value)",
                        {"value": value},
                        value_of_resolver=lambda _: "x",
                    )
                self.assertEqual(
                    dict(raised.exception.context)["reason"],
                    "value_of_registry_value_id_invalid",
                )
            with self.subTest(builtin="primary_key_of", value=value):
                with self.assertRaises(
                    evaluator.ValidationExpressionEvaluationError
                ) as raised:
                    evaluate(
                        "primary_key_of(value)",
                        {"value": value},
                        primary_key_resolver=lambda _: "item_id",
                    )
                self.assertEqual(
                    dict(raised.exception.context)["reason"],
                    "primary_key_table_source_invalid",
                )
        for builtin, resolver_name, resolver, reason in (
            (
                "value_of",
                "value_of_resolver",
                lambda _: False,
                "value_of_result_invalid",
            ),
            (
                "primary_key_of",
                "primary_key_resolver",
                lambda _: 1,
                "primary_key_result_invalid",
            ),
        ):
            with self.subTest(builtin=builtin):
                with self.assertRaises(
                    evaluator.ValidationExpressionEvaluationError
                ) as raised:
                    evaluate(
                        f'{builtin}("value")',
                        **{resolver_name: resolver},
                    )
                self.assertEqual(
                    dict(raised.exception.context)["reason"],
                    reason,
                )
        for builtin, resolver_name, resolver in (
            ("value_of", "value_of_resolver", lambda _: None),
            ("primary_key_of", "primary_key_resolver", lambda _: "id"),
        ):
            for arguments in (
                (),
                (literal("string", "one"), literal("string", "two")),
            ):
                with self.subTest(builtin=builtin, arguments=arguments):
                    with self.assertRaises(
                        evaluator.ValidationExpressionUnsupportedError
                    ) as raised:
                        evaluate(
                            validation.Call(builtin, arguments),
                            **{resolver_name: resolver},
                        )
                    self.assertEqual(
                        dict(raised.exception.context)["reason"],
                        "builtin_arity_not_supported",
                    )


class TestTemplateBindingShape(EvaluatorTestCase):
    EXPRESSION = (
        "template_binding_shape_valid(kind,parameter,source,"
        "[fixed_boolean,fixed_integer,fixed_text,"
        "fixed_registry,fixed_reference])"
    )
    FIXED_NAMES = (
        "fixed_boolean",
        "fixed_integer",
        "fixed_text",
        "fixed_registry",
        "fixed_reference",
    )

    def shape(self, kind, parameter=None, source=None, fixed=None):
        values = dict(zip(self.FIXED_NAMES, fixed or (None,) * 5))
        values.update(kind=kind, parameter=parameter, source=source)
        return evaluate(self.EXPRESSION, values)

    def test_fixed_value_uses_exact_non_null_presence(self):
        populated = (
            (0, True),
            (0, False),
            (1, 1),
            (1, 0),
            (2, "x"),
            (2, ""),
            (3, "registry_value"),
            (4, "reference_value"),
            (0, "deferred_boolean_type_check"),
            (1, False),
            (2, 7),
            (3, 0),
            (4, False),
        )
        for index, value in populated:
            fixed = [None] * 5
            fixed[index] = value
            with self.subTest(index=index, value=value):
                self.assertIs(self.shape("fixed_value", fixed=fixed), True)

        failures = (
            ((None,) * 5, None, None),
            ((True, 1, None, None, None), None, None),
            ((True, 1, "x", "registry", "reference"), None, None),
            ((True, None, None, None, None), "parameter", None),
            ((True, None, None, None, None), None, "source"),
        )
        for fixed, parameter, source in failures:
            with self.subTest(
                fixed=fixed, parameter=parameter, source=source
            ):
                self.assertIs(
                    self.shape(
                        "fixed_value",
                        parameter=parameter,
                        source=source,
                        fixed=fixed,
                    ),
                    False,
                )

    def test_template_parameter_shape(self):
        self.assertIs(
            self.shape("template_parameter", parameter="contract_field"),
            True,
        )
        self.assertIs(
            self.shape("template_parameter", parameter=""),
            True,
        )
        failures = (
            (None, None, (None,) * 5),
            ("contract_field", "source", (None,) * 5),
            ("contract_field", None, (None, None, 0, None, None)),
        )
        for parameter, source, fixed in failures:
            with self.subTest(parameter=parameter, source=source, fixed=fixed):
                self.assertIs(
                    self.shape(
                        "template_parameter",
                        parameter=parameter,
                        source=source,
                        fixed=fixed,
                    ),
                    False,
                )

    def test_generated_node_id_shape(self):
        self.assertIs(
            self.shape("generated_node_id", source="node-key"), True
        )
        self.assertIs(self.shape("generated_node_id", source=""), True)
        failures = (
            (None, None, (None,) * 5),
            ("contract_field", "node-key", (None,) * 5),
            (None, "node-key", (False, None, None, None, None)),
        )
        for parameter, source, fixed in failures:
            with self.subTest(parameter=parameter, source=source, fixed=fixed):
                self.assertIs(
                    self.shape(
                        "generated_node_id",
                        parameter=parameter,
                        source=source,
                        fixed=fixed,
                    ),
                    False,
                )

    def test_explicit_null_shape(self):
        self.assertIs(self.shape("explicit_null"), True)
        failures = (
            ("contract_field", None, (None,) * 5),
            (None, "node-key", (None,) * 5),
            (None, None, (None, None, "", None, None)),
        )
        for parameter, source, fixed in failures:
            with self.subTest(parameter=parameter, source=source, fixed=fixed):
                self.assertIs(
                    self.shape(
                        "explicit_null",
                        parameter=parameter,
                        source=source,
                        fixed=fixed,
                    ),
                    False,
                )

    def test_unknown_kind_is_false_and_malformed_inputs_fail_closed(self):
        self.assertIs(self.shape("future_binding_kind"), False)
        invalid_scalars = (
            ("kind", None, "template_binding_shape_kind_type_invalid"),
            ("kind", False, "template_binding_shape_kind_type_invalid"),
            ("kind", 1, "template_binding_shape_kind_type_invalid"),
            (
                "kind",
                frozen_record(value="fixed_value"),
                "template_binding_shape_kind_type_invalid",
            ),
            ("parameter", False, "template_binding_shape_parameter_type_invalid"),
            ("parameter", 1, "template_binding_shape_parameter_type_invalid"),
            ("source", False, "template_binding_shape_source_type_invalid"),
            ("source", 1, "template_binding_shape_source_type_invalid"),
        )
        base = {
            "kind": "explicit_null",
            "parameter": None,
            "source": None,
            **dict(zip(self.FIXED_NAMES, (None,) * 5)),
        }
        for name, value, reason in invalid_scalars:
            identifiers = dict(base)
            identifiers[name] = value
            with self.subTest(name=name, value=value):
                self.assert_evaluation_error(
                    parse(self.EXPRESSION), identifiers, reason=reason
                )

        list_kind = validation.Call(
            "template_binding_shape_valid",
            (
                validation.ListLiteral((literal("string", "fixed_value"),)),
                literal("null", None),
                literal("null", None),
                validation.ListLiteral((literal("null", None),) * 5),
            ),
        )
        self.assert_evaluation_error(
            list_kind, reason="template_binding_shape_kind_type_invalid"
        )

        fixed_prefix = (
            literal("string", "explicit_null"),
            literal("null", None),
            literal("null", None),
        )
        for arguments in (
            (),
            fixed_prefix,
            fixed_prefix
            + (validation.ListLiteral((literal("null", None),) * 5),)
            + (literal("null", None),),
        ):
            with self.subTest(arguments=arguments):
                self.assert_evaluation_error(
                    validation.Call("template_binding_shape_valid", arguments),
                    reason="template_binding_shape_arity_invalid",
                )

        for fixed_ast, reason in (
            (
                literal("string", "not-a-list"),
                "template_binding_shape_fixed_values_container_invalid",
            ),
            (
                validation.ListLiteral((literal("null", None),) * 4),
                "template_binding_shape_fixed_values_length_invalid",
            ),
            (
                validation.ListLiteral((literal("null", None),) * 6),
                "template_binding_shape_fixed_values_length_invalid",
            ),
            (
                validation.ListLiteral((
                    validation.ListLiteral((literal("null", None),)),
                    *(literal("null", None) for _ in range(4)),
                )),
                "template_binding_shape_fixed_value_type_invalid",
            ),
        ):
            with self.subTest(reason=reason):
                self.assert_evaluation_error(
                    validation.Call(
                        "template_binding_shape_valid",
                        fixed_prefix + (fixed_ast,),
                    ),
                    reason=reason,
                )

    def test_repeated_execution_is_deterministic(self):
        identifiers = {
            "kind": "fixed_value",
            "parameter": None,
            "source": None,
            **dict(zip(self.FIXED_NAMES, (False, None, None, None, None))),
        }
        first = evaluate(self.EXPRESSION, identifiers)
        second = evaluate(
            self.EXPRESSION, dict(reversed(tuple(identifiers.items())))
        )
        self.assertEqual((first, second), (True, True))


class TestTemplateArgumentValueType(EvaluatorTestCase):
    EXPRESSION = (
        "template_argument_value_type_valid(contract,value_boolean,"
        "value_integer,value_text,value_registry,value_reference,"
        "value_expression)"
    )
    CHANNELS = (
        "value_boolean",
        "value_integer",
        "value_text",
        "value_registry",
        "value_reference",
        "value_expression",
    )

    @staticmethod
    def contract(
        contract_field_id,
        data_type,
        *,
        allowed_group_id=None,
        reference_type_id=None,
        is_collection=False,
        nullable=False,
        null_handling=None,
        **extra,
    ):
        return frozen_record(
            contract_field_id=contract_field_id,
            data_type=data_type,
            nullable=nullable,
            null_handling=(
                null_handling
                if null_handling is not None
                else "explicit_null" if nullable else "forbidden"
            ),
            allowed_group_id=allowed_group_id,
            reference_type_id=reference_type_id,
            is_collection=is_collection,
            status="active",
            **extra,
        )

    def argument(self, contract, value_index, value, *, records=None):
        identifiers = dict(zip(self.CHANNELS, (None,) * 6))
        if value_index is not None:
            identifiers[self.CHANNELS[value_index]] = value
        identifiers["contract"] = contract
        authority = records or (
            self.contract("bool", "boolean"),
            self.contract("integer", "integer"),
            self.contract("text", "text"),
            self.contract("string", "string"),
            self.contract("date", "date"),
            self.contract("version", "version"),
            self.contract("language", "language_tag"),
            self.contract("registry", "string", allowed_group_id="keyword"),
            self.contract(
                "reference", "string", reference_type_id="ref_direct_card"
            ),
        )
        return evaluate(
            self.EXPRESSION,
            identifiers,
            table_resolver=lambda token: (
                authority if token == "registry:contract_fields" else None
            ),
            registry_group_resolver={"keyword_speed": "keyword"}.get,
        )

    def assert_contract_error(self, identifiers, records, reason):
        with self.assertRaises(
            evaluator.ValidationExpressionEvaluationError
        ) as raised:
            evaluate(
                self.EXPRESSION,
                identifiers,
                table_resolver=lambda _: records,
                registry_group_resolver=lambda _: None,
            )
        self.assertNotIsInstance(
            raised.exception, evaluator.ValidationExpressionUnsupportedError
        )
        self.assertEqual(dict(raised.exception.context)["reason"], reason)

    def test_scalar_channels_are_exact_and_preserve_falsy_values(self):
        passing = (
            ("bool", 0, True),
            ("bool", 0, False),
            ("integer", 1, 1),
            ("integer", 1, 0),
            ("text", 2, "value"),
            ("text", 2, ""),
            ("string", 2, "value"),
            ("date", 2, "2026-09-15"),
            ("version", 2, "1.2.3"),
            ("language", 2, "hu-HU"),
        )
        for contract, index, value in passing:
            with self.subTest(contract=contract, value=value):
                self.assertIs(self.argument(contract, index, value), True)
        rejected = (
            ("bool", 1, 1),
            ("bool", 0, 1),
            ("integer", 0, True),
            ("integer", 1, True),
            ("text", 1, 1),
        )
        for contract, index, value in rejected:
            with self.subTest(contract=contract, value=value):
                self.assertIs(self.argument(contract, index, value), False)

    def test_controlled_registry_requires_exact_full_id_and_group(self):
        self.assertIs(self.argument("registry", 3, "keyword_speed"), True)
        for value in (
            "damage_kind_direct",
            "unknown_registry_id",
            "speed",
            "gyorsasag",
        ):
            with self.subTest(value=value):
                self.assertIs(self.argument("registry", 3, value), False)
        self.assertIs(self.argument("registry", 2, "keyword_speed"), False)

    def test_reference_and_dynamic_expression_are_separate_channels(self):
        self.assertIs(self.argument("reference", 4, "entity-1"), True)
        self.assertIs(self.argument("reference", 2, "entity-1"), False)
        self.assertIs(self.argument("integer", 5, "expr-1"), True)
        identifiers = dict(zip(self.CHANNELS, (None,) * 6))
        identifiers.update(
            contract="integer", value_integer=1, value_expression="expr-1"
        )
        self.assertIs(
            evaluate(
                self.EXPRESSION,
                identifiers,
                table_resolver=lambda _: (
                    self.contract("integer", "integer"),
                ),
            ),
            False,
        )

    def test_cardinality_unknown_ambiguous_and_collection_fail_closed(self):
        self.assertIs(self.argument("integer", None, None), False)
        self.assertIs(self.argument("missing", 1, 1), False)
        ambiguous = self.contract(
            "ambiguous",
            "string",
            allowed_group_id="keyword",
            reference_type_id="ref_direct_card",
        )
        self.assertIs(
            self.argument("ambiguous", 3, "keyword_speed", records=(ambiguous,)),
            False,
        )
        collection = self.contract(
            "collection", "integer", is_collection=True
        )
        self.assertIs(
            self.argument("collection", 1, 1, records=(collection,)), False
        )
        unknown_type = self.contract("future", "future_scalar")
        self.assertIs(
            self.argument("future", 2, "value", records=(unknown_type,)),
            False,
        )
        self.assertIs(
            self.argument("future", 5, "expr-1", records=(unknown_type,)),
            False,
        )

    def test_duplicate_and_malformed_authority_are_controlled(self):
        identifiers = dict(zip(self.CHANNELS, (None,) * 6))
        identifiers.update(contract="integer", value_integer=1)
        duplicate = self.contract("integer", "integer")
        self.assert_contract_error(
            identifiers,
            (duplicate, duplicate),
            "template_argument_contract_field_ambiguous",
        )
        malformed = dict(self.contract("integer", "integer"))
        malformed["nullable"] = "false"
        self.assert_contract_error(
            identifiers,
            (frozen_record(**malformed),),
            "template_argument_contract_nullable_invalid",
        )
        for value in (None, False, 1, ""):
            broken = dict(identifiers)
            broken["contract"] = value
            with self.subTest(contract=value), self.assertRaises(
                evaluator.ValidationExpressionEvaluationError
            ) as raised:
                evaluate(
                    self.EXPRESSION,
                    broken,
                    table_resolver=lambda _: (duplicate,),
                )
            self.assertEqual(
                dict(raised.exception.context)["reason"],
                "template_argument_contract_field_id_invalid",
            )

    def test_exact_arity_and_authority_resolver_are_required(self):
        for arguments in ((), (literal("string", "contract"),) * 8):
            with self.subTest(count=len(arguments)), self.assertRaises(
                evaluator.ValidationExpressionEvaluationError
            ) as raised:
                evaluate(
                    validation.Call(
                        "template_argument_value_type_valid", arguments
                    )
                )
            self.assertEqual(
                dict(raised.exception.context)["reason"],
                "template_argument_value_type_arity_invalid",
            )
        identifiers = dict(zip(self.CHANNELS, (None,) * 6))
        identifiers.update(contract="integer", value_integer=1)
        with self.assertRaises(
            evaluator.ValidationExpressionUnsupportedError
        ) as raised:
            evaluate(self.EXPRESSION, identifiers)
        self.assertEqual(
            dict(raised.exception.context)["reason"],
            "typed_contract_table_resolver_missing",
        )


class TestTemplateBindingValueType(EvaluatorTestCase):
    EXPRESSION = (
        "template_binding_value_type_valid(target,kind,parameter,"
        "fixed_boolean,fixed_integer,fixed_text,fixed_registry,"
        "fixed_reference)"
    )
    FIXED_NAMES = (
        "fixed_boolean",
        "fixed_integer",
        "fixed_text",
        "fixed_registry",
        "fixed_reference",
    )

    @staticmethod
    def schema_field(
        field_id,
        data_type="string",
        *,
        field_name=None,
        table_id="items",
        nullable=False,
        null_handling=None,
        allowed_group_id=None,
        reference_table_id=None,
        reference_field_id=None,
        **extra,
    ):
        return frozen_record(
            field_id=field_id,
            field_name=field_name or field_id.removeprefix("fld_"),
            table_id=table_id,
            data_type=data_type,
            nullable=nullable,
            null_handling=(
                null_handling
                if null_handling is not None
                else "explicit_null" if nullable else "forbidden"
            ),
            allowed_group_id=allowed_group_id,
            reference_table_id=reference_table_id,
            reference_field_id=reference_field_id,
            status="active",
            **extra,
        )

    @staticmethod
    def contract(
        contract_field_id,
        data_type,
        *,
        allowed_group_id=None,
        reference_type_id=None,
        is_collection=False,
        **extra,
    ):
        return frozen_record(
            contract_field_id=contract_field_id,
            data_type=data_type,
            nullable=False,
            null_handling="forbidden",
            allowed_group_id=allowed_group_id,
            reference_type_id=reference_type_id,
            is_collection=is_collection,
            status="active",
            **extra,
        )

    def tables(self, *, schema_fields=(), contracts=(), schema_tables=()):
        registry_pk = self.schema_field(
            "fld_value_registry_registry_value_id",
            field_name="registry_value_id",
            table_id="value_registry",
        )
        values = {
            "carddatabase:schema_fields": tuple(schema_fields),
            "carddatabase:schema_tables": tuple(schema_tables),
            "registry:schema_fields": (registry_pk,),
            "registry:schema_tables": (
                frozen_record(
                    table_id="value_registry",
                    primary_key="registry_value_id",
                    status="active",
                ),
            ),
            "registry:contract_fields": tuple(contracts),
        }
        return values.get

    def binding(
        self,
        target,
        kind,
        *,
        parameter=None,
        fixed=None,
        schema_fields=(),
        contracts=(),
        schema_tables=(),
        reverse=False,
    ):
        identifiers = dict(zip(self.FIXED_NAMES, fixed or (None,) * 5))
        identifiers.update(target=target, kind=kind, parameter=parameter)
        fields = tuple(reversed(schema_fields)) if reverse else schema_fields
        contract_rows = tuple(reversed(contracts)) if reverse else contracts
        tables = tuple(reversed(schema_tables)) if reverse else schema_tables
        return evaluate(
            self.EXPRESSION,
            identifiers,
            table_resolver=self.tables(
                schema_fields=fields,
                contracts=contract_rows,
                schema_tables=tables,
            ),
            registry_group_resolver={
                "keyword_speed": "keyword",
                "damage_kind_direct": "damage_kind",
            }.get,
        )

    def scalar_targets(self):
        return (
            self.schema_field("fld_bool", "boolean"),
            self.schema_field("fld_int", "integer"),
            self.schema_field("fld_text", "text", nullable=True),
        )

    def reference_authority(self):
        target = self.schema_field(
            "fld_ref",
            reference_table_id="targets",
            reference_field_id="fld_targets_id",
        )
        primary = self.schema_field(
            "fld_targets_id", field_name="target_id", table_id="targets"
        )
        table = frozen_record(
            table_id="targets", primary_key="target_id", status="active"
        )
        return target, primary, table

    def test_fixed_scalar_channels_are_exact(self):
        fields = self.scalar_targets()
        cases = (
            ("fld_bool", (True, None, None, None, None), True),
            ("fld_bool", (False, None, None, None, None), True),
            ("fld_int", (None, 0, None, None, None), True),
            ("fld_int", (None, 7, None, None, None), True),
            ("fld_text", (None, None, "", None, None), True),
            ("fld_text", (None, None, "text", None, None), True),
            ("fld_int", (True, None, None, None, None), False),
            ("fld_int", (None, True, None, None, None), False),
            ("fld_text", (None, 1, None, None, None), False),
        )
        for target, fixed, expected in cases:
            with self.subTest(target=target, fixed=fixed):
                self.assertIs(
                    self.binding(
                        target,
                        "fixed_value",
                        fixed=fixed,
                        schema_fields=fields,
                    ),
                    expected,
                )

    def test_fixed_controlled_registry_is_exact(self):
        controlled = self.schema_field(
            "fld_controlled", allowed_group_id="keyword"
        )
        for value, expected in (
            ("keyword_speed", True),
            ("damage_kind_direct", False),
            ("unknown_registry_id", False),
            ("speed", False),
        ):
            with self.subTest(value=value):
                self.assertIs(
                    self.binding(
                        "fld_controlled",
                        "fixed_value",
                        fixed=(None, None, None, value, None),
                        schema_fields=(controlled,),
                    ),
                    expected,
                )

    def test_physical_reference_requires_valid_canonical_primary_key(self):
        target, primary, table = self.reference_authority()
        self.assertIs(
            self.binding(
                "fld_ref",
                "fixed_value",
                fixed=(None, None, None, None, "target-1"),
                schema_fields=(target, primary),
                schema_tables=(table,),
            ),
            True,
        )
        self.assertIs(
            self.binding(
                "fld_ref",
                "fixed_value",
                fixed=(None, None, "target-1", None, None),
                schema_fields=(target, primary),
                schema_tables=(table,),
            ),
            False,
        )
        missing = self.schema_field(
            "fld_missing",
            reference_table_id="targets",
            reference_field_id="fld_unknown",
        )
        wrong_table = self.schema_field(
            "fld_targets_id", field_name="target_id", table_id="other"
        )
        non_pk_target = self.schema_field(
            "fld_ref_non_pk",
            reference_table_id="targets",
            reference_field_id="fld_label",
        )
        non_pk = self.schema_field(
            "fld_label", field_name="label", table_id="targets"
        )
        for target_id, fields in (
            ("fld_missing", (missing,)),
            ("fld_ref", (target, wrong_table)),
            ("fld_ref_non_pk", (non_pk_target, non_pk)),
        ):
            with self.subTest(target=target_id):
                self.assertIs(
                    self.binding(
                        target_id,
                        "fixed_value",
                        fixed=(None, None, None, None, "target-1"),
                        schema_fields=fields,
                        schema_tables=(table,),
                    ),
                    False,
                )

    def test_value_registry_reference_uses_registry_channel_by_schema_proof(self):
        target = self.schema_field(
            "fld_registry_ref",
            reference_table_id="registry:value_registry",
            reference_field_id="registry:fld_value_registry_registry_value_id",
        )
        self.assertIs(
            self.binding(
                "fld_registry_ref",
                "fixed_value",
                fixed=(None, None, None, "keyword_speed", None),
                schema_fields=(target,),
            ),
            True,
        )
        self.assertIs(
            self.binding(
                "fld_registry_ref",
                "fixed_value",
                fixed=(None, None, None, "unknown", None),
                schema_fields=(target,),
            ),
            False,
        )

    def test_template_parameter_requires_machine_readable_compatibility(self):
        fields = self.scalar_targets() + (
            self.schema_field("fld_controlled", allowed_group_id="keyword"),
        )
        contracts = (
            self.contract("int_contract", "integer"),
            self.contract("bool_contract", "boolean"),
            self.contract("text_contract", "version"),
            self.contract(
                "controlled_contract", "string", allowed_group_id="keyword"
            ),
            self.contract(
                "reference_contract",
                "string",
                reference_type_id="ref_direct_card",
            ),
        )
        cases = (
            ("fld_int", "int_contract", True),
            ("fld_bool", "int_contract", False),
            ("fld_text", "int_contract", False),
            ("fld_bool", "bool_contract", True),
            ("fld_text", "text_contract", True),
            ("fld_controlled", "controlled_contract", True),
            ("fld_int", "missing_contract", False),
            ("fld_int", "reference_contract", False),
        )
        for target, parameter, expected in cases:
            with self.subTest(target=target, parameter=parameter):
                self.assertIs(
                    self.binding(
                        target,
                        "template_parameter",
                        parameter=parameter,
                        schema_fields=fields,
                        contracts=contracts,
                    ),
                    expected,
                )

    def test_generated_node_local_type_and_explicit_null(self):
        target, primary, table = self.reference_authority()
        scalar = self.schema_field("fld_scalar", "string")
        nullable = self.schema_field("fld_nullable", nullable=True)
        null_forbidden = self.schema_field(
            "fld_null_forbidden", nullable=True, null_handling="forbidden"
        )
        fields = (target, primary, scalar, nullable, null_forbidden)
        self.assertIs(
            self.binding(
                "fld_ref",
                "generated_node_id",
                schema_fields=fields,
                schema_tables=(table,),
            ),
            True,
        )
        self.assertIs(
            self.binding(
                "fld_scalar", "generated_node_id", schema_fields=fields
            ),
            False,
        )
        for field_id, expected in (
            ("fld_nullable", True),
            ("fld_scalar", False),
            ("fld_null_forbidden", False),
        ):
            self.assertIs(
                self.binding(
                    field_id, "explicit_null", schema_fields=fields
                ),
                expected,
            )

    def test_malformed_unknown_and_reversed_authority_are_deterministic(self):
        fields = self.scalar_targets()
        self.assertIs(
            self.binding("fld_int", "future_kind", schema_fields=fields), False
        )
        self.assertIs(
            self.binding("fld_unknown", "fixed_value", schema_fields=fields),
            False,
        )
        for target in (None, False, 1, ""):
            with self.subTest(target=target), self.assertRaises(
                evaluator.ValidationExpressionEvaluationError
            ):
                self.binding(target, "fixed_value", schema_fields=fields)
        for kind in (None, False, 1):
            with self.subTest(kind=kind), self.assertRaises(
                evaluator.ValidationExpressionEvaluationError
            ):
                self.binding("fld_int", kind, schema_fields=fields)
        for parameter in (False, 1):
            with self.subTest(parameter=parameter), self.assertRaises(
                evaluator.ValidationExpressionEvaluationError
            ):
                self.binding(
                    "fld_int",
                    "template_parameter",
                    parameter=parameter,
                    schema_fields=fields,
                )
        malformed = dict(self.schema_field("fld_malformed"))
        malformed.pop("data_type")
        with self.assertRaises(
            evaluator.ValidationExpressionEvaluationError
        ) as raised:
            self.binding(
                "fld_malformed",
                "fixed_value",
                fixed=(None, None, "text", None, None),
                schema_fields=(frozen_record(**malformed),),
            )
        self.assertEqual(
            dict(raised.exception.context)["reason"],
            "template_binding_target_metadata_missing",
        )
        contract = self.contract("int_contract", "integer")
        with self.assertRaises(
            evaluator.ValidationExpressionEvaluationError
        ) as duplicate_contract:
            self.binding(
                "fld_int",
                "template_parameter",
                parameter="int_contract",
                schema_fields=fields,
                contracts=(contract, contract),
            )
        self.assertEqual(
            dict(duplicate_contract.exception.context)["reason"],
            "template_binding_parameter_contract_ambiguous",
        )
        malformed_contract = dict(contract)
        malformed_contract["is_collection"] = "false"
        with self.assertRaises(
            evaluator.ValidationExpressionEvaluationError
        ) as bad_contract:
            self.binding(
                "fld_int",
                "template_parameter",
                parameter="int_contract",
                schema_fields=fields,
                contracts=(frozen_record(**malformed_contract),),
            )
        self.assertEqual(
            dict(bad_contract.exception.context)["reason"],
            "template_binding_parameter_contract_is_collection_invalid",
        )
        with self.assertRaises(
            evaluator.ValidationExpressionEvaluationError
        ) as duplicate_target:
            self.binding(
                "fld_int",
                "fixed_value",
                fixed=(None, 1, None, None, None),
                schema_fields=(fields[1], fields[1]),
            )
        self.assertEqual(
            dict(duplicate_target.exception.context)["reason"],
            "template_binding_target_field_ambiguous",
        )
        first = self.binding(
            "fld_int",
            "template_parameter",
            parameter="int_contract",
            schema_fields=fields,
            contracts=(contract,),
        )
        second = self.binding(
            "fld_int",
            "template_parameter",
            parameter="int_contract",
            schema_fields=fields,
            contracts=(contract,),
            reverse=True,
        )
        self.assertEqual((first, second), (True, True))

    def test_shape_ambiguity_and_exact_arity_fail_closed(self):
        target = self.schema_field("fld_int", "integer")
        self.assertIs(
            self.binding(
                "fld_int", "fixed_value", schema_fields=(target,)
            ),
            False,
        )
        self.assertIs(
            self.binding(
                "fld_int",
                "fixed_value",
                fixed=(None, 1, "also", None, None),
                schema_fields=(target,),
            ),
            False,
        )
        for arguments in ((), (literal("string", "value"),) * 9):
            with self.subTest(count=len(arguments)), self.assertRaises(
                evaluator.ValidationExpressionEvaluationError
            ) as raised:
                evaluate(
                    validation.Call(
                        "template_binding_value_type_valid", arguments
                    )
                )
            self.assertEqual(
                dict(raised.exception.context)["reason"],
                "template_binding_value_type_arity_invalid",
            )


class TestTableCount(EvaluatorTestCase):
    ROWS = (
        frozen_record(item_id="a", status="active", value=1),
        frozen_record(item_id="b", status="inactive", value=2),
        frozen_record(item_id="c", status="active", value=3),
    )

    def test_empty_zero_one_and_multiple_matches_return_exact_integers(self):
        cases = (
            ((), "true", 0),
            (self.ROWS, "value == 99", 0),
            (self.ROWS, "value == 2", 1),
            (self.ROWS, 'status == "active"', 2),
        )
        for rows, predicate, expected in cases:
            with self.subTest(predicate=predicate):
                result = evaluate(
                    f'count("items",{predicate})',
                    table_resolver=lambda _: rows,
                )
                self.assertIs(type(result), int)
                self.assertGreaterEqual(result, 0)
                self.assertEqual(result, expected)

    def test_current_and_candidate_same_named_fields_have_distinct_scopes(self):
        outer = frozen_record(realm_id="outer", marker="outer")
        rows = (
            frozen_record(
                item_id="a",
                realm_id="outer",
                marker="inner",
                current="shadow",
            ),
            frozen_record(
                item_id="b",
                realm_id="other",
                marker="inner",
                current="shadow",
            ),
        )
        self.assertEqual(
            evaluate(
                'count("items",realm_id == current.realm_id and '
                'marker == "inner")',
                {"current": outer, "realm_id": "outer-source"},
                table_resolver=lambda _: rows,
            ),
            1,
        )

    def test_nested_count_normalize_and_current_keep_distinct_scopes(self):
        outer = frozen_record(
            legacy_group="keyword",
            legacy_value="  STRA\u1e9eE  ",
            target_record_id="keyword_street",
            requires_manual_review=False,
        )
        rows = (
            frozen_record(
                alias_id="matching",
                group_id="keyword",
                alias_value="strasse",
                normalization_mode="trim_casefold",
                case_sensitive=False,
                canonical_registry_value_id="keyword_street",
                requires_audit=False,
                status="active",
                current="candidate-shadow",
            ),
            frozen_record(
                alias_id="wrong-target",
                group_id="keyword",
                alias_value="STRASSE",
                normalization_mode="trim_casefold",
                case_sensitive=False,
                canonical_registry_value_id="keyword_other",
                requires_audit=False,
                status="active",
                current="candidate-shadow",
            ),
            frozen_record(
                alias_id="wrong-group",
                group_id="other",
                alias_value="strasse",
                normalization_mode="exact",
                case_sensitive=True,
                canonical_registry_value_id="keyword_street",
                requires_audit=False,
                status="active",
                current="candidate-shadow",
            ),
        )
        expression = (
            'count("aliases",group_id == current.legacy_group and '
            "normalize(alias_value,normalization_mode,case_sensitive) == "
            "normalize(current.legacy_value,normalization_mode,case_sensitive) "
            "and canonical_registry_value_id == current.target_record_id and "
            "requires_audit == current.requires_manual_review and "
            'status == "active") >= 1'
        )
        forward = evaluate(
            expression,
            {"current": outer},
            table_resolver=lambda _: rows,
        )
        reverse = evaluate(
            expression,
            {"current": outer},
            table_resolver=lambda _: tuple(reversed(rows)),
        )
        self.assertIs(forward, True)
        self.assertIs(reverse, True)

    def test_outer_local_binding_is_readable_and_not_shadowed(self):
        rows = (frozen_record(item_id="a", label="candidate"),)
        self.assertIs(
            evaluate(
                'label = "outer"; count("items",label == "outer") == 1',
                table_resolver=lambda _: rows,
            ),
            True,
        )

    def test_lifecycle_filter_is_only_applied_when_explicit(self):
        self.assertEqual(
            evaluate(
                'count("items",status == "active")',
                table_resolver=lambda _: self.ROWS,
            ),
            2,
        )
        self.assertEqual(
            evaluate(
                'count("items",true)',
                table_resolver=lambda _: self.ROWS,
            ),
            3,
        )

    def test_qualified_and_unqualified_table_tokens_are_exact(self):
        calls = []

        def resolve(table):
            calls.append(table)
            return ()

        self.assertEqual(
            evaluate('count("items",true)', table_resolver=resolve), 0
        )
        self.assertEqual(
            evaluate(
                'count("registry:items",true)', table_resolver=resolve
            ),
            0,
        )
        self.assertEqual(calls, ["items", "registry:items"])

    def test_missing_table_and_namespace_failures_are_controlled(self):
        with self.assertRaises(
            evaluator.ValidationExpressionEvaluationError
        ) as missing:
            evaluate('count("missing",true)', table_resolver=lambda _: None)
        self.assertEqual(
            dict(missing.exception.context)["reason"], "count_table_missing"
        )

        def missing_namespace(_):
            raise evaluator.ValidationExpressionEvaluationError(
                node_type="Call",
                builtin="count",
                reason="count_namespace_invalid",
            )

        with self.assertRaises(
            evaluator.ValidationExpressionEvaluationError
        ) as namespace:
            evaluate(
                'count("missing:items",true)',
                table_resolver=missing_namespace,
            )
        self.assertEqual(
            dict(namespace.exception.context)["reason"],
            "count_namespace_invalid",
        )

    def test_table_source_type_and_arity_are_strict(self):
        for expression, identifiers in (
            ("count(null,true)", {}),
            ("count(false,true)", {}),
            ("count(1,true)", {}),
            ("count(source,true)", {"source": frozen_record(value="items")}),
        ):
            with self.subTest(expression=expression):
                with self.assertRaises(
                    evaluator.ValidationExpressionEvaluationError
                ) as raised:
                    evaluate(
                        expression,
                        identifiers,
                        table_resolver=lambda _: (),
                    )
                self.assertEqual(
                    dict(raised.exception.context)["reason"],
                    "count_table_token_invalid",
                )
        with self.assertRaises(
            evaluator.ValidationExpressionEvaluationError
        ) as arity:
            evaluate(
                validation.Call(
                    "count", (literal("string", "items"),)
                ),
                table_resolver=lambda _: (),
            )
        self.assertEqual(
            dict(arity.exception.context)["reason"], "count_arity_invalid"
        )

    def test_predicate_missing_field_and_non_boolean_fail_closed(self):
        rows = (frozen_record(item_id="a", value="not-boolean"),)
        for expression, reason in (
            ('count("items",missing == 1)', "identifier_missing"),
            ('count("items",value)', "boolean_operand_required"),
        ):
            with self.subTest(expression=expression):
                with self.assertRaises(
                    evaluator.ValidationExpressionEvaluationError
                ) as raised:
                    evaluate(expression, table_resolver=lambda _: rows)
                self.assertEqual(
                    dict(raised.exception.context)["reason"], reason
                )

    def test_missing_current_member_is_controlled(self):
        with self.assertRaises(
            evaluator.ValidationExpressionEvaluationError
        ) as raised:
            evaluate(
                'count("items",value == current.missing)',
                {"current": frozen_record(value=1)},
                table_resolver=lambda _: self.ROWS,
            )
        self.assertEqual(
            dict(raised.exception.context)["reason"], "member_missing"
        )

    def test_false_when_guard_does_not_resolve_count_table(self):
        calls = []
        self.assertIs(
            evaluate(
                'when(false,count("missing",true) > 0)',
                table_resolver=lambda table: calls.append(table),
            ),
            True,
        )
        self.assertEqual(calls, [])

    def test_malformed_candidate_and_unexpected_resolver_error_are_controlled(self):
        with self.assertRaises(
            evaluator.ValidationExpressionEvaluationError
        ) as malformed:
            evaluate(
                'count("items",true)',
                table_resolver=lambda _: (
                    MappingProxyType({"item_id": "a", "bad": []}),
                ),
            )
        self.assertEqual(
            dict(malformed.exception.context)["reason"],
            "count_candidate_record_invalid",
        )

        def fail(_):
            raise RuntimeError("resolver detail")

        with self.assertRaises(
            evaluator.ValidationExpressionEvaluationError
        ) as wrapped:
            evaluate('count("items",true)', table_resolver=fail)
        self.assertEqual(
            dict(wrapped.exception.context)["reason"],
            "count_table_resolution_failed",
        )
        self.assertNotIn("resolver detail", str(wrapped.exception))

    def test_reversed_rows_are_deterministic_and_inputs_remain_immutable(self):
        outer_values = {"realm_id": "outer"}
        outer = MappingProxyType(outer_values)
        rows = (
            frozen_record(item_id="b", realm_id="other"),
            frozen_record(item_id="a", realm_id="outer"),
        )
        expression = 'count("items",realm_id == current.realm_id)'
        forward = evaluate(
            expression,
            {"current": outer},
            table_resolver=lambda _: rows,
        )
        reverse = evaluate(
            expression,
            {"current": outer},
            table_resolver=lambda _: tuple(reversed(rows)),
        )
        self.assertEqual((forward, reverse), (1, 1))
        self.assertEqual(outer_values, {"realm_id": "outer"})
        self.assertEqual(rows[0]["item_id"], "b")


class TestVersionHelpers(EvaluatorTestCase):
    def test_version_gte_compares_numeric_major_minor_patch_components(self):
        cases = (
            ("0.7.0", "0.7.0", True),
            ("0.7.1", "0.7.0", True),
            ("0.7.0", "0.7.1", False),
            ("0.10.0", "0.9.0", True),
            ("0.9.0", "0.10.0", False),
            ("1.0.0", "0.99.99", True),
            ("0.99.99", "1.0.0", False),
            ("12345678901234567890.0.0", "9999999999999999999.9.9", True),
        )
        for current, minimum, expected in cases:
            with self.subTest(current=current, minimum=minimum):
                self.assertIs(
                    evaluate(
                        "version_gte(current,minimum)",
                        {"current": current, "minimum": minimum},
                    ),
                    expected,
                )

    def test_version_gte_rejects_noncanonical_versions_without_coercion(self):
        malformed = (
            "",
            "1",
            "1.2",
            "1.2.3.4",
            "1..3",
            "01.2.3",
            "1.02.3",
            "1.2.03",
            "+1.2.3",
            "1.2.-3",
            " 1.2.3",
            "1.2.3 ",
            "1.2.3-alpha",
            "１.2.3",
        )
        for value in malformed:
            with self.subTest(value=value):
                with self.assertRaises(
                    evaluator.ValidationExpressionEvaluationError
                ) as raised:
                    evaluate(
                        "version_gte(current,minimum)",
                        {"current": value, "minimum": "0.0.0"},
                    )
                self.assertNotIsInstance(
                    raised.exception,
                    evaluator.ValidationExpressionUnsupportedError,
                )
                self.assertEqual(
                    dict(raised.exception.context)["reason"],
                    "version_argument_0_malformed",
                )

    def test_version_gte_rejects_null_bool_integer_and_record_arguments(self):
        invalid = (None, False, 0, MappingProxyType({"version": "1.0.0"}))
        for value in invalid:
            with self.subTest(value=value):
                with self.assertRaises(
                    evaluator.ValidationExpressionEvaluationError
                ) as raised:
                    evaluate(
                        "version_gte(current,minimum)",
                        {"current": value, "minimum": "0.0.0"},
                    )
                self.assertEqual(
                    dict(raised.exception.context)["reason"],
                    "version_argument_0_type_invalid",
                )

    def test_version_helper_arities_are_explicitly_unsupported(self):
        for ast, builtin in (
            (
                validation.Call(
                    "version_gte", (literal("string", "1.0.0"),)
                ),
                "version_gte",
            ),
            (validation.Call("current_schema_version", ()), "current_schema_version"),
        ):
            with self.subTest(builtin=builtin):
                with self.assertRaises(
                    evaluator.ValidationExpressionUnsupportedError
                ) as raised:
                    evaluate(
                        ast,
                        schema_version_resolver=lambda _: "1.0.0",
                    )
                self.assertEqual(
                    dict(raised.exception.context),
                    {
                        "builtin": builtin,
                        "node_type": "Call",
                        "reason": "builtin_arity_not_supported",
                    },
                )

    def test_current_schema_version_uses_exact_resolver_value(self):
        calls = []

        def resolve(component_id):
            calls.append(component_id)
            return "0.7.0"

        self.assertEqual(
            evaluate(
                'current_schema_version("CARDDATABASE")',
                schema_version_resolver=resolve,
            ),
            "0.7.0",
        )
        self.assertEqual(calls, ["CARDDATABASE"])

    def test_current_schema_version_failures_are_controlled(self):
        cases = (
            (
                'current_schema_version("CARDDATABASE")',
                None,
                evaluator.ValidationExpressionUnsupportedError,
                "schema_version_resolver_missing",
            ),
            (
                "current_schema_version(component)",
                lambda _: "0.7.0",
                evaluator.ValidationExpressionEvaluationError,
                "component_identifier_invalid",
            ),
            (
                'current_schema_version("CARDDATABASE")',
                lambda _: None,
                evaluator.ValidationExpressionEvaluationError,
                "schema_version_result_type_invalid",
            ),
            (
                'current_schema_version("CARDDATABASE")',
                lambda _: "0.7",
                evaluator.ValidationExpressionEvaluationError,
                "schema_version_malformed",
            ),
        )
        for expression, resolver, error_type, reason in cases:
            with self.subTest(reason=reason):
                identifiers = {"component": None}
                with self.assertRaises(error_type) as raised:
                    evaluate(
                        expression,
                        identifiers,
                        schema_version_resolver=resolver,
                    )
                self.assertEqual(
                    dict(raised.exception.context)["reason"], reason
                )

    def test_current_schema_version_wraps_unexpected_resolver_exception(self):
        def fail(_):
            raise RuntimeError("resolver implementation detail")

        with self.assertRaises(
            evaluator.ValidationExpressionEvaluationError
        ) as raised:
            evaluate(
                'current_schema_version("CARDDATABASE")',
                schema_version_resolver=fail,
            )
        self.assertEqual(
            dict(raised.exception.context)["reason"],
            "schema_version_resolution_failed",
        )
        self.assertNotIn("resolver implementation detail", str(raised.exception))

    def test_false_when_guard_does_not_resolve_schema_version(self):
        calls = []
        self.assertIs(
            evaluate(
                'when(false,version_gte(current_schema_version("MISSING"),'
                '"0.0.0"))',
                schema_version_resolver=lambda value: calls.append(value),
            ),
            True,
        )
        self.assertEqual(calls, [])


class TestUnsupportedSurface(EvaluatorTestCase):
    def test_disallowed_ast_nodes_are_explicitly_unsupported(self):
        cases = (
            validation.TbdLiteral(),
            validation.MapLiteral(()),
            validation.Binding("row", validation.Identifier("value")),
        )
        for ast in cases:
            with self.subTest(node_type=type(ast).__name__):
                self.assert_unsupported(ast, node_type=type(ast).__name__)

    def test_arbitrary_builtin_is_unsupported_without_argument_evaluation(self):
        ast = validation.Call(
            "future_builtin", (validation.Identifier("missing"),)
        )
        self.assert_unsupported(
            ast, builtin="future_builtin", reason="builtin_not_allowlisted"
        )

    def test_unsupported_binary_operator_is_not_evaluated(self):
        ast = validation.BinaryOperation(
            "<=", validation.Identifier("missing"), literal("integer", 1)
        )
        self.assert_unsupported(ast, operator="<=", reason="operator_not_allowlisted")

    def test_less_than_is_exact_integer_only(self):
        self.assertIs(evaluate("left < right", {"left": 1, "right": 2}), True)
        self.assertIs(evaluate("left < right", {"left": 2, "right": 1}), False)
        for left, right in ((True, 2), (1, False), ("1", 2), (1, "2")):
            with self.subTest(left=left, right=right):
                with self.assertRaises(
                    evaluator.ValidationExpressionEvaluationError
                ) as raised:
                    evaluate("left < right", {"left": left, "right": right})
                self.assertEqual(
                    dict(raised.exception.context)["reason"],
                    "integer_operands_required",
                )

    def test_unsupported_unary_operator_is_explicit(self):
        ast = validation.UnaryOperation("-", validation.Identifier("missing"))
        self.assert_unsupported(ast, operator="-", reason="operator_not_allowlisted")

    def test_errors_are_deterministic_and_structured(self):
        ast = validation.Identifier("missing")
        first = self.assert_evaluation_error(ast)
        second = self.assert_evaluation_error(ast)
        self.assertEqual(first.context, second.context)
        self.assertEqual(str(first), str(second))
        self.assertNotIn("0x", str(first))


class TestParserIntegration(EvaluatorTestCase):
    def test_parser_to_evaluator_direct_predicate(self):
        ast = parse("minimum_choices >= 0 and maximum_choices >= minimum_choices")
        self.assertIs(
            evaluate(ast, {"minimum_choices": 1, "maximum_choices": 2}), True
        )

    def test_parser_to_evaluator_guarded_equality(self):
        ast = parse("when(optional == true, minimum_choices == 0)")
        self.assertIs(evaluate(ast, {"optional": False}), True)
        self.assertIs(
            evaluate(ast, {"optional": True, "minimum_choices": 0}), True
        )

    def test_parser_to_evaluator_membership(self):
        ast = parse('output_table_id in ["ability_triggers","ability_effects"]')
        self.assertIs(evaluate(ast, {"output_table_id": "ability_effects"}), True)

    def test_parser_to_evaluator_negated_membership(self):
        ast = parse('target_record_id not in [null,"#TBD"]')
        self.assertIs(evaluate(ast, {"target_record_id": "target-1"}), True)
        self.assertIs(evaluate(ast, {"target_record_id": None}), False)


class TestPublicBoundaryAndTargetCohort(EvaluatorTestCase):
    DIRECT_RULE_IDS = frozenset(
        {
            "cdb_val_abilities_template_mode_contract",
            "cdb_val_card_keywords_parameter_exclusive",
            "cdb_val_card_relations_not_self",
            "cdb_val_cards_holding_set_not_introduced",
            "cdb_val_choices_count_bounds",
            "cdb_val_costs_amount_exclusive",
            "cdb_val_costs_amount_nonnegative",
            "cdb_val_durations_maximum_positive",
            "cdb_val_targets_count_bounds",
            "cdb_val_usage_limits_maximum_positive",
            "val_ability_template_nodes_output_table_allowed",
            "val_modifier_types_duration_invariant",
            "val_modifier_types_fixed_field_invariant",
            "val_restriction_types_duration_invariant",
        }
    )
    GUARDED_RULE_IDS = frozenset(
        {
            "cdb_val_card_printings_reprint_not_self",
            "cdb_val_choices_optional_minimum",
            "cdb_val_expressions_aggregate_reference_required",
            "cdb_val_expressions_field_reference_required",
            "cdb_val_sets_holding_release_date_null",
            "cdb_val_targets_activity_state_object_contract",
            "cdb_val_targets_optional_minimum",
            "val_aliases_casefold_case_sensitive_consistency",
            "val_aliases_legacy_term_requires_audit",
            "val_modifier_types_additive_integer_type",
            "val_restriction_phase_completion_kind",
        }
    )

    @staticmethod
    def walk(node):
        yield node
        for attribute in ("operand", "left", "right"):
            child = getattr(node, attribute, None)
            if child is not None:
                yield from TestPublicBoundaryAndTargetCohort.walk(child)
        for attribute in ("items", "arguments", "statements"):
            for child in getattr(node, attribute, ()):
                yield from TestPublicBoundaryAndTargetCohort.walk(child)

    def test_public_api_is_exactly_three_exports(self):
        self.assertEqual(
            evaluator.__all__,
            [
                "ValidationExpressionEvaluationError",
                "ValidationExpressionUnsupportedError",
                "evaluate_validation_expression",
            ],
        )

    def test_evaluator_has_no_execution_or_stage_dependency(self):
        source = EVALUATOR_PATH.read_text(encoding="utf-8")
        for forbidden in (
            "ValidationDataContext",
            "ValidationExecutionResult",
            "canonical_validation_execution",
            "canonical_validation_stage",
            "BUILTIN_CATALOG",
            "builtin_registry",
            "call_resolver_registry",
        ):
            self.assertNotIn(forbidden, source)

    def test_target_25_rule_surface_is_fully_representable(self):
        catalog, _ = execution_tests.current_corpus_catalog_and_context()
        target_ids = self.DIRECT_RULE_IDS | self.GUARDED_RULE_IDS
        self.assertEqual(len(self.DIRECT_RULE_IDS), 14)
        self.assertEqual(len(self.GUARDED_RULE_IDS), 11)
        self.assertEqual(len(target_ids), 25)

        allowed_nodes = {
            validation.Literal,
            validation.Identifier,
            validation.ListLiteral,
            validation.UnaryOperation,
            validation.BinaryOperation,
            validation.Call,
            validation.Sequence,
        }
        allowed_operators = {"==", "!=", ">=", "and", "or", "in", "not"}
        unsupported = []
        observed_nodes = set()
        observed_operators = set()
        observed_builtins = set()
        for rule_id in sorted(target_ids):
            rule = catalog.get(rule_id)
            self.assertIsNotNone(rule, rule_id)
            if rule_id in self.DIRECT_RULE_IDS:
                self.assertFalse(
                    any(
                        isinstance(node, validation.Call)
                        for node in self.walk(rule.condition_ast)
                    ),
                    rule_id,
                )
            elif rule_id == "val_aliases_casefold_case_sensitive_consistency":
                self.assertIsInstance(rule.condition_ast, validation.Sequence)
                self.assertEqual(len(rule.condition_ast.statements), 2)
                self.assertTrue(
                    all(
                        isinstance(statement, validation.Call)
                        and statement.function == "when"
                        and len(statement.arguments) == 2
                        for statement in rule.condition_ast.statements
                    )
                )
                guarded_operators = {
                    node.operator
                    for node in self.walk(rule.condition_ast)
                    if isinstance(node, validation.BinaryOperation)
                }
                self.assertLessEqual(guarded_operators, {"==", "!="}, rule_id)
            else:
                self.assertIsInstance(rule.condition_ast, validation.Call, rule_id)
                self.assertEqual(rule.condition_ast.function, "when", rule_id)
                guarded_operators = {
                    node.operator
                    for node in self.walk(rule.condition_ast)
                    if isinstance(node, validation.BinaryOperation)
                }
                self.assertLessEqual(guarded_operators, {"==", "!="}, rule_id)
            for node in self.walk(rule.condition_ast):
                observed_nodes.add(type(node))
                if type(node) not in allowed_nodes:
                    unsupported.append((rule_id, type(node).__name__))
                if isinstance(node, (validation.UnaryOperation, validation.BinaryOperation)):
                    observed_operators.add(node.operator)
                    if node.operator not in allowed_operators:
                        unsupported.append((rule_id, node.operator))
                if isinstance(node, validation.Call):
                    observed_builtins.add(node.function)
                    if node.function != "when" or len(node.arguments) != 2:
                        unsupported.append((rule_id, node.function))

        self.assertEqual(unsupported, [])
        self.assertEqual(observed_nodes, allowed_nodes)
        self.assertEqual(observed_operators, allowed_operators)
        self.assertEqual(observed_builtins, {"when"})

    def test_target_greater_equal_operands_are_integer_integer(self):
        catalog, context = execution_tests.current_corpus_catalog_and_context()
        observed_pairs = []
        for rule_id in sorted(self.DIRECT_RULE_IDS | self.GUARDED_RULE_IDS):
            rule = catalog.get(rule_id)
            namespace = context.namespace_for_component(rule.component_identity)
            schema = context.table("schema_fields", namespace=namespace)
            field_types = {
                record.get("field_name"): record.get("data_type")
                for record in schema
                if record.get("table_id") == rule.target_table_id
                and record.get("status") == "active"
            }
            for node in self.walk(rule.condition_ast):
                if not (
                    isinstance(node, validation.BinaryOperation)
                    and node.operator == ">="
                ):
                    continue
                pair = []
                for operand in (node.left, node.right):
                    if isinstance(operand, validation.Identifier):
                        pair.append(field_types.get(operand.name))
                    elif isinstance(operand, validation.Literal):
                        pair.append(operand.literal_kind)
                    else:
                        pair.append(type(operand).__name__)
                observed_pairs.append(tuple(pair))
        self.assertEqual(len(observed_pairs), 7)
        self.assertEqual(set(observed_pairs), {("integer", "integer")})


if __name__ == "__main__":
    unittest.main()
