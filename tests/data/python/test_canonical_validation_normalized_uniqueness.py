import json
import subprocess
import sys
import unittest
from collections import Counter, defaultdict
from dataclasses import replace
from unittest.mock import patch

import test_canonical_validation_execution as base
import test_canonical_validation_stage as stage_tests


execution = base.execution
expr = base.validation_expr
family = sys.modules["canonical_validation_normalized_uniqueness"]
evaluator = sys.modules["canonical_validation_expr_eval"]
stage = stage_tests.stage
parse = expr.parse_validation_expression
ALIASES = (
    'for_each_group(["group_id",normalize(alias_value,normalization_mode,case_sensitive)], '
    'count_distinct(canonical_registry_value_id) == 1)'
)
MIGRATION = (
    'for_each_group(["source_system_id","legacy_group",normalize(legacy_value,"trim_casefold",false)], '
    'count_distinct(target_record_id) <= 1)'
)
TARGETS = {
    "val_aliases_normalized_target_conflict": ("aliases", "alias_value", ALIASES),
    "val_migration_map_normalized_legacy_conflict": ("migration_map", "legacy_value", MIGRATION),
}


def make_rule(source=ALIASES, *, table="aliases", field="alias_value"):
    return base.make_rule(
        validation_rule_id="synthetic_normalized_uniqueness",
        validation_kind_id="normalized_uniqueness",
        rule_scope_id="table",
        target_table_id=table,
        target_field_id=f"fld_{table}_{field}",
        condition_expression=source,
        operator_id="#NULL",
        comparison_value="#NULL",
    )


def make_context(rows, *, table="aliases", field="alias_value", reverse=False):
    tables = {
        table: tuple(reversed(rows)) if reverse else tuple(rows),
        "schema_tables": ({"table_id": table, "primary_key": "id", "status": "active"},),
        "schema_fields": ({
            "field_id": f"fld_{table}_{field}", "field_name": field,
            "table_id": table, "status": "active",
        },),
    }
    return execution.ValidationDataContext(tables)


def alias(identity, value="ignis", target="realm_ignis", **overrides):
    return {
        "id": identity, "group_id": "realm", "alias_value": value,
        "canonical_registry_value_id": target,
        "normalization_mode": "trim_casefold", "case_sensitive": False,
        "status": "inactive", **overrides,
    }


def migration(identity, value="old", target="new", **overrides):
    return {
        "id": identity, "source_system_id": "legacy", "legacy_group": "realm",
        "legacy_value": value, "target_record_id": target,
        "status": "inactive", **overrides,
    }


def run_rows(rows, *, migration_rule=False, source=None, reverse=False):
    table, field, expression = (
        ("migration_map", "legacy_value", MIGRATION)
        if migration_rule else ("aliases", "alias_value", ALIASES)
    )
    rule = make_rule(source or expression, table=table, field=field)
    context = make_context(rows, table=table, field=field, reverse=reverse)
    return execution.execute_normalized_uniqueness_rule(rule, context)


class E4TestCase(unittest.TestCase):
    def assert_error(self, function, *args, reason=None):
        with self.assertRaises(evaluator.ValidationExpressionEvaluationError) as raised:
            function(*args)
        if reason is not None:
            self.assertEqual(dict(raised.exception.context)["reason"], reason)

    def assert_pass(self, result, count):
        self.assertIs(result.outcome, execution.ValidationOutcome.PASS)
        self.assertEqual(result.evaluated_record_count, count)
        self.assertEqual((result.violation_count, result.diagnostics), (0, ()))


