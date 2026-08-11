using System.Collections.Immutable;
using System.Text.Json;
using Aeterna.Engine.Runtime;

internal static class CanonicalAbilityCatalogTests
{
    public static void IntrinsicKeywordOnlyCardMaterializes()
    {
        var catalog = Materialize();

        True(!catalog.AbilitiesByCardId.ContainsKey("IGN-HAM-001"), "Keyword-only fixture unexpectedly acquired an ability.");
        var keyword = Single(catalog.KeywordsByCardId["IGN-HAM-001"]);
        Equal("speed", keyword.KeywordId, "Intrinsic keyword identity was not preserved.");
        Equal(1, keyword.Sequence, "Intrinsic keyword order was not preserved.");
    }

    public static void SingleTargetTriggeredGraphMaterializes()
    {
        var ability = Single(Materialize().AbilitiesByCardId["IGN-HAM-005"]);

        Equal("triggered", ability.AbilityKindId, "Triggered ability kind was not preserved.");
        Equal("event_card_entered_play", Single(ability.Triggers).EventTypeId, "Trigger relationship was not preserved.");
        var target = Single(ability.Targets);
        Equal("target_choose_one_card", target.TargetPrimitiveId, "Target primitive was not preserved.");
        Equal(1, target.MinimumTargets, "Target minimum was not preserved.");
        Equal(1, target.MaximumTargets, "Target maximum was not preserved.");
        var effect = Single(ability.Effects);
        Equal("effect_exhaust_card", effect.EffectActionTypeId, "Effect action was not preserved.");
        Equal(target.TargetId, effect.TargetId, "Effect-to-target relationship was not preserved.");
    }

    public static void IgnHam044ResolutionGraphMaterializes()
    {
        var ability = Single(Materialize().AbilitiesByCardId["IGN-HAM-044"]);

        Equal("resolution", ability.AbilityKindId, "IGN-HAM-044 ability kind is invalid.");
        Equal("full_resolution_required", ability.ResolutionRequirementId, "IGN-HAM-044 resolution requirement is invalid.");
        Equal("hand", ability.ActiveZoneId, "IGN-HAM-044 active zone is invalid.");
        True(ability.IsStructuredGraphAuthority, "IGN-HAM-044 is not direct structured authority.");
        Equal(null, ability.AbilityTemplateId, "IGN-HAM-044 unexpectedly uses a template.");
        var target = Single(ability.Targets);
        Equal("opponent_of_ability_controller", target.PlayerReferenceId, "IGN-HAM-044 target player is invalid.");
        Equal("zenit", target.DomainRowId, "IGN-HAM-044 target row is invalid.");
        Equal("active", target.ActivityStateId, "IGN-HAM-044 target activity is invalid.");
        Equal("effect_exhaust_card", Single(ability.Effects).EffectActionTypeId, "IGN-HAM-044 effect is invalid.");
        Equal(0, ability.Conditions.Length, "IGN-HAM-044 unexpectedly has a condition.");
        Equal(0, ability.Expressions.Length, "IGN-HAM-044 unexpectedly has an expression.");
        Equal(0, Single(ability.Effects).Durations.Length, "IGN-HAM-044 unexpectedly has a duration.");
    }

    public static void SequentialMultiEffectGraphMaterializes()
    {
        var ability = Single(Materialize().AbilitiesByCardId["AQU-ART-044"]);
        var target = Single(ability.Targets);

        Equal(0, target.MinimumTargets, "Optional target minimum was not preserved.");
        Equal(2, target.MaximumTargets, "Optional target maximum was not preserved.");
        True(target.Optional, "Optional target flag was not preserved.");
        Equal("effect_exhaust_card", ability.Effects[0].EffectActionTypeId, "First effect order is incorrect.");
        Equal("effect_deal_damage", ability.Effects[1].EffectActionTypeId, "Second effect order is incorrect.");
        Equal(1, ability.Effects[0].Sequence, "First effect sequence was not preserved.");
        Equal(2, ability.Effects[1].Sequence, "Second effect sequence was not preserved.");
        Equal(2, ability.Effects[1].Parameters.Length, "Damage parameters were not attached to their effect.");
        Equal(2, ability.Effects[1].Parameters.Single(value => value.ContractFieldId == "parameter_field_deal_damage_amount").ValueInteger, "Damage amount was not preserved.");
    }

    public static void ConditionExpressionFilteredTargetMaterializes()
    {
        var catalog = Materialize();
        var ability = Single(catalog.AbilitiesByCardId["AQU-MOR-007"]);
        var target = Single(ability.Targets);
        var condition = Single(ability.Conditions);

        Equal(condition.ConditionId, target.FilterConditionId, "Target filter relationship was not preserved.");
        Equal("op_less_than_or_equal", condition.ComparisonOperatorId, "Comparison operator was not preserved.");
        Equal("card_magnitude", catalog.ExpressionsById[condition.LeftExpressionId!].FieldId, "Magnitude field expression was not preserved.");
        Equal("ref_target_candidate_card", catalog.ExpressionsById[condition.LeftExpressionId!].ReferenceTypeId, "Target-candidate reference was not preserved.");
        Equal(3, catalog.ExpressionsById[condition.RightExpressionId!].LiteralNumber, "Magnitude literal was not preserved.");
    }

    public static void StaticRestrictionGraphMaterializes()
    {
        var ability = Single(Materialize().AbilitiesByCardId["AQU-MOR-017"]);
        var target = Single(ability.Targets);
        var effect = Single(ability.Effects);

        Equal("static", ability.AbilityKindId, "Static ability kind was not preserved.");
        Equal("target_reference_ability_source_card", target.TargetPrimitiveId, "Source-card target was not preserved.");
        Equal("effect_apply_restriction", effect.EffectActionTypeId, "Restriction action was not preserved.");
        Equal("restriction_entity_cannot_initiate_attack", effect.RestrictionTypeId, "Restriction identity was not preserved.");
        Equal("duration_while_source_in_required_zone", Single(effect.Durations).DurationPolicyId, "Static duration was not preserved.");
    }

