"""Deterministic orchestration for the canonical pre-export validation stage."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import TypeAlias

try:  # Package import when the tools directory is on sys.path.
    from .canonical_validation_execution import (
        ValidationDataContext,
        ValidationExecutionDiagnostic,
        ValidationExecutionResult,
        ValidationOutcome,
        execute_allowed_value_rule,
        execute_contract_field_invariant_rule,
        execute_definition_invariant_rule,
        execute_hierarchy_integrity_rule,
        execute_normalized_uniqueness_rule,
        execute_cross_field_consistency_rule,
        execute_target_group_membership_rule,
        execute_qualified_reference_match_rule,
        execute_range_rule,
        execute_reference_integrity_rule,
        execute_supported_custom_expression_rule,
        execute_uniqueness_rule,
    )
    from .canonical_validation_rules import (
        ValidationRuleCatalog,
        ValidationRuleDefinition,
    )
except ImportError:  # Direct file loading used by the repository test suite.
    from canonical_validation_execution import (
        ValidationDataContext,
        ValidationExecutionDiagnostic,
        ValidationExecutionResult,
        ValidationOutcome,
        execute_allowed_value_rule,
        execute_contract_field_invariant_rule,
        execute_definition_invariant_rule,
        execute_hierarchy_integrity_rule,
        execute_normalized_uniqueness_rule,
        execute_cross_field_consistency_rule,
        execute_target_group_membership_rule,
        execute_qualified_reference_match_rule,
        execute_range_rule,
        execute_reference_integrity_rule,
        execute_supported_custom_expression_rule,
        execute_uniqueness_rule,
    )
    from canonical_validation_rules import (
        ValidationRuleCatalog,
        ValidationRuleDefinition,
    )


VALIDATION_EXECUTOR_NOT_REGISTERED = "VALIDATION_EXECUTOR_NOT_REGISTERED"

_PRE_EXPORT_STAGE = "pre_export"
_PRODUCTION_EXPORT_STAGE = "production_export"
_SUPPORTED_STAGES = frozenset({_PRE_EXPORT_STAGE, _PRODUCTION_EXPORT_STAGE})
_ValidationExecutor: TypeAlias = Callable[
    [ValidationRuleDefinition, ValidationDataContext],
    ValidationExecutionResult,
]


class ValidationStageVerdict(str, Enum):
    PASS = "PASS"
    BLOCKED = "BLOCKED"


class ValidationStageExecutionError(RuntimeError):
    """Unexpected executor or executor-result contract failure."""

    def __init__(
        self,
        message: str,
        *,
        stage_id: str,
        rule_id: str | None,
        validation_kind_id: str | None,
    ) -> None:
        super().__init__(message)
        self.stage_id = stage_id
        self.rule_id = rule_id
        self.validation_kind_id = validation_kind_id


@dataclass(frozen=True, slots=True)
class ValidationStageRuleResult:
    rule: ValidationRuleDefinition
    execution: ValidationExecutionResult

    def __post_init__(self) -> None:
        if not isinstance(self.rule, ValidationRuleDefinition):
            raise TypeError("rule must be a ValidationRuleDefinition")
        if not isinstance(self.execution, ValidationExecutionResult):
            raise TypeError("execution must be a ValidationExecutionResult")
        if self.rule.rule_id != self.execution.rule_id:
            raise ValueError("Stage rule and execution result IDs must match.")


@dataclass(frozen=True, slots=True)
class ValidationStageResult:
    stage_id: str
    rule_results: tuple[ValidationStageRuleResult, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.stage_id, str) or not self.stage_id:
            raise ValueError("stage_id must be a non-empty string")
        if not isinstance(self.rule_results, tuple) or any(
            not isinstance(result, ValidationStageRuleResult)
            for result in self.rule_results
        ):
            raise TypeError("rule_results must be a tuple of stage rule results")

    @property
    def active_rule_count(self) -> int:
        return len(self.rule_results)

    @property
    def blocking_rule_count(self) -> int:
        return sum(result.rule.blocking for result in self.rule_results)

    @property
    def nonblocking_rule_count(self) -> int:
        return self.active_rule_count - self.blocking_rule_count

    def _outcome_count(
        self,
        outcome: ValidationOutcome,
        *,
        blocking: bool | None = None,
    ) -> int:
        return sum(
            result.execution.outcome is outcome
            and (blocking is None or result.rule.blocking is blocking)
            for result in self.rule_results
        )

    @property
    def pass_count(self) -> int:
        return self._outcome_count(ValidationOutcome.PASS)

    @property
    def fail_count(self) -> int:
        return self._outcome_count(ValidationOutcome.FAIL)

    @property
    def unsupported_count(self) -> int:
        return self._outcome_count(ValidationOutcome.UNSUPPORTED)

    @property
    def not_executed_count(self) -> int:
        return self._outcome_count(ValidationOutcome.NOT_EXECUTED)

    @property
    def not_applicable_count(self) -> int:
        return self._outcome_count(ValidationOutcome.NOT_APPLICABLE)

    @property
    def blocking_pass_count(self) -> int:
        return self._outcome_count(ValidationOutcome.PASS, blocking=True)

    @property
    def blocking_fail_count(self) -> int:
        return self._outcome_count(ValidationOutcome.FAIL, blocking=True)

    @property
    def blocking_unsupported_count(self) -> int:
        return self._outcome_count(ValidationOutcome.UNSUPPORTED, blocking=True)

    @property
    def blocking_not_executed_count(self) -> int:
        return self._outcome_count(ValidationOutcome.NOT_EXECUTED, blocking=True)

    @property
    def blocking_not_applicable_count(self) -> int:
        return self._outcome_count(ValidationOutcome.NOT_APPLICABLE, blocking=True)

    @property
    def nonblocking_pass_count(self) -> int:
        return self._outcome_count(ValidationOutcome.PASS, blocking=False)

    @property
    def nonblocking_fail_count(self) -> int:
        return self._outcome_count(ValidationOutcome.FAIL, blocking=False)

    @property
    def nonblocking_unsupported_count(self) -> int:
        return self._outcome_count(ValidationOutcome.UNSUPPORTED, blocking=False)

    @property
    def nonblocking_not_executed_count(self) -> int:
        return self._outcome_count(ValidationOutcome.NOT_EXECUTED, blocking=False)

    @property
    def nonblocking_not_applicable_count(self) -> int:
        return self._outcome_count(ValidationOutcome.NOT_APPLICABLE, blocking=False)

    @property
    def stage_verdict(self) -> ValidationStageVerdict:
        if any(
            result.rule.blocking
            and result.execution.outcome
            in {
                ValidationOutcome.FAIL,
                ValidationOutcome.UNSUPPORTED,
                ValidationOutcome.NOT_EXECUTED,
            }
            for result in self.rule_results
        ):
            return ValidationStageVerdict.BLOCKED
        return ValidationStageVerdict.PASS


def _freeze_executor_registry(
    entries: Iterable[tuple[str, _ValidationExecutor]],
) -> Mapping[str, _ValidationExecutor]:
    items = tuple(entries)
    kinds = tuple(kind for kind, _ in items)
    if len(kinds) != len(set(kinds)):
        raise ValueError("Validation executor registry kinds must be unique.")
    if any(not isinstance(kind, str) or not kind for kind in kinds):
        raise ValueError("Validation executor registry kinds must be non-empty strings.")
    if any(not callable(executor) for _, executor in items):
        raise ValueError("Validation executor registry values must be callable.")
    return MappingProxyType(dict(items))


DEFAULT_PRE_EXPORT_EXECUTORS = _freeze_executor_registry(
    (
        ("allowed_value", execute_allowed_value_rule),
        ("contract_field_invariant", execute_contract_field_invariant_rule),
        (
            "custom_expression",
            execute_supported_custom_expression_rule,
        ),
        ("definition_invariant", execute_definition_invariant_rule),
        ("hierarchy_integrity", execute_hierarchy_integrity_rule),
        ("normalized_uniqueness", execute_normalized_uniqueness_rule),
        ("cross_field_consistency", execute_cross_field_consistency_rule),
        ("target_group_membership", execute_target_group_membership_rule),
        (
            "qualified_reference_match",
            execute_qualified_reference_match_rule,
        ),
        ("range", execute_range_rule),
        ("reference_integrity", execute_reference_integrity_rule),
        ("uniqueness", execute_uniqueness_rule),
    )
)
_PRODUCTION_EXPORT_EXECUTORS = _freeze_executor_registry(
    (("custom_expression", execute_supported_custom_expression_rule),)
)


def run_validation_stage(
    catalog: ValidationRuleCatalog,
    stage_id: str,
    data: ValidationDataContext,
    executors: Mapping[str, _ValidationExecutor] | None = None,
) -> ValidationStageResult:
    """Execute one supported catalog stage deterministically."""

    if not isinstance(catalog, ValidationRuleCatalog):
        raise TypeError("catalog must be a ValidationRuleCatalog")
    if not isinstance(stage_id, str):
        raise TypeError("stage_id must be a string")
    if stage_id not in _SUPPORTED_STAGES:
        raise ValueError(
            "Only pre_export and production_export validation stages are supported."
        )
    if not isinstance(data, ValidationDataContext):
        raise TypeError("data must be a ValidationDataContext")
    if executors is None:
        registry = (
            DEFAULT_PRE_EXPORT_EXECUTORS
            if stage_id == _PRE_EXPORT_STAGE
            else _PRODUCTION_EXPORT_EXECUTORS
        )
    else:
        if not isinstance(executors, Mapping):
            raise TypeError("executors must be a mapping")
        registry = _freeze_executor_registry(executors.items())

    selected = tuple(
        sorted(catalog.by_stage(stage_id), key=lambda rule: rule.rule_id.encode("utf-8"))
    )
    results: list[ValidationStageRuleResult] = []
    for rule in selected:
        executor = registry.get(rule.validation_kind_id)
        if executor is None:
            execution = _not_executed_result(rule)
        else:
            try:
                execution = executor(rule, data)
            except Exception as error:
                raise _stage_execution_error(
                    "Validation executor raised an unexpected exception.",
                    rule,
                    stage_id,
                ) from error
            if not isinstance(execution, ValidationExecutionResult):
                raise _stage_execution_error(
                    "Validation executor returned an invalid result type.",
                    rule,
                    stage_id,
                )
            if execution.rule_id != rule.rule_id:
                raise _stage_execution_error(
                    "Validation executor returned a mismatched rule ID.",
                    rule,
                    stage_id,
                )
            if not isinstance(execution.outcome, ValidationOutcome):
                raise _stage_execution_error(
                    "Validation executor returned an invalid outcome.",
                    rule,
                    stage_id,
                )
        results.append(ValidationStageRuleResult(rule, execution))
    return ValidationStageResult(stage_id, tuple(results))


def _not_executed_result(
    rule: ValidationRuleDefinition,
) -> ValidationExecutionResult:
    diagnostic = ValidationExecutionDiagnostic(
        VALIDATION_EXECUTOR_NOT_REGISTERED,
        "No validation executor is registered for the active rule kind.",
        rule.rule_id,
        rule.target_table_id,
        rule.target_field_id,
        observed_value=rule.validation_kind_id,
        expected_contract=(
            "registered public executor for validation_kind_id="
            f"{rule.validation_kind_id}"
        ),
        reason="executor_not_registered",
    )
    return ValidationExecutionResult(
        rule.rule_id,
        ValidationOutcome.NOT_EXECUTED,
        (diagnostic,),
        0,
        0,
    )


def _stage_execution_error(
    message: str,
    rule: ValidationRuleDefinition,
    stage_id: str,
) -> ValidationStageExecutionError:
    return ValidationStageExecutionError(
        message,
        stage_id=stage_id,
        rule_id=rule.rule_id,
        validation_kind_id=rule.validation_kind_id,
    )


__all__ = [
    "DEFAULT_PRE_EXPORT_EXECUTORS",
    "VALIDATION_EXECUTOR_NOT_REGISTERED",
    "ValidationStageExecutionError",
    "ValidationStageResult",
    "ValidationStageRuleResult",
    "ValidationStageVerdict",
    "run_validation_stage",
]
