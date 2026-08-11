using System.Collections.Immutable;
using System.Text.Json;

namespace Aeterna.Engine.Runtime;

public static class CanonicalAbilityTableIds
{
    public const string Cards = "cards";
    public const string CardKeywords = "card_keywords";
    public const string Abilities = "abilities";
    public const string Targets = "ability_targets";
    public const string Effects = "ability_effects";
    public const string EffectParameters = "ability_effect_parameters";
    public const string Triggers = "ability_triggers";
    public const string Conditions = "ability_conditions";
    public const string Expressions = "ability_expressions";
    public const string Durations = "ability_durations";
    public const string TemplateArguments = "ability_template_arguments";
    public const string AbilityTemplates = "ability_templates";
    public const string AbilityTemplateNodes = "ability_template_nodes";
    public const string AbilityTemplateBindings = "ability_template_bindings";
    public const string ContractFields = "contract_fields";
    public const string SchemaFields = "schema_fields";
    public const string ValueRegistry = "value_registry";
}

public sealed record CanonicalAbilityTemplateDefinition(
    string TemplateId,
    string TemplateVersion,
    string ParameterSchemaId,
    string AbilityKindId,
    string ResolutionRequirementId,
    string DefaultActiveZoneId,
    string ExpansionPolicyId,
    string MinimumCardDatabaseSchemaVersion,
    string Status,
    string EngineSupportStatus,
    string SourceId,
    string? SourceRef,
    string? Notes,
    ImmutableDictionary<string, JsonElement> RawFields);

public sealed record CanonicalAbilityTemplateArgumentDefinition(
    string ArgumentId,
    string AbilityId,
    string ContractFieldId,
    int ItemIndex,
    bool? ValueBoolean,
    int? ValueInteger,
    string? ValueText,
    string? ValueRegistryValueId,
    string? ValueReferenceId,
    string? ValueExpressionId,
    string Status,
    string SourceId,
    string? SourceRef,
    string? Notes,
    ImmutableDictionary<string, JsonElement> RawFields);

public sealed record CanonicalCardKeywordDefinition(
    string CardKeywordId,
    string CardId,
    string KeywordId,
    int? NumericValue,
    string? TextValue,
    int Sequence,
    string Status,
    string SourceId,
    string? SourceRef,
    string? Notes,
    ImmutableDictionary<string, JsonElement> RawFields);

public sealed record CanonicalAbilityTargetDefinition(
    string TargetId,
    string AbilityId,
    int Sequence,
    string TargetRoleId,
    string TargetPrimitiveId,
    string? ReferenceTypeId,
    string? GameObjectId,
    string? CardTypeId,
    string? PlayerReferenceId,
    string? ZoneId,
    string? DomainRowId,
    string? DomainLaneId,
    string? ActivityStateId,
    string SelectionMethodId,
    int MinimumTargets,
    int MaximumTargets,
    string? FilterConditionId,
    bool Optional,
    string Status,
    string SourceId,
    string? SourceRef,
    string? Notes,
    ImmutableDictionary<string, JsonElement> RawFields);

public sealed record CanonicalAbilityEffectParameterDefinition(
    string EffectParameterId,
    string EffectId,
    string ContractFieldId,
    int ItemIndex,
    bool? ValueBoolean,
    int? ValueInteger,
    string? ValueText,
    string? ValueRegistryValueId,
    string? ValueReferenceId,
    string? ValueExpressionId,
    string Status,
    string SourceId,
    string? SourceRef,
    string? Notes,
    ImmutableDictionary<string, JsonElement> RawFields);

public sealed record CanonicalAbilityDurationDefinition(
    string DurationId,
    string EffectId,
    string DurationPolicyId,
    string? StartEventTypeId,
    string? BoundaryPlayerReferenceId,
    string? BoundaryPhaseId,
    string? ExpirationEventTypeId,
    string? DependencyReferenceTypeId,
    string? ConditionId,
    int? MaximumApplications,
    string Status,
    string SourceId,
    string? SourceRef,
    string? Notes,
    ImmutableDictionary<string, JsonElement> RawFields);

public sealed record CanonicalAbilityEffectDefinition(
    string EffectId,
    string AbilityId,
    string? ParentEffectId,
    int Sequence,
    string? BranchKey,
    string EffectActionTypeId,
    string? SourceReferenceTypeId,
    string? TargetId,
    string? ValueTypeId,
    int? ValueNumber,
    string? ValueText,
    string? ValueRegistryValueId,
    string? ValueExpressionId,
    string? FieldId,
    string? FromZoneId,
    string? ToZoneId,
    string? DestinationPositionId,
    string? ModifierTypeId,
    string? RestrictionTypeId,
    string? ConditionId,
    string Status,
    string EngineSupportStatus,
    string SourceId,
    string? SourceRef,
    string? Notes,
    ImmutableArray<CanonicalAbilityEffectParameterDefinition> Parameters,
    ImmutableArray<CanonicalAbilityDurationDefinition> Durations,
    ImmutableDictionary<string, JsonElement> RawFields);

public sealed record CanonicalAbilityTriggerDefinition(
    string TriggerId,
    string AbilityId,
    int Sequence,
    string EventTypeId,
    string? EventStageId,
    string? SubjectReferenceTypeId,
    string? PlayerReferenceId,
    string? PhaseId,
    string? FromZoneId,
    string? ToZoneId,
    string? FilterConditionId,
    string? TimingWindowId,
    string Status,
    string SourceId,
    string? SourceRef,
    string? Notes,
    ImmutableDictionary<string, JsonElement> RawFields);

public sealed record CanonicalAbilityConditionDefinition(
    string ConditionId,
    string AbilityId,
    string? ParentConditionId,
    int Sequence,
    string ConditionKindId,
    string? LogicalOperatorId,
    bool Negated,
    string? LeftExpressionId,
    string? ComparisonOperatorId,
    string? RightExpressionId,
    string Status,
    string SourceId,
    string? SourceRef,
    string? Notes,
    ImmutableDictionary<string, JsonElement> RawFields);

public sealed record CanonicalAbilityExpressionDefinition(
    string ExpressionId,
    string AbilityId,
    string? ParentExpressionId,
    int Sequence,
    string ExpressionKindId,
    string? OperatorId,
    string? ReferenceTypeId,
    string? FieldId,
    string? AggregateTypeId,
    string? LiteralDataTypeId,
    int? LiteralNumber,
    string? LiteralText,
    string? LiteralRegistryValueId,
    string? TargetId,
    string Status,
    string SourceId,
    string? SourceRef,
    string? Notes,
    ImmutableDictionary<string, JsonElement> RawFields);

public sealed record CanonicalAbilityDefinition(
    string AbilityId,
    string CardId,
    int AbilityIndex,
    string? AbilityKindId,
    string? ResolutionRequirementId,
    string? ActiveZoneId,
    string ImplementationModeId,
    string? AbilityTemplateId,
    CanonicalAbilityTemplateDefinition? Template,
    CanonicalAbilityTemplateProvenance? TemplateProvenance,
    string? ModuleKey,
    string? ParentAbilityId,
    string Status,
    string EngineSupportStatus,
    string SourceId,
    string? SourceRef,
    string? Notes,
    ImmutableArray<CanonicalAbilityTargetDefinition> Targets,
    ImmutableArray<CanonicalAbilityEffectDefinition> Effects,
    ImmutableArray<CanonicalAbilityTriggerDefinition> Triggers,
    ImmutableArray<CanonicalAbilityConditionDefinition> Conditions,
    ImmutableArray<CanonicalAbilityExpressionDefinition> Expressions,
    ImmutableArray<CanonicalAbilityTemplateArgumentDefinition> TemplateArguments,
    ImmutableDictionary<string, JsonElement> RawFields)
{
    public bool IsStructuredGraphAuthority => string.Equals(ImplementationModeId, "structured_data", StringComparison.Ordinal);

    public bool IsTemplateInstanceAuthority => TemplateProvenance is not null
                                               || string.Equals(ImplementationModeId, "template_instance", StringComparison.Ordinal);
}

