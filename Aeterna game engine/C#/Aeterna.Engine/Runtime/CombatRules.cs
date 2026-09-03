using System.Collections.Immutable;
using Aeterna.Engine.Rules;
using Aeterna.Engine.State;

namespace Aeterna.Engine.Runtime;

internal static class CombatRuleIds
{
    internal const string CardInstanceObjectKind = "card_instance";
    internal const string EntityTargetKind = "entity";
    internal const string SealSlotTargetKind = "seal_slot";
    internal const string AeternalTargetKind = "aeternal";
    internal const string AttackReactionStage = "attack_reaction";
    internal const string AttackCheckpointStage = "attack_checkpoint";
    internal const string InterventionChoiceStage = "intervention_choice";
    internal const string DefenseReactionStage = "defense_reaction";
    internal const string DefenseCheckpointStage = "defense_checkpoint";
    internal const string SealOutcomeCheckpointStage = "seal_outcome_checkpoint";
    internal const string PostSurgeCheckpointStage = "post_surge_checkpoint";
    internal const string AeternalOutcomeCheckpointStage = "aeternal_outcome_checkpoint";
    internal const string AfterAttackReactionResumePoint = "after_attack_reaction";
    internal const string AfterDefenseReactionResumePoint = "after_defense_reaction";
    internal const string CombatContinuationEntryKind = "combat_continuation";
    internal const string AttackReactionProfile = "combat_attack_commit";
    internal const string DefenseReactionProfile = "combat_defense_commit";
    internal const string AttackContinuityUnchecked = "unchecked";
    internal const string AttackContinuityContinuous = "continuous";
    internal const string AttackContinuityAttackerLost = "attacker_continuity_lost";
    internal const string AttackContinuityTargetLost = "original_target_continuity_lost";
    internal const string AttackContinuitySealUnavailable = "original_seal_unavailable";
    internal const string AttackContinuityAeternalPathClosed = "aeternal_attack_path_closed";
    internal const string DefenseDecisionPending = "pending";
    internal const string DefenseDecisionChoiceOpen = "choice_open";
    internal const string DefenseDecisionUnavailable = "unavailable";
    internal const string DefenseDecisionDeclined = "declined";
    internal const string DefenseDecisionCommitted = "committed";
    internal const string EntityCombatResolvedOutcome = "entity_combat_resolved";
    internal const string NoHitOutcome = "no_hit";
    internal const string FutureOutcomePending = "future_outcome_pending";
    internal const string SealBreakCommittedOutcome = "seal_break_committed";
    internal const string AttackerMissingNoHitReason = "attacker_missing";
    internal const string TargetMissingNoHitReason = "target_missing";
    internal const string DefenderMissingNoHitReason = "defender_missing";
    internal const string ContactInvalidNoHitReason = "contact_invalid";
    internal const string SealUnavailableNoHitReason = "seal_unavailable";
    internal const string SealLaneInvalidNoHitReason = "seal_lane_invalid";
    internal const string CombatCauseKind = "combat";
    internal const string CombatDamageKind = "damage_kind_combat";
    internal const string SpeedKeyword = "speed";
    internal const string WardKeyword = "ward";
    internal const string AerialKeyword = "aerial";
}

internal sealed record CombatAttackDeclarationOption(
    CardInstanceState Attacker,
    GameObjectRefState AttackerRef,
    string DefendingPlayerId,
    CombatTargetState Target,
    int OriginalAttackLaneIndex,
    DomainRow? OriginalTargetRowAtAttackCommit,
    bool OriginalTargetHadWardAtAttackCommit);

internal sealed record CombatInterventionOption(
    CardInstanceState Defender,
    GameObjectRefState DefenderRef,
    int DefenderLaneIndex);

