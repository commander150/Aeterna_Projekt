using System.Collections.Immutable;
using System.Text.Json;
using Aeterna.Engine;
using Aeterna.Engine.Contracts;
using Aeterna.Engine.Rules;
using Aeterna.Engine.Runtime;
using Aeterna.Engine.State;

internal static class CanonicalDamageExecutionTests
{
    private const string Target003 = "target_ign_lan_003_01_enemy_entity";
    private const string Target031 = "target_ign_lan_031_01_enemy_entities";
    private const string Target044 = "target_aqu_art_044_01_enemy_horizont_entities";

    internal static void DamageMarkedAndCommittedStateInvariants()
    {
        var fixture = CreateFixture(
            [],
            [Board("target", "IGN-HAM-001", DomainRow.Horizon, 0)],
            hpOverrides: new Dictionary<string, int> { ["IGN-HAM-001"] = 2 });
        var target = fixture.State.GetCardInstance("target");
        Equal(0, target.DamageMarked, "New Entity instance damage must start at zero.");

        target.DamageMarked = -1;
        ThrowsState(() => EngineSession.ValidateState(fixture.State, fixture.Cards));
        target.DamageMarked = 2;
        ThrowsState(() => EngineSession.ValidateState(fixture.State, fixture.Cards));
        target.DamageMarked = 1;
        EngineSession.ValidateState(fixture.State, fixture.Cards);

        fixture.State.GetPlayer("player_2").Domain.HorizonCardInstanceIds[0] = null;
        fixture.State.GetPlayer("player_2").VoidCardInstanceIds.Add(target.CardInstanceId);
        target.Zone = "void";
        target.ZoneIndex = 0;
        target.ActivityState = null;
        target.DomainRow = null;
        target.DomainLaneIndex = null;
        target.EnteredDomainTurnNumber = null;
        ThrowsState(() => EngineSession.ValidateState(fixture.State, fixture.Cards));
    }

    internal static void IgnLan003RowUnrestrictedDamageAndLethalFlow()
    {
        var survivor = CreateFixture(
            [Hand("source", "IGN-LAN-003", "entity")],
            [
                Board("horizon_target", "IGN-HAM-001", DomainRow.Horizon, 0),
                Board("zenith_target", "IGN-HAM-005", DomainRow.Zenith, 1),
            ],
            hpOverrides: new Dictionary<string, int>
            {
                ["IGN-HAM-001"] = 2,
                ["IGN-HAM-005"] = 2,
            });
        var play = Play(survivor, "source", "horizon", 2, null);
        True(play.Accepted, "IGN-LAN-003 Entity play was rejected.");
        var pending = Single(survivor.State.PendingTriggerWindow!.PendingTriggers);
        var resolved = Resolve(survivor, pending.PendingTriggerId, Target003, ["zenith_target"]);
        True(resolved.Accepted, "IGN-LAN-003 Zenith target resolution was rejected.");
        Equal(1, survivor.State.GetCardInstance("zenith_target").DamageMarked, "IGN-LAN-003 did not mark one direct damage.");
        Equal("dominion", survivor.State.GetCardInstance("source").Zone, "Riadó source left Dominion.");
        Equal(2, survivor.State.StateVersion, "IGN-LAN-003 play plus resolution state version is invalid.");
        SequenceEqual(
            ["damage_dealt", "canonical_ability_resolved"],
            resolved.Events.Select(item => item.EventType),
            "IGN-LAN-003 nonlethal event order is invalid.");

        var lethal = CreateFixture(
            [Hand("lethal_source", "IGN-LAN-003", "entity")],
            [Board("lethal_target", "IGN-HAM-001", DomainRow.Horizon, 0)],
            hpOverrides: new Dictionary<string, int> { ["IGN-HAM-001"] = 1 });
        True(Play(lethal, "lethal_source", "zenith", 2, null).Accepted, "Lethal Riadó source play was rejected.");
        var lethalPending = Single(lethal.State.PendingTriggerWindow!.PendingTriggers);
        var lethalResponse = Resolve(lethal, lethalPending.PendingTriggerId, Target003, ["lethal_target"]);
        True(lethalResponse.Accepted, "Lethal IGN-LAN-003 resolution was rejected.");
        Equal(null, lethal.State.GetPlayer("player_2").Domain.HorizonCardInstanceIds[0], "Lethal target still occupies Domain.");
        SequenceEqual(["lethal_target"], lethal.State.GetPlayer("player_2").VoidCardInstanceIds, "Lethal target did not enter owner Void.");
        var destroyed = lethal.State.GetCardInstance("lethal_target");
        Equal("void", destroyed.Zone, "Lethal target zone is invalid.");
        Equal(0, destroyed.DamageMarked, "Leaving Dominion did not clear damage.");
        Equal(null, destroyed.ActivityState, "Destroyed Entity retained activity state.");
        SequenceEqual(
            ["damage_dealt", "entity_destroyed", "card_zone_changed", "canonical_ability_resolved"],
            lethalResponse.Events.Select(item => item.EventType),
            "Lethal semantic event order is invalid.");
        Equal(true, lethalResponse.Events[0].Payload.GetProperty("lethal").GetBoolean(), "Damage event did not expose lethal result.");
        Equal("damage_kind_direct", lethalResponse.Events[0].Payload.GetProperty("damage_kind_id").GetString(), "Damage kind is not canonical direct damage.");
    }

