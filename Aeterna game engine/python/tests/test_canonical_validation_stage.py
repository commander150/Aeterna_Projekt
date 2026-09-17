import sys
import unittest
from collections import Counter
from dataclasses import FrozenInstanceError, replace
from pathlib import Path
from types import MappingProxyType

from test_canonical_validation_execution import (
    current_corpus_catalog_and_context,
    execution,
    load_module,
    local_executor_namespaced_context,
    make_rule,
    rules,
)


PYTHON_ROOT = Path(__file__).resolve().parents[1]
MODULE_DIRECTORY = PYTHON_ROOT / "tools" / "canonical_export"
STAGE_PATH = MODULE_DIRECTORY / "canonical_validation_stage.py"
_previous_rules_module = sys.modules.get("canonical_validation_rules")
_previous_execution_module = sys.modules.get("canonical_validation_execution")
try:
    sys.modules["canonical_validation_rules"] = rules
    sys.modules["canonical_validation_execution"] = execution
    stage = load_module("canonical_validation_stage", STAGE_PATH)
finally:
    if _previous_rules_module is None:
        sys.modules.pop("canonical_validation_rules", None)
    else:
        sys.modules["canonical_validation_rules"] = _previous_rules_module
    if _previous_execution_module is None:
        sys.modules.pop("canonical_validation_execution", None)
    else:
        sys.modules["canonical_validation_execution"] = _previous_execution_module


def make_stage_rule(
    rule_id="stage_test_rule",
    *,
    kind="custom_expression",
    blocking=True,
    stage_id="pre_export",
    severity=None,
):
    return replace(
        make_rule(),
        rule_id=rule_id,
        validation_kind_id=kind,
        validation_stage_id=stage_id,
        blocking=blocking,
        severity_id=severity or ("critical" if blocking else "warning"),
    )


def make_catalog(*definitions):
    return rules.ValidationRuleCatalog(tuple(definitions))


def make_execution(rule, outcome, *, rule_id=None):
    return execution.ValidationExecutionResult(
        rule_id or rule.rule_id,
        outcome,
        (),
        1,
        1 if outcome is execution.ValidationOutcome.FAIL else 0,
    )


def fixed_executor(outcome, *, rule_id=None):
    def execute(rule, data):
        return make_execution(rule, outcome, rule_id=rule_id)

    return execute


def run_one(rule, *, outcome=None, registered=True):
    executors = (
        {rule.validation_kind_id: fixed_executor(outcome)}
        if registered
        else {}
    )
    return stage.run_validation_stage(
        make_catalog(rule),
        "pre_export",
        local_executor_namespaced_context(),
        executors,
    )


class TestStageModuleBoundary(unittest.TestCase):
    def test_public_api_is_minimal_and_default_registry_is_exact(self):
        self.assertEqual(
            set(stage.__all__),
            {
                "DEFAULT_PRE_EXPORT_EXECUTORS",
                "VALIDATION_EXECUTOR_NOT_REGISTERED",
                "ValidationStageExecutionError",
                "ValidationStageResult",
                "ValidationStageRuleResult",
                "ValidationStageVerdict",
                "run_validation_stage",
            },
        )
        self.assertIsInstance(stage.DEFAULT_PRE_EXPORT_EXECUTORS, MappingProxyType)
        self.assertEqual(
            stage.DEFAULT_PRE_EXPORT_EXECUTORS,
            {
                "allowed_value": execution.execute_allowed_value_rule,
                "contract_field_invariant": execution.execute_contract_field_invariant_rule,
                "custom_expression": execution.execute_supported_custom_expression_rule,
                "definition_invariant": execution.execute_definition_invariant_rule,
                "hierarchy_integrity": execution.execute_hierarchy_integrity_rule,
                "normalized_uniqueness": execution.execute_normalized_uniqueness_rule,
                "cross_field_consistency": execution.execute_cross_field_consistency_rule,
                "target_group_membership": execution.execute_target_group_membership_rule,
                "qualified_reference_match": execution.execute_qualified_reference_match_rule,
                "range": execution.execute_range_rule,
                "reference_integrity": execution.execute_reference_integrity_rule,
                "uniqueness": execution.execute_uniqueness_rule,
            },
        )
        with self.assertRaises(TypeError):
            stage.DEFAULT_PRE_EXPORT_EXECUTORS["custom_expression"] = lambda *_: None

    def test_stage_uses_only_public_executor_boundary(self):
        source = STAGE_PATH.read_text(encoding="utf-8")
        forbidden = (
            "_unsupported_reason",
            "_contract_field_shape",
            "_range_contract",
            "_reference_contract_reason",
            "_hierarchy_expression_contract",
            "_uniqueness_contract",
            "openpyxl",
            "load_workbook",
        )
        for token in forbidden:
            with self.subTest(token=token):
                self.assertNotIn(token, source)


