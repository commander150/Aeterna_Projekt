import sys
import unittest
from collections import defaultdict
from dataclasses import FrozenInstanceError, replace

from test_canonical_validation_execution import (
    current_corpus_catalog_and_context,
    execution,
    make_context,
    make_rule,
    validation_expr,
)


contiguous = sys.modules["canonical_validation_contiguous_order"]
evaluator = sys.modules["canonical_validation_expr_eval"]
EXPRESSION = (
    'for_each_group("group", '
    'sorted_unique(value) == range(1,count_rows()+1))'
)
CURRENT_RULES = {
    "val_contract_fields_order_contiguous": (
        "registry", "contract_fields", "contract_schema_id", "field_order",
        237, 33, 1, 15, 1, 15,
    ),
    "cdb_val_schema_fields_order_contiguous": (
        "carddatabase", "schema_fields", "table_id", "column_order",
        391, 30, 4, 25, 1, 25,
    ),
    "cdb_val_card_keywords_sequence_contiguous": (
        "carddatabase", "card_keywords", "card_id", "sequence",
        399, 344, 1, 3, 1, 3,
    ),
    "cdb_val_deck_entries_sequence_contiguous": (
        "carddatabase", "deck_entries", "deck_id", "entry_index",
        32, 2, 15, 17, 1, 17,
    ),
}


def parse(source):
    return validation_expr.parse_validation_expression(source)


def literal(value):
    if value is None:
        return validation_expr.Literal("null", None)
    if type(value) is bool:
        return validation_expr.Literal("boolean", value)
    if type(value) is int:
        return validation_expr.Literal("integer", value)
    return validation_expr.Literal("string", value)


def call(function, *values):
    return validation_expr.Call(function, tuple(literal(value) for value in values))


def group(*values):
    return contiguous.GroupEvaluationContext(
        "group", "a", tuple({"group": "a", "value": value} for value in values)
    )


def records(groups):
    return tuple(
        {"group": group_id, "value": value, "status": "inactive"}
        for group_id, values in groups
        for value in values
    )


def make_contiguous_rule(source=EXPRESSION):
    return make_rule(
        validation_rule_id="synthetic_contiguous_rule",
        rule_scope_id="table",
        validation_kind_id="custom_expression",
        condition_expression=source,
        operator_id="#NULL",
        comparison_value="#NULL",
        target_table_id="items",
        target_field_id="fld_items_value",
    )


class H7TestCase(unittest.TestCase):
    def assert_evaluation_error(self, function, *args, **expected):
        with self.assertRaises(evaluator.ValidationExpressionEvaluationError) as raised:
            function(*args)
        details = dict(raised.exception.context)
        for key, value in expected.items():
            self.assertEqual(details.get(key), value)
        return raised.exception


class TestGroupContextAndForEachGroup(H7TestCase):
    def test_one_multiple_and_reversed_groups(self):
        cases = (
            records((('a', (1,)),)),
            records((('a', (1, 2, 3)), ('b', (3, 1, 2)))),
            records((('b', (3, 1, 2)), ('a', (1, 2, 3)))),
        )
        for rows in cases:
            with self.subTest(rows=rows):
                self.assertIs(contiguous.evaluate_contiguous_expression(parse(EXPRESSION), rows), True)
                self.assertIs(contiguous.evaluate_contiguous_expression(parse(EXPRESSION), tuple(reversed(rows))), True)

    def test_null_group_is_its_own_typed_group(self):
        rows = records(((None, (1, 2)), ("a", (1,))))
        self.assertIs(contiguous.evaluate_contiguous_expression(parse(EXPRESSION), rows), True)
        self.assertIs(contiguous.evaluate_contiguous_expression(parse(EXPRESSION), tuple(reversed(rows))), True)

    def test_bool_and_integer_group_keys_do_not_alias(self):
        rows = records(((True, (1,)), (1, (1, 2))))
        self.assertIs(contiguous.evaluate_contiguous_expression(parse(EXPRESSION), rows), True)

    def test_missing_group_field_is_controlled(self):
        self.assert_evaluation_error(
            contiguous.evaluate_contiguous_expression,
            parse(EXPRESSION),
            ({"value": 1},),
            builtin="for_each_group",
            reason="group_field_missing",
        )

    def test_empty_table_is_vacuously_true(self):
        self.assertIs(contiguous.evaluate_contiguous_expression(parse(EXPRESSION), ()), True)

    def test_one_or_multiple_false_groups_make_expression_false(self):
        for rows in (
            records((('a', (1,)), ('b', (1, 3)))),
            records((('a', (1, 3)), ('b', (2, 3)))),
        ):
            with self.subTest(rows=rows):
                self.assertIs(contiguous.evaluate_contiguous_expression(parse(EXPRESSION), rows), False)

    def test_wrong_arity_and_group_name_type_fail_closed(self):
        bad_calls = (
            validation_expr.Call("for_each_group", (literal("group"),)),
            validation_expr.Call("for_each_group", (literal(1), literal(True))),
            validation_expr.Call("for_each_group", (literal(""), literal(True))),
        )
        for node in bad_calls:
            with self.subTest(node=node):
                self.assert_evaluation_error(contiguous.evaluate_contiguous_expression, node, ())

    def test_group_context_is_snapshot_immutable(self):
        source = {"group": "a", "value": 1}
        context = contiguous.GroupEvaluationContext("group", "a", (source,))
        source["value"] = 7
        self.assertEqual(context.records[0]["value"], 1)
        with self.assertRaises(TypeError):
            context.records[0]["value"] = 7
        with self.assertRaises(FrozenInstanceError):
            context.records = ()


