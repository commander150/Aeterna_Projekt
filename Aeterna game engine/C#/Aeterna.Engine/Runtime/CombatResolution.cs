using System.Collections.Immutable;
using Aeterna.Engine.State;

namespace Aeterna.Engine.Runtime;

internal sealed record CombatDamageMutation(
    string DamageInstanceId,
    GameObjectRefState SourceRef,
    string SourceCardId,
    GameObjectRefState TargetRef,
    string TargetCardId,
    int Amount,
    int DamageBefore,
    int DamageAfter,
    int EffectiveMaxHp,
    bool Lethal,
    CanonicalDestructionMutation? Destruction);

internal sealed record CombatResolutionPlan(
    string CombatId,
    int CombatStageSequence,
    int StateVersion,
    string TimingAnchorId,
    string SimultaneousGroupId,
    string OutcomeId,
    string? NoHitReasonId,
    string? FutureStageId,
    GameObjectRefState AttackerRef,
    GameObjectRefState? OpponentRef,
    ImmutableArray<CombatDamageMutation> DamageMutations);

internal static class CombatResolution
{
    internal static CombatResolutionPlan BuildPlan(
        MatchState state,
        PendingCombatState combat,
        RuntimePackageCatalog? runtimePackage,
        CanonicalCardCatalog? canonicalCards,
        CanonicalAbilityCatalog? canonicalAbilities)
    {
        ArgumentNullException.ThrowIfNull(state);
        ArgumentNullException.ThrowIfNull(combat);
        if (!string.Equals(
                combat.StageId,
                CombatRuleIds.DefenseCheckpointStage,
                StringComparison.Ordinal))
        {
            throw new EngineStateException(
                "Combat resolution can only be planned from defense_checkpoint.");
        }

        if (runtimePackage is null || canonicalCards is null)
        {
            throw new EngineStateException(
                "COMBAT_CARD_STATS_REQUIRED",
                "Combat resolution requires runtime Entity identity and canonical card-stat authority.");
        }

        var timingAnchorId = $"{combat.CombatId}:resolution";
        var simultaneousGroupId = $"{combat.CombatId}:simultaneous_damage";
        if (!CombatRules.IsContinuousDominionEntity(
                state,
                combat.AttackerRef,
                combat.AttackingPlayerId,
                DomainRow.Horizon,
                expectedLaneIndex: null,
                runtimePackage))
        {
            return NoHit(
                state,
                combat,
                timingAnchorId,
                simultaneousGroupId,
                CombatRuleIds.AttackerMissingNoHitReason,
                OpponentReference(combat));
        }

        if (!combat.DefenseCommitted
            && !string.Equals(
                combat.OriginalTarget.TargetKindId,
                CombatRuleIds.EntityTargetKind,
                StringComparison.Ordinal))
        {
            var futureStageId = combat.OriginalTarget.TargetKindId switch
            {
                CombatRuleIds.SealSlotTargetKind => CombatRuleIds.SealOutcomeCheckpointStage,
                CombatRuleIds.AeternalTargetKind => CombatRuleIds.AeternalOutcomeCheckpointStage,
                _ => throw new EngineStateException("PendingCombat target kind is unsupported."),
            };
            return new CombatResolutionPlan(
                combat.CombatId,
                combat.StageSequence,
                state.StateVersion,
                timingAnchorId,
                simultaneousGroupId,
                CombatRuleIds.FutureOutcomePending,
                NoHitReasonId: null,
                futureStageId,
                combat.AttackerRef,
                OpponentRef: null,
                ImmutableArray<CombatDamageMutation>.Empty);
        }

        var opponentRef = combat.DefenseCommitted
            ? combat.DefenderRef
              ?? throw new EngineStateException("Committed Combat defense has no DefenderRef.")
            : combat.OriginalTarget.EntityRef
              ?? throw new EngineStateException("Undefended Entity Combat has no OriginalTarget reference.");
        var opponentControllerId = combat.DefendingPlayerId;
        var expectedOpponentRow = combat.DefenseCommitted
            ? DomainRow.Horizon
            : combat.OriginalTargetRowAtAttackCommit
              ?? throw new EngineStateException("Undefended Entity Combat has no committed target row.");
        var expectedOpponentLane = combat.DefenseCommitted
            ? combat.DefenderLaneAtCommit
              ?? throw new EngineStateException("Committed Combat defense has no defender lane.")
            : combat.OriginalAttackLaneIndex;
        if (!CombatRules.IsContinuousDominionEntity(
                state,
                opponentRef,
                opponentControllerId,
                expectedOpponentRow,
                expectedOpponentLane,
                runtimePackage))
        {
            return NoHit(
                state,
                combat,
                timingAnchorId,
                simultaneousGroupId,
                combat.DefenseCommitted
                    ? CombatRuleIds.DefenderMissingNoHitReason
                    : CombatRuleIds.TargetMissingNoHitReason,
                opponentRef);
        }

        var attacker = state.GetCardInstance(combat.AttackerRef.ObjectId);
        var opponent = state.GetCardInstance(opponentRef.ObjectId);
        var attackerIsAerial = HasAerial(state, attacker, canonicalAbilities);
        var opponentIsAerial = HasAerial(state, opponent, canonicalAbilities);
        var contactValid = IsFinalContactValid(
            attackerIsAerial,
            opponentIsAerial,
            combat.DefenseCommitted);
        if (!contactValid)
        {
            return NoHit(
                state,
                combat,
                timingAnchorId,
                simultaneousGroupId,
                CombatRuleIds.ContactInvalidNoHitReason,
                opponentRef);
        }

        var attackerAtk = CanonicalVitals.GetEffectiveAtk(state, attacker, canonicalCards);
        var opponentAtk = CanonicalVitals.GetEffectiveAtk(state, opponent, canonicalCards);
        var voidCounts = state.Players.ToDictionary(
            player => player.PlayerId,
            player => player.VoidCardInstanceIds.Count,
            StringComparer.Ordinal);
        var attackerToOpponent = BuildDamageMutation(
            state,
            combat,
            combat.AttackerRef,
            attacker,
            opponentRef,
            opponent,
            attackerAtk,
            "attacker_to_opponent",
            canonicalCards,
            voidCounts);
        var opponentToAttacker = BuildDamageMutation(
            state,
            combat,
            opponentRef,
            opponent,
            combat.AttackerRef,
            attacker,
            opponentAtk,
            "opponent_to_attacker",
            canonicalCards,
            voidCounts);
        return new CombatResolutionPlan(
            combat.CombatId,
            combat.StageSequence,
            state.StateVersion,
            timingAnchorId,
            simultaneousGroupId,
            CombatRuleIds.EntityCombatResolvedOutcome,
            NoHitReasonId: null,
            FutureStageId: null,
            combat.AttackerRef,
            opponentRef,
            [attackerToOpponent, opponentToAttacker]);
    }

