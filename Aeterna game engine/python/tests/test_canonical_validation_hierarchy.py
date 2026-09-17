import hashlib
import sys
import unittest
from collections import Counter
from dataclasses import replace
from pathlib import Path

import test_canonical_validation_execution as execution_tests


PYTHON_ROOT = Path(__file__).resolve().parents[1]
MODULE_DIRECTORY = PYTHON_ROOT / "tools" / "canonical_export"
HIERARCHY_PATH = MODULE_DIRECTORY / "canonical_validation_hierarchy.py"

execution = execution_tests.execution
rules = execution_tests.rules
validation = execution_tests.validation_expr
hierarchy = sys.modules[execution.execute_hierarchy_integrity_rule.__module__]


EXPRESSION = (
    'no_self_reference("node_id","parent_id") and '
    'hierarchy_is_acyclic("node_id","parent_id")'
)


def make_hierarchy_rule(expression=EXPRESSION, *, ast=None, **overrides):
    ast = ast or validation.parse_validation_expression(expression)
    return replace(
        execution_tests.make_rule(),
        rule_id="hierarchy_test_rule",
        rule_scope_id="table",
        validation_kind_id="hierarchy_integrity",
        validation_stage_id="pre_export",
        target_table_id="nodes",
        target_field_id="fld_nodes_parent_id",
        condition_expression_source=expression,
        condition_ast=ast,
        condition_ast_hash=validation.semantic_ast_hash(ast),
        operator_id=None,
        comparison_value=None,
        minimum_value=None,
        maximum_value=None,
        reference_table_id=None,
        reference_field_id=None,
        component_identity="registry-component",
        free_identifiers=(),
        local_bindings=(),
        **overrides,
    )


def node_field(data_type="string", **overrides):
    field = {
        "field_id": "fld_nodes_node_id",
        "table_id": "nodes",
        "field_name": "node_id",
        "data_type": data_type,
        "required_mode": "always",
        "nullable": False,
        "null_handling": "forbidden",
        "status": "active",
    }
    field.update(overrides)
    return field


def parent_field(data_type="string", *, nullable=True, **overrides):
    field = {
        "field_id": "fld_nodes_parent_id",
        "table_id": "nodes",
        "field_name": "parent_id",
        "data_type": data_type,
        "required_mode": "conditional" if nullable else "always",
        "nullable": nullable,
        "null_handling": "explicit_null" if nullable else "forbidden",
        "reference_table_id": "nodes",
        "reference_field_id": "fld_nodes_node_id",
        "status": "active",
    }
    field.update(overrides)
    return field


def namespace_tables(
    records=(),
    *,
    include_target=True,
    include_table_schema=True,
    fields=None,
):
    tables = {
        "schema_tables": (
            {
                "table_id": "nodes",
                "primary_key": "node_id",
                "status": "active",
            },
        )
        if include_table_schema
        else (),
        "schema_fields": tuple(
            fields if fields is not None else (node_field(), parent_field())
        ),
    }
    if include_target:
        tables["nodes"] = tuple(records)
    return tables


def make_context(
    records=(),
    *,
    registry_tables=None,
    carddatabase_tables=None,
    component_namespaces=None,
    **table_options,
):
    registry = (
        registry_tables
        if registry_tables is not None
        else namespace_tables(records, **table_options)
    )
    return execution.ValidationDataContext(
        namespaced_tables={
            "registry": registry,
            "carddatabase": carddatabase_tables or {},
        },
        component_namespaces=(
            component_namespaces
            if component_namespaces is not None
            else {"registry-component": "registry"}
        ),
    )


def run(records=(), *, rule=None, **context_options):
    return execution.execute_hierarchy_integrity_rule(
        rule or make_hierarchy_rule(),
        make_context(records, **context_options),
    )


