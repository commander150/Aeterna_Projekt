using System.Collections.Immutable;
using System.Text.Json;
using Aeterna.Engine;
using Aeterna.Engine.Contracts;
using Aeterna.Engine.Rules;
using Aeterna.Engine.Runtime;
using Aeterna.Engine.State;

internal static class CombatSealFoundationTests
{
    private const string PlainEntityCardId = "IGN-HAM-044";
    private const string SpeedEntityCardId = "IGN-HAM-001";
    private const string AerialEntityCardId = "IGN-LAN-003";
    private const string WardEntityCardId = "FIXTURE-ENTITY-WARD";
    private const string RestrictedEntityCardId = "AQU-MOR-017";
    private const string ReactionEntityCardId = "IGN-HAM-005";
    private const string ReactionAbilityId = "ability_ign_ham_005_01";
    private const string ReactionTargetId = "target_ign_ham_005_01_enemy_horizont_entity";

    internal static void PhaseAttackerSummoningAndSpeedLegality()
    {
        var fixture = CreateFixture(
            "combat-attacker-legality",
            board:
            [
                Board("attacker", PlainEntityCardId, "player_1", DomainRow.Horizon, 0, "active", 1),
                Board("target", PlainEntityCardId, "player_2", DomainRow.Horizon, 0, "active", 1),
            ]);
        var attacker = fixture.State.GetCardInstance("attacker");

        fixture.State.Phase = CanonicalPhaseIds.Manifestation;
        False(
            fixture.Session.ListLegalActions("player_1", includeDisabled: true).Actions
                .Any(action => action.ActionType == "attack"),
            "Attack was exposed outside Incursion.");

        fixture.State.Phase = CanonicalPhaseIds.Incursion;
        True(AttackAction(fixture, "player_1").Enabled, "Active Incursion attacker was not legal.");
        var inactiveAction = AttackAction(fixture, "player_2");
        False(inactiveAction.Enabled, "Inactive player received attack authority.");
        Equal("not_active_player", inactiveAction.DisabledReason, "Inactive attack reason is unstable.");

        attacker.ActivityState = "exhausted";
        AssertNoLegalAttack(fixture, "Exhausted attacker was legal.");
        attacker.ActivityState = "active";
        fixture.State.GetPlayer("player_1").Domain.HorizonCardInstanceIds[0] = null;
        True(
            fixture.State.GetPlayer("player_1").Domain.TryOccupy(DomainRow.Zenith, 0, attacker.CardInstanceId),
            "Attacker could not be moved to the Zenith legality fixture.");
        attacker.DomainRow = DomainRow.Zenith;
        AssertNoLegalAttack(fixture, "Zenith attacker was legal.");

        fixture.State.GetPlayer("player_1").Domain.ZenithCardInstanceIds[0] = null;
        True(
            fixture.State.GetPlayer("player_1").Domain.TryOccupy(DomainRow.Horizon, 0, attacker.CardInstanceId),
            "Attacker could not be restored to Horizon.");
        attacker.DomainRow = DomainRow.Horizon;
        attacker.EnteredDomainTurnNumber = fixture.State.TurnNumber;
        AssertNoLegalAttack(fixture, "Summoning-sick attacker without Speed was legal.");

        var speed = CreateFixture(
            "combat-speed",
            board:
            [
                Board("speed-attacker", SpeedEntityCardId, "player_1", DomainRow.Horizon, 0, "active", 2),
                Board("speed-target", PlainEntityCardId, "player_2", DomainRow.Horizon, 0, "active", 1),
            ]);
        True(AttackAction(speed, "player_1").Enabled, "Speed did not bypass summoning sickness.");

        var firstTurn = CreateFixture(
            "combat-first-turn-ban",
            turnNumber: 1,
            board:
            [
                Board("first-turn-speed", SpeedEntityCardId, "player_1", DomainRow.Horizon, 0, "active", 1),
                Board("first-turn-target", PlainEntityCardId, "player_2", DomainRow.Horizon, 0, "active", 1),
            ]);
        var firstTurnAction = AttackAction(firstTurn, "player_1");
        False(firstTurnAction.Enabled, "Starting player attacked on the first turn with Speed.");
        Equal(
            "starting_player_first_turn_attack_forbidden",
            firstTurnAction.DisabledReason,
            "Starting-player first-turn attack reason is unstable.");
        firstTurn.State.TurnNumber = 2;
        True(AttackAction(firstTurn, "player_1").Enabled, "Attack did not become available in the next eligible round.");

        var restricted = CreateFixture(
            "combat-static-restriction",
            board:
            [
                Board("restricted-attacker", RestrictedEntityCardId, "player_1", DomainRow.Horizon, 0, "active", 1),
                Board("restricted-target", PlainEntityCardId, "player_2", DomainRow.Horizon, 0, "active", 1),
            ]);
        AssertNoLegalAttack(restricted, "Canonical cannot-initiate-attack restriction was ignored.");
    }

    internal static void HorizonZenithWardAndAerialTargeting()
    {
        var layers = CreateFixture(
            "combat-target-layers",
            board:
            [
                Board("layer-attacker", PlainEntityCardId, "player_1", DomainRow.Horizon, 5, "active", 1),
                Board("horizon-zero", PlainEntityCardId, "player_2", DomainRow.Horizon, 0, "active", 1),
                Board("zenith-zero", PlainEntityCardId, "player_2", DomainRow.Zenith, 0, "active", 1),
                Board("zenith-one", PlainEntityCardId, "player_2", DomainRow.Zenith, 1, "active", 1),
                Board("horizon-exhausted", PlainEntityCardId, "player_2", DomainRow.Horizon, 3, "exhausted", 1),
                Board("aerial-four", AerialEntityCardId, "player_2", DomainRow.Horizon, 4, "active", 1),
            ]);
        var layerTargets = EntityTargetIds(layers);
        True(layerTargets.Contains("horizon-zero"), "Horizon target was not legal.");
        True(layerTargets.Contains("zenith-one"), "Unprotected Zenith target was not legal.");
        True(layerTargets.Contains("horizon-exhausted"), "Exhausted Horizon target was not legal.");
        False(layerTargets.Contains("zenith-zero"), "Protected Zenith target was legal.");
        False(layerTargets.Contains("aerial-four"), "Ground attacker targeted an Aerial Entity.");

        var aerial = CreateFixture(
            "combat-aerial-targeting",
            board:
            [
                Board("aerial-attacker", AerialEntityCardId, "player_1", DomainRow.Horizon, 0, "active", 1),
                Board("ground-target", PlainEntityCardId, "player_2", DomainRow.Horizon, 0, "active", 1),
                Board("aerial-target", AerialEntityCardId, "player_2", DomainRow.Horizon, 1, "active", 1),
            ]);
        var aerialTargets = EntityTargetIds(aerial);
        True(aerialTargets.Contains("ground-target"), "Aerial attacker could not target a ground Entity.");
        True(aerialTargets.Contains("aerial-target"), "Aerial attacker could not target an Aerial Entity.");

        var ward = CreateFixture(
            "combat-ward-priority",
            board:
            [
                Board("ward-attacker", PlainEntityCardId, "player_1", DomainRow.Horizon, 0, "active", 1),
                Board("plain-target", PlainEntityCardId, "player_2", DomainRow.Horizon, 0, "active", 1),
                Board("ward-active-one", WardEntityCardId, "player_2", DomainRow.Horizon, 1, "active", 1),
                Board("ward-active-two", WardEntityCardId, "player_2", DomainRow.Horizon, 2, "active", 1),
                Board("ward-exhausted", WardEntityCardId, "player_2", DomainRow.Horizon, 3, "exhausted", 1),
            ]);
        SequenceEqual(
            ["ward-active-one", "ward-active-two"],
            AttackChoices(ward).Select(choice => choice.TargetId),
            "Active Horizon Ward did not exclusively constrain the attack target set.");
    }

    internal static void SealSlotAndAeternalDeclarationLegality()
    {
        var standing = CreateFixture(
            "combat-seal-targets",
            board:
            [
                Board("seal-attacker", PlainEntityCardId, "player_1", DomainRow.Horizon, 5, "active", 1),
                Board("seal-block-horizon", PlainEntityCardId, "player_2", DomainRow.Horizon, 0, "active", 1),
                Board("seal-block-zenith", PlainEntityCardId, "player_2", DomainRow.Zenith, 1, "active", 1),
            ]);
        var sealTargets = AttackChoices(standing)
            .Where(choice => choice.TargetKindId == CombatRuleIds.SealSlotTargetKind)
            .Select(choice => choice.TargetId)
            .ToArray();
        SequenceEqual(
            ["seal:player_2:03", "seal:player_2:04", "seal:player_2:05", "seal:player_2:06"],
            sealTargets,
            "Standing Seal target legality did not follow lane openness.");
        False(
            AttackChoices(standing).Any(choice => choice.TargetKindId == CombatRuleIds.AeternalTargetKind),
            "Aeternal was targetable while standing Seals remained.");
        var beforeHiddenIdentityAttempt = Fingerprint(standing);
        var hiddenIdentityAttempt = SubmitAttack(
            standing,
            AttackAction(standing, "player_1"),
            "hidden-seal-identity-attack",
            "seal-attacker",
            CombatRuleIds.SealSlotTargetKind,
            "player_2-hidden-seal-03");
        False(hiddenIdentityAttempt.Accepted, "Hidden Seal CardInstanceId was accepted as a public target.");
        Equal(beforeHiddenIdentityAttempt, Fingerprint(standing), "Hidden Seal target rejection mutated state.");

        var broken = CreateFixture(
            "combat-aeternal-target",
            playerTwoSealsBroken: true,
            board:
            [
                Board("aeternal-attacker", PlainEntityCardId, "player_1", DomainRow.Horizon, 4, "active", 1),
            ]);
        var aeternal = Single(AttackChoices(broken));
        Equal(CombatRuleIds.AeternalTargetKind, aeternal.TargetKindId, "Zero-standing-Seal target kind is invalid.");
        Equal("aeternal:player_2", aeternal.TargetId, "Aeternal public target identity is invalid.");
    }

    internal static void AttackCommitIsAtomicBoundAndDeterministic()
    {
        var fixture = CreateFixture(
            "combat-commit",
            board:
            [
                Board("commit-attacker", PlainEntityCardId, "player_1", DomainRow.Horizon, 2, "active", 1, 4),
                Board("commit-target", PlainEntityCardId, "player_2", DomainRow.Horizon, 3, "active", 1, 7),
            ]);
        var action = AttackAction(fixture, "player_1");
        var before = Fingerprint(fixture);
        var stale = SubmitAttack(
            fixture,
            action,
            "stale-attack",
            "commit-attacker",
            CombatRuleIds.EntityTargetKind,
            "commit-target",
            expectedStateVersion: -1);
        False(stale.Accepted, "Stale attack was accepted.");
        Equal(before, Fingerprint(fixture), "Stale attack mutated state.");

        var illegal = SubmitAttack(
            fixture,
            action,
            "illegal-attack",
            "commit-attacker",
            CombatRuleIds.EntityTargetKind,
            "unknown-target");
        False(illegal.Accepted, "Illegal attacker/target tuple was accepted.");
        Equal(before, Fingerprint(fixture), "Illegal attack mutated state.");
        Equal(1, fixture.State.NextCombatSequence, "Rejected attack allocated a Combat identity.");
        Equal(null, fixture.State.PendingCombat, "Rejected attack created PendingCombat.");
        Equal("active", fixture.State.GetCardInstance("commit-attacker").ActivityState, "Rejected attack exhausted the attacker.");
        Equal(0, fixture.State.Events.Count, "Rejected attack emitted a committed event.");

        var response = SubmitAttack(
            fixture,
            action,
            "commit-attack",
            "commit-attacker",
            CombatRuleIds.EntityTargetKind,
            "commit-target");
        True(response.Accepted, "Legal attack declaration failed.");
        Equal(0, response.StateVersionBefore, "Attack state-version boundary started incorrectly.");
        Equal(1, response.StateVersionAfter, "AttackCommit did not advance state exactly once.");
        SequenceEqual(
            ["attack_declared", "attacker_exhausted", "reaction_window_opened"],
            response.Events.Select(engineEvent => engineEvent.EventType),
            "AttackCommit event order is invalid.");
        True(response.Events.All(engineEvent => engineEvent.StateVersion == 1), "AttackCommit events split across state versions.");
        Equal(1, response.Events.Count(engineEvent => engineEvent.EventType == "attacker_exhausted"),
            "AttackCommit did not exhaust exactly once.");
        Equal("exhausted", fixture.State.GetCardInstance("commit-attacker").ActivityState, "Attacker was not exhausted atomically.");

        var combat = NotNull(fixture.State.PendingCombat, "AttackCommit did not create PendingCombat.");
        Equal("combat:combat-commit:000001", combat.CombatId, "CombatId is not deterministic.");
        Equal(1, combat.CombatSequence, "Combat sequence is invalid.");
        Equal(CombatRuleIds.AttackReactionStage, combat.StageId, "Initial Combat stage is invalid.");
        Equal(1, combat.StageSequence, "Initial Combat stage sequence is invalid.");
        Equal(4, combat.AttackerRef.IncarnationSequence, "Attacker incarnation was not bound.");
        Equal(7, combat.OriginalTarget.EntityRef?.IncarnationSequence, "Target incarnation was not bound.");
        Equal(3, combat.OriginalAttackLaneIndex, "Target attack lane was not committed.");
        Equal("combat:combat-commit:000001:attack_commit", combat.AttackTimingAnchorId, "Attack timing anchor is invalid.");
        Equal(1, combat.AttackCommitStateVersion, "AttackCommit state version is invalid.");

        var bottom = Single(fixture.State.ResolutionStack);
        Equal(CombatRuleIds.CombatContinuationEntryKind, bottom.EntryKindId, "Combat continuation is not the bottom stack entry.");
        Equal(null, bottom.AbilityResolution, "Combat continuation reused an ability payload.");
        var continuation = NotNull(bottom.CombatContinuation, "Combat continuation payload is missing.");
        Equal(combat.CombatId, continuation.CombatId, "Continuation CombatId is inconsistent.");
        Equal(CombatRuleIds.AfterAttackReactionResumePoint, continuation.ResumePointId, "Combat resume point is invalid.");
        var window = NotNull(fixture.State.ReactionWindow, "First Combat ReactionWindow was not opened.");
        Equal(bottom.ResolutionId, window.UnderlyingResolutionId, "UnderlyingResolutionId does not bind the Combat continuation.");
        Equal("player_2", fixture.State.PriorityPlayerId, "Defender did not receive first Combat reaction priority.");
        EngineSession.ValidateState(fixture.State, fixture.CanonicalCards, fixture.CanonicalAbilities);
    }

    internal static void ReactionClosureLeavesExplicitAttackCheckpointAndBlocksGameplay()
    {
        var fixture = CreateFixture(
            "combat-checkpoint",
            board:
            [
                Board("checkpoint-attacker", AerialEntityCardId, "player_1", DomainRow.Horizon, 0, "active", 1),
                Board("checkpoint-target", PlainEntityCardId, "player_2", DomainRow.Horizon, 0, "active", 1),
            ]);
        var attackAction = AttackAction(fixture, "player_1");
        True(SubmitAttack(
            fixture,
            attackAction,
            "checkpoint-attack",
            "checkpoint-attacker",
            CombatRuleIds.EntityTargetKind,
            "checkpoint-target").Accepted, "Checkpoint attack failed.");

        var duringWindow = fixture.Session.ListLegalActions("player_2", includeDisabled: true).Actions;
        True(duringWindow.Single(action => action.ActionType == "pass_priority").Enabled, "Defender cannot pass Combat priority.");
        True(duringWindow.Where(action => action.ActionType is "advance_phase" or "attack")
            .All(action => !action.Enabled && action.DisabledReason == "reaction_window_open"),
            "Normal gameplay bypassed the first Combat ReactionWindow.");
        Equal(
            "reaction_window",
            fixture.Session.GetPlayerSnapshot("player_2").PendingDecisionSummary.GetProperty("pending_type").GetString(),
            "ReactionWindow did not take projection precedence over PendingCombat.");
        var beforeSecondAttack = Fingerprint(fixture);
        var blockedAttack = SubmitAttack(
            fixture,
            attackAction,
            "nested-attack",
            "checkpoint-attacker",
            CombatRuleIds.EntityTargetKind,
            "checkpoint-target");
        False(blockedAttack.Accepted, "A new attack was accepted during active Combat.");
        Equal(beforeSecondAttack, Fingerprint(fixture), "Blocked nested attack mutated state.");

        True(Pass(fixture, "player_2", "checkpoint-pass-one").Accepted, "First Combat pass failed.");
        var closure = Pass(fixture, "player_1", "checkpoint-pass-two");
        True(closure.Accepted, "Combat ReactionWindow closure failed.");
        Equal(null, fixture.State.ReactionWindow, "Closed Combat ReactionWindow remained open.");
        Equal(0, fixture.State.ResolutionStack.Count, "Closed Combat continuation remained on the stack.");
        Equal(null, fixture.State.PendingCombat, "Resolved Entity Combat retained PendingCombat.");
        Equal("exhausted", fixture.State.GetCardInstance("checkpoint-attacker").ActivityState,
            "Reaction closure rewound the committed attacker exhaustion.");
        Equal(1, fixture.State.GetCardInstance("checkpoint-attacker").DamageMarked,
            "The surviving attacker did not retain simultaneous return damage.");
        Equal("void", fixture.State.GetCardInstance("checkpoint-target").Zone,
            "Lethal target did not use the canonical Void transition.");
        True(closure.Events.Any(engineEvent => engineEvent.EventType == "combat_attack_reaction_completed"),
            "Combat checkpoint transition event is missing.");
        True(closure.Events.Any(engineEvent => engineEvent.EventType == "combat_damage_committed"),
            "Combat did not emit its simultaneous damage commitment.");
        True(closure.Events.Any(engineEvent => engineEvent.EventType == "combat_resolved"),
            "Combat resolution event is missing.");
        True(fixture.Session.ListLegalActions("player_1").Actions.Any(action => action.Enabled),
            "Normal gameplay did not resume after Entity Combat closed.");
        False(fixture.Session.GetPlayerSnapshot("player_1").PendingDecisionSummary
            .GetProperty("has_pending").GetBoolean(),
            "Closed Combat remained projected as a pending decision.");
    }

    internal static void CombatWindowUsesExistingReactPassAndLifoSemantics()
    {
        var fixture = CreateFixture(
            "combat-reaction-lifo",
            board:
            [
                Board("lifo-attacker", PlainEntityCardId, "player_1", DomainRow.Horizon, 0, "active", 1),
                Board("p1-reaction-target", PlainEntityCardId, "player_1", DomainRow.Horizon, 1, "active", 1),
                Board("p1-reaction-source", ReactionEntityCardId, "player_1", DomainRow.Zenith, 2, "active", 1),
                Board("lifo-attack-target", PlainEntityCardId, "player_2", DomainRow.Horizon, 0, "active", 1),
                Board("p2-reaction-target", PlainEntityCardId, "player_2", DomainRow.Horizon, 1, "active", 1),
                Board("p2-reaction-source", ReactionEntityCardId, "player_2", DomainRow.Zenith, 2, "active", 1),
            ]);
        True(SubmitAttack(
            fixture,
            AttackAction(fixture, "player_1"),
            "lifo-attack",
            "lifo-attacker",
            CombatRuleIds.EntityTargetKind,
            "lifo-attack-target").Accepted, "LIFO attack declaration failed.");

        var firstReaction = React(
            fixture,
            "player_2",
            "p2-reaction-source",
            "p1-reaction-target",
            "lifo-react-one");
        True(firstReaction.Accepted, "Defender reaction was rejected.");
        var firstResolutionId = firstReaction.Events.Single(engineEvent => engineEvent.EventType == "reaction_declared")
            .Payload.GetProperty("resolution_id").GetString()!;
        var secondReaction = React(
            fixture,
            "player_1",
            "p1-reaction-source",
            "p2-reaction-target",
            "lifo-react-two");
        True(secondReaction.Accepted, "Attacker response reaction was rejected.");
        var secondResolutionId = secondReaction.Events.Single(engineEvent => engineEvent.EventType == "reaction_declared")
            .Payload.GetProperty("resolution_id").GetString()!;
        var continuationId = fixture.State.ResolutionStack[0].ResolutionId;

        True(Pass(fixture, "player_2", "lifo-pass-one").Accepted, "First LIFO pass failed.");
        var closure = Pass(fixture, "player_1", "lifo-pass-two");
        True(closure.Accepted, "LIFO Combat closure failed.");
        SequenceEqual(
            [secondResolutionId, firstResolutionId, continuationId],
            closure.Events.Where(engineEvent => engineEvent.EventType == "resolution_entry_resolved")
                .Select(engineEvent => engineEvent.Payload.GetProperty("resolution_id").GetString()!),
            "Combat reactions did not resolve LIFO above the continuation.");
        Equal("exhausted", fixture.State.GetCardInstance("p1-reaction-target").ActivityState, "Defender reaction did not resolve.");
        Equal("exhausted", fixture.State.GetCardInstance("p2-reaction-target").ActivityState, "Attacker reaction did not resolve.");
        Equal(null, fixture.State.PendingCombat, "LIFO closure did not finish Entity Combat.");
        True(closure.Events.Any(engineEvent => engineEvent.EventType == "combat_resolved"),
            "LIFO closure omitted the Combat result.");
    }

