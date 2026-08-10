using System.Collections.Immutable;
using Aeterna.Engine.Contracts;
using Aeterna.Engine.State;

namespace Aeterna.Engine.Runtime;

internal enum CanonicalResolutionOrigin
{
    TriggeredAbility,
    PlayedCard,
}

internal sealed record CanonicalAbilityResolutionContext(
    string ResolutionId,
    CanonicalResolutionOrigin Origin,
    string? SourceActionId,
    string SourceActionType,
    CanonicalAbilityDefinition Ability,
    string SourceCardInstanceId,
    string SourceCardId,
    string ControllerPlayerId,
    ImmutableArray<CanonicalTargetSelectionPayload> TargetSelections,
    string? PendingTriggerId,
    string? TriggerId);

internal sealed record CanonicalCardActivityMutation(
    string EffectId,
    int EffectSequence,
    string CardInstanceId,
    string CardId,
    string FromActivityState,
    string ToActivityState);

internal sealed record CanonicalEffectExecutionPlan(
    CanonicalAbilityResolutionContext Context,
    ImmutableArray<CanonicalResolvedTargetSelection> TargetSelections,
    ImmutableArray<CanonicalCardActivityMutation> ActivityMutations);

internal sealed record CanonicalAbilityResolutionRecord(
    string ResolutionId,
    string ResolutionOrigin,
    string AbilityId,
    string SourceCardInstanceId,
    string SourceCardId,
    string ControllerPlayerId,
    string ResolutionOutcome,
    int AppliedEffectCount,
    string? SourceActionId,
    string? PendingTriggerId,
    string? TriggerId);

internal sealed class CanonicalAbilityExecutionException : Exception
{
    internal CanonicalAbilityExecutionException(string code, string message)
        : base(message)
    {
        Code = code;
    }

    internal string Code { get; }
}

internal static class CanonicalEffectExecutor
{
    internal const string ExhaustCardEffectActionTypeId = "effect_exhaust_card";
    internal const string AppliedOutcome = "resolved_effect_applied";
    internal const string NoLegalTargetOutcome = "resolved_no_effect_no_legal_target";
    internal const string PlayedCardOriginId = "played_card";
    internal const string TriggeredAbilityOriginId = "triggered_ability";

    private const string ActiveStatus = "active";

    internal static bool IsSupportedGraph(CanonicalAbilityDefinition ability)
    {
        try
        {
            ValidateSupportedGraph(ability);
            return true;
        }
        catch (CanonicalAbilityExecutionException exception) when (
            exception.Code is "CANONICAL_TARGET_CONTRACT_UNSUPPORTED"
                or "CANONICAL_EFFECT_ACTION_UNSUPPORTED"
                or "CANONICAL_EFFECT_GRAPH_UNSUPPORTED")
        {
            return false;
        }
    }