    public static void MassTemporaryBuffGraphMaterializes()
    {
        var ability = Single(Materialize().AbilitiesByCardId["AQU-MOR-033"]);

        Equal("target_all_matching_cards", Single(ability.Targets).TargetPrimitiveId, "All-matching target was not preserved.");
        Equal("modifier_entity_max_hp_additive", ability.Effects[0].ModifierTypeId, "Maximum-HP modifier was not preserved.");
        Equal(1, ability.Effects[0].ValueNumber, "Maximum-HP modifier value was not preserved.");
        Equal("effect_grant_keyword", ability.Effects[1].EffectActionTypeId, "Keyword-grant action was not preserved.");
        Equal("keyword_ward", ability.Effects[1].ValueRegistryValueId, "Oltalom canonical identity was not preserved.");
        Equal("duration_until_end_of_current_turn", Single(ability.Effects[0].Durations).DurationPolicyId, "First duration was not preserved.");
        Equal("duration_until_end_of_current_turn", Single(ability.Effects[1].Durations).DurationPolicyId, "Second duration was not preserved.");
    }

    public static void TemplateInstanceNormalizesWithProvenance()
    {
        var ability = Single(Materialize().AbilitiesByCardId["LUX-FHL-034"]);

        True(ability.IsTemplateInstanceAuthority, "Template-instance authority was not identified.");
        True(ability.IsStructuredGraphAuthority, "Template instance was not normalized to structured graph authority.");
        Equal("template_resolution_damage_all_enemy_horizont_entities_v1", ability.Template?.TemplateId, "Template relationship was not resolved.");
        Equal(2, Single(ability.TemplateArguments).ValueInteger, "Template argument was not preserved.");
        Equal("template_resolution_damage_all_enemy_horizont_entities_v1", ability.TemplateProvenance?.TemplateId, "Template provenance was not retained.");
        Equal("effect_deal_damage", Single(ability.Effects).EffectActionTypeId, "Template effect was not expanded.");
        Equal("all_matching", Single(ability.Targets).SelectionMethodId, "Template automatic target was not expanded.");
        Equal(2, Single(ability.Effects).Parameters.Single(parameter => parameter.ContractFieldId == "parameter_field_deal_damage_amount").ValueInteger, "Typed argument was not bound.");
    }

    public static void CatalogIsImmutableDeterministicAndLossless()
    {
        var catalog = Materialize();
        var effects = catalog.EffectsByAbilityId["ability_aqu_art_044_01"];

        Equal(StringComparer.Ordinal, catalog.AbilitiesById.KeyComparer, "Ability index does not use ordinal identity.");
        Equal(StringComparer.Ordinal, catalog.KeywordsByCardId.KeyComparer, "Keyword index does not use ordinal identity.");
        Equal(1, effects[0].Sequence, "Deterministic effect order is incorrect.");
        Equal(2, effects[1].Sequence, "Deterministic effect order is incorrect.");
        Equal("preserved", effects[1].RawFields["future_field"].GetString(), "Unmodeled canonical field was discarded.");
        var changed = catalog.AbilitiesById.SetItem("other", catalog.AbilitiesById.Values.First());
        True(!catalog.AbilitiesById.ContainsKey("other"), "Immutable ability index was mutated.");
        True(changed.ContainsKey("other"), "Immutable ability index copy operation failed.");
    }

    public static void MissingParentAbilityIsRejected() =>
        ThrowsCode(
            "CANONICAL_ABILITY_REFERENCE_MISSING",
            () => CanonicalAbilityMaterializer.Materialize(SetField(CreatePackage(), CanonicalAbilityTableIds.Targets, "target_ign_ham_005_01_enemy_horizont_entity", "ability_id", "missing_ability")));

    public static void MissingEffectTargetIsRejected() =>
        ThrowsCode(
            "CANONICAL_ABILITY_REFERENCE_MISSING",
            () => CanonicalAbilityMaterializer.Materialize(SetField(CreatePackage(), CanonicalAbilityTableIds.Effects, "effect_ign_ham_005_01_exhaust_target", "target_id", "missing_target")));

    public static void CrossAbilityTargetReferenceIsRejected() =>
        ThrowsCode(
            "CANONICAL_ABILITY_REFERENCE_SCOPE_MISMATCH",
            () => CanonicalAbilityMaterializer.Materialize(SetField(CreatePackage(), CanonicalAbilityTableIds.Effects, "effect_ign_ham_005_01_exhaust_target", "target_id", "target_aqu_art_044_01_enemy_horizont_entities")));

    public static void MissingDurationEffectIsRejected() =>
        ThrowsCode(
            "CANONICAL_ABILITY_REFERENCE_MISSING",
            () => CanonicalAbilityMaterializer.Materialize(SetField(CreatePackage(), CanonicalAbilityTableIds.Durations, "duration_aqu_mor_017_01_attack_prohibition_source_zone", "effect_id", "missing_effect")));

    public static void InvalidSequenceTypeIsRejected() =>
        ThrowsCode(
            "CANONICAL_ABILITY_FIELD_INVALID",
            () => CanonicalAbilityMaterializer.Materialize(SetField(CreatePackage(), CanonicalAbilityTableIds.Targets, "target_ign_ham_005_01_enemy_horizont_entity", "sequence", "1")));

    public static void DuplicateStableIdIsRejected() =>
        ThrowsCode(
            "CANONICAL_ABILITY_ID_DUPLICATE",
            () => CanonicalAbilityMaterializer.Materialize(DuplicateFirstRecord(CreatePackage(), CanonicalAbilityTableIds.Effects)));