class TestHierarchyModuleBoundary(unittest.TestCase):
    def test_public_boundary_and_facade_identity_are_exact(self):
        symbols = (
            "VALIDATION_HIERARCHY_INTEGRITY_FAILED",
            "VALIDATION_HIERARCHY_TARGET_RECORD_INVALID",
            "VALIDATION_HIERARCHY_TARGET_TABLE_MISSING",
            "execute_hierarchy_integrity_rule",
        )
        self.assertEqual(set(hierarchy.__all__), set(symbols))
        for symbol in symbols:
            with self.subTest(symbol=symbol):
                self.assertIs(getattr(execution, symbol), getattr(hierarchy, symbol))

    def test_module_is_dedicated_pure_and_rule_id_independent(self):
        source = HIERARCHY_PATH.read_text(encoding="utf-8")
        for forbidden in (
            "openpyxl",
            "load_workbook",
            "canonical_validation_expr_eval",
            "evaluate_validation_expression",
            "if rule.rule_id",
            "cdb_val_",
            "val_rule_",
        ):
            self.assertNotIn(forbidden, source)

    def test_argument_types_are_explicit(self):
        with self.assertRaises(TypeError):
            execution.execute_hierarchy_integrity_rule(object(), make_context())
        with self.assertRaises(TypeError):
            execution.execute_hierarchy_integrity_rule(
                make_hierarchy_rule(), object()
            )


class TestHierarchyPass(unittest.TestCase):
    def assert_pass(self, records, **options):
        result = run(records, **options)
        self.assertIs(result.outcome, execution.ValidationOutcome.PASS)
        self.assertEqual(result.evaluated_record_count, len(records))
        self.assertEqual(result.violation_count, 0)
        self.assertEqual(result.diagnostics, ())
        return result

    def test_empty_table(self):
        self.assert_pass(())

    def test_one_legitimate_null_root(self):
        self.assert_pass(({"node_id": "root", "parent_id": None},))

    def test_simple_chain(self):
        self.assert_pass(
            (
                {"node_id": "root", "parent_id": None},
                {"node_id": "middle", "parent_id": "root"},
                {"node_id": "leaf", "parent_id": "middle"},
            )
        )

    def test_branching_tree(self):
        self.assert_pass(
            (
                {"node_id": "root", "parent_id": None},
                {"node_id": "left", "parent_id": "root"},
                {"node_id": "right", "parent_id": "root"},
                {"node_id": "leaf", "parent_id": "left"},
            )
        )

    def test_multiple_disconnected_acyclic_components(self):
        self.assert_pass(
            (
                {"node_id": "a", "parent_id": None},
                {"node_id": "b", "parent_id": "a"},
                {"node_id": "x", "parent_id": None},
                {"node_id": "y", "parent_id": "x"},
            )
        )

    def test_missing_external_parent_is_not_a_hierarchy_violation(self):
        self.assert_pass(({"node_id": "a", "parent_id": "MISSING"},))

    def test_exact_values_are_not_normalized(self):
        self.assert_pass(
            (
                {"node_id": "a", "parent_id": "A"},
                {"node_id": "A", "parent_id": " a "},
                {"node_id": "é", "parent_id": "é"},
            )
        )


