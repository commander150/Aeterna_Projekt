using Aeterna.Engine.State;

namespace Aeterna.Engine.Runtime;

internal sealed record CanonicalSealToHandTransitionPlan(
    string TransitionId,
    string CauseKindId,
    string CauseInstanceId,
    string OwnerPlayerId,
    string SealSlotId,
    int SealLaneIndex,
    GameObjectRefState SealedObjectRef,
    string CardId,
    int ToHandIndex,
    int ZoneSequenceAfter,
    string VisibilityBefore,
    string VisibilityAfter);

internal sealed record CanonicalHandToWellspringTransitionPlan(
    string TransitionId,
    string CauseKindId,
    string CauseInstanceId,
    string OwnerPlayerId,
    GameObjectRefState HandObjectRef,
    string CardId,
    int FromHandIndex,
    int ToWellspringIndex,
    int ZoneSequenceAfter,
    string VisibilityBefore,
    string VisibilityAfter);

internal static class CanonicalSurgeTransition
{
    internal const string SealBreakCauseKind = "seal_break";
    internal const string ProvidenceCauseKind = "providence";

    internal static CanonicalSealToHandTransitionPlan PlanSealToHand(
        MatchState state,
        PlayerState owner,
        SealSlotState slot,
        GameObjectRefState sealedObjectRef,
        string transitionId,
        string causeInstanceId)
    {
        ArgumentNullException.ThrowIfNull(state);
        ArgumentNullException.ThrowIfNull(owner);
        ArgumentNullException.ThrowIfNull(slot);
        ArgumentNullException.ThrowIfNull(sealedObjectRef);
        if (!string.Equals(slot.OwnerPlayerId, owner.PlayerId, StringComparison.Ordinal)
            || !string.Equals(slot.Status, "standing", StringComparison.Ordinal)
            || !string.Equals(slot.CardInstanceId, sealedObjectRef.ObjectId, StringComparison.Ordinal)
            || !string.Equals(sealedObjectRef.ObjectKindId, CombatRuleIds.CardInstanceObjectKind, StringComparison.Ordinal)
            || slot.LaneIndex is < 0 or >= DomainState.LaneCount
            || string.IsNullOrWhiteSpace(transitionId)
            || string.IsNullOrWhiteSpace(causeInstanceId))
        {
            throw Invalid("Seal-to-hand transition binding is invalid.");
        }

        var card = state.GetCardInstance(sealedObjectRef.ObjectId);
        if (card.ZoneSequence != sealedObjectRef.IncarnationSequence
            || card.ZoneSequence == int.MaxValue
            || !string.Equals(card.OwnerPlayerId, owner.PlayerId, StringComparison.Ordinal)
            || !string.Equals(card.ControllerPlayerId, owner.PlayerId, StringComparison.Ordinal)
            || !string.Equals(card.Zone, "seal", StringComparison.Ordinal)
            || card.ZoneIndex != slot.LaneIndex
            || !string.Equals(card.Visibility, "hidden", StringComparison.Ordinal)
            || card.ActivityState is not null
            || card.DomainRow is not null
            || card.DomainLaneIndex is not null
            || card.EnteredDomainTurnNumber is not null
            || card.DamageMarked != 0)
        {
            throw Invalid("Seal-to-hand transition source state is invalid.");
        }

        return new CanonicalSealToHandTransitionPlan(
            transitionId,
            SealBreakCauseKind,
            causeInstanceId,
            owner.PlayerId,
            slot.SealSlotId,
            slot.LaneIndex,
            sealedObjectRef,
            card.CardId,
            owner.HandCardInstanceIds.Count,
            checked(card.ZoneSequence + 1),
            card.Visibility,
            "owner_only");
    }

    internal static void ApplySealToHand(
        MatchState state,
        CanonicalSealToHandTransitionPlan plan)
    {
        ArgumentNullException.ThrowIfNull(state);
        ArgumentNullException.ThrowIfNull(plan);
        var owner = state.GetPlayer(plan.OwnerPlayerId);
        var slot = owner.SealSlots.SingleOrDefault(candidate => string.Equals(
            candidate.SealSlotId,
            plan.SealSlotId,
            StringComparison.Ordinal));
        if (slot is null
            || slot.LaneIndex != plan.SealLaneIndex
            || !string.Equals(slot.Status, "standing", StringComparison.Ordinal)
            || !string.Equals(slot.CardInstanceId, plan.SealedObjectRef.ObjectId, StringComparison.Ordinal)
            || owner.HandCardInstanceIds.Count != plan.ToHandIndex)
        {
            throw Stale("Seal-to-hand transition no longer matches its slot or destination.");
        }

        var card = state.GetCardInstance(plan.SealedObjectRef.ObjectId);
        if (!string.Equals(card.CardId, plan.CardId, StringComparison.Ordinal)
            || !string.Equals(card.OwnerPlayerId, owner.PlayerId, StringComparison.Ordinal)
            || !string.Equals(card.ControllerPlayerId, owner.PlayerId, StringComparison.Ordinal)
            || !string.Equals(card.Zone, "seal", StringComparison.Ordinal)
            || card.ZoneIndex != plan.SealLaneIndex
            || card.ZoneSequence != plan.SealedObjectRef.IncarnationSequence
            || !string.Equals(card.Visibility, plan.VisibilityBefore, StringComparison.Ordinal))
        {
            throw Stale("Seal-to-hand transition card state is stale.");
        }

        slot.Status = "broken";
        slot.CardInstanceId = null;
        owner.HandCardInstanceIds.Add(card.CardInstanceId);
        card.Zone = "hand";
        card.ZoneIndex = plan.ToHandIndex;
        card.Visibility = plan.VisibilityAfter;
        card.ActivityState = null;
        card.DomainRow = null;
        card.DomainLaneIndex = null;
        card.EnteredDomainTurnNumber = null;
        card.DamageMarked = 0;
        card.ZoneSequence = plan.ZoneSequenceAfter;
    }

