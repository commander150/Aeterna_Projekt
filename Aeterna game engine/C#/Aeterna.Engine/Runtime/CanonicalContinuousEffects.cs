using System.Collections.Immutable;
using Aeterna.Engine.State;

namespace Aeterna.Engine.Runtime;

internal abstract record CanonicalContinuousEffectExpiration(
    int CreatedSequence,
    string InstanceId);

internal sealed record CanonicalModifierExpiration(
    ModifierInstanceState Instance,
    int ResolvedValueBefore,
    int ResolvedValueAfter)
    : CanonicalContinuousEffectExpiration(Instance.CreatedSequence, Instance.ModifierInstanceId);

internal sealed record CanonicalKeywordGrantExpiration(
    KeywordGrantInstanceState Instance,
    bool EffectiveKeywordPresentBefore,
    bool EffectiveKeywordPresentAfter)
    : CanonicalContinuousEffectExpiration(Instance.CreatedSequence, Instance.KeywordGrantInstanceId);

internal sealed record CanonicalExpiryLethalMutation(
    string TargetCardInstanceId,
    string TargetCardId,
    int DamageMarked,
    int EffectiveMaxHpAfterExpiry,
    ModifierInstanceState CauseModifier,
    string ModifierRemovalInstanceId,
    CanonicalDestructionMutation Destruction);

internal sealed record CanonicalEndTurnContinuousEffectPlan(
    string TurnInstanceId,
    string PhaseInstanceId,
    ImmutableArray<CanonicalContinuousEffectExpiration> Expirations,
    ImmutableArray<CanonicalExpiryLethalMutation> LethalMutations)
{
    internal static CanonicalEndTurnContinuousEffectPlan Empty(MatchState state) => new(
        CanonicalContinuousEffects.TurnInstanceId(state),
        CanonicalContinuousEffects.PhaseInstanceId(state),
        ImmutableArray<CanonicalContinuousEffectExpiration>.Empty,
        ImmutableArray<CanonicalExpiryLethalMutation>.Empty);
}

internal static class CanonicalContinuousEffects
{
    internal const string ApplyModifierEffectActionTypeId = "effect_apply_modifier";
    internal const string GrantKeywordEffectActionTypeId = "effect_grant_keyword";
    internal const string AttackModifierTypeId = "modifier_entity_attack_additive";
    internal const string MaxHpModifierTypeId = "modifier_entity_max_hp_additive";
    internal const string AttackFieldId = "entity_attack";
    internal const string MaxHpFieldId = "entity_max_hp";
    internal const string UntilEndOfCurrentTurnDurationPolicyId = "duration_until_end_of_current_turn";
    internal const string WardRegistryValueId = "keyword_ward";
    internal const string CleaveRegistryValueId = "keyword_cleave";
    internal const string WardKeywordId = "ward";
    internal const string CleaveKeywordId = "cleave";
    internal const string DurationExpiredRemovalReasonId = "duration_expired";

    private const string ActiveStatus = "active";

    internal static string ResolveModifierField(CanonicalAbilityEffectDefinition effect)
    {
        ArgumentNullException.ThrowIfNull(effect);
        var fieldId = effect.ModifierTypeId switch
        {
            AttackModifierTypeId => AttackFieldId,
            MaxHpModifierTypeId => MaxHpFieldId,
            _ => throw Unsupported($"Unsupported canonical modifier type: {effect.ModifierTypeId ?? "<null>"}"),
        };
        if (!string.Equals(effect.EffectActionTypeId, ApplyModifierEffectActionTypeId, StringComparison.Ordinal)
            || !string.Equals(effect.ValueTypeId, "number", StringComparison.Ordinal)
            || effect.ValueNumber is not int value
            || value <= 0
            || effect.ValueText is not null
            || effect.ValueRegistryValueId is not null
            || effect.ValueExpressionId is not null
            || effect.FieldId is not null
            || effect.FromZoneId is not null
            || effect.ToZoneId is not null
            || effect.DestinationPositionId is not null
            || effect.RestrictionTypeId is not null
            || effect.Parameters.Length != 0)
        {
            throw Unsupported("effect_apply_modifier is outside positive additive stat modifier v1.");
        }

        _ = RequireDuration(effect);
        return fieldId;
    }