class TestCompositeGrouping(E4TestCase):
    def test_one_two_three_ordered_components(self):
        row = {"a": "realm", "b": "ignis", "c": 7}
        for source, expected in (
            ('["a"]', (("str", "realm"),)),
            ('["a","b"]', (("str", "realm"), ("str", "ignis"))),
            ('["a","b","c"]', (("str", "realm"), ("str", "ignis"), ("int", 7))),
        ):
            with self.subTest(source=source):
                self.assertEqual(family.composite_group_key(parse(source), row), expected)

    def test_component_order_is_significant(self):
        row = {"a": "realm", "b": "ignis"}
        first = family.composite_group_key(parse('["a","b"]'), row)
        second = family.composite_group_key(parse('["b","a"]'), row)
        self.assertNotEqual(first, second)
        self.assertEqual(first, tuple(reversed(second)))

    def test_type_aware_components_and_explicit_null(self):
        values = (True, 1, 1.0, "1", None)
        keys = {family.composite_group_key(parse('["value"]'), {"value": v}) for v in values}
        self.assertEqual(len(keys), len(values))
        self.assertIn((("null", None),), keys)

    def test_key_is_immutable_and_independent_of_source_mutation(self):
        row = {"a": "realm"}
        key = family.composite_group_key(parse('["a"]'), row)
        row["a"] = "changed"
        self.assertEqual(key, (("str", "realm"),))
        with self.assertRaises(TypeError):
            key[0] = ("str", "changed")

    def test_missing_component_is_not_null(self):
        self.assert_error(
            family.composite_group_key, parse('["missing"]'), {}, reason="identifier_missing"
        )

    def test_malformed_key_and_non_scalar_components_fail_closed(self):
        for source in ('[]', '["a","a","a","a"]', '[a]', '[null]', '[""]'):
            with self.subTest(source=source):
                self.assert_error(family.composite_group_key, parse(source), {"a": "x"})
        for value in ({"x": "y"}, [1], (1,), float("nan"), float("inf")):
            with self.subTest(value=value):
                self.assert_error(family.composite_group_key, parse('["a"]'), {"a": value})

    def test_whole_rule_preserves_typed_and_null_group_components(self):
        rows = tuple(alias(str(i), target=str(i), group_id=v) for i, v in enumerate((True, 1, "1", None)))
        self.assert_pass(run_rows(rows), 4)
        self.assertEqual(run_rows(rows), run_rows(rows, reverse=True))


class TestNormalizeGrouping(E4TestCase):
    def key(self, value, mode, case):
        return family.composite_group_key(
            parse('[normalize(value,mode,case)]'), {"value": value, "mode": mode, "case": case}
        )

    def test_exact_true_preserves_every_character(self):
        for value in (" IGNIS ", "Straße", "E\u0301", "\u200bname\u200b", ""):
            with self.subTest(value=value):
                self.assertEqual(self.key(value, "exact", True), (("str", value),))

    def test_trim_casefold_reuses_unicode_strip_casefold_only(self):
        for value, expected in (
            (" IGNIS ", "ignis"), ("\u2003Straße\u2003", "strasse"),
            ("A  B", "a  b"), ("E\u0301", "e\u0301"), ("\u200bA\u200b", "\u200ba\u200b"),
        ):
            with self.subTest(value=value):
                self.assertEqual(self.key(value, "trim_casefold", False), (("str", expected),))
        self.assertNotEqual(self.key("É", "trim_casefold", False), self.key("E\u0301", "trim_casefold", False))

    def test_raw_differences_merge_but_group_ids_remain_independent(self):
        self.assertEqual(self.key(" IGNIS ", "trim_casefold", False), self.key("ignis", "trim_casefold", False))
        self.assert_pass(run_rows((alias("a"), alias("b", " IGNIS ", "other", group_id="other"))), 2)

    def test_invalid_modes_types_and_combinations_fail_even_for_null(self):
        for value in ("value", None):
            for mode, case in (("exact", False), ("trim_casefold", True), ("unknown", False), (None, False), ("exact", 1)):
                with self.subTest(value=value, mode=mode, case=case):
                    self.assert_error(self.key, value, mode, case)
        for value in (True, 1, 1.2, [], {}):
            with self.subTest(value=value):
                self.assert_error(self.key, value, "exact", True)

    def test_explicit_null_is_local_to_grouping_not_global_normalize(self):
        self.assertEqual(self.key(None, "trim_casefold", False), (("null", None),))
        self.assertEqual(self.key(None, "exact", True), (("null", None),))
        self.assert_error(
            evaluator.evaluate_validation_expression,
            parse('normalize(value,"trim_casefold",false)'), {"value": None},
            reason="normalize_value_type_invalid",
        )

    def test_missing_value_mode_or_case_and_wrong_arity_fail_closed(self):
        for field in ("value", "mode", "case"):
            row = {"value": None, "mode": "trim_casefold", "case": False}
            del row[field]
            with self.subTest(field=field):
                self.assert_error(family.composite_group_key, parse('[normalize(value,mode,case)]'), row)
        for arguments in ((), (expr.Identifier("value"),), (expr.Identifier("value"),) * 4):
            key = expr.ListLiteral((expr.Call("normalize", arguments),))
            self.assert_error(family.composite_group_key, key, {"value": "x"})


