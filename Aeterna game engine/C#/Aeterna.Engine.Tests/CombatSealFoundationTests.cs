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
        Equal(CombatRuleIds.AttackCheckpointStage, combat.StageId, "Combat did not enter explicit post-reaction checkpoint.");
        Equal(2, combat.StageSequence, "Combat checkpoint sequence is invalid.");
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
        Equal(CombatRuleIds.AttackCheckpointStage, summary.GetProperty("stage").GetString(), "Projected Combat checkpoint stage is invalid.");
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
        Equal(CombatRuleIds.AttackCheckpointStage, fixture.State.PendingCombat?.StageId, "LIFO closure did not resume Combat.");
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
