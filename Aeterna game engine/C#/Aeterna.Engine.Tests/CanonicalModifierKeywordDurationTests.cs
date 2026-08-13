using System.Collections.Immutable;
using System.Text.Json;
using Aeterna.Engine;
using Aeterna.Engine.Contracts;
using Aeterna.Engine.Rules;
using Aeterna.Engine.Runtime;
using Aeterna.Engine.State;

internal static class CanonicalModifierKeywordDurationTests
{
    private const string AquTargetId = "target_aqu_mor_033_01_all_allied_entities";
    private const string Ham036TargetId = "target_ign_ham_036_01_primary_entity";
    private const string Ham041TargetId = "target_ign_ham_041_01_primary_entity";

    internal static void AquMor033UsesSnapshotInstancesAndPublicProjection()
    {
        var fixture = CreateFixture(
            "AQU-MOR-033",
            "ritual",
            "aqua",
            5,
            [
                Board("plain", "IGN-LAN-003", DomainRow.Horizon, 0, damageMarked: 1),
                Board("intrinsic", "FIXTURE-ENTITY-WARD", DomainRow.Zenith, 1),
            ]);
        var response = Play(fixture, ImmutableArray<CanonicalTargetSelectionPayload>.Empty);

        True(response.Accepted, "AQU-MOR-033 public play was rejected.");
        Equal(2, fixture.State.ModifierInstances.Count, "AQU-MOR-033 did not create one modifier per snapshot target.");
        Equal(2, fixture.State.KeywordGrantInstances.Count, "AQU-MOR-033 did not create one keyword grant per snapshot target.");
        SequenceEqual(
            ["plain", "intrinsic"],
            fixture.State.ModifierInstances.Values
                .OrderBy(item => item.CreatedSequence)
                .Select(item => item.TargetCardInstanceId),
            "Automatic target snapshot order is unstable.");
        Equal(3, CanonicalVitals.GetEffectiveMaxHp(fixture.State, fixture.State.GetCardInstance("plain"), fixture.Cards), "AQU-MOR-033 max-HP modifier is invalid.");
        Equal(1, fixture.State.GetCardInstance("plain").DamageMarked, "Max-HP modifier mutated DamageMarked.");
        True(HasKeyword(fixture, "plain", "ward"), "AQU-MOR-033 did not grant Ward.");
        True(HasKeyword(fixture, "intrinsic", "ward"), "Intrinsic Ward disappeared while a grant was active.");

        AddBoardCard(fixture.State, "late", "IGN-HAM-001", DomainRow.Horizon, 2);
        Equal(1, CanonicalVitals.GetEffectiveMaxHp(fixture.State, fixture.State.GetCardInstance("late"), fixture.Cards), "Late Entity received a retroactive collection modifier.");
        True(!HasKeyword(fixture, "late", "ward"), "Late Entity received a retroactive keyword grant.");

        var occupant = fixture.Session.GetPlayerSnapshot("player_2").BoardSummary
            .GetProperty("players")[0]
            .GetProperty("horizon")[0]
            .GetProperty("occupant");
        Equal(2, occupant.GetProperty("effective_atk").GetInt32(), "Public effective ATK projection is invalid.");
        Equal(3, occupant.GetProperty("effective_max_hp").GetInt32(), "Public effective max-HP projection is invalid.");
        SequenceEqual(["ward"], occupant.GetProperty("effective_keywords").EnumerateArray().Select(item => item.GetString()!), "Public effective keyword projection is invalid.");

        var end = EndTurn(fixture);
        True(end.Accepted, "AQU-MOR-033 expiry end_turn was rejected.");
        Equal(0, fixture.State.ModifierInstances.Count, "AQU-MOR-033 modifiers did not expire.");
        Equal(0, fixture.State.KeywordGrantInstances.Count, "AQU-MOR-033 grants did not expire.");
        Equal(2, CanonicalVitals.GetEffectiveMaxHp(fixture.State, fixture.State.GetCardInstance("plain"), fixture.Cards), "Printed max HP was not restored after expiry.");
        True(!HasKeyword(fixture, "plain", "ward"), "Granted Ward survived expiry without another source.");
        True(HasKeyword(fixture, "intrinsic", "ward"), "Expiry removed intrinsic Ward.");
        Equal(0, fixture.State.GetCardInstance("plain").DamageMarked, "Surviving Entity did not receive end-turn damage cleanup.");
    }

