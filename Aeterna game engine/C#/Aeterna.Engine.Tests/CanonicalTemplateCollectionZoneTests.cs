using System.Collections.Immutable;
using System.Text.Json;
using Aeterna.Engine;
using Aeterna.Engine.Contracts;
using Aeterna.Engine.Rules;
using Aeterna.Engine.Runtime;
using Aeterna.Engine.State;

internal static class CanonicalTemplateCollectionZoneTests
{
    internal static void TemplateNormalizationIsTypedDeterministicAndIsolated()
    {
        var first = CanonicalAbilityMaterializer.Materialize(CanonicalAbilityCatalogTests.CreatePackage());
        var second = CanonicalAbilityMaterializer.Materialize(CanonicalAbilityCatalogTests.CreatePackage());
        var ability = first.AbilitiesByCardId["LUX-FHL-034"].Single();
        True(ability.IsStructuredGraphAuthority && ability.IsTemplateInstanceAuthority, "Template authority was not normalized.");
        Equal("template_resolution_damage_all_enemy_horizont_entities_v1", ability.TemplateProvenance?.TemplateId, "Template provenance is missing.");
        Equal("ability_lux_fhl_034_01__target", ability.Targets.Single().TargetId, "Generated target identity is invalid.");
        Equal(2, ability.Effects.Single().Parameters.Single(parameter => parameter.ContractFieldId == "parameter_field_deal_damage_amount").ValueInteger, "Typed argument binding is invalid.");
        Equal(
            Fingerprint(ability),
            Fingerprint(second.AbilitiesByCardId["LUX-FHL-034"].Single()),
            "Repeated template expansion is not deterministic.");
        var changed = ability.TemplateProvenance!.GeneratedNodeIds.SetItem("target", "changed");
        Equal("ability_lux_fhl_034_01__target", ability.TemplateProvenance.GeneratedNodeIds["target"], "Template provenance contains shared mutable state.");
        Equal("changed", changed["target"], "Immutable provenance copy did not change independently.");
    }

    internal static void TemplateArgumentAndBindingFailuresAreControlled()
    {
        var missing = CanonicalAbilityCatalogTests.RemoveRecord(
            CanonicalAbilityCatalogTests.CreatePackage(),
            CanonicalAbilityTableIds.TemplateArguments,
            "arg_lux_fhl_034_01_damage_amount");
        ThrowsInput("CANONICAL_TEMPLATE_ARGUMENT_MISSING", () => CanonicalAbilityMaterializer.Materialize(missing));

        var wrongType = CanonicalAbilityCatalogTests.SetField(
            CanonicalAbilityCatalogTests.CreatePackage(),
            CanonicalAbilityTableIds.TemplateArguments,
            "arg_lux_fhl_034_01_damage_amount",
            "value_integer",
            null);
        wrongType = CanonicalAbilityCatalogTests.SetField(
            wrongType,
            CanonicalAbilityTableIds.TemplateArguments,
            "arg_lux_fhl_034_01_damage_amount",
            "value_text",
            "2");
        ThrowsInput("CANONICAL_TEMPLATE_ARGUMENT_TYPE_INVALID", () => CanonicalAbilityMaterializer.Materialize(wrongType));

        var duplicate = AddRegistryRecord(
            CanonicalAbilityCatalogTests.CreatePackage(),
            CanonicalAbilityTableIds.AbilityTemplateBindings,
            CanonicalAbilityCatalogTests.Record(
                ("template_binding_id", "template_binding_fixture_duplicate"),
                ("template_node_id", "template_node_fixture_target"),
                ("target_field_id", "fixture_schema_ability_targets_target_role_id"),
                ("binding_kind_id", "fixed_value"),
                ("parameter_contract_field_id", null),
                ("source_node_key", null),
                ("fixed_boolean", null),
                ("fixed_integer", null),
                ("fixed_text", null),
                ("fixed_registry_value_id", null),
                ("fixed_reference_id", "primary")));
        ThrowsInput("CANONICAL_TEMPLATE_BINDING_DUPLICATE", () => CanonicalAbilityMaterializer.Materialize(duplicate));

        var unsupportedNode = SetRegistryField(
            CanonicalAbilityCatalogTests.CreatePackage(),
            CanonicalAbilityTableIds.AbilityTemplateNodes,
            "template_node_fixture_target",
            "output_table_id",
            "ability_choices");
        ThrowsInput("CANONICAL_TEMPLATE_NODE_INVALID", () => CanonicalAbilityMaterializer.Materialize(unsupportedNode));
    }