    internal static string ResolveGrantedKeywordId(CanonicalAbilityEffectDefinition effect)
    {
        ArgumentNullException.ThrowIfNull(effect);
        var keywordId = effect.ValueRegistryValueId switch
        {
            WardRegistryValueId => WardKeywordId,
            CleaveRegistryValueId => CleaveKeywordId,
            _ => throw Unsupported($"Unsupported canonical keyword registry value: {effect.ValueRegistryValueId ?? "<null>"}"),
        };
        if (!string.Equals(effect.EffectActionTypeId, GrantKeywordEffectActionTypeId, StringComparison.Ordinal)
            || !string.Equals(effect.ValueTypeId, "registry_value", StringComparison.Ordinal)
            || effect.ValueNumber is not null
            || effect.ValueText is not null
            || effect.ValueExpressionId is not null
            || effect.FieldId is not null
            || effect.FromZoneId is not null
            || effect.ToZoneId is not null
            || effect.DestinationPositionId is not null
            || effect.ModifierTypeId is not null
            || effect.RestrictionTypeId is not null
            || effect.Parameters.Length != 0)
        {
            throw Unsupported("effect_grant_keyword is outside temporary keyword grant v1.");
        }

        _ = RequireDuration(effect);
        return keywordId;
    }

    internal static string ResolveKeywordRegistryValue(string registryValueId) => registryValueId switch
    {
        WardRegistryValueId => WardKeywordId,
        CleaveRegistryValueId => CleaveKeywordId,
        _ => throw Unsupported($"Unsupported canonical keyword registry value: {registryValueId}"),
    };

    internal static CanonicalAbilityDurationDefinition RequireDuration(
        CanonicalAbilityEffectDefinition effect)
    {
        if (effect.Durations.Length != 1)
        {
            throw Unsupported("Temporary modifier and keyword grant effects require exactly one duration.");
        }

        var duration = effect.Durations[0];
        if (!string.Equals(duration.Status, ActiveStatus, StringComparison.Ordinal)
            || !string.Equals(duration.EffectId, effect.EffectId, StringComparison.Ordinal)
            || !string.Equals(
                duration.DurationPolicyId,
                UntilEndOfCurrentTurnDurationPolicyId,
                StringComparison.Ordinal)
            || duration.StartEventTypeId is not null
            || duration.BoundaryPlayerReferenceId is not null
            || duration.BoundaryPhaseId is not null
            || duration.ExpirationEventTypeId is not null
            || duration.DependencyReferenceTypeId is not null
            || duration.ConditionId is not null
            || duration.MaximumApplications is not null)
        {
            throw Unsupported("Only duration_until_end_of_current_turn without overrides is supported.");
        }

        return duration;
    }

    internal static ModifierInstanceState CreateModifierInstance(
        CanonicalAbilityResolutionContext context,
        CanonicalAbilityEffectDefinition effect,
        CanonicalTargetCandidate target,
        int targetIndex,
        MatchState state,
        int createdSequence)
    {
        var fieldId = ResolveModifierField(effect);
        var duration = RequireDuration(effect);
        var instanceId = $"modifier_{context.ResolutionId}_{effect.Sequence:000}_{targetIndex + 1:000}";
        return new ModifierInstanceState(
            instanceId,
            context.Ability.AbilityId,
            effect.EffectId,
            context.ResolutionId,
            context.SourceCardInstanceId,
            context.ControllerPlayerId,
            target.CardInstanceId,
            state.GetCardInstance(target.CardInstanceId).ZoneSequence,
            effect.ModifierTypeId!,
            fieldId,
            effect.ValueNumber!.Value,
            duration.DurationId,
            duration.DurationPolicyId,
            $"duration_{instanceId}",
            TurnInstanceId(state),
            PhaseInstanceId(state),
            state.TurnNumber,
            state.ActivePlayerId,
            checked(state.StateVersion + 1),
            createdSequence);
    }