    internal static void AquMor033ExpiryLossCanBeLethalBeforeDamageCleanup()
    {
        var fixture = CreateFixture(
            "AQU-MOR-033",
            "ritual",
            "aqua",
            5,
            [Board("lethal", "IGN-LAN-003", DomainRow.Horizon, 0)]);
        True(Play(fixture, ImmutableArray<CanonicalTargetSelectionPayload>.Empty).Accepted, "AQU-MOR-033 lethal fixture play failed.");
        var target = fixture.State.GetCardInstance("lethal");
        target.DamageMarked = 2;
        Equal(3, CanonicalVitals.GetEffectiveMaxHp(fixture.State, target, fixture.Cards), "Temporary max HP is not three before expiry.");

        var response = EndTurn(fixture);

        True(response.Accepted, "Expiry-lethal end_turn was rejected.");
        Equal("void", target.Zone, "Expiry-lethal Entity did not move to Void.");
        Equal(0, target.DamageMarked, "Dominion departure did not reset damage.");
        True(!response.Events.Any(item => item.EventType == "damage_removed"
                                         && item.Payload.GetProperty("entity_instance_id").GetString() == "lethal"),
            "Destroyed Entity incorrectly received survivor damage cleanup.");
        SequenceEqual(
            ["phase_transition", "modifier_removed", "keyword_removed", "entity_destroyed", "card_zone_changed"],
            response.Events.Select(item => item.EventType),
            "Expiry/lethal/cleanup/turn ordering is invalid.");
        Equal("destruction_cause_kind_rule_state_consequence", response.Events[3].Payload.GetProperty("destruction_cause_kind_id").GetString(), "Expiry-lethal destruction cause is invalid.");
    }

    internal static void IgnHam036And041ShareGenericModifierGrantRuntime()
    {
        AssertHamAttackAndCleave("IGN-HAM-036", "ritual", 3, Ham036TargetId);
        AssertHamAttackAndCleave("IGN-HAM-041", "incantation", 2, Ham041TargetId);
    }