public sealed class CanonicalAbilityCatalog
{
    internal CanonicalAbilityCatalog(
        ImmutableDictionary<string, CanonicalAbilityDefinition> abilitiesById,
        ImmutableDictionary<string, ImmutableArray<CanonicalAbilityDefinition>> abilitiesByCardId,
        ImmutableDictionary<string, CanonicalAbilityTargetDefinition> targetsById,
        ImmutableDictionary<string, ImmutableArray<CanonicalAbilityTargetDefinition>> targetsByAbilityId,
        ImmutableDictionary<string, CanonicalAbilityEffectDefinition> effectsById,
        ImmutableDictionary<string, ImmutableArray<CanonicalAbilityEffectDefinition>> effectsByAbilityId,
        ImmutableDictionary<string, CanonicalAbilityEffectParameterDefinition> effectParametersById,
        ImmutableDictionary<string, ImmutableArray<CanonicalAbilityEffectParameterDefinition>> effectParametersByEffectId,
        ImmutableDictionary<string, CanonicalAbilityTriggerDefinition> triggersById,
        ImmutableDictionary<string, ImmutableArray<CanonicalAbilityTriggerDefinition>> triggersByAbilityId,
        ImmutableDictionary<string, CanonicalAbilityConditionDefinition> conditionsById,
        ImmutableDictionary<string, ImmutableArray<CanonicalAbilityConditionDefinition>> conditionsByAbilityId,
        ImmutableDictionary<string, CanonicalAbilityExpressionDefinition> expressionsById,
        ImmutableDictionary<string, ImmutableArray<CanonicalAbilityExpressionDefinition>> expressionsByAbilityId,
        ImmutableDictionary<string, CanonicalAbilityDurationDefinition> durationsById,
        ImmutableDictionary<string, ImmutableArray<CanonicalAbilityDurationDefinition>> durationsByEffectId,
        ImmutableDictionary<string, CanonicalCardKeywordDefinition> keywordsById,
        ImmutableDictionary<string, ImmutableArray<CanonicalCardKeywordDefinition>> keywordsByCardId,
        ImmutableDictionary<string, CanonicalAbilityTemplateDefinition> templatesById,
        ImmutableDictionary<string, CanonicalAbilityTemplateArgumentDefinition> templateArgumentsById,
        ImmutableDictionary<string, ImmutableArray<CanonicalAbilityTemplateArgumentDefinition>> templateArgumentsByAbilityId)
    {
        AbilitiesById = abilitiesById;
        AbilitiesByCardId = abilitiesByCardId;
        TargetsById = targetsById;
        TargetsByAbilityId = targetsByAbilityId;
        EffectsById = effectsById;
        EffectsByAbilityId = effectsByAbilityId;
        EffectParametersById = effectParametersById;
        EffectParametersByEffectId = effectParametersByEffectId;
        TriggersById = triggersById;
        TriggersByAbilityId = triggersByAbilityId;
        ConditionsById = conditionsById;
        ConditionsByAbilityId = conditionsByAbilityId;
        ExpressionsById = expressionsById;
        ExpressionsByAbilityId = expressionsByAbilityId;
        DurationsById = durationsById;
        DurationsByEffectId = durationsByEffectId;
        KeywordsById = keywordsById;
        KeywordsByCardId = keywordsByCardId;
        TemplatesById = templatesById;
        TemplateArgumentsById = templateArgumentsById;
        TemplateArgumentsByAbilityId = templateArgumentsByAbilityId;
    }

    public ImmutableDictionary<string, CanonicalAbilityDefinition> AbilitiesById { get; }

    public ImmutableDictionary<string, ImmutableArray<CanonicalAbilityDefinition>> AbilitiesByCardId { get; }

    public ImmutableDictionary<string, CanonicalAbilityTargetDefinition> TargetsById { get; }

    public ImmutableDictionary<string, ImmutableArray<CanonicalAbilityTargetDefinition>> TargetsByAbilityId { get; }

    public ImmutableDictionary<string, CanonicalAbilityEffectDefinition> EffectsById { get; }

    public ImmutableDictionary<string, ImmutableArray<CanonicalAbilityEffectDefinition>> EffectsByAbilityId { get; }

    public ImmutableDictionary<string, CanonicalAbilityEffectParameterDefinition> EffectParametersById { get; }

    public ImmutableDictionary<string, ImmutableArray<CanonicalAbilityEffectParameterDefinition>> EffectParametersByEffectId { get; }

    public ImmutableDictionary<string, CanonicalAbilityTriggerDefinition> TriggersById { get; }

    public ImmutableDictionary<string, ImmutableArray<CanonicalAbilityTriggerDefinition>> TriggersByAbilityId { get; }

    public ImmutableDictionary<string, CanonicalAbilityConditionDefinition> ConditionsById { get; }

    public ImmutableDictionary<string, ImmutableArray<CanonicalAbilityConditionDefinition>> ConditionsByAbilityId { get; }

    public ImmutableDictionary<string, CanonicalAbilityExpressionDefinition> ExpressionsById { get; }

    public ImmutableDictionary<string, ImmutableArray<CanonicalAbilityExpressionDefinition>> ExpressionsByAbilityId { get; }

    public ImmutableDictionary<string, CanonicalAbilityDurationDefinition> DurationsById { get; }

    public ImmutableDictionary<string, ImmutableArray<CanonicalAbilityDurationDefinition>> DurationsByEffectId { get; }

    public ImmutableDictionary<string, CanonicalCardKeywordDefinition> KeywordsById { get; }

    public ImmutableDictionary<string, ImmutableArray<CanonicalCardKeywordDefinition>> KeywordsByCardId { get; }

    public ImmutableDictionary<string, CanonicalAbilityTemplateDefinition> TemplatesById { get; }

    public ImmutableDictionary<string, CanonicalAbilityTemplateArgumentDefinition> TemplateArgumentsById { get; }

    public ImmutableDictionary<string, ImmutableArray<CanonicalAbilityTemplateArgumentDefinition>> TemplateArgumentsByAbilityId { get; }
}

public static class CanonicalAbilityMaterializer
{
    private const string FieldInvalidCode = "CANONICAL_ABILITY_FIELD_INVALID";
    private const string ReferenceMissingCode = "CANONICAL_ABILITY_REFERENCE_MISSING";
    private const string ScopeMismatchCode = "CANONICAL_ABILITY_REFERENCE_SCOPE_MISMATCH";

