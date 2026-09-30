import sys
import unittest

from test_canonical_validation_execution import (
    current_corpus_catalog_and_context,
    execution,
    make_context,
    make_rule,
    validation_expr,
)


evaluator = sys.modules["canonical_validation_expr_eval"]
custom_expression = sys.modules["canonical_validation_custom_expression"]

E2_RULE_IDS = {
    "cdb_val_card_localization_name_nonblank",
    "cdb_val_export_manifest_filename_policy",
    "cdb_val_set_localization_name_nonblank",
    "val_localization_display_name_nonblank",
    "val_source_registry_active_checksum_finalized",
    "val_source_registry_path_nonblank",
}


def literal(value):
    if value is None:
        return validation_expr.Literal("null", None)
    if type(value) is bool:
        return validation_expr.Literal("boolean", value)
    if type(value) is int:
        return validation_expr.Literal("integer", value)
    return validation_expr.Literal("string", value)


def call(name, *values):
    return validation_expr.Call(name, tuple(literal(value) for value in values))


def evaluate(node):
    return evaluator.evaluate_validation_expression(node, {})


def make_custom_rule(source="trim(value) != \"\""):
    return make_rule(
        validation_rule_id="custom_e2_test",
        validation_kind_id="custom_expression",
        condition_expression=source,
        operator_id="#NULL",
        comparison_value="#NULL",
        target_table_id="items",
        target_field_id="fld_items_value",
    )


class TestTrimBuiltin(unittest.TestCase):
    def test_exact_unicode_edge_whitespace_contract(self):
        cases = (
            ("abc", "abc"),
            (" abc", "abc"),
            ("abc ", "abc"),
            (" abc ", "abc"),
            ("\tabc\n", "abc"),
            ("\u2003abc\u00a0", "abc"),
            ("a  b", "a  b"),
            ("", ""),
            ("   ", ""),
            (" Árvíztűrő ", "Árvíztűrő"),
        )
        for source, expected in cases:
            with self.subTest(source=source):
                self.assertEqual(evaluate(call("trim", source)), expected)

    def test_null_wrong_types_and_wrong_arity_fail_closed(self):
        cases = (
            call("trim", None),
            call("trim", True),
            call("trim", 1),
            validation_expr.Call("trim", ()),
            validation_expr.Call("trim", (literal("a"), literal("b"))),
        )
        for node in cases:
            with self.subTest(node=node):
                with self.assertRaises(
                    evaluator.ValidationExpressionEvaluationError
                ):
                    evaluate(node)

    def test_repeat_is_deterministic(self):
        node = call("trim", "\u2003 Árvíztűrő \n")
        self.assertEqual(tuple(evaluate(node) for _ in range(10)), ("Árvíztűrő",) * 10)


class TestStartsWithBuiltin(unittest.TestCase):
    def test_exact_case_sensitive_prefix_contract(self):
        cases = (
            ("sha256:abc", "sha256:", True),
            ("abc", "z", False),
            ("SHA256:abc", "sha256:", False),
            ("abc", "", True),
            ("ab", "abc", False),
            ("árvíz", "ár", True),
        )
        for value, prefix, expected in cases:
            with self.subTest(value=value, prefix=prefix):
                self.assertIs(evaluate(call("starts_with", value, prefix)), expected)

    def test_null_wrong_types_and_wrong_arity_fail_closed(self):
        cases = (
            call("starts_with", None, "x"),
            call("starts_with", "x", None),
            call("starts_with", 1, "1"),
            call("starts_with", "1", True),
            validation_expr.Call("starts_with", (literal("x"),)),
            validation_expr.Call(
                "starts_with", (literal("x"), literal("x"), literal("x"))
            ),
        )
        for node in cases:
            with self.subTest(node=node):
                with self.assertRaises(
                    evaluator.ValidationExpressionEvaluationError
                ):
                    evaluate(node)

    def test_repeat_is_deterministic(self):
        node = call("starts_with", "sha256:abc", "sha256:")
        self.assertEqual(tuple(evaluate(node) for _ in range(10)), (True,) * 10)