class TestStageVerdictAndOutcomes(unittest.TestCase):
    def test_registered_definition_unsupported_differs_from_unregistered_kind(self):
        catalog, context = current_corpus_catalog_and_context()
        supported_definition = next(
            rule
            for rule in catalog.by_kind("definition_invariant")
        )
        unsupported_rule = replace(supported_definition, condition_ast=None)
        definition_result = stage.run_validation_stage(
            make_catalog(unsupported_rule), "pre_export", context
        ).rule_results[0].execution
        unregistered_rule = make_stage_rule(kind="contract_instance_consistency")
        unregistered_result = stage.run_validation_stage(
            make_catalog(unregistered_rule),
            "pre_export",
            local_executor_namespaced_context(),
        ).rule_results[0].execution

        self.assertIs(
            definition_result.outcome, execution.ValidationOutcome.UNSUPPORTED
        )
        self.assertEqual(
            definition_result.diagnostics[0].code,
            execution.VALIDATION_EXECUTOR_UNSUPPORTED,
        )
        self.assertIs(
            unregistered_result.outcome,
            execution.ValidationOutcome.NOT_EXECUTED,
        )
        self.assertEqual(
            unregistered_result.diagnostics[0].code,
            stage.VALIDATION_EXECUTOR_NOT_REGISTERED,
        )

    def test_blocking_outcomes_define_verdict(self):
        cases = (
            (execution.ValidationOutcome.PASS, True, stage.ValidationStageVerdict.PASS),
            (
                execution.ValidationOutcome.NOT_APPLICABLE,
                True,
                stage.ValidationStageVerdict.PASS,
            ),
            (execution.ValidationOutcome.FAIL, True, stage.ValidationStageVerdict.BLOCKED),
            (
                execution.ValidationOutcome.UNSUPPORTED,
                True,
                stage.ValidationStageVerdict.BLOCKED,
            ),
        )
        for outcome, blocking, expected in cases:
            with self.subTest(outcome=outcome):
                result = run_one(
                    make_stage_rule(blocking=blocking), outcome=outcome
                )
                self.assertEqual(result.stage_verdict, expected)
                self.assertIs(result.rule_results[0].execution.outcome, outcome)

        not_executed = run_one(make_stage_rule(), registered=False)
        self.assertEqual(
            not_executed.stage_verdict, stage.ValidationStageVerdict.BLOCKED
        )

    def test_nonblocking_negative_outcomes_remain_explicit_but_clean(self):
        for outcome in (
            execution.ValidationOutcome.FAIL,
            execution.ValidationOutcome.UNSUPPORTED,
        ):
            with self.subTest(outcome=outcome):
                result = run_one(
                    make_stage_rule(blocking=False), outcome=outcome
                )
                self.assertEqual(result.stage_verdict, stage.ValidationStageVerdict.PASS)
                self.assertIs(result.rule_results[0].execution.outcome, outcome)

        not_executed = run_one(
            make_stage_rule(blocking=False), registered=False
        )
        self.assertEqual(
            not_executed.stage_verdict, stage.ValidationStageVerdict.PASS
        )
        self.assertEqual(not_executed.nonblocking_not_executed_count, 1)

    def test_severity_is_reporting_metadata_not_gating_authority(self):
        nonblocking_critical = run_one(
            make_stage_rule(blocking=False, severity="critical"),
            outcome=execution.ValidationOutcome.FAIL,
        )
        blocking_warning = run_one(
            make_stage_rule(blocking=True, severity="warning"),
            outcome=execution.ValidationOutcome.FAIL,
        )

        self.assertEqual(
            nonblocking_critical.stage_verdict,
            stage.ValidationStageVerdict.PASS,
        )
        self.assertEqual(
            blocking_warning.stage_verdict,
            stage.ValidationStageVerdict.BLOCKED,
        )

    def test_stage_models_are_immutable(self):
        result = run_one(
            make_stage_rule(), outcome=execution.ValidationOutcome.PASS
        )

        with self.assertRaises(FrozenInstanceError):
            result.stage_id = "other"
        with self.assertRaises(FrozenInstanceError):
            result.rule_results[0].execution = None

    def test_registered_unsupported_and_unregistered_are_distinct(self):
        rule = make_stage_rule()
        unsupported = run_one(
            rule, outcome=execution.ValidationOutcome.UNSUPPORTED
        )
        not_executed = run_one(rule, registered=False)

        self.assertEqual(unsupported.unsupported_count, 1)
        self.assertEqual(unsupported.not_executed_count, 0)
        self.assertEqual(not_executed.unsupported_count, 0)
        self.assertEqual(not_executed.not_executed_count, 1)
        diagnostic = not_executed.rule_results[0].execution.diagnostics[0]
        self.assertEqual(
            diagnostic.code, stage.VALIDATION_EXECUTOR_NOT_REGISTERED
        )
        self.assertEqual(diagnostic.reason, "executor_not_registered")
        self.assertEqual(
            not_executed.rule_results[0].execution.evaluated_record_count, 0
        )
        self.assertEqual(
            not_executed.rule_results[0].execution.violation_count, 0
        )

    def test_executor_result_object_is_preserved(self):
        rule = make_stage_rule(blocking=False)
        expected = make_execution(rule, execution.ValidationOutcome.FAIL)

        result = stage.run_validation_stage(
            make_catalog(rule),
            "pre_export",
            local_executor_namespaced_context(),
            {rule.validation_kind_id: lambda *_: expected},
        )

        self.assertIs(result.rule_results[0].execution, expected)
        self.assertEqual(result.nonblocking_fail_count, 1)
        self.assertEqual(result.stage_verdict, stage.ValidationStageVerdict.PASS)

    def test_all_computed_counts_are_derived_from_rule_results(self):
        outcomes = (
            execution.ValidationOutcome.PASS,
            execution.ValidationOutcome.FAIL,
            execution.ValidationOutcome.UNSUPPORTED,
            execution.ValidationOutcome.NOT_EXECUTED,
            execution.ValidationOutcome.NOT_APPLICABLE,
        )
        entries = []
        for blocking in (True, False):
            for index, outcome in enumerate(outcomes):
                rule = make_stage_rule(
                    f"rule_{blocking}_{index}", blocking=blocking
                )
                entries.append(
                    stage.ValidationStageRuleResult(
                        rule, make_execution(rule, outcome)
                    )
                )
        result = stage.ValidationStageResult("pre_export", tuple(entries))

        self.assertEqual(result.active_rule_count, 10)
        self.assertEqual(result.blocking_rule_count, 5)
        self.assertEqual(result.nonblocking_rule_count, 5)
        for name in (
            "pass_count",
            "fail_count",
            "unsupported_count",
            "not_executed_count",
            "not_applicable_count",
        ):
            with self.subTest(count=name):
                self.assertEqual(getattr(result, name), 2)
        for prefix in ("blocking", "nonblocking"):
            for outcome_name in (
                "pass",
                "fail",
                "unsupported",
                "not_executed",
                "not_applicable",
            ):
                with self.subTest(prefix=prefix, outcome=outcome_name):
                    self.assertEqual(
                        getattr(result, f"{prefix}_{outcome_name}_count"), 1
                    )