    internal static void TemplateAndStructuredGraphsHaveEquivalentRuntimeSemantics()
    {
        var package = Set(
            CanonicalAbilityCatalogTests.CreatePackage(),
            CanonicalAbilityTableIds.Cards,
            "IGN-LAN-003",
            "hp",
            4);
        var catalog = CanonicalAbilityMaterializer.Materialize(package);
        var cards = CanonicalCardMaterializer.Materialize(package);
        var template = catalog.AbilitiesById["ability_lux_fhl_034_01"];
        var structured = template with
        {
            AbilityTemplateId = null,
            Template = null,
            TemplateProvenance = null,
            TemplateArguments = ImmutableArray<CanonicalAbilityTemplateArgumentDefinition>.Empty,
        };
        var firstState = State(Board("ci_auto_damage", "IGN-LAN-003", "player_2", "player_2", DomainRow.Horizon, 2, 0));
        var secondState = State(Board("ci_auto_damage", "IGN-LAN-003", "player_2", "player_2", DomainRow.Horizon, 2, 0));
        var runtime = Runtime(package);
        var firstPlan = Plan(template, firstState, runtime, cards, ImmutableArray<CanonicalTargetSelectionPayload>.Empty);
        var secondPlan = Plan(structured, secondState, runtime, cards, ImmutableArray<CanonicalTargetSelectionPayload>.Empty);
        Equal(
            JsonSerializer.Serialize(firstPlan.Mutations),
            JsonSerializer.Serialize(secondPlan.Mutations),
            "Template and equivalent structured graph produced different runtime semantics.");
        CanonicalEffectExecutor.Apply(firstState, firstPlan);
        Equal(2, firstState.GetCardInstance("ci_auto_damage").DamageMarked, "Normalized template automatic damage was not executed.");
    }

    internal static void AutomaticCollectionHealUsesSnapshotAndCurrentDamage()
    {
        var package = AddEffectVocabulary(CanonicalAbilityCatalogTests.CreatePackage(), "effect_heal_entity");
        package = Set(package, CanonicalAbilityTableIds.Effects, "effect_aqu_mor_033_01_max_hp_bonus", "effect_action_type_id", "effect_heal_entity");
        foreach (var field in new[] { "value_type_id", "value_number", "modifier_type_id" })
        {
            package = Set(package, CanonicalAbilityTableIds.Effects, "effect_aqu_mor_033_01_max_hp_bonus", field, null);
        }

        package = CanonicalAbilityCatalogTests.RemoveRecord(package, CanonicalAbilityTableIds.Effects, "effect_aqu_mor_033_01_grant_ward");
        package = CanonicalAbilityCatalogTests.RemoveRecord(package, CanonicalAbilityTableIds.Durations, "duration_aqu_mor_033_01_max_hp_turn");
        package = CanonicalAbilityCatalogTests.RemoveRecord(package, CanonicalAbilityTableIds.Durations, "duration_aqu_mor_033_01_ward_turn");
        package = CompleteDominionTarget(package, "target_aqu_mor_033_01_all_allied_entities");
        package = CanonicalAbilityCatalogTests.AddRecord(package, CanonicalAbilityTableIds.EffectParameters, Parameter(
            "heal_amount", "effect_aqu_mor_033_01_max_hp_bonus", "parameter_field_heal_entity_amount", ("value_integer", 2)));
        package = CanonicalAbilityCatalogTests.AddRecord(package, CanonicalAbilityTableIds.EffectParameters, Parameter(
            "heal_miasma", "effect_aqu_mor_033_01_max_hp_bonus", "parameter_field_heal_entity_remove_miasma", ("value_boolean", false)));
        package = Set(package, CanonicalAbilityTableIds.Cards, "IGN-HAM-001", "hp", 6);
        package = Set(package, CanonicalAbilityTableIds.Cards, "IGN-LAN-003", "hp", 6);
        var catalog = CanonicalAbilityMaterializer.Materialize(package);
        var cards = CanonicalCardMaterializer.Materialize(package);
        var state = State(
            Board("ci_own_h", "IGN-HAM-001", "player_1", "player_1", DomainRow.Horizon, 4, 3),
            Board("ci_own_z", "IGN-LAN-003", "player_1", "player_1", DomainRow.Zenith, 1, 1),
            Board("ci_enemy", "IGN-HAM-001", "player_2", "player_2", DomainRow.Horizon, 0, 3));
        var ability = catalog.AbilitiesById["ability_aqu_mor_033_01"];
        var plan = Plan(ability, state, Runtime(package), cards, ImmutableArray<CanonicalTargetSelectionPayload>.Empty);

        Equal("ci_own_h,ci_own_z", string.Join(',', plan.TargetSelections.Single().SelectedCards.Select(card => card.CardInstanceId)), "Automatic collection ordering or controller scope is invalid.");
        Equal(CanonicalTargetResolver.AllMatchingSelectionMethodId, plan.TargetSelections.Single().ResolutionModeId, "Automatic target result mode is invalid.");
        CanonicalEffectExecutor.Apply(state, plan);
        Equal(1, state.GetCardInstance("ci_own_h").DamageMarked, "Heal did not remove two marked damage.");
        Equal(0, state.GetCardInstance("ci_own_z").DamageMarked, "Heal did not clamp at zero.");
        Equal(3, state.GetCardInstance("ci_enemy").DamageMarked, "Automatic own collection leaked to an opponent.");
    }

