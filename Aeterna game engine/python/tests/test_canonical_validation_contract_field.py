import hashlib
import sys
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import test_canonical_validation_execution as execution_tests


PYTHON_ROOT = Path(__file__).resolve().parents[1]
MODULE_DIRECTORY = PYTHON_ROOT / "tools" / "canonical_export"
CONTRACT_PATH = MODULE_DIRECTORY / "canonical_validation_contract_field.py"
EVALUATOR_PATH = MODULE_DIRECTORY / "canonical_validation_expr_eval.py"

execution = execution_tests.execution
validation = execution_tests.validation_expr
contract = sys.modules[
    execution.execute_contract_field_invariant_rule.__module__
]

ALWAYS_EXPRESSION = (
    'when(required_mode == "always", nullable == false and '
    'null_handling == "forbidden")'
)
COLLECTION_EXPRESSION = (
    'when(is_collection == true, (min_items == null or min_items >= 0) '
    'and (max_items == null or (min_items == null or '
    'max_items >= min_items)))'
)
SCALAR_EXPRESSION = (
    "when(is_collection == false, min_items == null and max_items == null)"
)

IDENTIFIERS = {
    ALWAYS_EXPRESSION: ("null_handling", "nullable", "required_mode"),
    COLLECTION_EXPRESSION: ("is_collection", "max_items", "min_items"),
    SCALAR_EXPRESSION: ("is_collection", "max_items", "min_items"),
}


def make_contract_rule(expression=ALWAYS_EXPRESSION, *, ast=None, **overrides):
    ast = ast or validation.parse_validation_expression(expression)
    target_field_id = (
        "fld_contract_fields_required_mode"
        if expression == ALWAYS_EXPRESSION
        else "fld_contract_fields_is_collection"
    )
    return replace(
        execution_tests.make_rule(),
        rule_id="contract_field_test_rule",
        rule_scope_id="record",
        validation_kind_id="contract_field_invariant",
        validation_stage_id="pre_export",
        target_table_id="contract_fields",
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
        component_identity="registry-component",
        free_identifiers=IDENTIFIERS.get(expression, ()),
        local_bindings=(),
        **overrides,
    )


def schema_field(
    field_name,
    data_type,
    *,
    required_mode="always",
    nullable=False,
    null_handling="forbidden",
    **overrides,
):
    field = {
        "field_id": f"fld_contract_fields_{field_name}",
        "table_id": "contract_fields",
        "field_name": field_name,
        "data_type": data_type,
        "required_mode": required_mode,
        "nullable": nullable,
        "null_handling": null_handling,
        "status": "active",
    }
    field.update(overrides)
    return field


def default_fields():
    return (
        schema_field("contract_field_id", "string"),
        schema_field("required_mode", "string"),
        schema_field("nullable", "boolean"),
        schema_field("null_handling", "string"),
        schema_field("is_collection", "boolean"),
        schema_field(
            "min_items",
            "integer",
            required_mode="conditional",
            nullable=True,
            null_handling="explicit_null",
        ),
        schema_field(
            "max_items",
            "integer",
            required_mode="conditional",
            nullable=True,
            null_handling="explicit_null",
        ),
    )


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
                "table_id": "contract_fields",
                "primary_key": "contract_field_id",
                "status": "active",
            },
        )
        if include_table_schema
        else (),
        "schema_fields": tuple(fields if fields is not None else default_fields()),
    }
    if include_target:
        tables["contract_fields"] = tuple(records)
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
    return execution.execute_contract_field_invariant_rule(
        rule or make_contract_rule(),
        make_context(records, **context_options),
    )


def always_record(identity="field-1", **overrides):
    record = {
        "contract_field_id": identity,
        "required_mode": "always",
        "nullable": False,
        "null_handling": "forbidden",
    }
    record.update(overrides)
    return record


def collection_record(identity="field-1", **overrides):
    record = {
        "contract_field_id": identity,
        "is_collection": True,
        "min_items": None,
        "max_items": None,
    }
    record.update(overrides)
    return record