    public static void DuplicateSequenceInCanonicalScopeIsRejected() =>
        ThrowsCode(
            "CANONICAL_ABILITY_SEQUENCE_DUPLICATE",
            () => CanonicalAbilityMaterializer.Materialize(SetField(CreatePackage(), CanonicalAbilityTableIds.Effects, "effect_aqu_art_044_01_damage_selected", "sequence", 1)));

    public static void UnknownRequiredRegistryVocabularyIsRejected() =>
        ThrowsCode(
            "CANONICAL_ABILITY_VOCABULARY_UNKNOWN",
            () => CanonicalAbilityMaterializer.Materialize(SetField(CreatePackage(), CanonicalAbilityTableIds.Effects, "effect_ign_ham_005_01_exhaust_target", "effect_action_type_id", "effect_unknown")));

    public static void MissingTemplateReferenceIsRejected() =>
        ThrowsCode(
            "CANONICAL_ABILITY_TEMPLATE_MISSING",
            () => CanonicalAbilityMaterializer.Materialize(SetField(CreatePackage(), CanonicalAbilityTableIds.Abilities, "ability_lux_fhl_034_01", "ability_template_id", "template_missing")));

    public static void MalformedRequiredFieldTypeIsRejected() =>
        ThrowsCode(
            "CANONICAL_ABILITY_FIELD_INVALID",
            () => CanonicalAbilityMaterializer.Materialize(SetField(CreatePackage(), CanonicalAbilityTableIds.Abilities, "ability_ign_ham_005_01", "card_id", 7)));

    private static CanonicalAbilityCatalog Materialize() => CanonicalAbilityMaterializer.Materialize(CreatePackage());