    internal static void ModifierAndKeywordSourcesRemainIndependent()
    {
        var fixture = CreateFixture(
            "IGN-HAM-036",
            "ritual",
            "ignis",
            3,
            [
                Board("plain", "IGN-LAN-003", DomainRow.Horizon, 0),
                Board("intrinsic", "FIXTURE-ENTITY-WARD", DomainRow.Horizon, 1),
            ]);
        var source = fixture.SourceCardInstanceId;
        var plain = fixture.State.GetCardInstance("plain");
        fixture.State.ModifierInstances.Add("modifier_a", Modifier("modifier_a", source, "plain", plain.ZoneSequence, "entity_attack", 1, 1));
        fixture.State.ModifierInstances.Add("modifier_b", Modifier("modifier_b", source, "plain", plain.ZoneSequence, "entity_attack", 2, 2));
        Equal(5, CanonicalVitals.GetEffectiveAtk(fixture.State, plain, fixture.Cards), "Independent +1/+2 modifier stacking is invalid.");
        fixture.State.ModifierInstances.Remove("modifier_a");
        Equal(4, CanonicalVitals.GetEffectiveAtk(fixture.State, plain, fixture.Cards), "Removing source A removed source B's value.");
        fixture.State.ModifierInstances.Remove("modifier_b");
        Equal(2, CanonicalVitals.GetEffectiveAtk(fixture.State, plain, fixture.Cards), "Removing all modifiers did not restore printed ATK.");

        var intrinsic = fixture.State.GetCardInstance("intrinsic");
        fixture.State.KeywordGrantInstances.Add("grant_ward_a", Grant("grant_ward_a", source, "intrinsic", intrinsic.ZoneSequence, "ward", 3));
        fixture.State.KeywordGrantInstances.Add("grant_ward_b", Grant("grant_ward_b", source, "intrinsic", intrinsic.ZoneSequence, "ward", 4));
        Equal(1, CanonicalContinuousEffects.GetEffectiveKeywords(fixture.State, intrinsic, fixture.Abilities).Count(value => value == "ward"), "Identical intrinsic/granted keywords mechanically stacked.");
        fixture.State.KeywordGrantInstances.Remove("grant_ward_a");
        fixture.State.KeywordGrantInstances.Remove("grant_ward_b");
        True(HasKeyword(fixture, "intrinsic", "ward"), "Removing grant sources removed intrinsic Ward.");

        fixture.State.KeywordGrantInstances.Add("grant_cleave_a", Grant("grant_cleave_a", source, "plain", plain.ZoneSequence, "cleave", 5));
        fixture.State.KeywordGrantInstances.Add("grant_cleave_b", Grant("grant_cleave_b", source, "plain", plain.ZoneSequence, "cleave", 6));
        Equal(1, CanonicalContinuousEffects.GetEffectiveKeywords(fixture.State, plain, fixture.Abilities).Count(value => value == "cleave"), "Identical grants mechanically stacked.");
        fixture.State.KeywordGrantInstances.Remove("grant_cleave_a");
        True(HasKeyword(fixture, "plain", "cleave"), "Removing grant A removed grant B's keyword.");
        fixture.State.KeywordGrantInstances.Remove("grant_cleave_b");
        True(!HasKeyword(fixture, "plain", "cleave"), "Keyword remained after its last source was removed.");

        var zeroAttackPackage = CanonicalAbilityCatalogTests.SetField(
            CanonicalAbilityCatalogTests.CreatePackage(),
            CanonicalAbilityTableIds.Cards,
            "IGN-LAN-003",
            "atk",
            0);
        var zeroAttack = CreateFixture(
            "IGN-HAM-036",
            "ritual",
            "ignis",
            3,
            [Board("zero", "IGN-LAN-003", DomainRow.Horizon, 0)],
            zeroAttackPackage);
        Equal(0, CanonicalVitals.GetEffectiveAtk(zeroAttack.State, zeroAttack.State.GetCardInstance("zero"), zeroAttack.Cards), "Zero printed ATK was incorrectly clamped or rejected.");
    }

    internal static void ZoneSequencePreventsCrossZoneResurrection()
    {
        var fixture = CreateFixture(
            "IGN-HAM-036",
            "ritual",
            "ignis",
            3,
            [Board("target", "IGN-LAN-003", DomainRow.Horizon, 0)]);
        var target = fixture.State.GetCardInstance("target");
        fixture.State.ModifierInstances.Add("modifier_old", Modifier("modifier_old", fixture.SourceCardInstanceId, "target", target.ZoneSequence, "entity_attack", 2, 1));
        fixture.State.KeywordGrantInstances.Add("grant_old", Grant("grant_old", fixture.SourceCardInstanceId, "target", target.ZoneSequence, "cleave", 2));
        Equal(4, CanonicalVitals.GetEffectiveAtk(fixture.State, target, fixture.Cards), "Active-zone modifier did not apply.");

        target.Zone = "hand";
        target.ZoneSequence += 1;
        Equal(2, CanonicalVitals.GetEffectiveAtk(fixture.State, target, fixture.Cards), "Modifier remained effective outside Dominion.");
        True(!HasKeyword(fixture, "target", "cleave"), "Keyword grant remained effective outside Dominion.");
        target.Zone = "dominion";
        target.ZoneSequence += 1;
        Equal(2, CanonicalVitals.GetEffectiveAtk(fixture.State, target, fixture.Cards), "Old modifier resurrected after re-entry.");
        True(!HasKeyword(fixture, "target", "cleave"), "Old grant resurrected after re-entry.");
    }