    public static CanonicalAbilityCatalog Materialize(CanonicalCardDatabasePackage cardDatabase)
    {
        ArgumentNullException.ThrowIfNull(cardDatabase);

        var registry = cardDatabase.Registry;
        var cards = RequireTable(cardDatabase.Tables, CanonicalAbilityTableIds.Cards);
        var keywordTable = RequireTable(cardDatabase.Tables, CanonicalAbilityTableIds.CardKeywords);
        var abilityTable = RequireTable(cardDatabase.Tables, CanonicalAbilityTableIds.Abilities);
        var targetTable = RequireTable(cardDatabase.Tables, CanonicalAbilityTableIds.Targets);
        var effectTable = RequireTable(cardDatabase.Tables, CanonicalAbilityTableIds.Effects);
        var parameterTable = RequireTable(cardDatabase.Tables, CanonicalAbilityTableIds.EffectParameters);
        var triggerTable = RequireTable(cardDatabase.Tables, CanonicalAbilityTableIds.Triggers);
        var conditionTable = RequireTable(cardDatabase.Tables, CanonicalAbilityTableIds.Conditions);
        var expressionTable = RequireTable(cardDatabase.Tables, CanonicalAbilityTableIds.Expressions);
        var durationTable = RequireTable(cardDatabase.Tables, CanonicalAbilityTableIds.Durations);
        var argumentTable = RequireTable(cardDatabase.Tables, CanonicalAbilityTableIds.TemplateArguments);
        var templateTable = RequireTable(registry.Tables, CanonicalAbilityTableIds.AbilityTemplates);

        var vocabulary = CanonicalVocabularyValidator.Create(cardDatabase, registry);
        vocabulary.ValidateRegistryTable(CanonicalAbilityTableIds.AbilityTemplates, templateTable.Records);
        vocabulary.ValidateCardDatabaseTable(CanonicalAbilityTableIds.CardKeywords, keywordTable.Records);
        vocabulary.ValidateCardDatabaseTable(CanonicalAbilityTableIds.Abilities, abilityTable.Records);
        vocabulary.ValidateCardDatabaseTable(CanonicalAbilityTableIds.Targets, targetTable.Records);
        vocabulary.ValidateCardDatabaseTable(CanonicalAbilityTableIds.Effects, effectTable.Records);
        vocabulary.ValidateCardDatabaseTable(CanonicalAbilityTableIds.EffectParameters, parameterTable.Records);
        vocabulary.ValidateCardDatabaseTable(CanonicalAbilityTableIds.Triggers, triggerTable.Records);
        vocabulary.ValidateCardDatabaseTable(CanonicalAbilityTableIds.Conditions, conditionTable.Records);
        vocabulary.ValidateCardDatabaseTable(CanonicalAbilityTableIds.Expressions, expressionTable.Records);
        vocabulary.ValidateCardDatabaseTable(CanonicalAbilityTableIds.Durations, durationTable.Records);
        vocabulary.ValidateCardDatabaseTable(CanonicalAbilityTableIds.TemplateArguments, argumentTable.Records);

        var templates = BuildUnique(
            templateTable.Records.Select(ParseTemplate),
            template => template.TemplateId,
            CanonicalAbilityTableIds.AbilityTemplates);
        var declaredAbilityIds = BuildRecordIdSet(
            abilityTable.Records,
            "ability_id",
            CanonicalAbilityTableIds.Abilities);
        var keywords = BuildUnique(
            keywordTable.Records.Select(ParseKeyword),
            keyword => keyword.CardKeywordId,
            CanonicalAbilityTableIds.CardKeywords);
        var arguments = BuildUnique(
            argumentTable.Records.Select(ParseTemplateArgument),
            argument => argument.ArgumentId,
            CanonicalAbilityTableIds.TemplateArguments);
        var expansion = CanonicalAbilityTemplateCompiler.Expand(
            cardDatabase,
            templates,
            arguments,
            abilityTable.Records);
        var targetRecords = targetTable.Records.AddRange(expansion.GetRecords(CanonicalAbilityTableIds.Targets));
        var parameterRecords = parameterTable.Records.AddRange(expansion.GetRecords(CanonicalAbilityTableIds.EffectParameters));
        var triggerRecords = triggerTable.Records.AddRange(expansion.GetRecords(CanonicalAbilityTableIds.Triggers));
        var conditionRecords = conditionTable.Records.AddRange(expansion.GetRecords(CanonicalAbilityTableIds.Conditions));
        var expressionRecords = expressionTable.Records.AddRange(expansion.GetRecords(CanonicalAbilityTableIds.Expressions));
        var durationRecords = durationTable.Records.AddRange(expansion.GetRecords(CanonicalAbilityTableIds.Durations));
        var effectRecords = effectTable.Records.AddRange(expansion.GetRecords(CanonicalAbilityTableIds.Effects));
        vocabulary.ValidateCardDatabaseTable(CanonicalAbilityTableIds.Targets, targetRecords);
        vocabulary.ValidateCardDatabaseTable(CanonicalAbilityTableIds.Effects, effectRecords);
        vocabulary.ValidateCardDatabaseTable(CanonicalAbilityTableIds.EffectParameters, parameterRecords);
        vocabulary.ValidateCardDatabaseTable(CanonicalAbilityTableIds.Triggers, triggerRecords);
        vocabulary.ValidateCardDatabaseTable(CanonicalAbilityTableIds.Conditions, conditionRecords);
        vocabulary.ValidateCardDatabaseTable(CanonicalAbilityTableIds.Expressions, expressionRecords);
        vocabulary.ValidateCardDatabaseTable(CanonicalAbilityTableIds.Durations, durationRecords);

        var targets = BuildUnique(
            targetRecords.Select(ParseTarget),
            target => target.TargetId,
            CanonicalAbilityTableIds.Targets);
        var parameters = BuildUnique(
            parameterRecords.Select(ParseEffectParameter),
            parameter => parameter.EffectParameterId,
            CanonicalAbilityTableIds.EffectParameters);
        var triggers = BuildUnique(
            triggerRecords.Select(ParseTrigger),
            trigger => trigger.TriggerId,
            CanonicalAbilityTableIds.Triggers);
        var conditions = BuildUnique(
            conditionRecords.Select(ParseCondition),
            condition => condition.ConditionId,
            CanonicalAbilityTableIds.Conditions);
        var expressions = BuildUnique(
            expressionRecords.Select(ParseExpression),
            expression => expression.ExpressionId,
            CanonicalAbilityTableIds.Expressions);
        var durations = BuildUnique(
            durationRecords.Select(ParseDuration),
            duration => duration.DurationId,
            CanonicalAbilityTableIds.Durations);

        var parameterGroups = GroupOrdered(
            parameters.Values,
            parameter => parameter.EffectId,
            parameter => parameter.ContractFieldId,
            parameter => parameter.ItemIndex,
            parameter => parameter.EffectParameterId);
        var durationGroups = GroupSequenced(
            durations.Values,
            duration => duration.EffectId,
            duration => 0,
            duration => duration.DurationId);
        var effects = BuildUnique(
            effectRecords.Select(record => ParseEffect(record, parameterGroups, durationGroups)),
            effect => effect.EffectId,
            CanonicalAbilityTableIds.Effects);

        ValidateReferences(cards, declaredAbilityIds, keywords, targets, effects, parameters, triggers, conditions, expressions, durations, arguments);
        ValidateSequences(keywords.Values, targets.Values, effects.Values, parameters.Values, triggers.Values, conditions.Values, expressions.Values, durations.Values, arguments.Values);
        ValidateHierarchies(abilityTable.Records, effects, conditions, expressions);

        var targetGroups = GroupSequenced(targets.Values, target => target.AbilityId, target => target.Sequence, target => target.TargetId);
        var effectGroups = GroupSequenced(effects.Values, effect => effect.AbilityId, effect => effect.Sequence, effect => effect.EffectId);
        var triggerGroups = GroupSequenced(triggers.Values, trigger => trigger.AbilityId, trigger => trigger.Sequence, trigger => trigger.TriggerId);
        var conditionGroups = GroupSequenced(conditions.Values, condition => condition.AbilityId, condition => condition.Sequence, condition => condition.ConditionId);
        var expressionGroups = GroupSequenced(expressions.Values, expression => expression.AbilityId, expression => expression.Sequence, expression => expression.ExpressionId);
        var argumentGroups = GroupOrdered(arguments.Values, argument => argument.AbilityId, argument => argument.ContractFieldId, argument => argument.ItemIndex, argument => argument.ArgumentId);

        var abilities = BuildUnique(
            abilityTable.Records.Select(record => ParseAbility(
                record,
                templates,
                targetGroups,
                effectGroups,
                triggerGroups,
                conditionGroups,
                expressionGroups,
                argumentGroups,
                expansion.ProvenanceByAbilityId)),
            ability => ability.AbilityId,
            CanonicalAbilityTableIds.Abilities);
        ValidateAbilityReferences(cards, abilities, templates);
        ValidateAbilitySequences(abilities.Values);

        return new CanonicalAbilityCatalog(
            abilities,
            GroupSequenced(abilities.Values, ability => ability.CardId, ability => ability.AbilityIndex, ability => ability.AbilityId),
            targets,
            targetGroups,
            effects,
            effectGroups,
            parameters,
            parameterGroups,
            triggers,
            triggerGroups,
            conditions,
            conditionGroups,
            expressions,
            expressionGroups,
            durations,
            durationGroups,
            keywords,
            GroupSequenced(keywords.Values, keyword => keyword.CardId, keyword => keyword.Sequence, keyword => keyword.CardKeywordId),
            templates,
            arguments,
            argumentGroups);
    }