    internal static CanonicalHandToWellspringTransitionPlan PlanHandToWellspring(
        MatchState state,
        PendingSurgeWindowState window,
        string transitionId,
        string causeInstanceId)
    {
        ArgumentNullException.ThrowIfNull(state);
        ArgumentNullException.ThrowIfNull(window);
        if (string.IsNullOrWhiteSpace(transitionId) || string.IsNullOrWhiteSpace(causeInstanceId))
        {
            throw Invalid("Hand-to-Wellspring transition identity is invalid.");
        }

        var (owner, card, fromHandIndex) = ResolveSurgedCardInHand(state, window);
        if (card.ZoneSequence == int.MaxValue)
        {
            throw Invalid("Providence transition cannot advance the surged card incarnation.");
        }

        return new CanonicalHandToWellspringTransitionPlan(
            transitionId,
            ProvidenceCauseKind,
            causeInstanceId,
            owner.PlayerId,
            window.SurgedObjectRef,
            card.CardId,
            fromHandIndex,
            owner.WellspringCardInstanceIds.Count,
            checked(card.ZoneSequence + 1),
            card.Visibility,
            "owner_only");
    }

    internal static void ValidateSurgedCardInHand(
        MatchState state,
        PendingSurgeWindowState window) => _ = ResolveSurgedCardInHand(state, window);

    internal static void ApplyHandToWellspring(
        MatchState state,
        CanonicalHandToWellspringTransitionPlan plan)
    {
        ArgumentNullException.ThrowIfNull(state);
        ArgumentNullException.ThrowIfNull(plan);
        var owner = state.GetPlayer(plan.OwnerPlayerId);
        if (plan.FromHandIndex < 0
            || plan.FromHandIndex >= owner.HandCardInstanceIds.Count
            || !string.Equals(
                owner.HandCardInstanceIds[plan.FromHandIndex],
                plan.HandObjectRef.ObjectId,
                StringComparison.Ordinal)
            || owner.WellspringCardInstanceIds.Count != plan.ToWellspringIndex)
        {
            throw Stale("Hand-to-Wellspring transition zone membership is stale.");
        }

        var card = state.GetCardInstance(plan.HandObjectRef.ObjectId);
        if (!string.Equals(card.CardId, plan.CardId, StringComparison.Ordinal)
            || !string.Equals(card.OwnerPlayerId, owner.PlayerId, StringComparison.Ordinal)
            || !string.Equals(card.ControllerPlayerId, owner.PlayerId, StringComparison.Ordinal)
            || !string.Equals(card.Zone, "hand", StringComparison.Ordinal)
            || card.ZoneIndex != plan.FromHandIndex
            || card.ZoneSequence != plan.HandObjectRef.IncarnationSequence
            || !string.Equals(card.Visibility, plan.VisibilityBefore, StringComparison.Ordinal))
        {
            throw Stale("Hand-to-Wellspring transition card state is stale.");
        }

        owner.HandCardInstanceIds.RemoveAt(plan.FromHandIndex);
        ReindexHand(state, owner.HandCardInstanceIds);
        owner.WellspringCardInstanceIds.Add(card.CardInstanceId);
        card.Zone = "wellspring";
        card.ZoneIndex = plan.ToWellspringIndex;
        card.Visibility = plan.VisibilityAfter;
        card.ActivityState = "active";
        card.ZoneSequence = plan.ZoneSequenceAfter;
    }

    private static void ReindexHand(MatchState state, IReadOnlyList<string> cardInstanceIds)
    {
        for (var index = 0; index < cardInstanceIds.Count; index += 1)
        {
            var card = state.GetCardInstance(cardInstanceIds[index]);
            card.Zone = "hand";
            card.ZoneIndex = index;
        }
    }

    private static (PlayerState Owner, CardInstanceState Card, int HandIndex) ResolveSurgedCardInHand(
        MatchState state,
        PendingSurgeWindowState window)
    {
        var owner = state.GetPlayer(window.OwnerPlayerId);
        var card = state.GetCardInstance(window.SurgedObjectRef.ObjectId);
        var handIndex = owner.HandCardInstanceIds.IndexOf(card.CardInstanceId);
        if (!string.Equals(
                window.SurgedObjectRef.ObjectKindId,
                CombatRuleIds.CardInstanceObjectKind,
                StringComparison.Ordinal)
            || card.ZoneSequence != window.SurgedObjectRef.IncarnationSequence
            || !string.Equals(card.OwnerPlayerId, owner.PlayerId, StringComparison.Ordinal)
            || !string.Equals(card.ControllerPlayerId, owner.PlayerId, StringComparison.Ordinal)
            || !string.Equals(card.Zone, "hand", StringComparison.Ordinal)
            || handIndex < 0
            || card.ZoneIndex != handIndex
            || !string.Equals(card.Visibility, "owner_only", StringComparison.Ordinal)
            || card.ActivityState is not null
            || card.DomainRow is not null
            || card.DomainLaneIndex is not null
            || card.EnteredDomainTurnNumber is not null
            || card.DamageMarked != 0)
        {
            throw Invalid("Providence source is not the exact surged hand incarnation.");
        }

        return (owner, card, handIndex);
    }

    private static EngineStateException Invalid(string message) => new(
        "CANONICAL_SURGE_TRANSITION_INVALID",
        message);

    private static EngineStateException Stale(string message) => new(
        "CANONICAL_SURGE_TRANSITION_STALE",
        message);
}