class TestStageExceptionBoundary(unittest.TestCase):
    def test_executor_exceptions_are_chained_with_rule_context(self):
        class CustomExecutorError(Exception):
            pass

        for original in (ValueError("bad value"), CustomExecutorError("custom")):
            def raising_executor(rule, data, error=original):
                raise error

            rule = make_stage_rule()
            with self.subTest(error_type=type(original).__name__):
                with self.assertRaises(stage.ValidationStageExecutionError) as raised:
                    stage.run_validation_stage(
                        make_catalog(rule),
                        "pre_export",
                        local_executor_namespaced_context(),
                        {rule.validation_kind_id: raising_executor},
                    )
                self.assertIs(raised.exception.__cause__, original)
                self.assertEqual(raised.exception.stage_id, "pre_export")
                self.assertEqual(raised.exception.rule_id, rule.rule_id)
                self.assertEqual(
                    raised.exception.validation_kind_id,
                    rule.validation_kind_id,
                )

    def test_base_exceptions_are_not_swallowed(self):
        for exception_type in (KeyboardInterrupt, SystemExit):
            def raising_executor(rule, data, error_type=exception_type):
                raise error_type()

            rule = make_stage_rule()
            with self.subTest(exception_type=exception_type.__name__):
                with self.assertRaises(exception_type):
                    stage.run_validation_stage(
                        make_catalog(rule),
                        "pre_export",
                        local_executor_namespaced_context(),
                        {rule.validation_kind_id: raising_executor},
                    )

    def test_invalid_return_type_is_infrastructure_error(self):
        rule = make_stage_rule()
        with self.assertRaises(stage.ValidationStageExecutionError) as raised:
            stage.run_validation_stage(
                make_catalog(rule),
                "pre_export",
                local_executor_namespaced_context(),
                {rule.validation_kind_id: lambda *_: None},
            )
        self.assertIsNone(raised.exception.__cause__)
        self.assertEqual(raised.exception.rule_id, rule.rule_id)

    def test_mismatched_rule_identity_is_infrastructure_error(self):
        rule = make_stage_rule()
        with self.assertRaises(stage.ValidationStageExecutionError):
            stage.run_validation_stage(
                make_catalog(rule),
                "pre_export",
                local_executor_namespaced_context(),
                {
                    rule.validation_kind_id: fixed_executor(
                        execution.ValidationOutcome.PASS,
                        rule_id="different_rule",
                    )
                },
            )

    def test_invalid_outcome_is_infrastructure_error(self):
        rule = make_stage_rule()
        invalid = replace(
            make_execution(rule, execution.ValidationOutcome.PASS),
            outcome="PASS",
        )
        with self.assertRaises(stage.ValidationStageExecutionError):
            stage.run_validation_stage(
                make_catalog(rule),
                "pre_export",
                local_executor_namespaced_context(),
                {rule.validation_kind_id: lambda *_: invalid},
            )