    internal static void IgnLan031PlayedDamageIsAtomicAndCardinalityControlled()
    {
        var fixture = CreateFixture(
            [
                Hand("ritual", "IGN-LAN-031", "ritual"),
                Hand("ritual_second", "IGN-LAN-031", "ritual"),
            ],
            [Board("target", "IGN-HAM-001", DomainRow.Zenith, 0)],
            hpOverrides: new Dictionary<string, int> { ["IGN-HAM-001"] = 3 });
        var response = Play(fixture, "ritual", null, null, Selection(Target031, ["target"]));
        True(response.Accepted, "IGN-LAN-031 played resolution was rejected.");
        Equal(2, fixture.State.GetCardInstance("target").DamageMarked, "Played Ritual damage is invalid.");
        Equal("void", fixture.State.GetCardInstance("ritual").Zone, "Played Ritual source did not enter Void.");
        SequenceEqual(
            ["damage_dealt", "canonical_ability_resolved", "zone_move"],
            response.Events.Select(item => item.EventType),
            "Played damage/source movement event order is invalid.");
        var cumulative = Play(fixture, "ritual_second", null, null, Selection(Target031, ["target"]));
        True(cumulative.Accepted, "Second cumulative direct-damage resolution was rejected.");
        var cumulativeDamage = cumulative.Events[0].Payload;
        Equal(2, cumulativeDamage.GetProperty("accumulated_damage_before").GetInt32(), "Cumulative damage_before is invalid.");
        Equal(4, cumulativeDamage.GetProperty("accumulated_damage_after").GetInt32(), "Overkill damage_after is invalid.");
        Equal(true, cumulativeDamage.GetProperty("lethal").GetBoolean(), "Overkill damage was not lethal.");
        Equal("void", fixture.State.GetCardInstance("target").Zone, "Cumulative overkill did not move target to Void.");

        var zero = CreateFixture(
            [Hand("ritual_zero", "IGN-LAN-031", "ritual")],
            [Board("untouched", "IGN-HAM-001", DomainRow.Horizon, 0)],
            hpOverrides: new Dictionary<string, int> { ["IGN-HAM-001"] = 3 });
        var zeroResponse = Play(zero, "ritual_zero", null, null, Selection(Target031, []));
        True(zeroResponse.Accepted, "Canonical 0..2 selection rejected zero targets.");
        Equal(0, zero.State.GetCardInstance("untouched").DamageMarked, "Zero-target resolution mutated unrelated Entity.");
        SequenceEqual(
            ["canonical_ability_resolved", "zone_move"],
            zeroResponse.Events.Select(item => item.EventType),
            "Zero-target resolution event order is invalid.");

        var rejected = CreateFixture(
            [Hand("ritual_bad", "IGN-LAN-031", "ritual")],
            [
                Board("one", "IGN-HAM-001", DomainRow.Horizon, 0),
                Board("two", "IGN-HAM-005", DomainRow.Zenith, 0),
                Board("three", "IGN-LAN-003", DomainRow.Horizon, 1),
            ]);
        var before = Fingerprint(rejected);
        var duplicate = Play(rejected, "ritual_bad", null, null, Selection(Target031, ["one", "one"]));
        True(!duplicate.Accepted, "Duplicate target selection was accepted.");
        Equal("PLAY_CARD_TARGET_DUPLICATE", Single(duplicate.Diagnostics).Code, "Duplicate diagnostic is invalid.");
        Equal(before, Fingerprint(rejected), "Duplicate-target rejection was not atomic.");
        var third = Play(rejected, "ritual_bad", null, null, Selection(Target031, ["one", "two", "three"]));
        True(!third.Accepted, "Third target exceeded canonical maximum without rejection.");
        Equal("PLAY_CARD_TARGET_COUNT_INVALID", Single(third.Diagnostics).Code, "Maximum-target diagnostic is invalid.");
        Equal(before, Fingerprint(rejected), "Maximum-target rejection was not atomic.");
    }

