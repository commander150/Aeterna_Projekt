using Aeterna.Engine.State;

namespace Aeterna.Engine.Runtime;

internal static class CanonicalZoneTransitionCauseKinds
{
    internal const string DamageLethal = "damage_lethal";
    internal const string DestroyEffect = "destroy_effect";
    internal const string MoveEffect = "move_effect";
}

internal sealed record CanonicalProposedZoneTransition(
    string ZoneTransitionInstanceId,
    string CardInstanceId,
    string CardId,
    string FromZoneId,
    string ToZoneId,
    string DestinationPlayerId,
    string CauseKindId,
    string CauseInstanceId);

internal sealed record CanonicalActualZoneTransition(
    string ZoneTransitionInstanceId,
    string CardInstanceId,
    string CardId,
    string OwnerPlayerId,
    string ControllerPlayerIdBefore,
    string ControllerPlayerIdAfter,
    string FromZoneId,
    string ToZoneId,
    string FromZonePresenceInstanceId,
    string ToZonePresenceInstanceId,
    DomainRow FromDomainRow,
    int FromDomainLaneIndex,
    int ToZoneIndex,
    int ZoneSequenceBefore,
    int ZoneSequenceAfter,
    string VisibilityBefore,
    string VisibilityAfter,
    string CauseKindId,
    string CauseInstanceId);

internal sealed record CanonicalZoneTransitionPlan(
    CanonicalProposedZoneTransition Proposed,
    CanonicalActualZoneTransition Actual);

internal static class CanonicalZoneTransition
{
    internal static CanonicalZoneTransitionPlan PlanDominionToVoid(
        CardInstanceState card,
        int destinationVoidIndex,
        string transitionInstanceId,
        string causeKindId,
        string causeInstanceId) => PlanDominionDeparture(
            card,
            destinationVoidIndex,
            transitionInstanceId,
            "void",
            card.OwnerPlayerId,
            "public",
            causeKindId,
            causeInstanceId);

    internal static CanonicalZoneTransitionPlan PlanDominionToHand(
        CardInstanceState card,
        int destinationHandIndex,
        string transitionInstanceId,
        string causeInstanceId) => PlanDominionDeparture(
            card,
            destinationHandIndex,
            transitionInstanceId,
            "hand",
            card.OwnerPlayerId,
            "owner_only",
            CanonicalZoneTransitionCauseKinds.MoveEffect,
            causeInstanceId);

    internal static void Apply(MatchState state, CanonicalZoneTransitionPlan plan)
    {
        ArgumentNullException.ThrowIfNull(state);
        ArgumentNullException.ThrowIfNull(plan);
        if (!Equals(plan.Proposed, ToProposed(plan.Actual)))
        {
            throw new EngineStateException(
                "CANONICAL_ZONE_TRANSITION_REPLACEMENT_INVALID",
                "Actual transition is inconsistent with the accepted proposed transition.");
        }

        var actual = plan.Actual;
        var card = state.GetCardInstance(actual.CardInstanceId);
        var controller = state.GetPlayer(actual.ControllerPlayerIdBefore);
        var owner = state.GetPlayer(actual.OwnerPlayerId);
        var slots = controller.Domain.GetSlots(actual.FromDomainRow);
        var destination = string.Equals(actual.ToZoneId, "void", StringComparison.Ordinal)
            ? owner.VoidCardInstanceIds
            : string.Equals(actual.ToZoneId, "hand", StringComparison.Ordinal)
                ? owner.HandCardInstanceIds
                : throw Invalid("Actual destination is outside the supported Dominion departure slice.");
        if (!string.Equals(card.CardId, actual.CardId, StringComparison.Ordinal)
            || !string.Equals(card.OwnerPlayerId, actual.OwnerPlayerId, StringComparison.Ordinal)
            || !string.Equals(card.ControllerPlayerId, actual.ControllerPlayerIdBefore, StringComparison.Ordinal)
            || !string.Equals(card.Zone, actual.FromZoneId, StringComparison.Ordinal)
            || card.DomainRow != actual.FromDomainRow
            || card.DomainLaneIndex != actual.FromDomainLaneIndex
            || !string.Equals(slots[actual.FromDomainLaneIndex], card.CardInstanceId, StringComparison.Ordinal)
            || card.ZoneSequence != actual.ZoneSequenceBefore
            || destination.Count != actual.ToZoneIndex)
        {
            throw new EngineStateException(
                "CANONICAL_ZONE_TRANSITION_STALE",
                "Canonical zone-transition plan no longer matches authoritative state.");
        }

        slots[actual.FromDomainLaneIndex] = null;
        destination.Add(card.CardInstanceId);
        card.ControllerPlayerId = actual.ControllerPlayerIdAfter;
        card.Zone = actual.ToZoneId;
        card.ZoneIndex = actual.ToZoneIndex;
        card.Visibility = actual.VisibilityAfter;
        card.ActivityState = null;
        card.DomainRow = null;
        card.DomainLaneIndex = null;
        card.EnteredDomainTurnNumber = null;
        card.DamageMarked = 0;
        card.ZoneSequence = actual.ZoneSequenceAfter;
    }

