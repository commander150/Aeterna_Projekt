using Aeterna.Engine.Contracts;
using Aeterna.Engine.State;

namespace Aeterna.Engine.Runtime;

internal sealed record AeternalOutcomeResolutionPlan(
    string CombatId,
    int CombatStageSequence,
    int StateVersion,
    string TimingAnchorId,
    string OutcomeId,
    string? NoHitReasonId,
    bool SuccessfulHit,
    GameObjectRefState AttackerRef,
    string WinnerPlayerId,
    string LoserPlayerId,
    string TargetId,
    int StandingSealCount);

internal static class AeternalOutcomeResolution
{
    internal const string MatchInProgressStatus = "in_progress";
    internal const string MatchEndedStatus = "ended";
    internal const string VictoryOutcome = "victory";
    internal const string AeternalHitReasonId = "aeternal_hit";

    internal static AeternalOutcomeResolutionPlan BuildPlan(
        MatchState state,
        PendingCombatState combat,
        RuntimePackageCatalog? runtimePackage)
    {
        ArgumentNullException.ThrowIfNull(state);
        ArgumentNullException.ThrowIfNull(combat);
        if (!ReferenceEquals(state.PendingCombat, combat)
            || !string.Equals(
                combat.StageId,
                CombatRuleIds.AeternalOutcomeCheckpointStage,
                StringComparison.Ordinal)
            || !string.Equals(
                combat.OriginalTarget.TargetKindId,
                CombatRuleIds.AeternalTargetKind,
                StringComparison.Ordinal)
            || !string.Equals(
                combat.OriginalTarget.PublicTargetId,
                $"aeternal:{combat.DefendingPlayerId}",
                StringComparison.Ordinal)
            || !string.Equals(
                combat.OutcomeId,
                CombatRuleIds.FutureOutcomePending,
                StringComparison.Ordinal)
            || combat.DefenseCommitted
            || state.Result.Completed
            || state.ReactionWindow is not null
            || state.PendingSurgeWindow is not null
            || state.PendingTriggerWindow is not null
            || state.QueuedTriggerBatches.Count != 0)
        {
            throw new EngineStateException(
                "Aeternal outcome can only be planned from the unblocked aeternal_outcome_checkpoint.");
        }

        if (runtimePackage is null)
        {
            throw new EngineStateException(
                "Aeternal outcome requires runtime Entity identity authority.");
        }

        var standingSealCount = state.GetPlayer(combat.DefendingPlayerId).SealSlots.Count(slot =>
            string.Equals(slot.Status, "standing", StringComparison.Ordinal));
        var attackerContinuous = CombatRules.IsContinuousDominionEntity(
            state,
            combat.AttackerRef,
            combat.AttackingPlayerId,
            DomainRow.Horizon,
            expectedLaneIndex: null,
            runtimePackage);
        if (!attackerContinuous)
        {
            return NoHit(
                state,
                combat,
                standingSealCount,
                CombatRuleIds.AttackerMissingNoHitReason);
        }

        if (standingSealCount != 0)
        {
            return NoHit(
                state,
                combat,
                standingSealCount,
                CombatRuleIds.StandingSealRestoredNoHitReason);
        }

        return new AeternalOutcomeResolutionPlan(
            combat.CombatId,
            combat.StageSequence,
            state.StateVersion,
            $"{combat.CombatId}:aeternal_outcome",
            CombatRuleIds.AeternalHitOutcome,
            NoHitReasonId: null,
            SuccessfulHit: true,
            combat.AttackerRef,
            combat.AttackingPlayerId,
            combat.DefendingPlayerId,
            combat.OriginalTarget.PublicTargetId,
            StandingSealCount: 0);
    }