class TestMatchesBuiltin(unittest.TestCase):
    PATTERN = r"^carddatabase\.[a-z0-9_]+\.json$"

    def test_current_pattern_accepts_only_current_filename_shape(self):
        cases = (
            ("carddatabase.cards.json", True),
            ("carddatabase.ability_effects.json", True),
            ("CARDDATABASE.cards.json", False),
            ("cards.json", False),
            ("carddatabase.cards.JSON", False),
            ("carddatabase.cards.json.bak", False),
            ("carddatabase..json", False),
            ("carddatabase.card-name.json", False),
        )
        for value, expected in cases:
            with self.subTest(value=value):
                self.assertIs(evaluate(call("matches", value, self.PATTERN)), expected)

    def test_malformed_or_unsupported_patterns_fail_closed(self):
        patterns = (
            r"^[a-z$",
            r"^a|b$",
            r"^(?=a)a$",
            r"^(?i)a$",
            r"^(a)$",
            r"^(a+)\1$",
            r"^a*$",
            r"a+",
        )
        for pattern in patterns:
            with self.subTest(pattern=pattern):
                with self.assertRaises(
                    evaluator.ValidationExpressionEvaluationError
                ):
                    evaluate(call("matches", "a", pattern))

    def test_resource_limits_fail_closed(self):
        with self.assertRaises(evaluator.ValidationExpressionEvaluationError):
            evaluate(
                call(
                    "matches",
                    "a" * (evaluator.MATCHES_MAX_INPUT_LENGTH + 1),
                    r"^a+$",
                )
            )
        with self.assertRaises(evaluator.ValidationExpressionEvaluationError):
            evaluate(
                call(
                    "matches",
                    "a",
                    "^" + "a" * evaluator.MATCHES_MAX_PATTERN_LENGTH + "$",
                )
            )

    def test_null_wrong_types_and_wrong_arity_fail_closed(self):
        cases = (
            call("matches", None, self.PATTERN),
            call("matches", "x", None),
            call("matches", 1, self.PATTERN),
            call("matches", "x", True),
            validation_expr.Call("matches", (literal("x"),)),
            validation_expr.Call(
                "matches", (literal("x"), literal("^x$"), literal("extra"))
            ),
        )
        for node in cases:
            with self.subTest(node=node):
                with self.assertRaises(
                    evaluator.ValidationExpressionEvaluationError
                ):
                    evaluate(node)

    def test_repeat_is_deterministic(self):
        node = call("matches", "carddatabase.cards.json", self.PATTERN)
        self.assertEqual(tuple(evaluate(node) for _ in range(10)), (True,) * 10)


class TestE2CapabilityGate(unittest.TestCase):
    def test_current_corpus_has_exactly_six_supported_rules(self):
        catalog, _ = current_corpus_catalog_and_context()
        custom_rules = catalog.by_kind("custom_expression")
        supported = tuple(
            rule
            for rule in custom_rules
            if custom_expression.scalar_string_pattern_capability_reason(rule) is None
        )

        self.assertEqual(len(custom_rules), 57)
        self.assertEqual({rule.rule_id for rule in supported}, E2_RULE_IDS)
        self.assertEqual(
            sum(rule.validation_stage_id == "pre_export" for rule in supported), 5
        )
        self.assertEqual(
            sum(rule.validation_stage_id == "production_export" for rule in supported),
            1,
        )
        self.assertTrue(all(rule.blocking for rule in supported))
        self.assertEqual(
            {
                rule.rule_id: rule.condition_expression_source
                for rule in supported
            },
            {
                "cdb_val_card_localization_name_nonblank": 'trim(card_name) != ""',
                "cdb_val_export_manifest_filename_policy": (
                    'when(export_enabled == true, matches(export_file,'
                    '"^carddatabase\\\\.[a-z0-9_]+\\\\.json$"))'
                ),
                "cdb_val_set_localization_name_nonblank": 'trim(set_name) != ""',
                "val_localization_display_name_nonblank": (
                    'trim(display_name) != ""'
                ),
                "val_source_registry_active_checksum_finalized": (
                    'when(status == "active" and source_kind != "external_reference", '
                    'checksum not in [null,"#TBD"] and '
                    'starts_with(checksum,"sha256:"))'
                ),
                "val_source_registry_path_nonblank": 'trim(path_or_uri) != ""',
            },
        )

    def test_representative_other_families_remain_not_executed(self):
        catalog, context = current_corpus_catalog_and_context()
        by_id = {rule.rule_id: rule for rule in catalog.rules}
        representatives = (
            "cdb_val_export_manifest_json_only",
            "cdb_val_card_keywords_sequence_contiguous",
            "cdb_val_export_manifest_complete_coverage",
            "cdb_val_effect_destination_parameter_context",
            "cdb_val_schema_headers_match",
        )
        for rule_id in representatives:
            rule = by_id[rule_id]
            with self.subTest(rule_id=rule_id):
                self.assertIsNotNone(
                    custom_expression.scalar_string_pattern_capability_reason(rule)
                )
                result = execution.execute_scalar_string_pattern_custom_expression_rule(
                    rule, context
                )
                self.assertIs(
                    result.outcome, execution.ValidationOutcome.NOT_EXECUTED
                )
                self.assertEqual(result.evaluated_record_count, 0)
                self.assertEqual(result.violation_count, 0)

    def test_gate_requires_an_e2_builtin_even_for_simple_when_expression(self):
        rule = make_custom_rule('when(value == "x", value == "x")')
        self.assertEqual(
            custom_expression.scalar_string_pattern_capability_reason(rule),
            "e2_builtin_not_used",
        )

    def test_unsupported_operator_or_helper_fails_closed_before_any_record(self):
        for source in (
            'trim(value) == "x" or value == "y"',
            'trim(value) != "" and count_rows() == 1',
        ):
            with self.subTest(source=source):
                rule = make_custom_rule(source)
                self.assertEqual(
                    custom_expression.scalar_string_pattern_capability_reason(rule),
                    "expression_shape_not_supported",
                )
                result = execution.execute_scalar_string_pattern_custom_expression_rule(
                    rule, make_context(({"item_id": "a", "value": "a"},))
                )
                self.assertIs(result.outcome, execution.ValidationOutcome.NOT_EXECUTED)
                self.assertEqual(result.evaluated_record_count, 0)