    private static CanonicalAbilityTemplateDefinition ParseTemplate(CanonicalRecord record) => new(
        ReadRequiredString(record, "ability_template_id"),
        ReadRequiredString(record, "template_version"),
        ReadRequiredString(record, "parameter_schema_id"),
        ReadRequiredString(record, "ability_kind_id"),
        ReadRequiredString(record, "resolution_requirement_id"),
        ReadRequiredString(record, "default_active_zone_id"),
        ReadRequiredString(record, "expansion_policy_id"),
        ReadRequiredString(record, "minimum_carddatabase_schema_version"),
        ReadRequiredString(record, "status"),
        ReadRequiredString(record, "engine_support_status"),
        ReadRequiredString(record, "source_id"),
        ReadOptionalString(record, "source_ref"),
        ReadOptionalText(record, "notes"),
        record.Fields);

    private static CanonicalCardKeywordDefinition ParseKeyword(CanonicalRecord record) => new(
        ReadRequiredString(record, "card_keyword_id"),
        ReadRequiredString(record, "card_id"),
        ReadRequiredString(record, "keyword_id"),
        ReadOptionalInteger(record, "numeric_value"),
        ReadOptionalText(record, "text_value"),
        ReadRequiredInteger(record, "sequence"),
        ReadRequiredString(record, "status"),
        ReadRequiredString(record, "source_id"),
        ReadOptionalString(record, "source_ref"),
        ReadOptionalText(record, "notes"),
        record.Fields);

    private static CanonicalAbilityTargetDefinition ParseTarget(CanonicalRecord record) => new(
        ReadRequiredString(record, "target_id"),
        ReadRequiredString(record, "ability_id"),
        ReadRequiredInteger(record, "sequence"),
        ReadRequiredString(record, "target_role_id"),
        ReadRequiredString(record, "target_primitive_id"),
        ReadOptionalString(record, "reference_type_id"),
        ReadOptionalString(record, "game_object_id"),
        ReadOptionalString(record, "card_type_id"),
        ReadOptionalString(record, "player_reference_id"),
        ReadOptionalString(record, "zone_id"),
        ReadOptionalString(record, "domain_row_id"),
        ReadOptionalString(record, "domain_lane_id"),
        ReadOptionalString(record, "activity_state_id"),
        ReadRequiredString(record, "selection_method_id"),
        ReadRequiredInteger(record, "minimum_targets"),
        ReadRequiredInteger(record, "maximum_targets"),
        ReadOptionalString(record, "filter_condition_id"),
        ReadRequiredBoolean(record, "optional"),
        ReadRequiredString(record, "status"),
        ReadRequiredString(record, "source_id"),
        ReadOptionalString(record, "source_ref"),
        ReadOptionalText(record, "notes"),
        record.Fields);

    private static CanonicalAbilityEffectParameterDefinition ParseEffectParameter(CanonicalRecord record) => new(
        ReadRequiredString(record, "effect_parameter_id"),
        ReadRequiredString(record, "effect_id"),
        ReadRequiredString(record, "contract_field_id"),
        ReadRequiredInteger(record, "item_index"),
        ReadOptionalBoolean(record, "value_boolean"),
        ReadOptionalInteger(record, "value_integer"),
        ReadOptionalText(record, "value_text"),
        ReadOptionalString(record, "value_registry_value_id"),
        ReadOptionalString(record, "value_reference_id"),
        ReadOptionalString(record, "value_expression_id"),
        ReadRequiredString(record, "status"),
        ReadRequiredString(record, "source_id"),
        ReadOptionalString(record, "source_ref"),
        ReadOptionalText(record, "notes"),
        record.Fields);

    private static CanonicalAbilityTriggerDefinition ParseTrigger(CanonicalRecord record) => new(
        ReadRequiredString(record, "trigger_id"),
        ReadRequiredString(record, "ability_id"),
        ReadRequiredInteger(record, "sequence"),
        ReadRequiredString(record, "event_type_id"),
        ReadOptionalString(record, "event_stage_id"),
        ReadOptionalString(record, "subject_reference_type_id"),
        ReadOptionalString(record, "player_reference_id"),
        ReadOptionalString(record, "phase_id"),
        ReadOptionalString(record, "from_zone_id"),
        ReadOptionalString(record, "to_zone_id"),
        ReadOptionalString(record, "filter_condition_id"),
        ReadOptionalString(record, "timing_window_id"),
        ReadRequiredString(record, "status"),
        ReadRequiredString(record, "source_id"),
        ReadOptionalString(record, "source_ref"),
        ReadOptionalText(record, "notes"),
        record.Fields);

    private static CanonicalAbilityConditionDefinition ParseCondition(CanonicalRecord record) => new(
        ReadRequiredString(record, "condition_id"),
        ReadRequiredString(record, "ability_id"),
        ReadOptionalString(record, "parent_condition_id"),
        ReadRequiredInteger(record, "sequence"),
        ReadRequiredString(record, "condition_kind_id"),
        ReadOptionalString(record, "logical_operator_id"),
        ReadRequiredBoolean(record, "negated"),
        ReadOptionalString(record, "left_expression_id"),
        ReadOptionalString(record, "comparison_operator_id"),
        ReadOptionalString(record, "right_expression_id"),
        ReadRequiredString(record, "status"),
        ReadRequiredString(record, "source_id"),
        ReadOptionalString(record, "source_ref"),
        ReadOptionalText(record, "notes"),
        record.Fields);

    private static CanonicalAbilityExpressionDefinition ParseExpression(CanonicalRecord record) => new(
        ReadRequiredString(record, "expression_id"),
        ReadRequiredString(record, "ability_id"),
        ReadOptionalString(record, "parent_expression_id"),
        ReadRequiredInteger(record, "sequence"),
        ReadRequiredString(record, "expression_kind_id"),
        ReadOptionalString(record, "operator_id"),
        ReadOptionalString(record, "reference_type_id"),
        ReadOptionalString(record, "field_id"),
        ReadOptionalString(record, "aggregate_type_id"),
        ReadOptionalString(record, "literal_data_type_id"),
        ReadOptionalInteger(record, "literal_number"),
        ReadOptionalText(record, "literal_text"),
        ReadOptionalString(record, "literal_registry_value_id"),
        ReadOptionalString(record, "target_id"),
        ReadRequiredString(record, "status"),
        ReadRequiredString(record, "source_id"),
        ReadOptionalString(record, "source_ref"),
        ReadOptionalText(record, "notes"),
        record.Fields);

    private static CanonicalAbilityDurationDefinition ParseDuration(CanonicalRecord record) => new(
        ReadRequiredString(record, "duration_id"),
        ReadRequiredString(record, "effect_id"),
        ReadRequiredString(record, "duration_policy_id"),
        ReadOptionalString(record, "start_event_type_id"),
        ReadOptionalString(record, "boundary_player_reference_id"),
        ReadOptionalString(record, "boundary_phase_id"),
        ReadOptionalString(record, "expiration_event_type_id"),
        ReadOptionalString(record, "dependency_reference_type_id"),
        ReadOptionalString(record, "condition_id"),
        ReadOptionalInteger(record, "maximum_applications"),
        ReadRequiredString(record, "status"),
        ReadRequiredString(record, "source_id"),
        ReadOptionalString(record, "source_ref"),
        ReadOptionalText(record, "notes"),
        record.Fields);