    internal static void CombatProjectionProtectsHiddenSealIdentity()
    {
        var fixture = CreateFixture(
            "combat-seal-privacy",
            board:
            [
                Board("privacy-attacker", PlainEntityCardId, "player_1", DomainRow.Horizon, 0, "active", 1),
            ]);
        var hiddenSealInstanceIds = fixture.State.Players
            .SelectMany(player => player.SealSlots)
            .Where(slot => slot.CardInstanceId is not null)
            .Select(slot => slot.CardInstanceId!)
            .ToArray();
        var action = AttackAction(fixture, "player_1");
        var schemaJson = action.PayloadSchema.GetRawText();
        False(hiddenSealInstanceIds.Any(schemaJson.Contains), "Attack action payload leaked a hidden Seal instance.");

        var response = SubmitAttack(
            fixture,
            action,
            "privacy-attack",
            "privacy-attacker",
            CombatRuleIds.SealSlotTargetKind,
            "seal:player_2:01");
        True(response.Accepted, "Public SealSlot attack declaration failed.");
        var publicResponse = JsonSerializer.Serialize(response);
        False(hiddenSealInstanceIds.Any(publicResponse.Contains), "Attack events leaked a hidden Seal instance.");

        var playerOne = fixture.Session.GetPlayerSnapshot("player_1");
        var playerTwo = fixture.Session.GetPlayerSnapshot("player_2");
        Equal(ContractSchemas.DomainBoardProjectionWithCombat, playerOne.BoardSummary.GetProperty("schema_version").GetString(),
            "Combat board projection schema is invalid.");
        Equal(playerOne.BoardSummary.GetRawText(), playerTwo.BoardSummary.GetRawText(),
            "Public Combat projection differs by viewer.");
        var publicProjection = playerOne.BoardSummary.GetRawText();
        False(hiddenSealInstanceIds.Any(publicProjection.Contains), "Combat projection leaked a hidden Seal instance.");
        var target = playerOne.BoardSummary.GetProperty("pending_combat").GetProperty("original_target");
        Equal(CombatRuleIds.SealSlotTargetKind, target.GetProperty("target_kind_id").GetString(), "Projected Seal target kind is invalid.");
        Equal("seal:player_2:01", target.GetProperty("target_id").GetString(), "Projected SealSlotId is invalid.");
        False(target.TryGetProperty("entity_ref", out _), "Seal target projection exposed an Entity reference.");
        var debugCombat = NotNull(fixture.Session.GetDebugSnapshot().PendingCombat,
            "Debug snapshot lost authoritative Combat state.");
        Equal("combat:combat-seal-privacy:000001", debugCombat.CombatId, "Debug Combat identity is invalid.");
        True(debugCombat.AttackCommitted, "Debug Combat projection lost AttackCommit authority.");
        True(
            fixture.Session.GetDebugSnapshot().Players.SelectMany(player => player.SealSlots)
                .All(slot => slot.Status == "broken" || slot.CardInstanceId is not null),
            "Authoritative debug projection lost hidden Seal identity.");
    }

    internal static void CombatStateRejectsMalformedTypedContinuation()
    {
        var fixture = CreateFixture(
            "combat-invariant",
            board:
            [
                Board("invariant-attacker", PlainEntityCardId, "player_1", DomainRow.Horizon, 0, "active", 1),
                Board("invariant-target", PlainEntityCardId, "player_2", DomainRow.Horizon, 0, "active", 1),
            ]);
        True(SubmitAttack(
            fixture,
            AttackAction(fixture, "player_1"),
            "invariant-attack",
            "invariant-attacker",
            CombatRuleIds.EntityTargetKind,
            "invariant-target").Accepted, "Invariant fixture attack failed.");
        var bottom = Single(fixture.State.ResolutionStack);
        fixture.State.ResolutionStack[0] = new ResolutionStackEntryState
        {
            ResolutionId = bottom.ResolutionId,
            Sequence = bottom.Sequence,
            EntryKindId = bottom.EntryKindId,
            ReactionWindowId = bottom.ReactionWindowId,
            ReactionSubjectId = bottom.ReactionSubjectId,
            ParentResolutionId = bottom.ParentResolutionId,
            AbilityResolution = new CanonicalAbilityResolutionState(
                "invalid-combat-overlap",
                null,
                "attack",
                ReactionAbilityId,
                "invariant-attacker",
                PlainEntityCardId,
                "dominion",
                1,
                ReactionPolicyIds.SameZonePresence,
                "player_1",
                ImmutableArray<CanonicalTargetSelectionPayload>.Empty,
                ImmutableArray<DeclaredTargetSelectionState>.Empty,
                null,
                null,
                1),
            CombatContinuation = bottom.CombatContinuation,
        };
        ThrowsState(
            () => EngineSession.ValidateState(fixture.State, fixture.CanonicalCards, fixture.CanonicalAbilities),
            "payload",
            "Combat continuation accepted overlapping ability and continuation payloads.");
    }

    internal static void RepeatedCombatProtocolIsDeterministic()
    {
        static string Run()
        {
            var fixture = CreateFixture(
                "combat-repeated",
                board:
                [
                    Board("repeat-attacker", PlainEntityCardId, "player_1", DomainRow.Horizon, 4, "active", 1),
                ]);
            True(SubmitAttack(
                fixture,
                AttackAction(fixture, "player_1"),
                "repeat-attack",
                "repeat-attacker",
                CombatRuleIds.SealSlotTargetKind,
                "seal:player_2:03").Accepted, "Repeated attack declaration failed.");
            True(Pass(fixture, "player_2", "repeat-pass-one").Accepted, "Repeated first pass failed.");
            True(Pass(fixture, "player_1", "repeat-pass-two").Accepted, "Repeated second pass failed.");
            return Fingerprint(fixture);
        }

        Equal(Run(), Run(), "Repeated Combat protocol is not deterministic.");
    }

    internal static void InterventionCandidatesUseLinearAdjacentOwnActiveHorizonEntities()
    {
        var both = CreateFixture(
            "combat-intervention-adjacency",
            board:
            [
                Board("adj-attacker", PlainEntityCardId, "player_1", DomainRow.Horizon, 5, "active", 1),
                Board("foreign-neighbor", PlainEntityCardId, "player_1", DomainRow.Horizon, 1, "active", 1),
                Board("adj-left", PlainEntityCardId, "player_2", DomainRow.Horizon, 1, "active", 1),
                Board("adj-target", PlainEntityCardId, "player_2", DomainRow.Horizon, 2, "active", 1),
                Board("adj-right", PlainEntityCardId, "player_2", DomainRow.Horizon, 3, "active", 1),
                Board("adj-far", PlainEntityCardId, "player_2", DomainRow.Horizon, 5, "active", 1),
            ]);
        OpenInterventionChoice(
            both,
            "adj-attacker",
            CombatRuleIds.EntityTargetKind,
            "adj-target",
            "adj");
        SequenceEqual(
            ["adj-left", "adj-right"],
            InterventionCandidateIds(both),
            "Both linear adjacent defender candidates were not exposed deterministically.");
        False(InterventionCandidateIds(both).Contains("foreign-neighbor"),
            "An attacker-owned Entity became a defender candidate.");
        False(InterventionCandidateIds(both).Contains("adj-far"),
            "A non-adjacent Entity became a defender candidate.");
        var summary = both.Session.GetPlayerSnapshot("player_2").PendingDecisionSummary;
        Equal("combat", summary.GetProperty("pending_type").GetString(), "Intervention projection lost Combat pending type.");
        Equal(CombatRuleIds.InterventionChoiceStage, summary.GetProperty("stage").GetString(),
            "Intervention projection stage is invalid.");
        Equal("player_2", summary.GetProperty("current_player_id").GetString(),
            "Intervention projection did not identify the defending decision player.");
        True(summary.GetProperty("decline_intervention_available").GetBoolean(),
            "Intervention projection omitted decline availability.");

        var laneOne = CreateFixture(
            "combat-intervention-lane-one",
            board:
            [
                Board("lane-one-attacker", PlainEntityCardId, "player_1", DomainRow.Horizon, 3, "active", 1),
                Board("lane-one-target", PlainEntityCardId, "player_2", DomainRow.Horizon, 0, "active", 1),
                Board("lane-one-adjacent", PlainEntityCardId, "player_2", DomainRow.Horizon, 1, "active", 1),
                Board("lane-one-wrap", PlainEntityCardId, "player_2", DomainRow.Horizon, 5, "active", 1),
            ]);
        OpenInterventionChoice(laneOne, "lane-one-attacker", CombatRuleIds.EntityTargetKind, "lane-one-target", "lane-one");
        SequenceEqual(["lane-one-adjacent"], InterventionCandidateIds(laneOne),
            "Lane 1 did not expose only lane 2.");

        var laneSix = CreateFixture(
            "combat-intervention-lane-six",
            board:
            [
                Board("lane-six-attacker", PlainEntityCardId, "player_1", DomainRow.Horizon, 2, "active", 1),
                Board("lane-six-wrap", PlainEntityCardId, "player_2", DomainRow.Horizon, 0, "active", 1),
                Board("lane-six-adjacent", PlainEntityCardId, "player_2", DomainRow.Horizon, 4, "active", 1),
                Board("lane-six-target", PlainEntityCardId, "player_2", DomainRow.Horizon, 5, "active", 1),
            ]);
        OpenInterventionChoice(laneSix, "lane-six-attacker", CombatRuleIds.EntityTargetKind, "lane-six-target", "lane-six");
        SequenceEqual(["lane-six-adjacent"], InterventionCandidateIds(laneSix),
            "Lane 6 did not expose only lane 5, or incorrectly wrapped to lane 1.");

        var none = CreateFixture(
            "combat-intervention-none",
            board:
            [
                Board("none-attacker", PlainEntityCardId, "player_1", DomainRow.Horizon, 5, "active", 1),
                Board("none-exhausted", PlainEntityCardId, "player_2", DomainRow.Horizon, 1, "exhausted", 1),
                Board("none-target", PlainEntityCardId, "player_2", DomainRow.Horizon, 2, "active", 1),
                Board("none-zenith", PlainEntityCardId, "player_2", DomainRow.Zenith, 3, "active", 1),
            ]);
        var noneResponse = CloseFirstCombatReaction(
            none,
            "none-attacker",
            CombatRuleIds.EntityTargetKind,
            "none-target",
            "none");
        Equal(null, none.State.PendingCombat,
            "No-candidate Entity Combat did not resolve immediately.");
        False(none.Session.ListLegalActions("player_2", includeDisabled: true).Actions
            .Any(action => action.ActionType is "intervene" or "decline_intervention"),
            "No-candidate Combat exposed intervention actions.");
        True(noneResponse.Events.Any(engineEvent => engineEvent.EventType == "combat_resolved"),
            "No-candidate Combat omitted its resolution event.");
    }

    internal static void InterventionRequiresMatchingAerialContact()
    {
        static ImmutableArray<string> Candidates(
            string matchId,
            string attackerCardId,
            string defenderCardId)
        {
            var fixture = CreateFixture(
                matchId,
                board:
                [
                    Board($"{matchId}-attacker", attackerCardId, "player_1", DomainRow.Horizon, 5, "active", 1),
                    Board($"{matchId}-defender", defenderCardId, "player_2", DomainRow.Horizon, 1, "active", 1),
                    Board($"{matchId}-target", PlainEntityCardId, "player_2", DomainRow.Horizon, 2, "active", 1),
                ]);
            CloseFirstCombatReaction(
                fixture,
                $"{matchId}-attacker",
                CombatRuleIds.EntityTargetKind,
                $"{matchId}-target",
                matchId);
            return fixture.State.PendingCombat?.StageId == CombatRuleIds.InterventionChoiceStage
                ? InterventionCandidateIds(fixture)
                : ImmutableArray<string>.Empty;
        }

        SequenceEqual(["air-ground-defender"],
            Candidates("air-ground", PlainEntityCardId, PlainEntityCardId),
            "Ground attacker could not use a ground defender.");
        SequenceEqual(Array.Empty<string>(),
            Candidates("ground-aerial", PlainEntityCardId, AerialEntityCardId),
            "Ground attacker accepted an Aerial defender.");
        SequenceEqual(["aerial-aerial-defender"],
            Candidates("aerial-aerial", AerialEntityCardId, AerialEntityCardId),
            "Aerial attacker could not use an Aerial defender.");
        SequenceEqual(Array.Empty<string>(),
            Candidates("aerial-ground", AerialEntityCardId, PlainEntityCardId),
            "Aerial attacker accepted a ground defender.");
    }

    internal static void AttackCheckpointUsesCommitRestrictionsAndContinuityOnly()
    {
        var ward = CreateFixture(
            "combat-intervention-ward",
            board:
            [
                Board("ward-c3-attacker", PlainEntityCardId, "player_1", DomainRow.Horizon, 5, "active", 1),
                Board("ward-c3-defender", PlainEntityCardId, "player_2", DomainRow.Horizon, 1, "active", 1),
                Board("ward-c3-target", WardEntityCardId, "player_2", DomainRow.Horizon, 2, "active", 1),
            ]);
        SubmitInitialAttack(
            ward,
            "ward-c3-attacker",
            CombatRuleIds.EntityTargetKind,
            "ward-c3-target",
            "ward-c3");
        True(ward.State.PendingCombat?.OriginalTargetHadWardAtAttackCommit == true,
            "Ward target commitment was not retained.");
        var wardClosure = CloseOpenReaction(ward, "ward-c3");
        Equal(null, ward.State.PendingCombat, "Ward Entity Combat did not resolve.");
        False(wardClosure.Events.Any(engineEvent => engineEvent.EventType == "intervention_choice_opened"),
            "Ward OriginalTarget opened normal intervention.");

        var aeternal = CreateFixture(
            "combat-intervention-aeternal",
            playerTwoSealsBroken: true,
            board:
            [
                Board("aeternal-c3-attacker", PlainEntityCardId, "player_1", DomainRow.Horizon, 2, "active", 1),
                Board("aeternal-c3-defender", PlainEntityCardId, "player_2", DomainRow.Horizon, 1, "active", 1),
            ]);
        CloseFirstCombatReaction(
            aeternal,
            "aeternal-c3-attacker",
            CombatRuleIds.AeternalTargetKind,
            "aeternal:player_2",
            "aeternal-c3");
        True(aeternal.State.Result.Completed,
            "Aeternal attack did not bypass normal intervention and resolve through C6.");
        True(aeternal.State.Events.All(engineEvent =>
                engineEvent.EventType != "intervention_choice_opened"),
            "Aeternal attack opened normal intervention.");

        var lostTarget = CreateFixture(
            "combat-intervention-target-lost",
            board:
            [
                Board("lost-target-attacker", PlainEntityCardId, "player_1", DomainRow.Horizon, 5, "active", 1),
                Board("lost-target-defender", PlainEntityCardId, "player_2", DomainRow.Horizon, 1, "active", 1),
                Board("lost-target-original", PlainEntityCardId, "player_2", DomainRow.Horizon, 2, "active", 1),
            ]);
        SubmitInitialAttack(
            lostTarget,
            "lost-target-attacker",
            CombatRuleIds.EntityTargetKind,
            "lost-target-original",
            "lost-target");
        MoveDomainCardToVoid(lostTarget, "lost-target-original");
        var lostTargetClosure = CloseOpenReaction(lostTarget, "lost-target");
        Equal(CombatRuleIds.AttackContinuityTargetLost,
            CombatCheckpointContinuity(lostTargetClosure),
            "OriginalTarget leave-and-return continuity loss was not explicit.");
        Equal(null, lostTarget.State.PendingCombat, "Lost OriginalTarget did not close as no-hit.");
        Equal(CombatRuleIds.TargetMissingNoHitReason, NoHitReason(lostTargetClosure),
            "Lost OriginalTarget no-hit reason is invalid.");

        var movedTarget = CreateFixture(
            "combat-intervention-target-moved",
            board:
            [
                Board("moved-target-attacker", PlainEntityCardId, "player_1", DomainRow.Horizon, 5, "active", 1),
                Board("moved-target-defender", PlainEntityCardId, "player_2", DomainRow.Horizon, 1, "active", 1),
                Board("moved-target-original", PlainEntityCardId, "player_2", DomainRow.Horizon, 2, "active", 1),
            ]);
        SubmitInitialAttack(
            movedTarget,
            "moved-target-attacker",
            CombatRuleIds.EntityTargetKind,
            "moved-target-original",
            "moved-target");
        MoveDomainCardWithinDomain(movedTarget, "moved-target-original", DomainRow.Zenith, 3);
        var movedTargetClosure = CloseOpenReaction(movedTarget, "moved-target");
        Equal(CombatRuleIds.AttackContinuityTargetLost,
            CombatCheckpointContinuity(movedTargetClosure),
            "OriginalTarget row/lane continuity change was not detected.");
        Equal(CombatRuleIds.TargetMissingNoHitReason, NoHitReason(movedTargetClosure),
            "Moved OriginalTarget did not produce target-missing no-hit.");

        var lostAttacker = CreateFixture(
            "combat-intervention-attacker-lost",
            board:
            [
                Board("lost-attacker-original", PlainEntityCardId, "player_1", DomainRow.Horizon, 5, "active", 1),
                Board("lost-attacker-defender", PlainEntityCardId, "player_2", DomainRow.Horizon, 1, "active", 1),
                Board("lost-attacker-target", PlainEntityCardId, "player_2", DomainRow.Horizon, 2, "active", 1),
            ]);
        SubmitInitialAttack(
            lostAttacker,
            "lost-attacker-original",
            CombatRuleIds.EntityTargetKind,
            "lost-attacker-target",
            "lost-attacker");
        MoveDomainCardToVoid(lostAttacker, "lost-attacker-original");
        var lostAttackerClosure = CloseOpenReaction(lostAttacker, "lost-attacker");
        Equal(CombatRuleIds.AttackContinuityAttackerLost,
            CombatCheckpointContinuity(lostAttackerClosure),
            "Attacker incarnation continuity loss was not explicit.");
        Equal(CombatRuleIds.AttackerMissingNoHitReason, NoHitReason(lostAttackerClosure),
            "Lost attacker did not produce attacker-missing no-hit.");

        var declarationOnly = CreateFixture(
            "combat-intervention-declaration-only",
            board:
            [
                Board("declaration-attacker", PlainEntityCardId, "player_1", DomainRow.Horizon, 5, "active", 1),
                Board("declaration-defender", PlainEntityCardId, "player_2", DomainRow.Horizon, 1, "active", 1),
                Board("declaration-target", PlainEntityCardId, "player_2", DomainRow.Horizon, 2, "active", 1),
            ]);
        SubmitInitialAttack(
            declarationOnly,
            "declaration-attacker",
            CombatRuleIds.EntityTargetKind,
            "declaration-target",
            "declaration-only");
        declarationOnly.State.GetCardInstance("declaration-attacker").ActivityState = "active";
        CloseOpenReaction(declarationOnly, "declaration-only");
        Equal(CombatRuleIds.AttackContinuityContinuous,
            declarationOnly.State.PendingCombat?.AttackContinuityStateId,
            "Attack checkpoint incorrectly reapplied declaration-time activity legality.");
        Equal(CombatRuleIds.InterventionChoiceStage, declarationOnly.State.PendingCombat?.StageId,
            "A declaration-only state change canceled the intervention opportunity.");
    }

    internal static void InterventionActionsAreDefenderOnlyExactAndAtomic()
    {
        var fixture = CreateInterventionFixture("combat-intervention-actions");
        OpenInterventionChoice(
            fixture,
            "combat-intervention-actions-attacker",
            CombatRuleIds.EntityTargetKind,
            "combat-intervention-actions-target",
            "actions");
        var action = InterventionAction(fixture, "player_2");
        SequenceEqual(["combat-intervention-actions-defender"],
            action.PayloadSchema.GetProperty("properties")
                .GetProperty("defender_card_instance_id")
                .GetProperty("enum")
                .EnumerateArray()
                .Select(item => item.GetString()!),
            "Intervene payload schema did not expose only public defender IDs.");
        var attackerAction = InterventionAction(fixture, "player_1", includeDisabled: true);
        False(attackerAction.Enabled, "Attacking player received intervention authority.");
        Equal("not_defending_player", attackerAction.DisabledReason,
            "Attacker intervention disabled reason is unstable.");
        var attackerDecline = fixture.Session.ListLegalActions("player_1", includeDisabled: true).Actions
            .Single(item => item.ActionType == "decline_intervention");
        False(attackerDecline.Enabled, "Attacking player received decline_intervention authority.");
        Equal("not_defending_player", attackerDecline.DisabledReason,
            "Attacker decline disabled reason is unstable.");

        var before = Fingerprint(fixture);
        var malformed = SubmitCombatAction(
            fixture,
            action,
            "malformed-intervene",
            ContractJsonValue.From(new Dictionary<string, object?>
            {
                ["defender_card_instance_id"] = "combat-intervention-actions-defender",
                ["lane_index"] = 1,
            }));
        False(malformed.Accepted, "Intervene accepted a client-derived lane field.");
        Equal(before, Fingerprint(fixture), "Malformed intervene mutated state.");

        var stale = SubmitCombatAction(
            fixture,
            action,
            "stale-intervene",
            ContractJsonValue.From(new Dictionary<string, object?>
            {
                ["defender_card_instance_id"] = "combat-intervention-actions-defender",
            }),
            expectedStateVersion: -1);
        False(stale.Accepted, "Stale intervene was accepted.");
        Equal(before, Fingerprint(fixture), "Stale intervene mutated state.");

        var illegal = SubmitCombatAction(
            fixture,
            action,
            "illegal-intervene",
            ContractJsonValue.From(new Dictionary<string, object?>
            {
                ["defender_card_instance_id"] = "unknown-defender",
            }));
        False(illegal.Accepted, "Unknown defender was accepted.");
        Equal(before, Fingerprint(fixture), "Illegal defender selection mutated state.");

        var attackerAttempt = SubmitCombatAction(
            fixture,
            attackerAction,
            "attacker-intervene",
            ContractJsonValue.From(new Dictionary<string, object?>
            {
                ["defender_card_instance_id"] = "combat-intervention-actions-defender",
            }));
        False(attackerAttempt.Accepted, "Attacking player intervened.");
        Equal(before, Fingerprint(fixture), "Attacker intervention attempt mutated state.");
    }