    internal static KeywordGrantInstanceState CreateKeywordGrantInstance(
        CanonicalAbilityResolutionContext context,
        CanonicalAbilityEffectDefinition effect,
        CanonicalTargetCandidate target,
        int targetIndex,
        MatchState state,
        int createdSequence)
    {
        var keywordId = ResolveGrantedKeywordId(effect);
        var duration = RequireDuration(effect);
        var instanceId = $"keyword_grant_{context.ResolutionId}_{effect.Sequence:000}_{targetIndex + 1:000}";
        return new KeywordGrantInstanceState(
            instanceId,
            context.Ability.AbilityId,
            effect.EffectId,
            context.ResolutionId,
            context.SourceCardInstanceId,
            context.ControllerPlayerId,
            target.CardInstanceId,
            state.GetCardInstance(target.CardInstanceId).ZoneSequence,
            keywordId,
            duration.DurationId,
            duration.DurationPolicyId,
            $"duration_{instanceId}",
            TurnInstanceId(state),
            PhaseInstanceId(state),
            state.TurnNumber,
            state.ActivePlayerId,
            checked(state.StateVersion + 1),
            createdSequence);
    }

    internal static int ModifierTotal(
        MatchState state,
        CardInstanceState card,
        string fieldId,
        IReadOnlySet<string>? excludedModifierIds = null)
    {
        var total = state.ModifierInstances.Values
            .Where(instance => string.Equals(instance.TargetCardInstanceId, card.CardInstanceId, StringComparison.Ordinal)
                               && instance.TargetZoneSequence == card.ZoneSequence
                               && string.Equals(card.Zone, "dominion", StringComparison.Ordinal)
                               && string.Equals(instance.AffectedFieldId, fieldId, StringComparison.Ordinal)
                               && (excludedModifierIds is null || !excludedModifierIds.Contains(instance.ModifierInstanceId)))
            .Sum(instance => (long)instance.IntegerValue);
        if (total > int.MaxValue)
        {
            throw new EngineStateException("Active canonical modifier total exceeds the supported integer range.");
        }

        return (int)total;
    }

    internal static ImmutableArray<string> GetEffectiveKeywords(
        MatchState state,
        CardInstanceState card,
        CanonicalAbilityCatalog abilities,
        IReadOnlySet<string>? excludedGrantIds = null)
    {
        ArgumentNullException.ThrowIfNull(state);
        ArgumentNullException.ThrowIfNull(card);
        ArgumentNullException.ThrowIfNull(abilities);
        if (!string.Equals(card.Zone, "dominion", StringComparison.Ordinal))
        {
            return ImmutableArray<string>.Empty;
        }

        var result = new HashSet<string>(StringComparer.Ordinal);
        if (abilities.KeywordsByCardId.TryGetValue(card.CardId, out var intrinsic))
        {
            foreach (var keyword in intrinsic.Where(keyword => string.Equals(
                         keyword.Status,
                         ActiveStatus,
                         StringComparison.Ordinal)))
            {
                result.Add(keyword.KeywordId);
            }
        }

        foreach (var grant in state.KeywordGrantInstances.Values)
        {
            if (string.Equals(grant.TargetCardInstanceId, card.CardInstanceId, StringComparison.Ordinal)
                && grant.TargetZoneSequence == card.ZoneSequence
                && (excludedGrantIds is null || !excludedGrantIds.Contains(grant.KeywordGrantInstanceId)))
            {
                result.Add(grant.KeywordId);
            }
        }

        return result.OrderBy(value => value, StringComparer.Ordinal).ToImmutableArray();
    }

    internal static bool HasEffectiveKeyword(
        MatchState state,
        CardInstanceState card,
        CanonicalAbilityCatalog abilities,
        string keywordId,
        IReadOnlySet<string>? excludedGrantIds = null) => GetEffectiveKeywords(
            state,
            card,
            abilities,
            excludedGrantIds).Contains(keywordId, StringComparer.Ordinal);