    private static CanonicalAbilityTemplateArgumentDefinition ParseTemplateArgument(CanonicalRecord record) => new(
        ReadRequiredString(record, "ability_argument_id"),
        ReadRequiredString(record, "ability_id"),
        ReadRequiredString(record, "contract_field_id"),
        ReadRequiredInteger(record, "item_index"),
        ReadOptionalBoolean(record, "value_boolean"),
        ReadOptionalInteger(record, "value_integer"),
        ReadOptionalText(record, "value_text"),
        ReadOptionalString(record, "value_registry_value_id"),
        ReadOptionalString(record, "value_reference_id"),
        ReadOptionalString(record, "value_expression_id"),
        ReadRequiredString(record, "status"),
        ReadRequiredString(record, "source_id"),
        ReadOptionalString(record, "source_ref"),
        ReadOptionalText(record, "notes"),
        record.Fields);

    private static CanonicalAbilityEffectDefinition ParseEffect(
        CanonicalRecord record,
        ImmutableDictionary<string, ImmutableArray<CanonicalAbilityEffectParameterDefinition>> parameterGroups,
        ImmutableDictionary<string, ImmutableArray<CanonicalAbilityDurationDefinition>> durationGroups)
    {
        var effectId = ReadRequiredString(record, "effect_id");
        return new CanonicalAbilityEffectDefinition(
            effectId,
            ReadRequiredString(record, "ability_id"),
            ReadOptionalString(record, "parent_effect_id"),
            ReadRequiredInteger(record, "sequence"),
            ReadOptionalString(record, "branch_key"),
            ReadRequiredString(record, "effect_action_type_id"),
            ReadOptionalString(record, "source_reference_type_id"),
            ReadOptionalString(record, "target_id"),
            ReadOptionalString(record, "value_type_id"),
            ReadOptionalInteger(record, "value_number"),
            ReadOptionalText(record, "value_text"),
            ReadOptionalString(record, "value_registry_value_id"),
            ReadOptionalString(record, "value_expression_id"),
            ReadOptionalString(record, "field_id"),
            ReadOptionalString(record, "from_zone_id"),
            ReadOptionalString(record, "to_zone_id"),
            ReadOptionalString(record, "destination_position_id"),
            ReadOptionalString(record, "modifier_type_id"),
            ReadOptionalString(record, "restriction_type_id"),
            ReadOptionalString(record, "condition_id"),
            ReadRequiredString(record, "status"),
            ReadRequiredString(record, "engine_support_status"),
            ReadRequiredString(record, "source_id"),
            ReadOptionalString(record, "source_ref"),
            ReadOptionalText(record, "notes"),
            GetGroup(parameterGroups, effectId),
            GetGroup(durationGroups, effectId),
            record.Fields);
    }

    private static CanonicalAbilityDefinition ParseAbility(
        CanonicalRecord record,
        ImmutableDictionary<string, CanonicalAbilityTemplateDefinition> templates,
        ImmutableDictionary<string, ImmutableArray<CanonicalAbilityTargetDefinition>> targets,
        ImmutableDictionary<string, ImmutableArray<CanonicalAbilityEffectDefinition>> effects,
        ImmutableDictionary<string, ImmutableArray<CanonicalAbilityTriggerDefinition>> triggers,
        ImmutableDictionary<string, ImmutableArray<CanonicalAbilityConditionDefinition>> conditions,
        ImmutableDictionary<string, ImmutableArray<CanonicalAbilityExpressionDefinition>> expressions,
        ImmutableDictionary<string, ImmutableArray<CanonicalAbilityTemplateArgumentDefinition>> arguments,
        ImmutableDictionary<string, CanonicalAbilityTemplateProvenance> provenanceByAbilityId)
    {
        var abilityId = ReadRequiredString(record, "ability_id");
        var templateId = ReadOptionalString(record, "ability_template_id");
        templates.TryGetValue(templateId ?? string.Empty, out var template);
        provenanceByAbilityId.TryGetValue(abilityId, out var provenance);
        return new CanonicalAbilityDefinition(
            abilityId,
            ReadRequiredString(record, "card_id"),
            ReadRequiredInteger(record, "ability_index"),
            provenance is null ? ReadOptionalString(record, "ability_kind_id") : template!.AbilityKindId,
            provenance is null ? ReadOptionalString(record, "resolution_requirement_id") : template!.ResolutionRequirementId,
            provenance is null ? ReadOptionalString(record, "active_zone_id") : template!.DefaultActiveZoneId,
            provenance is null ? ReadRequiredString(record, "implementation_mode_id") : "structured_data",
            templateId,
            template,
            provenance,
            ReadOptionalString(record, "module_key"),
            ReadOptionalString(record, "parent_ability_id"),
            ReadRequiredString(record, "status"),
            ReadRequiredString(record, "engine_support_status"),
            ReadRequiredString(record, "source_id"),
            ReadOptionalString(record, "source_ref"),
            ReadOptionalText(record, "notes"),
            GetGroup(targets, abilityId),
            GetGroup(effects, abilityId),
            GetGroup(triggers, abilityId),
            GetGroup(conditions, abilityId),
            GetGroup(expressions, abilityId),
            GetGroup(arguments, abilityId),
            record.Fields);
    }

