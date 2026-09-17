import subprocess
import sys
import unittest
from collections import Counter
from dataclasses import replace
from unittest.mock import patch

import test_canonical_validation_execution as base
import test_canonical_validation_qualified_reference as qualified
import test_canonical_validation_stage as stage_tests


execution = base.execution
expr = base.validation_expr
family = sys.modules["canonical_validation_reference_constraints"]
evaluator = sys.modules["canonical_validation_expr_eval"]
stage = stage_tests.stage
parse = expr.parse_validation_expression
GROUP_EXPRESSION = (
    'expected_group = map(relation_type_id,{"known":"event_kind","other":"modifier_kind"}); '
    'expected_group == null or group_of(target_registry_value_id) == expected_group'
)
CROSS_EXPRESSION = (
    'when(authority_level == "canonical_technical_source" and status == "active", '
    'version == lookup("meta","key","schema_version","value"))'
)
TARGETS = {
    "target_group_membership": "val_value_relations_target_group_mapping",
    "cross_field_consistency": "val_source_registry_technical_version_matches_meta",
}
EXECUTORS = {
    "target_group_membership": execution.execute_target_group_membership_rule,
    "cross_field_consistency": execution.execute_cross_field_consistency_rule,
}


def make_rule(kind="target_group_membership", source=None):
    group = kind == "target_group_membership"
    rule = base.make_rule(
        validation_rule_id="synthetic_reference_constraint",
        validation_kind_id=kind, rule_scope_id="record" if group else "cross_table",
        target_table_id="items",
        target_field_id="fld_items_target_registry_value_id" if group else "fld_items_version",
        condition_expression=source or (GROUP_EXPRESSION if group else CROSS_EXPRESSION),
        operator_id="#NULL", comparison_value="#NULL",
        reference_table_id="value_registry" if group else "meta",
        reference_field_id="fld_value_registry_registry_value_id" if group else "fld_meta_value",
    )
    return replace(rule, component_identity="registry-component")


def group_row(identity="row", **overrides):
    return {
        "item_id": identity, "relation_type_id": "known",
        "target_registry_value_id": "event_kind_resolve", "status": "inactive", **overrides,
    }


def source_row(identity="row", **overrides):
    return {
        "item_id": identity, "authority_level": "canonical_technical_source",
        "status": "active", "version": "0.5.1", **overrides,
    }


def tables(rows=(), *, meta=({"key": "schema_version", "value": "0.5.1"},), registry=None):
    result = qualified.namespace_tables(items=rows, value_registry=registry)
    result["schema_tables"] += ({"table_id": "meta", "primary_key": "key", "status": "active"},)
    result["schema_fields"] += tuple(
        qualified.field_schema("items", name) for name in ("relation_type_id", "authority_level", "status", "version")
    ) + (qualified.field_schema("meta", "key"), qualified.field_schema("meta", "value", nullable=True))
    if meta is not None:
        result["meta"] = tuple(meta)
    return result


def execute(rows, *, kind="target_group_membership", source=None, reverse=False, **options):
    context = qualified.make_context(registry=tables(rows, **options), reverse=reverse)
    return EXECUTORS[kind](make_rule(kind, source), context)


class E5TestCase(unittest.TestCase):
    def assert_pass(self, result, count):
        self.assertIs(result.outcome, execution.ValidationOutcome.PASS)
        self.assertEqual((result.evaluated_record_count, result.violation_count, result.diagnostics), (count, 0, ()))

    def assert_failure(self, result, count=1):
        self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(result.violation_count, count)
        self.assertEqual(len(result.diagnostics), count)