    internal static void NumericFiltersDriveDestroyAndMagnitudeEligibility()
    {
        var package = AddEffectVocabulary(CanonicalAbilityCatalogTests.CreatePackage(), "effect_destroy_entity");
        package = CompleteDominionTarget(package, "target_aqu_mor_007_01_enemy_horizont_entity");
        package = Set(package, CanonicalAbilityTableIds.Effects, "effect_aqu_mor_007_01_exhaust_target", "effect_action_type_id", "effect_destroy_entity");
        package = Set(package, CanonicalAbilityTableIds.Expressions, "expr_aqu_mor_007_01_candidate_magnitude", "field_id", "entity_max_hp");
        package = Set(package, CanonicalAbilityTableIds.Cards, "IGN-HAM-001", "hp", 4);
        package = Set(package, CanonicalAbilityTableIds.Cards, "IGN-LAN-003", "hp", 2);
        var catalog = CanonicalAbilityMaterializer.Materialize(package);
        var cards = CanonicalCardMaterializer.Materialize(package);
        var state = State(
            Board("ci_hp4", "IGN-HAM-001", "player_2", "player_2", DomainRow.Horizon, 0, 0),
            Board("ci_hp2", "IGN-LAN-003", "player_2", "player_2", DomainRow.Horizon, 1, 1));
        var runtime = Runtime(package);
        var ability = catalog.AbilitiesById["ability_aqu_mor_007_01"];
        var target = ability.Targets.Single();
        var candidates = CanonicalTargetResolver.ResolveCandidates(target, ability, "player_1", state, runtime, cards);
        Equal("ci_hp2", candidates.Single().CardInstanceId, "EffectiveMaxHp filter did not exclude HP 4.");
        var plan = Plan(ability, state, runtime, cards, [new CanonicalTargetSelectionPayload(target.TargetId, ["ci_hp2"])]);
        CanonicalEffectExecutor.Apply(state, plan);
        Equal("void", state.GetCardInstance("ci_hp2").Zone, "Semantic destroy did not move the target to Void.");
        Equal(0, state.GetCardInstance("ci_hp2").DamageMarked, "Destroy incorrectly accumulated damage.");
        Equal("destruction_cause_kind_explicit_destroy_effect", plan.Mutations.OfType<CanonicalDestroyEffectMutation>().Single().Destruction.DestructionCauseKindId, "Destroy cause is invalid.");
    }

    internal static void DominionToHandMoveResetsStateAndPreservesProposal()
    {
        var card = new CardInstanceState
        {
            CardInstanceId = "ci_move",
            CardId = "IGN-HAM-001",
            OwnerPlayerId = "player_2",
            ControllerPlayerId = "player_1",
            Zone = "dominion",
            ZoneIndex = -1,
            Visibility = "public",
            CreatedSequence = 1,
            ZoneSequence = 2,
            InitialZone = "hand",
            ActivityState = "exhausted",
            DomainRow = DomainRow.Zenith,
            DomainLaneIndex = 3,
            EnteredDomainTurnNumber = 1,
            DamageMarked = 2,
        };
        var state = State(card);
        var transition = CanonicalZoneTransition.PlanDominionToHand(card, 0, "transition_move", "effect_move");
        Equal(transition.Proposed.ToZoneId, transition.Actual.ToZoneId, "Actual transition differs from the proposal without replacement authority.");
        Equal(CanonicalZoneTransitionCauseKinds.MoveEffect, transition.Actual.CauseKindId, "Move cause is missing.");
        CanonicalZoneTransition.Apply(state, transition);
        Equal("hand", card.Zone, "Dominion-to-Hand did not reach Hand.");
        Equal("player_2", card.ControllerPlayerId, "Leaving Dominion did not restore owner control.");
        Equal("owner_only", card.Visibility, "Hand visibility is invalid.");
        True(card.ActivityState is null && card.DomainRow is null && card.DomainLaneIndex is null && card.EnteredDomainTurnNumber is null, "Domain state was not reset.");
        Equal(0, card.DamageMarked, "Zone move did not clear marked damage.");
        Equal("ci_move", state.GetPlayer("player_2").HandCardInstanceIds.Single(), "Owner Hand destination membership is invalid.");
    }