internal static class CombatRules
{
    internal static ImmutableArray<CombatAttackDeclarationOption> ResolveAttackDeclarations(
        MatchState state,
        PlayerState player,
        RuntimePackageCatalog? runtimePackage,
        CanonicalAbilityCatalog? canonicalAbilities)
    {
        ArgumentNullException.ThrowIfNull(state);
        ArgumentNullException.ThrowIfNull(player);
        if (runtimePackage is null
            || !string.Equals(state.Phase, CanonicalPhaseIds.Incursion, StringComparison.Ordinal)
            || !string.Equals(state.ActivePlayerId, player.PlayerId, StringComparison.Ordinal)
            || state.Result.Completed
            || state.Setup is { Completed: false }
            || IsStartingPlayerFirstTurnAttackBan(state, player.PlayerId))
        {
            return ImmutableArray<CombatAttackDeclarationOption>.Empty;
        }

        var defendingPlayerId = state.GetNextPlayerId(player.PlayerId);
        var defendingPlayer = state.GetPlayer(defendingPlayerId);
        var result = ImmutableArray.CreateBuilder<CombatAttackDeclarationOption>();
        foreach (var attacker in player.Domain.HorizonCardInstanceIds
                     .Where(cardInstanceId => cardInstanceId is not null)
                     .Select(cardInstanceId => state.GetCardInstance(cardInstanceId!))
                     .OrderBy(card => card.DomainLaneIndex)
                     .ThenBy(card => card.CreatedSequence)
                     .ThenBy(card => card.CardInstanceId, StringComparer.Ordinal))
        {
            if (!IsLegalAttacker(
                    state,
                    player,
                    attacker,
                    runtimePackage,
                    canonicalAbilities))
            {
                continue;
            }

            var attackerRef = new GameObjectRefState(
                CombatRuleIds.CardInstanceObjectKind,
                attacker.CardInstanceId,
                attacker.ZoneSequence);
            var targets = ResolveTargetsForAttacker(
                state,
                attacker,
                defendingPlayer,
                runtimePackage,
                canonicalAbilities);
            result.AddRange(targets.Select(target => new CombatAttackDeclarationOption(
                attacker,
                attackerRef,
                defendingPlayerId,
                target.Target,
                target.AttackLaneIndex,
                target.Card?.DomainRow,
                target.HasWard)));
        }

        return result.ToImmutable();
    }

    internal static bool IsStartingPlayerFirstTurnAttackBan(MatchState state, string playerId) =>
        state.TurnNumber == 1
        && string.Equals(state.StartingPlayerId, playerId, StringComparison.Ordinal);

    private static bool IsLegalAttacker(
        MatchState state,
        PlayerState player,
        CardInstanceState attacker,
        RuntimePackageCatalog runtimePackage,
        CanonicalAbilityCatalog? canonicalAbilities)
    {
        if (!runtimePackage.Cards.TryGetValue(attacker.CardId, out var definition)
            || !string.Equals(definition.CardType, "entity", StringComparison.Ordinal)
            || !string.Equals(attacker.ControllerPlayerId, player.PlayerId, StringComparison.Ordinal)
            || !string.Equals(attacker.Zone, "dominion", StringComparison.Ordinal)
            || attacker.DomainRow != DomainRow.Horizon
            || attacker.DomainLaneIndex is null
            || !string.Equals(attacker.ActivityState, "active", StringComparison.Ordinal)
            || attacker.EnteredDomainTurnNumber is null
            || attacker.EnteredDomainTurnNumber > state.TurnNumber
            || HasCannotInitiateAttackRestriction(attacker, canonicalAbilities))
        {
            return false;
        }

        var summoningSick = attacker.EnteredDomainTurnNumber == state.TurnNumber;
        return !summoningSick
               || HasEffectiveKeyword(
                   state,
                   attacker,
                   canonicalAbilities,
                   CombatRuleIds.SpeedKeyword);
    }