class TestContractFieldModuleBoundary(unittest.TestCase):
    def test_public_boundary_and_facade_identity_are_exact(self):
        symbols = (
            "VALIDATION_CONTRACT_FIELD_INVARIANT_FAILED",
            "VALIDATION_CONTRACT_FIELD_TARGET_RECORD_INVALID",
            "VALIDATION_CONTRACT_FIELD_TARGET_TABLE_MISSING",
            "execute_contract_field_invariant_rule",
        )
        self.assertEqual(set(contract.__all__), set(symbols))
        for symbol in symbols:
            with self.subTest(symbol=symbol):
                self.assertIs(getattr(execution, symbol), getattr(contract, symbol))

    def test_module_is_dedicated_pure_and_rule_id_independent(self):
        source = CONTRACT_PATH.read_text(encoding="utf-8")
        for forbidden in (
            "openpyxl",
            "load_workbook",
            "if rule.rule_id",
            "val_contract_fields_",
            "runtime_load",
            "contract_instance_consistency",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)
        self.assertIn("evaluate_validation_expression", source)

    def test_evaluator_has_no_contract_field_executor_specific_surface(self):
        source = EVALUATOR_PATH.read_text(encoding="utf-8")
        for token in (
            "contract_field_invariant",
            "required_mode",
            "min_items",
            "max_items",
        ):
            self.assertNotIn(token, source)
        self.assertIn('record["is_collection"]', source)

    def test_argument_types_are_explicit(self):
        with self.assertRaises(TypeError):
            execution.execute_contract_field_invariant_rule(object(), make_context())
        with self.assertRaises(TypeError):
            execution.execute_contract_field_invariant_rule(
                make_contract_rule(), object()
            )


class TestAlwaysRequiredContract(unittest.TestCase):
    def test_valid_always_non_null_forbidden_policy(self):
        result = run((always_record(),))
        self.assertIs(result.outcome, execution.ValidationOutcome.PASS)
        self.assertEqual((result.evaluated_record_count, result.violation_count), (1, 0))

    def test_nullable_and_wrong_null_policy_are_violations(self):
        records = (
            always_record("nullable", nullable=True),
            always_record("policy", null_handling="explicit_null"),
        )
        result = run(records)
        self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual((result.evaluated_record_count, result.violation_count), (2, 2))
        self.assertTrue(all(item.reason == "predicate_false" for item in result.diagnostics))

    def test_non_always_false_guard_satisfies_without_constraint_evaluation(self):
        record = always_record(
            required_mode="conditional",
            nullable=True,
            null_handling="explicit_null",
        )
        result = run((record,))
        self.assertIs(result.outcome, execution.ValidationOutcome.PASS)
        self.assertEqual((result.evaluated_record_count, result.violation_count), (1, 0))


class TestCollectionBoundsContract(unittest.TestCase):
    def run_collection(self, records):
        return run(records, rule=make_contract_rule(COLLECTION_EXPRESSION))

    def test_zero_positive_null_equal_and_greater_bounds_pass(self):
        records = (
            collection_record("zero", min_items=0, max_items=None),
            collection_record("positive", min_items=2, max_items=None),
            collection_record("equal", min_items=2, max_items=2),
            collection_record("greater", min_items=2, max_items=5),
            collection_record("unbounded", min_items=None, max_items=1),
        )
        result = self.run_collection(records)
        self.assertIs(result.outcome, execution.ValidationOutcome.PASS)
        self.assertEqual((result.evaluated_record_count, result.violation_count), (5, 0))

    def test_negative_minimum_fails(self):
        result = self.run_collection(
            (collection_record(min_items=-1, max_items=None),)
        )
        self.assertEqual(result.violation_count, 1)
        self.assertEqual(result.diagnostics[0].reason, "predicate_false")

    def test_maximum_below_minimum_fails(self):
        result = self.run_collection(
            (collection_record(min_items=3, max_items=2),)
        )
        self.assertEqual(result.violation_count, 1)

    def test_false_collection_guard_is_satisfied(self):
        result = self.run_collection(
            (collection_record(is_collection=False, min_items=-1, max_items=-2),)
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.PASS)