    internal static void MoveEffectUsesFilteredControllerChoiceAndOwnerHand()
    {
        var package = AddEffectVocabulary(CanonicalAbilityCatalogTests.CreatePackage(), "effect_move_card_between_zones");
        package = CompleteDominionTarget(package, "target_aqu_mor_007_01_enemy_horizont_entity");
        package = Set(package, CanonicalAbilityTableIds.Effects, "effect_aqu_mor_007_01_exhaust_target", "effect_action_type_id", "effect_move_card_between_zones");
        package = Set(package, CanonicalAbilityTableIds.Effects, "effect_aqu_mor_007_01_exhaust_target", "from_zone_id", "dominion");
        package = Set(package, CanonicalAbilityTableIds.Effects, "effect_aqu_mor_007_01_exhaust_target", "to_zone_id", "hand");
        package = CanonicalAbilityCatalogTests.AddRecord(package, CanonicalAbilityTableIds.EffectParameters, Parameter(
            "move_destination", "effect_aqu_mor_007_01_exhaust_target", "parameter_field_move_between_zones_destination_player",
            ("value_registry_value_id", "player_reference_subject_card_owner")));
        var catalog = CanonicalAbilityMaterializer.Materialize(package);
        var cards = CanonicalCardMaterializer.Materialize(package);
        var state = State(Board("ci_bounce", "IGN-LAN-003", "player_2", "player_2", DomainRow.Horizon, 2, 1));
        var ability = catalog.AbilitiesById["ability_aqu_mor_007_01"];
        var plan = Plan(
            ability,
            state,
            Runtime(package),
            cards,
            [new CanonicalTargetSelectionPayload(ability.Targets.Single().TargetId, ["ci_bounce"])]);
        CanonicalEffectExecutor.Apply(state, plan);
        Equal("hand", state.GetCardInstance("ci_bounce").Zone, "Move effect did not use the common Dominion-to-Hand transition.");
        Equal("ci_bounce", state.GetPlayer("player_2").HandCardInstanceIds.Single(), "Move effect used the wrong destination player.");
        Equal(0, state.GetCardInstance("ci_bounce").DamageMarked, "Move effect did not reset damage.");
    }

    internal static void ZoneChangedBridgeUsesAuthoritativeEventContext()
    {
        var package = CanonicalAbilityCatalogTests.CreatePackage();
        package = Set(package, CanonicalAbilityTableIds.Triggers, "trigger_ign_ham_005_01_entered_play", "event_type_id", "event_card_zone_changed");
        package = Set(package, CanonicalAbilityTableIds.Triggers, "trigger_ign_ham_005_01_entered_play", "from_zone_id", "dominion");
        package = Set(package, CanonicalAbilityTableIds.Triggers, "trigger_ign_ham_005_01_entered_play", "to_zone_id", "void");
        var catalog = CanonicalAbilityMaterializer.Materialize(package);
        var source = new CardInstanceState
        {
            CardInstanceId = "ci_echo",
            CardId = "IGN-HAM-005",
            OwnerPlayerId = "player_1",
            ControllerPlayerId = "player_1",
            Zone = "void",
            ZoneIndex = 0,
            Visibility = "public",
            CreatedSequence = 1,
            ZoneSequence = 2,
            InitialZone = "hand",
        };
        var state = State(source);
        state.StateVersion = 1;
        var payload = ContractJsonValue.From(new CardZoneChangedPayload(
            "transition_echo", "ci_echo", "dominion", "void", "zone_presence_ci_echo_000001",
            "zone_presence_ci_echo_000002", "destruction_echo", "IGN-HAM-005", "player_1", "player_1",
            "horizont", 0, 0, "public", "public", "ability_source", "effect_source", "resolution_source"));
        var engineEvent = new EngineEvent(
            ContractSchemas.EngineEvent, "event_000001", 1, "card_zone_changed", state.MatchId, 1, 1,
            "player_1", "resolve_triggered_ability", "public", payload);
        state.Events.Add(engineEvent);

        Equal("event_card_zone_changed", CanonicalTriggerResolver.MapEngineEventType("card_zone_changed"), "Canonical zone bridge is missing.");
        var discovery = CanonicalTriggerResolver.Resolve(catalog, engineEvent, state).Single();
        Equal("dominion", discovery.SourceFromZoneId, "Trigger lost authoritative from-zone context.");
        Equal("void", discovery.SourceToZoneId, "Trigger lost authoritative to-zone context.");
        Equal("transition_echo", discovery.SourceZoneTransitionInstanceId, "Trigger lost movement identity.");
        Equal("void", source.Zone, "Trigger discovery required the source to remain in Dominion.");

        var invalidPayload = ContractJsonValue.From(new CardZoneChangedPayload(
            "transition_invalid_echo", "ci_echo", "hand", "void", "zone_presence_ci_echo_000001",
            "zone_presence_ci_echo_000002", "move_invalid_echo", "IGN-HAM-005", "player_1", "player_1",
            "horizont", 0, 0, "owner_only", "public", "ability_source", "effect_source", "resolution_source"));
        var invalidEvent = engineEvent with { EventId = "event_invalid_echo", Payload = invalidPayload };
        state.Events[0] = invalidEvent;
        var beforeInvalid = StateFingerprint(state);
        ThrowsState("CANONICAL_TRIGGER_SOURCE_INVALID", () => CanonicalTriggerResolver.Resolve(catalog, invalidEvent, state));
        Equal(beforeInvalid, StateFingerprint(state), "Invalid Visszhang context mutated authoritative state.");
    }

