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
                Board("checkpoint-attacker", PlainEntityCardId, "player_1", DomainRow.Horizon, 0, "active", 1),
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
        var combat = NotNull(fixture.State.PendingCombat, "PendingCombat disappeared after first window closure.");
        Equal(CombatRuleIds.DefenseCheckpointStage, combat.StageId, "Combat did not advance through the attack checkpoint.");
        Equal(3, combat.StageSequence, "Combat checkpoint sequence is invalid.");
        Equal(CombatRuleIds.DefenseDecisionUnavailable, combat.DefenseDecisionStateId,
            "No-candidate Combat did not record the unavailable intervention decision.");
        Equal("checkpoint-target", combat.OriginalTarget.PublicTargetId, "Reaction closure rewrote OriginalTarget.");
        Equal("exhausted", fixture.State.GetCardInstance("checkpoint-attacker").ActivityState,
            "Reaction closure rewound the committed attacker exhaustion.");
        True(closure.Events.Any(engineEvent => engineEvent.EventType == "combat_attack_reaction_completed"),
            "Combat checkpoint transition event is missing.");

        foreach (var playerId in new[] { "player_1", "player_2" })
        {
            var blocked = fixture.Session.ListLegalActions(playerId, includeDisabled: true).Actions;
            True(blocked.Length > 0, "Combat checkpoint exposed an empty diagnostic action space.");
            True(blocked.All(action => !action.Enabled && action.DisabledReason == "combat_pending"),
                "Normal gameplay remained enabled at the Combat checkpoint.");
        }

        var summary = fixture.Session.GetPlayerSnapshot("player_1").PendingDecisionSummary;
        Equal("combat", summary.GetProperty("pending_type").GetString(), "Post-window pending summary lost Combat state.");
        Equal(CombatRuleIds.DefenseCheckpointStage, summary.GetProperty("stage").GetString(), "Projected Combat checkpoint stage is invalid.");
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
        Equal(CombatRuleIds.DefenseCheckpointStage, fixture.State.PendingCombat?.StageId, "LIFO closure did not resume Combat.");
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
        CloseFirstCombatReaction(none, "none-attacker", CombatRuleIds.EntityTargetKind, "none-target", "none");
        Equal(CombatRuleIds.DefenseCheckpointStage, none.State.PendingCombat?.StageId,
            "No-candidate Combat opened an unnecessary decision.");
        False(none.Session.ListLegalActions("player_2", includeDisabled: true).Actions
            .Any(action => action.ActionType is "intervene" or "decline_intervention"),
            "No-candidate Combat exposed intervention actions.");
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
        CloseFirstCombatReaction(ward, "ward-c3-attacker", CombatRuleIds.EntityTargetKind, "ward-c3-target", "ward-c3");
        True(ward.State.PendingCombat?.OriginalTargetHadWardAtAttackCommit == true,
            "Ward target commitment was not retained.");
        Equal(CombatRuleIds.DefenseCheckpointStage, ward.State.PendingCombat?.StageId,
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
        Equal(CombatRuleIds.DefenseCheckpointStage, aeternal.State.PendingCombat?.StageId,
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
        CloseOpenReaction(lostTarget, "lost-target");
        Equal(CombatRuleIds.AttackContinuityTargetLost, lostTarget.State.PendingCombat?.AttackContinuityStateId,
            "OriginalTarget leave-and-return continuity loss was not explicit.");
        Equal("lost-target-original", lostTarget.State.PendingCombat?.OriginalTarget.PublicTargetId,
            "Continuity loss retargeted the attack.");
        Equal(CombatRuleIds.DefenseCheckpointStage, lostTarget.State.PendingCombat?.StageId,
            "Lost OriginalTarget opened intervention.");

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
        CloseOpenReaction(movedTarget, "moved-target");
        Equal(CombatRuleIds.AttackContinuityTargetLost, movedTarget.State.PendingCombat?.AttackContinuityStateId,
            "OriginalTarget row/lane continuity change was not detected.");

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
        CloseOpenReaction(lostAttacker, "lost-attacker");
        Equal(CombatRuleIds.AttackContinuityAttackerLost,
            lostAttacker.State.PendingCombat?.AttackContinuityStateId,
            "Attacker incarnation continuity loss was not explicit.");
        Equal(CombatRuleIds.DefenseCheckpointStage, lostAttacker.State.PendingCombat?.StageId,
            "Lost attacker opened intervention.");

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
        var combat = NotNull(fixture.State.PendingCombat, "Decline removed PendingCombat.");
        Equal(CombatRuleIds.DefenseCheckpointStage, combat.StageId, "Decline did not reach defense_checkpoint.");
        Equal(4, combat.StageSequence, "Decline stage sequence is invalid.");
        Equal(CombatRuleIds.DefenseDecisionDeclined, combat.DefenseDecisionStateId,
            "Decline state was not retained explicitly.");
        False(combat.DefenseCommitted, "Decline created DefenseCommit.");
        Equal(null, combat.DefenderRef, "Decline created a defender binding.");
        Equal(null, fixture.State.ReactionWindow, "Decline opened a defense ReactionWindow.");
        True(response.Events.Single().EventType == "intervention_declined",
            "Decline semantic event is missing.");
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
        var combat = NotNull(fixture.State.PendingCombat, "Second window closure removed PendingCombat.");
        Equal(CombatRuleIds.DefenseCheckpointStage, combat.StageId,
            "Second window did not resume at defense_checkpoint.");
        Equal(5, combat.StageSequence, "Committed defense checkpoint sequence is invalid.");
        True(combat.DefenseCommitted, "Second window closure erased DefenseCommit.");
        True(closure.Events.Any(engineEvent => engineEvent.EventType == "combat_defense_reaction_completed"),
            "Defense reaction completion event is missing.");
        foreach (var playerId in new[] { "player_1", "player_2" })
        {
            var blocked = fixture.Session.ListLegalActions(playerId, includeDisabled: true).Actions;
            True(blocked.All(action => !action.Enabled && action.DisabledReason == "combat_pending"),
                "Normal gameplay became available at defense_checkpoint.");
        }
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
        CloseOpenReaction(defenderGone, "defender-gone");
        var goneCombat = NotNull(defenderGone.State.PendingCombat, "Defender disappearance removed Combat.");
        True(goneCombat.DefenseCommitted, "Defender disappearance rewound DefenseCommit.");
        Equal("combat-defense-gone-defender", goneCombat.DefenderRef?.ObjectId,
            "Defender disappearance erased committed identity.");
        Equal("combat-defense-gone-target", goneCombat.OriginalTarget.PublicTargetId,
            "Defender disappearance restored or replaced OriginalTarget.");
        Equal(CombatRuleIds.DefenseCheckpointStage, goneCombat.StageId,
            "Defender disappearance prevented defense checkpoint continuation.");

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
        CloseOpenReaction(targetGone, "target-gone-after-defense");
        var targetGoneCombat = NotNull(targetGone.State.PendingCombat,
            "OriginalTarget disappearance removed Combat.");
        True(targetGoneCombat.DefenseCommitted,
            "OriginalTarget disappearance invalidated committed defense.");
        Equal("combat-original-target-gone-defender", targetGoneCombat.DefenderRef?.ObjectId,
            "OriginalTarget disappearance erased defender binding.");
        Equal("combat-original-target-gone-target", targetGoneCombat.OriginalTarget.PublicTargetId,
            "OriginalTarget identity was not retained beside DefenderRef.");

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

    private static CombatFixture CreateFixture(
        string matchId,
        int turnNumber = 2,
        bool playerTwoSealsBroken = false,
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
        int zoneSequence = 1) => new(
            cardInstanceId,
            cardId,
            playerId,
            row,
            laneIndex,
            activityState,
            enteredDomainTurnNumber,
            zoneSequence);

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
        int ZoneSequence);

    private sealed record AttackChoice(
        string AttackerCardInstanceId,
        string TargetKindId,
        string TargetId);
}