    internal static void AquArt044SimulatesExhaustThenDamageAcrossTargets()
    {
        var fixture = CreateFixture(
            [Hand("spell", "AQU-ART-044", "incantation")],
            [
                Board("lethal", "IGN-HAM-001", DomainRow.Horizon, 0),
                Board("survivor", "IGN-HAM-005", DomainRow.Horizon, 1),
            ],
            hpOverrides: new Dictionary<string, int>
            {
                ["IGN-HAM-001"] = 2,
                ["IGN-HAM-005"] = 3,
            });
        var response = Play(
            fixture,
            "spell",
            null,
            null,
            Selection(Target044, ["survivor", "lethal"]));
        True(response.Accepted, "AQU-ART-044 multi-target resolution was rejected.");
        var lethal = fixture.State.GetCardInstance("lethal");
        var survivor = fixture.State.GetCardInstance("survivor");
        Equal("void", lethal.Zone, "First multi-target Entity did not make its lethal transition.");
        Equal(0, lethal.DamageMarked, "Lethal transition did not clear accumulated damage.");
        Equal("dominion", survivor.Zone, "Surviving multi-target Entity left Dominion.");
        Equal("exhausted", survivor.ActivityState, "Surviving target did not retain prior exhaust effect.");
        Equal(2, survivor.DamageMarked, "Surviving target damage is invalid.");
        SequenceEqual(
            [
                "card_activity_changed",
                "card_activity_changed",
                "damage_dealt",
                "entity_destroyed",
                "card_zone_changed",
                "damage_dealt",
                "canonical_ability_resolved",
                "zone_move",
            ],
            response.Events.Select(item => item.EventType),
            "AQU-ART-044 sequence or deterministic candidate order is invalid.");
        Equal("lethal", response.Events[0].Payload.GetProperty("card_instance_id").GetString(), "Request order overrode canonical target order.");
        Equal("survivor", response.Events[1].Payload.GetProperty("card_instance_id").GetString(), "Canonical second target order is invalid.");
    }