class TestCountDistinct(E4TestCase):
    def count(self, values):
        return family.evaluate_count_distinct(parse('count_distinct(value)'), tuple({"value": v} for v in values))

    def test_non_null_distinct_vectors_and_reversed_order(self):
        for values, expected in (
            (("A",), 1), (("A", "A"), 1), (("A", "B"), 2),
            ((None, None), 0), (("A", None), 1), (("A", "A", None), 1),
            (("A", "B", None), 2), ((), 0),
        ):
            with self.subTest(values=values):
                self.assertEqual(self.count(values), expected)
                self.assertEqual(self.count(tuple(reversed(values))), expected)

    def test_types_and_string_case_are_exact(self):
        self.assertEqual(self.count((True, 1, 1.0, "1", None)), 4)
        self.assertEqual(self.count(("A", "a", " A ")), 3)

    def test_literal_scalar_expression_is_evaluated_per_record(self):
        self.assertEqual(family.evaluate_count_distinct(parse('count_distinct("A")'), ({}, {})), 1)
        self.assertEqual(family.evaluate_count_distinct(parse('count_distinct(null)'), ({}, {})), 0)

    def test_missing_field_record_collection_and_nonfinite_are_rejected(self):
        self.assert_error(family.evaluate_count_distinct, parse('count_distinct(value)'), ({},), reason="identifier_missing")
        for value in ({"x": 1}, ["A"], ("A",), float("nan"), float("inf")):
            with self.subTest(value=value):
                self.assert_error(self.count, (value,))
        self.assert_error(family.evaluate_count_distinct, parse('count_distinct(["A"])'), ({},))
        self.assert_error(family.evaluate_count_distinct, parse('count_distinct(value)'), (None,))

    def test_wrong_arity_and_absent_group_context_are_controlled(self):
        for arguments in ((), (expr.Identifier("value"),) * 2):
            self.assert_error(
                family.evaluate_count_distinct, expr.Call("count_distinct", arguments), (),
                reason="builtin_arity_invalid",
            )
        for group in (None, "value", {}, iter(())):
            self.assert_error(family.evaluate_count_distinct, parse('count_distinct(value)'), group)