class TestTargetGroupMembership(E5TestCase):
    def test_known_mapping_correct_group_passes_and_wrong_group_fails(self):
        self.assert_pass(execute((group_row(),)), 1)
        result = execute((group_row(target_registry_value_id="modifier_kind_add"),))
        self.assert_failure(result)
        self.assertEqual(result.diagnostics[0].code, family.VALIDATION_TARGET_GROUP_MEMBERSHIP_FAILED)
        self.assertEqual(result.diagnostics[0].record_identity, "row")

    def test_mapping_is_read_from_expression_not_from_rule_identity(self):
        source = GROUP_EXPRESSION.replace('"known":"event_kind"', '"known":"modifier_kind"')
        self.assert_pass(execute((group_row(target_registry_value_id="modifier_kind_add"),), source=source), 1)
        rule = replace(make_rule(source=source), rule_id="renamed_rule")
        result = EXECUTORS[rule.validation_kind_id](rule, qualified.make_context(registry=tables((group_row(target_registry_value_id="modifier_kind_add"),))))
        self.assert_pass(result, 1)

    def test_unknown_and_case_different_relation_short_circuit_group_resolution(self):
        rows = (group_row("a", relation_type_id="unknown"), group_row("b", relation_type_id="KNOWN", target_registry_value_id=None))
        missing = {"item_id": "c", "relation_type_id": "not_mapped"}
        context_tables = tables(rows + (missing,))
        del context_tables["value_registry"]
        with patch.object(family, "_resolve_registry_value", side_effect=AssertionError("unexpected resolution")) as resolver:
            result = EXECUTORS["target_group_membership"](make_rule(), qualified.make_context(registry=context_tables))
            self.assert_pass(result, 3)
            resolver.assert_not_called()

    def test_group_case_and_target_identity_are_exact_without_alias_fallback(self):
        registry = ({"registry_value_id": "event_kind_resolve", "group_id": "Event_Kind", "value_id": "resolve"},)
        self.assert_failure(execute((group_row(),), registry=registry))
        for target in ("resolve", "EVENT_KIND_RESOLVE", "event_kind_resolve ", "unknown"):
            with self.subTest(target=target):
                self.assert_failure(execute((group_row(target_registry_value_id=target),)))

    def test_required_missing_and_malformed_targets_fail_closed(self):
        for value in (None, "", 1, True):
            with self.subTest(value=value):
                result = execute((group_row(target_registry_value_id=value),))
                self.assert_failure(result)
                self.assertEqual(result.diagnostics[0].code, family.VALIDATION_REFERENCE_CONSTRAINT_EVALUATION_ERROR)
        row = group_row()
        del row["target_registry_value_id"]
        self.assert_failure(execute((row,)))

    def test_duplicate_registry_identity_is_fail_closed_and_deterministic(self):
        registry = (
            {"registry_value_id": "event_kind_resolve", "group_id": "event_kind", "value_id": "resolve"},
            {"registry_value_id": "event_kind_resolve", "group_id": "modifier_kind", "value_id": "other"},
        )
        rows = (group_row("z"), group_row("a"))
        result = execute(rows, registry=registry)
        self.assert_failure(result, 2)
        self.assertEqual(result, execute(rows, registry=registry, reverse=True))
        self.assertTrue(all(d.reason == "lookup_ambiguous" for d in result.diagnostics))
        self.assertTrue(all(d.related_record_identities for d in result.diagnostics))

    def test_missing_registry_table_field_or_malformed_group_fails_closed(self):
        for registry in (
            ({"registry_value_id": "event_kind_resolve", "value_id": "resolve"},),
            ({"registry_value_id": "event_kind_resolve", "value_id": "resolve", "group_id": ""},),
            ({"registry_value_id": "event_kind_resolve", "value_id": "resolve", "group_id": None},),
        ):
            self.assert_failure(execute((group_row(),), registry=registry))
        data = tables((group_row(),))
        del data["value_registry"]
        self.assert_failure(EXECUTORS["target_group_membership"](make_rule(), qualified.make_context(registry=data)))

    def test_map_key_is_exact_nonempty_string_and_missing_is_failure(self):
        for value in (None, "", True, 1):
            with self.subTest(value=value):
                self.assert_failure(execute((group_row(relation_type_id=value),)))
        row = group_row()
        del row["relation_type_id"]
        self.assert_failure(execute((row,)))

    def test_map_rejects_malformed_keys_values_duplicates_and_arity(self):
        for items in ((("known", 1),), (("known", None),), ((None, "event_kind"),), (("", "event_kind"),), (("known", ""),), (("known", "a"), ("known", "b"))):
            node = expr.Call("map", (expr.Identifier("key"), expr.MapLiteral(items)))
            with self.subTest(items=items), self.assertRaises(evaluator.ValidationExpressionEvaluationError):
                family.evaluate_group_mapping(node, {"key": "known"})
        for args in ((), (expr.Identifier("key"),), (expr.Identifier("key"), expr.Literal("string", "x"))):
            with self.assertRaises(evaluator.ValidationExpressionEvaluationError):
                family.evaluate_group_mapping(expr.Call("map", args), {"key": "known"})

    def test_unknown_map_key_returns_canonical_none_and_known_value_is_unchanged(self):
        node = parse('map(key,{"known":"Event_Kind"})')
        self.assertEqual(family.evaluate_group_mapping(node, {"key": "known"}), "Event_Kind")
        self.assertIsNone(family.evaluate_group_mapping(node, {"key": "KNOWN"}))

    def test_source_order_and_inactive_rows_preserve_diagnostics(self):
        rows = (group_row("z", target_registry_value_id="modifier_kind_add"), group_row("a", target_registry_value_id="missing"), group_row("m"))
        result = execute(rows)
        self.assert_failure(result, 2)
        self.assertEqual(result.evaluated_record_count, 3)
        self.assertEqual(result, execute(rows, reverse=True))
        self.assertEqual(tuple(d.record_identity for d in result.diagnostics), ("a", "z"))

    def test_binding_does_not_overwrite_source_field_or_expand_global_map(self):
        self.assert_failure(execute((group_row(expected_group="event_kind"),)))
        with self.assertRaises(evaluator.ValidationExpressionUnsupportedError):
            evaluator.evaluate_validation_expression(parse(GROUP_EXPRESSION), group_row())