    private static ImmutableArray<CombatTargetCandidate> ResolveTargetsForAttacker(
        MatchState state,
        CardInstanceState attacker,
        PlayerState defender,
        RuntimePackageCatalog runtimePackage,
        CanonicalAbilityCatalog? canonicalAbilities)
    {
        var entityTargets = ResolveEntityTargets(
            state,
            attacker,
            defender,
            runtimePackage,
            canonicalAbilities);
        var wardTargets = entityTargets.Where(candidate => candidate.HasWard)
            .ToImmutableArray();
        if (!wardTargets.IsDefaultOrEmpty)
        {
            return wardTargets;
        }

        var result = ImmutableArray.CreateBuilder<CombatTargetCandidate>();
        result.AddRange(entityTargets);
        foreach (var seal in defender.SealSlots
                     .Where(slot => string.Equals(slot.Status, "standing", StringComparison.Ordinal))
                     .OrderBy(slot => slot.LaneIndex))
        {
            if (defender.Domain.HorizonCardInstanceIds[seal.LaneIndex] is not null
                || defender.Domain.ZenithCardInstanceIds[seal.LaneIndex] is not null)
            {
                continue;
            }

            result.Add(new CombatTargetCandidate(
                new CombatTargetState(
                    CombatRuleIds.SealSlotTargetKind,
                    seal.SealSlotId,
                    EntityRef: null),
                seal.LaneIndex,
                Card: null,
                HasWard: false));
        }

        if (defender.SealSlots.Count > 0
            && defender.SealSlots.All(slot => string.Equals(
                slot.Status,
                "broken",
                StringComparison.Ordinal)))
        {
            // Aeternal has no board lane. Its attack path is authoritatively bound
            // to the declaring attacker's current Horizon lane.
            result.Add(new CombatTargetCandidate(
                new CombatTargetState(
                    CombatRuleIds.AeternalTargetKind,
                    $"aeternal:{defender.PlayerId}",
                    EntityRef: null),
                attacker.DomainLaneIndex
                ?? throw new EngineStateException("A legal attacker has no Horizon lane."),
                Card: null,
                HasWard: false));
        }

        return result.ToImmutable();
    }

    private static ImmutableArray<CombatTargetCandidate> ResolveEntityTargets(
        MatchState state,
        CardInstanceState attacker,
        PlayerState defender,
        RuntimePackageCatalog runtimePackage,
        CanonicalAbilityCatalog? canonicalAbilities)
    {
        var attackerIsAerial = HasEffectiveKeyword(
            state,
            attacker,
            canonicalAbilities,
            CombatRuleIds.AerialKeyword);
        var result = ImmutableArray.CreateBuilder<CombatTargetCandidate>();
        for (var laneIndex = 0; laneIndex < DomainState.LaneCount; laneIndex += 1)
        {
            AddEntityTarget(defender.Domain.HorizonCardInstanceIds[laneIndex], laneIndex);
            if (defender.Domain.HorizonCardInstanceIds[laneIndex] is null)
            {
                AddEntityTarget(defender.Domain.ZenithCardInstanceIds[laneIndex], laneIndex);
            }
        }

        return result.ToImmutable();

        void AddEntityTarget(string? cardInstanceId, int laneIndex)
        {
            if (cardInstanceId is null)
            {
                return;
            }

            var target = state.GetCardInstance(cardInstanceId);
            if (!runtimePackage.Cards.TryGetValue(target.CardId, out var definition)
                || !string.Equals(definition.CardType, "entity", StringComparison.Ordinal)
                || !string.Equals(target.ControllerPlayerId, defender.PlayerId, StringComparison.Ordinal)
                || !string.Equals(target.Zone, "dominion", StringComparison.Ordinal)
                || target.DomainLaneIndex != laneIndex
                || target.DomainRow is null
                || target.ActivityState is not ("active" or "exhausted")
                || HasEffectiveKeyword(
                    state,
                    target,
                    canonicalAbilities,
                    CombatRuleIds.AerialKeyword) && !attackerIsAerial)
            {
                return;
            }

            result.Add(new CombatTargetCandidate(
                new CombatTargetState(
                    CombatRuleIds.EntityTargetKind,
                    target.CardInstanceId,
                    new GameObjectRefState(
                        CombatRuleIds.CardInstanceObjectKind,
                        target.CardInstanceId,
                        target.ZoneSequence)),
                laneIndex,
                target,
                target.DomainRow == DomainRow.Horizon
                && string.Equals(target.ActivityState, "active", StringComparison.Ordinal)
                && HasEffectiveKeyword(
                    state,
                    target,
                    canonicalAbilities,
                    CombatRuleIds.WardKeyword)));
        }
    }

