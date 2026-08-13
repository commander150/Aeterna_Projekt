using System.Collections.Immutable;
using Aeterna.Engine.State;

namespace Aeterna.Engine.Runtime;

internal sealed record CanonicalAwakeningEntryPlan(
    string PlayerId,
    int DrawCount,
    ImmutableArray<string> ReadyCardInstanceIds,
    ImmutableArray<CanonicalDrawTransitionPlan> DrawTransitions);

internal static class CanonicalPhaseLifecycle
{
    internal const string RefreshPenaltyUnsupportedCode =
        "CANONICAL_DRAW_REFRESH_PENALTY_UNSUPPORTED";

    internal static CanonicalAwakeningEntryPlan PlanAwakeningEntry(
        MatchState state,
        string playerId,
        int drawCount)
    {
        ArgumentNullException.ThrowIfNull(state);
        if (drawCount < 0)
        {
            throw new ArgumentOutOfRangeException(nameof(drawCount));
        }

        var player = state.GetPlayer(playerId);
        if (player.DeckCardInstanceIds.Count < drawCount)
        {
            throw new CanonicalAwakeningEntryException(
                RefreshPenaltyUnsupportedCode,
                player.PlayerId,
                drawCount,
                player.DeckCardInstanceIds.Count);
        }

        var readyCards = player.Domain.HorizonCardInstanceIds
            .Concat(player.Domain.ZenithCardInstanceIds)
            .Where(cardInstanceId => cardInstanceId is not null)
            .Select(cardInstanceId => state.GetCardInstance(cardInstanceId!))
            .Concat(player.WellspringCardInstanceIds.Select(state.GetCardInstance))
            .Where(card => string.Equals(card.ControllerPlayerId, player.PlayerId, StringComparison.Ordinal)
                           && string.Equals(card.ActivityState, "exhausted", StringComparison.Ordinal))
            .OrderBy(card => card.CreatedSequence)
            .ThenBy(card => card.CardInstanceId, StringComparer.Ordinal)
            .Select(card => card.CardInstanceId)
            .ToImmutableArray();

        var simulatedDeck = player.DeckCardInstanceIds.ToList();
        var simulatedHandCount = player.HandCardInstanceIds.Count;
        var draws = ImmutableArray.CreateBuilder<CanonicalDrawTransitionPlan>(drawCount);
        for (var index = 0; index < drawCount; index += 1)
        {
            draws.Add(CanonicalDrawTransition.PlanTopCard(
                state,
                player.PlayerId,
                simulatedDeck,
                simulatedHandCount));
            simulatedDeck.RemoveAt(0);
            simulatedHandCount += 1;
        }

        return new CanonicalAwakeningEntryPlan(
            player.PlayerId,
            drawCount,
            readyCards,
            draws.ToImmutable());
    }

    internal static void ApplyAwakeningEntry(
        MatchState state,
        CanonicalAwakeningEntryPlan plan)
    {
        ArgumentNullException.ThrowIfNull(state);
        ArgumentNullException.ThrowIfNull(plan);
        foreach (var cardInstanceId in plan.ReadyCardInstanceIds)
        {
            var card = state.GetCardInstance(cardInstanceId);
            if (!string.Equals(card.ControllerPlayerId, plan.PlayerId, StringComparison.Ordinal)
                || !string.Equals(card.ActivityState, "exhausted", StringComparison.Ordinal)
                || card.Zone is not ("dominion" or "wellspring"))
            {
                throw new EngineStateException("Canonical Awakening ready plan is stale.");
            }

            card.ActivityState = "active";
        }

        foreach (var draw in plan.DrawTransitions)
        {
            CanonicalDrawTransition.Apply(state, draw);
        }
    }
}

internal sealed class CanonicalAwakeningEntryException : Exception
{
    internal CanonicalAwakeningEntryException(
        string code,
        string playerId,
        int requiredDrawCount,
        int availableDeckCount)
        : base("The mandatory Awakening draw cannot be completed before Refresh Penalty exists.")
    {
        Code = code;
        PlayerId = playerId;
        RequiredDrawCount = requiredDrawCount;
        AvailableDeckCount = availableDeckCount;
    }

    internal string Code { get; }

    internal string PlayerId { get; }

    internal int RequiredDrawCount { get; }

    internal int AvailableDeckCount { get; }
}