class TestGroupBuiltins(H7TestCase):
    def test_count_rows_exact_integer_and_scope(self):
        node = validation_expr.Call("count_rows", ())
        self.assertEqual(contiguous.evaluate_group_expression(node, group(1)), 1)
        self.assertEqual(contiguous.evaluate_group_expression(node, group(1, 2, 3)), 3)
        self.assert_evaluation_error(
            contiguous.evaluate_group_expression,
            node,
            None,
            builtin="count_rows",
            reason="group_context_missing",
        )
        self.assert_evaluation_error(
            contiguous.evaluate_group_expression,
            call("count_rows", 1),
            group(1),
            builtin="count_rows",
            reason="builtin_arity_invalid",
        )

    def test_sorted_unique_exact_integer_collection(self):
        node = validation_expr.Call("sorted_unique", (validation_expr.Identifier("value"),))
        for values, expected in (
            ((1, 2, 3), (1, 2, 3)),
            ((3, 1, 2), (1, 2, 3)),
            ((1, 2, 2), (1, 2)),
            ((0, -1, 2), (-1, 0, 2)),
        ):
            with self.subTest(values=values):
                self.assertEqual(contiguous.evaluate_group_expression(node, group(*values)), expected)

    def test_sorted_unique_invalid_values_and_missing_field(self):
        node = validation_expr.Call("sorted_unique", (validation_expr.Identifier("value"),))
        for value in (None, True, "1"):
            with self.subTest(value=value):
                self.assert_evaluation_error(
                    contiguous.evaluate_group_expression,
                    node,
                    group(value),
                    builtin="sorted_unique",
                    reason="order_value_not_integer",
                )
        missing = contiguous.GroupEvaluationContext("group", "a", ({"group": "a"},))
        self.assert_evaluation_error(
            contiguous.evaluate_group_expression,
            node,
            missing,
            reason="order_field_missing",
        )
        self.assert_evaluation_error(
            contiguous.evaluate_group_expression,
            node,
            None,
            reason="group_context_missing",
        )

    def test_sorted_unique_wrong_arity_and_field_type(self):
        for node in (
            validation_expr.Call("sorted_unique", ()),
            call("sorted_unique", "value"),
            validation_expr.Call("sorted_unique", (validation_expr.Identifier("value"), literal(1))),
        ):
            with self.subTest(node=node):
                self.assert_evaluation_error(contiguous.evaluate_group_expression, node, group(1))

    def test_range_is_half_open_and_exact_integer(self):
        for start, end, expected in (
            (1, 4, (1, 2, 3)),
            (1, 2, (1,)),
            (1, 1, ()),
            (3, 1, ()),
        ):
            with self.subTest(start=start, end=end):
                self.assertEqual(tuple(contiguous.evaluate_group_expression(call("range", start, end), None)), expected)
        enormous = contiguous.evaluate_group_expression(
            call("range", 1, 10**100), None
        )
        self.assertIsInstance(enormous, range)
        self.assertEqual(tuple(enormous[:3]), (1, 2, 3))
        for node in (
            call("range", True, 4),
            call("range", "1", 4),
            call("range", None, 4),
            call("range", 1, False),
            call("range", 1),
            call("range", 1, 2, 3),
        ):
            with self.subTest(node=node):
                self.assert_evaluation_error(contiguous.evaluate_group_expression, node, None)

    def test_plus_only_accepts_exact_integers(self):
        for a, b, expected in ((1, 2, 3), (-1, 1, 0)):
            node = validation_expr.BinaryOperation("+", literal(a), literal(b))
            self.assertEqual(contiguous.evaluate_group_expression(node, None), expected)
        for a, b in ((True, 1), (1, "2"), (None, 1)):
            node = validation_expr.BinaryOperation("+", literal(a), literal(b))
            self.assert_evaluation_error(
                contiguous.evaluate_group_expression,
                node,
                None,
                operator=None,
                reason="integer_operands_required",
            )

    def test_sequence_equality_is_ordered_and_type_aware(self):
        self.assertTrue(contiguous._sequence_equal((1, 2), (1, 2)))
        self.assertFalse(contiguous._sequence_equal((1, 2), (2, 1)))
        self.assertFalse(contiguous._sequence_equal((1, 2), (1, 2, 3)))
        self.assertFalse(contiguous._sequence_equal((1,), (True,)))
        self.assertFalse(contiguous._sequence_equal((1,), range(1, 10**100)))