    internal static string ResolveAttackContinuityState(
        MatchState state,
        PendingCombatState combat,
        RuntimePackageCatalog? runtimePackage)
    {
        ArgumentNullException.ThrowIfNull(state);
        ArgumentNullException.ThrowIfNull(combat);
        if (runtimePackage is null
            || !IsContinuousDominionEntity(
                state,
                combat.AttackerRef,
                combat.AttackingPlayerId,
                DomainRow.Horizon,
                expectedLaneIndex: null,
                runtimePackage))
        {
            return CombatRuleIds.AttackContinuityAttackerLost;
        }

        return combat.OriginalTarget.TargetKindId switch
        {
            CombatRuleIds.EntityTargetKind =>
                combat.OriginalTarget.EntityRef is not null
                && combat.OriginalTargetRowAtAttackCommit is DomainRow targetRow
                && IsContinuousDominionEntity(
                    state,
                    combat.OriginalTarget.EntityRef,
                    combat.DefendingPlayerId,
                    targetRow,
                    combat.OriginalAttackLaneIndex,
                    runtimePackage)
                    ? CombatRuleIds.AttackContinuityContinuous
                    : CombatRuleIds.AttackContinuityTargetLost,
            CombatRuleIds.SealSlotTargetKind => state.GetPlayer(combat.DefendingPlayerId).SealSlots
                .Any(slot => string.Equals(
                                 slot.SealSlotId,
                                 combat.OriginalTarget.PublicTargetId,
                                 StringComparison.Ordinal)
                             && slot.LaneIndex == combat.OriginalAttackLaneIndex
                             && string.Equals(slot.Status, "standing", StringComparison.Ordinal))
                    ? CombatRuleIds.AttackContinuityContinuous
                    : CombatRuleIds.AttackContinuitySealUnavailable,
            CombatRuleIds.AeternalTargetKind => state.GetPlayer(combat.DefendingPlayerId).SealSlots
                .All(slot => string.Equals(slot.Status, "broken", StringComparison.Ordinal))
                    ? CombatRuleIds.AttackContinuityContinuous
                    : CombatRuleIds.AttackContinuityAeternalPathClosed,
            _ => throw new EngineStateException("PendingCombat target kind is unsupported."),
        };
    }

    internal static ImmutableArray<CombatInterventionOption> ResolveInterventionCandidates(
        MatchState state,
        PendingCombatState combat,
        RuntimePackageCatalog? runtimePackage,
        CanonicalAbilityCatalog? canonicalAbilities)
    {
        ArgumentNullException.ThrowIfNull(state);
        ArgumentNullException.ThrowIfNull(combat);
        if (runtimePackage is null
            || !string.Equals(
                combat.AttackContinuityStateId,
                CombatRuleIds.AttackContinuityContinuous,
                StringComparison.Ordinal)
            || combat.OriginalTargetHadWardAtAttackCommit
            || string.Equals(
                combat.OriginalTarget.TargetKindId,
                CombatRuleIds.AeternalTargetKind,
                StringComparison.Ordinal))
        {
            return ImmutableArray<CombatInterventionOption>.Empty;
        }

        var attacker = state.GetCardInstance(combat.AttackerRef.ObjectId);
        var attackerIsAerial = HasEffectiveKeyword(
            state,
            attacker,
            canonicalAbilities,
            CombatRuleIds.AerialKeyword);
        var defender = state.GetPlayer(combat.DefendingPlayerId);
        var result = ImmutableArray.CreateBuilder<CombatInterventionOption>();
        foreach (var candidate in defender.Domain.HorizonCardInstanceIds
                     .Select((cardInstanceId, laneIndex) => (cardInstanceId, laneIndex))
                     .Where(item => item.cardInstanceId is not null
                                    && Math.Abs(item.laneIndex - combat.OriginalAttackLaneIndex) == 1)
                     .Select(item => (Card: state.GetCardInstance(item.cardInstanceId!), item.laneIndex))
                     .OrderBy(item => item.laneIndex)
                     .ThenBy(item => item.Card.CreatedSequence)
                     .ThenBy(item => item.Card.CardInstanceId, StringComparer.Ordinal))
        {
            if (!runtimePackage.Cards.TryGetValue(candidate.Card.CardId, out var definition)
                || !string.Equals(definition.CardType, "entity", StringComparison.Ordinal)
                || !string.Equals(
                    candidate.Card.ControllerPlayerId,
                    combat.DefendingPlayerId,
                    StringComparison.Ordinal)
                || !string.Equals(candidate.Card.Zone, "dominion", StringComparison.Ordinal)
                || candidate.Card.DomainRow != DomainRow.Horizon
                || candidate.Card.DomainLaneIndex != candidate.laneIndex
                || !string.Equals(candidate.Card.ActivityState, "active", StringComparison.Ordinal)
                || HasEffectiveKeyword(
                    state,
                    candidate.Card,
                    canonicalAbilities,
                    CombatRuleIds.AerialKeyword) != attackerIsAerial)
            {
                continue;
            }

            result.Add(new CombatInterventionOption(
                candidate.Card,
                new GameObjectRefState(
                    CombatRuleIds.CardInstanceObjectKind,
                    candidate.Card.CardInstanceId,
                    candidate.Card.ZoneSequence),
                candidate.laneIndex));
        }

        return result.ToImmutable();
    }