class TestScalarBoundsContract(unittest.TestCase):
    def run_scalar(self, records):
        return run(records, rule=make_contract_rule(SCALAR_EXPRESSION))

    def test_both_bounds_null_pass(self):
        result = self.run_scalar(
            (collection_record(is_collection=False),)
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.PASS)

    def test_minimum_maximum_and_both_populated_fail(self):
        records = (
            collection_record("min", is_collection=False, min_items=1),
            collection_record("max", is_collection=False, max_items=1),
            collection_record(
                "both", is_collection=False, min_items=1, max_items=2
            ),
        )
        result = self.run_scalar(records)
        self.assertEqual((result.evaluated_record_count, result.violation_count), (3, 3))

    def test_true_collection_guard_is_satisfied(self):
        result = self.run_scalar((collection_record(min_items=1, max_items=2),))
        self.assertIs(result.outcome, execution.ValidationOutcome.PASS)


class TestContractFieldMalformedInputs(unittest.TestCase):
    def test_empty_table_passes(self):
        result = run(())
        self.assertIs(result.outcome, execution.ValidationOutcome.PASS)
        self.assertEqual((result.evaluated_record_count, result.violation_count), (0, 0))

    def test_missing_namespace_table_and_table_schema_fail_closed(self):
        cases = (
            (
                make_context(component_namespaces={}),
                "source_namespace_missing",
            ),
            (
                make_context(include_target=False),
                "target_table_missing",
            ),
            (
                make_context(include_table_schema=False),
                "target_table_schema_unresolved",
            ),
        )
        for context, reason in cases:
            with self.subTest(reason=reason):
                result = execution.execute_contract_field_invariant_rule(
                    make_contract_rule(), context
                )
                self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
                self.assertEqual(result.diagnostics[0].reason, reason)

    def test_missing_field_invalid_type_and_forbidden_null_fail_per_record(self):
        records = (
            {key: value for key, value in always_record("missing").items() if key != "nullable"},
            always_record("type", nullable=1),
            always_record("null", required_mode=None),
        )
        result = run(records)
        self.assertEqual((result.evaluated_record_count, result.violation_count), (3, 3))
        self.assertEqual(
            {item.reason.split(":")[0] for item in result.diagnostics},
            {
                "target_field_missing",
                "target_value_type_invalid",
                "target_value_null_forbidden",
            },
        )

    def test_bool_is_not_integer_and_values_are_not_coerced(self):
        rule = make_contract_rule(COLLECTION_EXPRESSION)
        result = run(
            (collection_record(min_items=True),),
            rule=rule,
        )
        self.assertEqual(result.diagnostics[0].reason, "target_value_type_invalid:min_items")

    def test_invalid_record_identity_fails_closed(self):
        result = run((always_record(identity=""),))
        self.assertEqual(result.diagnostics[0].reason, "target_identity_invalid")

    def test_non_boolean_evaluator_result_is_record_failure(self):
        with patch.object(contract, "evaluate_validation_expression", return_value=1):
            result = run((always_record(),))
        self.assertEqual(result.violation_count, 1)
        self.assertEqual(result.diagnostics[0].reason, "expression_result_not_boolean")