    internal static void DeclineInterventionAdvancesWithoutDefenseCommit()
    {
        var fixture = CreateInterventionFixture("combat-intervention-decline");
        OpenInterventionChoice(
            fixture,
            "combat-intervention-decline-attacker",
            CombatRuleIds.EntityTargetKind,
            "combat-intervention-decline-target",
            "decline");
        var defender = fixture.State.GetCardInstance("combat-intervention-decline-defender");
        var action = DeclineAction(fixture, "player_2");
        var beforeMalformed = Fingerprint(fixture);
        var malformed = SubmitCombatAction(
            fixture,
            action,
            "decline-with-payload",
            ContractJsonValue.From(new Dictionary<string, object?> { ["unexpected"] = true }));
        False(malformed.Accepted, "decline_intervention accepted a non-empty payload.");
        Equal(beforeMalformed, Fingerprint(fixture), "Malformed decline mutated state.");

        var response = SubmitCombatAction(
            fixture,
            action,
            "decline-intervention",
            ContractJsonValue.EmptyObject());
        True(response.Accepted, "Legal decline_intervention failed.");
        Equal("active", defender.ActivityState, "Decline exhausted a defender.");
        Equal(null, fixture.State.PendingCombat, "Declined Entity Combat remained pending after resolution.");
        Equal(null, fixture.State.ReactionWindow, "Decline opened a defense ReactionWindow.");
        Equal(0, fixture.State.ResolutionStack.Count, "Declined Combat retained a continuation.");
        True(response.Events.First().EventType == "intervention_declined",
            "Decline semantic event is missing.");
        True(response.Events.Any(engineEvent => engineEvent.EventType == "combat_damage_committed"),
            "Declined Entity Combat did not enter simultaneous damage.");
        True(response.Events.Any(engineEvent => engineEvent.EventType == "combat_resolved"),
            "Declined Entity Combat did not close.");
    }

    internal static void DefenseCommitIsAtomicBoundAndOpensSecondReactionWindow()
    {
        var fixture = CreateInterventionFixture("combat-defense-commit", defenderZoneSequence: 9);
        OpenInterventionChoice(
            fixture,
            "combat-defense-commit-attacker",
            CombatRuleIds.EntityTargetKind,
            "combat-defense-commit-target",
            "defense-commit");
        var combatBefore = NotNull(fixture.State.PendingCombat, "DefenseCommit fixture lost Combat.");
        var originalTargetId = combatBefore.OriginalTarget.PublicTargetId;
        var originalTargetRef = combatBefore.OriginalTarget.EntityRef;
        var stateVersionBefore = fixture.State.StateVersion;
        var action = InterventionAction(fixture, "player_2");
        var response = SubmitIntervene(
            fixture,
            action,
            "defense-commit-intervene",
            "combat-defense-commit-defender");
        True(response.Accepted, "Legal intervention failed.");
        Equal(stateVersionBefore + 1, fixture.State.StateVersion,
            "DefenseCommit did not advance state exactly once.");
        SequenceEqual(
            ["defender_intervened", "defender_exhausted", "reaction_window_opened"],
            response.Events.Select(engineEvent => engineEvent.EventType),
            "DefenseCommit event order is invalid.");
        True(response.Events.All(engineEvent => engineEvent.StateVersion == fixture.State.StateVersion),
            "DefenseCommit events split across state versions.");

        var combat = NotNull(fixture.State.PendingCombat, "DefenseCommit removed PendingCombat.");
        Equal(CombatRuleIds.DefenseReactionStage, combat.StageId, "DefenseCommit stage is invalid.");
        Equal(4, combat.StageSequence, "DefenseCommit stage sequence is invalid.");
        True(combat.DefenseCommitted, "DefenseCommit flag was not set.");
        Equal(CombatRuleIds.DefenseDecisionCommitted, combat.DefenseDecisionStateId,
            "Defense decision did not become committed.");
        Equal("combat-defense-commit-defender", combat.DefenderRef?.ObjectId,
            "DefenderRef did not bind the selected Entity.");
        Equal(9, combat.DefenderRef?.IncarnationSequence, "Defender incarnation was not bound.");
        Equal(1, combat.DefenderLaneAtCommit, "Defender lane-at-commit is invalid.");
        Equal(fixture.State.StateVersion, combat.DefenseCommitStateVersion,
            "DefenseCommit state version is invalid.");
        Equal("combat:combat-defense-commit:000001:defense_commit", combat.DefenseTimingAnchorId,
            "Defense timing anchor is not deterministic.");
        Equal("exhausted", fixture.State.GetCardInstance("combat-defense-commit-defender").ActivityState,
            "DefenseCommit did not exhaust the defender.");
        Equal(originalTargetId, combat.OriginalTarget.PublicTargetId,
            "DefenseCommit replaced OriginalTarget.");
        Equal(originalTargetRef, combat.OriginalTarget.EntityRef,
            "DefenseCommit rewrote OriginalTarget binding.");

        var bottom = Single(fixture.State.ResolutionStack);
        Equal(CombatRuleIds.CombatContinuationEntryKind, bottom.EntryKindId,
            "Defense continuation is not a typed Combat bottom entry.");
        Equal(null, bottom.AbilityResolution, "Defense continuation used a fake ability.");
        var continuation = NotNull(bottom.CombatContinuation, "Defense continuation payload is missing.");
        Equal(combat.CombatId, continuation.CombatId, "Defense continuation CombatId is inconsistent.");
        Equal(CombatRuleIds.DefenseReactionStage, continuation.CombatStageId,
            "Defense continuation stage is inconsistent.");
        Equal(CombatRuleIds.AfterDefenseReactionResumePoint, continuation.ResumePointId,
            "Defense continuation resume point is invalid.");
        var window = NotNull(fixture.State.ReactionWindow, "Second Combat ReactionWindow was not opened.");
        Equal(bottom.ResolutionId, window.UnderlyingResolutionId,
            "Second ReactionWindow does not bind the defense continuation.");
        Equal(CombatRuleIds.DefenseReactionProfile, window.ReactionProfileId,
            "Second ReactionWindow profile is invalid.");
        Equal("player_2", window.InitiatorPlayerId, "Defender is not the second window initiator.");
        Equal("player_1", fixture.State.PriorityPlayerId,
            "Attacker did not receive first priority after DefenseCommit.");
        True(response.Events.All(engineEvent =>
            engineEvent.Payload.GetRawText().Contains(combat.DefenseTimingAnchorId!, StringComparison.Ordinal)),
            "DefenseCommit events do not share the DefenseTimingAnchor.");
        EngineSession.ValidateState(fixture.State, fixture.CanonicalCards, fixture.CanonicalAbilities);

        var invalid = CreateInterventionFixture("combat-defense-continuation-invalid");
        OpenInterventionChoice(
            invalid,
            "combat-defense-continuation-invalid-attacker",
            CombatRuleIds.EntityTargetKind,
            "combat-defense-continuation-invalid-target",
            "defense-invalid");
        True(SubmitIntervene(
            invalid,
            InterventionAction(invalid, "player_2"),
            "defense-invalid-intervene",
            "combat-defense-continuation-invalid-defender").Accepted,
            "Defense continuation invariant fixture could not commit.");
        var invalidBottom = Single(invalid.State.ResolutionStack);
        invalid.State.ResolutionStack[0] = new ResolutionStackEntryState
        {
            ResolutionId = invalidBottom.ResolutionId,
            Sequence = invalidBottom.Sequence,
            EntryKindId = invalidBottom.EntryKindId,
            ReactionWindowId = invalidBottom.ReactionWindowId,
            ReactionSubjectId = invalidBottom.ReactionSubjectId,
            ParentResolutionId = null,
            AbilityResolution = null,
            CombatContinuation = invalidBottom.CombatContinuation! with
            {
                ResumePointId = CombatRuleIds.AfterAttackReactionResumePoint,
            },
        };
        ThrowsState(
            () => EngineSession.ValidateState(invalid.State, invalid.CanonicalCards, invalid.CanonicalAbilities),
            "continuation",
            "Defense stage accepted an attack-reaction continuation.");
    }

    internal static void SecondCombatReactionPreservesReactPassLifoAndClosesAtDefenseCheckpoint()
    {
        var fixture = CreateFixture(
            "combat-defense-reaction-lifo",
            board:
            [
                Board("defense-lifo-attacker", PlainEntityCardId, "player_1", DomainRow.Horizon, 5, "active", 1),
                Board("defense-lifo-p1-target", PlainEntityCardId, "player_1", DomainRow.Horizon, 4, "active", 1),
                Board("defense-lifo-p1-source", ReactionEntityCardId, "player_1", DomainRow.Zenith, 0, "active", 1),
                Board("defense-lifo-defender", PlainEntityCardId, "player_2", DomainRow.Horizon, 1, "active", 1),
                Board("defense-lifo-target", PlainEntityCardId, "player_2", DomainRow.Horizon, 2, "active", 1),
                Board("defense-lifo-p2-target", PlainEntityCardId, "player_2", DomainRow.Horizon, 3, "active", 1),
                Board("defense-lifo-p2-source", ReactionEntityCardId, "player_2", DomainRow.Zenith, 4, "active", 1),
            ]);
        OpenInterventionChoice(
            fixture,
            "defense-lifo-attacker",
            CombatRuleIds.EntityTargetKind,
            "defense-lifo-target",
            "defense-lifo");
        True(SubmitIntervene(
            fixture,
            InterventionAction(fixture, "player_2"),
            "defense-lifo-intervene",
            "defense-lifo-defender").Accepted,
            "Defense LIFO fixture could not intervene.");
        Equal("reaction_window",
            fixture.Session.GetPlayerSnapshot("player_1").PendingDecisionSummary
                .GetProperty("pending_type").GetString(),
            "Second ReactionWindow did not take projection precedence over Combat.");

        var firstReaction = React(
            fixture,
            "player_1",
            "defense-lifo-p1-source",
            "defense-lifo-p2-target",
            "defense-lifo-react-one");
        True(firstReaction.Accepted, "Attacker reaction in second window failed.");
        var firstResolutionId = firstReaction.Events.Single(engineEvent => engineEvent.EventType == "reaction_declared")
            .Payload.GetProperty("resolution_id").GetString()!;
        var secondReaction = React(
            fixture,
            "player_2",
            "defense-lifo-p2-source",
            "defense-lifo-p1-target",
            "defense-lifo-react-two");
        True(secondReaction.Accepted, "Defender response in second window failed.");
        var secondResolutionId = secondReaction.Events.Single(engineEvent => engineEvent.EventType == "reaction_declared")
            .Payload.GetProperty("resolution_id").GetString()!;
        var continuationId = fixture.State.ResolutionStack[0].ResolutionId;

        True(Pass(fixture, "player_1", "defense-lifo-pass-one").Accepted,
            "First second-window pass failed.");
        var closure = Pass(fixture, "player_2", "defense-lifo-pass-two");
        True(closure.Accepted, "Second ReactionWindow closure failed.");
        SequenceEqual(
            [secondResolutionId, firstResolutionId, continuationId],
            closure.Events.Where(engineEvent => engineEvent.EventType == "resolution_entry_resolved")
                .Select(engineEvent => engineEvent.Payload.GetProperty("resolution_id").GetString()!),
            "Second Combat reactions did not resolve LIFO above the continuation.");
        Equal(null, fixture.State.ReactionWindow, "Second ReactionWindow remained open.");
        Equal(0, fixture.State.ResolutionStack.Count, "Defense continuation remained on the stack.");
        Equal(null, fixture.State.PendingCombat, "Second window closure did not finish Entity Combat.");
        True(closure.Events.Any(engineEvent => engineEvent.EventType == "combat_defense_reaction_completed"),
            "Defense reaction completion event is missing.");
        True(closure.Events.Any(engineEvent => engineEvent.EventType == "combat_resolved"),
            "Second window closure omitted Combat resolution.");
        Equal("dominion", fixture.State.GetCardInstance("defense-lifo-target").Zone,
            "Committed defense incorrectly damaged OriginalTarget.");
        True(fixture.Session.ListLegalActions("player_1").Actions.Any(action => action.Enabled),
            "Normal gameplay did not resume after defended Entity Combat.");
    }

    internal static void DefenseCommitContinuityAndProjectionRemainViewerSafe()
    {
        var defenderGone = CreateInterventionFixture("combat-defense-gone");
        OpenInterventionChoice(
            defenderGone,
            "combat-defense-gone-attacker",
            CombatRuleIds.EntityTargetKind,
            "combat-defense-gone-target",
            "defender-gone");
        True(SubmitIntervene(
            defenderGone,
            InterventionAction(defenderGone, "player_2"),
            "defender-gone-intervene",
            "combat-defense-gone-defender").Accepted,
            "Defender-disappearance fixture could not commit.");
        MoveDomainCardToVoid(defenderGone, "combat-defense-gone-defender");
        var defenderGoneClosure = CloseOpenReaction(defenderGone, "defender-gone");
        Equal(null, defenderGone.State.PendingCombat, "Defender disappearance did not close Combat.");
        Equal(CombatRuleIds.DefenderMissingNoHitReason, NoHitReason(defenderGoneClosure),
            "Defender disappearance did not produce committed no-hit.");
        Equal(0, defenderGoneClosure.Events.Count(engineEvent => engineEvent.EventType == "damage_dealt"),
            "Missing defender no-hit dealt Combat damage.");
        Equal("dominion", defenderGone.State.GetCardInstance("combat-defense-gone-target").Zone,
            "Missing defender resumed damage against OriginalTarget.");

        var targetGone = CreateInterventionFixture("combat-original-target-gone");
        OpenInterventionChoice(
            targetGone,
            "combat-original-target-gone-attacker",
            CombatRuleIds.EntityTargetKind,
            "combat-original-target-gone-target",
            "target-gone-after-defense");
        True(SubmitIntervene(
            targetGone,
            InterventionAction(targetGone, "player_2"),
            "target-gone-after-defense-intervene",
            "combat-original-target-gone-defender").Accepted,
            "OriginalTarget-disappearance fixture could not commit.");
        MoveDomainCardToVoid(targetGone, "combat-original-target-gone-target");
        var targetGoneClosure = CloseOpenReaction(targetGone, "target-gone-after-defense");
        Equal(null, targetGone.State.PendingCombat,
            "OriginalTarget disappearance prevented defended Combat closure.");
        True(targetGoneClosure.Events.Any(engineEvent => engineEvent.EventType == "combat_damage_committed"),
            "Valid defender did not fight after OriginalTarget disappeared.");
        True(targetGoneClosure.Events.Where(engineEvent => engineEvent.EventType == "damage_dealt")
            .Any(engineEvent => engineEvent.Payload.GetProperty("entity_instance_id").GetString()
                == "combat-original-target-gone-defender"),
            "OriginalTarget disappearance erased the committed defender participant.");

        var privacy = CreateInterventionFixture("combat-intervention-privacy");
        OpenInterventionChoice(
            privacy,
            "combat-intervention-privacy-attacker",
            CombatRuleIds.EntityTargetKind,
            "combat-intervention-privacy-target",
            "intervention-privacy");
        var hiddenSealIds = privacy.State.Players.SelectMany(player => player.SealSlots)
            .Where(slot => slot.CardInstanceId is not null)
            .Select(slot => slot.CardInstanceId!)
            .ToArray();
        var actionJson = InterventionAction(privacy, "player_2").PayloadSchema.GetRawText();
        False(hiddenSealIds.Any(actionJson.Contains),
            "Intervention action leaked hidden Seal identity.");
        var playerOneProjection = privacy.Session.GetPlayerSnapshot("player_1").BoardSummary.GetRawText();
        var playerTwoProjection = privacy.Session.GetPlayerSnapshot("player_2").BoardSummary.GetRawText();
        Equal(playerOneProjection, playerTwoProjection,
            "Public intervention projection differs by viewer.");
        False(hiddenSealIds.Any(playerOneProjection.Contains),
            "Intervention projection leaked hidden Seal identity.");
        True(playerOneProjection.Contains("combat-intervention-privacy-defender", StringComparison.Ordinal),
            "Projection omitted the public defender candidate.");
    }

    internal static void UndefendedEntityCombatCommitsSimultaneousPersistentDamage()
    {
        var fixture = CreateFixture(
            "combat-c4-persistent",
            statOverrides: new Dictionary<string, (int Atk, int Hp)>
            {
                [PlainEntityCardId] = (1, 3),
            },
            board:
            [
                Board("persistent-attacker", PlainEntityCardId, "player_1", DomainRow.Horizon, 0, "active", 1),
                Board("persistent-target", PlainEntityCardId, "player_2", DomainRow.Horizon, 0, "exhausted", 1,
                    damageMarked: 1),
            ]);

        var response = CloseFirstCombatReaction(
            fixture,
            "persistent-attacker",
            CombatRuleIds.EntityTargetKind,
            "persistent-target",
            "persistent");

        Equal(null, fixture.State.PendingCombat, "Nonlethal Entity Combat remained pending.");
        Equal(0, fixture.State.ResolutionStack.Count, "Nonlethal Entity Combat retained a continuation.");
        Equal(null, fixture.State.ReactionWindow, "Nonlethal Entity Combat retained a ReactionWindow.");
        Equal(1, fixture.State.GetCardInstance("persistent-attacker").DamageMarked,
            "Target current ATK was not marked on the attacker.");
        Equal(2, fixture.State.GetCardInstance("persistent-target").DamageMarked,
            "Attacker current ATK did not accumulate on the exhausted target.");
        Equal("exhausted", fixture.State.GetCardInstance("persistent-attacker").ActivityState,
            "Combat cleanup refunded AttackCommit exhaustion.");
        Equal("exhausted", fixture.State.GetCardInstance("persistent-target").ActivityState,
            "An exhausted OriginalTarget did not remain a retaliating participant.");

        var commitment = response.Events.Single(engineEvent =>
            engineEvent.EventType == "combat_damage_committed").Payload;
        True(commitment.GetProperty("simultaneous").GetBoolean(),
            "Combat damage commitment is not explicitly simultaneous.");
        SequenceEqual(
            ["persistent-target", "persistent-attacker"],
            commitment.GetProperty("assignments").EnumerateArray().Select(assignment =>
                assignment.GetProperty("target_object_ref").GetProperty("object_id").GetString()!),
            "The simultaneous assignment order is not deterministic.");
        True(commitment.GetProperty("assignments").EnumerateArray().All(assignment =>
            assignment.GetProperty("current_effective_atk").GetInt32() == 1),
            "Combat did not use both current effective ATK values.");
        var damageEvents = response.Events.Where(engineEvent => engineEvent.EventType == "damage_dealt").ToArray();
        Equal(2, damageEvents.Length, "Physical Combat did not emit exactly two damage events.");
        Equal(1, damageEvents[0].Payload.GetProperty("accumulated_damage_before").GetInt32(),
            "Existing target damage was not part of the pre-damage snapshot.");
        Equal(0, damageEvents[1].Payload.GetProperty("accumulated_damage_before").GetInt32(),
            "Attacker pre-damage snapshot is invalid.");
        Equal(CombatRuleIds.EntityCombatResolvedOutcome,
            response.Events.Single(engineEvent => engineEvent.EventType == "combat_resolved")
                .Payload.GetProperty("outcome_id").GetString(),
            "Entity Combat outcome is invalid.");
        True(fixture.Session.ListLegalActions("player_1").Actions.Any(action => action.Enabled),
            "Normal gameplay did not resume after nonlethal Entity Combat.");
        EngineSession.ValidateState(fixture.State, fixture.CanonicalCards, fixture.CanonicalAbilities);
    }