    internal static void InvalidFilterAndMoveContractsRejectBeforeMutation()
    {
        var package = CompleteDominionTarget(
            CanonicalAbilityCatalogTests.CreatePackage(),
            "target_aqu_mor_007_01_enemy_horizont_entity");
        package = Set(package, CanonicalAbilityTableIds.Conditions, "condition_aqu_mor_007_01_magnitude_lte_3", "comparison_operator_id", "op_unknown");
        var catalog = CanonicalAbilityMaterializer.Materialize(package);
        var cards = CanonicalCardMaterializer.Materialize(package);
        var state = State(Board("ci_atomic", "IGN-HAM-001", "player_2", "player_2", DomainRow.Horizon, 0, 0));
        var before = StateFingerprint(state);
        ThrowsExecution("CANONICAL_TARGET_FILTER_UNSUPPORTED", () => Plan(
            catalog.AbilitiesById["ability_aqu_mor_007_01"],
            state,
            Runtime(package),
            cards,
            [new CanonicalTargetSelectionPayload("target_aqu_mor_007_01_enemy_horizont_entity", ["ci_atomic"])]));
        Equal(before, StateFingerprint(state), "Filter rejection mutated authoritative state.");

        var automatic = CreateHealPackage();
        automatic = Set(automatic, CanonicalAbilityTableIds.Targets, "target_aqu_mor_033_01_all_allied_entities", "optional", true);
        AssertPlanRejectedAtomically(
            "CANONICAL_TARGET_CONTRACT_UNSUPPORTED",
            automatic,
            "ability_aqu_mor_033_01",
            State(Board("ci_auto_invalid", "IGN-HAM-001", "player_1", "player_1", DomainRow.Horizon, 0, 1)),
            ImmutableArray<CanonicalTargetSelectionPayload>.Empty);

        var destroy = AddEffectVocabulary(CanonicalAbilityCatalogTests.CreatePackage(), "effect_destroy_entity");
        destroy = CompleteDominionTarget(destroy, "target_aqu_mor_007_01_enemy_horizont_entity");
        destroy = Set(destroy, CanonicalAbilityTableIds.Effects, "effect_aqu_mor_007_01_exhaust_target", "effect_action_type_id", "effect_destroy_entity");
        destroy = CanonicalAbilityCatalogTests.AddRecord(destroy, CanonicalAbilityTableIds.EffectParameters, Parameter(
            "destroy_invalid_parameter", "effect_aqu_mor_007_01_exhaust_target", "parameter_field_invalid", ("value_integer", 1)));
        AssertPlanRejectedAtomically(
            "CANONICAL_EFFECT_GRAPH_UNSUPPORTED",
            destroy,
            "ability_aqu_mor_007_01",
            State(Board("ci_destroy_invalid", "IGN-LAN-003", "player_2", "player_2", DomainRow.Horizon, 0, 0)),
            [new CanonicalTargetSelectionPayload("target_aqu_mor_007_01_enemy_horizont_entity", ["ci_destroy_invalid"])]);

        var move = AddEffectVocabulary(CanonicalAbilityCatalogTests.CreatePackage(), "effect_move_card_between_zones");
        move = CompleteDominionTarget(move, "target_aqu_mor_007_01_enemy_horizont_entity");
        move = Set(move, CanonicalAbilityTableIds.Effects, "effect_aqu_mor_007_01_exhaust_target", "effect_action_type_id", "effect_move_card_between_zones");
        move = Set(move, CanonicalAbilityTableIds.Effects, "effect_aqu_mor_007_01_exhaust_target", "from_zone_id", "dominion");
        move = Set(move, CanonicalAbilityTableIds.Effects, "effect_aqu_mor_007_01_exhaust_target", "to_zone_id", "void");
        move = CanonicalAbilityCatalogTests.AddRecord(move, CanonicalAbilityTableIds.EffectParameters, Parameter(
            "move_invalid_destination", "effect_aqu_mor_007_01_exhaust_target", "parameter_field_move_between_zones_destination_player",
            ("value_registry_value_id", "player_reference_subject_card_owner")));
        AssertPlanRejectedAtomically(
            "CANONICAL_EFFECT_GRAPH_UNSUPPORTED",
            move,
            "ability_aqu_mor_007_01",
            State(Board("ci_move_invalid", "IGN-LAN-003", "player_2", "player_2", DomainRow.Horizon, 0, 0)),
            [new CanonicalTargetSelectionPayload("target_aqu_mor_007_01_enemy_horizont_entity", ["ci_move_invalid"])]);

        var heal = CreateHealPackage();
        heal = Set(heal, CanonicalAbilityTableIds.EffectParameters, "heal_amount", "value_integer", 0);
        AssertPlanRejectedAtomically(
            "CANONICAL_EFFECT_GRAPH_UNSUPPORTED",
            heal,
            "ability_aqu_mor_033_01",
            State(Board("ci_heal_invalid", "IGN-HAM-001", "player_1", "player_1", DomainRow.Horizon, 0, 2)),
            ImmutableArray<CanonicalTargetSelectionPayload>.Empty);
    }