    internal static CanonicalEndTurnContinuousEffectPlan BuildEndTurnPlan(
        MatchState state,
        CanonicalCardCatalog? cards,
        CanonicalAbilityCatalog? abilities)
    {
        ArgumentNullException.ThrowIfNull(state);
        var expiringModifiers = state.ModifierInstances.Values
            .Where(instance => ExpiresAtCurrentTurnEnd(instance, state))
            .ToImmutableArray();
        var expiringGrants = state.KeywordGrantInstances.Values
            .Where(instance => ExpiresAtCurrentTurnEnd(instance, state))
            .ToImmutableArray();
        if (expiringModifiers.IsEmpty && expiringGrants.IsEmpty)
        {
            return CanonicalEndTurnContinuousEffectPlan.Empty(state);
        }

        if (cards is null || abilities is null)
        {
            throw new EngineStateException(
                "Canonical modifier expiry requires canonical card and ability authority.");
        }

        var excludedModifiers = new HashSet<string>(StringComparer.Ordinal);
        var excludedGrants = new HashSet<string>(StringComparer.Ordinal);
        var ordered = expiringModifiers
            .Select<ModifierInstanceState, (int CreatedSequence, string InstanceId, object Instance)>(instance =>
                (instance.CreatedSequence, instance.ModifierInstanceId, instance))
            .Concat(expiringGrants.Select(instance =>
                (CreatedSequence: instance.CreatedSequence,
                    InstanceId: instance.KeywordGrantInstanceId,
                    Instance: (object)instance)))
            .OrderBy(item => item.CreatedSequence)
            .ThenBy(item => item.InstanceId, StringComparer.Ordinal)
            .ToImmutableArray();
        var expirations = ImmutableArray.CreateBuilder<CanonicalContinuousEffectExpiration>();
        foreach (var item in ordered)
        {
            switch (item.Instance)
            {
                case ModifierInstanceState modifier:
                {
                    var card = state.GetCardInstance(modifier.TargetCardInstanceId);
                    var before = GetEffectiveField(state, card, cards, modifier.AffectedFieldId, excludedModifiers);
                    excludedModifiers.Add(modifier.ModifierInstanceId);
                    var after = GetEffectiveField(state, card, cards, modifier.AffectedFieldId, excludedModifiers);
                    expirations.Add(new CanonicalModifierExpiration(modifier, before, after));
                    break;
                }
                case KeywordGrantInstanceState grant:
                {
                    var card = state.GetCardInstance(grant.TargetCardInstanceId);
                    var before = HasEffectiveKeyword(state, card, abilities, grant.KeywordId, excludedGrants);
                    excludedGrants.Add(grant.KeywordGrantInstanceId);
                    var after = HasEffectiveKeyword(state, card, abilities, grant.KeywordId, excludedGrants);
                    expirations.Add(new CanonicalKeywordGrantExpiration(grant, before, after));
                    break;
                }
            }
        }

        var simulatedVoidCounts = state.Players.ToDictionary(
            player => player.PlayerId,
            player => player.VoidCardInstanceIds.Count,
            StringComparer.Ordinal);
        var lethal = ImmutableArray.CreateBuilder<CanonicalExpiryLethalMutation>();
        foreach (var cardInstanceId in expiringModifiers
                     .Where(instance => string.Equals(instance.AffectedFieldId, MaxHpFieldId, StringComparison.Ordinal))
                     .Select(instance => instance.TargetCardInstanceId)
                     .Distinct(StringComparer.Ordinal)
                     .OrderBy(value => value, StringComparer.Ordinal))
        {
            var target = state.GetCardInstance(cardInstanceId);
            if (!string.Equals(target.Zone, "dominion", StringComparison.Ordinal))
            {
                continue;
            }

            var effectiveMaxHp = CanonicalVitals.GetEffectiveMaxHp(
                state,
                target,
                cards,
                excludedModifiers);
            if (target.DamageMarked < effectiveMaxHp)
            {
                continue;
            }

            var cause = expiringModifiers
                .Where(instance => string.Equals(instance.TargetCardInstanceId, cardInstanceId, StringComparison.Ordinal)
                                   && string.Equals(instance.AffectedFieldId, MaxHpFieldId, StringComparison.Ordinal))
                .OrderBy(instance => instance.CreatedSequence)
                .ThenBy(instance => instance.ModifierInstanceId, StringComparer.Ordinal)
                .Last();
            var removalId = $"modifier_removal_{cause.ModifierInstanceId}";
            var destructionId = $"destruction_{removalId}";
            var transition = CanonicalZoneTransition.PlanDominionToVoid(
                target,
                simulatedVoidCounts[target.OwnerPlayerId],
                $"zone_transition_{destructionId}",
                CanonicalZoneTransitionCauseKinds.ModifierExpiryLethal,
                destructionId);
            simulatedVoidCounts[target.OwnerPlayerId] += 1;
            lethal.Add(new CanonicalExpiryLethalMutation(
                target.CardInstanceId,
                target.CardId,
                target.DamageMarked,
                effectiveMaxHp,
                cause,
                removalId,
                new CanonicalDestructionMutation(
                    destructionId,
                    "destruction_cause_kind_rule_state_consequence",
                    cause.SourceCardInstanceId,
                    removalId,
                    transition)));
        }

        return new CanonicalEndTurnContinuousEffectPlan(
            TurnInstanceId(state),
            PhaseInstanceId(state),
            expirations.ToImmutable(),
            lethal.ToImmutable());
    }

