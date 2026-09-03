using Aeterna.Engine.State;

namespace Aeterna.Engine.Runtime;

internal sealed record SealBreakIntentState(
    string IntentId,
    string CombatId,
    string TimingAnchorId,
    string SealSlotId,
    GameObjectRefState AttackerRef,
    bool Prevented,
    string PreventionOutcomeId);

internal sealed record SealOutcomeResolutionPlan(
    string CombatId,
    int CombatStageSequence,
    int StateVersion,
    string TimingAnchorId,
    string OutcomeId,
    string? NoHitReasonId,
    SealBreakIntentState? BreakIntent,
    string? SealBreakId,
    string? SurgeId,
    string OwnerPlayerId,
    string SealSlotId,
    GameObjectRefState AttackerRef,
    GameObjectRefState? SealedObjectRef,
    string? SealedCardId,
    CanonicalSealToHandTransitionPlan? SurgeTransition);

internal sealed record ProvidenceEligibilityEvaluation(
    int CardMagnitude,
    int OwnerMagnitude,
    bool Eligible);

internal static class SealSurgeResolution
{
    internal const string ProvidenceOpportunityId = "providence";
    internal const string UnpreventedOutcomeId = "unprevented";
    internal const string SealBreakCauseKind = "combat_seal_break";

    internal static SealOutcomeResolutionPlan BuildPlan(
        MatchState state,
        PendingCombatState combat,
        RuntimePackageCatalog? runtimePackage,
        CanonicalCardCatalog? canonicalCards)
    {
        ArgumentNullException.ThrowIfNull(state);
        ArgumentNullException.ThrowIfNull(combat);
        if (!string.Equals(combat.StageId, CombatRuleIds.SealOutcomeCheckpointStage, StringComparison.Ordinal)
            || !string.Equals(combat.OriginalTarget.TargetKindId, CombatRuleIds.SealSlotTargetKind, StringComparison.Ordinal)
            || combat.DefenseCommitted)
        {
            throw new EngineStateException(
                "SEAL_OUTCOME_CHECKPOINT_INVALID",
                "Seal outcome resolution requires an undefended seal_outcome_checkpoint Combat.");
        }

        if (runtimePackage is null || canonicalCards is null)
        {
            throw new EngineStateException(
                "SEAL_OUTCOME_AUTHORITY_REQUIRED",
                "Seal outcome resolution requires runtime identity and canonical card Magnitude authority.");
        }

        var timingAnchorId = $"{combat.CombatId}:seal_outcome";
        var owner = state.GetPlayer(combat.DefendingPlayerId);
        if (!string.Equals(combat.OutcomeId, CombatRuleIds.FutureOutcomePending, StringComparison.Ordinal)
            || !string.Equals(
                combat.AttackContinuityStateId,
                CombatRuleIds.AttackContinuityContinuous,
                StringComparison.Ordinal)
            || !CombatRules.IsContinuousDominionEntity(
                state,
                combat.AttackerRef,
                combat.AttackingPlayerId,
                DomainRow.Horizon,
                expectedLaneIndex: null,
                runtimePackage))
        {
            return NoHit(
                state,
                combat,
                timingAnchorId,
                CombatRuleIds.AttackerMissingNoHitReason,
                owner.PlayerId);
        }

        var slot = owner.SealSlots.SingleOrDefault(candidate => string.Equals(
            candidate.SealSlotId,
            combat.OriginalTarget.PublicTargetId,
            StringComparison.Ordinal));
        if (slot is null || slot.LaneIndex != combat.OriginalAttackLaneIndex)
        {
            return NoHit(
                state,
                combat,
                timingAnchorId,
                CombatRuleIds.SealLaneInvalidNoHitReason,
                owner.PlayerId);
        }

        if (!string.Equals(slot.Status, "standing", StringComparison.Ordinal)
            || slot.CardInstanceId is null
            || !state.CardInstances.TryGetValue(slot.CardInstanceId, out var sealedCard)
            || !string.Equals(sealedCard.OwnerPlayerId, owner.PlayerId, StringComparison.Ordinal)
            || !string.Equals(sealedCard.ControllerPlayerId, owner.PlayerId, StringComparison.Ordinal)
            || !string.Equals(sealedCard.Zone, "seal", StringComparison.Ordinal)
            || sealedCard.ZoneIndex != slot.LaneIndex
            || !string.Equals(sealedCard.Visibility, "hidden", StringComparison.Ordinal))
        {
            return NoHit(
                state,
                combat,
                timingAnchorId,
                CombatRuleIds.SealUnavailableNoHitReason,
                owner.PlayerId);
        }

        if (!canonicalCards.DefinitionsById.TryGetValue(sealedCard.CardId, out var definition)
            || !string.Equals(definition.Status, "active", StringComparison.Ordinal))
        {
            throw new EngineStateException(
                "SEAL_SURGE_CARD_DEFINITION_MISSING",
                "The targeted standing Seal has no active canonical card definition.");
        }

        var sealedObjectRef = new GameObjectRefState(
            CombatRuleIds.CardInstanceObjectKind,
            sealedCard.CardInstanceId,
            sealedCard.ZoneSequence);
        var intentId = $"seal_break_intent:{combat.CombatId}:{slot.SealSlotId}";
        var sealBreakId = $"seal_break:{combat.CombatId}:{slot.SealSlotId}";
        var surgeId = $"surge:{combat.CombatId}:{slot.SealSlotId}";
        var intent = new SealBreakIntentState(
            intentId,
            combat.CombatId,
            timingAnchorId,
            slot.SealSlotId,
            combat.AttackerRef,
            Prevented: false,
            UnpreventedOutcomeId);
        var transition = CanonicalSurgeTransition.PlanSealToHand(
            state,
            owner,
            slot,
            sealedObjectRef,
            $"zone_transition:{surgeId}",
            sealBreakId);
        return new SealOutcomeResolutionPlan(
            combat.CombatId,
            combat.StageSequence,
            state.StateVersion,
            timingAnchorId,
            CombatRuleIds.SealBreakCommittedOutcome,
            NoHitReasonId: null,
            intent,
            sealBreakId,
            surgeId,
            owner.PlayerId,
            slot.SealSlotId,
            combat.AttackerRef,
            sealedObjectRef,
            sealedCard.CardId,
            transition);
    }