    private static CanonicalCardDatabasePackage CreateHealPackage()
    {
        var package = AddEffectVocabulary(CanonicalAbilityCatalogTests.CreatePackage(), "effect_heal_entity");
        package = Set(package, CanonicalAbilityTableIds.Effects, "effect_aqu_mor_033_01_max_hp_bonus", "effect_action_type_id", "effect_heal_entity");
        foreach (var field in new[] { "value_type_id", "value_number", "modifier_type_id" })
        {
            package = Set(package, CanonicalAbilityTableIds.Effects, "effect_aqu_mor_033_01_max_hp_bonus", field, null);
        }

        package = CanonicalAbilityCatalogTests.RemoveRecord(package, CanonicalAbilityTableIds.Effects, "effect_aqu_mor_033_01_grant_ward");
        package = CanonicalAbilityCatalogTests.RemoveRecord(package, CanonicalAbilityTableIds.Durations, "duration_aqu_mor_033_01_max_hp_turn");
        package = CanonicalAbilityCatalogTests.RemoveRecord(package, CanonicalAbilityTableIds.Durations, "duration_aqu_mor_033_01_ward_turn");
        package = CompleteDominionTarget(package, "target_aqu_mor_033_01_all_allied_entities");
        package = CanonicalAbilityCatalogTests.AddRecord(package, CanonicalAbilityTableIds.EffectParameters, Parameter(
            "heal_amount", "effect_aqu_mor_033_01_max_hp_bonus", "parameter_field_heal_entity_amount", ("value_integer", 2)));
        return CanonicalAbilityCatalogTests.AddRecord(package, CanonicalAbilityTableIds.EffectParameters, Parameter(
            "heal_miasma", "effect_aqu_mor_033_01_max_hp_bonus", "parameter_field_heal_entity_remove_miasma", ("value_boolean", false)));
    }

    private static void AssertPlanRejectedAtomically(
        string expectedCode,
        CanonicalCardDatabasePackage package,
        string abilityId,
        MatchState state,
        ImmutableArray<CanonicalTargetSelectionPayload> selections)
    {
        var catalog = CanonicalAbilityMaterializer.Materialize(package);
        var cards = CanonicalCardMaterializer.Materialize(package);
        var before = StateFingerprint(state);
        ThrowsExecution(expectedCode, () => Plan(catalog.AbilitiesById[abilityId], state, Runtime(package), cards, selections));
        Equal(before, StateFingerprint(state), $"{expectedCode} rejection mutated authoritative state.");
    }