    internal static void EntityCombatLethalOutcomesUseCanonicalAftermath()
    {
        static (CombatFixture Fixture, ActionResponse Response) Resolve(
            string matchId,
            string attackerCardId,
            string targetCardId,
            IReadOnlyDictionary<string, (int Atk, int Hp)> stats)
        {
            var fixture = CreateFixture(
                matchId,
                statOverrides: stats,
                board:
                [
                    Board($"{matchId}-attacker", attackerCardId, "player_1", DomainRow.Horizon, 0, "active", 1),
                    Board($"{matchId}-target", targetCardId, "player_2", DomainRow.Horizon, 0, "active", 1),
                ]);
            var response = CloseFirstCombatReaction(
                fixture,
                $"{matchId}-attacker",
                CombatRuleIds.EntityTargetKind,
                $"{matchId}-target",
                matchId);
            return (fixture, response);
        }

        var targetOnly = Resolve(
            "combat-c4-target-lethal",
            AerialEntityCardId,
            PlainEntityCardId,
            new Dictionary<string, (int Atk, int Hp)>
            {
                [AerialEntityCardId] = (2, 3),
                [PlainEntityCardId] = (1, 1),
            });
        Equal("dominion", targetOnly.Fixture.State.GetCardInstance("combat-c4-target-lethal-attacker").Zone,
            "Target-only lethal incorrectly destroyed the attacker.");
        Equal(1, targetOnly.Fixture.State.GetCardInstance("combat-c4-target-lethal-attacker").DamageMarked,
            "Target-only lethal lost return damage.");
        Equal("void", targetOnly.Fixture.State.GetCardInstance("combat-c4-target-lethal-target").Zone,
            "Target-only lethal did not use canonical destruction.");
        Equal(1, targetOnly.Response.Events.Count(engineEvent => engineEvent.EventType == "entity_destroyed"),
            "Target-only lethal emitted an invalid destruction count.");

        var attackerOnly = Resolve(
            "combat-c4-attacker-lethal",
            PlainEntityCardId,
            SpeedEntityCardId,
            new Dictionary<string, (int Atk, int Hp)>
            {
                [PlainEntityCardId] = (1, 1),
                [SpeedEntityCardId] = (2, 3),
            });
        Equal("void", attackerOnly.Fixture.State.GetCardInstance("combat-c4-attacker-lethal-attacker").Zone,
            "Attacker-only lethal did not destroy the attacker.");
        Equal("dominion", attackerOnly.Fixture.State.GetCardInstance("combat-c4-attacker-lethal-target").Zone,
            "Attacker-only lethal incorrectly destroyed the target.");
        Equal(1, attackerOnly.Fixture.State.GetCardInstance("combat-c4-attacker-lethal-target").DamageMarked,
            "Attacker-only lethal lost outgoing attacker damage.");

        var both = Resolve(
            "combat-c4-both-lethal",
            PlainEntityCardId,
            PlainEntityCardId,
            new Dictionary<string, (int Atk, int Hp)>
            {
                [PlainEntityCardId] = (1, 1),
            });
        Equal("void", both.Fixture.State.GetCardInstance("combat-c4-both-lethal-attacker").Zone,
            "Simultaneous lethal spared the attacker.");
        Equal("void", both.Fixture.State.GetCardInstance("combat-c4-both-lethal-target").Zone,
            "Simultaneous lethal spared the target.");
        Equal(2, both.Response.Events.Count(engineEvent => engineEvent.EventType == "damage_dealt"),
            "Both-lethal resolution failed to commit both damage assignments first.");
        Equal(2, both.Response.Events.Count(engineEvent => engineEvent.EventType == "entity_destroyed"),
            "Both-lethal resolution did not destroy both Entities.");
        Equal(2, both.Response.Events.Count(engineEvent => engineEvent.EventType == "card_zone_changed"),
            "Both-lethal resolution did not use two canonical zone transitions.");
        True(both.Fixture.State.GetPlayer("player_1").VoidCardInstanceIds
            .Contains("combat-c4-both-lethal-attacker"),
            "Destroyed attacker is absent from its owner's Void.");
        True(both.Fixture.State.GetPlayer("player_2").VoidCardInstanceIds
            .Contains("combat-c4-both-lethal-target"),
            "Destroyed target is absent from its owner's Void.");
        EngineSession.ValidateState(both.Fixture.State, both.Fixture.CanonicalCards, both.Fixture.CanonicalAbilities);
    }

    internal static void CombatUsesCurrentEffectiveAttackAfterCommit()
    {
        var fixture = CreateFixture(
            "combat-c4-current-atk",
            statOverrides: new Dictionary<string, (int Atk, int Hp)>
            {
                [PlainEntityCardId] = (1, 5),
                [SpeedEntityCardId] = (1, 5),
            },
            board:
            [
                Board("current-atk-attacker", PlainEntityCardId, "player_1", DomainRow.Horizon, 0, "active", 1),
                Board("current-atk-target", SpeedEntityCardId, "player_2", DomainRow.Horizon, 0, "active", 1),
            ]);
        var sourceOwner = fixture.State.GetPlayer("player_1");
        sourceOwner.HandCardInstanceIds.Add("current-atk-source");
        fixture.State.CardInstances.Add("current-atk-source", new CardInstanceState
        {
            CardInstanceId = "current-atk-source",
            CardId = "IGN-HAM-036",
            OwnerPlayerId = "player_1",
            ControllerPlayerId = "player_1",
            Zone = "hand",
            ZoneIndex = sourceOwner.HandCardInstanceIds.Count - 1,
            Visibility = "owner_only",
            CreatedSequence = fixture.State.CardInstances.Count + 1,
            ZoneSequence = 1,
            InitialZone = "hand",
        });
        Equal(1, CanonicalVitals.GetEffectiveAtk(
            fixture.State,
            fixture.State.GetCardInstance("current-atk-attacker"),
            fixture.CanonicalCards),
            "Current-ATK fixture base value is invalid.");
        SubmitInitialAttack(
            fixture,
            "current-atk-attacker",
            CombatRuleIds.EntityTargetKind,
            "current-atk-target",
            "current-atk");
        fixture.State.ModifierInstances.Add(
            "modifier_combat_c4_current_atk",
            new ModifierInstanceState(
                "modifier_combat_c4_current_atk",
                "ability_ign_ham_036_01",
                "effect_ign_ham_036_01_attack_bonus",
                "resolution_combat_c4_setup",
                "current-atk-source",
                "player_1",
                "current-atk-attacker",
                fixture.State.GetCardInstance("current-atk-attacker").ZoneSequence,
                CanonicalContinuousEffects.AttackModifierTypeId,
                CanonicalContinuousEffects.AttackFieldId,
                2,
                "duration_ign_ham_036_01_attack_bonus_turn",
                CanonicalContinuousEffects.UntilEndOfCurrentTurnDurationPolicyId,
                "duration_instance_combat_c4_current_atk",
                CanonicalContinuousEffects.TurnInstanceId(fixture.State),
                CanonicalContinuousEffects.PhaseInstanceId(fixture.State),
                fixture.State.TurnNumber,
                fixture.State.ActivePlayerId,
                fixture.State.StateVersion,
                1));
        fixture.State.NextContinuousEffectSequence = 2;
        Equal(3, CanonicalVitals.GetEffectiveAtk(
            fixture.State,
            fixture.State.GetCardInstance("current-atk-attacker"),
            fixture.CanonicalCards),
            "Commit-time modifier did not change current effective ATK.");

        var response = CloseOpenReaction(fixture, "current-atk");
        var attackerDamage = response.Events.Single(engineEvent =>
            engineEvent.EventType == "damage_dealt"
            && engineEvent.Payload.GetProperty("source_card_instance_id").GetString() == "current-atk-attacker");
        Equal(3, attackerDamage.Payload.GetProperty("applied_amount").GetInt32(),
            "Combat used declaration-time ATK instead of resolution-time effective ATK.");
        Equal(3, fixture.State.GetCardInstance("current-atk-target").DamageMarked,
            "Resolution-time modified ATK did not persist on the target.");
        Equal(null, fixture.State.PendingCombat, "Modified-ATK Combat did not close.");
    }

    internal static void UndefendedContinuityLossIsNoHitWithoutRetarget()
    {
        var attackerLost = CreateFixture(
            "combat-c4-attacker-reentry",
            statOverrides: new Dictionary<string, (int Atk, int Hp)>
            {
                [PlainEntityCardId] = (1, 3),
            },
            board:
            [
                Board("reentry-attacker", PlainEntityCardId, "player_1", DomainRow.Horizon, 0, "active", 1),
                Board("reentry-target", PlainEntityCardId, "player_2", DomainRow.Horizon, 0, "active", 1),
            ]);
        SubmitInitialAttack(
            attackerLost,
            "reentry-attacker",
            CombatRuleIds.EntityTargetKind,
            "reentry-target",
            "attacker-reentry");
        MoveDomainCardToVoid(attackerLost, "reentry-attacker");
        ReturnVoidCardToDomain(attackerLost, "reentry-attacker", DomainRow.Horizon, 0);
        var attackerLostResponse = CloseOpenReaction(attackerLost, "attacker-reentry");
        Equal(CombatRuleIds.AttackerMissingNoHitReason, NoHitReason(attackerLostResponse),
            "Attacker leave-and-return reconnected the old participant reference.");
        Equal(0, attackerLostResponse.Events.Count(engineEvent => engineEvent.EventType == "damage_dealt"),
            "Attacker continuity no-hit dealt damage.");

        var targetLost = CreateFixture(
            "combat-c4-target-reentry",
            statOverrides: new Dictionary<string, (int Atk, int Hp)>
            {
                [PlainEntityCardId] = (1, 3),
            },
            board:
            [
                Board("target-reentry-attacker", PlainEntityCardId, "player_1", DomainRow.Horizon, 0, "active", 1),
                Board("target-reentry-original", PlainEntityCardId, "player_2", DomainRow.Horizon, 0, "active", 1),
                Board("target-reentry-other", PlainEntityCardId, "player_2", DomainRow.Horizon, 3, "active", 1),
            ]);
        SubmitInitialAttack(
            targetLost,
            "target-reentry-attacker",
            CombatRuleIds.EntityTargetKind,
            "target-reentry-original",
            "target-reentry");
        MoveDomainCardToVoid(targetLost, "target-reentry-original");
        ReturnVoidCardToDomain(targetLost, "target-reentry-original", DomainRow.Horizon, 0);
        var targetLostResponse = CloseOpenReaction(targetLost, "target-reentry");
        Equal(CombatRuleIds.TargetMissingNoHitReason, NoHitReason(targetLostResponse),
            "OriginalTarget leave-and-return reconnected the old participant reference.");
        Equal(0, targetLost.State.GetCardInstance("target-reentry-other").DamageMarked,
            "Continuity loss implicitly retargeted another Entity.");
        Equal(0, targetLostResponse.Events.Count(engineEvent => engineEvent.EventType == "damage_dealt"),
            "Target continuity no-hit dealt damage.");
        Equal(null, targetLost.State.PendingCombat, "Target continuity no-hit retained Combat.");
    }

    internal static void CommittedDefenderIsExclusiveParticipantAndContinuityIsFinal()
    {
        var valid = CreateFixture(
            "combat-c4-defense-valid",
            statOverrides: new Dictionary<string, (int Atk, int Hp)>
            {
                [PlainEntityCardId] = (1, 3),
                [SpeedEntityCardId] = (1, 3),
            },
            board:
            [
                Board("defense-valid-attacker", PlainEntityCardId, "player_1", DomainRow.Horizon, 5, "active", 1),
                Board("defense-valid-defender", PlainEntityCardId, "player_2", DomainRow.Horizon, 1, "active", 1),
                Board("defense-valid-target", SpeedEntityCardId, "player_2", DomainRow.Horizon, 2, "exhausted", 1),
            ]);
        OpenInterventionChoice(
            valid,
            "defense-valid-attacker",
            CombatRuleIds.EntityTargetKind,
            "defense-valid-target",
            "defense-valid");
        True(SubmitIntervene(
            valid,
            InterventionAction(valid, "player_2"),
            "defense-valid-commit",
            "defense-valid-defender").Accepted,
            "Valid C4 defender could not commit.");
        var validResponse = CloseOpenReaction(valid, "defense-valid");
        Equal(1, valid.State.GetCardInstance("defense-valid-attacker").DamageMarked,
            "Committed defender did not retaliate while Exhausted.");
        Equal(1, valid.State.GetCardInstance("defense-valid-defender").DamageMarked,
            "Attacker did not damage the committed defender.");
        Equal(0, valid.State.GetCardInstance("defense-valid-target").DamageMarked,
            "DefenseCommit incorrectly rewrote or damaged OriginalTarget.");
        Equal("exhausted", valid.State.GetCardInstance("defense-valid-attacker").ActivityState,
            "Defended Combat refunded attacker Exhaust.");
        Equal("exhausted", valid.State.GetCardInstance("defense-valid-defender").ActivityState,
            "Defended Combat refunded defender Exhaust.");
        SequenceEqual(
            ["defense-valid-defender", "defense-valid-attacker"],
            validResponse.Events.Where(engineEvent => engineEvent.EventType == "damage_dealt")
                .Select(engineEvent => engineEvent.Payload.GetProperty("entity_instance_id").GetString()!),
            "Committed defender was not the exclusive opponent participant.");

        var moved = CreateFixture(
            "combat-c4-defense-moved",
            statOverrides: new Dictionary<string, (int Atk, int Hp)>
            {
                [PlainEntityCardId] = (1, 3),
            },
            board:
            [
                Board("defense-moved-attacker", PlainEntityCardId, "player_1", DomainRow.Horizon, 5, "active", 1),
                Board("defense-moved-selected", PlainEntityCardId, "player_2", DomainRow.Horizon, 1, "active", 1),
                Board("defense-moved-target", PlainEntityCardId, "player_2", DomainRow.Horizon, 2, "active", 1),
                Board("defense-moved-replacement", PlainEntityCardId, "player_2", DomainRow.Horizon, 3, "active", 1),
            ]);
        OpenInterventionChoice(
            moved,
            "defense-moved-attacker",
            CombatRuleIds.EntityTargetKind,
            "defense-moved-target",
            "defense-moved");
        True(SubmitIntervene(
            moved,
            InterventionAction(moved, "player_2"),
            "defense-moved-commit",
            "defense-moved-selected").Accepted,
            "Moved-defender fixture could not commit.");
        MoveDomainCardWithinDomain(moved, "defense-moved-selected", DomainRow.Zenith, 1);
        var movedResponse = CloseOpenReaction(moved, "defense-moved");
        Equal(CombatRuleIds.DefenderMissingNoHitReason, NoHitReason(movedResponse),
            "Defender row continuity loss did not become no-hit.");
        Equal("exhausted", moved.State.GetCardInstance("defense-moved-selected").ActivityState,
            "Defender continuity loss refunded committed Exhaust.");
        Equal(0, moved.State.GetCardInstance("defense-moved-target").DamageMarked,
            "Defender continuity loss resumed OriginalTarget.");
        Equal(0, moved.State.GetCardInstance("defense-moved-replacement").DamageMarked,
            "Defender continuity loss selected a replacement defender.");
        Equal(0, movedResponse.Events.Count(engineEvent => engineEvent.EventType == "damage_dealt"),
            "Defender continuity no-hit dealt damage.");

        var reentered = CreateInterventionFixture("combat-c4-defense-reentered");
        OpenInterventionChoice(
            reentered,
            "combat-c4-defense-reentered-attacker",
            CombatRuleIds.EntityTargetKind,
            "combat-c4-defense-reentered-target",
            "defense-reentered");
        True(SubmitIntervene(
            reentered,
            InterventionAction(reentered, "player_2"),
            "defense-reentered-commit",
            "combat-c4-defense-reentered-defender").Accepted,
            "Defender re-entry fixture could not commit.");
        MoveDomainCardToVoid(reentered, "combat-c4-defense-reentered-defender");
        ReturnVoidCardToDomain(
            reentered,
            "combat-c4-defense-reentered-defender",
            DomainRow.Horizon,
            1);
        var reenteredResponse = CloseOpenReaction(reentered, "defense-reentered");
        Equal(CombatRuleIds.DefenderMissingNoHitReason, NoHitReason(reenteredResponse),
            "Defender leave-and-return reconnected the committed incarnation.");
        Equal(0, reenteredResponse.Events.Count(engineEvent => engineEvent.EventType == "damage_dealt"),
            "Re-entered defender no-hit dealt damage.");
        Equal(0, reentered.State.GetCardInstance("combat-c4-defense-reentered-target").DamageMarked,
            "Re-entered defender resumed OriginalTarget.");
    }

    internal static void FinalAerialContactRulesRemainPathSpecific()
    {
        True(CombatResolution.IsFinalContactValid(false, false, defenseCommitted: false),
            "Ground direct contact was rejected.");
        True(CombatResolution.IsFinalContactValid(true, true, defenseCommitted: false),
            "Aerial direct contact was rejected.");
        True(CombatResolution.IsFinalContactValid(true, false, defenseCommitted: false),
            "Aerial attacker to ground direct target contact was rejected.");
        False(CombatResolution.IsFinalContactValid(false, true, defenseCommitted: false),
            "Ground attacker to Aerial direct target contact was accepted.");
        True(CombatResolution.IsFinalContactValid(false, false, defenseCommitted: true),
            "Ground intervention contact was rejected.");
        True(CombatResolution.IsFinalContactValid(true, true, defenseCommitted: true),
            "Aerial intervention contact was rejected.");
        False(CombatResolution.IsFinalContactValid(true, false, defenseCommitted: true),
            "Aerial attacker accepted a ground committed defender.");
        False(CombatResolution.IsFinalContactValid(false, true, defenseCommitted: true),
            "Ground attacker accepted an Aerial committed defender.");

        var fixture = CreateFixture(
            "combat-c4-aerial-loss",
            additionalAerialCardIds: [PlainEntityCardId],
            board:
            [
                Board("aerial-loss-attacker", AerialEntityCardId, "player_1", DomainRow.Horizon, 5, "active", 1),
                Board("aerial-loss-defender", PlainEntityCardId, "player_2", DomainRow.Horizon, 1, "active", 1),
                Board("aerial-loss-target", SpeedEntityCardId, "player_2", DomainRow.Horizon, 2, "active", 1),
            ]);
        OpenInterventionChoice(
            fixture,
            "aerial-loss-attacker",
            CombatRuleIds.EntityTargetKind,
            "aerial-loss-target",
            "aerial-loss");
        True(SubmitIntervene(
            fixture,
            InterventionAction(fixture, "player_2"),
            "aerial-loss-commit",
            "aerial-loss-defender").Accepted,
            "Aerial final-contact fixture could not commit its initially compatible defender.");
        var combat = NotNull(fixture.State.PendingCombat, "Aerial final-contact fixture lost Combat.");
        fixture.State.ReactionWindow = null;
        fixture.State.ResolutionStack.Clear();
        combat.StageId = CombatRuleIds.DefenseCheckpointStage;
        combat.StageSequence = 5;
        var postCommitAbilities = CreateAerialAbilityCatalog(AerialEntityCardId);
        var plan = CombatResolution.BuildPlan(
            fixture.State,
            combat,
            fixture.Runtime,
            fixture.CanonicalCards,
            postCommitAbilities);
        Equal(CombatRuleIds.NoHitOutcome, plan.OutcomeId,
            "Committed defender contact invalidation did not produce no-hit.");
        Equal(CombatRuleIds.ContactInvalidNoHitReason, plan.NoHitReasonId,
            "Committed defender Aerial incompatibility reason is invalid.");
        CombatResolution.Apply(fixture.State, plan);
        Equal(0, fixture.State.GetCardInstance("aerial-loss-attacker").DamageMarked,
            "Aerial contact no-hit damaged the attacker.");
        Equal(0, fixture.State.GetCardInstance("aerial-loss-defender").DamageMarked,
            "Aerial contact no-hit damaged the defender.");
        Equal(0, fixture.State.GetCardInstance("aerial-loss-target").DamageMarked,
            "Aerial contact no-hit resumed OriginalTarget.");
    }

    internal static void CombatDamageProvenanceIsTypedAndDeterministic()
    {
        static string Run()
        {
            var fixture = CreateFixture(
                "combat-c4-provenance",
                statOverrides: new Dictionary<string, (int Atk, int Hp)>
                {
                    [PlainEntityCardId] = (1, 3),
                },
                board:
                [
                    Board("provenance-attacker", PlainEntityCardId, "player_1", DomainRow.Horizon, 0, "active", 1),
                    Board("provenance-target", PlainEntityCardId, "player_2", DomainRow.Horizon, 0, "active", 1),
                ]);
            var response = CloseFirstCombatReaction(
                fixture,
                "provenance-attacker",
                CombatRuleIds.EntityTargetKind,
                "provenance-target",
                "provenance");
            var damageEvents = response.Events.Where(engineEvent => engineEvent.EventType == "damage_dealt").ToArray();
            True(damageEvents.All(engineEvent =>
                engineEvent.Payload.GetProperty("cause_kind_id").GetString() == CombatRuleIds.CombatCauseKind
                && engineEvent.Payload.GetProperty("combat_id").GetString() == "combat:combat-c4-provenance:000001"
                && engineEvent.Payload.TryGetProperty("source_object_ref", out _)
                && !engineEvent.Payload.TryGetProperty("source_ability_id", out _)
                && !engineEvent.Payload.TryGetProperty("source_effect_id", out _)),
                "Combat damage provenance used a fake ability or omitted typed Combat identity.");
            Equal(1, damageEvents.Select(engineEvent =>
                    engineEvent.Payload.GetProperty("simultaneous_group_id").GetString())
                .Distinct(StringComparer.Ordinal).Count(),
                "Damage events do not share one simultaneous group.");
            Equal(1, damageEvents.Select(engineEvent =>
                    engineEvent.Payload.GetProperty("timing_anchor_id").GetString())
                .Distinct(StringComparer.Ordinal).Count(),
                "Damage events do not share one resolution timing anchor.");
            return JsonSerializer.Serialize(new
            {
                response,
                snapshot = fixture.Session.GetDebugSnapshot(),
            });
        }

        Equal(Run(), Run(), "Repeated C4 damage protocol is not deterministic.");
    }