    private static void ValidateReferences(
        CanonicalTable cards,
        ImmutableHashSet<string> declaredAbilityIds,
        ImmutableDictionary<string, CanonicalCardKeywordDefinition> keywords,
        ImmutableDictionary<string, CanonicalAbilityTargetDefinition> targets,
        ImmutableDictionary<string, CanonicalAbilityEffectDefinition> effects,
        ImmutableDictionary<string, CanonicalAbilityEffectParameterDefinition> parameters,
        ImmutableDictionary<string, CanonicalAbilityTriggerDefinition> triggers,
        ImmutableDictionary<string, CanonicalAbilityConditionDefinition> conditions,
        ImmutableDictionary<string, CanonicalAbilityExpressionDefinition> expressions,
        ImmutableDictionary<string, CanonicalAbilityDurationDefinition> durations,
        ImmutableDictionary<string, CanonicalAbilityTemplateArgumentDefinition> arguments)
    {
        foreach (var keyword in keywords.Values)
        {
            RequireReference(cards.RecordsById.ContainsKey(keyword.CardId), CanonicalAbilityTableIds.CardKeywords, keyword.CardKeywordId, "card_id");
        }

        var referencedAbilityIds = targets.Values.Select(target => target.AbilityId)
            .Concat(effects.Values.Select(effect => effect.AbilityId))
            .Concat(triggers.Values.Select(trigger => trigger.AbilityId))
            .Concat(conditions.Values.Select(condition => condition.AbilityId))
            .Concat(expressions.Values.Select(expression => expression.AbilityId))
            .Concat(arguments.Values.Select(argument => argument.AbilityId))
            .Distinct(StringComparer.Ordinal)
            .ToImmutableHashSet(StringComparer.Ordinal);
        foreach (var abilityId in referencedAbilityIds)
        {
            RequireReference(declaredAbilityIds.Contains(abilityId), CanonicalAbilityTableIds.Abilities, abilityId, "ability_id");
        }

        foreach (var parameter in parameters.Values)
        {
            RequireReference(effects.ContainsKey(parameter.EffectId), CanonicalAbilityTableIds.EffectParameters, parameter.EffectParameterId, "effect_id");
            if (parameter.ValueExpressionId is not null)
            {
                RequireReference(expressions.ContainsKey(parameter.ValueExpressionId), CanonicalAbilityTableIds.EffectParameters, parameter.EffectParameterId, "value_expression_id");
                RequireSameAbility(
                    effects[parameter.EffectId].AbilityId,
                    expressions[parameter.ValueExpressionId].AbilityId,
                    CanonicalAbilityTableIds.EffectParameters,
                    parameter.EffectParameterId,
                    "value_expression_id");
            }
        }

        foreach (var duration in durations.Values)
        {
            RequireReference(effects.ContainsKey(duration.EffectId), CanonicalAbilityTableIds.Durations, duration.DurationId, "effect_id");
            if (duration.ConditionId is not null)
            {
                RequireReference(conditions.ContainsKey(duration.ConditionId), CanonicalAbilityTableIds.Durations, duration.DurationId, "condition_id");
                RequireSameAbility(
                    effects[duration.EffectId].AbilityId,
                    conditions[duration.ConditionId].AbilityId,
                    CanonicalAbilityTableIds.Durations,
                    duration.DurationId,
                    "condition_id");
            }
        }

        foreach (var effect in effects.Values)
        {
            ValidateScopedReference(effect.TargetId, targets, target => target.AbilityId, effect.AbilityId, CanonicalAbilityTableIds.Effects, effect.EffectId, "target_id");
            ValidateScopedReference(effect.ConditionId, conditions, condition => condition.AbilityId, effect.AbilityId, CanonicalAbilityTableIds.Effects, effect.EffectId, "condition_id");
            ValidateScopedReference(effect.ValueExpressionId, expressions, expression => expression.AbilityId, effect.AbilityId, CanonicalAbilityTableIds.Effects, effect.EffectId, "value_expression_id");
            ValidateScopedReference(effect.ParentEffectId, effects, parent => parent.AbilityId, effect.AbilityId, CanonicalAbilityTableIds.Effects, effect.EffectId, "parent_effect_id");
        }

        foreach (var target in targets.Values)
        {
            ValidateScopedReference(target.FilterConditionId, conditions, condition => condition.AbilityId, target.AbilityId, CanonicalAbilityTableIds.Targets, target.TargetId, "filter_condition_id");
        }

        foreach (var trigger in triggers.Values)
        {
            ValidateScopedReference(trigger.FilterConditionId, conditions, condition => condition.AbilityId, trigger.AbilityId, CanonicalAbilityTableIds.Triggers, trigger.TriggerId, "filter_condition_id");
        }

        foreach (var condition in conditions.Values)
        {
            ValidateScopedReference(condition.ParentConditionId, conditions, parent => parent.AbilityId, condition.AbilityId, CanonicalAbilityTableIds.Conditions, condition.ConditionId, "parent_condition_id");
            ValidateScopedReference(condition.LeftExpressionId, expressions, expression => expression.AbilityId, condition.AbilityId, CanonicalAbilityTableIds.Conditions, condition.ConditionId, "left_expression_id");
            ValidateScopedReference(condition.RightExpressionId, expressions, expression => expression.AbilityId, condition.AbilityId, CanonicalAbilityTableIds.Conditions, condition.ConditionId, "right_expression_id");
        }

        foreach (var expression in expressions.Values)
        {
            ValidateScopedReference(expression.ParentExpressionId, expressions, parent => parent.AbilityId, expression.AbilityId, CanonicalAbilityTableIds.Expressions, expression.ExpressionId, "parent_expression_id");
            ValidateScopedReference(expression.TargetId, targets, target => target.AbilityId, expression.AbilityId, CanonicalAbilityTableIds.Expressions, expression.ExpressionId, "target_id");
        }

        foreach (var argument in arguments.Values)
        {
            if (argument.ValueExpressionId is not null)
            {
                RequireReference(expressions.ContainsKey(argument.ValueExpressionId), CanonicalAbilityTableIds.TemplateArguments, argument.ArgumentId, "value_expression_id");
                RequireSameAbility(argument.AbilityId, expressions[argument.ValueExpressionId].AbilityId, CanonicalAbilityTableIds.TemplateArguments, argument.ArgumentId, "value_expression_id");
            }
        }
    }

    private static void ValidateAbilityReferences(
        CanonicalTable cards,
        ImmutableDictionary<string, CanonicalAbilityDefinition> abilities,
        ImmutableDictionary<string, CanonicalAbilityTemplateDefinition> templates)
    {
        foreach (var ability in abilities.Values)
        {
            RequireReference(cards.RecordsById.ContainsKey(ability.CardId), CanonicalAbilityTableIds.Abilities, ability.AbilityId, "card_id");
            if (ability.ParentAbilityId is not null)
            {
                RequireReference(abilities.ContainsKey(ability.ParentAbilityId), CanonicalAbilityTableIds.Abilities, ability.AbilityId, "parent_ability_id");
                var parent = abilities[ability.ParentAbilityId];
                RequireSameAbility(ability.CardId, parent.CardId, CanonicalAbilityTableIds.Abilities, ability.AbilityId, "parent_ability_id");
            }

            foreach (var childAbilityId in ability.Targets.Select(target => target.AbilityId)
                         .Concat(ability.Effects.Select(effect => effect.AbilityId))
                         .Concat(ability.Triggers.Select(trigger => trigger.AbilityId))
                         .Concat(ability.Conditions.Select(condition => condition.AbilityId))
                         .Concat(ability.Expressions.Select(expression => expression.AbilityId))
                         .Concat(ability.TemplateArguments.Select(argument => argument.AbilityId)))
            {
                RequireReference(abilities.ContainsKey(childAbilityId), CanonicalAbilityTableIds.Abilities, childAbilityId, "ability_id");
            }

            if (ability.IsTemplateInstanceAuthority)
            {
                if (ability.AbilityTemplateId is null || !templates.ContainsKey(ability.AbilityTemplateId))
                {
                    throw new EngineInputException(
                        "CANONICAL_ABILITY_TEMPLATE_MISSING",
                        $"Template-instance ability references an unknown ability template: {ability.AbilityId}");
                }
            }
            else if (ability.AbilityTemplateId is not null && !templates.ContainsKey(ability.AbilityTemplateId))
            {
                throw new EngineInputException(
                    "CANONICAL_ABILITY_TEMPLATE_MISSING",
                    $"Canonical ability references an unknown ability template: {ability.AbilityId}");
            }

            if (!ability.IsTemplateInstanceAuthority && ability.TemplateArguments.Length != 0)
            {
                throw new EngineInputException(
                    "CANONICAL_ABILITY_IMPLEMENTATION_MODE_INVALID",
                    $"A non-template ability contains template arguments: {ability.AbilityId}");
            }
        }

        foreach (var ability in abilities.Values)
        {
            foreach (var child in ability.Targets)
            {
                RequireSameAbility(ability.AbilityId, child.AbilityId, CanonicalAbilityTableIds.Targets, child.TargetId, "ability_id");
            }

            foreach (var child in ability.Effects)
            {
                RequireSameAbility(ability.AbilityId, child.AbilityId, CanonicalAbilityTableIds.Effects, child.EffectId, "ability_id");
            }
        }
    }

    private static void ValidateSequences(
        IEnumerable<CanonicalCardKeywordDefinition> keywords,
        IEnumerable<CanonicalAbilityTargetDefinition> targets,
        IEnumerable<CanonicalAbilityEffectDefinition> effects,
        IEnumerable<CanonicalAbilityEffectParameterDefinition> parameters,
        IEnumerable<CanonicalAbilityTriggerDefinition> triggers,
        IEnumerable<CanonicalAbilityConditionDefinition> conditions,
        IEnumerable<CanonicalAbilityExpressionDefinition> expressions,
        IEnumerable<CanonicalAbilityDurationDefinition> durations,
        IEnumerable<CanonicalAbilityTemplateArgumentDefinition> arguments)
    {
        RequireUniqueScope(keywords, value => (value.CardId, value.Sequence), CanonicalAbilityTableIds.CardKeywords);
        RequireUniqueScope(targets, value => (value.AbilityId, value.Sequence), CanonicalAbilityTableIds.Targets);
        RequireUniqueScope(effects, value => (value.AbilityId, value.ParentEffectId ?? string.Empty, value.BranchKey ?? string.Empty, value.Sequence), CanonicalAbilityTableIds.Effects);
        RequireUniqueScope(parameters, value => (value.EffectId, value.ContractFieldId, value.ItemIndex), CanonicalAbilityTableIds.EffectParameters);
        RequireUniqueScope(triggers, value => (value.AbilityId, value.Sequence), CanonicalAbilityTableIds.Triggers);
        RequireUniqueScope(conditions, value => (value.AbilityId, value.ParentConditionId ?? string.Empty, value.Sequence), CanonicalAbilityTableIds.Conditions);
        RequireUniqueScope(expressions, value => (value.AbilityId, value.ParentExpressionId ?? string.Empty, value.Sequence), CanonicalAbilityTableIds.Expressions);
        RequireUniqueScope(durations, value => value.EffectId, CanonicalAbilityTableIds.Durations);
        RequireUniqueScope(arguments, value => (value.AbilityId, value.ContractFieldId, value.ItemIndex), CanonicalAbilityTableIds.TemplateArguments);
    }