class TestContractFieldStaticSupport(unittest.TestCase):
    def assert_unsupported(self, rule):
        result = execution.execute_contract_field_invariant_rule(
            rule, make_context(include_target=False)
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.UNSUPPORTED)
        self.assertEqual((result.evaluated_record_count, result.violation_count), (0, 0))
        self.assertEqual(result.diagnostics[0].code, execution.VALIDATION_EXECUTOR_UNSUPPORTED)

    def test_wrong_builtin_arity_extra_call_and_unrelated_expression(self):
        expressions = (
            'unique_by(["required_mode"])',
            f"({ALWAYS_EXPRESSION}) and true",
            'required_mode == "always"',
        )
        for expression in expressions:
            with self.subTest(expression=expression):
                self.assert_unsupported(make_contract_rule(expression))
        wrong_arity = validation.Call(
            "when", (validation.Literal("boolean", True),)
        )
        self.assert_unsupported(
            make_contract_rule("when(true)", ast=wrong_arity)
        )

    def test_binding_sequence_and_member_access_are_unsupported(self):
        expressions = (
            f"x = 1; {ALWAYS_EXPRESSION}",
            'when(record.required_mode == "always", true)',
        )
        for expression in expressions:
            with self.subTest(expression=expression):
                self.assert_unsupported(make_contract_rule(expression))

    def test_swapped_semantic_fields_are_unsupported(self):
        expression = (
            'when(is_collection == false, max_items == null and '
            'min_items == null)'
        )
        self.assert_unsupported(make_contract_rule(expression))

    def test_scope_stage_kind_target_and_structured_shapes_are_unsupported(self):
        base = make_contract_rule()
        cases = (
            replace(base, validation_kind_id="definition_invariant"),
            replace(base, validation_stage_id="runtime_load"),
            replace(base, rule_scope_id="table"),
            replace(base, target_table_id="other_table"),
            replace(base, comparison_value="unexpected"),
        )
        for rule in cases:
            with self.subTest(rule=rule):
                self.assert_unsupported(rule)

    def test_source_ast_hash_and_identifier_inventory_must_agree(self):
        base = make_contract_rule()
        cases = (
            replace(base, condition_expression_source=SCALAR_EXPRESSION),
            replace(base, condition_ast_hash="sha256:wrong"),
            replace(base, free_identifiers=("required_mode",)),
            replace(base, local_bindings=("x",)),
        )
        for rule in cases:
            with self.subTest(rule=rule):
                self.assert_unsupported(rule)

    def test_target_field_and_schema_roles_must_match(self):
        wrong_target = replace(
            make_contract_rule(),
            target_field_id="fld_contract_fields_nullable",
        )
        self.assert_unsupported(wrong_target)

        fields = list(default_fields())
        fields[1] = schema_field("required_mode", "integer")
        result = execution.execute_contract_field_invariant_rule(
            make_contract_rule(),
            make_context(fields=fields),
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.UNSUPPORTED)

    def test_identifier_schema_must_resolve_once(self):
        fields = list(default_fields())
        fields.append(schema_field("required_mode", "string", field_id="duplicate"))
        result = execution.execute_contract_field_invariant_rule(
            make_contract_rule(), make_context(fields=fields)
        )
        self.assertIs(result.outcome, execution.ValidationOutcome.FAIL)
        self.assertEqual(
            result.diagnostics[0].reason,
            "identifier_field_schema_unresolved:required_mode",
        )


class TestContractFieldDeterminism(unittest.TestCase):
    def test_reversed_records_have_identical_complete_result(self):
        records = (
            always_record("z", nullable=True),
            always_record("a", null_handling="explicit_null"),
            always_record("m"),
        )
        self.assertEqual(run(records), run(tuple(reversed(records))))


class TestCurrentContractFieldCorpus(unittest.TestCase):
    EXPECTED = {
        "val_contract_fields_always_forbids_null": ALWAYS_EXPRESSION,
        "val_contract_fields_collection_bounds_valid": COLLECTION_EXPRESSION,
        "val_contract_fields_noncollection_has_no_bounds": SCALAR_EXPRESSION,
    }

    def test_exact_three_rules_schema_and_current_results(self):
        before = {
            path: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in execution_tests.WORKBOOKS
        }
        catalog, context = execution_tests.current_corpus_catalog_and_context()
        cohort = tuple(
            rule
            for rule in catalog.by_stage("pre_export")
            if rule.validation_kind_id == "contract_field_invariant"
        )
        self.assertEqual(len(cohort), 3)
        self.assertTrue(all(rule.blocking for rule in cohort))
        self.assertEqual({rule.rule_id for rule in cohort}, set(self.EXPECTED))

        for rule in cohort:
            namespace = context.namespace_for_component(rule.component_identity)
            records = context.table(rule.target_table_id, namespace=namespace)
            shape, reason = contract._contract_field_shape(rule)
            result = execution.execute_contract_field_invariant_rule(rule, context)
            with self.subTest(rule=rule.rule_id):
                self.assertEqual(namespace, "registry")
                self.assertEqual(rule.target_table_id, "contract_fields")
                self.assertEqual(rule.condition_expression_source, self.EXPECTED[rule.rule_id])
                self.assertIsNone(reason)
                self.assertIsNotNone(shape)
                self.assertEqual(len(records), 237)
                self.assertIs(result.outcome, execution.ValidationOutcome.PASS)
                self.assertEqual(result.evaluated_record_count, 237)
                self.assertEqual(result.violation_count, 0)

        after = {
            path: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in execution_tests.WORKBOOKS
        }
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