class TestWholeRulesAndDiagnostics(E4TestCase):
    def test_aliases_pass_unique_repeated_target_and_independent_groups(self):
        for rows in (
            (alias("a"),),
            (alias("a"), alias("b", " IGNIS ")),
            (alias("a"), alias("b", "ignis", "other", group_id="other")),
            (alias("a"), alias("b", "aqua", "realm_aqua")),
        ):
            with self.subTest(rows=rows):
                self.assert_pass(run_rows(rows), len(rows))

    def test_aliases_conflict_identifies_normalized_key_targets_and_every_row(self):
        rows = (alias("z", " IGNIS "), alias("a", "ignis", "realm_aqua"), alias("m", "ignis", None))
        result = run_rows(rows)
        self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual((result.evaluated_record_count, result.violation_count), (3, 1))
        diagnostic, = result.diagnostics
        self.assertEqual(diagnostic.code, family.VALIDATION_NORMALIZED_UNIQUENESS_CONFLICT)
        self.assertEqual(json.loads(diagnostic.observed_value), {
            "group_key": [["str", "realm"], ["str", "ignis"]],
            "non_null_targets": [["str", "realm_aqua"], ["str", "realm_ignis"]],
        })
        self.assertEqual(diagnostic.related_record_identities, ("a", "m", "z"))
        self.assertEqual(result, run_rows(rows, reverse=True))

    def test_aliases_all_null_targets_fail_naturally(self):
        result = run_rows((alias("a", target=None), alias("b", target=None)))
        self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(result.violation_count, 1)
        self.assertEqual(json.loads(result.diagnostics[0].observed_value)["non_null_targets"], [])

    def test_migration_pass_vectors_and_nullable_legacy(self):
        for targets in (("A",), ("A", "A"), ("A", None), (None, None), ("A", "A", None)):
            for legacy_value in (" OLD ", None):
                rows = tuple(migration(str(i), legacy_value, target) for i, target in enumerate(targets))
                with self.subTest(targets=targets, legacy_value=legacy_value):
                    self.assert_pass(run_rows(rows, migration_rule=True), len(rows))
        self.assert_pass(run_rows((migration("a", " OLD "), migration("b", "old")), migration_rule=True), 2)

    def test_migration_source_and_legacy_group_are_independent(self):
        rows = (
            migration("a", target="A"), migration("b", target="B", source_system_id="other"),
            migration("c", target="C", legacy_group="other"), migration("d", target="D", legacy_group=None),
        )
        self.assert_pass(run_rows(rows, migration_rule=True), 4)

    def test_migration_two_targets_fail_including_null_legacy_groups(self):
        for targets in (("A", "B"), ("A", "B", None)):
            for value in ("old", None):
                rows = tuple(migration(str(i), value, target) for i, target in enumerate(targets))
                with self.subTest(targets=targets, value=value):
                    result = run_rows(rows, migration_rule=True)
                    self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
                    self.assertEqual(result.violation_count, 1)
                    self.assertEqual(result, run_rows(rows, migration_rule=True, reverse=True))
                    observed = json.loads(result.diagnostics[0].observed_value)
                    self.assertEqual(observed["group_key"][-1], ["null", None] if value is None else ["str", value])
                    self.assertEqual(observed["non_null_targets"], [["str", "A"], ["str", "B"]])

    def test_no_lifecycle_or_null_row_filtering(self):
        rows = (migration("a", None, "A", status="active"), migration("b", None, "B", status="deprecated"), migration("c", None, None))
        result = run_rows(rows, migration_rule=True)
        self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(result.evaluated_record_count, 3)
        self.assertEqual(result.diagnostics[0].related_record_identities, ("a", "b", "c"))

    def test_count_distinct_typed_values_are_preserved_in_diagnostics(self):
        result = run_rows((alias("a", target=True), alias("b", target=1)))
        self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(json.loads(result.diagnostics[0].observed_value)["non_null_targets"], [["bool", True], ["int", 1]])

    def test_missing_group_normalize_and_target_fields_are_controlled_failures(self):
        for field in ("group_id", "alias_value", "normalization_mode", "case_sensitive", "canonical_registry_value_id"):
            row = alias("a")
            del row[field]
            with self.subTest(field=field):
                result = run_rows((row,))
                self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
                self.assertEqual(result.evaluated_record_count, 1)
                self.assertEqual(result.diagnostics[0].code, family.VALIDATION_NORMALIZED_UNIQUENESS_EVALUATION_ERROR)
                self.assertIn("identifier_missing", result.diagnostics[0].reason)

    def test_one_component_key_executes_and_empty_table_passes(self):
        source = 'for_each_group([normalize(alias_value,normalization_mode,case_sensitive)], count_distinct(canonical_registry_value_id) == 1)'
        self.assert_pass(run_rows((alias("a"), alias("b", " IGNIS ")), source=source), 2)
        self.assert_pass(run_rows(()), 0)
        self.assert_pass(run_rows((), migration_rule=True), 0)

    def test_multiple_violations_and_errors_have_stable_identity(self):
        rows = (
            alias("d", " AQUA ", "A"), alias("c", "aqua", "B"),
            alias("b", "IGNIS", "C"), alias("a", "ignis", "D"),
            alias("invalid", normalization_mode="unknown"),
        )
        result = run_rows(rows)
        self.assertEqual(result.violation_count, 3)
        self.assertEqual(result, run_rows(rows, reverse=True))
        self.assertEqual(result, run_rows(rows[2:] + rows[:2]))