    internal static void Apply(
        MatchState state,
        AeternalOutcomeResolutionPlan plan,
        RuntimePackageCatalog? runtimePackage)
    {
        ArgumentNullException.ThrowIfNull(state);
        ArgumentNullException.ThrowIfNull(plan);
        var combat = state.PendingCombat;
        if (combat is null
            || !string.Equals(combat.CombatId, plan.CombatId, StringComparison.Ordinal)
            || !string.Equals(
                combat.StageId,
                CombatRuleIds.AeternalOutcomeCheckpointStage,
                StringComparison.Ordinal)
            || !string.Equals(
                combat.OriginalTarget.TargetKindId,
                CombatRuleIds.AeternalTargetKind,
                StringComparison.Ordinal)
            || !string.Equals(
                combat.OutcomeId,
                CombatRuleIds.FutureOutcomePending,
                StringComparison.Ordinal)
            || combat.StageSequence != plan.CombatStageSequence
            || combat.DefenseCommitted
            || state.StateVersion != plan.StateVersion
            || state.Result.Completed
            || state.ReactionWindow is not null
            || state.PendingSurgeWindow is not null
            || state.PendingTriggerWindow is not null
            || state.QueuedTriggerBatches.Count != 0
            || !string.Equals(combat.AttackingPlayerId, plan.WinnerPlayerId, StringComparison.Ordinal)
            || !string.Equals(combat.DefendingPlayerId, plan.LoserPlayerId, StringComparison.Ordinal)
            || !string.Equals(
                combat.OriginalTarget.PublicTargetId,
                plan.TargetId,
                StringComparison.Ordinal))
        {
            throw new EngineStateException("Aeternal outcome plan is stale.");
        }

        if (runtimePackage is null)
        {
            throw new EngineStateException(
                "Aeternal outcome requires runtime Entity identity authority.");
        }

        var standingSealCount = state.GetPlayer(plan.LoserPlayerId).SealSlots.Count(slot =>
            string.Equals(slot.Status, "standing", StringComparison.Ordinal));
        var attackerContinuous = CombatRules.IsContinuousDominionEntity(
            state,
            plan.AttackerRef,
            plan.WinnerPlayerId,
            DomainRow.Horizon,
            expectedLaneIndex: null,
            runtimePackage);
        var expectedSuccessfulHit = attackerContinuous && standingSealCount == 0;
        var expectedNoHitReasonId = attackerContinuous
            ? standingSealCount == 0
                ? null
                : CombatRuleIds.StandingSealRestoredNoHitReason
            : CombatRuleIds.AttackerMissingNoHitReason;
        if (standingSealCount != plan.StandingSealCount
            || plan.SuccessfulHit != expectedSuccessfulHit
            || plan.SuccessfulHit != string.Equals(
                plan.OutcomeId,
                CombatRuleIds.AeternalHitOutcome,
                StringComparison.Ordinal)
            || !string.Equals(
                plan.NoHitReasonId,
                expectedNoHitReasonId,
                StringComparison.Ordinal))
        {
            throw new EngineStateException(
                "Aeternal outcome plan no longer matches attacker or standing-Seal state.");
        }

        if (!plan.SuccessfulHit)
        {
            return;
        }

        state.Result = new MatchResult(
            ContractSchemas.MatchResult,
            Completed: true,
            MatchEndedStatus,
            VictoryOutcome,
            plan.WinnerPlayerId,
            plan.LoserPlayerId,
            AeternalHitReasonId,
            plan.CombatId,
            plan.StateVersion);
    }

    private static AeternalOutcomeResolutionPlan NoHit(
        MatchState state,
        PendingCombatState combat,
        int standingSealCount,
        string reasonId) => new(
        combat.CombatId,
        combat.StageSequence,
        state.StateVersion,
        $"{combat.CombatId}:aeternal_outcome",
        CombatRuleIds.NoHitOutcome,
        reasonId,
        SuccessfulHit: false,
        combat.AttackerRef,
        combat.AttackingPlayerId,
        combat.DefendingPlayerId,
        combat.OriginalTarget.PublicTargetId,
        standingSealCount);
}