    internal static void ApplyEndTurnPlan(MatchState state, CanonicalEndTurnContinuousEffectPlan plan)
    {
        ArgumentNullException.ThrowIfNull(state);
        ArgumentNullException.ThrowIfNull(plan);
        foreach (var expiration in plan.Expirations)
        {
            var matches = expiration switch
            {
                CanonicalModifierExpiration modifier => state.ModifierInstances.TryGetValue(
                    modifier.Instance.ModifierInstanceId,
                    out var actual) && Equals(actual, modifier.Instance),
                CanonicalKeywordGrantExpiration grant => state.KeywordGrantInstances.TryGetValue(
                    grant.Instance.KeywordGrantInstanceId,
                    out var actual) && Equals(actual, grant.Instance),
                _ => false,
            };
            if (!matches)
            {
                throw new EngineStateException("Canonical continuous-effect expiry plan is stale.");
            }
        }

        foreach (var expiration in plan.Expirations)
        {
            switch (expiration)
            {
                case CanonicalModifierExpiration modifier:
                    state.ModifierInstances.Remove(modifier.Instance.ModifierInstanceId);
                    break;
                case CanonicalKeywordGrantExpiration grant:
                    state.KeywordGrantInstances.Remove(grant.Instance.KeywordGrantInstanceId);
                    break;
            }
        }

        foreach (var lethal in plan.LethalMutations)
        {
            CanonicalZoneTransition.Apply(state, lethal.Destruction.ZoneTransition);
        }
    }