class TestStageRegistryAndCatalog(unittest.TestCase):
    def test_custom_registry_is_copied_before_execution(self):
        first = make_stage_rule("a_mutating_rule", kind="custom_expression")
        second = make_stage_rule("b_second_rule", kind="allowed_value")
        registry = {}

        def mutating_executor(rule, data):
            registry.pop("allowed_value")
            return make_execution(rule, execution.ValidationOutcome.PASS)

        registry.update(
            {
                "custom_expression": mutating_executor,
                "allowed_value": fixed_executor(execution.ValidationOutcome.PASS),
            }
        )
        result = stage.run_validation_stage(
            make_catalog(first, second),
            "pre_export",
            local_executor_namespaced_context(),
            registry,
        )

        self.assertEqual(result.pass_count, 2)
        self.assertEqual(result.not_executed_count, 0)
        self.assertNotIn("allowed_value", registry)

    def test_duplicate_registry_construction_is_rejected(self):
        executor = fixed_executor(execution.ValidationOutcome.PASS)
        with self.assertRaises(ValueError):
            stage._freeze_executor_registry(
                (("custom_expression", executor), ("custom_expression", executor))
            )

    def test_full_catalog_is_filtered_and_other_stage_is_rejected(self):
        pre_export = make_stage_rule("pre_export_rule")
        runtime = make_stage_rule("runtime_rule", stage_id="runtime_load")
        catalog = make_catalog(runtime, pre_export)
        result = stage.run_validation_stage(
            catalog,
            "pre_export",
            local_executor_namespaced_context(),
            {
                pre_export.validation_kind_id: fixed_executor(
                    execution.ValidationOutcome.PASS
                )
            },
        )

        self.assertEqual(
            tuple(entry.rule.rule_id for entry in result.rule_results),
            ("pre_export_rule",),
        )
        with self.assertRaises(ValueError):
            stage.run_validation_stage(
                catalog,
                "runtime_load",
                local_executor_namespaced_context(),
            )

    def test_rule_order_is_utf8_and_independent_of_source_order(self):
        definitions = tuple(
            make_stage_rule(rule_id) for rule_id in ("á_rule", "z_rule", "a_rule")
        )
        executor = fixed_executor(execution.ValidationOutcome.PASS)
        registry = {"custom_expression": executor}

        forward = stage.run_validation_stage(
            make_catalog(*definitions),
            "pre_export",
            local_executor_namespaced_context(),
            registry,
        )
        reverse = stage.run_validation_stage(
            make_catalog(*reversed(definitions)),
            "pre_export",
            local_executor_namespaced_context(reverse=True),
            registry,
        )

        self.assertEqual(forward, reverse)
        self.assertEqual(
            tuple(entry.rule.rule_id for entry in forward.rule_results),
            ("a_rule", "z_rule", "á_rule"),
        )

    def test_empty_pre_export_stage_vacuously_passes(self):
        result = stage.run_validation_stage(
            make_catalog(make_stage_rule("runtime", stage_id="runtime_load")),
            "pre_export",
            local_executor_namespaced_context(),
        )

        self.assertEqual(result.rule_results, ())
        self.assertEqual(result.active_rule_count, 0)
        self.assertEqual(result.stage_verdict, stage.ValidationStageVerdict.PASS)


