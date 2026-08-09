using System.Collections.Immutable;
using Aeterna.Engine.State;

namespace Aeterna.Engine.Runtime;

internal sealed record CanonicalTargetCandidate(
    string TargetId,
    string CardInstanceId,
    string CardId,
    string ControllerPlayerId,
    string ZoneId,
    string DomainRowId,
    int LaneIndex,
    string ActivityStateId);

internal sealed record CanonicalResolvedTargetSelection(
    CanonicalAbilityTargetDefinition Definition,
    ImmutableArray<CanonicalTargetCandidate> SelectedCards);

internal static class CanonicalTargetResolver
{
    private const string ActiveStatus = "active";

    internal static ImmutableArray<CanonicalAbilityTargetDefinition> GetSupportedTargets(
        CanonicalAbilityDefinition ability)
    {
        ArgumentNullException.ThrowIfNull(ability);
        var targets = ability.Targets
            .Where(target => string.Equals(target.Status, ActiveStatus, StringComparison.Ordinal))
            .ToImmutableArray();
        if (targets.Length != 1)
        {
            throw Unsupported("The first canonical target runtime slice requires exactly one active target definition.");
        }

        RequireSupportedContract(targets[0]);
        return targets;
    }

    internal static ImmutableArray<CanonicalTargetCandidate> ResolveCandidates(
        CanonicalAbilityTargetDefinition target,
        string abilityControllerPlayerId,
        MatchState state,
        RuntimePackageCatalog runtimePackage)
    {
        ArgumentNullException.ThrowIfNull(target);
        ArgumentNullException.ThrowIfNull(state);
        ArgumentNullException.ThrowIfNull(runtimePackage);
        RequireSupportedContract(target);

        if (state.Players.All(player => !string.Equals(
                player.PlayerId,
                abilityControllerPlayerId,
                StringComparison.Ordinal)))
        {
            throw new EngineStateException(
                "CANONICAL_TARGET_CONTROLLER_INVALID",
                "Canonical target resolution references an unknown ability controller.");
        }

        var candidates = ImmutableArray.CreateBuilder<CanonicalTargetCandidate>();
        foreach (var player in state.Players.Where(player => !string.Equals(
                     player.PlayerId,
                     abilityControllerPlayerId,
                     StringComparison.Ordinal)))
        {
            for (var laneIndex = 0; laneIndex < DomainState.LaneCount; laneIndex += 1)
            {
                var cardInstanceId = player.Domain.HorizonCardInstanceIds[laneIndex];
                if (cardInstanceId is null)
                {
                    continue;
                }

                var card = state.GetCardInstance(cardInstanceId);
                if (!runtimePackage.Cards.TryGetValue(card.CardId, out var cardDefinition))
                {
                    throw new EngineStateException(
                        "CANONICAL_TARGET_CARD_DEFINITION_MISSING",
                        "A Domain card has no validated gameplay runtime definition.");
                }

                if (!string.Equals(cardDefinition.CardType, target.CardTypeId, StringComparison.Ordinal)
                    || !string.Equals(card.Zone, target.ZoneId, StringComparison.Ordinal)
                    || card.DomainRow != DomainRow.Horizon
                    || !string.Equals(card.ActivityState, target.ActivityStateId, StringComparison.Ordinal))
                {
                    continue;
                }

                candidates.Add(new CanonicalTargetCandidate(
                    target.TargetId,
                    card.CardInstanceId,
                    card.CardId,
                    card.ControllerPlayerId,
                    card.Zone,
                    "horizont",
                    laneIndex,
                    card.ActivityState!));
            }
        }

        // This is a stable UI/runtime enumeration order, not game-semantic priority.
        return candidates
            .OrderBy(candidate => state.Players.FindIndex(player => string.Equals(
                player.PlayerId,
                candidate.ControllerPlayerId,
                StringComparison.Ordinal)))
            .ThenBy(candidate => candidate.LaneIndex)
            .ThenBy(candidate => candidate.CardInstanceId, StringComparer.Ordinal)
            .ToImmutableArray();
    }