    internal static void ValidateState(
        MatchState state,
        CanonicalCardCatalog? cards,
        CanonicalAbilityCatalog? abilities)
    {
        var createdSequences = new HashSet<int>();
        var instanceIds = new HashSet<string>(StringComparer.Ordinal);
        foreach (var (registryKey, instance) in state.ModifierInstances)
        {
            if (!string.Equals(registryKey, instance.ModifierInstanceId, StringComparison.Ordinal)
                || !instanceIds.Add(instance.ModifierInstanceId))
            {
                throw new EngineStateException("Modifier instance registry identity is invalid.");
            }

            ValidateCommon(
                state,
                instance.ModifierInstanceId,
                instance.SourceAbilityId,
                instance.SourceEffectId,
                instance.SourceResolutionId,
                instance.SourceCardInstanceId,
                instance.ControllerPlayerId,
                instance.TargetCardInstanceId,
                instance.TargetZoneSequence,
                instance.DurationId,
                instance.DurationPolicyId,
                instance.DurationInstanceId,
                instance.TurnInstanceId,
                instance.PhaseInstanceId,
                instance.CreatedTurnNumber,
                instance.CreatedActivePlayerId,
                instance.CreatedStateVersion,
                instance.CreatedSequence,
                createdSequences);
            if (instance.IntegerValue <= 0
                || (instance.ModifierTypeId switch
                {
                    AttackModifierTypeId => !string.Equals(instance.AffectedFieldId, AttackFieldId, StringComparison.Ordinal),
                    MaxHpModifierTypeId => !string.Equals(instance.AffectedFieldId, MaxHpFieldId, StringComparison.Ordinal),
                    _ => true,
                }))
            {
                throw new EngineStateException("Modifier instance type, field, or value is invalid.");
            }

            ValidateSourceEffect(state, abilities, instance.SourceAbilityId, instance.SourceEffectId, instance.SourceCardInstanceId, effect =>
                string.Equals(effect.EffectActionTypeId, ApplyModifierEffectActionTypeId, StringComparison.Ordinal)
                && string.Equals(effect.ModifierTypeId, instance.ModifierTypeId, StringComparison.Ordinal)
                && effect.ValueNumber == instance.IntegerValue
                && string.Equals(RequireDuration(effect).DurationId, instance.DurationId, StringComparison.Ordinal));
            ValidateEntityTarget(state, cards, instance.TargetCardInstanceId);
        }

        foreach (var (registryKey, instance) in state.KeywordGrantInstances)
        {
            if (!string.Equals(registryKey, instance.KeywordGrantInstanceId, StringComparison.Ordinal)
                || !instanceIds.Add(instance.KeywordGrantInstanceId))
            {
                throw new EngineStateException("Keyword grant instance registry identity is invalid.");
            }

            ValidateCommon(
                state,
                instance.KeywordGrantInstanceId,
                instance.SourceAbilityId,
                instance.SourceEffectId,
                instance.SourceResolutionId,
                instance.SourceCardInstanceId,
                instance.ControllerPlayerId,
                instance.TargetCardInstanceId,
                instance.TargetZoneSequence,
                instance.DurationId,
                instance.DurationPolicyId,
                instance.DurationInstanceId,
                instance.TurnInstanceId,
                instance.PhaseInstanceId,
                instance.CreatedTurnNumber,
                instance.CreatedActivePlayerId,
                instance.CreatedStateVersion,
                instance.CreatedSequence,
                createdSequences);
            if (instance.KeywordId is not (WardKeywordId or CleaveKeywordId))
            {
                throw new EngineStateException("Keyword grant instance keyword is unsupported.");
            }

            ValidateSourceEffect(state, abilities, instance.SourceAbilityId, instance.SourceEffectId, instance.SourceCardInstanceId, effect =>
                string.Equals(effect.EffectActionTypeId, GrantKeywordEffectActionTypeId, StringComparison.Ordinal)
                && string.Equals(ResolveGrantedKeywordId(effect), instance.KeywordId, StringComparison.Ordinal)
                && string.Equals(RequireDuration(effect).DurationId, instance.DurationId, StringComparison.Ordinal));
            ValidateEntityTarget(state, cards, instance.TargetCardInstanceId);
        }

        if (state.NextContinuousEffectSequence <= 0
            || createdSequences.Any(sequence => sequence >= state.NextContinuousEffectSequence))
        {
            throw new EngineStateException("Continuous-effect creation sequence is invalid.");
        }
    }

    internal static string TurnInstanceId(MatchState state) => TurnInstanceId(
        state.TurnNumber,
        state.ActivePlayerId);

    internal static string PhaseInstanceId(MatchState state) =>
        $"phase_{TurnInstanceId(state)}_{state.Phase}";

    private static string TurnInstanceId(int turnNumber, string activePlayerId) =>
        $"turn_{turnNumber:000000}_{activePlayerId}";

    private static bool ExpiresAtCurrentTurnEnd(ModifierInstanceState instance, MatchState state) =>
        string.Equals(instance.DurationPolicyId, UntilEndOfCurrentTurnDurationPolicyId, StringComparison.Ordinal)
        && instance.CreatedTurnNumber == state.TurnNumber
        && string.Equals(instance.CreatedActivePlayerId, state.ActivePlayerId, StringComparison.Ordinal)
        && string.Equals(instance.TurnInstanceId, TurnInstanceId(state), StringComparison.Ordinal);

    private static bool ExpiresAtCurrentTurnEnd(KeywordGrantInstanceState instance, MatchState state) =>
        string.Equals(instance.DurationPolicyId, UntilEndOfCurrentTurnDurationPolicyId, StringComparison.Ordinal)
        && instance.CreatedTurnNumber == state.TurnNumber
        && string.Equals(instance.CreatedActivePlayerId, state.ActivePlayerId, StringComparison.Ordinal)
        && string.Equals(instance.TurnInstanceId, TurnInstanceId(state), StringComparison.Ordinal);

    private static int GetEffectiveField(
        MatchState state,
        CardInstanceState card,
        CanonicalCardCatalog cards,
        string fieldId,
        IReadOnlySet<string> excludedModifierIds) => fieldId switch
        {
            AttackFieldId => CanonicalVitals.GetEffectiveAtk(state, card, cards, excludedModifierIds),
            MaxHpFieldId => CanonicalVitals.GetEffectiveMaxHp(state, card, cards, excludedModifierIds),
            _ => throw new EngineStateException("Modifier instance affected field is unsupported."),
        };