    private static CanonicalEffectExecutionPlan Plan(
        CanonicalAbilityDefinition ability,
        MatchState state,
        RuntimePackageCatalog runtime,
        CanonicalCardCatalog cards,
        ImmutableArray<CanonicalTargetSelectionPayload> selections) => CanonicalEffectExecutor.BuildPlan(
        new CanonicalAbilityResolutionContext(
            "resolution_fixture", CanonicalResolutionOrigin.PlayedCard, "action_fixture", "play_card", ability,
            "ci_source", ability.CardId, "player_1", selections, null, null),
        state,
        runtime,
        cards);

    private static CanonicalCardDatabasePackage CompleteDominionTarget(
        CanonicalCardDatabasePackage package,
        string targetId)
    {
        package = Set(package, CanonicalAbilityTableIds.Targets, targetId, "game_object_id", "card_instance");
        package = Set(package, CanonicalAbilityTableIds.Targets, targetId, "card_type_id", "entity");
        package = Set(package, CanonicalAbilityTableIds.Targets, targetId, "zone_id", "dominion");
        return package;
    }

    private static CanonicalCardDatabasePackage AddEffectVocabulary(
        CanonicalCardDatabasePackage package,
        string effectActionTypeId) => AddRegistryRecord(
        package,
        "effect_action_types",
        CanonicalAbilityCatalogTests.Record(("effect_action_type_id", effectActionTypeId)));

    private static CanonicalCardDatabasePackage AddRegistryRecord(
        CanonicalCardDatabasePackage package,
        string tableId,
        CanonicalRecord record)
    {
        var table = package.Registry.Tables[tableId];
        var id = record.GetRequiredString(table.PrimaryKey);
        var changedTable = table with
        {
            Records = table.Records.Add(record),
            RecordsById = table.RecordsById.Add(id, record),
        };
        var registry = package.Registry with { Tables = package.Registry.Tables.SetItem(tableId, changedTable) };
        return package with { Registry = registry };
    }

    private static CanonicalCardDatabasePackage SetRegistryField(
        CanonicalCardDatabasePackage package,
        string tableId,
        string recordId,
        string fieldName,
        object? value)
    {
        var table = package.Registry.Tables[tableId];
        var record = table.RecordsById[recordId];
        var changedRecord = record with
        {
            Fields = record.Fields.SetItem(
                fieldName,
                JsonSerializer.SerializeToElement(value, value?.GetType() ?? typeof(object))),
        };
        var index = table.Records.IndexOf(record);
        var changedTable = table with
        {
            Records = table.Records.SetItem(index, changedRecord),
            RecordsById = table.RecordsById.SetItem(recordId, changedRecord),
        };
        var registry = package.Registry with { Tables = package.Registry.Tables.SetItem(tableId, changedTable) };
        return package with { Registry = registry };
    }

    private static CanonicalCardDatabasePackage Set(
        CanonicalCardDatabasePackage package,
        string tableId,
        string recordId,
        string field,
        object? value) => CanonicalAbilityCatalogTests.SetField(package, tableId, recordId, field, value);

    private static CanonicalRecord Parameter(
        string parameterId,
        string effectId,
        string fieldId,
        params (string Key, object? Value)[] values) => CanonicalAbilityCatalogTests.Record(
        new[]
        {
            ("effect_parameter_id", (object?)parameterId),
            ("effect_id", effectId),
            ("contract_field_id", fieldId),
            ("item_index", 1),
        }.Concat(values).ToArray());

    private static RuntimePackageCatalog Runtime(CanonicalCardDatabasePackage package)
    {
        var cards = CanonicalCardMaterializer.Materialize(package).Definitions.ToImmutableDictionary(
            card => card.CardId,
            card => new RuntimeCardDefinition(
                card.CardId,
                card.Magnitude,
                card.PrintedAuraCost,
                card.Realm,
                card.CardType == "entity" ? "entity" : card.CardType),
            StringComparer.Ordinal);
        return new RuntimePackageCatalog(
            "runtime_fixture",
            cards,
            ImmutableDictionary<string, RuntimeDeckDefinition>.Empty.WithComparers(StringComparer.Ordinal),
            new RuntimeLookupCatalog(ImmutableDictionary<string, RuntimeLookupGroup>.Empty.WithComparers(StringComparer.Ordinal)));
    }