    internal static void DebugProjectionAndExpiryAreDeterministic()
    {
        var first = CreateFixture("IGN-HAM-036", "ritual", "ignis", 3, [Board("target", "IGN-LAN-003", DomainRow.Horizon, 0)]);
        var second = CreateFixture("IGN-HAM-036", "ritual", "ignis", 3, [Board("target", "IGN-LAN-003", DomainRow.Horizon, 0)]);
        True(Play(first, [new CanonicalTargetSelectionPayload(Ham036TargetId, ["target"])]).Accepted, "First deterministic fixture failed.");
        True(Play(second, [new CanonicalTargetSelectionPayload(Ham036TargetId, ["target"])]).Accepted, "Second deterministic fixture failed.");
        var debug = first.Session.GetDebugSnapshot();
        Equal("aeterna-debug-match-snapshot-v4", debug.SchemaVersion, "Debug contribution contract version is invalid.");
        Equal(1, debug.ModifierInstances.Length, "Debug modifier registry is missing.");
        Equal(1, debug.KeywordGrantInstances.Length, "Debug grant registry is missing.");
        Equal("ability_ign_ham_036_01", debug.ModifierInstances[0].SourceAbilityId, "Debug source identity is invalid.");
        True(!string.IsNullOrWhiteSpace(debug.ModifierInstances[0].SourceResolutionId), "Debug resolution identity is missing.");
        Equal(
            JsonSerializer.Serialize(first.Session.GetDebugSnapshot()),
            JsonSerializer.Serialize(second.Session.GetDebugSnapshot()),
            "Equivalent continuous-effect applications are not deterministic.");
        SequenceEqual(
            EndTurn(first).Events.Select(item => item.EventType),
            EndTurn(second).Events.Select(item => item.EventType),
            "Equivalent expiry event order is not deterministic.");
    }

    internal static void UnsupportedGraphsRejectWithoutPartialMutation()
    {
        var cases = new (string Name, Func<CanonicalCardDatabasePackage, CanonicalCardDatabasePackage> Mutate)[]
        {
            ("unsupported modifier type", package => Set(package, "effect_ign_ham_036_01_attack_bonus", "modifier_type_id", "modifier_unknown")),
            ("unsupported field", package => Set(package, "effect_ign_ham_036_01_attack_bonus", "field_id", "entity_max_hp")),
            ("invalid modifier value", package => Set(package, "effect_ign_ham_036_01_attack_bonus", "value_number", 0)),
            ("unsupported duration", package => CanonicalAbilityCatalogTests.SetField(package, CanonicalAbilityTableIds.Durations, "duration_ign_ham_036_01_attack_bonus_turn", "duration_policy_id", "duration_while_source_in_required_zone")),
            ("invalid keyword", package => Set(package, "effect_ign_ham_036_01_grant_cleave", "value_registry_value_id", "keyword_speed")),
            ("wrong value channel", package => Set(package, "effect_ign_ham_036_01_attack_bonus", "value_type_id", "text")),
            ("malformed modifier graph", package => CanonicalAbilityCatalogTests.RemoveRecord(package, CanonicalAbilityTableIds.Durations, "duration_ign_ham_036_01_attack_bonus_turn")),
            ("malformed grant graph", package => Set(package, "effect_ign_ham_036_01_grant_cleave", "from_zone_id", "dominion")),
            ("mixed supported and unsupported", package => Set(package, "effect_ign_ham_036_01_grant_cleave", "value_registry_value_id", "keyword_unknown")),
        };

        foreach (var testCase in cases)
        {
            var fixture = CreateFixture(
                "IGN-HAM-036",
                "ritual",
                "ignis",
                3,
                [Board("target", "IGN-LAN-003", DomainRow.Horizon, 0)],
                testCase.Mutate(CanonicalAbilityCatalogTests.CreatePackage()));
            var before = Fingerprint(fixture);
            var response = Play(fixture, [new CanonicalTargetSelectionPayload(Ham036TargetId, ["target"])]);
            True(!response.Accepted, $"{testCase.Name} was accepted.");
            Equal("CANONICAL_EFFECT_GRAPH_UNSUPPORTED", Single(response.Diagnostics).Code, $"{testCase.Name} returned an unexpected diagnostic.");
            Equal(before, Fingerprint(fixture), $"{testCase.Name} mutated authoritative state.");
            Equal(0, fixture.State.ModifierInstances.Count, $"{testCase.Name} committed a partial modifier.");
            Equal(0, fixture.State.KeywordGrantInstances.Count, $"{testCase.Name} committed a partial keyword grant.");
        }
    }