    internal static CanonicalCardDatabasePackage CreatePackage()
    {
        var registryTables = ImmutableDictionary.CreateBuilder<string, CanonicalTable>(StringComparer.Ordinal);
        registryTables.Add("schema_fields", Table("schema_fields", "field_id"));
        registryTables.Add("value_registry", Table(
            "value_registry",
            "value_id",
            Record(("value_id", "entity"), ("group_id", "card_type")),
            Record(("value_id", "spell"), ("group_id", "card_type")),
            Record(("value_id", "ritual"), ("group_id", "card_type")),
            Record(("value_id", "sign"), ("group_id", "card_type")),
            Record(("value_id", "plane"), ("group_id", "card_type")),
            Record(("value_id", "ignis"), ("group_id", "realm")),
            Record(("value_id", "aqua"), ("group_id", "realm")),
            Record(("value_id", "active"), ("group_id", "record_status"))));
        registryTables.Add(CanonicalAbilityTableIds.AbilityTemplates, Table(
            CanonicalAbilityTableIds.AbilityTemplates,
            "ability_template_id",
            Record(
                ("ability_template_id", "template_resolution_damage_all_enemy_horizont_entities_v1"),
                ("template_version", "1.0.0"),
                ("parameter_schema_id", "parameters_template_resolution_damage_all_enemy_horizont_entities_v1"),
                ("ability_kind_id", "resolution"),
                ("resolution_requirement_id", "full_resolution_required"),
                ("default_active_zone_id", "hand"),
                ("expansion_policy_id", "load_time_compile"),
                ("minimum_carddatabase_schema_version", "0.7.0"))));
        registryTables.Add(CanonicalAbilityTableIds.AbilityTemplateNodes, Table(
            CanonicalAbilityTableIds.AbilityTemplateNodes,
            "template_node_id",
            TemplateNodes().ToArray()));
        registryTables.Add(CanonicalAbilityTableIds.AbilityTemplateBindings, Table(
            CanonicalAbilityTableIds.AbilityTemplateBindings,
            "template_binding_id",
            TemplateBindings().ToArray()));
        registryTables.Add(CanonicalAbilityTableIds.ContractFields, Table(
            CanonicalAbilityTableIds.ContractFields,
            "contract_field_id",
            Record(
                ("contract_field_id", "parameter_field_template_damage_all_enemy_horizont_amount"),
                ("contract_schema_id", "parameters_template_resolution_damage_all_enemy_horizont_entities_v1"),
                ("field_order", 1),
                ("data_type", "integer"),
                ("required_mode", "always"),
                ("nullable", false),
                ("is_collection", false))));
        registryTables.Add("effect_action_types", VocabularyTable(
            "effect_action_types",
            "effect_action_type_id",
            "effect_exhaust_card",
            "effect_deal_damage",
            "effect_apply_restriction",
            "effect_apply_modifier",
            "effect_grant_keyword"));
        var registry = new CanonicalRegistryPackage(
            "aeterna_registry",
            "0.5.1",
            "0.16.7",
            CanonicalPackageLoader.RegistryManifestFileName,
            "registry.meta.json",
            registryTables.ToImmutable());

        var tables = ImmutableDictionary.CreateBuilder<string, CanonicalTable>(StringComparer.Ordinal);
        var schemaFieldRecords = new[]
        {
            Record(
                ("field_id", "cdb_fld_ability_effects_effect_action_type_id"),
                ("table_id", CanonicalAbilityTableIds.Effects),
                ("field_name", "effect_action_type_id"),
                ("data_type", "string"),
                ("allowed_group_id", null),
                ("reference_table_id", "registry:effect_action_types")),
        }.Concat(TemplateSchemaFields()).ToArray();
        tables.Add("schema_fields", Table("schema_fields", "field_id", schemaFieldRecords));
        tables.Add(CanonicalAbilityTableIds.Cards, Table(
            CanonicalAbilityTableIds.Cards,
            "card_id",
            Card("IGN-HAM-001"),
            Card("IGN-HAM-005"),
            Card("IGN-HAM-044"),
            Card("IGN-LAN-003", printedHp: 2, printedAtk: 2),
            Card("IGN-LAN-031", cardType: "ritual", magnitude: 1, auraCost: 2),
            Card("AQU-ART-044", cardType: "spell", realm: "aqua", magnitude: 5, auraCost: 4),
            Card("AQU-MOR-007"),
            Card("AQU-MOR-017"),
            Card("AQU-MOR-033"),
            Card("LUX-FHL-034"),
            Card("FIXTURE-CARD-P1-001", magnitude: 1, auraCost: 1),
            Card("FIXTURE-CARD-P1-002", magnitude: 1, auraCost: 1),
            Card("FIXTURE-CARD-P1-003", magnitude: 1, auraCost: 1),
            Card("FIXTURE-CARD-P2-001", magnitude: 1, auraCost: 1),
            Card("FIXTURE-CARD-P2-002", magnitude: 1, auraCost: 1),
            Card("FIXTURE-CARD-P2-003", magnitude: 1, auraCost: 1)));
        tables.Add(CanonicalAbilityTableIds.CardKeywords, Table(
            CanonicalAbilityTableIds.CardKeywords,
            "card_keyword_id",
            Record(
                ("card_keyword_id", "cardkw_ign_ham_001_speed"),
                ("card_id", "IGN-HAM-001"),
                ("keyword_id", "speed"),
                ("numeric_value", null),
                ("text_value", null),
                ("sequence", 1))));
        tables.Add(CanonicalAbilityTableIds.Abilities, Table(
            CanonicalAbilityTableIds.Abilities,
            "ability_id",
            StructuredAbility("ability_ign_ham_005_01", "IGN-HAM-005", "triggered", "full_resolution_required", "dominion"),
            StructuredAbility("ability_ign_ham_044_01", "IGN-HAM-044", "resolution", "full_resolution_required", "hand"),
            StructuredAbility("ability_ign_lan_003_01", "IGN-LAN-003", "triggered", "full_resolution_required", "dominion"),
            StructuredAbility("ability_ign_lan_031_01", "IGN-LAN-031", "resolution", "full_resolution_required", "hand"),
            StructuredAbility("ability_aqu_art_044_01", "AQU-ART-044", "resolution", "full_resolution_required", "hand"),
            StructuredAbility("ability_aqu_mor_007_01", "AQU-MOR-007", "triggered", "full_resolution_required", "dominion"),
            StructuredAbility("ability_aqu_mor_017_01", "AQU-MOR-017", "static", null, "dominion"),
            StructuredAbility("ability_aqu_mor_033_01", "AQU-MOR-033", "resolution", "full_resolution_required", "hand"),
            Record(
                ("ability_id", "ability_lux_fhl_034_01"),
                ("card_id", "LUX-FHL-034"),
                ("ability_index", 1),
                ("ability_kind_id", null),
                ("resolution_requirement_id", null),
                ("active_zone_id", null),
                ("implementation_mode_id", "template_instance"),
                ("ability_template_id", "template_resolution_damage_all_enemy_horizont_entities_v1"),
                ("module_key", null),
                ("parent_ability_id", null))));
        tables.Add(CanonicalAbilityTableIds.Targets, Table(
            CanonicalAbilityTableIds.Targets,
            "target_id",
            Target("target_ign_ham_005_01_enemy_horizont_entity", "ability_ign_ham_005_01", "target_choose_one_card", 1, 1, false, null,
                ("reference_type_id", "ref_selected_card_exactly_one"), ("game_object_id", "card_instance"), ("card_type_id", "entity"),
                ("player_reference_id", "opponent_of_ability_controller"), ("zone_id", "dominion"),
                ("domain_row_id", "horizont"), ("activity_state_id", "active")),
            Target("target_ign_ham_044_01_enemy_zenit_entity", "ability_ign_ham_044_01", "target_choose_one_card", 1, 1, false, null,
                ("reference_type_id", "ref_selected_card_exactly_one"), ("game_object_id", "card_instance"), ("card_type_id", "entity"),
                ("player_reference_id", "opponent_of_ability_controller"), ("zone_id", "dominion"),
                ("domain_row_id", "zenit"), ("activity_state_id", "active")),
            Target("target_ign_lan_003_01_enemy_entity", "ability_ign_lan_003_01", "target_choose_one_card", 1, 1, false, null,
                ("reference_type_id", "ref_selected_card_exactly_one"), ("game_object_id", "card_instance"), ("card_type_id", "entity"),
                ("player_reference_id", "opponent_of_ability_controller"), ("zone_id", "dominion"),
                ("domain_row_id", null), ("activity_state_id", null)),
            Target("target_ign_lan_031_01_enemy_entities", "ability_ign_lan_031_01", "target_choose_cards_zero_or_more", 0, 2, true, null,
                ("reference_type_id", "ref_selected_cards_zero_or_more"), ("game_object_id", "card_instance"), ("card_type_id", "entity"),
                ("player_reference_id", "opponent_of_ability_controller"), ("zone_id", "dominion"),
                ("domain_row_id", null), ("activity_state_id", null)),
            Target("target_aqu_art_044_01_enemy_horizont_entities", "ability_aqu_art_044_01", "target_choose_cards_zero_or_more", 0, 2, true, null,
                ("reference_type_id", "ref_selected_cards_zero_or_more"), ("game_object_id", "card_instance"), ("card_type_id", "entity"),
                ("player_reference_id", "opponent_of_ability_controller"), ("zone_id", "dominion"),
                ("domain_row_id", "horizont"), ("activity_state_id", null)),
            Target("target_aqu_mor_007_01_enemy_horizont_entity", "ability_aqu_mor_007_01", "target_choose_one_card", 1, 1, false, "condition_aqu_mor_007_01_magnitude_lte_3",
                ("reference_type_id", "ref_selected_card_exactly_one"), ("player_reference_id", "opponent_of_ability_controller"), ("domain_row_id", "horizont")),
            Target("target_aqu_mor_017_01_source_card", "ability_aqu_mor_017_01", "target_reference_ability_source_card", 1, 1, false, null,
                ("target_role_id", "reference_subject"), ("reference_type_id", "ref_ability_source_card"), ("selection_method_id", "automatic_reference")),
            Target("target_aqu_mor_033_01_all_allied_entities", "ability_aqu_mor_033_01", "target_all_matching_cards", 0, 12, false, null,
                ("reference_type_id", "ref_all_matching_cards_zero_or_more"), ("player_reference_id", "ability_controller"), ("selection_method_id", "all_matching"))));
        tables.Add(CanonicalAbilityTableIds.Effects, Table(
            CanonicalAbilityTableIds.Effects,
            "effect_id",
            Effect("effect_ign_ham_005_01_exhaust_target", "ability_ign_ham_005_01", 1, "effect_exhaust_card", "target_ign_ham_005_01_enemy_horizont_entity"),
            Effect("effect_ign_ham_044_01_exhaust_target", "ability_ign_ham_044_01", 1, "effect_exhaust_card", "target_ign_ham_044_01_enemy_zenit_entity"),
            Effect("effect_ign_lan_003_01_deal_damage", "ability_ign_lan_003_01", 1, "effect_deal_damage", "target_ign_lan_003_01_enemy_entity"),
            Effect("effect_ign_lan_031_01_deal_damage", "ability_ign_lan_031_01", 1, "effect_deal_damage", "target_ign_lan_031_01_enemy_entities"),
            Effect("effect_aqu_art_044_01_exhaust_selected", "ability_aqu_art_044_01", 1, "effect_exhaust_card", "target_aqu_art_044_01_enemy_horizont_entities"),
            Effect("effect_aqu_art_044_01_damage_selected", "ability_aqu_art_044_01", 2, "effect_deal_damage", "target_aqu_art_044_01_enemy_horizont_entities", ("future_field", "preserved")),
            Effect("effect_aqu_mor_007_01_exhaust_target", "ability_aqu_mor_007_01", 1, "effect_exhaust_card", "target_aqu_mor_007_01_enemy_horizont_entity"),
            Effect("effect_aqu_mor_017_01_attack_prohibition", "ability_aqu_mor_017_01", 1, "effect_apply_restriction", "target_aqu_mor_017_01_source_card", ("restriction_type_id", "restriction_entity_cannot_initiate_attack")),
            Effect("effect_aqu_mor_033_01_max_hp_bonus", "ability_aqu_mor_033_01", 1, "effect_apply_modifier", "target_aqu_mor_033_01_all_allied_entities", ("value_type_id", "number"), ("value_number", 1), ("modifier_type_id", "modifier_entity_max_hp_additive")),
            Effect("effect_aqu_mor_033_01_grant_ward", "ability_aqu_mor_033_01", 2, "effect_grant_keyword", "target_aqu_mor_033_01_all_allied_entities", ("value_type_id", "registry_value"), ("value_registry_value_id", "keyword_ward"))));
        tables.Add(CanonicalAbilityTableIds.EffectParameters, Table(
            CanonicalAbilityTableIds.EffectParameters,
            "effect_parameter_id",
            Parameter("effectparam_ign_lan_003_01_damage_kind", "effect_ign_lan_003_01_deal_damage", "parameter_field_deal_damage_damage_kind", ("value_registry_value_id", "damage_kind_direct")),
            Parameter("effectparam_ign_lan_003_01_damage_amount", "effect_ign_lan_003_01_deal_damage", "parameter_field_deal_damage_amount", ("value_integer", 1)),
            Parameter("effectparam_ign_lan_031_01_damage_kind", "effect_ign_lan_031_01_deal_damage", "parameter_field_deal_damage_damage_kind", ("value_registry_value_id", "damage_kind_direct")),
            Parameter("effectparam_ign_lan_031_01_damage_amount", "effect_ign_lan_031_01_deal_damage", "parameter_field_deal_damage_amount", ("value_integer", 2)),
            Parameter("effectparam_aqu_art_044_01_damage_kind", "effect_aqu_art_044_01_damage_selected", "parameter_field_deal_damage_damage_kind", ("value_registry_value_id", "damage_kind_direct")),
            Parameter("effectparam_aqu_art_044_01_damage_amount", "effect_aqu_art_044_01_damage_selected", "parameter_field_deal_damage_amount", ("value_integer", 2))));
        tables.Add(CanonicalAbilityTableIds.Triggers, Table(
            CanonicalAbilityTableIds.Triggers,
            "trigger_id",
            Trigger("trigger_ign_ham_005_01_entered_play", "ability_ign_ham_005_01"),
            Trigger("trigger_ign_lan_003_01_entered_play", "ability_ign_lan_003_01"),
            Trigger("trigger_aqu_mor_007_01_entered_play", "ability_aqu_mor_007_01")));
        tables.Add(CanonicalAbilityTableIds.Conditions, Table(
            CanonicalAbilityTableIds.Conditions,
            "condition_id",
            Record(
                ("condition_id", "condition_aqu_mor_007_01_magnitude_lte_3"),
                ("ability_id", "ability_aqu_mor_007_01"),
                ("parent_condition_id", null),
                ("sequence", 1),
                ("condition_kind_id", "comparison"),
                ("logical_operator_id", null),
                ("negated", false),
                ("left_expression_id", "expr_aqu_mor_007_01_candidate_magnitude"),
                ("comparison_operator_id", "op_less_than_or_equal"),
                ("right_expression_id", "expr_aqu_mor_007_01_max_magnitude"))));
        tables.Add(CanonicalAbilityTableIds.Expressions, Table(
            CanonicalAbilityTableIds.Expressions,
            "expression_id",
            Expression("expr_aqu_mor_007_01_candidate_magnitude", 1,
                ("expression_kind_id", "field_reference"), ("reference_type_id", "ref_target_candidate_card"), ("field_id", "card_magnitude")),
            Expression("expr_aqu_mor_007_01_max_magnitude", 2,
                ("expression_kind_id", "literal"), ("literal_data_type_id", "integer"), ("literal_number", 3))));
        tables.Add(CanonicalAbilityTableIds.Durations, Table(
            CanonicalAbilityTableIds.Durations,
            "duration_id",
            Duration("duration_aqu_mor_017_01_attack_prohibition_source_zone", "effect_aqu_mor_017_01_attack_prohibition", "duration_while_source_in_required_zone", ("dependency_reference_type_id", "ref_ability_source_card")),
            Duration("duration_aqu_mor_033_01_max_hp_turn", "effect_aqu_mor_033_01_max_hp_bonus", "duration_until_end_of_current_turn"),
            Duration("duration_aqu_mor_033_01_ward_turn", "effect_aqu_mor_033_01_grant_ward", "duration_until_end_of_current_turn")));
        tables.Add(CanonicalAbilityTableIds.TemplateArguments, Table(
            CanonicalAbilityTableIds.TemplateArguments,
            "ability_argument_id",
            Record(
                ("ability_argument_id", "arg_lux_fhl_034_01_damage_amount"),
                ("ability_id", "ability_lux_fhl_034_01"),
                ("contract_field_id", "parameter_field_template_damage_all_enemy_horizont_amount"),
                ("item_index", 1),
                ("value_integer", 2))));

        return new CanonicalCardDatabasePackage(
            "aeterna_carddatabase",
            "0.7.0",
            "0.19.1",
            CanonicalPackageLoader.CardDatabaseManifestFileName,
            "carddatabase.meta.json",
            tables.ToImmutable(),
            registry);
    }