    internal static void SealLifecycleClosesAndAeternalResolvesAtCheckpoint()
    {
        var seal = CreateFixture(
            "combat-c5-seal-boundary",
            sealCardMagnitude: 0,
            board:
            [
                Board("seal-boundary-attacker", PlainEntityCardId, "player_1", DomainRow.Horizon, 0, "active", 1),
            ]);
        var hiddenSealId = NotNull(
            seal.State.GetPlayer("player_2").SealSlots[0].CardInstanceId,
            "Seal boundary fixture is missing its hidden Seal.");
        var sealResponse = CloseFirstCombatReaction(
            seal,
            "seal-boundary-attacker",
            CombatRuleIds.SealSlotTargetKind,
            "seal:player_2:01",
            "seal-boundary");
        True(seal.State.PendingCombat is null, "C5 did not close a completed Seal-target Combat.");
        Equal("broken", seal.State.GetPlayer("player_2").SealSlots[0].Status,
            "C5 did not break the targeted Seal.");
        Equal("hand", seal.State.GetCardInstance(hiddenSealId).Zone,
            "C5 did not Surge the broken Seal to its owner's hand.");
        True(sealResponse.Events.Any(engineEvent => engineEvent.EventType == "seal_revealed"),
            "C5 did not publish the Seal reveal.");
        True(sealResponse.Events.Any(engineEvent => engineEvent.EventType == "combat_resolved"),
            "C5 did not close the no-opportunity Seal Combat.");
        False(sealResponse.Events.Any(engineEvent => engineEvent.EventType == "damage_dealt"),
            "Seal resolution entered the Entity damage path.");

        var aeternal = CreateFixture(
            "combat-c4-aeternal-future",
            playerTwoSealsBroken: true,
            board:
            [
                Board("aeternal-future-attacker", PlainEntityCardId, "player_1", DomainRow.Horizon, 5, "active", 1),
            ]);
        var aeternalResponse = CloseFirstCombatReaction(
            aeternal,
            "aeternal-future-attacker",
            CombatRuleIds.AeternalTargetKind,
            "aeternal:player_2",
            "aeternal-future");
        True(aeternal.State.PendingCombat is null,
            "C6 retained Aeternal-target Combat after outcome.");
        True(aeternal.State.Result.Completed, "C6 did not award Aeternal victory.");
        True(aeternalResponse.Events.Any(engineEvent => engineEvent.EventType == "aeternal_hit"),
            "Aeternal outcome checkpoint did not emit the successful hit.");
        False(aeternalResponse.Events.Any(engineEvent => engineEvent.EventType == "damage_dealt"),
            "Aeternal outcome entered the Entity damage path.");
        EngineSession.ValidateState(seal.State, seal.CanonicalCards, seal.CanonicalAbilities);
        EngineSession.ValidateState(aeternal.State, aeternal.CanonicalCards, aeternal.CanonicalAbilities);
    }

    internal static void SealBreakRevealAndSurgeLifecycleIsExactAndPublic()
    {
        var fixture = CreateFixture(
            "combat-c5-seal-lifecycle",
            sealCardMagnitude: 0,
            board:
            [
                Board("c5-lifecycle-attacker", PlainEntityCardId, "player_1", DomainRow.Horizon, 0, "active", 1),
            ]);
        var owner = fixture.State.GetPlayer("player_2");
        var targetSlot = owner.SealSlots[0];
        var sealedCardInstanceId = NotNull(
            targetSlot.CardInstanceId,
            "C5 lifecycle fixture has no standing Seal identity.");
        var untouchedSeals = owner.SealSlots.Skip(1).ToDictionary(
            slot => slot.SealSlotId,
            slot => slot.CardInstanceId,
            StringComparer.Ordinal);
        False(
            JsonSerializer.Serialize(fixture.Session.GetPlayerSnapshot("player_1"))
                .Contains(sealedCardInstanceId, StringComparison.Ordinal),
            "Standing Seal identity leaked to the attacker before break.");
        False(
            JsonSerializer.Serialize(fixture.Session.GetPlayerSnapshot("player_2"))
                .Contains(sealedCardInstanceId, StringComparison.Ordinal),
            "Standing Seal identity leaked to its owner before break.");

        var response = CloseFirstCombatReaction(
            fixture,
            "c5-lifecycle-attacker",
            CombatRuleIds.SealSlotTargetKind,
            targetSlot.SealSlotId,
            "c5-lifecycle");
        var semanticEvents = response.Events.Where(item => item.EventType is
                "seal_break_intent"
                or "seal_broken"
                or "seal_revealed"
                or "seal_surged"
                or "combat_resolved")
            .ToArray();
        SequenceEqual(
            new[]
            {
                "seal_break_intent",
                "seal_broken",
                "seal_revealed",
                "seal_surged",
                "combat_resolved",
            },
            semanticEvents.Select(item => item.EventType),
            "SealBreak, reveal, Surge, and Combat-close event order changed.");
        var broken = semanticEvents[1];
        var revealed = semanticEvents[2];
        var surged = semanticEvents[3];
        var expectedSurgeId =
            $"surge:{broken.Payload.GetProperty("combat_id").GetString()}:seal:player_2:01";
        Equal(expectedSurgeId, broken.Payload.GetProperty("surge_id").GetString(),
            "Surge identity is not deterministic.");
        Equal(broken.EventId, revealed.Payload.GetProperty("seal_break_event_id").GetString(),
            "Reveal is not correlated to the committed SealBreak event.");
        Equal(broken.EventId, surged.Payload.GetProperty("seal_break_event_id").GetString(),
            "Surge is not correlated to the committed SealBreak event.");
        Equal(sealedCardInstanceId, revealed.Payload.GetProperty("card_instance_id").GetString(),
            "Reveal published the wrong card instance.");
        Equal(PlainEntityCardId, revealed.Payload.GetProperty("card_id").GetString(),
            "Reveal published the wrong card definition.");
        Equal(sealedCardInstanceId, surged.Payload.GetProperty("card_instance_id").GetString(),
            "Surge moved the wrong card instance.");

        Equal("broken", targetSlot.Status, "The targeted Seal slot was not broken.");
        True(targetSlot.CardInstanceId is null, "The broken Seal slot retained hidden identity.");
        Equal("hand", fixture.State.GetCardInstance(sealedCardInstanceId).Zone,
            "The revealed Seal did not enter its owner's hand.");
        Equal(1, owner.HandCardInstanceIds.Count(id => id == sealedCardInstanceId),
            "The surged card does not appear exactly once in owner hand.");
        foreach (var slot in owner.SealSlots.Skip(1))
        {
            Equal("standing", slot.Status, "A non-targeted Seal was broken.");
            Equal(untouchedSeals[slot.SealSlotId], slot.CardInstanceId,
                "A non-targeted Seal identity changed.");
        }

        False(response.Events.Any(item => item.EventType is
            "zone_move" or "card_drawn" or "normal_inflow" or "prophecy_resolved"),
            "Surge emitted a normal draw, Inflow, Prophecy, or technical zone event.");
        True(fixture.State.PendingCombat is null, "No-opportunity Surge left PendingCombat.");
        True(fixture.State.PendingSurgeWindow is null, "Ineligible Surge opened an opportunity.");
        var attackerHistory = fixture.Session.GetEvents("player_1");
        var ownerHistory = fixture.Session.GetEvents("player_2");
        True(attackerHistory.Any(item => item.EventId == revealed.EventId
            && item.Payload.GetProperty("card_instance_id").GetString() == sealedCardInstanceId),
            "Attacker history did not retain the public reveal identity.");
        True(ownerHistory.Any(item => item.EventId == revealed.EventId
            && item.Payload.GetProperty("card_instance_id").GetString() == sealedCardInstanceId),
            "Owner history did not retain the public reveal identity.");
        False(
            JsonSerializer.Serialize(fixture.Session.GetPlayerSnapshot("player_1"))
                .Contains(sealedCardInstanceId, StringComparison.Ordinal),
            "Opponent current hand projection leaked the surged identity.");
        EngineSession.ValidateState(fixture.State, fixture.CanonicalCards, fixture.CanonicalAbilities);
    }

    internal static void ProvidenceEligibilityAndBlockingContractAreExact()
    {
        static CombatFixture Run(int cardMagnitude, int ownerMagnitude, string suffix)
        {
            var fixture = CreateFixture(
                $"combat-c5-eligibility-{suffix}",
                sealCardMagnitude: cardMagnitude,
                playerTwoWellspringCount: ownerMagnitude,
                board:
                [
                    Board($"c5-eligibility-attacker-{suffix}", PlainEntityCardId,
                        "player_1", DomainRow.Horizon, 0, "active", 1),
                ]);
            CloseFirstCombatReaction(
                fixture,
                $"c5-eligibility-attacker-{suffix}",
                CombatRuleIds.SealSlotTargetKind,
                "seal:player_2:01",
                $"c5-eligibility-{suffix}");
            return fixture;
        }

        var greater = Run(3, 2, "greater");
        var window = NotNull(greater.State.PendingSurgeWindow,
            "Greater surged-card Magnitude did not open Providence.");
        var combat = NotNull(greater.State.PendingCombat,
            "Providence opportunity did not retain blocking Combat.");
        Equal(CombatRuleIds.PostSurgeCheckpointStage, combat.StageId,
            "Providence did not stop at the post-Surge checkpoint.");
        Equal("player_2", window.OwnerPlayerId, "Providence owner is not the Seal owner.");
        SequenceEqual(new[] { SealSurgeResolution.ProvidenceOpportunityId },
            window.EligibleOpportunityIds, "Providence eligible opportunity set is not exact.");
        SequenceEqual(new[] { SealSurgeResolution.ProvidenceOpportunityId },
            window.RemainingOpportunityIds, "Providence remaining opportunity set is not exact.");
        Equal(SealSurgeResolution.ProvidenceOpportunityId, window.CurrentOpportunityId,
            "Providence current opportunity is not exact.");
        Equal("hand", greater.State.GetCardInstance(window.SurgedObjectRef.ObjectId).Zone,
            "Providence was evaluated before the surged card entered hand.");

        var ownerAction = SurgeAction(greater, "player_2", includeDisabled: true);
        True(ownerAction.Enabled, "Seal owner cannot resolve Providence.");
        Equal("resolve_surge_opportunity", ownerAction.ActionId,
            "Surge action ID is not the exact public contract.");
        SequenceEqual(
            new[] { "surge_id", "opportunity_id", "choice" },
            ownerAction.PayloadSchema.GetProperty("required").EnumerateArray()
                .Select(item => item.GetString()!),
            "Surge action required payload fields changed.");
        False(ownerAction.PayloadSchema.GetProperty("additional_properties").GetBoolean(),
            "Surge action unexpectedly permits additional payload properties.");
        SequenceEqual(new[] { "apply", "decline" },
            ownerAction.PayloadSchema.GetProperty("properties").GetProperty("choice")
                .GetProperty("enum").EnumerateArray().Select(item => item.GetString()!),
            "Surge action choices changed.");
        var opponentAction = SurgeAction(greater, "player_1", includeDisabled: true);
        False(opponentAction.Enabled, "Opponent received Providence authority.");
        Equal("not_surge_owner", opponentAction.DisabledReason,
            "Opponent Providence disabled reason is unstable.");
        True(greater.Session.ListLegalActions("player_2", includeDisabled: true).Actions
                .Where(action => action.ActionType != "resolve_surge_opportunity")
                .All(action => !action.Enabled && action.DisabledReason == "surge_opportunity_pending"),
            "Normal gameplay remained enabled during Providence.");
        var opponentSummary = greater.Session.GetPlayerSnapshot("player_1").PendingDecisionSummary;
        False(opponentSummary.GetProperty("viewer_is_owner").GetBoolean(),
            "Opponent pending summary claims Surge ownership.");
        True(opponentSummary.GetProperty("surged_card").ValueKind == JsonValueKind.Null,
            "Opponent pending summary leaked surged-card identity.");
        var ownerSummary = greater.Session.GetPlayerSnapshot("player_2").PendingDecisionSummary;
        Equal(window.SurgedObjectRef.ObjectId,
            ownerSummary.GetProperty("surged_card").GetProperty("card_instance_id").GetString(),
            "Owner pending summary omitted surged-card identity.");

        var equal = Run(2, 2, "equal");
        True(equal.State.PendingSurgeWindow is null && equal.State.PendingCombat is null,
            "Equal Magnitude incorrectly opened Providence or retained Combat.");
        var lower = Run(1, 2, "lower");
        True(lower.State.PendingSurgeWindow is null && lower.State.PendingCombat is null,
            "Lower Magnitude incorrectly opened Providence or retained Combat.");

        var interventionDeclined = CreateFixture(
            "combat-c5-eligibility-intervention-declined",
            sealCardMagnitude: 3,
            playerTwoWellspringCount: 2,
            board:
            [
                Board("c5-declined-path-attacker", PlainEntityCardId,
                    "player_1", DomainRow.Horizon, 0, "active", 1),
                Board("c5-declined-path-defender", PlainEntityCardId,
                    "player_2", DomainRow.Horizon, 1, "active", 1),
            ]);
        OpenInterventionChoice(
            interventionDeclined,
            "c5-declined-path-attacker",
            CombatRuleIds.SealSlotTargetKind,
            "seal:player_2:01",
            "c5-declined-path");
        var declinedResponse = SubmitCombatAction(
            interventionDeclined,
            DeclineAction(interventionDeclined, "player_2"),
            "c5-declined-path-decision",
            ContractJsonValue.EmptyObject());
        True(declinedResponse.Accepted, "Declined intervention did not resume Seal resolution.");
        Equal(6, interventionDeclined.State.PendingCombat?.StageSequence,
            "Declined-intervention Seal lifecycle has the wrong post-Surge stage sequence.");
        True(interventionDeclined.State.PendingSurgeWindow is not null,
            "Declined-intervention Seal lifecycle did not open eligible Providence.");
        EngineSession.ValidateState(
            interventionDeclined.State,
            interventionDeclined.CanonicalCards,
            interventionDeclined.CanonicalAbilities);
    }

    internal static void ProvidenceApplyIsCanonicalAndDoesNotConsumeNormalInflow()
    {
        var fixture = CreateEligibleSurgeFixture("combat-c5-providence-apply");
        fixture.State.GetPlayer("player_2").NormalInflowUsedTurnNumber = 1;
        OpenEligibleSurge(fixture, "c5-providence-apply");
        var window = NotNull(fixture.State.PendingSurgeWindow, "Apply fixture did not open Providence.");
        var cardInstanceId = window.SurgedObjectRef.ObjectId;
        var owner = fixture.State.GetPlayer("player_2");
        var normalInflowBefore = owner.NormalInflowUsedTurnNumber;
        var action = SurgeAction(fixture, "player_2");
        var response = SubmitSurge(
            fixture,
            action,
            "c5-providence-apply-action",
            window.SurgeId,
            SealSurgeResolution.ProvidenceOpportunityId,
            "apply");
        True(response.Accepted, "Providence apply was rejected.");
        False(owner.HandCardInstanceIds.Contains(cardInstanceId, StringComparer.Ordinal),
            "Providence apply retained the surged card in hand.");
        Equal(1, owner.WellspringCardInstanceIds.Count(id => id == cardInstanceId),
            "Providence apply did not add exactly one Wellspring object.");
        var card = fixture.State.GetCardInstance(cardInstanceId);
        Equal("wellspring", card.Zone, "Providence apply did not use the Wellspring zone.");
        Equal("owner_only", card.Visibility, "Providence Wellspring identity is not private.");
        Equal("active", card.ActivityState, "Providence Wellspring source is not active.");
        Equal(normalInflowBefore, owner.NormalInflowUsedTurnNumber,
            "Providence apply consumed or reset normal Inflow state.");
        SequenceEqual(new[] { "surge_opportunity_resolved", "combat_resolved" },
            response.Events.Select(item => item.EventType),
            "Providence apply emitted redundant lifecycle noise or wrong event order.");
        Equal("wellspring", response.Events[0].Payload.GetProperty("result_zone_id").GetString(),
            "Providence apply event has the wrong result zone.");
        True(response.Events[0].Payload.GetProperty("transition_id").GetString() is not null,
            "Providence apply did not expose its typed transition correlation.");
        True(fixture.Session.GetEvents("player_1").Any(item =>
                item.EventType == "seal_revealed"
                && item.Payload.GetProperty("card_instance_id").GetString() == cardInstanceId),
            "Public reveal history was lost after the card entered private Wellspring.");
        False(
            JsonSerializer.Serialize(fixture.Session.GetPlayerSnapshot("player_1"))
                .Contains(cardInstanceId, StringComparison.Ordinal),
            "Opponent Wellspring projection leaked the surged card instance.");
        AssertC5Closed(fixture, "Providence apply");
        True(fixture.Session.ListLegalActions("player_1").Actions.Any(action => action.Enabled),
            "Normal gameplay did not resume after Providence apply.");

        var beforeDuplicate = Fingerprint(fixture);
        var duplicate = SubmitSurge(
            fixture,
            action,
            "c5-providence-apply-duplicate",
            window.SurgeId,
            SealSurgeResolution.ProvidenceOpportunityId,
            "apply");
        False(duplicate.Accepted, "Resolved Providence was reusable.");
        Equal(beforeDuplicate, Fingerprint(fixture), "Duplicate Providence mutated state.");
    }

    internal static void ProvidenceDeclineAndInvalidRequestsAreAtomic()
    {
        var invalid = CreateEligibleSurgeFixture("combat-c5-providence-invalid");
        OpenEligibleSurge(invalid, "c5-providence-invalid");
        var window = NotNull(invalid.State.PendingSurgeWindow,
            "Invalid-request fixture did not open Providence.");
        var action = SurgeAction(invalid, "player_2");

        void RejectUnchanged(string requestId, JsonElement payload, int? stateVersion = null)
        {
            var before = Fingerprint(invalid);
            var response = SubmitCombatAction(invalid, action, requestId, payload, stateVersion);
            False(response.Accepted, $"Invalid Surge request was accepted: {requestId}");
            Equal(before, Fingerprint(invalid), $"Invalid Surge request mutated state: {requestId}");
        }

        RejectUnchanged(
            "c5-invalid-stale-version",
            SurgePayload(window.SurgeId, SealSurgeResolution.ProvidenceOpportunityId, "apply"),
            invalid.State.StateVersion - 1);
        RejectUnchanged(
            "c5-invalid-surge-id",
            SurgePayload("surge:stale", SealSurgeResolution.ProvidenceOpportunityId, "apply"));
        RejectUnchanged(
            "c5-invalid-opportunity",
            SurgePayload(window.SurgeId, "unknown", "apply"));
        RejectUnchanged(
            "c5-invalid-choice",
            SurgePayload(window.SurgeId, SealSurgeResolution.ProvidenceOpportunityId, "keep"));
        RejectUnchanged(
            "c5-invalid-extra-field",
            ContractJsonValue.From(new Dictionary<string, object?>
            {
                ["surge_id"] = window.SurgeId,
                ["opportunity_id"] = SealSurgeResolution.ProvidenceOpportunityId,
                ["choice"] = "decline",
                ["extra"] = true,
            }));

        var decline = SubmitSurge(
            invalid,
            action,
            "c5-providence-decline",
            window.SurgeId,
            SealSurgeResolution.ProvidenceOpportunityId,
            "decline");
        True(decline.Accepted, "Providence decline was rejected after atomic invalid requests.");
        var card = invalid.State.GetCardInstance(window.SurgedObjectRef.ObjectId);
        Equal("hand", card.Zone, "Providence decline moved the surged card out of hand.");
        Equal("hand", decline.Events[0].Payload.GetProperty("result_zone_id").GetString(),
            "Providence decline event has the wrong result zone.");
        False(decline.Events[0].Payload.TryGetProperty("transition_id", out _),
            "Providence decline emitted a nonexistent zone transition.");
        AssertC5Closed(invalid, "Providence decline");
        var beforeReuse = Fingerprint(invalid);
        var reused = SubmitSurge(
            invalid,
            action,
            "c5-providence-decline-reuse",
            window.SurgeId,
            SealSurgeResolution.ProvidenceOpportunityId,
            "decline");
        False(reused.Accepted, "Declined Providence was offered again.");
        Equal(beforeReuse, Fingerprint(invalid), "Reused decline mutated state.");
    }