    internal static void EndTurnIsTemporaryDissipationDamageCleanupBoundary()
    {
        var fixture = CreateFixture(
            [],
            [Board("survivor", "IGN-HAM-001", DomainRow.Horizon, 0, damageMarked: 1)],
            hpOverrides: new Dictionary<string, int> { ["IGN-HAM-001"] = 3 });
        fixture.State.Phase = CanonicalPhaseIds.Incursion;
        var action = fixture.Session.ListLegalActions("player_1").Actions.Single(item => item.ActionType == "advance_phase");
        var response = fixture.Session.SubmitAction(new ActionRequest(
            ContractSchemas.ActionRequest,
            "end-turn-cleanup",
            fixture.State.MatchId,
            "player_1",
            fixture.State.StateVersion,
            action.ActionId,
            action.ActionType,
            ContractJsonValue.EmptyObject()));
        True(response.Accepted, "Incursion-to-Distribution cleanup was rejected.");
        Equal(0, fixture.State.GetCardInstance("survivor").DamageMarked, "Survivor damage was not removed.");
        Equal("player_1", fixture.State.ActivePlayerId, "Distribution cleanup changed the active player early.");
        Equal(CanonicalPhaseIds.Distribution, fixture.State.Phase, "Cleanup did not enter Distribution.");
        SequenceEqual(
            ["phase_transition", "damage_removed"],
            response.Events.Select(item => item.EventType),
            "Distribution entry/cleanup ordering is invalid.");
        Equal(1, response.Events[1].Payload.GetProperty("removed_amount").GetInt32(), "Damage cleanup event amount is invalid.");
        Equal("distribution_phase_cleanup", response.Events[1].Payload.GetProperty("cleanup_boundary").GetString(), "Distribution boundary is undocumented in event payload.");
    }

    internal static void DamageRequiresCanonicalStatsAndProjectionIsPublic()
    {
        var noStats = CreateFixture(
            [Hand("ritual", "IGN-LAN-031", "ritual")],
            [Board("target", "IGN-HAM-001", DomainRow.Horizon, 0)],
            includeCardCatalog: false);
        var before = Fingerprint(noStats);
        var rejected = Play(noStats, "ritual", null, null, Selection(Target031, ["target"]));
        True(!rejected.Accepted, "Damage executed without canonical card-stat authority.");
        Equal("CANONICAL_CARD_STATS_REQUIRED", Single(rejected.Diagnostics).Code, "Missing-stat diagnostic is invalid.");
        Equal(before, Fingerprint(noStats), "Missing-stat rejection mutated state.");

        var projected = CreateFixture(
            [],
            [Board("public_target", "IGN-HAM-001", DomainRow.Horizon, 0, damageMarked: 1)],
            hpOverrides: new Dictionary<string, int> { ["IGN-HAM-001"] = 3 });
        foreach (var viewer in new[] { "player_1", "player_2" })
        {
            var board = projected.Session.GetPlayerSnapshot(viewer).BoardSummary;
            var occupant = board.GetProperty("players")[1]
                .GetProperty("horizon")[0]
                .GetProperty("occupant");
            Equal(3, occupant.GetProperty("effective_max_hp").GetInt32(), "Public effective HP projection is invalid.");
            Equal(1, occupant.GetProperty("damage_marked").GetInt32(), "Public damage projection is invalid.");
            Equal(2, occupant.GetProperty("remaining_hp").GetInt32(), "Derived remaining HP projection is invalid.");
        }

        var nonEntity = new CardInstanceState
        {
            CardInstanceId = "not-an-entity",
            CardId = "AQU-ART-044",
            OwnerPlayerId = "player_1",
            ControllerPlayerId = "player_1",
            Zone = "hand",
            ZoneIndex = 0,
            Visibility = "owner_only",
            CreatedSequence = 1,
            ZoneSequence = 1,
            InitialZone = "hand",
        };
        ThrowsState(() => CanonicalVitals.GetEffectiveMaxHp(nonEntity, projected.Cards));
    }