    private static CanonicalRecord Card(
        string cardId,
        string cardType = "entity",
        string realm = "ignis",
        int magnitude = 0,
        int auraCost = 0,
        int? printedAtk = null,
        int? printedHp = null) => Record(
        ("card_id", cardId),
        ("card_type_id", cardType),
        ("realm_id", realm),
        ("magnitude", magnitude),
        ("aura_cost", auraCost),
        ("atk", string.Equals(cardType, "entity", StringComparison.Ordinal) ? printedAtk ?? 1 : null),
        ("hp", string.Equals(cardType, "entity", StringComparison.Ordinal) ? printedHp ?? 1 : null),
        ("status", "active"));

    private static CanonicalRecord StructuredAbility(string abilityId, string cardId, string abilityKind, string? resolution, string zone) => Record(
        ("ability_id", abilityId),
        ("card_id", cardId),
        ("ability_index", 1),
        ("ability_kind_id", abilityKind),
        ("resolution_requirement_id", resolution),
        ("active_zone_id", zone),
        ("implementation_mode_id", "structured_data"),
        ("ability_template_id", null),
        ("module_key", null),
        ("parent_ability_id", null));

    private static CanonicalRecord Target(
        string targetId,
        string abilityId,
        string primitive,
        int minimum,
        int maximum,
        bool optional,
        string? filterConditionId,
        params (string Key, object? Value)[] overrides) => Record(Merge(
        [
            ("target_id", targetId),
            ("ability_id", abilityId),
            ("sequence", 1),
            ("target_role_id", "primary"),
            ("target_primitive_id", primitive),
            ("selection_method_id", "controller_choice"),
            ("minimum_targets", minimum),
            ("maximum_targets", maximum),
            ("filter_condition_id", filterConditionId),
            ("optional", optional),
        ], overrides));

