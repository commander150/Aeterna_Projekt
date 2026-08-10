using Aeterna.Engine.State;

namespace Aeterna.Engine.Runtime;

internal sealed record CanonicalZoneTransitionPlan(
    string ZoneTransitionInstanceId,
    string CardInstanceId,
    string CardId,
    string OwnerPlayerId,
    string ControllerPlayerId,
    string FromZoneId,
    string ToZoneId,
    string FromZonePresenceInstanceId,
    string ToZonePresenceInstanceId,
    DomainRow FromDomainRow,
    int FromDomainLaneIndex,
    int ToZoneIndex,
    int ZoneSequenceBefore,
    int ZoneSequenceAfter,
    string CauseInstanceId);

internal static class CanonicalZoneTransition
{
    internal static CanonicalZoneTransitionPlan PlanDominionToVoid(
        CardInstanceState card,
        int destinationVoidIndex,
        string transitionInstanceId,
        string causeInstanceId)
    {
        ArgumentNullException.ThrowIfNull(card);
        if (!string.Equals(card.Zone, "dominion", StringComparison.Ordinal)
            || card.DomainRow is not DomainRow row
            || card.DomainLaneIndex is not int laneIndex
            || laneIndex is < 0 or >= DomainState.LaneCount
            || card.ZoneIndex != -1
            || destinationVoidIndex < 0
            || string.IsNullOrWhiteSpace(transitionInstanceId)
            || string.IsNullOrWhiteSpace(causeInstanceId))
        {
            throw new CanonicalAbilityExecutionException(
                "CANONICAL_ZONE_TRANSITION_INVALID",
                "Dominion-to-Void transition preconditions are invalid.");
        }

        var nextZoneSequence = checked(card.ZoneSequence + 1);
        return new CanonicalZoneTransitionPlan(
            transitionInstanceId,
            card.CardInstanceId,
            card.CardId,
            card.OwnerPlayerId,
            card.ControllerPlayerId,
            "dominion",
            "void",
            PresenceId(card.CardInstanceId, card.ZoneSequence),
            PresenceId(card.CardInstanceId, nextZoneSequence),
            row,
            laneIndex,
            destinationVoidIndex,
            card.ZoneSequence,
            nextZoneSequence,
            causeInstanceId);
    }

    internal static void ApplyDominionToVoid(MatchState state, CanonicalZoneTransitionPlan plan)
    {
        ArgumentNullException.ThrowIfNull(state);
        ArgumentNullException.ThrowIfNull(plan);
        var card = state.GetCardInstance(plan.CardInstanceId);
        var controller = state.GetPlayer(plan.ControllerPlayerId);
        var owner = state.GetPlayer(plan.OwnerPlayerId);
        var slots = controller.Domain.GetSlots(plan.FromDomainRow);
        if (!string.Equals(card.CardId, plan.CardId, StringComparison.Ordinal)
            || !string.Equals(card.Zone, plan.FromZoneId, StringComparison.Ordinal)
            || card.DomainRow != plan.FromDomainRow
            || card.DomainLaneIndex != plan.FromDomainLaneIndex
            || !string.Equals(slots[plan.FromDomainLaneIndex], card.CardInstanceId, StringComparison.Ordinal)
            || card.ZoneSequence != plan.ZoneSequenceBefore
            || owner.VoidCardInstanceIds.Count != plan.ToZoneIndex)
        {
            throw new EngineStateException(
                "CANONICAL_ZONE_TRANSITION_STALE",
                "Dominion-to-Void transition plan no longer matches authoritative state.");
        }

        slots[plan.FromDomainLaneIndex] = null;
        owner.VoidCardInstanceIds.Add(card.CardInstanceId);
        card.Zone = plan.ToZoneId;
        card.ZoneIndex = plan.ToZoneIndex;
        card.Visibility = "public";
        card.ActivityState = null;
        card.DomainRow = null;
        card.DomainLaneIndex = null;
        card.EnteredDomainTurnNumber = null;
        card.DamageMarked = 0;
        card.ZoneSequence = plan.ZoneSequenceAfter;
    }

    private static string PresenceId(string cardInstanceId, int zoneSequence) =>
        $"zone_presence_{cardInstanceId}_{zoneSequence:000000}";
}
