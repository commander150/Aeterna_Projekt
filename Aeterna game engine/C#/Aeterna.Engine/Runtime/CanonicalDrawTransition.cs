using Aeterna.Engine.State;

namespace Aeterna.Engine.Runtime;

internal sealed record CanonicalDrawTransitionPlan(
    string PlayerId,
    string CardInstanceId,
    string CardId,
    int FromZoneIndex,
    int ToZoneIndex,
    int ZoneSequenceBefore,
    string VisibilityBefore,
    string VisibilityAfter);

internal static class CanonicalDrawTransition
{
    internal static CanonicalDrawTransitionPlan PlanTopCard(
        MatchState state,
        string playerId,
        IReadOnlyList<string> simulatedDeckCardInstanceIds,
        int simulatedHandCount)
    {
        ArgumentNullException.ThrowIfNull(state);
        ArgumentNullException.ThrowIfNull(simulatedDeckCardInstanceIds);
        var player = state.GetPlayer(playerId);
        if (simulatedDeckCardInstanceIds.Count == 0)
        {
            throw new EngineStateException("A draw transition cannot be planned from an empty Deck.");
        }

        var cardInstanceId = simulatedDeckCardInstanceIds[0];
        var card = state.GetCardInstance(cardInstanceId);
        if (!string.Equals(card.OwnerPlayerId, player.PlayerId, StringComparison.Ordinal)
            || !string.Equals(card.ControllerPlayerId, player.PlayerId, StringComparison.Ordinal)
            || !string.Equals(card.Zone, "deck", StringComparison.Ordinal)
            || !string.Equals(card.Visibility, "owner_only", StringComparison.Ordinal)
            || !player.DeckCardInstanceIds.Contains(cardInstanceId, StringComparer.Ordinal)
            || simulatedHandCount < 0)
        {
            throw new EngineStateException("A planned draw does not match authoritative Deck ownership or visibility.");
        }

        return new CanonicalDrawTransitionPlan(
            player.PlayerId,
            card.CardInstanceId,
            card.CardId,
            FromZoneIndex: 0,
            ToZoneIndex: simulatedHandCount,
            card.ZoneSequence,
            card.Visibility,
            VisibilityAfter: "owner_only");
    }

    internal static void Apply(MatchState state, CanonicalDrawTransitionPlan plan)
    {
        ArgumentNullException.ThrowIfNull(state);
        ArgumentNullException.ThrowIfNull(plan);
        var player = state.GetPlayer(plan.PlayerId);
        if (player.DeckCardInstanceIds.Count == 0
            || !string.Equals(player.DeckCardInstanceIds[0], plan.CardInstanceId, StringComparison.Ordinal)
            || player.HandCardInstanceIds.Count != plan.ToZoneIndex)
        {
            throw new EngineStateException("Canonical draw transition plan is stale.");
        }

        var card = state.GetCardInstance(plan.CardInstanceId);
        if (!string.Equals(card.CardId, plan.CardId, StringComparison.Ordinal)
            || !string.Equals(card.OwnerPlayerId, plan.PlayerId, StringComparison.Ordinal)
            || !string.Equals(card.ControllerPlayerId, plan.PlayerId, StringComparison.Ordinal)
            || !string.Equals(card.Zone, "deck", StringComparison.Ordinal)
            || card.ZoneIndex != plan.FromZoneIndex
            || card.ZoneSequence != plan.ZoneSequenceBefore
            || !string.Equals(card.Visibility, plan.VisibilityBefore, StringComparison.Ordinal))
        {
            throw new EngineStateException("Canonical draw transition card state is stale.");
        }

        player.DeckCardInstanceIds.RemoveAt(0);
        player.HandCardInstanceIds.Add(card.CardInstanceId);
        ReindexDeck(state, player.DeckCardInstanceIds);
        card.Zone = "hand";
        card.ZoneIndex = plan.ToZoneIndex;
        card.ZoneSequence += 1;
        card.Visibility = plan.VisibilityAfter;
    }

    private static void ReindexDeck(MatchState state, IReadOnlyList<string> cardInstanceIds)
    {
        for (var index = 0; index < cardInstanceIds.Count; index += 1)
        {
            var card = state.GetCardInstance(cardInstanceIds[index]);
            card.Zone = "deck";
            card.ZoneIndex = index;
        }
    }
}