    private static CanonicalRecord Effect(
        string effectId,
        string abilityId,
        int sequence,
        string action,
        string targetId,
        params (string Key, object? Value)[] overrides) => Record(Merge(
        [
            ("effect_id", effectId),
            ("ability_id", abilityId),
            ("parent_effect_id", null),
            ("sequence", sequence),
            ("branch_key", null),
            ("effect_action_type_id", action),
            ("source_reference_type_id", "ref_ability_source_card"),
            ("target_id", targetId),
        ], overrides));

    private static CanonicalRecord Parameter(
        string parameterId,
        string effectId,
        string contractFieldId,
        params (string Key, object? Value)[] values) => Record(Merge(
        [
            ("effect_parameter_id", parameterId),
            ("effect_id", effectId),
            ("contract_field_id", contractFieldId),
            ("item_index", 1),
        ], values));

    private static CanonicalRecord Trigger(string triggerId, string abilityId) => Record(
        ("trigger_id", triggerId),
        ("ability_id", abilityId),
        ("sequence", 1),
        ("event_type_id", "event_card_entered_play"),
        ("event_stage_id", "after"),
        ("subject_reference_type_id", "ref_ability_source_card"),
        ("to_zone_id", "dominion"));

    private static CanonicalRecord Expression(string expressionId, int sequence, params (string Key, object? Value)[] values) => Record(Merge(
        [
            ("expression_id", expressionId),
            ("ability_id", "ability_aqu_mor_007_01"),
            ("parent_expression_id", null),
            ("sequence", sequence),
            ("expression_kind_id", "literal"),
        ], values));

    private static CanonicalRecord Duration(
        string durationId,
        string effectId,
        string policyId,
        params (string Key, object? Value)[] values) => Record(Merge(
        [
            ("duration_id", durationId),
            ("effect_id", effectId),
            ("duration_policy_id", policyId),
        ], values));