class TestCurrentPreExportStage(unittest.TestCase):
    @staticmethod
    def run_current(*, reverse=False):
        catalog, context = current_corpus_catalog_and_context(reverse=reverse)
        return stage.run_validation_stage(catalog, "pre_export", context)

    def test_current_corpus_has_exact_fail_closed_golden_result(self):
        result = self.run_current()

        self.assertEqual(result.active_rule_count, 287)
        self.assertEqual(result.blocking_rule_count, 285)
        self.assertEqual(result.nonblocking_rule_count, 2)
        self.assertEqual(result.pass_count, 244)
        self.assertEqual(result.fail_count, 1)
        self.assertEqual(result.unsupported_count, 0)
        self.assertEqual(result.not_executed_count, 42)
        self.assertEqual(result.not_applicable_count, 0)
        self.assertEqual(result.blocking_pass_count, 244)
        self.assertEqual(result.blocking_fail_count, 0)
        self.assertEqual(result.blocking_unsupported_count, 0)
        self.assertEqual(result.blocking_not_executed_count, 41)
        self.assertEqual(result.blocking_not_applicable_count, 0)
        self.assertEqual(result.nonblocking_pass_count, 0)
        self.assertEqual(result.nonblocking_fail_count, 1)
        self.assertEqual(result.nonblocking_unsupported_count, 0)
        self.assertEqual(result.nonblocking_not_executed_count, 1)
        self.assertEqual(result.nonblocking_not_applicable_count, 0)
        self.assertEqual(result.stage_verdict, stage.ValidationStageVerdict.BLOCKED)
        self.assertEqual(
            round(
                100
                * (result.blocking_pass_count + result.blocking_fail_count)
                / result.blocking_rule_count,
                1,
            ),
            85.6,
        )

        definition_results = tuple(
            entry
            for entry in result.rule_results
            if entry.rule.validation_kind_id == "definition_invariant"
        )
        self.assertEqual(len(definition_results), 116)
        self.assertEqual(
            sum(
                entry.execution.outcome is not execution.ValidationOutcome.UNSUPPORTED
                for entry in definition_results
            ),
            116,
        )
        self.assertEqual(
            Counter(entry.execution.outcome for entry in definition_results),
            {
                execution.ValidationOutcome.PASS: 116,
            },
        )
        self.assertTrue(
            all(
                entry.execution.outcome is execution.ValidationOutcome.UNSUPPORTED
                and entry.execution.diagnostics[0].code
                == execution.VALIDATION_EXECUTOR_UNSUPPORTED
                for entry in definition_results
                if entry.execution.outcome is execution.ValidationOutcome.UNSUPPORTED
            )
        )
        supported_active = tuple(
            entry
            for entry in result.rule_results
            if entry.execution.outcome
            not in {
                execution.ValidationOutcome.UNSUPPORTED,
                execution.ValidationOutcome.NOT_EXECUTED,
            }
        )
        self.assertEqual(len(supported_active), 245)
        self.assertEqual(sum(entry.rule.blocking for entry in supported_active), 244)

        failures = tuple(
            entry
            for entry in result.rule_results
            if entry.execution.outcome is execution.ValidationOutcome.FAIL
        )
        self.assertEqual(len(failures), 1)
        self.assertEqual(
            {entry.rule.rule_id for entry in failures},
            {
                "cdb_val_card_localization_search_name_collision",
            },
        )
        blocking_failures = tuple(
            entry for entry in failures if entry.rule.blocking
        )
        nonblocking_failure = next(
            entry for entry in failures if not entry.rule.blocking
        )
        self.assertEqual(
            {
                entry.rule.rule_id: entry.execution.violation_count
                for entry in blocking_failures
            },
            {},
        )
        self.assertEqual(
            sum(
                entry.execution.violation_count
                for entry in blocking_failures
            ),
            0,
        )
        self.assertEqual(
            nonblocking_failure.rule.rule_id,
            "cdb_val_card_localization_search_name_collision",
        )
        self.assertEqual(nonblocking_failure.rule.severity_id, "warning")

        nonblocking_not_executed = tuple(
            entry
            for entry in result.rule_results
            if not entry.rule.blocking
            and entry.execution.outcome is execution.ValidationOutcome.NOT_EXECUTED
        )
        self.assertEqual(len(nonblocking_not_executed), 1)
        self.assertEqual(
            nonblocking_not_executed[0].rule.rule_id,
            "val_base_keyword_english_localization_coverage",
        )
        for entry in result.rule_results:
            if entry.execution.outcome is execution.ValidationOutcome.NOT_EXECUTED:
                self.assertEqual(entry.execution.evaluated_record_count, 0)
                self.assertEqual(entry.execution.violation_count, 0)
                self.assertEqual(
                    entry.execution.diagnostics[0].code,
                    stage.VALIDATION_EXECUTOR_NOT_REGISTERED,
                )

        self.assertFalse(
            any(
                diagnostic.reason == "target_field_unresolved"
                for entry in result.rule_results
                if entry.rule.validation_kind_id in {"allowed_value", "range"}
                for diagnostic in entry.execution.diagnostics
            )
        )

    def test_current_result_is_independent_of_corpus_and_context_order(self):
        self.assertEqual(self.run_current(), self.run_current(reverse=True))


