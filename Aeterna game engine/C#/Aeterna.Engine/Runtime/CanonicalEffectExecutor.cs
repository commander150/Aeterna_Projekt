using System.Collections.Immutable;
using Aeterna.Engine.Contracts;
using Aeterna.Engine.State;

namespace Aeterna.Engine.Runtime;

internal sealed record CanonicalCardActivityMutation(
    string EffectId,
    int EffectSequence,
    string CardInstanceId,
    string CardId,
    string FromActivityState,
    string ToActivityState);

internal sealed record CanonicalEffectExecutionPlan(
    string AbilityId,
    ImmutableArray<CanonicalResolvedTargetSelection> TargetSelections,
    ImmutableArray<CanonicalCardActivityMutation> ActivityMutations);

internal sealed record CanonicalAbilityResolutionRecord(
    string PendingTriggerId,
    string AbilityId,
    string TriggerId,
    string SourceCardInstanceId,
    string ControllerPlayerId,
    string ResolutionOutcome,
    int AppliedEffectCount);

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
                || effect.ParentEffectId is not null
                || effect.BranchKey is not null
                || effect.ConditionId is not null
                || effect.Parameters.Length != 0
                || effect.Durations.Length != 0)
            {
                throw new CanonicalAbilityExecutionException(
                    "CANONICAL_EFFECT_GRAPH_UNSUPPORTED",
                    "Canonical exhaust-card effect graph is outside the first runtime slice.");
            }
        }
    }

    internal static CanonicalEffectExecutionPlan BuildPlan(
        CanonicalAbilityDefinition ability,
        ImmutableArray<CanonicalTargetSelectionPayload> selections,
        string abilityControllerPlayerId,
        MatchState state,
        RuntimePackageCatalog runtimePackage)
    {
        ValidateSupportedGraph(ability);
        if (selections.IsDefault)
        {
            throw new CanonicalAbilityExecutionException(
                "RESOLVE_TRIGGER_TARGET_SELECTION_INVALID",
                "Target selections are missing.");
        }

        if (selections.Any(selection => selection is null || string.IsNullOrWhiteSpace(selection.TargetId)))
        {
            throw new CanonicalAbilityExecutionException(
                "RESOLVE_TRIGGER_TARGET_SELECTION_INVALID",
                "Target selection contains an invalid target identity.");
        }

        if (selections.Select(selection => selection.TargetId).Distinct(StringComparer.Ordinal).Count() != selections.Length)
        {
            throw new CanonicalAbilityExecutionException(
                "RESOLVE_TRIGGER_TARGET_SELECTION_INVALID",
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
                        : "RESOLVE_TRIGGER_TARGET_ID_INVALID",
                    "Target selection references an unknown or unsupported target definition.");
            }
        }

        if (selections.Length != definitions.Length)
        {
            throw new CanonicalAbilityExecutionException(
                "RESOLVE_TRIGGER_TARGET_SELECTION_INVALID",
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
                abilityControllerPlayerId,
                state,
                runtimePackage);
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
                if (!string.Equals(
                        simulatedActivity[selectedCard.CardInstanceId],
                        "active",
                        StringComparison.Ordinal))
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

        return new CanonicalEffectExecutionPlan(ability.AbilityId, resolved, mutations.ToImmutable());
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
}