    private static DamageFixture CreateFixture(
        IReadOnlyList<HandCard> handCards,
        IReadOnlyList<BoardCard> boardCards,
        IReadOnlyDictionary<string, int>? hpOverrides = null,
        bool includeCardCatalog = true)
    {
        var package = CanonicalAbilityCatalogTests.CreatePackage();
        if (hpOverrides is not null)
        {
            foreach (var (cardId, hp) in hpOverrides)
            {
                package = CanonicalAbilityCatalogTests.SetField(
                    package,
                    CanonicalAbilityTableIds.Cards,
                    cardId,
                    "hp",
                    hp);
            }
        }

        var abilities = CanonicalAbilityMaterializer.Materialize(package);
        var cards = CanonicalCardMaterializer.Materialize(package);
        var state = new MatchState
        {
            MatchId = "damage-fixture",
            Seed = 17,
            RuntimePackageId = "damage-runtime",
            StateVersion = 0,
            TurnNumber = 1,
            Phase = CanonicalPhaseIds.Manifestation,
            StartingPlayerId = "player_1",
            ActivePlayerId = "player_1",
            PriorityPlayerId = "player_1",
        };
        var player1 = new PlayerState { PlayerId = "player_1", DeckId = "deck-1" };
        var player2 = new PlayerState { PlayerId = "player_2", DeckId = "deck-2" };
        state.Players.Add(player1);
        state.Players.Add(player2);

        var created = 0;
        foreach (var hand in handCards)
        {
            var card = new CardInstanceState
            {
                CardInstanceId = hand.InstanceId,
                CardId = hand.CardId,
                OwnerPlayerId = "player_1",
                ControllerPlayerId = "player_1",
                Zone = "hand",
                ZoneIndex = player1.HandCardInstanceIds.Count,
                Visibility = "owner_only",
                CreatedSequence = ++created,
                ZoneSequence = 1,
                InitialZone = "hand",
            };
            state.CardInstances.Add(card.CardInstanceId, card);
            player1.HandCardInstanceIds.Add(card.CardInstanceId);
        }

        foreach (var board in boardCards)
        {
            var card = new CardInstanceState
            {
                CardInstanceId = board.InstanceId,
                CardId = board.CardId,
                OwnerPlayerId = "player_2",
                ControllerPlayerId = "player_2",
                Zone = "dominion",
                ZoneIndex = -1,
                Visibility = "public",
                CreatedSequence = ++created,
                ZoneSequence = 2,
                InitialZone = "deck",
                ActivityState = "active",
                DomainRow = board.Row,
                DomainLaneIndex = board.Lane,
                EnteredDomainTurnNumber = 1,
                DamageMarked = board.DamageMarked,
            };
            state.CardInstances.Add(card.CardInstanceId, card);
            player2.Domain.GetSlots(board.Row)[board.Lane] = card.CardInstanceId;
        }

        var runtimeCards = ImmutableDictionary.CreateBuilder<string, RuntimeCardDefinition>(StringComparer.Ordinal);
        foreach (var hand in handCards)
        {
            runtimeCards[hand.CardId] = new RuntimeCardDefinition(hand.CardId, 0, 0, "ignis", hand.CardType);
        }

        foreach (var board in boardCards)
        {
            runtimeCards[board.CardId] = new RuntimeCardDefinition(board.CardId, 0, 0, "ignis", "entity");
        }

        if (runtimeCards.Count == 0)
        {
            runtimeCards["IGN-HAM-001"] = new RuntimeCardDefinition("IGN-HAM-001", 0, 0, "ignis", "entity");
        }

        var runtime = new RuntimePackageCatalog(
            state.RuntimePackageId,
            runtimeCards.ToImmutable(),
            ImmutableDictionary<string, RuntimeDeckDefinition>.Empty.WithComparers(StringComparer.Ordinal),
            CreateLookups());
        EngineSession.ValidateState(state, includeCardCatalog ? cards : null);
        var session = includeCardCatalog
            ? new EngineSession(state, runtime, abilities, cards)
            : new EngineSession(state, runtime, abilities);
        return new DamageFixture(session, state, cards);
    }

    private static RuntimeLookupCatalog CreateLookups()
    {
        var groups = ImmutableDictionary.CreateBuilder<string, RuntimeLookupGroup>(StringComparer.Ordinal);
        groups["realm"] = new RuntimeLookupGroup(
            "realm",
            ImmutableDictionary.CreateRange(StringComparer.Ordinal, new Dictionary<string, string>
            {
                ["ignis"] = "ignis",
                ["aqua"] = "aqua",
            }));
        groups["card_type"] = new RuntimeLookupGroup(
            "card_type",
            ImmutableDictionary.CreateRange(StringComparer.Ordinal, new Dictionary<string, string>
            {
                ["entity"] = "entity",
                ["incantation"] = "incantation",
                ["ritual"] = "ritual",
                ["sigil"] = "sigil",
                ["plane"] = "plane",
            }));
        return new RuntimeLookupCatalog(groups.ToImmutable());
    }