    internal static void Apply(MatchState state, CombatResolutionPlan plan)
    {
        ArgumentNullException.ThrowIfNull(state);
        ArgumentNullException.ThrowIfNull(plan);
        var combat = state.PendingCombat;
        if (combat is null
            || !string.Equals(combat.CombatId, plan.CombatId, StringComparison.Ordinal)
            || !string.Equals(
                combat.StageId,
                CombatRuleIds.DefenseCheckpointStage,
                StringComparison.Ordinal)
            || combat.StageSequence != plan.CombatStageSequence
            || state.StateVersion != plan.StateVersion)
        {
            throw new EngineStateException("Combat resolution plan is stale.");
        }

        if (plan.FutureStageId is not null || plan.DamageMutations.IsDefaultOrEmpty)
        {
            return;
        }

        foreach (var damage in plan.DamageMutations)
        {
            var target = state.GetCardInstance(damage.TargetRef.ObjectId);
            if (target.ZoneSequence != damage.TargetRef.IncarnationSequence
                || !string.Equals(target.Zone, "dominion", StringComparison.Ordinal)
                || target.DamageMarked != damage.DamageBefore)
            {
                throw new EngineStateException("Combat damage plan no longer matches its target state.");
            }
        }

        // Both marks are committed before either lethal transition is applied.
        foreach (var damage in plan.DamageMutations)
        {
            state.GetCardInstance(damage.TargetRef.ObjectId).DamageMarked = damage.DamageAfter;
        }

        foreach (var damage in plan.DamageMutations)
        {
            if (damage.Destruction is not null)
            {
                CanonicalZoneTransition.Apply(state, damage.Destruction.ZoneTransition);
            }
        }
    }