    internal static CanonicalResolvedTargetSelection ValidateSelection(
        CanonicalAbilityTargetDefinition target,
        ImmutableArray<string> selectedCardInstanceIds,
        string abilityControllerPlayerId,
        MatchState state,
        RuntimePackageCatalog runtimePackage)
    {
        RequireSupportedContract(target);
        if (selectedCardInstanceIds.IsDefault)
        {
            throw new CanonicalAbilityExecutionException(
                "RESOLVE_TRIGGER_TARGET_SELECTION_INVALID",
                "Canonical target selection is missing.");
        }

        if (selectedCardInstanceIds.Any(string.IsNullOrWhiteSpace))
        {
            throw new CanonicalAbilityExecutionException(
                "RESOLVE_TRIGGER_TARGET_UNKNOWN",
                "Canonical target selection contains an empty card instance ID.");
        }

        if (selectedCardInstanceIds.Distinct(StringComparer.Ordinal).Count() != selectedCardInstanceIds.Length)
        {
            throw new CanonicalAbilityExecutionException(
                "RESOLVE_TRIGGER_TARGET_DUPLICATE",
                "Canonical target selection contains a duplicate card instance ID.");
        }

        if (selectedCardInstanceIds.Length < target.MinimumTargets
            || selectedCardInstanceIds.Length > target.MaximumTargets)
        {
            throw new CanonicalAbilityExecutionException(
                "RESOLVE_TRIGGER_TARGET_COUNT_INVALID",
                "Canonical target selection count is outside the declared minimum/maximum range.");
        }

        var candidates = ResolveCandidates(target, abilityControllerPlayerId, state, runtimePackage);
        var candidatesById = candidates.ToImmutableDictionary(
            candidate => candidate.CardInstanceId,
            StringComparer.Ordinal);
        var selected = ImmutableArray.CreateBuilder<CanonicalTargetCandidate>();
        foreach (var cardInstanceId in selectedCardInstanceIds)
        {
            if (!state.CardInstances.ContainsKey(cardInstanceId))
            {
                throw new CanonicalAbilityExecutionException(
                    "RESOLVE_TRIGGER_TARGET_UNKNOWN",
                    "Canonical target selection references an unknown card instance.");
            }

            if (!candidatesById.TryGetValue(cardInstanceId, out var candidate))
            {
                throw new CanonicalAbilityExecutionException(
                    "RESOLVE_TRIGGER_TARGET_ILLEGAL",
                    "Selected card instance does not currently satisfy the canonical target contract.");
            }

            selected.Add(candidate);
        }

        return new CanonicalResolvedTargetSelection(target, selected.ToImmutable());
    }

    private static void RequireSupportedContract(CanonicalAbilityTargetDefinition target)
    {
        if (!string.Equals(target.Status, ActiveStatus, StringComparison.Ordinal)
            || !string.Equals(target.TargetPrimitiveId, "target_choose_one_card", StringComparison.Ordinal)
            || !string.Equals(target.ReferenceTypeId, "ref_selected_card_exactly_one", StringComparison.Ordinal)
            || !string.Equals(target.GameObjectId, "card_instance", StringComparison.Ordinal)
            || !string.Equals(target.CardTypeId, "entity", StringComparison.Ordinal)
            || !string.Equals(target.PlayerReferenceId, "opponent_of_ability_controller", StringComparison.Ordinal)
            || !string.Equals(target.ZoneId, "dominion", StringComparison.Ordinal)
            || !string.Equals(target.DomainRowId, "horizont", StringComparison.Ordinal)
            || target.DomainLaneId is not null
            || !string.Equals(target.ActivityStateId, "active", StringComparison.Ordinal)
            || !string.Equals(target.SelectionMethodId, "controller_choice", StringComparison.Ordinal)
            || target.MinimumTargets != 1
            || target.MaximumTargets != 1
            || target.FilterConditionId is not null
            || target.Optional)
        {
            throw Unsupported("Canonical target definition is outside the first choose-one exhaust-card runtime slice.");
        }
    }

    private static CanonicalAbilityExecutionException Unsupported(string message) => new(
        "CANONICAL_TARGET_CONTRACT_UNSUPPORTED",
        message);
}