    private static void ValidateAbilitySequences(IEnumerable<CanonicalAbilityDefinition> abilities) =>
        RequireUniqueScope(abilities, value => (value.CardId, value.AbilityIndex), CanonicalAbilityTableIds.Abilities);

    private static void ValidateHierarchies(
        ImmutableArray<CanonicalRecord> abilityRecords,
        ImmutableDictionary<string, CanonicalAbilityEffectDefinition> effects,
        ImmutableDictionary<string, CanonicalAbilityConditionDefinition> conditions,
        ImmutableDictionary<string, CanonicalAbilityExpressionDefinition> expressions)
    {
        var abilityParents = abilityRecords.ToImmutableDictionary(
            record => ReadRequiredString(record, "ability_id"),
            record => ReadOptionalString(record, "parent_ability_id"),
            StringComparer.Ordinal);
        RequireAcyclic(abilityParents, CanonicalAbilityTableIds.Abilities);
        RequireAcyclic(effects.ToImmutableDictionary(pair => pair.Key, pair => pair.Value.ParentEffectId, StringComparer.Ordinal), CanonicalAbilityTableIds.Effects);
        RequireAcyclic(conditions.ToImmutableDictionary(pair => pair.Key, pair => pair.Value.ParentConditionId, StringComparer.Ordinal), CanonicalAbilityTableIds.Conditions);
        RequireAcyclic(expressions.ToImmutableDictionary(pair => pair.Key, pair => pair.Value.ParentExpressionId, StringComparer.Ordinal), CanonicalAbilityTableIds.Expressions);
    }

    private static void RequireAcyclic(ImmutableDictionary<string, string?> parents, string tableId)
    {
        foreach (var start in parents.Keys)
        {
            var visited = new HashSet<string>(StringComparer.Ordinal);
            var current = start;
            while (parents.TryGetValue(current, out var parent) && parent is not null)
            {
                if (!visited.Add(current) || string.Equals(parent, start, StringComparison.Ordinal))
                {
                    throw new EngineInputException(
                        "CANONICAL_ABILITY_HIERARCHY_CYCLE",
                        $"Canonical ability materialization found a hierarchy cycle in table {tableId}.");
                }

                current = parent;
            }
        }
    }

    private static CanonicalTable RequireTable(ImmutableDictionary<string, CanonicalTable> tables, string tableId)
    {
        if (!tables.TryGetValue(tableId, out var table))
        {
            throw new EngineInputException(
                "CANONICAL_ABILITY_TABLE_MISSING",
                $"Canonical ability materialization requires logical table: {tableId}");
        }

        return table;
    }

    private static ImmutableDictionary<string, T> BuildUnique<T>(IEnumerable<T> values, Func<T, string> id, string tableId)
    {
        var result = ImmutableDictionary.CreateBuilder<string, T>(StringComparer.Ordinal);
        foreach (var value in values)
        {
            if (!result.TryAdd(id(value), value))
            {
                throw new EngineInputException(
                    "CANONICAL_ABILITY_ID_DUPLICATE",
                    $"Canonical ability materialization found a duplicate stable ID in table {tableId}.");
            }
        }

        return result.ToImmutable();
    }

    private static ImmutableHashSet<string> BuildRecordIdSet(
        ImmutableArray<CanonicalRecord> records,
        string fieldName,
        string tableId)
    {
        var result = ImmutableHashSet.CreateBuilder<string>(StringComparer.Ordinal);
        foreach (var record in records)
        {
            if (!result.Add(ReadRequiredString(record, fieldName)))
            {
                throw new EngineInputException(
                    "CANONICAL_ABILITY_ID_DUPLICATE",
                    $"Canonical ability materialization found a duplicate stable ID in table {tableId}.");
            }
        }

        return result.ToImmutable();
    }

    private static ImmutableDictionary<string, ImmutableArray<T>> GroupSequenced<T>(
        IEnumerable<T> values,
        Func<T, string> groupKey,
        Func<T, int> sequence,
        Func<T, string> stableId) =>
        values.GroupBy(groupKey, StringComparer.Ordinal)
            .ToImmutableDictionary(
                group => group.Key,
                group => group.OrderBy(sequence).ThenBy(stableId, StringComparer.Ordinal).ToImmutableArray(),
                StringComparer.Ordinal);

    private static ImmutableDictionary<string, ImmutableArray<T>> GroupOrdered<T>(
        IEnumerable<T> values,
        Func<T, string> groupKey,
        Func<T, string> firstOrder,
        Func<T, int> secondOrder,
        Func<T, string> stableId) =>
        values.GroupBy(groupKey, StringComparer.Ordinal)
            .ToImmutableDictionary(
                group => group.Key,
                group => group.OrderBy(firstOrder, StringComparer.Ordinal).ThenBy(secondOrder).ThenBy(stableId, StringComparer.Ordinal).ToImmutableArray(),
                StringComparer.Ordinal);

    private static ImmutableArray<T> GetGroup<T>(ImmutableDictionary<string, ImmutableArray<T>> groups, string key) =>
        groups.TryGetValue(key, out var values) ? values : ImmutableArray<T>.Empty;

    private static void ValidateScopedReference<T>(
        string? referenceId,
        ImmutableDictionary<string, T> values,
        Func<T, string> abilityId,
        string expectedAbilityId,
        string tableId,
        string recordId,
        string fieldName)
    {
        if (referenceId is null)
        {
            return;
        }

        RequireReference(values.ContainsKey(referenceId), tableId, recordId, fieldName);
        RequireSameAbility(expectedAbilityId, abilityId(values[referenceId]), tableId, recordId, fieldName);
    }

    private static void RequireReference(bool exists, string tableId, string recordId, string fieldName)
    {
        if (!exists)
        {
            throw new EngineInputException(
                ReferenceMissingCode,
                $"Canonical record {tableId}/{recordId} has an unresolved {fieldName} reference.");
        }
    }

    private static void RequireSameAbility(string expected, string actual, string tableId, string recordId, string fieldName)
    {
        if (!string.Equals(expected, actual, StringComparison.Ordinal))
        {
            throw new EngineInputException(
                ScopeMismatchCode,
                $"Canonical record {tableId}/{recordId} has a cross-scope {fieldName} reference.");
        }
    }

    private static void RequireUniqueScope<T, TKey>(IEnumerable<T> values, Func<T, TKey> key, string tableId)
        where TKey : notnull
    {
        var seen = new HashSet<TKey>();
        foreach (var value in values)
        {
            if (!seen.Add(key(value)))
            {
                throw new EngineInputException(
                    "CANONICAL_ABILITY_SEQUENCE_DUPLICATE",
                    $"Canonical ability materialization found a duplicate ordered scope in table {tableId}.");
            }
        }
    }

    private static string ReadRequiredString(CanonicalRecord record, string fieldName)
    {
        if (!record.Fields.TryGetValue(fieldName, out var value)
            || value.ValueKind != JsonValueKind.String
            || string.IsNullOrWhiteSpace(value.GetString()))
        {
            throw InvalidField(fieldName);
        }

        return value.GetString()!;
    }

    private static string? ReadOptionalString(CanonicalRecord record, string fieldName) =>
        ReadOptionalStringCore(record, fieldName, allowEmpty: false);