    private static IEnumerable<CanonicalRecord> TemplateNodes()
    {
        yield return TemplateNode("target", CanonicalAbilityTableIds.Targets, 1, 1);
        yield return TemplateNode("effect", CanonicalAbilityTableIds.Effects, 2, 1);
        yield return TemplateNode("damage_kind", CanonicalAbilityTableIds.EffectParameters, 3, 1);
        yield return TemplateNode("damage_amount", CanonicalAbilityTableIds.EffectParameters, 4, 2);
    }

    private static CanonicalRecord TemplateNode(
        string nodeKey,
        string outputTableId,
        int nodeOrder,
        int outputSequence) => Record(
        ("template_node_id", $"template_node_fixture_{nodeKey}"),
        ("ability_template_id", "template_resolution_damage_all_enemy_horizont_entities_v1"),
        ("node_key", nodeKey),
        ("output_table_id", outputTableId),
        ("node_order", nodeOrder),
        ("output_sequence", outputSequence));

    private static IEnumerable<CanonicalRecord> TemplateBindings()
    {
        var bindings = new List<CanonicalRecord>();
        var sequence = 0;
        void Fixed(string node, string field, object value)
        {
            sequence += 1;
            bindings.Add(TemplateBinding(sequence, node, field, "fixed_value", value));
        }

        void Generated(string node, string field, string sourceNode)
        {
            sequence += 1;
            bindings.Add(TemplateBinding(sequence, node, field, "generated_node_id", sourceNode));
        }

        Fixed("target", "target_role_id", "primary");
        Fixed("target", "target_primitive_id", "target_all_matching_cards");
        Fixed("target", "reference_type_id", "ref_all_matching_cards_zero_or_more");
        Fixed("target", "game_object_id", "card_instance");
        Fixed("target", "card_type_id", "entity");
        Fixed("target", "player_reference_id", "opponent_of_ability_controller");
        Fixed("target", "zone_id", "dominion");
        Fixed("target", "domain_row_id", "horizont");
        Fixed("target", "selection_method_id", "all_matching");
        Fixed("target", "minimum_targets", 0);
        Fixed("target", "maximum_targets", 6);
        Fixed("target", "optional", false);
        Fixed("effect", "effect_action_type_id", "effect_deal_damage");
        Fixed("effect", "source_reference_type_id", "ref_ability_source_card");
        Generated("effect", "target_id", "target");
        Fixed("effect", "value_type_id", "no_value");
        Generated("damage_kind", "effect_id", "effect");
        Fixed("damage_kind", "contract_field_id", "parameter_field_deal_damage_damage_kind");
        Fixed("damage_kind", "item_index", 1);
        Fixed("damage_kind", "value_registry_value_id", "damage_kind_direct");
        Generated("damage_amount", "effect_id", "effect");
        Fixed("damage_amount", "contract_field_id", "parameter_field_deal_damage_amount");
        Fixed("damage_amount", "item_index", 1);
        sequence += 1;
        bindings.Add(Record(
            ("template_binding_id", $"template_binding_fixture_{sequence:000}"),
            ("template_node_id", "template_node_fixture_damage_amount"),
            ("target_field_id", "fixture_schema_ability_effect_parameters_value_integer"),
            ("binding_kind_id", "template_parameter"),
            ("parameter_contract_field_id", "parameter_field_template_damage_all_enemy_horizont_amount"),
            ("source_node_key", null),
            ("fixed_boolean", null),
            ("fixed_integer", null),
            ("fixed_text", null),
            ("fixed_registry_value_id", null),
            ("fixed_reference_id", null)));
        return bindings;
    }

    private static CanonicalRecord TemplateBinding(
        int sequence,
        string nodeKey,
        string fieldName,
        string kind,
        object value)
    {
        var boolean = value is bool booleanValue ? booleanValue : (bool?)null;
        var integer = value is int integerValue ? integerValue : (int?)null;
        var reference = value is string stringValue ? stringValue : null;
        return Record(
            ("template_binding_id", $"template_binding_fixture_{sequence:000}"),
            ("template_node_id", $"template_node_fixture_{nodeKey}"),
            ("target_field_id", nodeKey == "effect" && fieldName == "effect_action_type_id"
                ? "cdb_fld_ability_effects_effect_action_type_id"
                : $"fixture_schema_{OutputTable(nodeKey)}_{fieldName}"),
            ("binding_kind_id", kind),
            ("parameter_contract_field_id", null),
            ("source_node_key", kind == "generated_node_id" ? reference : null),
            ("fixed_boolean", kind == "fixed_value" ? boolean : null),
            ("fixed_integer", kind == "fixed_value" ? integer : null),
            ("fixed_text", null),
            ("fixed_registry_value_id", null),
            ("fixed_reference_id", kind == "fixed_value" ? reference : null));
    }

    private static IEnumerable<CanonicalRecord> TemplateSchemaFields()
    {
        var fields = new Dictionary<string, string[]>(StringComparer.Ordinal)
        {
            [CanonicalAbilityTableIds.Targets] =
            [
                "ability_id", "sequence", "target_role_id", "target_primitive_id", "reference_type_id",
                "game_object_id", "card_type_id", "player_reference_id", "zone_id", "domain_row_id",
                "selection_method_id", "minimum_targets", "maximum_targets", "optional", "status",
                "source_id", "source_ref", "notes",
            ],
            [CanonicalAbilityTableIds.Effects] =
            [
                "ability_id", "sequence", "source_reference_type_id", "target_id",
                "value_type_id", "status", "engine_support_status", "source_id", "source_ref", "notes",
            ],
            [CanonicalAbilityTableIds.EffectParameters] =
            [
                "effect_id", "contract_field_id", "item_index", "value_registry_value_id", "value_integer",
                "status", "source_id", "source_ref", "notes",
            ],
        };
        foreach (var (tableId, fieldNames) in fields)
        {
            foreach (var fieldName in fieldNames)
            {
                var dataType = fieldName is "sequence" or "minimum_targets" or "maximum_targets" or "item_index" or "value_integer"
                    ? "integer"
                    : fieldName == "optional" ? "boolean" : "string";
                yield return Record(
                    ("field_id", $"fixture_schema_{tableId}_{fieldName}"),
                    ("table_id", tableId),
                    ("field_name", fieldName),
                    ("data_type", dataType),
                    ("allowed_group_id", null),
                    ("reference_table_id", null));
            }
        }
    }