    private static ActionResponse Play(
        DamageFixture fixture,
        string cardInstanceId,
        string? row,
        int? lane,
        ImmutableArray<CanonicalTargetSelectionPayload>? targetSelections)
    {
        var action = fixture.Session.ListLegalActions("player_1", includeDisabled: true).Actions
            .Single(item => item.ActionType == "play_card");
        return fixture.Session.SubmitAction(new ActionRequest(
            ContractSchemas.ActionRequest,
            $"play-{cardInstanceId}",
            fixture.State.MatchId,
            "player_1",
            fixture.State.StateVersion,
            action.ActionId,
            action.ActionType,
            ContractJsonValue.From(new PlayCardActionPayload(
                cardInstanceId,
                row,
                lane,
                ImmutableArray<string>.Empty,
                targetSelections))));
    }

    private static ActionResponse Resolve(
        DamageFixture fixture,
        string pendingTriggerId,
        string targetId,
        ImmutableArray<string> targetCardInstanceIds)
    {
        var action = fixture.Session.ListLegalActions("player_1").Actions
            .Single(item => item.ActionType == "resolve_triggered_ability");
        return fixture.Session.SubmitAction(new ActionRequest(
            ContractSchemas.ActionRequest,
            $"resolve-{pendingTriggerId}",
            fixture.State.MatchId,
            "player_1",
            fixture.State.StateVersion,
            action.ActionId,
            action.ActionType,
            ContractJsonValue.From(new ResolveTriggeredAbilityActionPayload(
                pendingTriggerId,
                Selection(targetId, targetCardInstanceIds)))));
    }

    private static ImmutableArray<CanonicalTargetSelectionPayload> Selection(
        string targetId,
        ImmutableArray<string> cardInstanceIds) =>
        [new CanonicalTargetSelectionPayload(targetId, cardInstanceIds)];

    private static string Fingerprint(DamageFixture fixture) =>
        JsonSerializer.Serialize(fixture.Session.GetDebugSnapshot());

    private static void ThrowsState(Action action)
    {
        try
        {
            action();
        }
        catch (EngineStateException)
        {
            return;
        }

        throw new InvalidOperationException("Expected an authoritative state rejection.");
    }

    private static T Single<T>(IEnumerable<T> values)
    {
        var materialized = values.ToArray();
        Equal(1, materialized.Length, "Expected exactly one item.");
        return materialized[0];
    }

    private static void SequenceEqual<T>(IEnumerable<T> expected, IEnumerable<T> actual, string message)
    {
        if (!expected.SequenceEqual(actual))
        {
            throw new InvalidOperationException(
                $"{message} Expected={string.Join(',', expected)}; Actual={string.Join(',', actual)}");
        }
    }

    private static void True(bool condition, string message)
    {
        if (!condition)
        {
            throw new InvalidOperationException(message);
        }
    }

    private static void Equal<T>(T expected, T actual, string message)
    {
        if (!EqualityComparer<T>.Default.Equals(expected, actual))
        {
            throw new InvalidOperationException($"{message} Expected={expected}; Actual={actual}");
        }
    }

    private sealed record HandCard(string InstanceId, string CardId, string CardType);

    private sealed record BoardCard(
        string InstanceId,
        string CardId,
        DomainRow Row,
        int Lane,
        int DamageMarked);

    private sealed record DamageFixture(
        EngineSession Session,
        MatchState State,
        CanonicalCardCatalog Cards);

    private static HandCard Hand(string instanceId, string cardId, string cardType) =>
        new(instanceId, cardId, cardType);

    private static BoardCard Board(
        string instanceId,
        string cardId,
        DomainRow row,
        int lane,
        int damageMarked = 0) =>
        new(instanceId, cardId, row, lane, damageMarked);
}