    private static CanonicalZoneTransitionPlan PlanDominionDeparture(
        CardInstanceState card,
        int destinationIndex,
        string transitionInstanceId,
        string destinationZoneId,
        string destinationPlayerId,
        string visibilityAfter,
        string causeKindId,
        string causeInstanceId)
    {
        ArgumentNullException.ThrowIfNull(card);
        if (!string.Equals(card.Zone, "dominion", StringComparison.Ordinal)
            || card.DomainRow is not DomainRow row
            || card.DomainLaneIndex is not int laneIndex
            || laneIndex is < 0 or >= DomainState.LaneCount
            || card.ZoneIndex != -1
            || destinationIndex < 0
            || destinationZoneId is not ("void" or "hand")
            || !string.Equals(destinationPlayerId, card.OwnerPlayerId, StringComparison.Ordinal)
            || string.IsNullOrWhiteSpace(transitionInstanceId)
            || string.IsNullOrWhiteSpace(causeKindId)
            || string.IsNullOrWhiteSpace(causeInstanceId))
        {
            throw Invalid("Dominion departure transition preconditions are invalid.");
        }

        var nextZoneSequence = checked(card.ZoneSequence + 1);
        var proposed = new CanonicalProposedZoneTransition(
            transitionInstanceId,
            card.CardInstanceId,
            card.CardId,
            "dominion",
            destinationZoneId,
            destinationPlayerId,
            causeKindId,
            causeInstanceId);
        // Replacement evaluation is deliberately a future hook. In v1 every
        // supported proposal becomes the authoritative actual transition.
        var actual = new CanonicalActualZoneTransition(
            transitionInstanceId,
            card.CardInstanceId,
            card.CardId,
            card.OwnerPlayerId,
            card.ControllerPlayerId,
            card.OwnerPlayerId,
            "dominion",
            destinationZoneId,
            PresenceId(card.CardInstanceId, card.ZoneSequence),
            PresenceId(card.CardInstanceId, nextZoneSequence),
            row,
            laneIndex,
            destinationIndex,
            card.ZoneSequence,
            nextZoneSequence,
            card.Visibility,
            visibilityAfter,
            causeKindId,
            causeInstanceId);
        return new CanonicalZoneTransitionPlan(proposed, actual);
    }

    private static CanonicalProposedZoneTransition ToProposed(CanonicalActualZoneTransition actual) => new(
        actual.ZoneTransitionInstanceId,
        actual.CardInstanceId,
        actual.CardId,
        actual.FromZoneId,
        actual.ToZoneId,
        actual.OwnerPlayerId,
        actual.CauseKindId,
        actual.CauseInstanceId);

    private static CanonicalAbilityExecutionException Invalid(string message) => new(
        "CANONICAL_ZONE_TRANSITION_INVALID",
        message);

    private static string PresenceId(string cardInstanceId, int zoneSequence) =>
        $"zone_presence_{cardInstanceId}_{zoneSequence:000000}";
}