    private static string OutputTable(string nodeKey) => nodeKey switch
    {
        "target" => CanonicalAbilityTableIds.Targets,
        "effect" => CanonicalAbilityTableIds.Effects,
        "damage_kind" or "damage_amount" => CanonicalAbilityTableIds.EffectParameters,
        _ => throw new ArgumentOutOfRangeException(nameof(nodeKey)),
    };

    private static CanonicalTable VocabularyTable(string tableId, string primaryKey, params string[] ids) =>
        Table(tableId, primaryKey, ids.Select(id => Record((primaryKey, id))).ToArray());

    private static CanonicalTable Table(string tableId, string primaryKey, params CanonicalRecord[] records)
    {
        var values = records.ToImmutableArray();
        return new CanonicalTable(
            tableId,
            primaryKey,
            values,
            values.ToImmutableDictionary(record => record.GetRequiredString(primaryKey), record => record, StringComparer.Ordinal));
    }

    internal static CanonicalRecord Record(params (string Key, object? Value)[] fields)
    {
        var values = new Dictionary<string, object?>(StringComparer.Ordinal)
        {
            ["status"] = "active",
            ["engine_support_status"] = "planned",
            ["source_id"] = "fixture_source",
            ["source_ref"] = null,
            ["notes"] = null,
        };
        foreach (var (key, value) in fields)
        {
            values[key] = value;
        }

        return new CanonicalRecord(values.ToImmutableDictionary(
            pair => pair.Key,
            pair => JsonSerializer.SerializeToElement(pair.Value, pair.Value?.GetType() ?? typeof(object)),
            StringComparer.Ordinal));
    }

    private static (string Key, object? Value)[] Merge(
        IEnumerable<(string Key, object? Value)> defaults,
        IEnumerable<(string Key, object? Value)> overrides)
    {
        var values = defaults.ToDictionary(pair => pair.Key, pair => pair.Value, StringComparer.Ordinal);
        foreach (var (key, value) in overrides)
        {
            values[key] = value;
        }

        return values.Select(pair => (pair.Key, pair.Value)).ToArray();
    }

    internal static CanonicalCardDatabasePackage SetField(
        CanonicalCardDatabasePackage package,
        string tableId,
        string recordId,
        string fieldName,
        object? value)
    {
        var table = package.Tables[tableId];
        var index = -1;
        for (var candidate = 0; candidate < table.Records.Length; candidate += 1)
        {
            if (string.Equals(table.Records[candidate].GetRequiredString(table.PrimaryKey), recordId, StringComparison.Ordinal))
            {
                index = candidate;
                break;
            }
        }

        if (index < 0)
        {
            throw new InvalidOperationException("Fixture record was not found.");
        }

        var changed = table.Records[index] with
        {
            Fields = table.Records[index].Fields.SetItem(
                fieldName,
                JsonSerializer.SerializeToElement(value, value?.GetType() ?? typeof(object))),
        };
        var changedTable = table with
        {
            Records = table.Records.SetItem(index, changed),
            RecordsById = table.RecordsById.SetItem(recordId, changed),
        };
        return package with { Tables = package.Tables.SetItem(tableId, changedTable) };
    }

    internal static CanonicalCardDatabasePackage AddRecord(
        CanonicalCardDatabasePackage package,
        string tableId,
        CanonicalRecord record)
    {
        var table = package.Tables[tableId];
        var recordId = record.GetRequiredString(table.PrimaryKey);
        var changed = table with
        {
            Records = table.Records.Add(record),
            RecordsById = table.RecordsById.Add(recordId, record),
        };
        return package with { Tables = package.Tables.SetItem(tableId, changed) };
    }

    internal static CanonicalCardDatabasePackage RemoveRecord(
        CanonicalCardDatabasePackage package,
        string tableId,
        string recordId)
    {
        var table = package.Tables[tableId];
        var changed = table with
        {
            Records = table.Records.Where(record => !string.Equals(
                    record.GetRequiredString(table.PrimaryKey),
                    recordId,
                    StringComparison.Ordinal))
                .ToImmutableArray(),
            RecordsById = table.RecordsById.Remove(recordId),
        };
        return package with { Tables = package.Tables.SetItem(tableId, changed) };
    }

    private static CanonicalCardDatabasePackage DuplicateFirstRecord(CanonicalCardDatabasePackage package, string tableId)
    {
        var table = package.Tables[tableId];
        return package with
        {
            Tables = package.Tables.SetItem(tableId, table with { Records = table.Records.Add(table.Records[0]) }),
        };
    }

    private static void ThrowsCode(string expectedCode, Action action)
    {
        try
        {
            action();
        }
        catch (EngineInputException exception)
        {
            Equal(expectedCode, exception.Code, "Materializer returned an unexpected diagnostic code.");
            return;
        }

        throw new InvalidOperationException($"Expected EngineInputException with code {expectedCode}.");
    }

    private static T Single<T>(IEnumerable<T> values)
    {
        var materialized = values.ToArray();
        Equal(1, materialized.Length, "Expected exactly one fixture record.");
        return materialized[0];
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
            throw new InvalidOperationException($"{message} Expected: {expected}; actual: {actual}.");
        }
    }
}
