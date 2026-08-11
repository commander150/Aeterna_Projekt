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

internal sealed record CanonicalDestroyEffectMutation(
    string EffectId,
    int EffectSequence,
    string CardInstanceId,
    string CardId,
    CanonicalDestructionMutation Destruction)
    : CanonicalEffectMutation(EffectId, EffectSequence, CardInstanceId, CardId);

internal sealed record CanonicalHealMutation(
    string EffectId,
    int EffectSequence,
    string CardInstanceId,
    string CardId,
    string DamageRemovalInstanceId,
    string SourceCardInstanceId,
    int RequestedAmount,
    int RemovedAmount,
    int DamageBefore,
    int DamageAfter,
    bool MiasmaRemoved)
    : CanonicalEffectMutation(EffectId, EffectSequence, CardInstanceId, CardId);

internal sealed record CanonicalMoveCardMutation(
    string EffectId,
    int EffectSequence,
    string CardInstanceId,
    string CardId,
    CanonicalZoneTransitionPlan ZoneTransition)
    : CanonicalEffectMutation(EffectId, EffectSequence, CardInstanceId, CardId);

internal sealed record CanonicalEffectExecutionPlan(
    CanonicalAbilityResolutionContext Context,
    ImmutableArray<CanonicalResolvedTargetSet> TargetSelections,
    ImmutableArray<CanonicalEffectMutation> Mutations)
{
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
    internal const string DestroyEntityEffectActionTypeId = "effect_destroy_entity";
    internal const string HealEntityEffectActionTypeId = "effect_heal_entity";
    internal const string MoveCardBetweenZonesEffectActionTypeId = "effect_move_card_between_zones";
    internal const string DirectDamageKindId = "damage_kind_direct";
    internal const string AppliedOutcome = "resolved_effect_applied";
    internal const string NoLegalTargetOutcome = "resolved_no_effect_no_legal_target";
    internal const string PlayedCardOriginId = "played_card";
    internal const string TriggeredAbilityOriginId = "triggered_ability";

    private const string ActiveStatus = "active";
    private const string DamageAmountContractFieldId = "parameter_field_deal_damage_amount";
    private const string DamageKindContractFieldId = "parameter_field_deal_damage_damage_kind";
    private const string HealAmountContractFieldId = "parameter_field_heal_entity_amount";
    private const string HealRemoveMiasmaContractFieldId = "parameter_field_heal_entity_remove_miasma";
    private const string MoveDestinationPlayerContractFieldId = "parameter_field_move_between_zones_destination_player";

    internal static bool IsSupportedGraph(CanonicalAbilityDefinition ability)
    {
        try
        {
            ValidateSupportedGraph(ability);
            return true;
        }
        catch (CanonicalAbilityExecutionException exception) when (
            exception.Code is "CANONICAL_TARGET_CONTRACT_UNSUPPORTED"
                or "CANONICAL_TARGET_FILTER_UNSUPPORTED"
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
            throw UnsupportedGraph("Canonical ability execution requires normalized structured_data authority.");
        }

        var targets = CanonicalTargetResolver.GetSupportedTargets(ability);
        var targetIds = targets.Select(target => target.TargetId).ToImmutableHashSet(StringComparer.Ordinal);
        var effects = ActiveEffects(ability);
        if (effects.Length == 0)
        {
            throw UnsupportedGraph("Canonical ability has no active effects.");
        }

        foreach (var effect in effects)
        {
            if (effect.EffectActionTypeId is not (
                    ExhaustCardEffectActionTypeId or
                    DealDamageEffectActionTypeId or
                    DestroyEntityEffectActionTypeId or
                    HealEntityEffectActionTypeId or
                    MoveCardBetweenZonesEffectActionTypeId))
            {
                throw new CanonicalAbilityExecutionException(
                    "CANONICAL_EFFECT_ACTION_UNSUPPORTED",
                    $"Unsupported canonical effect action type: {effect.EffectActionTypeId}");
            }

            if (effect.TargetId is null
                || !targetIds.Contains(effect.TargetId)
                || !string.Equals(effect.SourceReferenceTypeId, "ref_ability_source_card", StringComparison.Ordinal)
                || effect.ParentEffectId is not null
                || effect.BranchKey is not null
                || effect.ConditionId is not null
                || effect.ValueTypeId is not (null or "no_value")
                || effect.ValueNumber is not null
                || effect.ValueText is not null
                || effect.ValueRegistryValueId is not null
                || effect.ValueExpressionId is not null
                || effect.FieldId is not null
                || effect.DestinationPositionId is not null
                || effect.ModifierTypeId is not null
                || effect.RestrictionTypeId is not null
                || effect.Durations.Length != 0)
            {
                throw UnsupportedGraph("Canonical effect graph is outside the direct execution runtime slice.");
            }

            switch (effect.EffectActionTypeId)
            {
                case ExhaustCardEffectActionTypeId:
                case DestroyEntityEffectActionTypeId:
                    RequireNoZoneOrParameters(effect);
                    break;
                case DealDamageEffectActionTypeId:
                    RequireNoZone(effect);
                    ValidateDamageParameters(effect);
                    break;
                case HealEntityEffectActionTypeId:
                    RequireNoZone(effect);
                    ValidateHealParameters(effect);
                    break;
                case MoveCardBetweenZonesEffectActionTypeId:
                    ValidateMoveContract(effect);
                    break;
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
            || ability.ModuleKey is not null
            || ability.ParentAbilityId is not null
            || ability.Triggers.Length != 0)
        {
            throw new CanonicalAbilityExecutionException(
                "CANONICAL_PLAYED_CARD_GRAPH_UNSUPPORTED",
                "Played resolution card is outside the normalized full-resolution runtime slice.");
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
        ValidateSupportedGraph(context.Ability);
        var provided = context.TargetSelections;
        if (provided.IsDefault
            || provided.Any(selection => selection is null || string.IsNullOrWhiteSpace(selection.TargetId))
            || provided.Select(selection => selection.TargetId).Distinct(StringComparer.Ordinal).Count() != provided.Length)
        {
            throw InvalidSelection(context.Origin, "Target selection identity is missing, invalid, or duplicated.");
        }

        var definitions = CanonicalTargetResolver.GetSupportedTargets(context.Ability);
        var controllerChoiceIds = definitions
            .Where(target => string.Equals(
                target.SelectionMethodId,
                CanonicalTargetResolver.ControllerChoiceSelectionMethodId,
                StringComparison.Ordinal))
            .Select(target => target.TargetId)
            .ToImmutableHashSet(StringComparer.Ordinal);
        foreach (var selection in provided)
        {
            if (!controllerChoiceIds.Contains(selection.TargetId))
            {
                var belongs = context.Ability.Targets.Any(target => string.Equals(
                    target.TargetId,
                    selection.TargetId,
                    StringComparison.Ordinal));
                throw new CanonicalAbilityExecutionException(
                    belongs ? Code(context.Origin, "TARGET_SELECTION_INVALID") : Code(context.Origin, "TARGET_ID_INVALID"),
                    belongs
                        ? "Automatic target collection must not be supplied by the client."
                        : "Target selection references an unknown target definition.");
            }
        }

        if (provided.Length != controllerChoiceIds.Count)
        {
            throw InvalidSelection(context.Origin, "Target selection does not cover every controller-choice target.");
        }

        var resolved = definitions.Select(definition =>
            string.Equals(
                definition.SelectionMethodId,
                CanonicalTargetResolver.AllMatchingSelectionMethodId,
                StringComparison.Ordinal)
                ? CanonicalTargetResolver.ResolveAutomatic(
                    definition,
                    context.Ability,
                    context.ControllerPlayerId,
                    state,
                    runtimePackage,
                    canonicalCards,
                    definition.Sequence)
                : CanonicalTargetResolver.ValidateSelection(
                    definition,
                    context.Ability,
                    provided.Single(item => string.Equals(item.TargetId, definition.TargetId, StringComparison.Ordinal)).CardInstanceIds,
                    context.ControllerPlayerId,
                    state,
                    runtimePackage,
                    canonicalCards,
                    context.Origin,
                    definition.Sequence)).ToImmutableArray();
        var targetSets = resolved.ToImmutableDictionary(set => set.Definition.TargetId, StringComparer.Ordinal);

        var simulatedActivity = state.CardInstances.Values.ToDictionary(card => card.CardInstanceId, card => card.ActivityState, StringComparer.Ordinal);
        var simulatedDamage = state.CardInstances.Values.ToDictionary(card => card.CardInstanceId, card => card.DamageMarked, StringComparer.Ordinal);
        var simulatedZone = state.CardInstances.Values.ToDictionary(card => card.CardInstanceId, card => card.Zone, StringComparer.Ordinal);
        var simulatedVoidCounts = state.Players.ToDictionary(player => player.PlayerId, player => player.VoidCardInstanceIds.Count, StringComparer.Ordinal);
        var simulatedHandCounts = state.Players.ToDictionary(player => player.PlayerId, player => player.HandCardInstanceIds.Count, StringComparer.Ordinal);
        var mutations = ImmutableArray.CreateBuilder<CanonicalEffectMutation>();
        foreach (var effect in ActiveEffects(context.Ability))
        {
            var selectedCards = targetSets[effect.TargetId!].SelectedCards;
            for (var targetIndex = 0; targetIndex < selectedCards.Length; targetIndex += 1)
            {
                var selected = selectedCards[targetIndex];
                if (!string.Equals(simulatedZone[selected.CardInstanceId], "dominion", StringComparison.Ordinal))
                {
                    throw new CanonicalAbilityExecutionException(
                        "CANONICAL_EFFECT_TARGET_STATE_INVALID",
                        "Canonical effect target has left Dominion at its sequence step.");
                }

                switch (effect.EffectActionTypeId)
                {
                    case ExhaustCardEffectActionTypeId:
                        PlanExhaust(effect, selected, simulatedActivity, mutations);
                        break;
                    case DealDamageEffectActionTypeId:
                        PlanDamage(
                            context,
                            effect,
                            selected,
                            targetIndex,
                            state,
                            canonicalCards,
                            simulatedDamage,
                            simulatedActivity,
                            simulatedZone,
                            simulatedVoidCounts,
                            mutations);
                        break;
                    case DestroyEntityEffectActionTypeId:
                        PlanDestroy(
                            context,
                            effect,
                            selected,
                            targetIndex,
                            state,
                            simulatedDamage,
                            simulatedActivity,
                            simulatedZone,
                            simulatedVoidCounts,
                            mutations);
                        break;
                    case HealEntityEffectActionTypeId:
                        PlanHeal(context, effect, selected, targetIndex, simulatedDamage, mutations);
                        break;
                    case MoveCardBetweenZonesEffectActionTypeId:
                        PlanMove(
                            context,
                            effect,
                            selected,
                            targetIndex,
                            state,
                            simulatedDamage,
                            simulatedActivity,
                            simulatedZone,
                            simulatedHandCounts,
                            mutations);
                        break;
                }
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
                        CanonicalZoneTransition.Apply(state, damage.Destruction.ZoneTransition);
                    }

                    break;
                case CanonicalDestroyEffectMutation destroy:
                    CanonicalZoneTransition.Apply(state, destroy.Destruction.ZoneTransition);
                    break;
                case CanonicalHealMutation heal:
                    state.GetCardInstance(heal.CardInstanceId).DamageMarked = heal.DamageAfter;
                    break;
                case CanonicalMoveCardMutation move:
                    CanonicalZoneTransition.Apply(state, move.ZoneTransition);
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
        CanonicalTargetCandidate selected,
        IDictionary<string, string?> simulatedActivity,
        ImmutableArray<CanonicalEffectMutation>.Builder mutations)
    {
        var activity = simulatedActivity[selected.CardInstanceId];
        if (string.Equals(activity, "exhausted", StringComparison.Ordinal))
        {
            return;
        }

        if (!string.Equals(activity, "active", StringComparison.Ordinal))
        {
            throw InvalidTargetState("effect_exhaust_card requires an active target.");
        }

        mutations.Add(new CanonicalCardActivityMutation(
            effect.EffectId,
            effect.Sequence,
            selected.CardInstanceId,
            selected.CardId,
            "active",
            "exhausted"));
        simulatedActivity[selected.CardInstanceId] = "exhausted";
    }

    private static void PlanDamage(
        CanonicalAbilityResolutionContext context,
        CanonicalAbilityEffectDefinition effect,
        CanonicalTargetCandidate selected,
        int targetIndex,
        MatchState state,
        CanonicalCardCatalog? canonicalCards,
        IDictionary<string, int> simulatedDamage,
        IDictionary<string, string?> simulatedActivity,
        IDictionary<string, string> simulatedZone,
        IDictionary<string, int> simulatedVoidCounts,
        ImmutableArray<CanonicalEffectMutation>.Builder mutations)
    {
        if (canonicalCards is null)
        {
            throw new CanonicalAbilityExecutionException(
                "CANONICAL_CARD_STATS_REQUIRED",
                "effect_deal_damage requires canonical card-stat authority.");
        }

        var target = state.GetCardInstance(selected.CardInstanceId);
        var amount = ReadIntegerParameter(effect, DamageAmountContractFieldId);
        var before = simulatedDamage[selected.CardInstanceId];
        if (before > int.MaxValue - amount)
        {
            throw new CanonicalAbilityExecutionException(
                "CANONICAL_DAMAGE_AMOUNT_INVALID",
                "Direct damage accumulation exceeds the supported integer range.");
        }

        var after = before + amount;
        var maxHp = CanonicalVitals.GetEffectiveMaxHp(target, canonicalCards);
        var lethal = after >= maxHp;
        var damageId = $"damage_{context.ResolutionId}_{effect.Sequence:000}_{targetIndex + 1:000}";
        CanonicalDestructionMutation? destruction = null;
        if (lethal)
        {
            var destructionId = $"destruction_{damageId}";
            var transition = CanonicalZoneTransition.PlanDominionToVoid(
                target,
                simulatedVoidCounts[target.OwnerPlayerId],
                $"zone_transition_{damageId}",
                CanonicalZoneTransitionCauseKinds.DamageLethal,
                destructionId);
            destruction = new CanonicalDestructionMutation(
                destructionId,
                "destruction_cause_kind_lethal_hp_state",
                context.SourceCardInstanceId,
                damageId,
                transition);
            RecordDeparture(target, simulatedDamage, simulatedActivity, simulatedZone, simulatedVoidCounts, "void");
        }
        else
        {
            simulatedDamage[selected.CardInstanceId] = after;
        }

        mutations.Add(new CanonicalDamageMutation(
            effect.EffectId,
            effect.Sequence,
            selected.CardInstanceId,
            selected.CardId,
            damageId,
            context.SourceCardInstanceId,
            context.SourceCardId,
            DirectDamageKindId,
            amount,
            before,
            after,
            maxHp,
            lethal,
            destruction));
    }

    private static void PlanDestroy(
        CanonicalAbilityResolutionContext context,
        CanonicalAbilityEffectDefinition effect,
        CanonicalTargetCandidate selected,
        int targetIndex,
        MatchState state,
        IDictionary<string, int> simulatedDamage,
        IDictionary<string, string?> simulatedActivity,
        IDictionary<string, string> simulatedZone,
        IDictionary<string, int> simulatedVoidCounts,
        ImmutableArray<CanonicalEffectMutation>.Builder mutations)
    {
        var target = state.GetCardInstance(selected.CardInstanceId);
        var destructionId = $"destruction_{context.ResolutionId}_{effect.Sequence:000}_{targetIndex + 1:000}";
        var transition = CanonicalZoneTransition.PlanDominionToVoid(
            target,
            simulatedVoidCounts[target.OwnerPlayerId],
            $"zone_transition_{destructionId}",
            CanonicalZoneTransitionCauseKinds.DestroyEffect,
            destructionId);
        var destruction = new CanonicalDestructionMutation(
            destructionId,
            "destruction_cause_kind_explicit_destroy_effect",
            context.SourceCardInstanceId,
            effect.EffectId,
            transition);
        mutations.Add(new CanonicalDestroyEffectMutation(
            effect.EffectId,
            effect.Sequence,
            selected.CardInstanceId,
            selected.CardId,
            destruction));
        RecordDeparture(target, simulatedDamage, simulatedActivity, simulatedZone, simulatedVoidCounts, "void");
    }

    private static void PlanHeal(
        CanonicalAbilityResolutionContext context,
        CanonicalAbilityEffectDefinition effect,
        CanonicalTargetCandidate selected,
        int targetIndex,
        IDictionary<string, int> simulatedDamage,
        ImmutableArray<CanonicalEffectMutation>.Builder mutations)
    {
        var amount = ReadIntegerParameter(effect, HealAmountContractFieldId);
        var before = simulatedDamage[selected.CardInstanceId];
        var removed = Math.Min(before, amount);
        var after = before - removed;
        mutations.Add(new CanonicalHealMutation(
            effect.EffectId,
            effect.Sequence,
            selected.CardInstanceId,
            selected.CardId,
            $"damage_removal_{context.ResolutionId}_{effect.Sequence:000}_{targetIndex + 1:000}",
            context.SourceCardInstanceId,
            amount,
            removed,
            before,
            after,
            MiasmaRemoved: false));
        simulatedDamage[selected.CardInstanceId] = after;
    }

    private static void PlanMove(
        CanonicalAbilityResolutionContext context,
        CanonicalAbilityEffectDefinition effect,
        CanonicalTargetCandidate selected,
        int targetIndex,
        MatchState state,
        IDictionary<string, int> simulatedDamage,
        IDictionary<string, string?> simulatedActivity,
        IDictionary<string, string> simulatedZone,
        IDictionary<string, int> simulatedHandCounts,
        ImmutableArray<CanonicalEffectMutation>.Builder mutations)
    {
        var target = state.GetCardInstance(selected.CardInstanceId);
        var moveId = $"move_{context.ResolutionId}_{effect.Sequence:000}_{targetIndex + 1:000}";
        var transition = CanonicalZoneTransition.PlanDominionToHand(
            target,
            simulatedHandCounts[target.OwnerPlayerId],
            $"zone_transition_{moveId}",
            moveId);
        mutations.Add(new CanonicalMoveCardMutation(
            effect.EffectId,
            effect.Sequence,
            selected.CardInstanceId,
            selected.CardId,
            transition));
        RecordDeparture(target, simulatedDamage, simulatedActivity, simulatedZone, simulatedHandCounts, "hand");
    }

    private static void RecordDeparture(
        CardInstanceState target,
        IDictionary<string, int> simulatedDamage,
        IDictionary<string, string?> simulatedActivity,
        IDictionary<string, string> simulatedZone,
        IDictionary<string, int> destinationCounts,
        string destinationZone)
    {
        destinationCounts[target.OwnerPlayerId] += 1;
        simulatedZone[target.CardInstanceId] = destinationZone;
        simulatedActivity[target.CardInstanceId] = null;
        simulatedDamage[target.CardInstanceId] = 0;
    }

    private static ImmutableArray<CanonicalAbilityEffectDefinition> ActiveEffects(CanonicalAbilityDefinition ability) =>
        ability.Effects
            .Where(effect => string.Equals(effect.Status, ActiveStatus, StringComparison.Ordinal))
            .OrderBy(effect => effect.Sequence)
            .ThenBy(effect => effect.EffectId, StringComparer.Ordinal)
            .ToImmutableArray();

    private static void RequireNoZoneOrParameters(CanonicalAbilityEffectDefinition effect)
    {
        RequireNoZone(effect);
        if (effect.Parameters.Length != 0)
        {
            throw UnsupportedGraph($"{effect.EffectActionTypeId} cannot carry parameters in this runtime slice.");
        }
    }

    private static void RequireNoZone(CanonicalAbilityEffectDefinition effect)
    {
        if (effect.FromZoneId is not null || effect.ToZoneId is not null)
        {
            throw UnsupportedGraph($"{effect.EffectActionTypeId} cannot carry zone fields in this runtime slice.");
        }
    }

    private static void ValidateDamageParameters(CanonicalAbilityEffectDefinition effect)
    {
        RequireParameterShape(effect, 2);
        var amount = FindParameter(effect, DamageAmountContractFieldId);
        var kind = FindParameter(effect, DamageKindContractFieldId);
        if (amount.ValueInteger is not int value
            || value <= 0
            || HasAnyOtherValue(amount, integerAllowed: true)
            || !string.Equals(kind.ValueRegistryValueId, DirectDamageKindId, StringComparison.Ordinal)
            || HasAnyOtherValue(kind, registryAllowed: true))
        {
            throw UnsupportedGraph("Only positive literal integer direct damage is supported.");
        }
    }

    private static void ValidateHealParameters(CanonicalAbilityEffectDefinition effect)
    {
        RequireParameterShape(effect, 2);
        var amount = FindParameter(effect, HealAmountContractFieldId);
        var miasma = FindParameter(effect, HealRemoveMiasmaContractFieldId);
        if (amount.ValueInteger is not int value
            || value <= 0
            || HasAnyOtherValue(amount, integerAllowed: true)
            || miasma.ValueBoolean is not false
            || HasAnyOtherValue(miasma, booleanAllowed: true))
        {
            throw UnsupportedGraph("effect_heal_entity requires positive amount and remove_miasma=false.");
        }
    }

    private static void ValidateMoveContract(CanonicalAbilityEffectDefinition effect)
    {
        if (!string.Equals(effect.FromZoneId, "dominion", StringComparison.Ordinal)
            || !string.Equals(effect.ToZoneId, "hand", StringComparison.Ordinal))
        {
            throw UnsupportedGraph("Only explicit Dominion-to-Hand movement is supported.");
        }

        RequireParameterShape(effect, 1);
        var destination = FindParameter(effect, MoveDestinationPlayerContractFieldId);
        if (!string.Equals(
                destination.ValueRegistryValueId,
                "player_reference_subject_card_owner",
                StringComparison.Ordinal)
            || HasAnyOtherValue(destination, registryAllowed: true))
        {
            throw UnsupportedGraph("Dominion-to-Hand destination must be the subject card owner.");
        }
    }

    private static void RequireParameterShape(CanonicalAbilityEffectDefinition effect, int count)
    {
        if (effect.Parameters.Length != count
            || effect.Parameters.Any(parameter =>
                !string.Equals(parameter.Status, ActiveStatus, StringComparison.Ordinal)
                || parameter.ItemIndex != 1)
            || effect.Parameters.Select(parameter => parameter.ContractFieldId)
                .Distinct(StringComparer.Ordinal).Count() != count)
        {
            throw UnsupportedGraph($"{effect.EffectActionTypeId} parameter shape is invalid.");
        }
    }

    private static CanonicalAbilityEffectParameterDefinition FindParameter(
        CanonicalAbilityEffectDefinition effect,
        string contractFieldId) => effect.Parameters.SingleOrDefault(parameter => string.Equals(
        parameter.ContractFieldId,
        contractFieldId,
        StringComparison.Ordinal)) ?? throw UnsupportedGraph(
        $"{effect.EffectActionTypeId} required parameter is missing: {contractFieldId}");

    private static bool HasAnyOtherValue(
        CanonicalAbilityEffectParameterDefinition parameter,
        bool booleanAllowed = false,
        bool integerAllowed = false,
        bool registryAllowed = false) =>
        (!booleanAllowed && parameter.ValueBoolean is not null)
        || (!integerAllowed && parameter.ValueInteger is not null)
        || parameter.ValueText is not null
        || (!registryAllowed && parameter.ValueRegistryValueId is not null)
        || parameter.ValueReferenceId is not null
        || parameter.ValueExpressionId is not null;

    private static int ReadIntegerParameter(CanonicalAbilityEffectDefinition effect, string fieldId) =>
        FindParameter(effect, fieldId).ValueInteger!.Value;

    private static CanonicalAbilityExecutionException UnsupportedGraph(string message) => new(
        "CANONICAL_EFFECT_GRAPH_UNSUPPORTED",
        message);

    private static CanonicalAbilityExecutionException InvalidTargetState(string message) => new(
        "CANONICAL_EFFECT_TARGET_STATE_INVALID",
        message);

    private static CanonicalAbilityExecutionException InvalidSelection(
        CanonicalResolutionOrigin origin,
        string message) => new(Code(origin, "TARGET_SELECTION_INVALID"), message);

    private static string Code(CanonicalResolutionOrigin origin, string suffix) =>
        origin == CanonicalResolutionOrigin.TriggeredAbility
            ? $"RESOLVE_TRIGGER_{suffix}"
            : $"PLAY_CARD_{suffix}";
}
