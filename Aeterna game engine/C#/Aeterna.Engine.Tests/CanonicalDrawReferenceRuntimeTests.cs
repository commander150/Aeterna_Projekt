using System.Collections.Immutable;
using System.Text.Json;
using Aeterna.Engine;
using Aeterna.Engine.Contracts;
using Aeterna.Engine.Rules;
using Aeterna.Engine.Runtime;
using Aeterna.Engine.State;

internal static class CanonicalDrawReferenceRuntimeTests
{
    private const string EnemyTargetId = "target_ign_ham_020_01_enemy_entity";
    private const string SourceTargetId = "target_ign_ham_020_01_source_card";
    private const string ControllerTargetId = "target_aqu_mor_037_01_controller";
    private const string WardQueryTargetId = "target_aqu_mor_037_01_ward_horizont_query";

    internal static void IgnHam020PublicFlowUsesAutomaticSourceIdentity()
    {
        var fixture = CreateFixture(
            ["IGN-HAM-020"],
            deckCount: 0,
            auraCount: 3,
            [
                Board("duplicate", "IGN-HAM-020", "player_1", DomainRow.Zenith, 1),
                Board("enemy", "FIXTURE-ENTITY-HP5", "player_2", DomainRow.Horizon, 0),
            ]);
        var sourceId = fixture.HandSourceIds[0];
        var play = PlayEntity(fixture, sourceId, DomainRow.Horizon, 0, auraPayment: 2);
        True(play.Accepted, "IGN-HAM-020 public entity play failed.");
        True(fixture.State.PendingTriggerWindow is not null, "IGN-HAM-020 Riadó was not pending.");

        var pendingAction = fixture.Session.ListLegalActions("player_1").Actions.Single();
        var option = pendingAction.PayloadSchema.GetProperty("pending_trigger_options")[0];
        var contracts = option.GetProperty("target_contracts");
        Equal(1, contracts.GetArrayLength(), "Automatic source reference leaked into player target contracts.");
        Equal(EnemyTargetId, contracts[0].GetProperty("target_id").GetString(), "Enemy choice contract is missing.");

        var resolve = Resolve(fixture, [new CanonicalTargetSelectionPayload(EnemyTargetId, ["enemy"])]);
        True(resolve.Accepted, "IGN-HAM-020 Riadó resolution failed.");
        Equal(2, fixture.State.GetCardInstance("enemy").DamageMarked, "Enemy did not take 2 direct damage.");
        Equal(1, fixture.State.GetCardInstance(sourceId).DamageMarked, "Ability source did not take 1 direct damage.");
        Equal(0, fixture.State.GetCardInstance("duplicate").DamageMarked, "Duplicate Card_ID confused source identity.");
        SequenceEqual(
            ["damage_dealt", "damage_dealt", "canonical_ability_resolved"],
            resolve.Events.Select(item => item.EventType),
            "IGN-HAM-020 nonlethal semantic effect order is invalid.");
    }

    internal static void IgnHam020LethalPipelinesRemainSequential()
    {
        var enemyLethal = CreateFixture(
            ["IGN-HAM-020"],
            deckCount: 0,
            auraCount: 3,
            [Board("enemy", "IGN-LAN-003", "player_2", DomainRow.Horizon, 0)]);
        var sourceId = enemyLethal.HandSourceIds[0];
        True(PlayEntity(enemyLethal, sourceId, DomainRow.Horizon, 0, 2).Accepted, "Enemy-lethal setup failed.");
        var response = Resolve(enemyLethal, [new CanonicalTargetSelectionPayload(EnemyTargetId, ["enemy"])]);
        True(response.Accepted, "Enemy-lethal resolution failed.");
        Equal("void", enemyLethal.State.GetCardInstance("enemy").Zone, "Exact-lethal enemy did not move to Void.");
        Equal("dominion", enemyLethal.State.GetCardInstance(sourceId).Zone, "Nonlethal source left Dominion.");
        SequenceEqual(
            ["damage_dealt", "entity_destroyed", "card_zone_changed", "damage_dealt", "canonical_ability_resolved"],
            response.Events.Select(item => item.EventType),
            "Enemy lethal was not completed before source self-damage.");

        var sourceLethal = CreateFixture(
            ["IGN-HAM-020"],
            deckCount: 0,
            auraCount: 3,
            [Board("enemy", "FIXTURE-ENTITY-HP5", "player_2", DomainRow.Horizon, 0)]);
        var lethalSourceId = sourceLethal.HandSourceIds[0];
        True(PlayEntity(sourceLethal, lethalSourceId, DomainRow.Horizon, 0, 2).Accepted, "Source-lethal setup failed.");
        sourceLethal.State.GetCardInstance(lethalSourceId).DamageMarked = 1;
        EngineSession.ValidateState(sourceLethal.State, sourceLethal.Cards, sourceLethal.Abilities);
        var lethalResponse = Resolve(
            sourceLethal,
            [new CanonicalTargetSelectionPayload(EnemyTargetId, ["enemy"])]);
        True(lethalResponse.Accepted, "Source-lethal resolution failed.");
        Equal(2, sourceLethal.State.GetCardInstance("enemy").DamageMarked, "Enemy first effect was not retained.");
        Equal("void", sourceLethal.State.GetCardInstance(lethalSourceId).Zone, "Exact-lethal source did not use the normal Void pipeline.");
        SequenceEqual(
            ["damage_dealt", "damage_dealt", "entity_destroyed", "card_zone_changed", "canonical_ability_resolved"],
            lethalResponse.Events.Select(item => item.EventType),
            "Source lethal event order is invalid.");

        var overkill = CreateFixture(
            ["IGN-HAM-020"],
            deckCount: 0,
            auraCount: 3,
            [Board("enemy", "IGN-HAM-001", "player_2", DomainRow.Horizon, 0)]);
        True(PlayEntity(overkill, overkill.HandSourceIds[0], DomainRow.Horizon, 0, 2).Accepted, "Overkill setup failed.");
        True(Resolve(overkill, [new CanonicalTargetSelectionPayload(EnemyTargetId, ["enemy"])]).Accepted, "Overkill resolution failed.");
        Equal("void", overkill.State.GetCardInstance("enemy").Zone, "Overkill did not use the lethal transition.");
    }