    internal static void ValidateSupportedGraph(CanonicalAbilityDefinition ability)
    {
        ArgumentNullException.ThrowIfNull(ability);
        if (!ability.IsStructuredGraphAuthority)
        {
            throw new CanonicalAbilityExecutionException(
                "CANONICAL_EFFECT_GRAPH_UNSUPPORTED",
                "Canonical ability execution currently requires structured_data authority.");
        }

        var targets = CanonicalTargetResolver.GetSupportedTargets(ability);
        var supportedTargetIds = targets.Select(target => target.TargetId).ToImmutableHashSet(StringComparer.Ordinal);
        var effects = ability.Effects
            .Where(effect => string.Equals(effect.Status, ActiveStatus, StringComparison.Ordinal))
            .ToImmutableArray();
        if (effects.Length == 0)
        {
            throw new CanonicalAbilityExecutionException(
                "CANONICAL_EFFECT_GRAPH_UNSUPPORTED",
                "Canonical triggered ability has no active effects.");
        }

        foreach (var effect in effects)
        {
            if (!string.Equals(effect.EffectActionTypeId, ExhaustCardEffectActionTypeId, StringComparison.Ordinal))
            {
                throw new CanonicalAbilityExecutionException(
                    "CANONICAL_EFFECT_ACTION_UNSUPPORTED",
                    $"Unsupported canonical effect action type: {effect.EffectActionTypeId}");
            }

            if (effect.TargetId is null
                || !supportedTargetIds.Contains(effect.TargetId)
                || !string.Equals(effect.SourceReferenceTypeId, "ref_ability_source_card", StringComparison.Ordinal)
                || effect.ParentEffectId is not null
                || effect.BranchKey is not null
                || effect.ConditionId is not null
                || effect.ValueTypeId is not null
                || effect.ValueNumber is not null
                || effect.ValueText is not null
                || effect.ValueRegistryValueId is not null
                || effect.ValueExpressionId is not null
                || effect.FieldId is not null
                || effect.FromZoneId is not null
                || effect.ToZoneId is not null
                || effect.DestinationPositionId is not null
                || effect.ModifierTypeId is not null
                || effect.RestrictionTypeId is not null
                || effect.Parameters.Length != 0
                || effect.Durations.Length != 0)
            {
                throw new CanonicalAbilityExecutionException(
                    "CANONICAL_EFFECT_GRAPH_UNSUPPORTED",
                    "Canonical exhaust-card effect graph is outside the first runtime slice.");
            }
        }
    }

    internal static void ValidateSupportedPlayedCardGraph(CanonicalAbilityDefinition ability)
    {
        ArgumentNullException.ThrowIfNull(ability);
        if (!string.Equals(ability.Status, ActiveStatus, StringComparison.Ordinal)
            || !string.Equals(ability.AbilityKindId, "resolution", StringComparison.Ordinal)
            || !string.Equals(ability.ResolutionRequirementId, "full_resolution_required", StringComparison.Ordinal)
            || !string.Equals(ability.ActiveZoneId, "hand", StringComparison.Ordinal)
            || !ability.IsStructuredGraphAuthority
            || ability.AbilityTemplateId is not null
            || ability.Template is not null
            || ability.ModuleKey is not null
            || ability.ParentAbilityId is not null
            || ability.Triggers.Length != 0
            || ability.Conditions.Length != 0
            || ability.Expressions.Length != 0
            || ability.TemplateArguments.Length != 0)
        {
            throw new CanonicalAbilityExecutionException(
                "CANONICAL_PLAYED_CARD_GRAPH_UNSUPPORTED",
                "Played resolution card ability is outside the first structured full-resolution runtime slice.");
        }

        ValidateSupportedGraph(ability);
    }