class TestHierarchyFailures(unittest.TestCase):
    def test_self_reference_is_one_diagnostic_and_not_a_cycle(self):
        result = run(({"node_id": "a", "parent_id": "a"},))
        self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual((result.evaluated_record_count, result.violation_count), (1, 1))
        diagnostic = result.diagnostics[0]
        self.assertEqual(
            diagnostic.code, hierarchy.VALIDATION_HIERARCHY_INTEGRITY_FAILED
        )
        self.assertEqual(diagnostic.reason, "self_reference")
        self.assertEqual(diagnostic.related_record_identities, ("a",))

    def test_two_node_cycle_is_one_canonical_diagnostic(self):
        result = run(
            (
                {"node_id": "b", "parent_id": "a"},
                {"node_id": "a", "parent_id": "b"},
            )
        )
        self.assertEqual(result.violation_count, 1)
        diagnostic = result.diagnostics[0]
        self.assertEqual(diagnostic.reason, "cycle")
        self.assertEqual(diagnostic.observed_value, '["a","b"]')
        self.assertEqual(diagnostic.related_record_identities, ("a", "b"))

    def test_three_node_cycle_preserves_edges_and_rotates_to_utf8_minimum(self):
        result = run(
            (
                {"node_id": "z", "parent_id": "a"},
                {"node_id": "a", "parent_id": "m"},
                {"node_id": "m", "parent_id": "z"},
            )
        )
        self.assertEqual(result.violation_count, 1)
        self.assertEqual(result.diagnostics[0].reason, "cycle")
        self.assertEqual(result.diagnostics[0].observed_value, '["a","m","z"]')
        self.assertEqual(
            result.diagnostics[0].related_record_identities, ("a", "m", "z")
        )

    def test_two_independent_cycles_are_two_diagnostics(self):
        result = run(
            (
                {"node_id": "a", "parent_id": "b"},
                {"node_id": "b", "parent_id": "a"},
                {"node_id": "x", "parent_id": "y"},
                {"node_id": "y", "parent_id": "x"},
            )
        )
        self.assertEqual(result.violation_count, 2)
        self.assertEqual(
            tuple(item.observed_value for item in result.diagnostics),
            ('["a","b"]', '["x","y"]'),
        )

    def test_duplicate_node_id_is_one_fail_closed_group(self):
        result = run(
            (
                {"node_id": "a", "parent_id": None},
                {"node_id": "a", "parent_id": "external"},
            )
        )
        self.assertEqual(result.violation_count, 1)
        diagnostic = result.diagnostics[0]
        self.assertEqual(diagnostic.reason, "duplicate_node_id")
        self.assertEqual(diagnostic.related_record_identities, ("a", "a"))

    def test_missing_node_and_parent_fields_fail_per_record(self):
        result = run(
            (
                {"parent_id": None},
                {"node_id": "a"},
            )
        )
        self.assertEqual((result.evaluated_record_count, result.violation_count), (2, 2))
        self.assertEqual(
            {item.reason for item in result.diagnostics},
            {"node_field_missing", "parent_field_missing"},
        )

    def test_invalid_node_and_parent_types_fail_without_coercion(self):
        result = run(
            (
                {"node_id": 1, "parent_id": None},
                {"node_id": "a", "parent_id": 1},
            )
        )
        self.assertEqual(result.violation_count, 2)
        self.assertEqual(
            {item.reason for item in result.diagnostics},
            {"node_value_type_invalid", "parent_value_type_invalid"},
        )

    def test_bool_is_not_an_integer_identity(self):
        fields = (node_field("integer"), parent_field("integer"))
        result = run(
            ({"node_id": 1, "parent_id": True},),
            fields=fields,
        )
        self.assertEqual(result.diagnostics[0].reason, "parent_value_type_invalid")

    def test_forbidden_null_parent_fails(self):
        fields = (node_field(), parent_field(nullable=False))
        result = run(
            ({"node_id": "a", "parent_id": None},),
            fields=fields,
        )
        self.assertEqual(result.violation_count, 1)
        self.assertEqual(result.diagnostics[0].reason, "parent_value_null_forbidden")

    def test_malformed_record_does_not_hide_independent_cycle(self):
        result = run(
            (
                {"node_id": 1, "parent_id": None},
                {"node_id": "a", "parent_id": "b"},
                {"node_id": "b", "parent_id": "a"},
            )
        )
        self.assertEqual(result.violation_count, 2)
        self.assertEqual(
            Counter(item.reason for item in result.diagnostics),
            {"node_value_type_invalid": 1, "cycle": 1},
        )