    internal static void SealOutcomeRevalidationAndStalePlansAreAtomic()
    {
        static CombatFixture Prepare(string matchId)
        {
            var fixture = CreateFixture(
                matchId,
                sealCardMagnitude: 0,
                board:
                [
                    Board($"{matchId}-attacker", PlainEntityCardId,
                        "player_1", DomainRow.Horizon, 0, "active", 1),
                ]);
            SubmitInitialAttack(
                fixture,
                $"{matchId}-attacker",
                CombatRuleIds.SealSlotTargetKind,
                "seal:player_2:01",
                matchId);
            fixture.State.ReactionWindow = null;
            fixture.State.ResolutionStack.Clear();
            fixture.State.PriorityPlayerId = "player_1";
            var combat = NotNull(fixture.State.PendingCombat, "Seal plan fixture lost Combat.");
            combat.StageId = CombatRuleIds.SealOutcomeCheckpointStage;
            combat.StageSequence = 4;
            combat.AttackContinuityStateId = CombatRuleIds.AttackContinuityContinuous;
            combat.DefenseDecisionStateId = CombatRuleIds.DefenseDecisionUnavailable;
            combat.ResolutionTimingAnchorId = $"{combat.CombatId}:resolution";
            combat.OutcomeId = CombatRuleIds.FutureOutcomePending;
            return fixture;
        }

        var attackerLost = Prepare("combat-c5-attacker-lost");
        MoveDomainCardToVoid(attackerLost, "combat-c5-attacker-lost-attacker");
        var lostCombat = NotNull(attackerLost.State.PendingCombat, "Attacker-lost fixture lost Combat.");
        var lostPlan = SealSurgeResolution.BuildPlan(
            attackerLost.State,
            lostCombat,
            attackerLost.Runtime,
            attackerLost.CanonicalCards);
        Equal(CombatRuleIds.NoHitOutcome, lostPlan.OutcomeId,
            "Lost attacker did not resolve as no-hit.");
        Equal(CombatRuleIds.AttackerMissingNoHitReason, lostPlan.NoHitReasonId,
            "Lost attacker no-hit reason changed.");
        var lostBefore = attackerLost.State.GetPlayer("player_2").SealSlots[0].CardInstanceId;
        SealSurgeResolution.Apply(attackerLost.State, lostPlan);
        Equal(lostBefore, attackerLost.State.GetPlayer("player_2").SealSlots[0].CardInstanceId,
            "Attacker-continuity no-hit mutated the Seal.");

        var alreadyBroken = Prepare("combat-c5-already-broken");
        MoveSealToHandForRevalidationFixture(alreadyBroken, 0);
        var brokenCombat = NotNull(alreadyBroken.State.PendingCombat, "Broken-Seal fixture lost Combat.");
        var brokenPlan = SealSurgeResolution.BuildPlan(
            alreadyBroken.State,
            brokenCombat,
            alreadyBroken.Runtime,
            alreadyBroken.CanonicalCards);
        Equal(CombatRuleIds.NoHitOutcome, brokenPlan.OutcomeId,
            "Already-broken Seal did not resolve as no-hit.");
        Equal(CombatRuleIds.SealUnavailableNoHitReason, brokenPlan.NoHitReasonId,
            "Already-broken Seal no-hit reason changed.");
        var brokenFingerprint = Fingerprint(alreadyBroken);
        SealSurgeResolution.Apply(alreadyBroken.State, brokenPlan);
        Equal(brokenFingerprint, Fingerprint(alreadyBroken),
            "Already-broken Seal no-hit mutated state.");

        var stale = Prepare("combat-c5-stale-plan");
        var staleCombat = NotNull(stale.State.PendingCombat, "Stale Seal-plan fixture lost Combat.");
        var plan = SealSurgeResolution.BuildPlan(
            stale.State,
            staleCombat,
            stale.Runtime,
            stale.CanonicalCards);
        stale.State.StateVersion += 1;
        var staleBefore = Fingerprint(stale);
        ThrowsState(
            () => SealSurgeResolution.Apply(stale.State, plan),
            "stale",
            "A stale Seal outcome plan was applied.");
        Equal(staleBefore, Fingerprint(stale), "Stale Seal plan partially mutated state.");
    }

    internal static void PendingSurgeInvariantsRejectMalformedState()
    {
        static CombatFixture Open(string suffix)
        {
            var fixture = CreateEligibleSurgeFixture($"combat-c5-invariant-{suffix}");
            OpenEligibleSurge(fixture, $"c5-invariant-{suffix}");
            return fixture;
        }

        var wrongOwner = Open("owner");
        var originalWindow = NotNull(
            wrongOwner.State.PendingSurgeWindow,
            "Owner invariant fixture has no window.");
        var wrongOwnerWindow = new PendingSurgeWindowState
        {
            SurgeId = originalWindow.SurgeId,
            SealBreakEventId = originalWindow.SealBreakEventId,
            BrokenSealSlotId = originalWindow.BrokenSealSlotId,
            SurgedObjectRef = originalWindow.SurgedObjectRef,
            OwnerPlayerId = "player_1",
            CurrentOpportunityId = originalWindow.CurrentOpportunityId,
            OpenedAtStateVersion = originalWindow.OpenedAtStateVersion,
        };
        wrongOwnerWindow.EligibleOpportunityIds.AddRange(originalWindow.EligibleOpportunityIds);
        wrongOwnerWindow.RemainingOpportunityIds.AddRange(originalWindow.RemainingOpportunityIds);
        wrongOwner.State.PendingSurgeWindow = wrongOwnerWindow;
        ThrowsState(
            () => EngineSession.ValidateState(
                wrongOwner.State,
                wrongOwner.CanonicalCards,
                wrongOwner.CanonicalAbilities),
            "PendingSurgeWindow",
            "Wrong Surge owner was accepted.");

        var duplicateOpportunity = Open("opportunity");
        NotNull(duplicateOpportunity.State.PendingSurgeWindow,
            "Opportunity invariant fixture has no window.")
            .RemainingOpportunityIds.Add(SealSurgeResolution.ProvidenceOpportunityId);
        ThrowsState(
            () => EngineSession.ValidateState(
                duplicateOpportunity.State,
                duplicateOpportunity.CanonicalCards,
                duplicateOpportunity.CanonicalAbilities),
            "PendingSurgeWindow",
            "Duplicate Surge opportunity was accepted.");

        var wrongIncarnation = Open("incarnation");
        var incarnationWindow = NotNull(wrongIncarnation.State.PendingSurgeWindow,
            "Incarnation invariant fixture has no window.");
        wrongIncarnation.State.GetCardInstance(incarnationWindow.SurgedObjectRef.ObjectId).ZoneSequence += 1;
        ThrowsState(
            () => EngineSession.ValidateState(
                wrongIncarnation.State,
                wrongIncarnation.CanonicalCards,
                wrongIncarnation.CanonicalAbilities),
            "surged",
            "Stale surged ObjectRef was accepted.");

        var duplicatedZone = Open("zone");
        var zoneWindow = NotNull(duplicatedZone.State.PendingSurgeWindow,
            "Zone invariant fixture has no window.");
        duplicatedZone.State.GetPlayer("player_2").SealSlots[0].CardInstanceId =
            zoneWindow.SurgedObjectRef.ObjectId;
        ThrowsState(
            () => EngineSession.ValidateState(
                duplicatedZone.State,
                duplicatedZone.CanonicalCards,
                duplicatedZone.CanonicalAbilities),
            "broken Seal",
            "Broken Seal slot duplicated the surged hand object.");

        var orphanCombat = Open("orphan");
        orphanCombat.State.PendingSurgeWindow = null;
        ThrowsState(
            () => EngineSession.ValidateState(
                orphanCombat.State,
                orphanCombat.CanonicalCards,
                orphanCombat.CanonicalAbilities),
            "Post-Surge",
            "Post-Surge Combat without its decision window was accepted.");
    }

    internal static void RepeatedC5ProtocolIsDeterministic()
    {
        static string Run()
        {
            var fixture = CreateEligibleSurgeFixture("combat-c5-repeated");
            OpenEligibleSurge(fixture, "c5-repeated");
            var window = NotNull(fixture.State.PendingSurgeWindow,
                "Repeated C5 fixture did not open Providence.");
            var response = SubmitSurge(
                fixture,
                SurgeAction(fixture, "player_2"),
                "c5-repeated-apply",
                window.SurgeId,
                SealSurgeResolution.ProvidenceOpportunityId,
                "apply");
            True(response.Accepted, "Repeated C5 apply failed.");
            return JsonSerializer.Serialize(new
            {
                response,
                snapshot = fixture.Session.GetDebugSnapshot(),
                owner = fixture.Session.GetPlayerSnapshot("player_2"),
                opponent = fixture.Session.GetPlayerSnapshot("player_1"),
            });
        }

        Equal(Run(), Run(), "Repeated C5 protocol is not deterministic.");
    }

    internal static void AeternalSuccessfulHitCommitsTerminalMatchResult()
    {
        var fixture = CreateAeternalFixture("combat-c6-success");
        var attacker = fixture.State.GetCardInstance("combat-c6-success-attacker");
        var attackerZoneSequence = attacker.ZoneSequence;
        var response = ResolveAeternalAttack(fixture, "c6-success");
        var result = fixture.Session.GetMatchResult();
        var expectedCombatId = "combat:combat-c6-success:000001";

        True(response.Accepted, "Successful Aeternal outcome action was rejected.");
        True(result.Completed, "Successful Aeternal hit did not complete the match.");
        Equal(ContractSchemas.MatchResult, result.SchemaVersion,
            "Aeternal MatchResult schema is invalid.");
        Equal(AeternalOutcomeResolution.MatchEndedStatus, result.Status,
            "Aeternal MatchResult status is invalid.");
        Equal(AeternalOutcomeResolution.VictoryOutcome, result.Outcome,
            "Aeternal MatchResult outcome is invalid.");
        Equal("player_1", result.WinnerPlayerId, "Aeternal winner is invalid.");
        Equal("player_2", result.LoserPlayerId, "Aeternal loser is invalid.");
        Equal(AeternalOutcomeResolution.AeternalHitReasonId, result.ReasonId,
            "Aeternal result reason is invalid.");
        Equal(expectedCombatId, result.WinningCombatId,
            "Aeternal result lost Combat correlation.");
        Equal(fixture.State.StateVersion, result.CommittedAtStateVersion,
            "Aeternal result committed-state version is invalid.");
        Equal("exhausted", attacker.ActivityState,
            "Successful outcome refunded AttackCommit Exhaust.");
        Equal(attackerZoneSequence, attacker.ZoneSequence,
            "Aeternal hit changed the attacker incarnation.");
        Equal(0, attacker.DamageMarked, "Aeternal outcome marked damage on the attacker.");
        False(fixture.State.CardInstances.ContainsKey("aeternal:player_2"),
            "Aeternal was modeled as a card or Entity instance.");
        False(response.Events.Any(item => item.EventType is
                "damage_dealt" or "entity_destroyed" or "card_zone_changed" or "seal_broken"),
            "Aeternal outcome used damage, destruction, zone, or Seal transitions.");
        SequenceEqual(
            ["aeternal_hit", "combat_resolved", "match_ended"],
            response.Events.Where(item => item.EventType is
                    "aeternal_hit" or "combat_resolved" or "match_ended")
                .Select(item => item.EventType),
            "Aeternal terminal semantic event order changed.");
        True(fixture.Session.ListLegalActions("player_1", includeDisabled: true).Actions.IsEmpty,
            "Winner retained a terminal gameplay action.");
        True(fixture.Session.ListLegalActions("player_2", includeDisabled: true).Actions.IsEmpty,
            "Loser retained a terminal gameplay action.");
        AssertC6Closed(fixture, expectTerminal: true, "Successful Aeternal hit");
    }

    internal static void AeternalRestoredSealUsesCurrentOutcomeState()
    {
        var restored = CreateAeternalFixture("combat-c6-restored-seal");
        SubmitInitialAttack(
            restored,
            "combat-c6-restored-seal-attacker",
            CombatRuleIds.AeternalTargetKind,
            "aeternal:player_2",
            "c6-restored-seal");
        var restoredCardId = RestoreStandingSealForFixture(restored, laneIndex: 2);
        var blocked = CloseOpenReaction(restored, "c6-restored-seal");
        False(restored.State.Result.Completed,
            "A restored standing Seal did not protect the Aeternal at outcome.");
        Equal(CombatRuleIds.StandingSealRestoredNoHitReason, NoHitReason(blocked),
            "Restored-Seal no-hit reason is invalid.");
        Equal("exhausted", restored.State.GetCardInstance(
                "combat-c6-restored-seal-attacker").ActivityState,
            "Restored Seal refunded the committed attacker.");
        Equal("seal", restored.State.GetCardInstance(restoredCardId).Zone,
            "Restored standing Seal did not remain authoritative.");
        False(blocked.Events.Any(item => item.EventType is
                "aeternal_hit" or "match_ended" or "seal_broken" or "seal_surged"),
            "Protected Aeternal outcome retargeted or emitted a successful hit.");
        AssertC6Closed(restored, expectTerminal: false, "Restored standing Seal");
        True(restored.Session.ListLegalActions("player_1").Actions.Any(action => action.Enabled),
            "Gameplay did not resume after a no-victory Combat close.");

        var restoredThenRemoved = CreateAeternalFixture("combat-c6-restored-removed");
        SubmitInitialAttack(
            restoredThenRemoved,
            "combat-c6-restored-removed-attacker",
            CombatRuleIds.AeternalTargetKind,
            "aeternal:player_2",
            "c6-restored-removed");
        RestoreStandingSealForFixture(restoredThenRemoved, laneIndex: 4);
        RemoveRestoredSealForFixture(restoredThenRemoved, laneIndex: 4);
        var successful = CloseOpenReaction(restoredThenRemoved, "c6-restored-removed");
        True(restoredThenRemoved.State.Result.Completed,
            "Current zero-Seal state did not govern after a restored Seal was removed again.");
        True(successful.Events.Any(item => item.EventType == "aeternal_hit"),
            "Current zero-Seal outcome did not emit Aeternal hit.");
        AssertC6Closed(restoredThenRemoved, expectTerminal: true,
            "Restored then removed Seal");
    }

    internal static void AeternalAttackerContinuityLossClosesWithoutVictory()
    {
        var missing = CreateAeternalFixture("combat-c6-attacker-missing");
        SubmitInitialAttack(
            missing,
            "combat-c6-attacker-missing-attacker",
            CombatRuleIds.AeternalTargetKind,
            "aeternal:player_2",
            "c6-attacker-missing");
        MoveDomainCardToVoid(missing, "combat-c6-attacker-missing-attacker");
        var missingResponse = CloseOpenReaction(missing, "c6-attacker-missing");
        False(missing.State.Result.Completed, "Missing attacker produced Aeternal victory.");
        Equal(CombatRuleIds.AttackerMissingNoHitReason, NoHitReason(missingResponse),
            "Missing attacker no-hit reason is invalid.");
        False(missingResponse.Events.Any(item => item.EventType == "aeternal_hit"),
            "Missing attacker emitted an Aeternal hit.");
        AssertC6Closed(missing, expectTerminal: false, "Missing attacker");

        var reincarnated = CreateAeternalFixture("combat-c6-attacker-reincarnated");
        SubmitInitialAttack(
            reincarnated,
            "combat-c6-attacker-reincarnated-attacker",
            CombatRuleIds.AeternalTargetKind,
            "aeternal:player_2",
            "c6-attacker-reincarnated");
        var committedIncarnation = NotNull(reincarnated.State.PendingCombat,
            "Reincarnation fixture lost Combat.").AttackerRef.IncarnationSequence;
        MoveDomainCardToVoid(reincarnated, "combat-c6-attacker-reincarnated-attacker");
        ReturnVoidCardToDomain(
            reincarnated,
            "combat-c6-attacker-reincarnated-attacker",
            DomainRow.Horizon,
            destinationLaneIndex: 3);
        var reincarnatedResponse = CloseOpenReaction(reincarnated, "c6-attacker-reincarnated");
        False(reincarnated.State.Result.Completed,
            "Leave-and-return attacker incarnation produced Aeternal victory.");
        True(reincarnated.State.GetCardInstance(
                "combat-c6-attacker-reincarnated-attacker").ZoneSequence > committedIncarnation,
            "Reincarnation fixture did not change zone presence.");
        Equal(CombatRuleIds.AttackerMissingNoHitReason, NoHitReason(reincarnatedResponse),
            "Reincarnated attacker no-hit reason is invalid.");
        False(reincarnatedResponse.Events.Any(item => item.EventType is
                "seal_broken" or "aeternal_hit"),
            "Attacker continuity loss retargeted or hit the Aeternal.");
        AssertC6Closed(reincarnated, expectTerminal: false,
            "Reincarnated attacker");
    }

    internal static void AeternalOutcomeIgnoresDeclarationOnlyRestrictions()
    {
        var ward = CreateFixture(
            "combat-c6-late-ward",
            playerTwoSealsBroken: true,
            board:
            [
                Board("combat-c6-late-ward-attacker", PlainEntityCardId,
                    "player_1", DomainRow.Horizon, 5, "active", 1),
                Board("combat-c6-late-ward-entity", WardEntityCardId,
                    "player_2", DomainRow.Horizon, 1, "exhausted", 1),
            ]);
        SubmitInitialAttack(
            ward,
            "combat-c6-late-ward-attacker",
            CombatRuleIds.AeternalTargetKind,
            "aeternal:player_2",
            "c6-late-ward");
        ward.State.GetCardInstance("combat-c6-late-ward-entity").ActivityState = "active";
        var wardResponse = CloseOpenReaction(ward, "c6-late-ward");
        True(ward.State.Result.Completed,
            "Oltalom appearing after AttackCommit prevented Aeternal outcome.");
        False(wardResponse.Events.Any(item => item.EventType == "intervention_choice_opened"),
            "Late Oltalom opened intervention or retargeted Combat.");

        var timing = CreateAeternalFixture(
            "combat-c6-declaration-only",
            statOverrides: new Dictionary<string, (int Atk, int Hp)>
            {
                [PlainEntityCardId] = (0, 3),
            });
        SubmitInitialAttack(
            timing,
            "combat-c6-declaration-only-attacker",
            CombatRuleIds.AeternalTargetKind,
            "aeternal:player_2",
            "c6-declaration-only");
        var attacker = timing.State.GetCardInstance("combat-c6-declaration-only-attacker");
        attacker.EnteredDomainTurnNumber = 1;
        timing.State.TurnNumber = 1;
        var response = CloseOpenReaction(timing, "c6-declaration-only");
        True(timing.State.Result.Completed,
            "Outcome reran summoning-sickness, first-turn, Exhaust, or ATK legality.");
        Equal("exhausted", attacker.ActivityState,
            "Declaration-only outcome did not preserve AttackCommit Exhaust.");
        False(response.Events.Any(item => item.EventType == "damage_dealt"),
            "Zero-ATK Aeternal success was converted into damage comparison.");
        AssertC6Closed(timing, expectTerminal: true,
            "Declaration-only restrictions");
    }

    internal static void TerminalGameplayActionsAreRejectedAtomically()
    {
        var fixture = CreateAeternalFixture("combat-c6-terminal-actions");
        ResolveAeternalAttack(fixture, "c6-terminal-actions");
        var stateVersion = fixture.State.StateVersion;
        var actionTypes = new[]
        {
            "attack",
            "play_card",
            "normal_inflow",
            "advance_phase",
            "end_turn",
            "pass_priority",
            "react",
            "intervene",
            "resolve_surge_opportunity",
            "resolve_triggered_ability",
        };
        foreach (var playerId in new[] { "player_1", "player_2" })
        {
            foreach (var actionType in actionTypes)
            {
                var before = Fingerprint(fixture);
                var response = fixture.Session.SubmitAction(new ActionRequest(
                    ContractSchemas.ActionRequest,
                    $"terminal-{playerId}-{actionType}",
                    fixture.State.MatchId,
                    playerId,
                    stateVersion - 1,
                    $"stale-{actionType}",
                    actionType,
                    ContractJsonValue.EmptyObject()));
                False(response.Accepted,
                    $"Terminal gameplay action was accepted: {playerId}/{actionType}");
                Equal("match_ended", response.Reason,
                    "Terminal precedence did not produce the stable reason.");
                Equal("MATCH_ENDED", Single(response.Diagnostics).Code,
                    "Terminal rejection diagnostic code is invalid.");
                Equal(stateVersion, response.StateVersionBefore,
                    "Terminal rejection reported the submitted stale version as authoritative.");
                Equal(stateVersion, response.StateVersionAfter,
                    "Terminal rejection changed state version.");
                Equal(before, Fingerprint(fixture),
                    $"Terminal rejection mutated state: {playerId}/{actionType}");
            }
        }

        True(fixture.Session.ListLegalActions("player_1").Actions.IsEmpty,
            "Winner public legal action space is not terminal.");
        True(fixture.Session.ListLegalActions("player_2").Actions.IsEmpty,
            "Loser public legal action space is not terminal.");
        Equal(1, fixture.State.Events.Count(item => item.EventType == "match_ended"),
            "Terminal rejections committed MatchResult more than once.");
    }