class TestCurrentProductionExportStage(unittest.TestCase):
    @staticmethod
    def run_current(*, reverse=False):
        catalog, context = current_corpus_catalog_and_context(reverse=reverse)
        return stage.run_validation_stage(catalog, "production_export", context)

    def test_checksum_rule_executes_and_other_custom_rules_remain_not_executed(self):
        result = self.run_current()

        self.assertEqual(result.active_rule_count, 5)
        self.assertEqual(result.blocking_rule_count, 5)
        self.assertEqual(result.pass_count, 0)
        self.assertEqual(result.fail_count, 1)
        self.assertEqual(result.unsupported_count, 0)
        self.assertEqual(result.not_executed_count, 4)
        self.assertEqual(result.not_applicable_count, 0)
        self.assertEqual(result.blocking_fail_count, 1)
        self.assertEqual(result.blocking_not_executed_count, 4)
        self.assertEqual(result.stage_verdict, stage.ValidationStageVerdict.BLOCKED)

        failure = next(
            entry
            for entry in result.rule_results
            if entry.execution.outcome is execution.ValidationOutcome.FAIL
        )
        self.assertEqual(
            failure.rule.rule_id,
            "val_source_registry_active_checksum_finalized",
        )
        self.assertEqual(failure.execution.violation_count, 8)
        self.assertEqual(
            {
                entry.rule.rule_id
                for entry in result.rule_results
                if entry.execution.outcome is execution.ValidationOutcome.NOT_EXECUTED
            },
            {
                "cdb_val_cards_legacy_identity_flags_resolved",
                "cdb_val_production_export_contains_no_tbd",
                "val_final_workbook_filename_resolved",
                "val_production_export_contains_no_tbd",
            },
        )

    def test_current_result_is_independent_of_corpus_and_context_order(self):
        self.assertEqual(self.run_current(), self.run_current(reverse=True))


if __name__ == "__main__":
    unittest.main()