    internal static ProvidenceEligibilityEvaluation EvaluateProvidenceAfterSurge(
        MatchState state,
        SealOutcomeResolutionPlan plan,
        CanonicalCardCatalog? canonicalCards)
    {
        ArgumentNullException.ThrowIfNull(state);
        ArgumentNullException.ThrowIfNull(plan);
        if (plan.SurgeTransition is null
            || plan.SealedObjectRef is null
            || plan.SealedCardId is null
            || canonicalCards is null)
        {
            throw new EngineStateException(
                "SURGE_OPPORTUNITY_AUTHORITY_REQUIRED",
                "Providence evaluation requires a committed Surge and canonical card authority.");
        }

        var owner = state.GetPlayer(plan.OwnerPlayerId);
        var card = state.GetCardInstance(plan.SealedObjectRef.ObjectId);
        var handIndex = owner.HandCardInstanceIds.IndexOf(card.CardInstanceId);
        if (!string.Equals(card.CardId, plan.SealedCardId, StringComparison.Ordinal)
            || card.ZoneSequence != plan.SurgeTransition.ZoneSequenceAfter
            || !string.Equals(card.OwnerPlayerId, owner.PlayerId, StringComparison.Ordinal)
            || !string.Equals(card.ControllerPlayerId, owner.PlayerId, StringComparison.Ordinal)
            || !string.Equals(card.Zone, "hand", StringComparison.Ordinal)
            || handIndex < 0
            || card.ZoneIndex != handIndex
            || !string.Equals(card.Visibility, "owner_only", StringComparison.Ordinal)
            || !canonicalCards.DefinitionsById.TryGetValue(card.CardId, out var definition)
            || !string.Equals(definition.Status, "active", StringComparison.Ordinal))
        {
            throw new EngineStateException(
                "SURGE_OPPORTUNITY_STATE_INVALID",
                "Providence can be evaluated only after the exact surged card entered owner hand.");
        }

        var ownerMagnitude = owner.WellspringCardInstanceIds.Count;
        return new ProvidenceEligibilityEvaluation(
            definition.Magnitude,
            ownerMagnitude,
            definition.Magnitude > ownerMagnitude);
    }

    internal static void Apply(MatchState state, SealOutcomeResolutionPlan plan)
    {
        ArgumentNullException.ThrowIfNull(state);
        ArgumentNullException.ThrowIfNull(plan);
        var combat = state.PendingCombat;
        if (combat is null
            || !string.Equals(combat.CombatId, plan.CombatId, StringComparison.Ordinal)
            || !string.Equals(combat.StageId, CombatRuleIds.SealOutcomeCheckpointStage, StringComparison.Ordinal)
            || combat.StageSequence != plan.CombatStageSequence
            || state.StateVersion != plan.StateVersion)
        {
            throw new EngineStateException(
                "SEAL_OUTCOME_PLAN_STALE",
                "Seal outcome resolution plan is stale.");
        }

        if (plan.BreakIntent is null || plan.SurgeTransition is null)
        {
            return;
        }

        if (plan.BreakIntent.Prevented
            || !string.Equals(
                plan.BreakIntent.PreventionOutcomeId,
                UnpreventedOutcomeId,
                StringComparison.Ordinal))
        {
            throw new EngineStateException(
                "SEAL_BREAK_PREVENTION_OUTCOME_INVALID",
                "C5 can commit only the explicit unprevented SealBreak intent.");
        }

        CanonicalSurgeTransition.ApplySealToHand(state, plan.SurgeTransition);
    }

    private static SealOutcomeResolutionPlan NoHit(
        MatchState state,
        PendingCombatState combat,
        string timingAnchorId,
        string reasonId,
        string ownerPlayerId) => new(
        combat.CombatId,
        combat.StageSequence,
        state.StateVersion,
        timingAnchorId,
        CombatRuleIds.NoHitOutcome,
        reasonId,
        BreakIntent: null,
        SealBreakId: null,
        SurgeId: null,
        ownerPlayerId,
        combat.OriginalTarget.PublicTargetId,
        combat.AttackerRef,
        SealedObjectRef: null,
        SealedCardId: null,
        SurgeTransition: null);
}