    internal static void TerminalProjectionAndEventsAreViewerSafe()
    {
        var fixture = CreateAeternalFixture("combat-c6-projection");
        var privateHandId = AddPrivateHandCardForFixture(fixture, "player_1");
        var hiddenSealId = NotNull(
            fixture.State.GetPlayer("player_1").SealSlots[0].CardInstanceId,
            "Projection fixture has no hidden Seal identity.");
        var response = ResolveAeternalAttack(fixture, "c6-projection");
        var playerOne = fixture.Session.GetPlayerSnapshot("player_1");
        var playerTwo = fixture.Session.GetPlayerSnapshot("player_2");

        Equal(playerOne.MatchResult, playerTwo.MatchResult,
            "Terminal result differs between viewers.");
        Equal(AeternalOutcomeResolution.MatchEndedStatus, playerOne.MatchResult.Status,
            "Player snapshot does not expose ended match status.");
        Equal("player_1", playerOne.MatchResult.WinnerPlayerId,
            "Terminal projection winner is invalid.");
        Equal("player_2", playerOne.MatchResult.LoserPlayerId,
            "Terminal projection loser is invalid.");
        Equal(AeternalOutcomeResolution.AeternalHitReasonId, playerOne.MatchResult.ReasonId,
            "Terminal projection reason is invalid.");
        var playerOneJson = JsonSerializer.Serialize(playerOne);
        var playerTwoJson = JsonSerializer.Serialize(playerTwo);
        False(playerOneJson.Contains(hiddenSealId, StringComparison.Ordinal),
            "Winner projection leaked hidden Seal identity.");
        False(playerTwoJson.Contains(hiddenSealId, StringComparison.Ordinal),
            "Loser projection leaked hidden Seal identity.");
        False(playerTwoJson.Contains(privateHandId, StringComparison.Ordinal),
            "Opponent terminal projection leaked hidden hand identity.");
        foreach (var viewer in new[] { "player_1", "player_2" })
        {
            var terminalEvents = fixture.Session.GetEvents(viewer).Where(item => item.EventType is
                    "aeternal_hit" or "match_ended")
                .ToArray();
            Equal(2, terminalEvents.Length,
                "Viewer did not receive both terminal semantic events.");
            var serialized = JsonSerializer.Serialize(terminalEvents);
            False(serialized.Contains(hiddenSealId, StringComparison.Ordinal),
                "Terminal event leaked hidden Seal identity.");
            False(serialized.Contains(privateHandId, StringComparison.Ordinal),
                "Terminal event leaked hidden hand identity.");
        }

        var hit = response.Events.Single(item => item.EventType == "aeternal_hit");
        Equal(0, hit.Payload.GetProperty("standing_seal_count").GetInt32(),
            "Aeternal hit event does not prove zero standing Seals.");
        Equal("aeternal:player_2", hit.Payload.GetProperty("target_id").GetString(),
            "Aeternal hit event target identity is invalid.");
        var ended = response.Events.Single(item => item.EventType == "match_ended");
        Equal(playerOne.MatchResult.WinningCombatId,
            ended.Payload.GetProperty("winning_combat_id").GetString(),
            "Match-ended event lost Combat correlation.");
    }

    internal static void AeternalOutcomePlansAndMatchResultInvariantsAreGuarded()
    {
        var stale = PrepareAeternalCheckpoint("combat-c6-stale-plan");
        var staleCombat = NotNull(stale.State.PendingCombat,
            "Stale Aeternal plan fixture lost Combat.");
        var stalePlan = AeternalOutcomeResolution.BuildPlan(
            stale.State,
            staleCombat,
            stale.Runtime);
        stale.State.StateVersion += 1;
        var staleBefore = Fingerprint(stale);
        ThrowsState(
            () => AeternalOutcomeResolution.Apply(stale.State, stalePlan, stale.Runtime),
            "stale",
            "Stale Aeternal outcome plan was applied.");
        Equal(staleBefore, Fingerprint(stale),
            "Stale Aeternal outcome plan partially mutated state.");

        var protectedAeternal = PrepareAeternalCheckpoint("combat-c6-plan-protected");
        RestoreStandingSealForFixture(protectedAeternal, laneIndex: 1);
        var protectedPlan = AeternalOutcomeResolution.BuildPlan(
            protectedAeternal.State,
            NotNull(protectedAeternal.State.PendingCombat,
                "Protected Aeternal plan fixture lost Combat."),
            protectedAeternal.Runtime);
        False(protectedPlan.SuccessfulHit,
            "A standing Seal produced a successful Aeternal outcome plan.");
        Equal(CombatRuleIds.StandingSealRestoredNoHitReason, protectedPlan.NoHitReasonId,
            "Protected Aeternal plan reason is invalid.");

        var duplicate = PrepareAeternalCheckpoint("combat-c6-duplicate-result");
        var duplicatePlan = AeternalOutcomeResolution.BuildPlan(
            duplicate.State,
            NotNull(duplicate.State.PendingCombat,
                "Duplicate MatchResult fixture lost Combat."),
            duplicate.Runtime);
        AeternalOutcomeResolution.Apply(duplicate.State, duplicatePlan, duplicate.Runtime);
        var duplicateBefore = duplicate.State.Result;
        ThrowsState(
            () => AeternalOutcomeResolution.Apply(duplicate.State, duplicatePlan, duplicate.Runtime),
            "stale",
            "Aeternal MatchResult committed twice.");
        Equal(duplicateBefore, duplicate.State.Result,
            "Duplicate MatchResult attempt changed the authoritative result.");

        var malformed = CreateAeternalFixture("combat-c6-result-invariant");
        ResolveAeternalAttack(malformed, "c6-result-invariant");
        malformed.State.Result = malformed.State.Result with
        {
            LoserPlayerId = malformed.State.Result.WinnerPlayerId,
        };
        ThrowsState(
            () => EngineSession.ValidateState(
                malformed.State,
                malformed.CanonicalCards,
                malformed.CanonicalAbilities),
            "MatchResult",
            "Terminal MatchResult accepted identical winner and loser.");

        var protectedTerminal = CreateAeternalFixture("combat-c6-terminal-seal-invariant");
        ResolveAeternalAttack(protectedTerminal, "c6-terminal-seal-invariant");
        RestoreStandingSealForFixture(protectedTerminal, laneIndex: 0);
        ThrowsState(
            () => EngineSession.ValidateState(
                protectedTerminal.State,
                protectedTerminal.CanonicalCards,
                protectedTerminal.CanonicalAbilities),
            "MatchResult",
            "Terminal Aeternal result accepted a standing Seal.");
    }

    internal static void RepeatedC6ProtocolIsDeterministic()
    {
        static string Run()
        {
            var fixture = CreateAeternalFixture("combat-c6-repeated");
            var response = ResolveAeternalAttack(fixture, "c6-repeated");
            return JsonSerializer.Serialize(new
            {
                response,
                result = fixture.Session.GetMatchResult(),
                debug = fixture.Session.GetDebugSnapshot(),
                playerOne = fixture.Session.GetPlayerSnapshot("player_1"),
                playerTwo = fixture.Session.GetPlayerSnapshot("player_2"),
                playerOneEvents = fixture.Session.GetEvents("player_1"),
                playerTwoEvents = fixture.Session.GetEvents("player_2"),
            });
        }

        Equal(Run(), Run(), "Repeated C6 protocol is not deterministic.");
    }

    internal static void CombatResolutionPlanningRejectsInvalidAndStaleCheckpoints()
    {
        var fixture = CreateFixture(
            "combat-c4-plan-guards",
            statOverrides: new Dictionary<string, (int Atk, int Hp)>
            {
                [PlainEntityCardId] = (1, 3),
            },
            board:
            [
                Board("plan-guard-attacker", PlainEntityCardId, "player_1", DomainRow.Horizon, 0, "active", 1),
                Board("plan-guard-target", PlainEntityCardId, "player_2", DomainRow.Horizon, 0, "active", 1),
            ]);
        SubmitInitialAttack(
            fixture,
            "plan-guard-attacker",
            CombatRuleIds.EntityTargetKind,
            "plan-guard-target",
            "plan-guard");
        var combat = NotNull(fixture.State.PendingCombat, "Plan-guard fixture lost Combat.");
        var beforeInvalid = Fingerprint(fixture);
        ThrowsState(
            () => CombatResolution.BuildPlan(
                fixture.State,
                combat,
                fixture.Runtime,
                fixture.CanonicalCards,
                fixture.CanonicalAbilities),
            "defense_checkpoint",
            "Combat resolution planned from the attack ReactionWindow.");
        Equal(beforeInvalid, Fingerprint(fixture), "Invalid checkpoint planning mutated state.");

        fixture.State.ReactionWindow = null;
        fixture.State.ResolutionStack.Clear();
        combat.StageId = CombatRuleIds.DefenseCheckpointStage;
        combat.StageSequence = 3;
        combat.AttackContinuityStateId = CombatRuleIds.AttackContinuityContinuous;
        combat.DefenseDecisionStateId = CombatRuleIds.DefenseDecisionUnavailable;
        var plan = CombatResolution.BuildPlan(
            fixture.State,
            combat,
            fixture.Runtime,
            fixture.CanonicalCards,
            fixture.CanonicalAbilities);
        fixture.State.StateVersion += 1;
        var beforeStale = fixture.State.GetCardInstance("plan-guard-target").DamageMarked;
        ThrowsState(
            () => CombatResolution.Apply(fixture.State, plan),
            "stale",
            "A stale Combat resolution plan was applied.");
        Equal(beforeStale, fixture.State.GetCardInstance("plan-guard-target").DamageMarked,
            "Stale Combat plan partially applied damage.");
    }

    internal static void RepeatedC3ProtocolIsDeterministic()
    {
        static string Run()
        {
            var fixture = CreateInterventionFixture("combat-c3-repeated", defenderZoneSequence: 6);
            OpenInterventionChoice(
                fixture,
                "combat-c3-repeated-attacker",
                CombatRuleIds.EntityTargetKind,
                "combat-c3-repeated-target",
                "c3-repeated");
            True(SubmitIntervene(
                fixture,
                InterventionAction(fixture, "player_2"),
                "c3-repeated-intervene",
                "combat-c3-repeated-defender").Accepted,
                "Repeated C3 intervention failed.");
            CloseOpenReaction(fixture, "c3-repeated-defense");
            return Fingerprint(fixture);
        }

        Equal(Run(), Run(), "Repeated C3 protocol is not deterministic.");
    }

    private static CombatFixture CreateAeternalFixture(
        string matchId,
        IReadOnlyDictionary<string, (int Atk, int Hp)>? statOverrides = null) => CreateFixture(
        matchId,
        playerTwoSealsBroken: true,
        statOverrides: statOverrides,
        board:
        [
            Board($"{matchId}-attacker", PlainEntityCardId,
                "player_1", DomainRow.Horizon, 0, "active", 1),
        ]);

    private static ActionResponse ResolveAeternalAttack(
        CombatFixture fixture,
        string requestPrefix) => CloseFirstCombatReaction(
        fixture,
        $"{fixture.State.MatchId}-attacker",
        CombatRuleIds.AeternalTargetKind,
        "aeternal:player_2",
        requestPrefix);

    private static CombatFixture PrepareAeternalCheckpoint(string matchId)
    {
        var fixture = CreateAeternalFixture(matchId);
        SubmitInitialAttack(
            fixture,
            $"{matchId}-attacker",
            CombatRuleIds.AeternalTargetKind,
            "aeternal:player_2",
            matchId);
        fixture.State.ReactionWindow = null;
        fixture.State.ResolutionStack.Clear();
        fixture.State.PriorityPlayerId = "player_1";
        var combat = NotNull(fixture.State.PendingCombat,
            "Aeternal checkpoint fixture lost Combat.");
        combat.StageId = CombatRuleIds.AeternalOutcomeCheckpointStage;
        combat.StageSequence = 4;
        combat.AttackContinuityStateId = CombatRuleIds.AttackContinuityContinuous;
        combat.DefenseDecisionStateId = CombatRuleIds.DefenseDecisionUnavailable;
        combat.ResolutionTimingAnchorId = $"{combat.CombatId}:resolution";
        combat.OutcomeId = CombatRuleIds.FutureOutcomePending;
        return fixture;
    }

    private static string RestoreStandingSealForFixture(
        CombatFixture fixture,
        int laneIndex)
    {
        var owner = fixture.State.GetPlayer("player_2");
        var slot = owner.SealSlots[laneIndex];
        Equal("broken", slot.Status, "Only a broken Seal slot can be restored in this fixture.");
        True(slot.CardInstanceId is null,
            "Broken Seal fixture retained an identity before restoration.");
        var cardInstanceId = $"{fixture.State.MatchId}-restored-seal-{laneIndex + 1:00}";
        slot.Status = "standing";
        slot.CardInstanceId = cardInstanceId;
        fixture.State.CardInstances.Add(cardInstanceId, new CardInstanceState
        {
            CardInstanceId = cardInstanceId,
            CardId = PlainEntityCardId,
            OwnerPlayerId = owner.PlayerId,
            ControllerPlayerId = owner.PlayerId,
            Zone = "seal",
            ZoneIndex = laneIndex,
            Visibility = "hidden",
            CreatedSequence = fixture.State.CardInstances.Count + 1,
            ZoneSequence = 1,
            InitialZone = "seal",
        });
        return cardInstanceId;
    }

    private static void RemoveRestoredSealForFixture(
        CombatFixture fixture,
        int laneIndex)
    {
        var owner = fixture.State.GetPlayer("player_2");
        var slot = owner.SealSlots[laneIndex];
        var cardInstanceId = NotNull(slot.CardInstanceId,
            "Restored Seal fixture has no standing identity to remove.");
        var card = fixture.State.GetCardInstance(cardInstanceId);
        slot.Status = "broken";
        slot.CardInstanceId = null;
        card.Zone = "void";
        card.ZoneIndex = owner.VoidCardInstanceIds.Count;
        card.Visibility = "public";
        card.ZoneSequence += 1;
        owner.VoidCardInstanceIds.Add(cardInstanceId);
    }

    private static string AddPrivateHandCardForFixture(
        CombatFixture fixture,
        string ownerPlayerId)
    {
        var owner = fixture.State.GetPlayer(ownerPlayerId);
        var cardInstanceId = $"{fixture.State.MatchId}-{ownerPlayerId}-private-hand";
        owner.HandCardInstanceIds.Add(cardInstanceId);
        fixture.State.CardInstances.Add(cardInstanceId, new CardInstanceState
        {
            CardInstanceId = cardInstanceId,
            CardId = PlainEntityCardId,
            OwnerPlayerId = owner.PlayerId,
            ControllerPlayerId = owner.PlayerId,
            Zone = "hand",
            ZoneIndex = owner.HandCardInstanceIds.Count - 1,
            Visibility = "owner_only",
            CreatedSequence = fixture.State.CardInstances.Count + 1,
            ZoneSequence = 1,
            InitialZone = "hand",
        });
        return cardInstanceId;
    }

    private static void AssertC6Closed(
        CombatFixture fixture,
        bool expectTerminal,
        string context)
    {
        Equal(expectTerminal, fixture.State.Result.Completed,
            $"{context} terminal result state is invalid.");
        True(fixture.State.PendingCombat is null, $"{context} left PendingCombat.");
        True(fixture.State.ReactionWindow is null, $"{context} left ReactionWindow.");
        True(fixture.State.PendingSurgeWindow is null,
            $"{context} left PendingSurgeWindow.");
        True(fixture.State.PendingTriggerWindow is null,
            $"{context} left PendingTriggerWindow.");
        Equal(0, fixture.State.ResolutionStack.Count,
            $"{context} left a resolution entry.");
        Equal(0, fixture.State.ResolutionCardInstanceIds.Count,
            $"{context} left a Resolution-zone card.");
        Equal(0, fixture.State.QueuedTriggerBatches.Count,
            $"{context} left a queued trigger batch.");
        EngineSession.ValidateState(
            fixture.State,
            fixture.CanonicalCards,
            fixture.CanonicalAbilities);
    }

    private static CombatFixture CreateEligibleSurgeFixture(string matchId) => CreateFixture(
        matchId,
        sealCardMagnitude: 3,
        playerTwoWellspringCount: 2,
        board:
        [
            Board($"{matchId}-attacker", PlainEntityCardId,
                "player_1", DomainRow.Horizon, 0, "active", 1),
        ]);

    private static ActionResponse OpenEligibleSurge(CombatFixture fixture, string requestPrefix)
    {
        var response = CloseFirstCombatReaction(
            fixture,
            $"{fixture.State.MatchId}-attacker",
            CombatRuleIds.SealSlotTargetKind,
            "seal:player_2:01",
            requestPrefix);
        True(fixture.State.PendingSurgeWindow is not null,
            $"{requestPrefix} did not open an eligible Surge opportunity.");
        return response;
    }

    private static LegalAction SurgeAction(
        CombatFixture fixture,
        string playerId,
        bool includeDisabled = false) => fixture.Session
        .ListLegalActions(playerId, includeDisabled)
        .Actions.Single(action => action.ActionType == "resolve_surge_opportunity");

    private static JsonElement SurgePayload(
        string surgeId,
        string opportunityId,
        string choice) => ContractJsonValue.From(new Dictionary<string, object?>
        {
            ["surge_id"] = surgeId,
            ["opportunity_id"] = opportunityId,
            ["choice"] = choice,
        });

    private static ActionResponse SubmitSurge(
        CombatFixture fixture,
        LegalAction action,
        string requestId,
        string surgeId,
        string opportunityId,
        string choice,
        int? expectedStateVersion = null) => SubmitCombatAction(
            fixture,
            action,
            requestId,
            SurgePayload(surgeId, opportunityId, choice),
            expectedStateVersion);

    private static void AssertC5Closed(CombatFixture fixture, string context)
    {
        True(fixture.State.PendingSurgeWindow is null,
            $"{context} left PendingSurgeWindow.");
        True(fixture.State.PendingCombat is null, $"{context} left PendingCombat.");
        True(fixture.State.ReactionWindow is null, $"{context} left ReactionWindow.");
        True(fixture.State.PendingTriggerWindow is null,
            $"{context} left PendingTriggerWindow.");
        Equal(0, fixture.State.QueuedTriggerBatches.Count,
            $"{context} left a queued trigger batch.");
        Equal(0, fixture.State.ResolutionStack.Count,
            $"{context} left a Combat continuation or resolution entry.");
        EngineSession.ValidateState(
            fixture.State,
            fixture.CanonicalCards,
            fixture.CanonicalAbilities);
    }

    private static void MoveSealToHandForRevalidationFixture(
        CombatFixture fixture,
        int laneIndex)
    {
        var owner = fixture.State.GetPlayer("player_2");
        var slot = owner.SealSlots[laneIndex];
        var cardInstanceId = NotNull(slot.CardInstanceId,
            "Seal revalidation fixture has no standing identity.");
        var card = fixture.State.GetCardInstance(cardInstanceId);
        slot.Status = "broken";
        slot.CardInstanceId = null;
        owner.HandCardInstanceIds.Add(cardInstanceId);
        card.Zone = "hand";
        card.ZoneIndex = owner.HandCardInstanceIds.Count - 1;
        card.Visibility = "owner_only";
        card.ZoneSequence += 1;
    }

    private static CombatFixture CreateInterventionFixture(
        string matchId,
        int defenderZoneSequence = 1) => CreateFixture(
            matchId,
            board:
            [
                Board($"{matchId}-attacker", PlainEntityCardId, "player_1", DomainRow.Horizon, 5, "active", 1),
                Board($"{matchId}-defender", PlainEntityCardId, "player_2", DomainRow.Horizon, 1, "active", 1,
                    defenderZoneSequence),
                Board($"{matchId}-target", PlainEntityCardId, "player_2", DomainRow.Horizon, 2, "active", 1),
            ]);

    private static ActionResponse SubmitInitialAttack(
        CombatFixture fixture,
        string attackerCardInstanceId,
        string targetKindId,
        string targetId,
        string requestPrefix)
    {
        var response = SubmitAttack(
            fixture,
            AttackAction(fixture, "player_1"),
            $"{requestPrefix}-attack",
            attackerCardInstanceId,
            targetKindId,
            targetId);
        True(response.Accepted, $"{requestPrefix} attack declaration failed.");
        return response;
    }

    private static ActionResponse CloseFirstCombatReaction(
        CombatFixture fixture,
        string attackerCardInstanceId,
        string targetKindId,
        string targetId,
        string requestPrefix)
    {
        SubmitInitialAttack(
            fixture,
            attackerCardInstanceId,
            targetKindId,
            targetId,
            requestPrefix);
        return CloseOpenReaction(fixture, $"{requestPrefix}-attack-reaction");
    }

    private static ActionResponse OpenInterventionChoice(
        CombatFixture fixture,
        string attackerCardInstanceId,
        string targetKindId,
        string targetId,
        string requestPrefix)
    {
        var response = CloseFirstCombatReaction(
            fixture,
            attackerCardInstanceId,
            targetKindId,
            targetId,
            requestPrefix);
        Equal(CombatRuleIds.InterventionChoiceStage, fixture.State.PendingCombat?.StageId,
            $"{requestPrefix} did not open intervention_choice.");
        return response;
    }

    private static ActionResponse CloseOpenReaction(CombatFixture fixture, string requestPrefix)
    {
        var firstPlayerId = fixture.State.PriorityPlayerId;
        True(Pass(fixture, firstPlayerId, $"{requestPrefix}-pass-one").Accepted,
            $"{requestPrefix} first priority pass failed.");
        var secondPlayerId = fixture.State.PriorityPlayerId;
        var response = Pass(fixture, secondPlayerId, $"{requestPrefix}-pass-two");
        True(response.Accepted, $"{requestPrefix} second priority pass failed.");
        return response;
    }