    internal static CanonicalEffectExecutionPlan BuildPlan(
        CanonicalAbilityResolutionContext context,
        MatchState state,
        RuntimePackageCatalog runtimePackage)
    {
        ArgumentNullException.ThrowIfNull(context);
        var ability = context.Ability;
        var selections = context.TargetSelections;
        ValidateSupportedGraph(ability);
        if (selections.IsDefault)
        {
            throw new CanonicalAbilityExecutionException(
                Code(context.Origin, "TARGET_SELECTION_INVALID"),
                "Target selections are missing.");
        }

        if (selections.Any(selection => selection is null || string.IsNullOrWhiteSpace(selection.TargetId)))
        {
            throw new CanonicalAbilityExecutionException(
                Code(context.Origin, "TARGET_SELECTION_INVALID"),
                "Target selection contains an invalid target identity.");
        }

        if (selections.Select(selection => selection.TargetId).Distinct(StringComparer.Ordinal).Count() != selections.Length)
        {
            throw new CanonicalAbilityExecutionException(
                Code(context.Origin, "TARGET_SELECTION_INVALID"),
                "Target selection contains a duplicate target_id entry.");
        }

        var definitions = CanonicalTargetResolver.GetSupportedTargets(ability);
        var definitionsById = definitions.ToImmutableDictionary(target => target.TargetId, StringComparer.Ordinal);
        foreach (var selection in selections)
        {
            if (!definitionsById.ContainsKey(selection.TargetId))
            {
                var belongsToAbility = ability.Targets.Any(target => string.Equals(
                    target.TargetId,
                    selection.TargetId,
                    StringComparison.Ordinal));
                throw new CanonicalAbilityExecutionException(
                    belongsToAbility
                        ? "CANONICAL_TARGET_CONTRACT_UNSUPPORTED"
                        : Code(context.Origin, "TARGET_ID_INVALID"),
                    "Target selection references an unknown or unsupported target definition.");
            }
        }

        if (selections.Length != definitions.Length)
        {
            throw new CanonicalAbilityExecutionException(
                Code(context.Origin, "TARGET_SELECTION_INVALID"),
                "Target selection does not cover every active canonical target definition.");
        }

        var resolved = definitions.Select(definition =>
        {
            var selection = selections.Single(item => string.Equals(
                item.TargetId,
                definition.TargetId,
                StringComparison.Ordinal));
            return CanonicalTargetResolver.ValidateSelection(
                definition,
                selection.CardInstanceIds,
                context.ControllerPlayerId,
                state,
                runtimePackage,
                context.Origin);
        }).ToImmutableArray();
        var selectedByTargetId = resolved.ToImmutableDictionary(
            selection => selection.Definition.TargetId,
            StringComparer.Ordinal);

        var simulatedActivity = state.CardInstances.Values.ToDictionary(
            card => card.CardInstanceId,
            card => card.ActivityState,
            StringComparer.Ordinal);
        var mutations = ImmutableArray.CreateBuilder<CanonicalCardActivityMutation>();
        foreach (var effect in ability.Effects.Where(effect => string.Equals(
                     effect.Status,
                     ActiveStatus,
                     StringComparison.Ordinal)))
        {
            foreach (var selectedCard in selectedByTargetId[effect.TargetId!].SelectedCards)
            {
                var activity = simulatedActivity[selectedCard.CardInstanceId];
                if (string.Equals(activity, "exhausted", StringComparison.Ordinal))
                {
                    // Canonical effect_exhaust_card is idempotent for an already
                    // exhausted target and emits no activity mutation.
                    continue;
                }

                if (!string.Equals(activity, "active", StringComparison.Ordinal))
                {
                    throw new CanonicalAbilityExecutionException(
                        "CANONICAL_EFFECT_TARGET_STATE_INVALID",
                        "effect_exhaust_card requires a target that is active at its canonical sequence step.");
                }

                mutations.Add(new CanonicalCardActivityMutation(
                    effect.EffectId,
                    effect.Sequence,
                    selectedCard.CardInstanceId,
                    selectedCard.CardId,
                    "active",
                    "exhausted"));
                simulatedActivity[selectedCard.CardInstanceId] = "exhausted";
            }
        }

        return new CanonicalEffectExecutionPlan(context, resolved, mutations.ToImmutable());
    }

    internal static void Apply(MatchState state, CanonicalEffectExecutionPlan plan)
    {
        ArgumentNullException.ThrowIfNull(state);
        ArgumentNullException.ThrowIfNull(plan);
        foreach (var mutation in plan.ActivityMutations)
        {
            state.GetCardInstance(mutation.CardInstanceId).ActivityState = mutation.ToActivityState;
        }
    }

    internal static string OriginId(CanonicalResolutionOrigin origin) => origin switch
    {
        CanonicalResolutionOrigin.TriggeredAbility => TriggeredAbilityOriginId,
        CanonicalResolutionOrigin.PlayedCard => PlayedCardOriginId,
        _ => throw new ArgumentOutOfRangeException(nameof(origin)),
    };

    private static string Code(CanonicalResolutionOrigin origin, string suffix) =>
        origin == CanonicalResolutionOrigin.TriggeredAbility
            ? $"RESOLVE_TRIGGER_{suffix}"
            : $"PLAY_CARD_{suffix}";
}