class TestExecutorBoundary(E4TestCase):
    def test_facade_identity_and_stage_registration(self):
        self.assertIs(execution.execute_normalized_uniqueness_rule, family.execute_normalized_uniqueness_rule)
        self.assertIs(stage.DEFAULT_PRE_EXPORT_EXECUTORS["normalized_uniqueness"], family.execute_normalized_uniqueness_rule)
        for name in ("VALIDATION_NORMALIZED_UNIQUENESS_CONFLICT", "VALIDATION_NORMALIZED_UNIQUENESS_EVALUATION_ERROR"):
            self.assertEqual(getattr(execution, name), getattr(family, name))

    def test_shape_dispatch_is_independent_of_rule_identity(self):
        rule = replace(make_rule(), rule_id="renamed_rule")
        self.assert_pass(execution.execute_normalized_uniqueness_rule(rule, make_context((alias("a"),))), 1)

    def test_other_kinds_stages_scopes_and_structured_contracts_are_unsupported(self):
        rule = make_rule()
        changes = (
            {"validation_kind_id": "custom_expression"}, {"validation_kind_id": "uniqueness"},
            {"validation_kind_id": "cross_field_consistency"}, {"validation_kind_id": "target_group_membership"},
            {"validation_stage_id": "runtime_load"}, {"validation_stage_id": "production_export"},
            {"rule_scope_id": "row"}, {"target_field_id": None}, {"comparison_value": "x"},
        )
        for change in changes:
            with self.subTest(change=change):
                result = execution.execute_normalized_uniqueness_rule(replace(rule, **change), make_context(()))
                self.assertIs(result.outcome, execution.ValidationOutcome.UNSUPPORTED)
                self.assertEqual((result.evaluated_record_count, result.violation_count), (0, 0))

    def test_nearby_expression_shapes_stay_closed_even_on_empty_tables(self):
        sources = (
            ALIASES.replace("== 1", "!= 1"), ALIASES.replace("== 1", "== 2"),
            ALIASES.replace("== 1", "== true"), ALIASES.replace("== 1", ">= 1"),
            ALIASES.replace('normalize(alias_value,normalization_mode,case_sensitive)', '"alias_value"'),
            'for_each_group("group_id", count_distinct(canonical_registry_value_id) == 1)',
            ALIASES.replace('count_distinct(canonical_registry_value_id)', 'count_rows()'),
            ALIASES.replace('count_distinct(canonical_registry_value_id)', 'count_distinct("target")'),
            ALIASES.replace('["group_id",', '["a","b","c",'),
        )
        for source in sources:
            with self.subTest(source=source):
                result = run_rows((), source=source)
                self.assertIs(result.outcome, execution.ValidationOutcome.UNSUPPORTED)

    def test_missing_namespace_table_schema_and_identity_fail_closed(self):
        rule = make_rule()
        context = make_context((alias("a"),))
        for tables in (
            {"schema_tables": context.table("schema_tables"), "schema_fields": context.table("schema_fields")},
            {"aliases": context.table("aliases"), "schema_fields": context.table("schema_fields")},
            {"aliases": context.table("aliases"), "schema_tables": context.table("schema_tables")},
        ):
            self.assertIs(execution.execute_normalized_uniqueness_rule(rule, execution.ValidationDataContext(tables)).outcome, execution.ValidationOutcome.FAIL)
        namespaced = execution.ValidationDataContext(namespaced_tables={"registry": {"aliases": ()}})
        self.assertEqual(execution.execute_normalized_uniqueness_rule(rule, namespaced).diagnostics[0].reason, "source_namespace_missing")
        self.assertIs(run_rows((alias(None),)).outcome, execution.ValidationOutcome.FAIL)
        mismatch = replace(rule, target_field_id="fld_aliases_other")
        self.assertEqual(execution.execute_normalized_uniqueness_rule(mismatch, context).diagnostics[0].reason, "target_normalized_field_unresolved")

    def test_programming_errors_propagate_to_the_stage_boundary(self):
        with patch.object(family, "evaluate_validation_expression", side_effect=RuntimeError("sentinel")):
            with self.assertRaises(RuntimeError):
                run_rows((alias("a"),))
            with self.assertRaises(stage.ValidationStageExecutionError) as raised:
                stage.run_validation_stage(base.rules.ValidationRuleCatalog((make_rule(),)), "pre_export", make_context((alias("a"),)))
            self.assertIsInstance(raised.exception.__cause__, RuntimeError)

    def test_direct_and_package_imports_work_without_cycles(self):
        for package in (False, True):
            directory = base.MODULE_DIRECTORY.parent if package else base.MODULE_DIRECTORY
            prefix = "canonical_export." if package else ""
            script = (
                f"import sys; sys.path.insert(0, {str(directory)!r}); "
                f"from {prefix}canonical_validation_normalized_uniqueness import execute_normalized_uniqueness_rule as direct; "
                f"from {prefix}canonical_validation_execution import execute_normalized_uniqueness_rule as facade; "
                f"from {prefix}canonical_validation_stage import DEFAULT_PRE_EXPORT_EXECUTORS; "
                "assert direct is facade is DEFAULT_PRE_EXPORT_EXECUTORS['normalized_uniqueness']"
            )
            completed = subprocess.run([sys.executable, "-B", "-c", script], capture_output=True, text=True, check=False)
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)