    internal static bool IsContinuousDominionEntity(
        MatchState state,
        GameObjectRefState reference,
        string controllerPlayerId,
        DomainRow expectedRow,
        int? expectedLaneIndex,
        RuntimePackageCatalog runtimePackage)
    {
        if (!state.CardInstances.TryGetValue(reference.ObjectId, out var card)
            || card.ZoneSequence != reference.IncarnationSequence
            || !runtimePackage.Cards.TryGetValue(card.CardId, out var definition)
            || !string.Equals(definition.CardType, "entity", StringComparison.Ordinal)
            || !string.Equals(card.ControllerPlayerId, controllerPlayerId, StringComparison.Ordinal)
            || !string.Equals(card.Zone, "dominion", StringComparison.Ordinal)
            || card.DomainRow != expectedRow
            || card.DomainLaneIndex is not int laneIndex
            || expectedLaneIndex is int requiredLane && laneIndex != requiredLane)
        {
            return false;
        }

        var slots = state.GetPlayer(controllerPlayerId).Domain.GetSlots(expectedRow);
        return laneIndex >= 0
               && laneIndex < slots.Count
               && string.Equals(slots[laneIndex], card.CardInstanceId, StringComparison.Ordinal);
    }

    private static bool HasEffectiveKeyword(
        MatchState state,
        CardInstanceState card,
        CanonicalAbilityCatalog? canonicalAbilities,
        string keywordId) => canonicalAbilities is not null
        && CanonicalContinuousEffects.HasEffectiveKeyword(
            state,
            card,
            canonicalAbilities,
            keywordId);

    private static bool HasCannotInitiateAttackRestriction(
        CardInstanceState attacker,
        CanonicalAbilityCatalog? canonicalAbilities) => canonicalAbilities is not null
        && canonicalAbilities.AbilitiesByCardId.TryGetValue(attacker.CardId, out var abilities)
        && abilities.Any(ability =>
            string.Equals(ability.Status, "active", StringComparison.Ordinal)
            && string.Equals(ability.AbilityKindId, "static", StringComparison.Ordinal)
            && string.Equals(ability.ActiveZoneId, attacker.Zone, StringComparison.Ordinal)
            && ability.Effects.Any(effect => string.Equals(
                effect.RestrictionTypeId,
                "restriction_entity_cannot_initiate_attack",
                StringComparison.Ordinal)));

    private sealed record CombatTargetCandidate(
        CombatTargetState Target,
        int AttackLaneIndex,
        CardInstanceState? Card,
        bool HasWard);
}