class TestHierarchyDeterminism(unittest.TestCase):
    def test_reversed_records_are_identical(self):
        records = (
            {"node_id": "x", "parent_id": "y"},
            {"node_id": "y", "parent_id": "x"},
            {"node_id": "a", "parent_id": "b"},
            {"node_id": "b", "parent_id": "a"},
        )
        self.assertEqual(run(records), run(tuple(reversed(records))))

    def test_cycle_reachable_from_multiple_nodes_is_reported_once(self):
        result = run(
            (
                {"node_id": "a", "parent_id": "b"},
                {"node_id": "b", "parent_id": "a"},
                {"node_id": "c", "parent_id": "a"},
                {"node_id": "d", "parent_id": "c"},
            )
        )
        self.assertEqual(result.violation_count, 1)
        self.assertEqual(result.diagnostics[0].observed_value, '["a","b"]')

    def test_reversed_duplicate_records_have_identical_evidence(self):
        records = (
            {"node_id": "a", "parent_id": None},
            {"node_id": "a", "parent_id": "external"},
        )
        self.assertEqual(run(records), run(tuple(reversed(records))))


class TestHierarchyStaticContract(unittest.TestCase):
    def assert_unsupported(self, rule):
        result = execution.execute_hierarchy_integrity_rule(
            rule,
            make_context(include_target=False),
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.UNSUPPORTED)
        self.assertEqual((result.evaluated_record_count, result.violation_count), (0, 0))
        self.assertEqual(result.diagnostics[0].code, execution.VALIDATION_EXECUTOR_UNSUPPORTED)

    def test_wrong_builtin_order_extra_call_and_unsupported_root(self):
        expressions = (
            'hierarchy_is_acyclic("node_id","parent_id") and '
            'no_self_reference("node_id","parent_id")',
            'no_self_reference("node_id","parent_id") and count(node_id)',
            f"({EXPRESSION}) and true",
            "true",
        )
        for expression in expressions:
            with self.subTest(expression=expression):
                self.assert_unsupported(make_hierarchy_rule(expression))

    def test_wrong_arity_and_non_literal_tokens(self):
        cases = (
            validation.BinaryOperation(
                "and",
                validation.Call(
                    "no_self_reference",
                    (validation.Literal("string", "node_id"),),
                ),
                validation.Call(
                    "hierarchy_is_acyclic",
                    (
                        validation.Literal("string", "node_id"),
                        validation.Literal("string", "parent_id"),
                    ),
                ),
            ),
            validation.BinaryOperation(
                "and",
                validation.Call(
                    "no_self_reference",
                    (
                        validation.Identifier("node_id"),
                        validation.Literal("string", "parent_id"),
                    ),
                ),
                validation.Call(
                    "hierarchy_is_acyclic",
                    (
                        validation.Identifier("node_id"),
                        validation.Literal("string", "parent_id"),
                    ),
                ),
            ),
        )
        for ast in cases:
            with self.subTest(ast=ast):
                self.assert_unsupported(
                    make_hierarchy_rule("synthetic invalid hierarchy", ast=ast)
                )

    def test_disagreeing_and_swapped_field_tokens_are_unsupported(self):
        expressions = (
            'no_self_reference("node_id","parent_id") and '
            'hierarchy_is_acyclic("other_id","parent_id")',
            'no_self_reference("parent_id","node_id") and '
            'hierarchy_is_acyclic("parent_id","node_id")',
        )
        for expression in expressions:
            with self.subTest(expression=expression):
                self.assert_unsupported(make_hierarchy_rule(expression))

    def test_scope_stage_kind_and_structured_fields_are_unsupported(self):
        base = make_hierarchy_rule()
        cases = (
            replace(base, validation_kind_id="definition_invariant"),
            replace(base, validation_stage_id="runtime_load"),
            replace(base, rule_scope_id="record"),
            replace(base, comparison_value="unexpected"),
        )
        for rule in cases:
            with self.subTest(rule=rule):
                self.assert_unsupported(rule)