    private static string? ReadOptionalText(CanonicalRecord record, string fieldName) =>
        ReadOptionalStringCore(record, fieldName, allowEmpty: true);

    private static string? ReadOptionalStringCore(CanonicalRecord record, string fieldName, bool allowEmpty)
    {
        if (!record.Fields.TryGetValue(fieldName, out var value) || value.ValueKind == JsonValueKind.Null)
        {
            return null;
        }

        if (value.ValueKind != JsonValueKind.String || (!allowEmpty && string.IsNullOrWhiteSpace(value.GetString())))
        {
            throw InvalidField(fieldName);
        }

        return value.GetString();
    }

    private static int ReadRequiredInteger(CanonicalRecord record, string fieldName)
    {
        if (!record.Fields.TryGetValue(fieldName, out var value)
            || value.ValueKind != JsonValueKind.Number
            || !value.TryGetInt32(out var result))
        {
            throw InvalidField(fieldName);
        }

        return result;
    }

    private static int? ReadOptionalInteger(CanonicalRecord record, string fieldName)
    {
        if (!record.Fields.TryGetValue(fieldName, out var value) || value.ValueKind == JsonValueKind.Null)
        {
            return null;
        }

        if (value.ValueKind != JsonValueKind.Number || !value.TryGetInt32(out var result))
        {
            throw InvalidField(fieldName);
        }

        return result;
    }

    private static bool ReadRequiredBoolean(CanonicalRecord record, string fieldName)
    {
        if (!record.Fields.TryGetValue(fieldName, out var value)
            || value.ValueKind is not (JsonValueKind.True or JsonValueKind.False))
        {
            throw InvalidField(fieldName);
        }

        return value.GetBoolean();
    }

    private static bool? ReadOptionalBoolean(CanonicalRecord record, string fieldName)
    {
        if (!record.Fields.TryGetValue(fieldName, out var value) || value.ValueKind == JsonValueKind.Null)
        {
            return null;
        }

        if (value.ValueKind is not (JsonValueKind.True or JsonValueKind.False))
        {
            throw InvalidField(fieldName);
        }

        return value.GetBoolean();
    }

    private static EngineInputException InvalidField(string fieldName) => new(
        FieldInvalidCode,
        $"Canonical ability field is missing or has an invalid JSON type: {fieldName}");

    private sealed class CanonicalVocabularyValidator
    {
        private readonly CanonicalRegistryPackage _registry;
        private readonly ImmutableDictionary<(string TableId, string FieldName), SchemaReference> _cardDatabaseSchema;
        private readonly ImmutableDictionary<(string TableId, string FieldName), SchemaReference> _registrySchema;
        private readonly ImmutableDictionary<string, ImmutableHashSet<string>> _valuesByGroup;

        private CanonicalVocabularyValidator(
            CanonicalRegistryPackage registry,
            ImmutableDictionary<(string TableId, string FieldName), SchemaReference> cardDatabaseSchema,
            ImmutableDictionary<(string TableId, string FieldName), SchemaReference> registrySchema,
            ImmutableDictionary<string, ImmutableHashSet<string>> valuesByGroup)
        {
            _registry = registry;
            _cardDatabaseSchema = cardDatabaseSchema;
            _registrySchema = registrySchema;
            _valuesByGroup = valuesByGroup;
        }

        public static CanonicalVocabularyValidator Create(
            CanonicalCardDatabasePackage cardDatabase,
            CanonicalRegistryPackage registry)
        {
            var cardSchema = ReadSchema(cardDatabase.Tables);
            var registrySchema = ReadSchema(registry.Tables);
            var valuesByGroup = ImmutableDictionary.CreateBuilder<string, ImmutableHashSet<string>>(StringComparer.Ordinal);
            if (registry.Tables.TryGetValue("value_registry", out var valueRegistry))
            {
                foreach (var group in valueRegistry.Records.GroupBy(record => ReadRequiredString(record, "group_id"), StringComparer.Ordinal))
                {
                    valuesByGroup[group.Key] = group.Select(record => ReadRequiredString(record, "value_id"))
                        .ToImmutableHashSet(StringComparer.Ordinal);
                }
            }

            return new CanonicalVocabularyValidator(registry, cardSchema, registrySchema, valuesByGroup.ToImmutable());
        }

        public void ValidateCardDatabaseTable(string tableId, ImmutableArray<CanonicalRecord> records) =>
            Validate(tableId, records, _cardDatabaseSchema, registryPrefixRequired: true);

        public void ValidateRegistryTable(string tableId, ImmutableArray<CanonicalRecord> records) =>
            Validate(tableId, records, _registrySchema, registryPrefixRequired: false);

        private void Validate(
            string tableId,
            ImmutableArray<CanonicalRecord> records,
            ImmutableDictionary<(string TableId, string FieldName), SchemaReference> schema,
            bool registryPrefixRequired)
        {
            foreach (var record in records)
            {
                foreach (var field in record.Fields)
                {
                    if (field.Value.ValueKind == JsonValueKind.Null
                        || !schema.TryGetValue((tableId, field.Key), out var reference)
                        || (reference.AllowedGroupId is null && reference.ReferenceTableId is null))
                    {
                        continue;
                    }

                    if (field.Value.ValueKind != JsonValueKind.String || string.IsNullOrWhiteSpace(field.Value.GetString()))
                    {
                        throw InvalidField(field.Key);
                    }

                    var value = field.Value.GetString()!;
                    if (reference.AllowedGroupId is not null)
                    {
                        if (!_valuesByGroup.TryGetValue(reference.AllowedGroupId, out var allowed) || !allowed.Contains(value))
                        {
                            throw UnknownVocabulary(tableId, field.Key, value);
                        }

                        continue;
                    }

                    var referenceTableId = reference.ReferenceTableId!;
                    if (registryPrefixRequired)
                    {
                        if (!referenceTableId.StartsWith("registry:", StringComparison.Ordinal))
                        {
                            continue;
                        }

                        referenceTableId = referenceTableId["registry:".Length..];
                    }
                    else if (referenceTableId.Contains(':', StringComparison.Ordinal))
                    {
                        continue;
                    }

                    if (!_registry.Tables.TryGetValue(referenceTableId, out var referenceTable)
                        || !referenceTable.RecordsById.ContainsKey(value))
                    {
                        throw UnknownVocabulary(tableId, field.Key, value);
                    }
                }
            }
        }

        private static ImmutableDictionary<(string TableId, string FieldName), SchemaReference> ReadSchema(
            ImmutableDictionary<string, CanonicalTable> tables)
        {
            var result = ImmutableDictionary.CreateBuilder<(string TableId, string FieldName), SchemaReference>();
            if (!tables.TryGetValue("schema_fields", out var schemaFields))
            {
                return result.ToImmutable();
            }

            foreach (var record in schemaFields.Records)
            {
                if (!record.Fields.TryGetValue("status", out var status)
                    || status.ValueKind != JsonValueKind.String
                    || !string.Equals(status.GetString(), "active", StringComparison.Ordinal))
                {
                    continue;
                }

                var key = (ReadRequiredString(record, "table_id"), ReadRequiredString(record, "field_name"));
                var reference = new SchemaReference(
                    ReadOptionalString(record, "allowed_group_id"),
                    ReadOptionalString(record, "reference_table_id"));
                if (!result.TryAdd(key, reference))
                {
                    throw new EngineInputException(
                        "CANONICAL_ABILITY_SCHEMA_INVALID",
                        $"Canonical schema contains a duplicate active field definition: {key.Item1}.{key.Item2}");
                }
            }

            return result.ToImmutable();
        }

        private static EngineInputException UnknownVocabulary(string tableId, string fieldName, string value) => new(
            "CANONICAL_ABILITY_VOCABULARY_UNKNOWN",
            $"Canonical ability vocabulary value is unknown for {tableId}.{fieldName}: {value}");

        private sealed record SchemaReference(string? AllowedGroupId, string? ReferenceTableId);
    }
}