    private static CombatDamageMutation BuildDamageMutation(
        MatchState state,
        PendingCombatState combat,
        GameObjectRefState sourceRef,
        CardInstanceState source,
        GameObjectRefState targetRef,
        CardInstanceState target,
        int amount,
        string directionId,
        CanonicalCardCatalog canonicalCards,
        IDictionary<string, int> voidCounts)
    {
        var afterLong = (long)target.DamageMarked + amount;
        if (amount < 0 || afterLong > int.MaxValue)
        {
            throw new EngineStateException(
                "COMBAT_DAMAGE_AMOUNT_INVALID",
                "Combat damage accumulation is outside the supported integer range.");
        }

        var after = (int)afterLong;
        var effectiveMaxHp = CanonicalVitals.GetEffectiveMaxHp(state, target, canonicalCards);
        var damageInstanceId = $"damage:{combat.CombatId}:{directionId}";
        var lethal = after >= effectiveMaxHp;
        CanonicalDestructionMutation? destruction = null;
        if (lethal)
        {
            var destructionInstanceId = $"destruction:{combat.CombatId}:{target.CardInstanceId}";
            var transition = CanonicalZoneTransition.PlanDominionToVoid(
                target,
                voidCounts[target.OwnerPlayerId],
                $"zone_transition:{destructionInstanceId}",
                CanonicalZoneTransitionCauseKinds.CombatDamageLethal,
                destructionInstanceId);
            voidCounts[target.OwnerPlayerId] += 1;
            destruction = new CanonicalDestructionMutation(
                destructionInstanceId,
                "destruction_cause_kind_combat_lethal_hp_state",
                source.CardInstanceId,
                damageInstanceId,
                transition);
        }

        return new CombatDamageMutation(
            damageInstanceId,
            sourceRef,
            source.CardId,
            targetRef,
            target.CardId,
            amount,
            target.DamageMarked,
            after,
            effectiveMaxHp,
            lethal,
            destruction);
    }

    private static CombatResolutionPlan NoHit(
        MatchState state,
        PendingCombatState combat,
        string timingAnchorId,
        string simultaneousGroupId,
        string reasonId,
        GameObjectRefState? opponentRef) => new(
        combat.CombatId,
        combat.StageSequence,
        state.StateVersion,
        timingAnchorId,
        simultaneousGroupId,
        CombatRuleIds.NoHitOutcome,
        reasonId,
        FutureStageId: null,
        combat.AttackerRef,
        opponentRef,
        ImmutableArray<CombatDamageMutation>.Empty);

    internal static bool IsFinalContactValid(
        bool attackerIsAerial,
        bool opponentIsAerial,
        bool defenseCommitted) => defenseCommitted
        ? attackerIsAerial == opponentIsAerial
        : !opponentIsAerial || attackerIsAerial;

    private static GameObjectRefState? OpponentReference(PendingCombatState combat) =>
        combat.DefenseCommitted
            ? combat.DefenderRef
            : combat.OriginalTarget.EntityRef;

    private static bool HasAerial(
        MatchState state,
        CardInstanceState card,
        CanonicalAbilityCatalog? canonicalAbilities) => canonicalAbilities is not null
        && CanonicalContinuousEffects.HasEffectiveKeyword(
            state,
            card,
            canonicalAbilities,
            CombatRuleIds.AerialKeyword);
}
