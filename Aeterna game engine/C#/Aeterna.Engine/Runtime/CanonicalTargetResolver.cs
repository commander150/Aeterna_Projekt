using System.Collections.Immutable;
using Aeterna.Engine.State;

namespace Aeterna.Engine.Runtime;

internal sealed record CanonicalTargetCandidate(
    string TargetId,
    string CardInstanceId,
    string CardId,
    string ControllerPlayerId,
    string ZoneId,
    string? DomainRowId,
    int? LaneIndex,
    string? ActivityStateId);

internal abstract record CanonicalResolvedTargetValue;

internal sealed record CanonicalResolvedCardTargets(
    ImmutableArray<CanonicalTargetCandidate> Cards) : CanonicalResolvedTargetValue;

internal sealed record CanonicalResolvedPlayerTarget(
    string PlayerId) : CanonicalResolvedTargetValue;

internal sealed record CanonicalResolvedTargetSet(
    CanonicalAbilityTargetDefinition Definition,
    string ResolutionModeId,
    CanonicalResolvedTargetValue Value,
    string AbilityControllerPlayerId,
    int SnapshotSequence)
{
    internal ImmutableArray<CanonicalTargetCandidate> SelectedCards => Value is CanonicalResolvedCardTargets cards
        ? cards.Cards
        : ImmutableArray<CanonicalTargetCandidate>.Empty;

    internal string? ReferencedPlayerId => Value is CanonicalResolvedPlayerTarget player
        ? player.PlayerId
        : null;
}

internal static class CanonicalTargetResolver
{
    internal const string ControllerChoiceSelectionMethodId = "controller_choice";
    internal const string AllMatchingSelectionMethodId = "all_matching";
    internal const string AutomaticReferenceSelectionMethodId = "automatic_reference";

    private const string ActiveStatus = "active";

    internal static ImmutableArray<CanonicalAbilityTargetDefinition> GetSupportedTargets(
        CanonicalAbilityDefinition ability)
    {
        ArgumentNullException.ThrowIfNull(ability);
        var targets = ability.Targets
            .Where(target => string.Equals(target.Status, ActiveStatus, StringComparison.Ordinal))
            .OrderBy(target => target.Sequence)
            .ThenBy(target => target.TargetId, StringComparer.Ordinal)
            .ToImmutableArray();
        if (targets.Length == 0)
        {
            throw Unsupported("The canonical target runtime slice requires at least one active target definition.");
        }

        foreach (var target in targets)
        {
            RequireSupportedContract(target, ability);
        }

        return targets;
    }

    internal static bool IsClientSelectable(CanonicalAbilityTargetDefinition target) => string.Equals(
        target.SelectionMethodId,
        ControllerChoiceSelectionMethodId,
        StringComparison.Ordinal);

    internal static bool IsAutomaticCollection(CanonicalAbilityTargetDefinition target) => string.Equals(
        target.SelectionMethodId,
        AllMatchingSelectionMethodId,
        StringComparison.Ordinal);

    internal static ImmutableArray<CanonicalTargetCandidate> ResolveCandidates(
        CanonicalAbilityTargetDefinition target,
        CanonicalAbilityDefinition ability,
        string abilityControllerPlayerId,
        MatchState state,
        RuntimePackageCatalog runtimePackage,
        CanonicalCardCatalog? canonicalCards,
        CanonicalAbilityCatalog? canonicalAbilities = null)
    {
        ArgumentNullException.ThrowIfNull(target);
        ArgumentNullException.ThrowIfNull(ability);
        ArgumentNullException.ThrowIfNull(state);
        ArgumentNullException.ThrowIfNull(runtimePackage);
        RequireSupportedContract(target, ability);
        if (!IsClientSelectable(target) && !IsAutomaticCollection(target))
        {
            throw Unsupported("Automatic references are resolved from the ability resolution context, not board enumeration.");
        }

        RequireController(state, abilityControllerPlayerId);
        var candidates = ImmutableArray.CreateBuilder<CanonicalTargetCandidate>();
        foreach (var player in state.Players)
        {
            var isController = string.Equals(
                player.PlayerId,
                abilityControllerPlayerId,
                StringComparison.Ordinal);
            if (string.Equals(target.PlayerReferenceId, "ability_controller", StringComparison.Ordinal)
                    ? !isController
                    : isController)
            {
                continue;
            }

            foreach (var row in new[] { DomainRow.Horizon, DomainRow.Zenith })
            {
                var rowId = row == DomainRow.Horizon ? "horizont" : "zenit";
                if (target.DomainRowId is not null
                    && !string.Equals(target.DomainRowId, rowId, StringComparison.Ordinal))
                {
                    continue;
                }

                var slots = player.Domain.GetSlots(row);
                for (var laneIndex = 0; laneIndex < DomainState.LaneCount; laneIndex += 1)
                {
                    var cardInstanceId = slots[laneIndex];
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
                        || card.DomainRow != row
                        || target.ActivityStateId is not null
                        && !string.Equals(card.ActivityState, target.ActivityStateId, StringComparison.Ordinal))
                    {
                        continue;
                    }

                    var candidate = new CanonicalTargetCandidate(
                        target.TargetId,
                        card.CardInstanceId,
                        card.CardId,
                        card.ControllerPlayerId,
                        card.Zone,
                        rowId,
                        laneIndex,
                        card.ActivityState);
                    if (CanonicalTargetFilterEvaluator.Matches(
                            ability,
                            target,
                            candidate,
                            state,
                            canonicalCards,
                            canonicalAbilities))
                    {
                        candidates.Add(candidate);
                    }
                }
            }
        }