class TestCrossFieldConsistency(E5TestCase):
    def run_cross(self, rows, **options):
        return execute(rows, kind="cross_field_consistency", **options)

    def test_active_technical_source_equal_passes_different_fails(self):
        self.assert_pass(self.run_cross((source_row(),)), 1)
        result = self.run_cross((source_row(version="0.5.2"),))
        self.assert_failure(result)
        self.assertEqual(result.diagnostics[0].code, family.VALIDATION_CROSS_FIELD_CONSISTENCY_FAILED)

    def test_false_guards_skip_missing_meta_and_predicate_fields(self):
        rows = (
            source_row("inactive", status="inactive"),
            source_row("nontechnical", authority_level="other"),
            {"item_id": "missing_version", "authority_level": "canonical_technical_source", "status": "inactive"},
        )
        with patch.object(family, "_resolve_scalar_lookup", side_effect=AssertionError("unexpected lookup")) as resolver:
            self.assert_pass(self.run_cross(rows, meta=None), 3)
            resolver.assert_not_called()

    def test_one_meta_match_returns_exact_scalar_and_zero_returns_none(self):
        for meta, expected in (
            (({"key": "schema_version", "value": "0.5.1"},), "0.5.1"),
            (({"key": "unrelated", "value": "0.5.1"},), None),
            ((), None),
        ):
            with self.subTest(meta=meta):
                context = qualified.make_context(registry=tables(meta=meta))
                value = family._resolve_scalar_lookup(context, "registry", "meta", "key", "schema_version", "value")
                self.assertEqual(value, expected)
                result = self.run_cross((source_row(),), meta=meta)
                self.assertIs(result.outcome, execution.ValidationOutcome.PASS if expected is not None else execution.ValidationOutcome.FAIL)

    def test_duplicate_lookup_never_selects_first_or_last(self):
        meta = ({"key": "schema_version", "value": "0.5.1"}, {"key": "schema_version", "value": "0.5.2"})
        result = self.run_cross((source_row(),), meta=meta)
        self.assert_failure(result)
        self.assertEqual(result.diagnostics[0].reason, "lookup_ambiguous")
        self.assertEqual(result, self.run_cross((source_row(),), meta=tuple(reversed(meta))))

    def test_missing_meta_table_key_output_and_schema_fail_closed(self):
        for meta in (None, ({"value": "0.5.1"},), ({"key": "schema_version"},)):
            with self.subTest(meta=meta):
                self.assert_failure(self.run_cross((source_row(),), meta=meta))
        for field in ("key", "value"):
            data = tables((source_row(),))
            data["schema_fields"] = tuple(f for f in data["schema_fields"] if f["field_id"] != f"fld_meta_{field}")
            self.assert_failure(EXECUTORS["cross_field_consistency"](make_rule("cross_field_consistency"), qualified.make_context(registry=data)))

    def test_equality_has_no_case_whitespace_or_type_coercion(self):
        meta = ({"key": "schema_version", "value": "ReleaseA"},)
        self.assert_pass(self.run_cross((source_row(version="ReleaseA"),), meta=meta), 1)
        for version in ("releasea", " ReleaseA", "ReleaseA ", True, 1, None):
            with self.subTest(version=version):
                self.assert_failure(self.run_cross((source_row(version=version),), meta=meta))
        self.assert_failure(self.run_cross((source_row(version=1),), meta=({"key": "schema_version", "value": "1"},)))

    def test_missing_source_fields_fail_only_when_evaluated(self):
        for field in ("authority_level", "status", "version"):
            row = source_row()
            del row[field]
            with self.subTest(field=field):
                self.assert_failure(self.run_cross((row,)))

    def test_no_namespace_fallback_to_another_meta_table(self):
        registry = tables((source_row(),), meta=None)
        context = qualified.make_context(registry=registry, carddatabase=tables())
        result = EXECUTORS["cross_field_consistency"](make_rule("cross_field_consistency"), context)
        self.assert_failure(result)
        self.assertEqual(result.diagnostics[0].reason, "lookup_table_missing")

    def test_reversed_meta_and_source_rows_preserve_success_and_failure(self):
        rows = (source_row("z", version="wrong"), source_row("a"), source_row("m", version="also_wrong"))
        meta = ({"key": "unrelated", "value": "x"}, {"key": "schema_version", "value": "0.5.1"})
        result = self.run_cross(rows, meta=meta)
        self.assert_failure(result, 2)
        self.assertEqual(result, self.run_cross(rows, meta=meta, reverse=True))
        self.assertEqual(tuple(d.record_identity for d in result.diagnostics), ("m", "z"))