    private static ImmutableArray<string> InterventionCandidateIds(CombatFixture fixture) =>
        InterventionAction(fixture, "player_2").PayloadSchema
            .GetProperty("defender_options")
            .EnumerateArray()
            .Select(option => option.GetProperty("defender_card_instance_id").GetString()!)
            .ToImmutableArray();

    private static string CombatCheckpointContinuity(ActionResponse response) => response.Events
        .Single(engineEvent => engineEvent.EventType == "combat_attack_checkpoint_completed")
        .Payload.GetProperty("attack_continuity_state_id").GetString()!;

    private static string? NoHitReason(ActionResponse response) => response.Events
        .Single(engineEvent => engineEvent.EventType == "combat_no_hit")
        .Payload.GetProperty("no_hit_reason_id").GetString();

    private static LegalAction InterventionAction(
        CombatFixture fixture,
        string playerId,
        bool includeDisabled = false) => fixture.Session
        .ListLegalActions(playerId, includeDisabled)
        .Actions.Single(action => action.ActionType == "intervene");

    private static LegalAction DeclineAction(CombatFixture fixture, string playerId) => fixture.Session
        .ListLegalActions(playerId)
        .Actions.Single(action => action.ActionType == "decline_intervention" && action.Enabled);

    private static ActionResponse SubmitIntervene(
        CombatFixture fixture,
        LegalAction action,
        string requestId,
        string defenderCardInstanceId,
        int? expectedStateVersion = null) => SubmitCombatAction(
            fixture,
            action,
            requestId,
            ContractJsonValue.From(new Dictionary<string, object?>
            {
                ["defender_card_instance_id"] = defenderCardInstanceId,
            }),
            expectedStateVersion);

    private static ActionResponse SubmitCombatAction(
        CombatFixture fixture,
        LegalAction action,
        string requestId,
        JsonElement payload,
        int? expectedStateVersion = null) => fixture.Session.SubmitAction(new ActionRequest(
            ContractSchemas.ActionRequest,
            requestId,
            fixture.State.MatchId,
            action.PlayerId,
            expectedStateVersion ?? fixture.State.StateVersion,
            action.ActionId,
            action.ActionType,
            payload));

    private static void MoveDomainCardToVoid(CombatFixture fixture, string cardInstanceId)
    {
        var card = fixture.State.GetCardInstance(cardInstanceId);
        var player = fixture.State.GetPlayer(card.ControllerPlayerId);
        var slots = player.Domain.GetSlots(card.DomainRow
            ?? throw new InvalidOperationException("Domain card has no row."));
        var laneIndex = card.DomainLaneIndex
            ?? throw new InvalidOperationException("Domain card has no lane.");
        Equal(cardInstanceId, slots[laneIndex], "Domain removal fixture found another occupant.");
        slots[laneIndex] = null;
        var owner = fixture.State.GetPlayer(card.OwnerPlayerId);
        card.Zone = "void";
        card.ZoneIndex = owner.VoidCardInstanceIds.Count;
        card.Visibility = "public";
        card.ZoneSequence += 1;
        card.ActivityState = null;
        card.DomainRow = null;
        card.DomainLaneIndex = null;
        card.EnteredDomainTurnNumber = null;
        card.DamageMarked = 0;
        card.ControllerPlayerId = card.OwnerPlayerId;
        owner.VoidCardInstanceIds.Add(card.CardInstanceId);
    }

    private static void MoveDomainCardWithinDomain(
        CombatFixture fixture,
        string cardInstanceId,
        DomainRow destinationRow,
        int destinationLaneIndex)
    {
        var card = fixture.State.GetCardInstance(cardInstanceId);
        var player = fixture.State.GetPlayer(card.ControllerPlayerId);
        var sourceSlots = player.Domain.GetSlots(card.DomainRow
            ?? throw new InvalidOperationException("Domain card has no row."));
        var sourceLaneIndex = card.DomainLaneIndex
            ?? throw new InvalidOperationException("Domain card has no lane.");
        Equal(cardInstanceId, sourceSlots[sourceLaneIndex],
            "Domain move fixture found another source occupant.");
        sourceSlots[sourceLaneIndex] = null;
        True(player.Domain.TryOccupy(destinationRow, destinationLaneIndex, cardInstanceId),
            "Domain move fixture could not occupy the destination.");
        card.DomainRow = destinationRow;
        card.DomainLaneIndex = destinationLaneIndex;
    }

    private static void ReturnVoidCardToDomain(
        CombatFixture fixture,
        string cardInstanceId,
        DomainRow destinationRow,
        int destinationLaneIndex)
    {
        var card = fixture.State.GetCardInstance(cardInstanceId);
        var owner = fixture.State.GetPlayer(card.OwnerPlayerId);
        True(string.Equals(card.Zone, "void", StringComparison.Ordinal),
            "Only a Void card can return in the incarnation-continuity fixture.");
        True(owner.VoidCardInstanceIds.Remove(cardInstanceId),
            "Void return fixture could not remove the card from Void.");
        True(owner.Domain.TryOccupy(destinationRow, destinationLaneIndex, cardInstanceId),
            "Void return fixture could not occupy the destination.");
        card.ControllerPlayerId = owner.PlayerId;
        card.Zone = "dominion";
        card.ZoneIndex = -1;
        card.Visibility = "public";
        card.ZoneSequence += 1;
        card.ActivityState = "active";
        card.DomainRow = destinationRow;
        card.DomainLaneIndex = destinationLaneIndex;
        card.EnteredDomainTurnNumber = fixture.State.TurnNumber;
        card.DamageMarked = 0;
    }

    private static CanonicalAbilityCatalog CreateAerialAbilityCatalog(params string[] aerialCardIds)
    {
        var package = CanonicalAbilityCatalogTests.CreatePackage();
        var sequence = 1;
        foreach (var cardId in aerialCardIds)
        {
            package = CanonicalAbilityCatalogTests.AddRecord(
                package,
                CanonicalAbilityTableIds.CardKeywords,
                CanonicalAbilityCatalogTests.Record(
                    ("card_keyword_id", $"cardkw_c4_{sequence:000}_aerial"),
                    ("card_id", cardId),
                    ("keyword_id", "aerial"),
                    ("numeric_value", null),
                    ("text_value", null),
                    ("sequence", 1)));
            sequence += 1;
        }

        return CanonicalAbilityMaterializer.Materialize(package);
    }

    private static CombatFixture CreateFixture(
        string matchId,
        int turnNumber = 2,
        bool playerTwoSealsBroken = false,
        IReadOnlyDictionary<string, (int Atk, int Hp)>? statOverrides = null,
        IReadOnlyCollection<string>? additionalAerialCardIds = null,
        int? sealCardMagnitude = null,
        int playerTwoWellspringCount = 0,
        params BoardSpec[] board)
    {
        var package = CanonicalAbilityCatalogTests.AddRecord(
            CanonicalAbilityCatalogTests.CreatePackage(),
            CanonicalAbilityTableIds.CardKeywords,
            CanonicalAbilityCatalogTests.Record(
                ("card_keyword_id", "cardkw_ign_lan_003_aerial"),
                ("card_id", AerialEntityCardId),
                ("keyword_id", "aerial"),
                ("numeric_value", null),
                ("text_value", null),
                ("sequence", 1)));
        if (additionalAerialCardIds is not null)
        {
            foreach (var cardId in additionalAerialCardIds.Order(StringComparer.Ordinal))
            {
                package = CanonicalAbilityCatalogTests.AddRecord(
                    package,
                    CanonicalAbilityTableIds.CardKeywords,
                    CanonicalAbilityCatalogTests.Record(
                        ("card_keyword_id", $"cardkw_{cardId.ToLowerInvariant().Replace('-', '_')}_aerial"),
                        ("card_id", cardId),
                        ("keyword_id", "aerial"),
                        ("numeric_value", null),
                        ("text_value", null),
                        ("sequence", 1)));
            }
        }
        if (statOverrides is not null)
        {
            foreach (var (cardId, stats) in statOverrides)
            {
                package = CanonicalAbilityCatalogTests.SetField(
                    package,
                    CanonicalAbilityTableIds.Cards,
                    cardId,
                    "atk",
                    stats.Atk);
                package = CanonicalAbilityCatalogTests.SetField(
                    package,
                    CanonicalAbilityTableIds.Cards,
                    cardId,
                    "hp",
                    stats.Hp);
            }
        }
        if (sealCardMagnitude is not null)
        {
            package = CanonicalAbilityCatalogTests.SetField(
                package,
                CanonicalAbilityTableIds.Cards,
                PlainEntityCardId,
                "magnitude",
                sealCardMagnitude.Value);
        }
        var canonicalAbilities = CanonicalAbilityMaterializer.Materialize(package);
        var canonicalCards = CanonicalCardMaterializer.Materialize(package);
        var state = new MatchState
        {
            MatchId = matchId,
            Seed = 1701,
            RuntimePackageId = "combat-foundation-runtime",
            StateVersion = 0,
            TurnNumber = turnNumber,
            Phase = CanonicalPhaseIds.Incursion,
            StartingPlayerId = "player_1",
            ActivePlayerId = "player_1",
            PriorityPlayerId = "player_1",
            Setup = new MatchSetupState
            {
                SetupModeId = "canonical",
                CurrentProphecyPlayerId = null,
                Completed = true,
            },
        };
        state.Setup.CompletedProphecyPlayerIds.AddRange(["player_1", "player_2"]);
        var playerOne = new PlayerState { PlayerId = "player_1", DeckId = "deck-player-1" };
        var playerTwo = new PlayerState { PlayerId = "player_2", DeckId = "deck-player-2" };
        state.Players.Add(playerOne);
        state.Players.Add(playerTwo);
        AddSeals(state, playerOne, broken: false);
        AddSeals(state, playerTwo, playerTwoSealsBroken);
        AddWellspringCards(state, playerTwo, playerTwoWellspringCount);
        foreach (var spec in board)
        {
            AddBoardCard(state, spec);
        }

        var runtimeCards = canonicalCards.Definitions.ToImmutableDictionary(
            definition => definition.CardId,
            definition => new RuntimeCardDefinition(
                definition.CardId,
                definition.Magnitude,
                definition.PrintedAuraCost,
                definition.Realm,
                definition.CardType switch
                {
                    "spell" => "incantation",
                    "sign" => "sigil",
                    _ => definition.CardType,
                }),
            StringComparer.Ordinal);
        var runtime = new RuntimePackageCatalog(
            state.RuntimePackageId,
            runtimeCards,
            ImmutableDictionary<string, RuntimeDeckDefinition>.Empty.WithComparers(StringComparer.Ordinal),
            CreateLookups());
        var resolver = new ReactionPolicyResolver(
            openingBindings: [],
            optionBindings:
            [
                new ReactionOptionProfileBinding(
                    CombatRuleIds.AttackReactionProfile,
                    ReactionAbilityId,
                    ReactionPolicyIds.StandardAlternatingResponse),
                new ReactionOptionProfileBinding(
                    CombatRuleIds.DefenseReactionProfile,
                    ReactionAbilityId,
                    ReactionPolicyIds.StandardAlternatingResponse),
            ]);
        EngineSession.ValidateState(state, canonicalCards, canonicalAbilities);
        return new CombatFixture(
            new EngineSession(state, runtime, canonicalAbilities, canonicalCards, resolver),
            state,
            runtime,
            canonicalCards,
            canonicalAbilities);
    }

    private static RuntimeLookupCatalog CreateLookups()
    {
        var realms = new[] { "ignis", "aqua", "terra", "lux", "umbra", "ventus", "aether" }
            .ToImmutableDictionary(value => value, value => value, StringComparer.Ordinal);
        var cardTypes = new[] { "entity", "incantation", "ritual", "sigil", "plane" }
            .ToImmutableDictionary(value => value, value => value, StringComparer.Ordinal);
        return new RuntimeLookupCatalog(ImmutableDictionary.CreateRange(
            StringComparer.Ordinal,
            new Dictionary<string, RuntimeLookupGroup>
            {
                ["realm"] = new("realm", realms),
                ["card_type"] = new("card_type", cardTypes),
            }));
    }

    private static void AddSeals(MatchState state, PlayerState player, bool broken)
    {
        for (var laneIndex = 0; laneIndex < DomainState.LaneCount; laneIndex += 1)
        {
            var cardInstanceId = $"{player.PlayerId}-hidden-seal-{laneIndex + 1:00}";
            player.SealSlots.Add(new SealSlotState
            {
                SealSlotId = $"seal:{player.PlayerId}:{laneIndex + 1:00}",
                OwnerPlayerId = player.PlayerId,
                LaneIndex = laneIndex,
                Status = broken ? "broken" : "standing",
                CardInstanceId = broken ? null : cardInstanceId,
            });
            if (broken)
            {
                continue;
            }

            state.CardInstances.Add(cardInstanceId, new CardInstanceState
            {
                CardInstanceId = cardInstanceId,
                CardId = PlainEntityCardId,
                OwnerPlayerId = player.PlayerId,
                ControllerPlayerId = player.PlayerId,
                Zone = "seal",
                ZoneIndex = laneIndex,
                Visibility = "hidden",
                CreatedSequence = state.CardInstances.Count + 1,
                ZoneSequence = 1,
                InitialZone = "seal",
            });
        }
    }

    private static void AddWellspringCards(MatchState state, PlayerState player, int count)
    {
        for (var index = 0; index < count; index += 1)
        {
            var cardInstanceId = $"{player.PlayerId}-wellspring-{index + 1:00}";
            player.WellspringCardInstanceIds.Add(cardInstanceId);
            state.CardInstances.Add(cardInstanceId, new CardInstanceState
            {
                CardInstanceId = cardInstanceId,
                CardId = PlainEntityCardId,
                OwnerPlayerId = player.PlayerId,
                ControllerPlayerId = player.PlayerId,
                Zone = "wellspring",
                ZoneIndex = index,
                Visibility = "owner_only",
                CreatedSequence = state.CardInstances.Count + 1,
                ZoneSequence = 1,
                InitialZone = "wellspring",
                ActivityState = "active",
            });
        }
    }

    private static void AddBoardCard(MatchState state, BoardSpec spec)
    {
        var player = state.GetPlayer(spec.PlayerId);
        True(
            player.Domain.TryOccupy(spec.Row, spec.LaneIndex, spec.CardInstanceId),
            $"Combat fixture Domain placement failed: {spec.CardInstanceId}");
        state.CardInstances.Add(spec.CardInstanceId, new CardInstanceState
        {
            CardInstanceId = spec.CardInstanceId,
            CardId = spec.CardId,
            OwnerPlayerId = spec.PlayerId,
            ControllerPlayerId = spec.PlayerId,
            Zone = "dominion",
            ZoneIndex = -1,
            Visibility = "public",
            CreatedSequence = state.CardInstances.Count + 1,
            ZoneSequence = spec.ZoneSequence,
            InitialZone = "dominion",
            ActivityState = spec.ActivityState,
            DomainRow = spec.Row,
            DomainLaneIndex = spec.LaneIndex,
            EnteredDomainTurnNumber = spec.EnteredDomainTurnNumber,
            DamageMarked = spec.DamageMarked,
        });
    }

    private static LegalAction AttackAction(CombatFixture fixture, string playerId) =>
        fixture.Session.ListLegalActions(playerId, includeDisabled: true).Actions.Single(action =>
            action.ActionType == "attack");

    private static ImmutableArray<AttackChoice> AttackChoices(CombatFixture fixture)
    {
        var action = AttackAction(fixture, "player_1");
        return action.PayloadSchema.GetProperty("attack_options").EnumerateArray()
            .Select(option => new AttackChoice(
                option.GetProperty("attacker_card_instance_id").GetString()!,
                option.GetProperty("target_kind_id").GetString()!,
                option.GetProperty("target_id").GetString()!))
            .ToImmutableArray();
    }

    private static ImmutableHashSet<string> EntityTargetIds(CombatFixture fixture) =>
        AttackChoices(fixture)
            .Where(choice => choice.TargetKindId == CombatRuleIds.EntityTargetKind)
            .Select(choice => choice.TargetId)
            .ToImmutableHashSet(StringComparer.Ordinal);

    private static ActionResponse SubmitAttack(
        CombatFixture fixture,
        LegalAction action,
        string requestId,
        string attackerCardInstanceId,
        string targetKindId,
        string targetId,
        int? expectedStateVersion = null) => fixture.Session.SubmitAction(new ActionRequest(
            ContractSchemas.ActionRequest,
            requestId,
            fixture.State.MatchId,
            action.PlayerId,
            expectedStateVersion ?? fixture.State.StateVersion,
            action.ActionId,
            action.ActionType,
            ContractJsonValue.From(new Dictionary<string, object?>
            {
                ["attacker_card_instance_id"] = attackerCardInstanceId,
                ["target_kind_id"] = targetKindId,
                ["target_id"] = targetId,
            })));

    private static ActionResponse Pass(CombatFixture fixture, string playerId, string requestId)
    {
        var action = fixture.Session.ListLegalActions(playerId).Actions.Single(item =>
            item.ActionType == "pass_priority" && item.Enabled);
        return fixture.Session.SubmitAction(new ActionRequest(
            ContractSchemas.ActionRequest,
            requestId,
            fixture.State.MatchId,
            playerId,
            fixture.State.StateVersion,
            action.ActionId,
            action.ActionType,
            ContractJsonValue.EmptyObject()));
    }

    private static ActionResponse React(
        CombatFixture fixture,
        string playerId,
        string sourceCardInstanceId,
        string targetCardInstanceId,
        string requestId)
    {
        var action = fixture.Session.ListLegalActions(playerId).Actions.Single(item =>
            item.ActionType == "react" && item.Enabled);
        var option = action.PayloadSchema.GetProperty("reaction_options").EnumerateArray().Single(item =>
            item.GetProperty("source_card_instance_id").GetString() == sourceCardInstanceId);
        return fixture.Session.SubmitAction(new ActionRequest(
            ContractSchemas.ActionRequest,
            requestId,
            fixture.State.MatchId,
            playerId,
            fixture.State.StateVersion,
            action.ActionId,
            action.ActionType,
            ContractJsonValue.From(new ReactActionPayload(
                option.GetProperty("reaction_option_id").GetString()!,
                [new CanonicalTargetSelectionPayload(ReactionTargetId, [targetCardInstanceId])]))));
    }

    private static void AssertNoLegalAttack(CombatFixture fixture, string message) =>
        False(AttackAction(fixture, "player_1").Enabled, message);

    private static string Fingerprint(CombatFixture fixture) =>
        JsonSerializer.Serialize(fixture.Session.GetDebugSnapshot());

    private static BoardSpec Board(
        string cardInstanceId,
        string cardId,
        string playerId,
        DomainRow row,
        int laneIndex,
        string activityState,
        int enteredDomainTurnNumber,
        int zoneSequence = 1,
        int damageMarked = 0) => new(
            cardInstanceId,
            cardId,
            playerId,
            row,
            laneIndex,
            activityState,
            enteredDomainTurnNumber,
            zoneSequence,
            damageMarked);

    private static void ThrowsState(Action action, string expectedMessagePart, string message)
    {
        try
        {
            action();
        }
        catch (EngineStateException exception)
        {
            True(exception.Message.Contains(expectedMessagePart, StringComparison.OrdinalIgnoreCase), message);
            return;
        }

        throw new InvalidOperationException(message);
    }

    private static T NotNull<T>(T? value, string message) where T : class =>
        value ?? throw new InvalidOperationException(message);

    private static T Single<T>(IEnumerable<T> values)
    {
        var materialized = values.ToArray();
        Equal(1, materialized.Length, "Expected exactly one item.");
        return materialized[0];
    }

    private static void SequenceEqual<T>(IEnumerable<T> expected, IEnumerable<T> actual, string message)
    {
        var expectedItems = expected.ToArray();
        var actualItems = actual.ToArray();
        if (!expectedItems.SequenceEqual(actualItems))
        {
            throw new InvalidOperationException(
                $"{message} Expected=[{string.Join(',', expectedItems)}]; Actual=[{string.Join(',', actualItems)}]");
        }
    }

    private static void Equal<T>(T expected, T actual, string message)
    {
        if (!EqualityComparer<T>.Default.Equals(expected, actual))
        {
            throw new InvalidOperationException($"{message} Expected={expected}; Actual={actual}");
        }
    }

    private static void True(bool condition, string message)
    {
        if (!condition)
        {
            throw new InvalidOperationException(message);
        }
    }

    private static void False(bool condition, string message) => True(!condition, message);

    private sealed record CombatFixture(
        EngineSession Session,
        MatchState State,
        RuntimePackageCatalog Runtime,
        CanonicalCardCatalog CanonicalCards,
        CanonicalAbilityCatalog CanonicalAbilities);

    private sealed record BoardSpec(
        string CardInstanceId,
        string CardId,
        string PlayerId,
        DomainRow Row,
        int LaneIndex,
        string ActivityState,
        int EnteredDomainTurnNumber,
        int ZoneSequence,
        int DamageMarked);

    private sealed record AttackChoice(
        string AttackerCardInstanceId,
        string TargetKindId,
        string TargetId);
}