class TestWholeContiguousExpression(H7TestCase):
    def test_canonical_positive_and_negative_examples(self):
        for values, expected in (
            ((1,), True),
            ((1, 2, 3), True),
            ((3, 2, 1), True),
            ((1, 3), False),
            ((1, 2, 2), False),
            ((0, 1, 2), False),
            ((-1, 1, 2), False),
            ((2, 3, 4), False),
            ((1, 2, 4), False),
        ):
            with self.subTest(values=values):
                rows = records((('a', values),))
                self.assertIs(contiguous.evaluate_contiguous_expression(parse(EXPRESSION), rows), expected)

    def test_no_implicit_active_filter(self):
        rule = make_contiguous_rule()
        result = execution.execute_supported_custom_expression_rule(
            rule,
            make_context(
                (
                    {"item_id": "a", "group": "x", "value": 1, "status": "active"},
                    {"item_id": "b", "group": "x", "value": 3, "status": "inactive"},
                )
            ),
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(result.evaluated_record_count, 2)
        self.assertEqual(result.violation_count, 1)
        self.assertIsNone(result.diagnostics[0].record_identity)

    def test_malformed_value_yields_one_controlled_table_diagnostic(self):
        rule = make_contiguous_rule()
        result = execution.execute_supported_custom_expression_rule(
            rule,
            make_context(({"item_id": "a", "group": "x", "value": True},)),
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(result.violation_count, 1)
        self.assertEqual(
            result.diagnostics[0].code,
            contiguous.VALIDATION_CONTIGUOUS_EVALUATION_ERROR,
        )

    def test_repeated_and_reordered_execution_is_deterministic(self):
        rule = make_contiguous_rule()
        rows = (
            {"item_id": "b", "group": "y", "value": 2},
            {"item_id": "a", "group": "x", "value": 1},
            {"item_id": "c", "group": "y", "value": 1},
        )
        results = tuple(
            execution.execute_supported_custom_expression_rule(rule, make_context(order))
            for order in (rows, tuple(reversed(rows)), rows)
        )
        self.assertEqual(results, (results[0],) * 3)


class TestH7CapabilityGate(unittest.TestCase):
    def test_exact_four_current_rules_and_no_fifth(self):
        catalog, _ = current_corpus_catalog_and_context()
        custom = catalog.by_kind("custom_expression")
        supported = tuple(
            rule for rule in custom
            if contiguous.contiguous_ordering_capability_reason(rule) is None
        )
        self.assertEqual(len(custom), 57)
        self.assertEqual({rule.rule_id for rule in supported}, set(CURRENT_RULES))
        self.assertTrue(all(rule.validation_stage_id == "pre_export" and rule.blocking for rule in supported))
        self.assertEqual(
            {rule.rule_id: rule.condition_expression_source for rule in supported},
            {
                "val_contract_fields_order_contiguous": (
                    'for_each_group("contract_schema_id", sorted_unique(field_order) == range(1,count_rows()+1))'
                ),
                "cdb_val_schema_fields_order_contiguous": (
                    'for_each_group("table_id", sorted_unique(column_order) == range(1,count_rows()+1))'
                ),
                "cdb_val_card_keywords_sequence_contiguous": (
                    'for_each_group("card_id", sorted_unique(sequence) == range(1,count_rows()+1))'
                ),
                "cdb_val_deck_entries_sequence_contiguous": (
                    'for_each_group("deck_id", sorted_unique(entry_index) == range(1,count_rows()+1))'
                ),
            },
        )

    def test_shape_not_rule_id_and_unrelated_families_stay_closed(self):
        matching = replace(make_contiguous_rule(), rule_id="renamed_shape")
        self.assertIsNone(contiguous.contiguous_ordering_capability_reason(matching))
        unrelated = (
            'for_each_group("group", count_rows() == 1)',
            'for_each_group("group", sorted_unique(value) == range(0,count_rows()+1))',
            'for_each_group("group", sorted_unique(value) == range(1,count_rows()+2))',
            'for_each_group("group", sorted_unique(value) != range(1,count_rows()+1))',
        )
        for source in unrelated:
            with self.subTest(source=source):
                rule = make_contiguous_rule(source)
                self.assertIsNotNone(contiguous.contiguous_ordering_capability_reason(rule))

    def test_exact_delta_preserves_e2_and_other_custom_rules(self):
        catalog, context = current_corpus_catalog_and_context()
        custom = catalog.by_kind("custom_expression")
        e2 = {
            rule.rule_id for rule in custom
            if execution.scalar_string_pattern_capability_reason(rule) is None
        }
        e3 = {
            rule.rule_id for rule in custom
            if contiguous.contiguous_ordering_capability_reason(rule) is None
        }
        self.assertEqual(len(e2), 6)
        self.assertEqual(e3, set(CURRENT_RULES))
        self.assertFalse(e2 & e3)
        for rule in custom:
            result = execution.execute_supported_custom_expression_rule(rule, context)
            with self.subTest(rule_id=rule.rule_id):
                if rule.rule_id in e2 | e3:
                    self.assertIn(result.outcome, {execution.ValidationOutcome.PASS, execution.ValidationOutcome.FAIL})
                else:
                    self.assertIs(result.outcome, execution.ValidationOutcome.NOT_EXECUTED)
                    self.assertEqual(result.evaluated_record_count, 0)
                    self.assertEqual(result.violation_count, 0)

    def test_other_validation_kinds_stay_unexecuted(self):
        catalog, context = current_corpus_catalog_and_context()
        for kind in (
            "normalized_uniqueness",
            "target_group_membership",
            "cross_field_consistency",
        ):
            selected = catalog.by_kind(kind)
            self.assertTrue(selected, kind)
            for rule in selected:
                result = execution.execute_supported_custom_expression_rule(rule, context)
                self.assertIs(result.outcome, execution.ValidationOutcome.NOT_EXECUTED)


class TestCurrentH7Corpus(unittest.TestCase):
    def test_each_rule_has_exact_clean_group_statistics(self):
        catalog, context = current_corpus_catalog_and_context()
        by_id = {rule.rule_id: rule for rule in catalog.rules}
        for rule_id, spec in CURRENT_RULES.items():
            namespace, table_id, group_field, order_field, row_count, group_count, min_size, max_size, order_min, order_max = spec
            with self.subTest(rule_id=rule_id):
                rows = context.table(table_id, namespace=namespace)
                groups = defaultdict(list)
                for row in rows:
                    groups[row[group_field]].append(row[order_field])
                sizes = tuple(map(len, groups.values()))
                values = tuple(value for group_values in groups.values() for value in group_values)
                duplicate_count = sum(len(group_values) - len(set(group_values)) for group_values in groups.values())
                affected = {
                    group_id for group_id, group_values in groups.items()
                    if tuple(sorted(set(group_values))) != tuple(range(1, len(group_values) + 1))
                }
                missing_positions = sum(
                    len(set(range(1, len(group_values) + 1)) - set(group_values))
                    for group_values in groups.values()
                )
                self.assertEqual((len(rows), len(groups)), (row_count, group_count))
                self.assertEqual((min(sizes), max(sizes)), (min_size, max_size))
                self.assertEqual((min(values), max(values)), (order_min, order_max))
                self.assertEqual(duplicate_count, 0)
                self.assertEqual(missing_positions, 0)
                self.assertEqual(affected, set())
                result = execution.execute_supported_custom_expression_rule(by_id[rule_id], context)
                self.assertIs(result.outcome, execution.ValidationOutcome.PASS)
                self.assertEqual(result.evaluated_record_count, row_count)
                self.assertEqual(result.diagnostics, ())

    def test_reversed_corpus_and_context_are_deterministic(self):
        catalog, context = current_corpus_catalog_and_context()
        reversed_catalog, reversed_context = current_corpus_catalog_and_context(reverse=True)
        for rule_id in CURRENT_RULES:
            rule = next(rule for rule in catalog.rules if rule.rule_id == rule_id)
            reversed_rule = next(rule for rule in reversed_catalog.rules if rule.rule_id == rule_id)
            self.assertEqual(
                execution.execute_supported_custom_expression_rule(rule, context),
                execution.execute_supported_custom_expression_rule(reversed_rule, reversed_context),
            )


if __name__ == "__main__":
    unittest.main()