class TestE2Executor(unittest.TestCase):
    def test_row_scope_has_no_implicit_lifecycle_filter(self):
        rule = make_custom_rule()
        result = execution.execute_scalar_string_pattern_custom_expression_rule(
            rule,
            make_context(
                (
                    {"item_id": "active", "value": "ok", "status": "active"},
                    {"item_id": "inactive", "value": " ", "status": "inactive"},
                )
            ),
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(result.evaluated_record_count, 2)
        self.assertEqual(result.violation_count, 1)
        self.assertEqual(result.diagnostics[0].record_identity, "inactive")

    def test_missing_or_wrong_typed_field_is_controlled_failure(self):
        rule = make_custom_rule()
        result = execution.execute_scalar_string_pattern_custom_expression_rule(
            rule,
            make_context(
                (
                    {"item_id": "missing"},
                    {"item_id": "null", "value": None},
                    {"item_id": "integer", "value": 1},
                )
            ),
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(result.evaluated_record_count, 3)
        self.assertEqual(result.violation_count, 3)
        self.assertTrue(
            all(
                diagnostic.code
                == execution.VALIDATION_CUSTOM_EXPRESSION_EVALUATION_ERROR
                for diagnostic in result.diagnostics
            )
        )

    def test_record_order_does_not_change_result(self):
        rule = make_custom_rule()
        records = (
            {"item_id": "b", "value": " "},
            {"item_id": "a", "value": "ok"},
        )
        forward = execution.execute_scalar_string_pattern_custom_expression_rule(
            rule, make_context(records)
        )
        reverse = execution.execute_scalar_string_pattern_custom_expression_rule(
            rule, make_context(tuple(reversed(records)))
        )
        self.assertEqual(forward, reverse)


class TestCurrentE2CorpusExecution(unittest.TestCase):
    @staticmethod
    def execute(reverse=False):
        catalog, context = current_corpus_catalog_and_context(reverse=reverse)
        selected = tuple(
            rule
            for rule in catalog.rules
            if custom_expression.scalar_string_pattern_capability_reason(rule) is None
        )
        return selected, tuple(
            execution.execute_scalar_string_pattern_custom_expression_rule(rule, context)
            for rule in selected
        )

    def test_exact_six_rules_execute_with_authoritative_outcomes(self):
        selected, results = self.execute()
        outcomes = {result.rule_id: result.outcome for result in results}
        self.assertEqual({rule.rule_id for rule in selected}, E2_RULE_IDS)
        self.assertEqual(
            {
                rule_id
                for rule_id, outcome in outcomes.items()
                if outcome is execution.ValidationOutcome.PASS
            },
            E2_RULE_IDS - {"val_source_registry_active_checksum_finalized"},
        )
        self.assertIs(
            outcomes["val_source_registry_active_checksum_finalized"],
            execution.ValidationOutcome.FAIL,
        )

    def test_reversed_corpus_is_deterministic(self):
        self.assertEqual(self.execute(), self.execute(reverse=True))

    def test_four_trim_rule_record_counts_and_no_blank_values(self):
        _, context = current_corpus_catalog_and_context()
        selected, results = self.execute()
        by_id = dict(zip((rule.rule_id for rule in selected), results))
        cases = (
            ("val_source_registry_path_nonblank", "registry", "source_registry", "path_or_uri", 21),
            ("val_localization_display_name_nonblank", "registry", "localization", "display_name", 167),
            ("cdb_val_set_localization_name_nonblank", "carddatabase", "set_localization", "set_name", 6),
            ("cdb_val_card_localization_name_nonblank", "carddatabase", "card_localization", "card_name", 814),
        )
        for rule_id, namespace, table_id, field, count in cases:
            with self.subTest(rule_id=rule_id):
                values = tuple(row.get(field) for row in context.table(table_id, namespace=namespace))
                self.assertEqual(len(values), count)
                self.assertEqual(sum(value is None for value in values), 0)
                self.assertEqual(sum(value == "" for value in values), 0)
                self.assertEqual(sum(type(value) is str and bool(value) and value.strip() == "" for value in values), 0)
                self.assertEqual(sum(type(value) is str and bool(value.strip()) for value in values), count)
                self.assertIs(by_id[rule_id].outcome, execution.ValidationOutcome.PASS)
                self.assertEqual(by_id[rule_id].evaluated_record_count, count)
                self.assertEqual(by_id[rule_id].diagnostics, ())

    def test_current_export_manifest_guard_and_pattern(self):
        _, context = current_corpus_catalog_and_context()
        rows = context.table("export_manifest", namespace="carddatabase")
        enabled = tuple(row for row in rows if row.get("export_enabled") is True)
        self.assertEqual(len(rows), 30)
        self.assertEqual(len(enabled), 29)
        self.assertEqual(sum(row.get("export_enabled") is False for row in rows), 1)
        self.assertTrue(
            all(
                evaluate(call("matches", row["export_file"], TestMatchesBuiltin.PATTERN))
                for row in enabled
            )
        )
        _, results = self.execute()
        result = next(
            result for result in results
            if result.rule_id == "cdb_val_export_manifest_filename_policy"
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.PASS)
        self.assertEqual(result.evaluated_record_count, 30)
        self.assertEqual(result.diagnostics, ())

    def test_current_production_checksum_guard_and_exact_violations(self):
        _, context = current_corpus_catalog_and_context()
        rows = context.table("source_registry", namespace="registry")
        guarded = tuple(
            row for row in rows
            if row.get("status") == "active"
            and row.get("source_kind") != "external_reference"
        )
        expected_ids = {
            "src_base_rules_1_4",
            "src_card_design_catalog_1_1",
            "src_carddatabase_schema_0_7_0",
            "src_excel_structure_1_2",
            "src_expansion_rules_1_4",
            "src_lookups_v2_schema_0_5_1",
            "src_project_map_1_7",
            "src_workflow_data_1_2",
        }
        self.assertEqual(len(rows), 21)
        self.assertEqual(len(guarded), 8)
        self.assertEqual(len(rows) - len(guarded), 13)
        self.assertEqual({row["source_id"] for row in guarded}, expected_ids)
        self.assertEqual(sum(row["checksum"] is None for row in guarded), 0)
        self.assertEqual(sum(row["checksum"] == "#TBD" for row in guarded), 8)
        self.assertEqual(sum(type(row["checksum"]) is str and row["checksum"].startswith("sha256:") for row in guarded), 0)
        self.assertEqual(sum(type(row["checksum"]) is str and row["checksum"] != "#TBD" and not row["checksum"].startswith("sha256:") for row in guarded), 0)
        _, results = self.execute()
        result = next(
            result for result in results
            if result.rule_id == "val_source_registry_active_checksum_finalized"
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(result.evaluated_record_count, 21)
        self.assertEqual(result.violation_count, 8)
        self.assertEqual({item.record_identity for item in result.diagnostics}, expected_ids)
        self.assertTrue(
            all(
                item.code == execution.VALIDATION_CUSTOM_EXPRESSION_FAILED
                for item in result.diagnostics
            )
        )


if __name__ == "__main__":
    unittest.main()