    private static void ValidateCommon(
        MatchState state,
        string instanceId,
        string sourceAbilityId,
        string sourceEffectId,
        string sourceResolutionId,
        string sourceCardInstanceId,
        string controllerPlayerId,
        string targetCardInstanceId,
        int targetZoneSequence,
        string durationId,
        string durationPolicyId,
        string durationInstanceId,
        string turnInstanceId,
        string phaseInstanceId,
        int createdTurnNumber,
        string createdActivePlayerId,
        int createdStateVersion,
        int createdSequence,
        ISet<int> createdSequences)
    {
        if (string.IsNullOrWhiteSpace(instanceId)
            || string.IsNullOrWhiteSpace(sourceAbilityId)
            || string.IsNullOrWhiteSpace(sourceEffectId)
            || string.IsNullOrWhiteSpace(sourceResolutionId)
            || string.IsNullOrWhiteSpace(sourceCardInstanceId)
            || string.IsNullOrWhiteSpace(controllerPlayerId)
            || string.IsNullOrWhiteSpace(targetCardInstanceId)
            || targetZoneSequence <= 0
            || string.IsNullOrWhiteSpace(durationId)
            || !string.Equals(durationPolicyId, UntilEndOfCurrentTurnDurationPolicyId, StringComparison.Ordinal)
            || string.IsNullOrWhiteSpace(durationInstanceId)
            || !string.Equals(turnInstanceId, TurnInstanceId(createdTurnNumber, createdActivePlayerId), StringComparison.Ordinal)
            || string.IsNullOrWhiteSpace(phaseInstanceId)
            || createdTurnNumber <= 0
            || createdStateVersion <= 0
            || createdStateVersion > state.StateVersion
            || createdSequence <= 0
            || !createdSequences.Add(createdSequence)
            || state.Players.All(player => !string.Equals(player.PlayerId, controllerPlayerId, StringComparison.Ordinal))
            || state.Players.All(player => !string.Equals(player.PlayerId, createdActivePlayerId, StringComparison.Ordinal))
            || !state.CardInstances.TryGetValue(sourceCardInstanceId, out _)
            || !state.CardInstances.TryGetValue(targetCardInstanceId, out var target)
            || target.ZoneSequence < targetZoneSequence)
        {
            throw new EngineStateException("Continuous-effect instance identity or duration context is invalid.");
        }
    }

    private static void ValidateSourceEffect(
        MatchState state,
        CanonicalAbilityCatalog? abilities,
        string abilityId,
        string effectId,
        string sourceCardInstanceId,
        Func<CanonicalAbilityEffectDefinition, bool> predicate)
    {
        if (abilities is null)
        {
            return;
        }

        if (!abilities.AbilitiesById.TryGetValue(abilityId, out var ability)
            || !abilities.EffectsById.TryGetValue(effectId, out var effect)
            || !string.Equals(effect.AbilityId, abilityId, StringComparison.Ordinal)
            || !string.Equals(state.GetCardInstance(sourceCardInstanceId).CardId, ability.CardId, StringComparison.Ordinal)
            || !predicate(effect))
        {
            throw new EngineStateException("Continuous-effect source ability or effect identity is invalid.");
        }
    }

    private static void ValidateEntityTarget(
        MatchState state,
        CanonicalCardCatalog? cards,
        string targetCardInstanceId)
    {
        if (cards is null)
        {
            return;
        }

        var target = state.GetCardInstance(targetCardInstanceId);
        if (!cards.DefinitionsById.TryGetValue(target.CardId, out var definition)
            || !string.Equals(definition.Status, ActiveStatus, StringComparison.Ordinal)
            || !string.Equals(definition.CardType, "entity", StringComparison.Ordinal))
        {
            throw new EngineStateException("Continuous-effect target requires an active canonical Entity definition.");
        }
    }

    private static CanonicalAbilityExecutionException Unsupported(string message) => new(
        "CANONICAL_EFFECT_GRAPH_UNSUPPORTED",
        message);
}