    internal static void AutomaticReferencesRejectClientSelectionsAtomically()
    {
        var triggered = CreateFixture(
            ["IGN-HAM-020"],
            deckCount: 0,
            auraCount: 3,
            [Board("enemy", "FIXTURE-ENTITY-HP5", "player_2", DomainRow.Horizon, 0)]);
        True(PlayEntity(triggered, triggered.HandSourceIds[0], DomainRow.Horizon, 0, 2).Accepted, "Triggered setup failed.");
        var before = Fingerprint(triggered);
        var badSource = Resolve(triggered,
        [
            new CanonicalTargetSelectionPayload(EnemyTargetId, ["enemy"]),
            new CanonicalTargetSelectionPayload(SourceTargetId, [triggered.HandSourceIds[0]]),
        ]);
        True(!badSource.Accepted, "Client-supplied source reference was accepted.");
        Equal("RESOLVE_TRIGGER_TARGET_SELECTION_INVALID", Single(badSource.Diagnostics).Code, "Source-reference rejection code is invalid.");
        Equal(before, Fingerprint(triggered), "Rejected source reference mutated authoritative state.");

        var played = CreateFixture(["AQU-MOR-037"], deckCount: 3, auraCount: 4, []);
        var playedBefore = Fingerprint(played);
        var badPlayer = PlayResolution(
            played,
            played.HandSourceIds[0],
            auraPayment: 3,
            [new CanonicalTargetSelectionPayload(ControllerTargetId, ImmutableArray<string>.Empty)]);
        True(!badPlayer.Accepted, "Client-supplied player reference was accepted.");
        Equal("PLAY_CARD_TARGET_SELECTION_INVALID", Single(badPlayer.Diagnostics).Code, "Player-reference rejection code is invalid.");
        Equal(playedBefore, Fingerprint(played), "Rejected player reference paid Aura or mutated zones.");
    }

    internal static void AquaMor037DrawsTwoOrThreeFromResolvedCount()
    {
        var noWard = CreateFixture(["AQU-MOR-037"], deckCount: 2, auraCount: 4, []);
        var response = PlayResolution(noWard, noWard.HandSourceIds[0], 3, ImmutableArray<CanonicalTargetSelectionPayload>.Empty);
        True(response.Accepted, "AQU-MOR-037 zero-match draw was rejected.");
        AssertDrawResult(noWard, response, expectedDraws: 2);

        var oneWard = CreateFixture(
            ["AQU-MOR-037"],
            deckCount: 3,
            auraCount: 4,
            [Board("ward", "FIXTURE-ENTITY-WARD", "player_1", DomainRow.Horizon, 0)]);
        var oneResponse = PlayResolution(oneWard, oneWard.HandSourceIds[0], 3, ImmutableArray<CanonicalTargetSelectionPayload>.Empty);
        True(oneResponse.Accepted, "AQU-MOR-037 one-match draw was rejected.");
        AssertDrawResult(oneWard, oneResponse, expectedDraws: 3);

        var manyWard = CreateFixture(
            ["AQU-MOR-037"],
            deckCount: 3,
            auraCount: 4,
            [
                Board("ward_1", "FIXTURE-ENTITY-WARD", "player_1", DomainRow.Horizon, 0),
                Board("ward_2", "FIXTURE-ENTITY-WARD", "player_1", DomainRow.Horizon, 1),
            ]);
        var manyResponse = PlayResolution(manyWard, manyWard.HandSourceIds[0], 3, ImmutableArray<CanonicalTargetSelectionPayload>.Empty);
        True(manyResponse.Accepted, "AQU-MOR-037 multi-match draw was rejected.");
        AssertDrawResult(manyWard, manyResponse, expectedDraws: 3);
    }