    internal static void ContinuousEffectStateInvariantsRejectMalformedInstances()
    {
        var fixture = CreateFixture(
            "IGN-HAM-036",
            "ritual",
            "ignis",
            3,
            [Board("target", "IGN-LAN-003", DomainRow.Horizon, 0)]);
        True(Play(fixture, [new CanonicalTargetSelectionPayload(Ham036TargetId, ["target"])]).Accepted, "Invariant fixture play failed.");
        var modifier = fixture.State.ModifierInstances.Values.Single();
        var grant = fixture.State.KeywordGrantInstances.Values.Single();

        fixture.State.ModifierInstances[modifier.ModifierInstanceId] = modifier with { IntegerValue = 0 };
        ThrowsState(() => EngineSession.ValidateState(fixture.State, fixture.Cards, fixture.Abilities));
        fixture.State.ModifierInstances[modifier.ModifierInstanceId] = modifier with { TargetCardInstanceId = "missing" };
        ThrowsState(() => EngineSession.ValidateState(fixture.State, fixture.Cards, fixture.Abilities));
        fixture.State.ModifierInstances[modifier.ModifierInstanceId] = modifier with { SourceEffectId = "missing" };
        ThrowsState(() => EngineSession.ValidateState(fixture.State, fixture.Cards, fixture.Abilities));
        fixture.State.ModifierInstances[modifier.ModifierInstanceId] = modifier with { DurationPolicyId = "unsupported" };
        ThrowsState(() => EngineSession.ValidateState(fixture.State, fixture.Cards, fixture.Abilities));
        fixture.State.ModifierInstances[modifier.ModifierInstanceId] = modifier with { SourceResolutionId = "" };
        ThrowsState(() => EngineSession.ValidateState(fixture.State, fixture.Cards, fixture.Abilities));
        fixture.State.ModifierInstances[modifier.ModifierInstanceId] = modifier;

        fixture.State.KeywordGrantInstances[grant.KeywordGrantInstanceId] = grant with { CreatedSequence = modifier.CreatedSequence };
        ThrowsState(() => EngineSession.ValidateState(fixture.State, fixture.Cards, fixture.Abilities));
        fixture.State.KeywordGrantInstances[grant.KeywordGrantInstanceId] = grant;
        fixture.State.ModifierInstances.Remove(modifier.ModifierInstanceId);
        fixture.State.ModifierInstances.Add("wrong_registry_key", modifier);
        ThrowsState(() => EngineSession.ValidateState(fixture.State, fixture.Cards, fixture.Abilities));
    }

    private static void AssertHamAttackAndCleave(string cardId, string runtimeType, int payment, string targetId)
    {
        var fixture = CreateFixture(cardId, runtimeType, "ignis", payment, [Board("target", "IGN-LAN-003", DomainRow.Horizon, 0)]);
        var response = Play(fixture, [new CanonicalTargetSelectionPayload(targetId, ["target"])]);
        True(response.Accepted, $"{cardId} public play was rejected.");
        Equal(4, CanonicalVitals.GetEffectiveAtk(fixture.State, fixture.State.GetCardInstance("target"), fixture.Cards), $"{cardId} +2 ATK is invalid.");
        True(HasKeyword(fixture, "target", "cleave"), $"{cardId} did not grant Cleave.");
        Equal(1, fixture.State.ModifierInstances.Count, $"{cardId} modifier identity is invalid.");
        Equal(1, fixture.State.KeywordGrantInstances.Count, $"{cardId} grant identity is invalid.");
        SequenceEqual(
            ["modifier_applied", "keyword_granted", "canonical_ability_resolved", "zone_move"],
            response.Events
                .Where(item => item.EventType != "aura_source_exhausted")
                .Select(item => item.EventType),
            $"{cardId} effect sequence is invalid.");
        True(EndTurn(fixture).Accepted, $"{cardId} expiry failed.");
        Equal(2, CanonicalVitals.GetEffectiveAtk(fixture.State, fixture.State.GetCardInstance("target"), fixture.Cards), $"{cardId} ATK modifier survived expiry.");
        True(!HasKeyword(fixture, "target", "cleave"), $"{cardId} Cleave survived expiry.");
    }

