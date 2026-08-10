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

internal abstract record CanonicalEffectMutation(
    string EffectId,
    int EffectSequence,
    string CardInstanceId,
    string CardId);

internal sealed record CanonicalCardActivityMutation(
    string EffectId,
    int EffectSequence,
    string CardInstanceId,
    string CardId,
    string FromActivityState,
    string ToActivityState)
    : CanonicalEffectMutation(EffectId, EffectSequence, CardInstanceId, CardId);

internal sealed record CanonicalDestructionMutation(
    string DestructionInstanceId,
    string DestructionCauseKindId,
    string SourceCardInstanceId,
    string CauseInstanceId,
    CanonicalZoneTransitionPlan ZoneTransition);

internal sealed record CanonicalDamageMutation(
    string EffectId,
    int EffectSequence,
    string CardInstanceId,
    string CardId,
    string DamageInstanceId,
    string SourceCardInstanceId,
    string SourceCardId,
    string DamageKindId,
    int Amount,
    int DamageBefore,
    int DamageAfter,
    int EffectiveMaxHp,
    bool Lethal,
    CanonicalDestructionMutation? Destruction)
    : CanonicalEffectMutation(EffectId, EffectSequence, CardInstanceId, CardId);

internal sealed record CanonicalEffectExecutionPlan(
    CanonicalAbilityResolutionContext Context,
    ImmutableArray<CanonicalResolvedTargetSelection> TargetSelections,
    ImmutableArray<CanonicalEffectMutation> Mutations)
{
    internal ImmutableArray<CanonicalCardActivityMutation> ActivityMutations =>
        Mutations.OfType<CanonicalCardActivityMutation>().ToImmutableArray();

    internal ImmutableArray<CanonicalDamageMutation> DamageMutations =>
        Mutations.OfType<CanonicalDamageMutation>().ToImmutableArray();

    internal int AppliedMutationCount => Mutations.Length;
}

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
    internal const string DealDamageEffectActionTypeId = "effect_deal_damage";
    internal const string DirectDamageKindId = "damage_kind_direct";
    internal const string AppliedOutcome = "resolved_effect_applied";
    internal const string NoLegalTargetOutcome = "resolved_no_effect_no_legal_target";
    internal const string PlayedCardOriginId = "played_card";
    internal const string TriggeredAbilityOriginId = "triggered_ability";

    private const string ActiveStatus = "active";
    private const string DamageAmountContractFieldId = "parameter_field_deal_damage_amount";
    private const string DamageKindContractFieldId = "parameter_field_deal_damage_damage_kind";

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
                "Canonical ability execution requires structured_data authority.");
        }

        var targets = CanonicalTargetResolver.GetSupportedTargets(ability);
        var supportedTargetIds = targets.Select(target => target.TargetId).ToImmutableHashSet(StringComparer.Ordinal);
        var effects = ability.Effects
            .Where(effect => string.Equals(effect.Status, ActiveStatus, StringComparison.Ordinal))
            .OrderBy(effect => effect.Sequence)
            .ToImmutableArray();
        if (effects.Length == 0)
        {
            throw UnsupportedGraph("Canonical ability has no active effects.");
        }

        foreach (var effect in effects)
        {
            if (effect.EffectActionTypeId is not (ExhaustCardEffectActionTypeId or DealDamageEffectActionTypeId))
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
                || effect.Durations.Length != 0)
            {
                throw UnsupportedGraph("Canonical effect graph is outside the direct execution runtime slice.");
            }

            if (string.Equals(effect.EffectActionTypeId, ExhaustCardEffectActionTypeId, StringComparison.Ordinal))
            {
                if (effect.Parameters.Length != 0)
                {
                    throw UnsupportedGraph("effect_exhaust_card cannot carry parameters in this runtime slice.");
                }

                continue;
            }

            ValidateDamageParameters(effect);
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
                "Played resolution card ability is outside the structured full-resolution runtime slice.");
        }

        ValidateSupportedGraph(ability);
    }

    internal static CanonicalEffectExecutionPlan BuildPlan(
        CanonicalAbilityResolutionContext context,
        MatchState state,
        RuntimePackageCatalog runtimePackage,
        CanonicalCardCatalog? canonicalCards)
    {
        ArgumentNullException.ThrowIfNull(context);
        var ability = context.Ability;
        var selections = context.TargetSelections;
        ValidateSupportedGraph(ability);
        if (selections.IsDefault)
        {
            throw InvalidSelection(context.Origin, "Target selections are missing.");
        }

        if (selections.Any(selection => selection is null || string.IsNullOrWhiteSpace(selection.TargetId))
            || selections.Select(selection => selection.TargetId).Distinct(StringComparer.Ordinal).Count() != selections.Length)
        {
            throw InvalidSelection(context.Origin, "Target selection identity is invalid or duplicated.");
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
            throw InvalidSelection(context.Origin, "Target selection does not cover every active target definition.");
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
        var simulatedDamage = state.CardInstances.Values.ToDictionary(
            card => card.CardInstanceId,
            card => card.DamageMarked,
            StringComparer.Ordinal);
        var simulatedZone = state.CardInstances.Values.ToDictionary(
            card => card.CardInstanceId,
            card => card.Zone,
            StringComparer.Ordinal);
        var simulatedVoidCounts = state.Players.ToDictionary(
            player => player.PlayerId,
            player => player.VoidCardInstanceIds.Count,
            StringComparer.Ordinal);
        var mutations = ImmutableArray.CreateBuilder<CanonicalEffectMutation>();
        foreach (var effect in ability.Effects
                     .Where(effect => string.Equals(effect.Status, ActiveStatus, StringComparison.Ordinal))
                     .OrderBy(effect => effect.Sequence))
        {
            var selectedCards = selectedByTargetId[effect.TargetId!].SelectedCards;
            for (var targetIndex = 0; targetIndex < selectedCards.Length; targetIndex += 1)
            {
                var selectedCard = selectedCards[targetIndex];
                if (!string.Equals(simulatedZone[selectedCard.CardInstanceId], "dominion", StringComparison.Ordinal))
                {
                    throw new CanonicalAbilityExecutionException(
                        "CANONICAL_EFFECT_TARGET_STATE_INVALID",
                        "Canonical effect target has left Dominion at its sequence step.");
                }

                if (string.Equals(effect.EffectActionTypeId, ExhaustCardEffectActionTypeId, StringComparison.Ordinal))
                {
                    PlanExhaust(effect, selectedCard, simulatedActivity, mutations);
                    continue;
                }

                if (canonicalCards is null)
                {
                    throw new CanonicalAbilityExecutionException(
                        "CANONICAL_CARD_STATS_REQUIRED",
                        "effect_deal_damage requires canonical card-stat authority.");
                }

                var targetState = state.GetCardInstance(selectedCard.CardInstanceId);
                var amount = ReadDamageAmount(effect);
                var damageBefore = simulatedDamage[selectedCard.CardInstanceId];
                if (damageBefore > int.MaxValue - amount)
                {
                    throw new CanonicalAbilityExecutionException(
                        "CANONICAL_DAMAGE_AMOUNT_INVALID",
                        "Direct damage accumulation exceeds the supported integer range.");
                }

                var damageAfter = damageBefore + amount;
                var effectiveMaxHp = CanonicalVitals.GetEffectiveMaxHp(targetState, canonicalCards);
                var lethal = damageAfter >= effectiveMaxHp;
                var damageInstanceId =
                    $"damage_{context.ResolutionId}_{effect.Sequence:000}_{targetIndex + 1:000}";
                CanonicalDestructionMutation? destruction = null;
                if (lethal)
                {
                    var destructionInstanceId = $"destruction_{damageInstanceId}";
                    var transition = CanonicalZoneTransition.PlanDominionToVoid(
                        targetState,
                        simulatedVoidCounts[targetState.OwnerPlayerId],
                        $"zone_transition_{damageInstanceId}",
                        destructionInstanceId);
                    destruction = new CanonicalDestructionMutation(
                        destructionInstanceId,
                        "destruction_cause_kind_lethal_hp_state",
                        context.SourceCardInstanceId,
                        damageInstanceId,
                        transition);
                    simulatedVoidCounts[targetState.OwnerPlayerId] += 1;
                    simulatedZone[selectedCard.CardInstanceId] = "void";
                    simulatedActivity[selectedCard.CardInstanceId] = null;
                    simulatedDamage[selectedCard.CardInstanceId] = 0;
                }
                else
                {
                    simulatedDamage[selectedCard.CardInstanceId] = damageAfter;
                }

                mutations.Add(new CanonicalDamageMutation(
                    effect.EffectId,
                    effect.Sequence,
                    selectedCard.CardInstanceId,
                    selectedCard.CardId,
                    damageInstanceId,
                    context.SourceCardInstanceId,
                    context.SourceCardId,
                    DirectDamageKindId,
                    amount,
                    damageBefore,
                    damageAfter,
                    effectiveMaxHp,
                    lethal,
                    destruction));
            }
        }

        return new CanonicalEffectExecutionPlan(context, resolved, mutations.ToImmutable());
    }

    internal static void Apply(MatchState state, CanonicalEffectExecutionPlan plan)
    {
        ArgumentNullException.ThrowIfNull(state);
        ArgumentNullException.ThrowIfNull(plan);
        foreach (var mutation in plan.Mutations)
        {
            switch (mutation)
            {
                case CanonicalCardActivityMutation activity:
                    state.GetCardInstance(activity.CardInstanceId).ActivityState = activity.ToActivityState;
                    break;
                case CanonicalDamageMutation damage:
                    state.GetCardInstance(damage.CardInstanceId).DamageMarked = damage.DamageAfter;
                    if (damage.Destruction is not null)
                    {
                        CanonicalZoneTransition.ApplyDominionToVoid(state, damage.Destruction.ZoneTransition);
                    }

                    break;
                default:
                    throw new EngineStateException("Unknown canonical effect mutation type.");
            }
        }
    }

    internal static string OriginId(CanonicalResolutionOrigin origin) => origin switch
    {
        CanonicalResolutionOrigin.TriggeredAbility => TriggeredAbilityOriginId,
        CanonicalResolutionOrigin.PlayedCard => PlayedCardOriginId,
        _ => throw new ArgumentOutOfRangeException(nameof(origin)),
    };

    private static void PlanExhaust(
        CanonicalAbilityEffectDefinition effect,
        CanonicalTargetCandidate selectedCard,
        IDictionary<string, string?> simulatedActivity,
        ImmutableArray<CanonicalEffectMutation>.Builder mutations)
    {
        var activity = simulatedActivity[selectedCard.CardInstanceId];
        if (string.Equals(activity, "exhausted", StringComparison.Ordinal))
        {
            return;
        }

        if (!string.Equals(activity, "active", StringComparison.Ordinal))
        {
            throw new CanonicalAbilityExecutionException(
                "CANONICAL_EFFECT_TARGET_STATE_INVALID",
                "effect_exhaust_card requires an active target at its sequence step.");
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

    private static void ValidateDamageParameters(CanonicalAbilityEffectDefinition effect)
    {
        if (effect.Parameters.Length != 2
            || effect.Parameters.Any(parameter =>
                !string.Equals(parameter.Status, ActiveStatus, StringComparison.Ordinal)
                || parameter.ItemIndex != 1
                || parameter.ValueBoolean is not null
                || parameter.ValueText is not null
                || parameter.ValueReferenceId is not null
                || parameter.ValueExpressionId is not null)
            || effect.Parameters.Select(parameter => parameter.ContractFieldId)
                .Distinct(StringComparer.Ordinal).Count() != 2)
        {
            throw UnsupportedGraph("effect_deal_damage parameter shape is invalid.");
        }

        var amount = effect.Parameters.SingleOrDefault(parameter => string.Equals(
            parameter.ContractFieldId,
            DamageAmountContractFieldId,
            StringComparison.Ordinal));
        var kind = effect.Parameters.SingleOrDefault(parameter => string.Equals(
            parameter.ContractFieldId,
            DamageKindContractFieldId,
            StringComparison.Ordinal));
        if (amount is null
            || amount.ValueInteger is not int value
            || value <= 0
            || amount.ValueRegistryValueId is not null
            || kind is null
            || kind.ValueInteger is not null
            || !string.Equals(kind.ValueRegistryValueId, DirectDamageKindId, StringComparison.Ordinal))
        {
            throw UnsupportedGraph("Only positive literal integer direct damage is supported.");
        }
    }

    private static int ReadDamageAmount(CanonicalAbilityEffectDefinition effect) =>
        effect.Parameters.Single(parameter => string.Equals(
            parameter.ContractFieldId,
            DamageAmountContractFieldId,
            StringComparison.Ordinal)).ValueInteger!.Value;

    private static CanonicalAbilityExecutionException UnsupportedGraph(string message) => new(
        "CANONICAL_EFFECT_GRAPH_UNSUPPORTED",
        message);

    private static CanonicalAbilityExecutionException InvalidSelection(
        CanonicalResolutionOrigin origin,
        string message) => new(Code(origin, "TARGET_SELECTION_INVALID"), message);

    private static string Code(CanonicalResolutionOrigin origin, string suffix) =>
        origin == CanonicalResolutionOrigin.TriggeredAbility
            ? $"RESOLVE_TRIGGER_{suffix}"
            : $"PLAY_CARD_{suffix}";
}