    internal static void EffectiveWardQueryUsesIntrinsicGrantScopeAndExpiry()
    {
        var fixture = CreateFixture(
            ["AQU-MOR-033", "AQU-MOR-037"],
            deckCount: 3,
            auraCount: 7,
            [
                Board("intrinsic", "FIXTURE-ENTITY-WARD", "player_1", DomainRow.Horizon, 0),
                Board("temporary", "IGN-LAN-003", "player_1", DomainRow.Horizon, 1),
                Board("zenith", "FIXTURE-ENTITY-WARD", "player_1", DomainRow.Zenith, 0),
                Board("opponent", "FIXTURE-ENTITY-WARD", "player_2", DomainRow.Horizon, 0),
            ]);
        True(PlayResolution(
            fixture,
            fixture.HandSourceIds[0],
            4,
            ImmutableArray<CanonicalTargetSelectionPayload>.Empty).Accepted, "AQU-MOR-033 Ward setup failed.");
        var beforeExpiry = ResolveWardCandidates(fixture);
        SequenceEqual(["intrinsic", "temporary"], beforeExpiry, "Effective Ward query scope or grant aggregation is invalid.");

        var draw = PlayResolution(
            fixture,
            fixture.HandSourceIds[1],
            3,
            ImmutableArray<CanonicalTargetSelectionPayload>.Empty);
        True(draw.Accepted, "Temporary Ward did not satisfy AQU-MOR-037 through the public API.");
        AssertDrawResult(fixture, draw, expectedDraws: 3, expectedRemainingHandCount: 3);

        var expiryFixture = CreateFixture(
            ["AQU-MOR-033", "AQU-MOR-037"],
            deckCount: 3,
            auraCount: 7,
            [Board("temporary", "IGN-LAN-003", "player_1", DomainRow.Horizon, 0)]);
        True(PlayResolution(
            expiryFixture,
            expiryFixture.HandSourceIds[0],
            4,
            ImmutableArray<CanonicalTargetSelectionPayload>.Empty).Accepted, "Expiry setup failed.");
        True(ResolveWardCandidates(expiryFixture).Contains("temporary", StringComparer.Ordinal), "Active temporary Ward was not matched.");
        True(EndTurn(expiryFixture).Accepted, "Temporary Ward expiry failed.");
        True(!ResolveWardCandidates(expiryFixture).Contains("temporary", StringComparer.Ordinal), "Expired Ward grant remained query-visible.");
    }

    internal static void DrawOrderProjectionAndPrivacyArePreserved()
    {
        var fixture = CreateFixture(["AQU-MOR-037"], deckCount: 3, auraCount: 4, []);
        var initialDeck = fixture.State.GetPlayer("player_1").DeckCardInstanceIds.ToArray();
        var response = PlayResolution(fixture, fixture.HandSourceIds[0], 3, ImmutableArray<CanonicalTargetSelectionPayload>.Empty);
        True(response.Accepted, "Draw/privacy proof play failed.");
        var hand = fixture.State.GetPlayer("player_1").HandCardInstanceIds;
        SequenceEqual(initialDeck.Take(2), hand, "Multi-card draw did not preserve top-card order or Hand append order.");
        for (var index = 0; index < hand.Count; index += 1)
        {
            var card = fixture.State.GetCardInstance(hand[index]);
            Equal("hand", card.Zone, "Drawn card zone is invalid.");
            Equal(index, card.ZoneIndex, "Drawn card ZoneIndex is invalid after source Ritual leaves Hand.");
            Equal("owner_only", card.Visibility, "Drawn card visibility is invalid.");
        }

        var ownProjection = fixture.Session.GetPlayerSnapshot("player_1");
        var opponentProjection = fixture.Session.GetPlayerSnapshot("player_2");
        Equal(2, ownProjection.Players.Single(player => player.PlayerId == "player_1").Hand.Objects.Length, "Owner projection hides drawn identities.");
        Equal(0, opponentProjection.Players.Single(player => player.PlayerId == "player_1").Hand.Objects.Length, "Opponent snapshot leaks drawn identities.");
        var opponentDrawEvents = fixture.Session.GetEvents("player_2")
            .Where(item => item.EventType == "zone_move"
                           && item.Payload.TryGetProperty("to_zone", out var toZone)
                           && string.Equals(toZone.GetString(), "hand", StringComparison.Ordinal))
            .ToArray();
        Equal(2, opponentDrawEvents.Length, "Opponent did not receive count-safe draw events.");
        True(opponentDrawEvents.All(item => item.Payload.GetProperty("identity_redacted").GetBoolean()), "Opponent draw identity was not redacted.");
        True(opponentDrawEvents.All(item => !item.Payload.TryGetProperty("card_id", out _)
                                             && !item.Payload.TryGetProperty("card_instance_id", out _)
                                             && !item.Payload.TryGetProperty("from_zone_index", out _)),
            "Opponent draw event leaks card or Deck-order identity.");
        Equal(1, fixture.State.StateVersion, "Played draw sequence did not increment StateVersion exactly once.");
    }