class TestHierarchyInfrastructure(unittest.TestCase):
    def test_missing_namespace_table_and_schema_fail_closed(self):
        cases = (
            (
                make_context(component_namespaces={}),
                hierarchy.VALIDATION_HIERARCHY_TARGET_TABLE_MISSING,
                "source_namespace_missing",
            ),
            (
                make_context(include_target=False),
                hierarchy.VALIDATION_HIERARCHY_TARGET_TABLE_MISSING,
                "target_table_missing",
            ),
            (
                make_context(fields=(parent_field(),)),
                hierarchy.VALIDATION_HIERARCHY_TARGET_RECORD_INVALID,
                "node_field_schema_unresolved",
            ),
            (
                make_context(fields=(node_field(),)),
                hierarchy.VALIDATION_HIERARCHY_TARGET_RECORD_INVALID,
                "parent_field_schema_unresolved",
            ),
        )
        for context, code, reason in cases:
            with self.subTest(reason=reason):
                result = execution.execute_hierarchy_integrity_rule(
                    make_hierarchy_rule(), context
                )
                self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
                self.assertEqual(result.diagnostics[0].code, code)
                self.assertEqual(result.diagnostics[0].reason, reason)

    def test_unqualified_target_uses_only_bound_namespace(self):
        registry = namespace_tables(
            (
                {"node_id": "a", "parent_id": None},
                {"node_id": "b", "parent_id": "a"},
            )
        )
        carddatabase = namespace_tables(
            (
                {"node_id": "x", "parent_id": "y"},
                {"node_id": "y", "parent_id": "x"},
            )
        )
        result = execution.execute_hierarchy_integrity_rule(
            make_hierarchy_rule(),
            make_context(
                registry_tables=registry,
                carddatabase_tables=carddatabase,
            ),
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.PASS)

    def test_parent_schema_must_reference_same_node_domain(self):
        fields = (
            node_field(),
            parent_field(reference_table_id="other_table"),
        )
        result = run((), fields=fields)
        self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(
            result.diagnostics[0].reason, "parent_field_domain_mismatch"
        )