class TestE5CapabilityBoundary(E5TestCase):
    def test_public_facade_and_registration_are_explicit(self):
        for kind, executor in EXECUTORS.items():
            self.assertIs(stage.DEFAULT_PRE_EXPORT_EXECUTORS[kind], executor)
            self.assertIs(getattr(family, executor.__name__), executor)

    def test_each_executor_rejects_other_kinds_stages_scopes_and_contracts(self):
        for kind, executor in EXECUTORS.items():
            rule = make_rule(kind)
            for changes in (
                {"validation_kind_id": "custom_expression"}, {"validation_kind_id": "definition_invariant"},
                {"validation_kind_id": "normalized_uniqueness"},
                {"validation_stage_id": "runtime_load"}, {"validation_stage_id": "production_export"},
                {"rule_scope_id": "table"}, {"target_field_id": None}, {"reference_table_id": "other"},
                {"reference_field_id": "other"}, {"comparison_value": "x"},
            ):
                with self.subTest(kind=kind, changes=changes):
                    result = executor(replace(rule, **changes), qualified.make_context(registry=tables()))
                    self.assertIs(result.outcome, execution.ValidationOutcome.UNSUPPORTED)
                    self.assertEqual((result.evaluated_record_count, result.violation_count), (0, 0))

    def test_other_map_binding_and_cross_field_shapes_stay_closed(self):
        sources = {
            "target_group_membership": (
                GROUP_EXPRESSION.replace(" or ", " and "),
                GROUP_EXPRESSION.replace("group_of(", "value_of("),
                GROUP_EXPRESSION.replace("== null", '== "event_kind"'),
                GROUP_EXPRESSION + '; relation_type_id == "known"',
            ),
            "cross_field_consistency": (
                CROSS_EXPRESSION.replace("version ==", "version !="),
                CROSS_EXPRESSION.replace('"schema_version"', '"other_key"'),
                CROSS_EXPRESSION.replace('"meta"', '"carddatabase:meta"'),
                'version == lookup("meta","key","schema_version","value")',
            ),
        }
        for kind, expressions in sources.items():
            for source in expressions:
                with self.subTest(kind=kind, source=source):
                    result = execute((), kind=kind, source=source)
                    self.assertIs(result.outcome, execution.ValidationOutcome.UNSUPPORTED)

    def test_missing_source_namespace_table_schema_and_identity_fail_closed(self):
        for kind, executor in EXECUTORS.items():
            rule = make_rule(kind)
            self.assert_failure(executor(replace(rule, component_identity="missing"), qualified.make_context()))
            row = group_row() if kind == "target_group_membership" else source_row()
            data = tables((row,))
            del data["items"]
            self.assert_failure(executor(rule, qualified.make_context(registry=data)))
            self.assert_failure(executor(replace(rule, target_field_id="missing"), qualified.make_context(registry=tables((row,)))))
            self.assert_failure(execute(({**row, "item_id": None},), kind=kind))

    def test_rule_id_is_not_a_dispatch_key_and_empty_tables_pass(self):
        for kind, executor in EXECUTORS.items():
            row = group_row() if kind == "target_group_membership" else source_row()
            self.assert_pass(executor(replace(make_rule(kind), rule_id="arbitrary_id"), qualified.make_context(registry=tables((row,)))), 1)
            self.assert_pass(execute((), kind=kind), 0)

    def test_unexpected_resolver_errors_reach_stage_infrastructure_boundary(self):
        for kind, name, row in (
            ("target_group_membership", "_resolve_registry_value", group_row()),
            ("cross_field_consistency", "_resolve_scalar_lookup", source_row()),
        ):
            with patch.object(family, name, side_effect=RuntimeError("sentinel")):
                with self.assertRaises(RuntimeError):
                    execute((row,), kind=kind)
                with self.assertRaises(stage.ValidationStageExecutionError):
                    stage.run_validation_stage(base.rules.ValidationRuleCatalog((make_rule(kind),)), "pre_export", qualified.make_context(registry=tables((row,))))

    def test_package_and_direct_imports_have_no_cycles(self):
        for package in (False, True):
            directory = base.MODULE_DIRECTORY.parent if package else base.MODULE_DIRECTORY
            prefix = "canonical_export." if package else ""
            script = (
                f"import sys; sys.path.insert(0, {str(directory)!r}); "
                f"from {prefix}canonical_validation_reference_constraints import execute_cross_field_consistency_rule as direct; "
                f"from {prefix}canonical_validation_execution import execute_cross_field_consistency_rule as facade; "
                f"from {prefix}canonical_validation_stage import DEFAULT_PRE_EXPORT_EXECUTORS; "
                "assert direct is facade is DEFAULT_PRE_EXPORT_EXECUTORS['cross_field_consistency']"
            )
            result = subprocess.run([sys.executable, "-B", "-c", script], capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class TestCurrentE5Corpus(E5TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog, cls.context = base.current_corpus_catalog_and_context()
        cls.reversed_catalog, cls.reversed_context = base.current_corpus_catalog_and_context(reverse=True)

    def test_exact_two_current_contracts_pass_including_reversed_corpus(self):
        for kind, rule_id in TARGETS.items():
            selected = self.catalog.by_kind(kind)
            self.assertEqual(tuple(r.rule_id for r in selected), (rule_id,))
            rule = selected[0]
            self.assertEqual((rule.validation_stage_id, rule.blocking, rule.component_identity), ("pre_export", True, "REGISTRY.xlsx"))
            result = EXECUTORS[kind](rule, self.context)
            self.assert_pass(result, len(self.context.table(rule.target_table_id, namespace="registry")))
            self.assertEqual(result, EXECUTORS[kind](self.reversed_catalog.get(rule_id), self.reversed_context))

    def test_current_group_mapping_and_exact_resolution_counts(self):
        rule = self.catalog.get(TARGETS["target_group_membership"])
        mapping = dict(rule.condition_ast.statements[0].value.arguments[1].items)
        rows = self.context.table("value_relations", namespace="registry")
        mapped = [r for r in rows if r["relation_type_id"] in mapping]
        self.assertEqual((len(mapping), len(rows), len(mapped), len(rows) - len(mapped)), (17, 59, 28, 31))
        groups = [family._resolve_registry_value(self.context, r["target_registry_value_id"], "group_id") for r in mapped]
        self.assertEqual(len(set(groups)), 11)
        self.assertEqual(sum(group == mapping[row["relation_type_id"]] for row, group in zip(mapped, groups)), 28)
        with patch.object(family, "_resolve_registry_value", wraps=family._resolve_registry_value) as resolver:
            self.assert_pass(EXECUTORS["target_group_membership"](rule, self.context), len(rows))
            self.assertEqual(resolver.call_count, len(mapped))

    def test_current_active_technical_version_and_meta_cardinality(self):
        rows = self.context.table("source_registry", namespace="registry")
        technical = [r for r in rows if r["authority_level"] == "canonical_technical_source"]
        active = [r for r in technical if r["status"] == "active"]
        meta = [r for r in self.context.table("meta", namespace="registry") if r["key"] == "schema_version"]
        self.assertEqual((len(rows), len(technical), len(active), len(meta)), (21, 7, 1, 1))
        self.assertEqual((active[0]["version"], meta[0]["value"]), ("0.5.1", "0.5.1"))
        with patch.object(family, "_resolve_scalar_lookup", wraps=family._resolve_scalar_lookup) as resolver:
            self.assert_pass(EXECUTORS["cross_field_consistency"](self.catalog.get(TARGETS["cross_field_consistency"]), self.context), len(rows))
            self.assertEqual(resolver.call_count, len(active))

    def test_exact_stage_delta_leaves_every_other_execution_unchanged(self):
        registry_before = {k: v for k, v in stage.DEFAULT_PRE_EXPORT_EXECUTORS.items() if k not in TARGETS}
        before = stage.run_validation_stage(self.catalog, "pre_export", self.context, registry_before)
        after = stage.run_validation_stage(self.catalog, "pre_export", self.context)
        old = {e.rule.rule_id: e.execution for e in before.rule_results}
        new = {e.rule.rule_id: e.execution for e in after.rule_results}
        self.assertEqual({r for r in old if old[r] != new[r]}, set(TARGETS.values()))
        self.assertEqual((before.pass_count, before.fail_count, before.unsupported_count, before.not_executed_count), (242, 1, 0, 44))
        self.assertEqual((after.pass_count, after.fail_count, after.unsupported_count, after.not_executed_count), (244, 1, 0, 42))
        self.assertEqual((after.active_rule_count, after.blocking_pass_count, after.blocking_fail_count, after.blocking_not_executed_count), (287, 244, 0, 41))
        remaining = [e for e in after.rule_results if e.execution.outcome is execution.ValidationOutcome.NOT_EXECUTED]
        self.assertEqual(Counter(e.rule.validation_kind_id for e in remaining), {"custom_expression": 42})
        self.assertEqual(sum(e.rule.blocking for e in remaining), 41)
        self.assertIs(new["cdb_val_printings_default_unique_per_card"].outcome, execution.ValidationOutcome.NOT_EXECUTED)
        for kind, rule_id in TARGETS.items():
            self.assertIs(old[rule_id].outcome, execution.ValidationOutcome.NOT_EXECUTED)
            self.assertEqual(new[rule_id], EXECUTORS[kind](self.catalog.get(rule_id), self.context))

    def test_family_gates_accept_no_other_current_rule(self):
        for kind, executor in EXECUTORS.items():
            supported = {r.rule_id for r in self.catalog.rules if executor(r, self.context).outcome is not execution.ValidationOutcome.UNSUPPORTED}
            self.assertEqual(supported, {TARGETS[kind]})


if __name__ == "__main__":
    unittest.main()