    internal static void RefreshPenaltyBoundaryRejectsBeforeAnyMutation()
    {
        AssertRefreshBoundary(hasWard: false, deckCount: 2, accepted: true);
        AssertRefreshBoundary(hasWard: false, deckCount: 1, accepted: false);
        AssertRefreshBoundary(hasWard: true, deckCount: 3, accepted: true);
        AssertRefreshBoundary(hasWard: true, deckCount: 2, accepted: false);
    }

    internal static void UnsupportedConditionAndDrawGraphsRejectAtomically()
    {
        var cases = new (string Name, Func<CanonicalCardDatabasePackage, CanonicalCardDatabasePackage> Mutate, string Code)[]
        {
            ("condition operator", package => CanonicalAbilityCatalogTests.SetField(package, CanonicalAbilityTableIds.Conditions, "condition_aqu_mor_037_01_has_ward_horizont", "comparison_operator_id", "op_equal"), "CANONICAL_EFFECT_CONDITION_UNSUPPORTED"),
            ("aggregate kind", package => CanonicalAbilityCatalogTests.SetField(package, CanonicalAbilityTableIds.Expressions, "expr_aqu_mor_037_01_ward_target_count", "aggregate_type_id", "sum"), "CANONICAL_EFFECT_CONDITION_UNSUPPORTED"),
            ("draw value channel", package => CanonicalAbilityCatalogTests.SetField(package, CanonicalAbilityTableIds.Effects, "effect_aqu_mor_037_01_draw_two", "value_type_id", "text"), "CANONICAL_EFFECT_GRAPH_UNSUPPORTED"),
            ("keyword field", package => CanonicalAbilityCatalogTests.SetField(package, CanonicalAbilityTableIds.Expressions, "expr_aqu_mor_037_01_candidate_keywords", "field_id", "card_keywords"), "CANONICAL_TARGET_FILTER_UNSUPPORTED"),
        };
        foreach (var testCase in cases)
        {
            var fixture = CreateFixture(["AQU-MOR-037"], 3, 4, [], testCase.Mutate(CreatePackage()));
            var before = Fingerprint(fixture);
            var response = PlayResolution(fixture, fixture.HandSourceIds[0], 3, ImmutableArray<CanonicalTargetSelectionPayload>.Empty);
            True(!response.Accepted, $"Unsupported {testCase.Name} was accepted.");
            Equal(testCase.Code, Single(response.Diagnostics).Code, $"Unsupported {testCase.Name} diagnostic is invalid.");
            Equal(before, Fingerprint(fixture), $"Unsupported {testCase.Name} mutated state.");
        }
    }

    private static void AssertRefreshBoundary(bool hasWard, int deckCount, bool accepted)
    {
        var board = hasWard
            ? new[] { Board("ward", "FIXTURE-ENTITY-WARD", "player_1", DomainRow.Horizon, 0) }
            : Array.Empty<BoardSetup>();
        var fixture = CreateFixture(["AQU-MOR-037"], deckCount, 4, board);
        var before = Fingerprint(fixture);
        var response = PlayResolution(fixture, fixture.HandSourceIds[0], 3, ImmutableArray<CanonicalTargetSelectionPayload>.Empty);
        Equal(accepted, response.Accepted, "Refresh-boundary acceptance is invalid.");
        if (accepted)
        {
            Equal(0, fixture.State.GetPlayer("player_1").DeckCardInstanceIds.Count, "Exact-size Deck did not end empty.");
            return;
        }

        Equal(CanonicalEffectExecutor.DrawRefreshPenaltyUnsupportedCode, Single(response.Diagnostics).Code, "Refresh migration diagnostic is invalid.");
        Equal(before, Fingerprint(fixture), "Refresh-required rejection partially mutated the played-card transition.");
        True(fixture.AuraSourceIds.All(id => fixture.State.GetCardInstance(id).ActivityState == "active"), "Refresh rejection paid Aura.");
        Equal("hand", fixture.State.GetCardInstance(fixture.HandSourceIds[0]).Zone, "Refresh rejection moved source Ritual.");
    }

    private static void AssertDrawResult(
        Fixture fixture,
        ActionResponse response,
        int expectedDraws,
        int? expectedRemainingHandCount = null)
    {
        Equal(expectedDraws, response.Events.Count(item => item.EventType == "zone_move"
            && item.Payload.GetProperty("to_zone").GetString() == "hand"), "Canonical draw count is invalid.");
        Equal(0, fixture.State.GetPlayer("player_1").DeckCardInstanceIds.Count, "Expected exact-size Deck to end empty.");
        Equal(expectedRemainingHandCount ?? expectedDraws, fixture.State.GetPlayer("player_1").HandCardInstanceIds.Count, "Final Hand count is invalid.");
        Equal("void", fixture.State.GetCardInstance(fixture.HandSourceIds.Last()).Zone, "Source Ritual did not enter Void after resolution.");
    }