        // Stable enumeration order only; it is not game-semantic priority.
        return candidates
            .OrderBy(candidate => state.Players.FindIndex(player => string.Equals(
                player.PlayerId,
                candidate.ControllerPlayerId,
                StringComparison.Ordinal)))
            .ThenBy(candidate => string.Equals(candidate.DomainRowId, "horizont", StringComparison.Ordinal) ? 0 : 1)
            .ThenBy(candidate => candidate.LaneIndex)
            .ThenBy(candidate => candidate.CardInstanceId, StringComparer.Ordinal)
            .ToImmutableArray();
    }

    internal static CanonicalResolvedTargetSet ResolveAutomaticCollection(
        CanonicalAbilityTargetDefinition target,
        CanonicalAbilityDefinition ability,
        string abilityControllerPlayerId,
        MatchState state,
        RuntimePackageCatalog runtimePackage,
        CanonicalCardCatalog? canonicalCards,
        CanonicalAbilityCatalog? canonicalAbilities,
        int snapshotSequence)
    {
        if (!IsAutomaticCollection(target))
        {
            throw Unsupported("Automatic collection resolution requires all_matching selection authority.");
        }

        var candidates = ResolveCandidates(
            target,
            ability,
            abilityControllerPlayerId,
            state,
            runtimePackage,
            canonicalCards,
            canonicalAbilities);
        if (candidates.Length < target.MinimumTargets || candidates.Length > target.MaximumTargets)
        {
            throw new CanonicalAbilityExecutionException(
                "CANONICAL_AUTOMATIC_TARGET_COUNT_INVALID",
                "Automatic target collection is outside canonical cardinality.");
        }

        return CardSet(target, AllMatchingSelectionMethodId, candidates, abilityControllerPlayerId, snapshotSequence);
    }

    internal static CanonicalResolvedTargetSet ResolveSourceCardReference(
        CanonicalAbilityTargetDefinition target,
        CanonicalAbilityResolutionContext context,
        MatchState state,
        RuntimePackageCatalog runtimePackage,
        int snapshotSequence)
    {
        RequireSupportedContract(target, context.Ability);
        if (!string.Equals(target.TargetPrimitiveId, "target_reference_ability_source_card", StringComparison.Ordinal))
        {
            throw Unsupported("Source-card resolution requires target_reference_ability_source_card authority.");
        }

        RequireController(state, context.ControllerPlayerId);
        if (!state.CardInstances.TryGetValue(context.SourceCardInstanceId, out var card)
            || !string.Equals(card.CardId, context.SourceCardId, StringComparison.Ordinal)
            || !string.Equals(card.CardId, context.Ability.CardId, StringComparison.Ordinal)
            || !string.Equals(card.ControllerPlayerId, context.ControllerPlayerId, StringComparison.Ordinal)
            || !runtimePackage.Cards.ContainsKey(card.CardId))
        {
            throw new CanonicalAbilityExecutionException(
                "CANONICAL_SOURCE_REFERENCE_INVALID",
                "The ability source CardInstance no longer matches its authoritative resolution context.");
        }

        var rowId = card.DomainRow switch
        {
            DomainRow.Horizon => "horizont",
            DomainRow.Zenith => "zenit",
            _ => null,
        };
        var candidate = new CanonicalTargetCandidate(
            target.TargetId,
            card.CardInstanceId,
            card.CardId,
            card.ControllerPlayerId,
            card.Zone,
            rowId,
            card.DomainLaneIndex,
            card.ActivityState);
        return CardSet(
            target,
            AutomaticReferenceSelectionMethodId,
            ImmutableArray.Create(candidate),
            context.ControllerPlayerId,
            snapshotSequence);
    }

    internal static CanonicalResolvedTargetSet ResolveControllerPlayerReference(
        CanonicalAbilityTargetDefinition target,
        CanonicalAbilityResolutionContext context,
        MatchState state,
        int snapshotSequence)
    {
        RequireSupportedContract(target, context.Ability);
        if (!string.Equals(
                target.TargetPrimitiveId,
                "target_reference_ability_controller_player",
                StringComparison.Ordinal))
        {
            throw Unsupported("Player resolution requires target_reference_ability_controller_player authority.");
        }

        RequireController(state, context.ControllerPlayerId);
        return new CanonicalResolvedTargetSet(
            target,
            AutomaticReferenceSelectionMethodId,
            new CanonicalResolvedPlayerTarget(context.ControllerPlayerId),
            context.ControllerPlayerId,
            snapshotSequence);
    }

    internal static CanonicalResolvedTargetSet ValidateSelection(
        CanonicalAbilityTargetDefinition target,
        CanonicalAbilityDefinition ability,
        ImmutableArray<string> selectedCardInstanceIds,
        string abilityControllerPlayerId,
        MatchState state,
        RuntimePackageCatalog runtimePackage,
        CanonicalCardCatalog? canonicalCards,
        CanonicalAbilityCatalog? canonicalAbilities,
        CanonicalResolutionOrigin origin,
        int snapshotSequence)
    {
        RequireSupportedContract(target, ability);
        if (!IsClientSelectable(target))
        {
            throw Invalid(origin, "Automatic target collections and references must not be submitted by the client.");
        }

        if (selectedCardInstanceIds.IsDefault)
        {
            throw Invalid(origin, "Canonical target selection is missing.");
        }

        if (selectedCardInstanceIds.Any(string.IsNullOrWhiteSpace))
        {
            throw new CanonicalAbilityExecutionException(
                Code(origin, "TARGET_UNKNOWN"),
                "Canonical target selection contains an empty card instance ID.");
        }

        if (selectedCardInstanceIds.Distinct(StringComparer.Ordinal).Count() != selectedCardInstanceIds.Length)
        {
            throw new CanonicalAbilityExecutionException(
                Code(origin, "TARGET_DUPLICATE"),
                "Canonical target selection contains a duplicate card instance ID.");
        }

        if (selectedCardInstanceIds.Length < target.MinimumTargets
            || selectedCardInstanceIds.Length > target.MaximumTargets)
        {
            throw new CanonicalAbilityExecutionException(
                Code(origin, "TARGET_COUNT_INVALID"),
                "Canonical target selection count is outside the declared minimum/maximum range.");
        }

        var candidates = ResolveCandidates(
            target,
            ability,
            abilityControllerPlayerId,
            state,
            runtimePackage,
            canonicalCards,
            canonicalAbilities);
        var candidatesById = candidates.ToImmutableDictionary(
            candidate => candidate.CardInstanceId,
            StringComparer.Ordinal);
        var selectedIds = selectedCardInstanceIds.ToImmutableHashSet(StringComparer.Ordinal);
        foreach (var cardInstanceId in selectedCardInstanceIds)
        {
            if (!state.CardInstances.ContainsKey(cardInstanceId))
            {
                throw new CanonicalAbilityExecutionException(
                    Code(origin, "TARGET_UNKNOWN"),
                    "Canonical target selection references an unknown card instance.");
            }

            if (!candidatesById.ContainsKey(cardInstanceId))
            {
                throw new CanonicalAbilityExecutionException(
                    Code(origin, "TARGET_ILLEGAL"),
                    "Selected card instance does not currently satisfy the canonical target contract.");
            }
        }

        return CardSet(
            target,
            ControllerChoiceSelectionMethodId,
            candidates.Where(candidate => selectedIds.Contains(candidate.CardInstanceId)).ToImmutableArray(),
            abilityControllerPlayerId,
            snapshotSequence);
    }

    private static CanonicalResolvedTargetSet CardSet(
        CanonicalAbilityTargetDefinition target,
        string mode,
        ImmutableArray<CanonicalTargetCandidate> cards,
        string controllerPlayerId,
        int snapshotSequence) => new(
            target,
            mode,
            new CanonicalResolvedCardTargets(cards),
            controllerPlayerId,
            snapshotSequence);

    private static void RequireController(MatchState state, string controllerPlayerId)
    {
        if (state.Players.All(player => !string.Equals(
                player.PlayerId,
                controllerPlayerId,
                StringComparison.Ordinal)))
        {
            throw new EngineStateException(
                "CANONICAL_TARGET_CONTROLLER_INVALID",
                "Canonical target resolution references an unknown ability controller.");
        }
    }

    private static void RequireSupportedContract(
        CanonicalAbilityTargetDefinition target,
        CanonicalAbilityDefinition ability)
    {
        var choice = IsClientSelectable(target)
                     && (string.Equals(target.TargetPrimitiveId, "target_choose_one_card", StringComparison.Ordinal)
                         && string.Equals(target.ReferenceTypeId, "ref_selected_card_exactly_one", StringComparison.Ordinal)
                         || string.Equals(target.TargetPrimitiveId, "target_choose_cards_zero_or_more", StringComparison.Ordinal)
                         && string.Equals(target.ReferenceTypeId, "ref_selected_cards_zero_or_more", StringComparison.Ordinal));
        var collection = IsAutomaticCollection(target)
                         && string.Equals(target.TargetPrimitiveId, "target_all_matching_cards", StringComparison.Ordinal)
                         && string.Equals(target.ReferenceTypeId, "ref_all_matching_cards_zero_or_more", StringComparison.Ordinal);
        var cardCollection = choice || collection;
        if (cardCollection)
        {
            if (!string.Equals(target.Status, ActiveStatus, StringComparison.Ordinal)
                || !string.Equals(target.GameObjectId, "card_instance", StringComparison.Ordinal)
                || !string.Equals(target.CardTypeId, "entity", StringComparison.Ordinal)
                || target.PlayerReferenceId is not ("ability_controller" or "opponent_of_ability_controller")
                || !string.Equals(target.ZoneId, "dominion", StringComparison.Ordinal)
                || target.DomainRowId is not (null or "horizont" or "zenit")
                || target.DomainLaneId is not null
                || target.ActivityStateId is not (null or "active")
                || target.MinimumTargets < 0
                || target.MaximumTargets < target.MinimumTargets
                || target.MaximumTargets > DomainState.LaneCount * 2
                || target.Optional != (choice && target.MinimumTargets == 0)
                || string.Equals(target.TargetPrimitiveId, "target_choose_one_card", StringComparison.Ordinal)
                && (target.MinimumTargets != 1 || target.MaximumTargets != 1))
            {
                throw Unsupported("Canonical target definition is outside the controlled Dominion Entity collection slice.");
            }

            CanonicalTargetFilterEvaluator.Validate(ability, target);
            return;
        }

        var sourceReference = string.Equals(
                                  target.TargetPrimitiveId,
                                  "target_reference_ability_source_card",
                                  StringComparison.Ordinal)
                              && string.Equals(target.ReferenceTypeId, "ref_ability_source_card", StringComparison.Ordinal)
                              && string.Equals(target.GameObjectId, "card_instance", StringComparison.Ordinal)
                              && target.CardTypeId is null
                              && target.PlayerReferenceId is null;
        var playerReference = string.Equals(
                                  target.TargetPrimitiveId,
                                  "target_reference_ability_controller_player",
                                  StringComparison.Ordinal)
                              && string.Equals(target.ReferenceTypeId, "ref_ability_controller_player", StringComparison.Ordinal)
                              && string.Equals(target.GameObjectId, "player_state", StringComparison.Ordinal)
                              && target.CardTypeId is null
                              && string.Equals(target.PlayerReferenceId, "ability_controller", StringComparison.Ordinal);
        if (!string.Equals(target.Status, ActiveStatus, StringComparison.Ordinal)
            || !string.Equals(target.SelectionMethodId, AutomaticReferenceSelectionMethodId, StringComparison.Ordinal)
            || !(sourceReference || playerReference)
            || target.ZoneId is not null
            || target.DomainRowId is not null
            || target.DomainLaneId is not null
            || target.ActivityStateId is not null
            || target.MinimumTargets != 1
            || target.MaximumTargets != 1
            || target.FilterConditionId is not null
            || target.Optional)
        {
            throw Unsupported("Canonical target definition is outside automatic source/player reference v1.");
        }
    }

    private static CanonicalAbilityExecutionException Unsupported(string message) => new(
        "CANONICAL_TARGET_CONTRACT_UNSUPPORTED",
        message);

    private static CanonicalAbilityExecutionException Invalid(
        CanonicalResolutionOrigin origin,
        string message) => new(Code(origin, "TARGET_SELECTION_INVALID"), message);

    private static string Code(CanonicalResolutionOrigin origin, string suffix) =>
        origin == CanonicalResolutionOrigin.TriggeredAbility
            ? $"RESOLVE_TRIGGER_{suffix}"
            : $"PLAY_CARD_{suffix}";
}