    private static Fixture CreateFixture(
        string sourceCardId,
        string sourceRuntimeType,
        string sourceRealm,
        int sourceCount,
        IReadOnlyList<BoardSetup> board,
        CanonicalCardDatabasePackage? package = null)
    {
        package ??= CanonicalAbilityCatalogTests.CreatePackage();
        var abilities = CanonicalAbilityMaterializer.Materialize(package);
        var cards = CanonicalCardMaterializer.Materialize(package);
        var state = new MatchState
        {
            MatchId = "modifier-keyword-fixture",
            Seed = 73,
            RuntimePackageId = "modifier-keyword-runtime",
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
        var sourceCardInstanceId = "source";
        state.CardInstances.Add(sourceCardInstanceId, new CardInstanceState
        {
            CardInstanceId = sourceCardInstanceId,
            CardId = sourceCardId,
            OwnerPlayerId = player1.PlayerId,
            ControllerPlayerId = player1.PlayerId,
            Zone = "hand",
            ZoneIndex = 0,
            Visibility = "owner_only",
            CreatedSequence = 1,
            ZoneSequence = 1,
            InitialZone = "hand",
        });
        player1.HandCardInstanceIds.Add(sourceCardInstanceId);

        var wellspringCardId = string.Equals(sourceRealm, "aqua", StringComparison.Ordinal)
            ? "FIXTURE-AQUA-SOURCE-001"
            : "FIXTURE-CARD-P1-001";
        var auraSources = ImmutableArray.CreateBuilder<string>();
        for (var index = 0; index < sourceCount; index += 1)
        {
            var cardInstanceId = $"aura_{index + 1}";
            state.CardInstances.Add(cardInstanceId, new CardInstanceState
            {
                CardInstanceId = cardInstanceId,
                CardId = wellspringCardId,
                OwnerPlayerId = player1.PlayerId,
                ControllerPlayerId = player1.PlayerId,
                Zone = "wellspring",
                ZoneIndex = index,
                Visibility = "owner_only",
                CreatedSequence = state.CardInstances.Count + 1,
                ZoneSequence = 1,
                InitialZone = "wellspring",
                ActivityState = "active",
            });
            player1.WellspringCardInstanceIds.Add(cardInstanceId);
            auraSources.Add(cardInstanceId);
        }

        foreach (var setup in board)
        {
            AddBoardCard(state, setup.InstanceId, setup.CardId, setup.Row, setup.Lane, setup.DamageMarked);
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
        Equal(sourceRuntimeType, runtimeCards[sourceCardId].CardType, "Fixture source card type disagrees with canonical authority.");
        var runtime = new RuntimePackageCatalog(
            state.RuntimePackageId,
            runtimeCards,
            ImmutableDictionary<string, RuntimeDeckDefinition>.Empty.WithComparers(StringComparer.Ordinal),
            CreateLookups());
        EngineSession.ValidateState(state, cards, abilities);
        return new Fixture(
            new EngineSession(state, runtime, abilities, cards),
            state,
            cards,
            abilities,
            sourceCardInstanceId,
            auraSources.ToImmutable());
    }

    private static void AddBoardCard(
        MatchState state,
        string instanceId,
        string cardId,
        DomainRow row,
        int lane,
        int damageMarked = 0)
    {
        var player = state.GetPlayer("player_1");
        var card = new CardInstanceState
        {
            CardInstanceId = instanceId,
            CardId = cardId,
            OwnerPlayerId = player.PlayerId,
            ControllerPlayerId = player.PlayerId,
            Zone = "dominion",
            ZoneIndex = -1,
            Visibility = "public",
            CreatedSequence = state.CardInstances.Count + 1,
            ZoneSequence = 1,
            InitialZone = "dominion",
            ActivityState = "active",
            DomainRow = row,
            DomainLaneIndex = lane,
            EnteredDomainTurnNumber = state.TurnNumber,
            DamageMarked = damageMarked,
        };
        state.CardInstances.Add(instanceId, card);
        player.Domain.GetSlots(row)[lane] = instanceId;
    }

    private static ActionResponse Play(Fixture fixture, ImmutableArray<CanonicalTargetSelectionPayload> targets)
    {
        var action = fixture.Session.ListLegalActions("player_1", includeDisabled: true).Actions.Single(item => item.ActionType == "play_card");
        var auraCost = fixture.Cards.DefinitionsById[fixture.State.GetCardInstance(fixture.SourceCardInstanceId).CardId].PrintedAuraCost;
        return fixture.Session.SubmitAction(new ActionRequest(
            ContractSchemas.ActionRequest,
            "play-source",
            fixture.State.MatchId,
            "player_1",
            fixture.State.StateVersion,
            action.ActionId,
            action.ActionType,
            ContractJsonValue.From(new PlayCardActionPayload(
                fixture.SourceCardInstanceId,
                null,
                null,
                fixture.AuraSourceIds.Take(auraCost).ToImmutableArray(),
                targets))));
    }

    private static ActionResponse EndTurn(Fixture fixture)
    {
        fixture.State.Phase = CanonicalPhaseIds.Incursion;
        var action = fixture.Session.ListLegalActions("player_1").Actions.Single(item => item.ActionType == "advance_phase");
        return fixture.Session.SubmitAction(new ActionRequest(
            ContractSchemas.ActionRequest,
            "end-turn",
            fixture.State.MatchId,
            "player_1",
            fixture.State.StateVersion,
            action.ActionId,
            action.ActionType,
            ContractJsonValue.EmptyObject()));
    }

    private static ModifierInstanceState Modifier(
        string id,
        string source,
        string target,
        int zoneSequence,
        string field,
        int value,
        int sequence) => new(
        id,
        "ability_ign_ham_036_01",
        "effect_ign_ham_036_01_attack_bonus",
        "resolution_manual",
        source,
        "player_1",
        target,
        zoneSequence,
        CanonicalContinuousEffects.AttackModifierTypeId,
        field,
        value,
        "duration_manual",
        CanonicalContinuousEffects.UntilEndOfCurrentTurnDurationPolicyId,
        $"duration_{id}",
        "turn_000001_player_1",
        "phase_turn_000001_player_1_main",
        1,
        "player_1",
        1,
        sequence);

    private static KeywordGrantInstanceState Grant(
        string id,
        string source,
        string target,
        int zoneSequence,
        string keyword,
        int sequence) => new(
        id,
        "ability_ign_ham_036_01",
        "effect_ign_ham_036_01_grant_cleave",
        "resolution_manual",
        source,
        "player_1",
        target,
        zoneSequence,
        keyword,
        "duration_manual",
        CanonicalContinuousEffects.UntilEndOfCurrentTurnDurationPolicyId,
        $"duration_{id}",
        "turn_000001_player_1",
        "phase_turn_000001_player_1_main",
        1,
        "player_1",
        1,
        sequence);

    private static bool HasKeyword(Fixture fixture, string target, string keyword) =>
        CanonicalContinuousEffects.HasEffectiveKeyword(
            fixture.State,
            fixture.State.GetCardInstance(target),
            fixture.Abilities,
            keyword);

    private static CanonicalCardDatabasePackage Set(
        CanonicalCardDatabasePackage package,
        string effectId,
        string field,
        object? value) => CanonicalAbilityCatalogTests.SetField(
        package,
        CanonicalAbilityTableIds.Effects,
        effectId,
        field,
        value);

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

    private static string Fingerprint(Fixture fixture) => JsonSerializer.Serialize(fixture.Session.GetDebugSnapshot());

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

        throw new InvalidOperationException("Expected continuous-effect state invariant rejection.");
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
            throw new InvalidOperationException($"{message} Expected={string.Join(',', expected)}; Actual={string.Join(',', actual)}");
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

    private sealed record BoardSetup(
        string InstanceId,
        string CardId,
        DomainRow Row,
        int Lane,
        int DamageMarked);

    private sealed record Fixture(
        EngineSession Session,
        MatchState State,
        CanonicalCardCatalog Cards,
        CanonicalAbilityCatalog Abilities,
        string SourceCardInstanceId,
        ImmutableArray<string> AuraSourceIds);

    private static BoardSetup Board(
        string instanceId,
        string cardId,
        DomainRow row,
        int lane,
        int damageMarked = 0) => new(instanceId, cardId, row, lane, damageMarked);
}