    private static CardInstanceState Board(
        string instanceId,
        string cardId,
        string ownerId,
        string controllerId,
        DomainRow row,
        int lane,
        int damage) => new()
    {
        CardInstanceId = instanceId,
        CardId = cardId,
        OwnerPlayerId = ownerId,
        ControllerPlayerId = controllerId,
        Zone = "dominion",
        ZoneIndex = -1,
        Visibility = "public",
        CreatedSequence = lane + 1,
        ZoneSequence = 1,
        InitialZone = "hand",
        ActivityState = "active",
        DomainRow = row,
        DomainLaneIndex = lane,
        EnteredDomainTurnNumber = 1,
        DamageMarked = damage,
    };

    private static MatchState State(params CardInstanceState[] cards)
    {
        var state = new MatchState
        {
            MatchId = "template-zone-fixture",
            Seed = 1,
            RuntimePackageId = "runtime_fixture",
            Phase = CanonicalPhaseIds.Manifestation,
            StartingPlayerId = "player_1",
            ActivePlayerId = "player_1",
            PriorityPlayerId = "player_1",
        };
        state.Players.Add(new PlayerState { PlayerId = "player_1", DeckId = "deck_1" });
        state.Players.Add(new PlayerState { PlayerId = "player_2", DeckId = "deck_2" });
        foreach (var card in cards)
        {
            state.CardInstances.Add(card.CardInstanceId, card);
            var owner = state.GetPlayer(card.OwnerPlayerId);
            if (card.Zone == "dominion")
            {
                state.GetPlayer(card.ControllerPlayerId).Domain.GetSlots(card.DomainRow!.Value)[card.DomainLaneIndex!.Value] = card.CardInstanceId;
            }
            else if (card.Zone == "void")
            {
                owner.VoidCardInstanceIds.Add(card.CardInstanceId);
            }
            else if (card.Zone == "hand")
            {
                owner.HandCardInstanceIds.Add(card.CardInstanceId);
            }
        }

        return state;
    }

    private static string Fingerprint(CanonicalAbilityDefinition ability) => JsonSerializer.Serialize(new
    {
        ability.AbilityId,
        ability.ImplementationModeId,
        ability.TemplateProvenance,
        ability.Targets,
        ability.Effects,
        ability.Triggers,
    });

    private static string StateFingerprint(MatchState state) => JsonSerializer.Serialize(new
    {
        state.StateVersion,
        state.TurnNumber,
        state.Phase,
        state.ActivePlayerId,
        state.PriorityPlayerId,
        Events = state.Events,
        Players = state.Players.Select(player => new
        {
            player.PlayerId,
            Deck = player.DeckCardInstanceIds,
            Hand = player.HandCardInstanceIds,
            Void = player.VoidCardInstanceIds,
            Wellspring = player.WellspringCardInstanceIds,
            Horizon = player.Domain.HorizonCardInstanceIds,
            Zenith = player.Domain.ZenithCardInstanceIds,
            player.NormalInflowUsedTurnNumber,
        }),
        Pending = state.PendingTriggerWindow is null ? null : new
        {
            state.PendingTriggerWindow.PendingWindowId,
            state.PendingTriggerWindow.ControllerPlayerId,
            Triggers = state.PendingTriggerWindow.PendingTriggers,
        },
        Cards = state.CardInstances.Values.OrderBy(card => card.CardInstanceId).Select(card => new
        {
            card.CardInstanceId,
            card.CardId,
            card.OwnerPlayerId,
            card.ControllerPlayerId,
            card.Zone,
            card.ZoneIndex,
            card.Visibility,
            card.ZoneSequence,
            card.DamageMarked,
            card.ActivityState,
            card.DomainRow,
            card.DomainLaneIndex,
            card.EnteredDomainTurnNumber,
        }),
    });

    private static void ThrowsInput(string code, Action action)
    {
        try { action(); }
        catch (EngineInputException exception) when (exception.Code == code) { return; }
        throw new InvalidOperationException($"Expected EngineInputException: {code}");
    }

    private static void ThrowsExecution(string code, Action action)
    {
        try { action(); }
        catch (CanonicalAbilityExecutionException exception) when (exception.Code == code) { return; }
        throw new InvalidOperationException($"Expected CanonicalAbilityExecutionException: {code}");
    }

    private static void ThrowsState(string code, Action action)
    {
        try { action(); }
        catch (EngineStateException exception) when (exception.Code == code) { return; }
        throw new InvalidOperationException($"Expected EngineStateException: {code}");
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
}