class TestCurrentHierarchyCorpus(unittest.TestCase):
    EXPECTED = {
        "cdb_val_abilities_hierarchy_acyclic": ("abilities", 26, 26),
        "cdb_val_conditions_hierarchy_acyclic": ("ability_conditions", 4, 4),
        "cdb_val_effects_hierarchy_acyclic": ("ability_effects", 21, 21),
        "cdb_val_expressions_hierarchy_acyclic": ("ability_expressions", 9, 8),
        "val_event_types_hierarchy_acyclic": ("event_types", 22, 22),
        "val_rule_registry_hierarchy_acyclic": ("rule_registry", 23, 10),
        "val_source_registry_supersession_acyclic": ("source_registry", 21, 8),
    }
    COMPANIONS = {
        "cdb_val_abilities_hierarchy_acyclic": "cdb_val_abilities_parent_same_card",
        "cdb_val_conditions_hierarchy_acyclic": "cdb_val_conditions_parent_same_ability",
        "cdb_val_effects_hierarchy_acyclic": "cdb_val_effects_parent_same_ability",
        "cdb_val_expressions_hierarchy_acyclic": "cdb_val_expressions_parent_same_ability",
        "val_rule_registry_hierarchy_acyclic": "val_rule_registry_parent_exists",
        "val_source_registry_supersession_acyclic": "val_source_registry_supersedes_exists",
    }

    def test_exact_seven_rule_shape_schema_and_current_results(self):
        before = {
            path: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in execution_tests.WORKBOOKS
        }
        catalog, context = execution_tests.current_corpus_catalog_and_context()
        cohort = tuple(
            rule
            for rule in catalog.by_stage("pre_export")
            if rule.validation_kind_id == "hierarchy_integrity"
        )
        self.assertEqual(len(cohort), 7)
        self.assertTrue(all(rule.blocking for rule in cohort))
        self.assertEqual({rule.rule_id for rule in cohort}, set(self.EXPECTED))

        for rule in cohort:
            namespace = context.namespace_for_component(rule.component_identity)
            records = context.table(rule.target_table_id, namespace=namespace)
            fields, reason = hierarchy._hierarchy_expression_contract(rule)
            self.assertIsNone(reason)
            node_name, parent_name = fields
            node_schema = execution_tests.core._resolve_field_schema(
                context,
                rule.target_table_id,
                field_name=node_name,
                namespace=namespace,
            )
            parent_schema = execution_tests.core._resolve_field_schema(
                context,
                rule.target_table_id,
                field_name=parent_name,
                namespace=namespace,
            )
            with self.subTest(rule=rule.rule_id):
                table, count, roots = self.EXPECTED[rule.rule_id]
                self.assertEqual(rule.target_table_id, table)
                self.assertEqual(len(records), count)
                self.assertEqual(sum(row[parent_name] is None for row in records), roots)
                self.assertEqual(
                    execution_tests.core._resolve_primary_key(
                        context, table, namespace=namespace
                    ),
                    node_name,
                )
                self.assertEqual(node_schema.get("data_type"), "string")
                self.assertIs(node_schema.get("nullable"), False)
                self.assertEqual(node_schema.get("required_mode"), "always")
                self.assertEqual(node_schema.get("null_handling"), "forbidden")
                self.assertEqual(parent_schema.get("data_type"), "string")
                self.assertIs(parent_schema.get("nullable"), True)
                self.assertEqual(parent_schema.get("required_mode"), "conditional")
                self.assertEqual(parent_schema.get("null_handling"), "explicit_null")
                self.assertEqual(parent_schema.get("reference_table_id"), table)
                self.assertEqual(
                    parent_schema.get("reference_field_id"),
                    node_schema.get("field_id"),
                )
                node_ids = {row[node_name] for row in records}
                self.assertEqual(len(node_ids), len(records))
                self.assertEqual(
                    sum(row[parent_name] == row[node_name] for row in records), 0
                )
                self.assertEqual(
                    sum(
                        row[parent_name] is not None
                        and row[parent_name] not in node_ids
                        for row in records
                    ),
                    0,
                )
                result = execution.execute_hierarchy_integrity_rule(rule, context)
                self.assertIs(result.outcome, execution.ValidationOutcome.PASS)
                self.assertEqual(result.evaluated_record_count, count)
                self.assertEqual(result.violation_count, 0)

        after = {
            path: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in execution_tests.WORKBOOKS
        }
        self.assertEqual(before, after)

    def test_companion_reference_or_definition_rules_are_present(self):
        catalog, _ = execution_tests.current_corpus_catalog_and_context()
        for hierarchy_rule, companion_rule in self.COMPANIONS.items():
            with self.subTest(rule=hierarchy_rule):
                companion = catalog.get(companion_rule)
                self.assertIsNotNone(companion)
                self.assertIn(
                    companion.validation_kind_id,
                    {"definition_invariant", "reference_integrity"},
                )

    def test_event_types_parent_field_has_authoritative_hierarchy_rule(self):
        catalog, context = execution_tests.current_corpus_catalog_and_context()
        field = execution_tests.core._resolve_field_schema(
            context,
            "event_types",
            field_name="parent_event_type_id",
            namespace="registry",
        )
        self.assertIsNotNone(field)
        hierarchy_rules = tuple(
            rule
            for rule in catalog.by_kind("hierarchy_integrity")
            if rule.target_table_id == "event_types"
            and rule.target_field_id == field.get("field_id")
        )
        self.assertEqual(len(hierarchy_rules), 1)
        self.assertEqual(
            hierarchy_rules[0].rule_id,
            "val_event_types_hierarchy_acyclic",
        )


if __name__ == "__main__":
    unittest.main()