class TestCurrentE4Corpus(E4TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog, cls.context = base.current_corpus_catalog_and_context()
        cls.reversed_catalog, cls.reversed_context = base.current_corpus_catalog_and_context(reverse=True)

    def test_exact_two_rules_have_expected_contract_and_pass(self):
        selected = self.catalog.by_kind("normalized_uniqueness")
        self.assertEqual({r.rule_id for r in selected}, set(TARGETS))
        for rule in selected:
            table, field, source = TARGETS[rule.rule_id]
            with self.subTest(rule=rule.rule_id):
                self.assertEqual((rule.target_table_id, rule.target_field_id, rule.condition_expression_source), (table, f"fld_{table}_{field}", source))
                self.assertEqual((rule.component_identity, rule.validation_stage_id, rule.rule_scope_id, rule.severity_id, rule.blocking), ("REGISTRY.xlsx", "pre_export", "table", "critical", True))
                rows = self.context.table(table, namespace="registry")
                self.assert_pass(execution.execute_normalized_uniqueness_rule(rule, self.context), len(rows))

    def test_current_group_statistics_include_all_nullable_rows(self):
        expected = {
            "aliases": (95, 95, 0, {1: 95}),
            "migration_map": (85, 36, 3, {0: 19, 1: 17}),
        }
        for rule in self.catalog.by_kind("normalized_uniqueness"):
            rows = self.context.table(rule.target_table_id, namespace="registry")
            key, predicate = rule.condition_ast.arguments
            groups = defaultdict(list)
            for row in rows:
                groups[family.composite_group_key(key, row)].append(row)
            counts = Counter(family.evaluate_count_distinct(predicate.left, group) for group in groups.values())
            with self.subTest(table=rule.target_table_id):
                self.assertEqual((len(rows), len(groups), sum(len(g) > 1 for g in groups.values()), dict(counts)), expected[rule.target_table_id])
                self.assertEqual(sum(len(g) for g in groups.values()), len(rows))
                if rule.target_table_id == "aliases":
                    self.assertEqual(Counter(r["normalization_mode"] for r in rows), {"trim_casefold": 94, "exact": 1})
                    self.assertEqual(Counter(r["case_sensitive"] for r in rows), {False: 94, True: 1})
                else:
                    self.assertEqual(sum(r["legacy_value"] is None for r in rows), 68)
                    self.assertEqual(sum(r["target_record_id"] is None for r in rows), 68)

    def test_reversed_corpus_and_context_return_identical_results(self):
        for rule in self.catalog.by_kind("normalized_uniqueness"):
            with self.subTest(rule=rule.rule_id):
                self.assertEqual(
                    execution.execute_normalized_uniqueness_rule(rule, self.context),
                    execution.execute_normalized_uniqueness_rule(self.reversed_catalog.get(rule.rule_id), self.reversed_context),
                )

    def test_exact_stage_delta_preserves_every_other_rule_result(self):
        # Keep this assertion scoped to the historical E4 activation boundary.
        registry_after = {
            kind: executor for kind, executor in stage.DEFAULT_PRE_EXPORT_EXECUTORS.items()
            if kind not in {"cross_field_consistency", "target_group_membership"}
        }
        registry_before = dict(registry_after)
        del registry_before["normalized_uniqueness"]
        before = stage.run_validation_stage(self.catalog, "pre_export", self.context, registry_before)
        after = stage.run_validation_stage(self.catalog, "pre_export", self.context, registry_after)
        old = {e.rule.rule_id: e.execution for e in before.rule_results}
        new = {e.rule.rule_id: e.execution for e in after.rule_results}
        self.assertEqual({rule_id for rule_id in old if old[rule_id] != new[rule_id]}, set(TARGETS))
        self.assertEqual((before.pass_count, before.fail_count, before.unsupported_count, before.not_executed_count), (240, 1, 0, 46))
        self.assertEqual((after.pass_count, after.fail_count, after.unsupported_count, after.not_executed_count), (242, 1, 0, 44))
        self.assertEqual((before.blocking_pass_count, before.blocking_fail_count, before.blocking_not_executed_count), (240, 0, 45))
        self.assertEqual((after.blocking_pass_count, after.blocking_fail_count, after.blocking_not_executed_count), (242, 0, 43))
        self.assertIs(new["cdb_val_printings_default_unique_per_card"].outcome, execution.ValidationOutcome.NOT_EXECUTED)
        for kind in ("cross_field_consistency", "target_group_membership"):
            for rule in self.catalog.by_kind(kind):
                self.assertIs(new[rule.rule_id].outcome, execution.ValidationOutcome.NOT_EXECUTED)
        for rule_id in TARGETS:
            self.assertIs(old[rule_id].outcome, execution.ValidationOutcome.NOT_EXECUTED)
            self.assertIs(new[rule_id].outcome, execution.ValidationOutcome.PASS)
            self.assertEqual(new[rule_id], execution.execute_normalized_uniqueness_rule(self.catalog.get(rule_id), self.context))

    def test_no_other_current_shape_is_supported_by_family(self):
        supported = {
            rule.rule_id for rule in self.catalog.rules
            if execution.execute_normalized_uniqueness_rule(rule, self.context).outcome is not execution.ValidationOutcome.UNSUPPORTED
        }
        self.assertEqual(supported, set(TARGETS))


if __name__ == "__main__":
    unittest.main()