    private static ImmutableArray<string> ResolveWardCandidates(Fixture fixture)
    {
        var ability = fixture.Abilities.AbilitiesById["ability_aqu_mor_037_01"];
        var target = ability.Targets.Single(item => item.TargetId == WardQueryTargetId);
        return CanonicalTargetResolver.ResolveCandidates(
                target,
                ability,
                "player_1",
                fixture.State,
                fixture.Runtime,
                fixture.Cards,
                fixture.Abilities)
            .Select(item => item.CardInstanceId)
            .ToImmutableArray();
    }

    private static Fixture CreateFixture(
        IReadOnlyList<string> handCardIds,
        int deckCount,
        int auraCount,
        IReadOnlyList<BoardSetup> board,
        CanonicalCardDatabasePackage? package = null)
    {
        package ??= CreatePackage();
        var abilities = CanonicalAbilityMaterializer.Materialize(package);
        var cards = CanonicalCardMaterializer.Materialize(package);
        var state = new MatchState
        {
            MatchId = "draw-reference-fixture",
            Seed = 113,
            RuntimePackageId = "draw-reference-runtime",
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
        var sourceIds = ImmutableArray.CreateBuilder<string>();
        for (var index = 0; index < handCardIds.Count; index += 1)
        {
            var id = $"source_{index + 1}";
            AddCard(state, player1, id, handCardIds[index], "hand", index, "owner_only", null, null);
            sourceIds.Add(id);
        }

        var deckIds = ImmutableArray.CreateBuilder<string>();
        for (var index = 0; index < deckCount; index += 1)
        {
            var id = $"deck_{index + 1}";
            AddCard(state, player1, id, "FIXTURE-CARD-P1-001", "deck", index, "owner_only", null, null);
            deckIds.Add(id);
        }

        var auraIds = ImmutableArray.CreateBuilder<string>();
        var auraCardId = handCardIds.Count > 0
                         && handCardIds[0].StartsWith("IGN-", StringComparison.Ordinal)
            ? "FIXTURE-CARD-P1-001"
            : "FIXTURE-AQUA-SOURCE-001";
        for (var index = 0; index < auraCount; index += 1)
        {
            var id = $"aura_{index + 1}";
            AddCard(state, player1, id, auraCardId, "wellspring", index, "owner_only", "active", null);
            auraIds.Add(id);
        }

        foreach (var setup in board)
        {
            var player = state.GetPlayer(setup.PlayerId);
            var card = new CardInstanceState
            {
                CardInstanceId = setup.InstanceId,
                CardId = setup.CardId,
                OwnerPlayerId = setup.PlayerId,
                ControllerPlayerId = setup.PlayerId,
                Zone = "dominion",
                ZoneIndex = -1,
                Visibility = "public",
                CreatedSequence = state.CardInstances.Count + 1,
                ZoneSequence = 1,
                InitialZone = "dominion",
                ActivityState = "active",
                DomainRow = setup.Row,
                DomainLaneIndex = setup.Lane,
                EnteredDomainTurnNumber = 1,
            };
            state.CardInstances.Add(card.CardInstanceId, card);
            player.Domain.GetSlots(setup.Row)[setup.Lane] = card.CardInstanceId;
        }

        var runtimeCards = cards.Definitions.ToImmutableDictionary(
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
        EngineSession.ValidateState(state, cards, abilities);
        return new Fixture(
            new EngineSession(state, runtime, abilities, cards),
            state,
            runtime,
            cards,
            abilities,
            sourceIds.ToImmutable(),
            deckIds.ToImmutable(),
            auraIds.ToImmutable());
    }

    private static void AddCard(
        MatchState state,
        PlayerState player,
        string instanceId,
        string cardId,
        string zone,
        int zoneIndex,
        string visibility,
        string? activity,
        DomainRow? row)
    {
        state.CardInstances.Add(instanceId, new CardInstanceState
        {
            CardInstanceId = instanceId,
            CardId = cardId,
            OwnerPlayerId = player.PlayerId,
            ControllerPlayerId = player.PlayerId,
            Zone = zone,
            ZoneIndex = zoneIndex,
            Visibility = visibility,
            CreatedSequence = state.CardInstances.Count + 1,
            ZoneSequence = 1,
            InitialZone = zone,
            ActivityState = activity,
            DomainRow = row,
        });
        (zone == "hand" ? player.HandCardInstanceIds
            : zone == "deck" ? player.DeckCardInstanceIds
            : player.WellspringCardInstanceIds).Add(instanceId);
    }

    private static ActionResponse PlayEntity(
        Fixture fixture,
        string sourceId,
        DomainRow row,
        int lane,
        int auraPayment) => SubmitPlay(
            fixture,
            sourceId,
            row == DomainRow.Horizon ? "horizon" : "zenith",
            lane,
            auraPayment,
            targets: null);

    private static ActionResponse PlayResolution(
        Fixture fixture,
        string sourceId,
        int auraPayment,
        ImmutableArray<CanonicalTargetSelectionPayload> targets) => SubmitPlay(
            fixture,
            sourceId,
            null,
            null,
            auraPayment,
            targets);

    private static ActionResponse SubmitPlay(
        Fixture fixture,
        string sourceId,
        string? row,
        int? lane,
        int auraPayment,
        ImmutableArray<CanonicalTargetSelectionPayload>? targets)
    {
        var action = fixture.Session.ListLegalActions("player_1", includeDisabled: true).Actions
            .Single(item => item.ActionType == "play_card");
        var activeAura = fixture.AuraSourceIds
            .Where(id => fixture.State.GetCardInstance(id).ActivityState == "active")
            .Take(auraPayment)
            .ToImmutableArray();
        return fixture.Session.SubmitAction(new ActionRequest(
            ContractSchemas.ActionRequest,
            $"play-{sourceId}",
            fixture.State.MatchId,
            "player_1",
            fixture.State.StateVersion,
            action.ActionId,
            action.ActionType,
            ContractJsonValue.From(new PlayCardActionPayload(sourceId, row, lane, activeAura, targets))));
    }

    private static ActionResponse Resolve(
        Fixture fixture,
        ImmutableArray<CanonicalTargetSelectionPayload> targets)
    {
        var action = fixture.Session.ListLegalActions("player_1", includeDisabled: true).Actions
            .Single(item => item.ActionType == "resolve_triggered_ability");
        var pending = fixture.State.PendingTriggerWindow!.PendingTriggers.Single();
        return fixture.Session.SubmitAction(new ActionRequest(
            ContractSchemas.ActionRequest,
            "resolve-trigger",
            fixture.State.MatchId,
            "player_1",
            fixture.State.StateVersion,
            action.ActionId,
            action.ActionType,
            ContractJsonValue.From(new ResolveTriggeredAbilityActionPayload(pending.PendingTriggerId, targets))));
    }

    private static ActionResponse EndTurn(Fixture fixture)
    {
        fixture.State.Phase = CanonicalPhaseIds.Incursion;
        var action = fixture.Session.ListLegalActions(fixture.State.ActivePlayerId).Actions.Single(item => item.ActionType == "advance_phase");
        return fixture.Session.SubmitAction(new ActionRequest(
            ContractSchemas.ActionRequest,
            "end-turn",
            fixture.State.MatchId,
            fixture.State.ActivePlayerId,
            fixture.State.StateVersion,
            action.ActionId,
            action.ActionType,
            ContractJsonValue.EmptyObject()));
    }

    private static CanonicalCardDatabasePackage CreatePackage()
    {
        var package = CanonicalAbilityCatalogTests.CreatePackage();
        package = AddRegistryVocabulary(package, "effect_action_types", "effect_action_type_id", "effect_draw_cards");
        package = Add(package, CanonicalAbilityTableIds.Cards,
            Card("IGN-HAM-020", "entity", "ignis", 3, 2, 3, 2),
            Card("AQU-MOR-037", "ritual", "aqua", 4, 3, null, null),
            Card("FIXTURE-ENTITY-HP5", "entity", "ignis", 1, 0, 1, 5));
        package = Add(package, CanonicalAbilityTableIds.Abilities,
            Ability("ability_ign_ham_020_01", "IGN-HAM-020", "triggered", "dominion"),
            Ability("ability_aqu_mor_037_01", "AQU-MOR-037", "resolution", "hand"));
        package = Add(package, CanonicalAbilityTableIds.Targets,
            Target(EnemyTargetId, "ability_ign_ham_020_01", 1, "primary", "target_choose_one_card", "ref_selected_card_exactly_one", "card_instance", "entity", "opponent_of_ability_controller", "dominion", null, "controller_choice", 1, 1, null),
            Target(SourceTargetId, "ability_ign_ham_020_01", 2, "reference_subject", "target_reference_ability_source_card", "ref_ability_source_card", "card_instance", null, null, null, null, "automatic_reference", 1, 1, null),
            Target(ControllerTargetId, "ability_aqu_mor_037_01", 1, "affected_player", "target_reference_ability_controller_player", "ref_ability_controller_player", "player_state", null, "ability_controller", null, null, "automatic_reference", 1, 1, null),
            Target(WardQueryTargetId, "ability_aqu_mor_037_01", 2, "additional", "target_all_matching_cards", "ref_all_matching_cards_zero_or_more", "card_instance", "entity", "ability_controller", "dominion", "horizont", "all_matching", 0, 6, "condition_aqu_mor_037_01_candidate_has_ward"));
        package = Add(package, CanonicalAbilityTableIds.Effects,
            Effect("effect_ign_ham_020_01_enemy_damage", "ability_ign_ham_020_01", 1, "effect_deal_damage", EnemyTargetId),
            Effect("effect_ign_ham_020_01_self_damage", "ability_ign_ham_020_01", 2, "effect_deal_damage", SourceTargetId),
            Effect("effect_aqu_mor_037_01_draw_two", "ability_aqu_mor_037_01", 1, "effect_draw_cards", ControllerTargetId, "number", 2, null),
            Effect("effect_aqu_mor_037_01_draw_one_if_ward", "ability_aqu_mor_037_01", 2, "effect_draw_cards", ControllerTargetId, "number", 1, "condition_aqu_mor_037_01_has_ward_horizont"));
        package = Add(package, CanonicalAbilityTableIds.EffectParameters,
            Parameter("effectparam_ign_ham_020_01_enemy_damage_kind", "effect_ign_ham_020_01_enemy_damage", "parameter_field_deal_damage_damage_kind", null, "damage_kind_direct"),
            Parameter("effectparam_ign_ham_020_01_enemy_amount", "effect_ign_ham_020_01_enemy_damage", "parameter_field_deal_damage_amount", 2, null),
            Parameter("effectparam_ign_ham_020_01_self_damage_kind", "effect_ign_ham_020_01_self_damage", "parameter_field_deal_damage_damage_kind", null, "damage_kind_direct"),
            Parameter("effectparam_ign_ham_020_01_self_amount", "effect_ign_ham_020_01_self_damage", "parameter_field_deal_damage_amount", 1, null));
        package = Add(package, CanonicalAbilityTableIds.Triggers,
            CanonicalAbilityCatalogTests.Record(
                ("trigger_id", "trigger_ign_ham_020_01_entered_play"),
                ("ability_id", "ability_ign_ham_020_01"),
                ("sequence", 1),
                ("event_type_id", "event_card_entered_play"),
                ("event_stage_id", "after"),
                ("subject_reference_type_id", "ref_ability_source_card"),
                ("to_zone_id", "dominion")));
        package = Add(package, CanonicalAbilityTableIds.Conditions,
            Condition("condition_aqu_mor_037_01_candidate_has_ward", 1, "expr_aqu_mor_037_01_candidate_keywords", "op_contains", "expr_aqu_mor_037_01_ward_literal"),
            Condition("condition_aqu_mor_037_01_has_ward_horizont", 2, "expr_aqu_mor_037_01_ward_target_count", "op_greater_than_or_equal", "expr_aqu_mor_037_01_one"));
        package = Add(package, CanonicalAbilityTableIds.Expressions,
            Expression("expr_aqu_mor_037_01_candidate_keywords", null, 1, "field_reference", "ref_target_candidate_card", "card_effective_keywords", null, null, null, null),
            Expression("expr_aqu_mor_037_01_ward_literal", null, 2, "literal", null, null, null, "string", null, "keyword_ward"),
            Expression("expr_aqu_mor_037_01_ward_target_count", null, 3, "aggregate", "ref_all_matching_cards_zero_or_more", null, "count", null, null, null),
            Expression("expr_aqu_mor_037_01_ward_target_result", "expr_aqu_mor_037_01_ward_target_count", 1, "reference", "ref_all_matching_cards_zero_or_more", null, null, null, null, null, WardQueryTargetId),
            Expression("expr_aqu_mor_037_01_one", null, 4, "literal", null, null, null, "integer", 1, null));
        return package;
    }

    private static CanonicalCardDatabasePackage AddRegistryVocabulary(
        CanonicalCardDatabasePackage package,
        string tableId,
        string primaryKey,
        string value)
    {
        var table = package.Registry.Tables[tableId];
        var record = CanonicalAbilityCatalogTests.Record((primaryKey, value));
        var changed = table with
        {
            Records = table.Records.Add(record),
            RecordsById = table.RecordsById.Add(value, record),
        };
        return package with
        {
            Registry = package.Registry with { Tables = package.Registry.Tables.SetItem(tableId, changed) },
        };
    }

    private static CanonicalCardDatabasePackage Add(
        CanonicalCardDatabasePackage package,
        string tableId,
        params CanonicalRecord[] records)
    {
        foreach (var record in records)
        {
            package = CanonicalAbilityCatalogTests.AddRecord(package, tableId, record);
        }

        return package;
    }

    private static CanonicalRecord Card(string id, string type, string realm, int magnitude, int cost, int? atk, int? hp) =>
        CanonicalAbilityCatalogTests.Record(
            ("card_id", id), ("card_type_id", type), ("realm_id", realm), ("magnitude", magnitude),
            ("aura_cost", cost), ("atk", atk), ("hp", hp));

    private static CanonicalRecord Ability(string id, string cardId, string kind, string zone) =>
        CanonicalAbilityCatalogTests.Record(
            ("ability_id", id), ("card_id", cardId), ("ability_index", 1), ("ability_kind_id", kind),
            ("resolution_requirement_id", "full_resolution_required"), ("active_zone_id", zone),
            ("implementation_mode_id", "structured_data"), ("ability_template_id", null),
            ("module_key", null), ("parent_ability_id", null));

    private static CanonicalRecord Target(
        string id, string ability, int sequence, string role, string primitive, string reference, string gameObject,
        string? cardType, string? playerReference, string? zone, string? row, string method, int min, int max, string? filter) =>
        CanonicalAbilityCatalogTests.Record(
            ("target_id", id), ("ability_id", ability), ("sequence", sequence), ("target_role_id", role),
            ("target_primitive_id", primitive), ("reference_type_id", reference), ("game_object_id", gameObject),
            ("card_type_id", cardType), ("player_reference_id", playerReference), ("zone_id", zone),
            ("domain_row_id", row), ("selection_method_id", method), ("minimum_targets", min),
            ("maximum_targets", max), ("filter_condition_id", filter), ("optional", false));

    private static CanonicalRecord Effect(
        string id, string ability, int sequence, string action, string target, string? valueType = null,
        int? valueNumber = null, string? condition = null) => CanonicalAbilityCatalogTests.Record(
            ("effect_id", id), ("ability_id", ability), ("parent_effect_id", null), ("sequence", sequence),
            ("branch_key", null), ("effect_action_type_id", action), ("source_reference_type_id", "ref_ability_source_card"),
            ("target_id", target), ("value_type_id", valueType), ("value_number", valueNumber), ("condition_id", condition));

    private static CanonicalRecord Parameter(string id, string effect, string field, int? integer, string? registry) =>
        CanonicalAbilityCatalogTests.Record(
            ("effect_parameter_id", id), ("effect_id", effect), ("contract_field_id", field), ("item_index", 1),
            ("value_integer", integer), ("value_registry_value_id", registry));

    private static CanonicalRecord Condition(string id, int sequence, string left, string op, string right) =>
        CanonicalAbilityCatalogTests.Record(
            ("condition_id", id), ("ability_id", "ability_aqu_mor_037_01"), ("parent_condition_id", null),
            ("sequence", sequence), ("condition_kind_id", "comparison"), ("logical_operator_id", null),
            ("negated", false), ("left_expression_id", left), ("comparison_operator_id", op),
            ("right_expression_id", right));

    private static CanonicalRecord Expression(
        string id, string? parent, int sequence, string kind, string? reference, string? field,
        string? aggregate, string? literalType, int? literalNumber, string? literalRegistry, string? target = null) =>
        CanonicalAbilityCatalogTests.Record(
            ("expression_id", id), ("ability_id", "ability_aqu_mor_037_01"), ("parent_expression_id", parent),
            ("sequence", sequence), ("expression_kind_id", kind), ("operator_id", null),
            ("reference_type_id", reference), ("field_id", field), ("aggregate_type_id", aggregate),
            ("literal_data_type_id", literalType), ("literal_number", literalNumber), ("literal_text", null),
            ("literal_registry_value_id", literalRegistry), ("target_id", target));

    private static RuntimeLookupCatalog CreateLookups()
    {
        var groups = ImmutableDictionary.CreateBuilder<string, RuntimeLookupGroup>(StringComparer.Ordinal);
        groups["realm"] = new RuntimeLookupGroup("realm", ImmutableDictionary.CreateRange(StringComparer.Ordinal,
            new Dictionary<string, string> { ["ignis"] = "ignis", ["aqua"] = "aqua" }));
        groups["card_type"] = new RuntimeLookupGroup("card_type", ImmutableDictionary.CreateRange(StringComparer.Ordinal,
            new Dictionary<string, string>
            {
                ["entity"] = "entity", ["incantation"] = "incantation", ["ritual"] = "ritual",
                ["sigil"] = "sigil", ["plane"] = "plane",
            }));
        return new RuntimeLookupCatalog(groups.ToImmutable());
    }

    private static string Fingerprint(Fixture fixture) => JsonSerializer.Serialize(new
    {
        Snapshot = fixture.Session.GetDebugSnapshot(),
        EventCount = fixture.State.Events.Count,
        ResolutionCount = fixture.Session.GetDebugCanonicalAbilityResolutions().Length,
    });

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
            throw new InvalidOperationException($"{message} Expected={string.Join(',', expected)}; Actual={string.Join(',', actual)}");
        }
    }

    private static void True(bool condition, string message)
    {
        if (!condition) throw new InvalidOperationException(message);
    }

    private static void Equal<T>(T expected, T actual, string message)
    {
        if (!EqualityComparer<T>.Default.Equals(expected, actual))
        {
            throw new InvalidOperationException($"{message} Expected={expected}; Actual={actual}");
        }
    }

    private sealed record BoardSetup(string InstanceId, string CardId, string PlayerId, DomainRow Row, int Lane);

    private sealed record Fixture(
        EngineSession Session,
        MatchState State,
        RuntimePackageCatalog Runtime,
        CanonicalCardCatalog Cards,
        CanonicalAbilityCatalog Abilities,
        ImmutableArray<string> HandSourceIds,
        ImmutableArray<string> InitialDeckIds,
        ImmutableArray<string> AuraSourceIds);

    private static BoardSetup Board(string id, string cardId, string playerId, DomainRow row, int lane) =>
        new(id, cardId, playerId, row, lane);
}
