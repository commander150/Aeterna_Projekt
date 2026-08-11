using System.Collections.Immutable;
using System.Text.Json;

namespace Aeterna.Engine.Runtime;

public sealed record CanonicalAbilityTemplateProvenance(
    string OriginalAbilityId,
    string SourceCardId,
    string TemplateId,
    string TemplateVersion,
    string ParameterSchemaId,
    ImmutableArray<string> ArgumentIds,
    ImmutableArray<string> BindingIds,
    ImmutableDictionary<string, string> GeneratedNodeIds);

internal sealed record CanonicalTemplateExpansionResult(
    ImmutableDictionary<string, ImmutableArray<CanonicalRecord>> RecordsByTable,
    ImmutableDictionary<string, CanonicalAbilityTemplateProvenance> ProvenanceByAbilityId)
{
    internal ImmutableArray<CanonicalRecord> GetRecords(string tableId) =>
        RecordsByTable.TryGetValue(tableId, out var records)
            ? records
            : ImmutableArray<CanonicalRecord>.Empty;
}

internal static class CanonicalAbilityTemplateCompiler
{
    private const string ActiveStatus = "active";
    private const string TemplateInstanceMode = "template_instance";
    private const string LoadTimeCompilePolicy = "load_time_compile";

    private static readonly ImmutableHashSet<string> SupportedOutputTables =
        ImmutableHashSet.Create(
            StringComparer.Ordinal,
            CanonicalAbilityTableIds.Targets,
            CanonicalAbilityTableIds.Effects,
            CanonicalAbilityTableIds.EffectParameters,
            CanonicalAbilityTableIds.Triggers,
            CanonicalAbilityTableIds.Conditions,
            CanonicalAbilityTableIds.Expressions,
            CanonicalAbilityTableIds.Durations);

    internal static CanonicalTemplateExpansionResult Expand(
        CanonicalCardDatabasePackage cardDatabase,
        ImmutableDictionary<string, CanonicalAbilityTemplateDefinition> templates,
        ImmutableDictionary<string, CanonicalAbilityTemplateArgumentDefinition> arguments,
        ImmutableArray<CanonicalRecord> abilityRecords)
    {
        ArgumentNullException.ThrowIfNull(cardDatabase);
        var compileCandidates = abilityRecords
            .Where(record => string.Equals(
                ReadRequiredString(record, "implementation_mode_id"),
                TemplateInstanceMode,
                StringComparison.Ordinal))
            .Where(record =>
            {
                var templateId = ReadOptionalString(record, "ability_template_id");
                return templateId is not null
                       && templates.TryGetValue(templateId, out var template)
                       && string.Equals(template.ExpansionPolicyId, LoadTimeCompilePolicy, StringComparison.Ordinal);
            })
            .OrderBy(record => ReadRequiredString(record, "ability_id"), StringComparer.Ordinal)
            .ToImmutableArray();
        if (compileCandidates.Length == 0)
        {
            return new CanonicalTemplateExpansionResult(
                ImmutableDictionary<string, ImmutableArray<CanonicalRecord>>.Empty.WithComparers(StringComparer.Ordinal),
                ImmutableDictionary<string, CanonicalAbilityTemplateProvenance>.Empty.WithComparers(StringComparer.Ordinal));
        }

        var registry = cardDatabase.Registry;
        var nodeTable = RequireTable(registry.Tables, CanonicalAbilityTableIds.AbilityTemplateNodes);
        var bindingTable = RequireTable(registry.Tables, CanonicalAbilityTableIds.AbilityTemplateBindings);
        var contractFieldTable = RequireTable(registry.Tables, CanonicalAbilityTableIds.ContractFields);
        var schemaFieldTable = RequireTable(cardDatabase.Tables, CanonicalAbilityTableIds.SchemaFields);
        var valueRegistryTable = RequireTable(registry.Tables, CanonicalAbilityTableIds.ValueRegistry);

        var nodes = BuildUnique(
            nodeTable.Records.Select(ParseNode),
            node => node.TemplateNodeId,
            "CANONICAL_TEMPLATE_NODE_DUPLICATE");
        var bindings = BuildUnique(
            bindingTable.Records.Select(ParseBinding),
            binding => binding.TemplateBindingId,
            "CANONICAL_TEMPLATE_BINDING_DUPLICATE");
        var contractFields = BuildUnique(
            contractFieldTable.Records.Select(ParseContractField),
            field => field.ContractFieldId,
            "CANONICAL_TEMPLATE_CONTRACT_FIELD_DUPLICATE");
        var schemaFields = BuildUnique(
            schemaFieldTable.Records
                .Where(record => string.Equals(ReadRequiredString(record, "status"), ActiveStatus, StringComparison.Ordinal))
                .Select(ParseSchemaField),
            field => field.FieldId,
            "CANONICAL_TEMPLATE_SCHEMA_FIELD_DUPLICATE");

        ValidateTemplateModel(templates, nodes, bindings, schemaFields);
        var nodesByTemplate = nodes.Values
            .GroupBy(node => node.TemplateId, StringComparer.Ordinal)
            .ToImmutableDictionary(
                group => group.Key,
                group => group.OrderBy(node => node.NodeOrder)
                    .ThenBy(node => node.TemplateNodeId, StringComparer.Ordinal)
                    .ToImmutableArray(),
                StringComparer.Ordinal);
        var bindingsByNode = bindings.Values
            .GroupBy(binding => binding.TemplateNodeId, StringComparer.Ordinal)
            .ToImmutableDictionary(
                group => group.Key,
                group => group.OrderBy(binding => binding.TargetFieldId, StringComparer.Ordinal)
                    .ThenBy(binding => binding.TemplateBindingId, StringComparer.Ordinal)
                    .ToImmutableArray(),
                StringComparer.Ordinal);
        var argumentsByAbility = arguments.Values
            .GroupBy(argument => argument.AbilityId, StringComparer.Ordinal)
            .ToImmutableDictionary(
                group => group.Key,
                group => group.OrderBy(argument => argument.ContractFieldId, StringComparer.Ordinal)
                    .ThenBy(argument => argument.ItemIndex)
                    .ThenBy(argument => argument.ArgumentId, StringComparer.Ordinal)
                    .ToImmutableArray(),
                StringComparer.Ordinal);

        var generated = SupportedOutputTables.ToDictionary(
            tableId => tableId,
            _ => ImmutableArray.CreateBuilder<CanonicalRecord>(),
            StringComparer.Ordinal);
        var provenance = ImmutableDictionary.CreateBuilder<string, CanonicalAbilityTemplateProvenance>(StringComparer.Ordinal);
        foreach (var abilityRecord in compileCandidates)
        {
            var abilityId = ReadRequiredString(abilityRecord, "ability_id");
            var cardId = ReadRequiredString(abilityRecord, "card_id");
            var templateId = ReadRequiredString(abilityRecord, "ability_template_id");
            var template = templates[templateId];
            if (!nodesByTemplate.TryGetValue(templateId, out var templateNodes) || templateNodes.Length == 0)
            {
                throw Error(
                    "CANONICAL_TEMPLATE_NODE_MISSING",
                    $"Load-time template has no active output nodes: {templateId}");
            }

            EnsureNoManualGraph(cardDatabase, abilityId);
            var abilityArguments = argumentsByAbility.TryGetValue(abilityId, out var declaredArguments)
                ? declaredArguments
                : ImmutableArray<CanonicalAbilityTemplateArgumentDefinition>.Empty;
            var argumentsByContractField = ValidateArguments(
                abilityId,
                template,
                abilityArguments,
                contractFields);
            var generatedNodeIds = templateNodes.ToImmutableDictionary(
                node => node.NodeKey,
                node => $"{abilityId}__{node.NodeKey}",
                StringComparer.Ordinal);
            var usedBindingIds = ImmutableArray.CreateBuilder<string>();
            foreach (var node in templateNodes)
            {
                if (!bindingsByNode.TryGetValue(node.TemplateNodeId, out var nodeBindings)
                    || nodeBindings.Length == 0)
                {
                    throw Error(
                        "CANONICAL_TEMPLATE_BINDING_MISSING",
                        $"Template node has no field bindings: {node.TemplateNodeId}");
                }

                var record = CompileNode(
                    cardDatabase,
                    valueRegistryTable,
                    abilityRecord,
                    node,
                    nodeBindings,
                    schemaFields,
                    generatedNodeIds,
                    argumentsByContractField);
                generated[node.OutputTableId].Add(record);
                usedBindingIds.AddRange(nodeBindings.Select(binding => binding.TemplateBindingId));
            }

            provenance.Add(
                abilityId,
                new CanonicalAbilityTemplateProvenance(
                    abilityId,
                    cardId,
                    template.TemplateId,
                    template.TemplateVersion,
                    template.ParameterSchemaId,
                    abilityArguments.Select(argument => argument.ArgumentId).ToImmutableArray(),
                    usedBindingIds.ToImmutable(),
                    generatedNodeIds));
        }

        return new CanonicalTemplateExpansionResult(
            generated.ToImmutableDictionary(
                pair => pair.Key,
                pair => pair.Value.ToImmutable(),
                StringComparer.Ordinal),
            provenance.ToImmutable());
    }

    private static CanonicalRecord CompileNode(
        CanonicalCardDatabasePackage cardDatabase,
        CanonicalTable valueRegistryTable,
        CanonicalRecord abilityRecord,
        TemplateNode node,
        ImmutableArray<TemplateBinding> bindings,
        ImmutableDictionary<string, TemplateSchemaField> schemaFields,
        ImmutableDictionary<string, string> generatedNodeIds,
        ImmutableDictionary<string, CanonicalAbilityTemplateArgumentDefinition> arguments)
    {
        if (!cardDatabase.Tables.TryGetValue(node.OutputTableId, out var outputTable))
        {
            throw Error(
                "CANONICAL_TEMPLATE_OUTPUT_TABLE_INVALID",
                $"Template node output table is unavailable: {node.OutputTableId}");
        }

        var fields = ImmutableDictionary.CreateBuilder<string, JsonElement>(StringComparer.Ordinal);
        var abilityId = ReadRequiredString(abilityRecord, "ability_id");
        fields[outputTable.PrimaryKey] = Json(generatedNodeIds[node.NodeKey]);
        if (HasSchemaField(schemaFields, node.OutputTableId, "ability_id"))
        {
            fields["ability_id"] = Json(abilityId);
        }

        if (HasSchemaField(schemaFields, node.OutputTableId, "sequence"))
        {
            fields["sequence"] = Json(node.OutputSequence);
        }

        foreach (var fieldName in new[] { "status", "source_id", "source_ref", "notes" })
        {
            if (HasSchemaField(schemaFields, node.OutputTableId, fieldName))
            {
                fields[fieldName] = fieldName switch
                {
                    "status" => Json(ReadRequiredString(abilityRecord, fieldName)),
                    "source_id" => Json(ReadRequiredString(abilityRecord, fieldName)),
                    "source_ref" => Json(ReadOptionalString(abilityRecord, fieldName)),
                    _ => Json(null),
                };
            }
        }

        if (HasSchemaField(schemaFields, node.OutputTableId, "engine_support_status"))
        {
            fields["engine_support_status"] = Json(ReadRequiredString(abilityRecord, "engine_support_status"));
        }

        var targetFields = new HashSet<string>(StringComparer.Ordinal);
        foreach (var binding in bindings)
        {
            if (!targetFields.Add(binding.TargetFieldId))
            {
                throw Error(
                    "CANONICAL_TEMPLATE_BINDING_DUPLICATE",
                    $"Template node binds the same output field more than once: {node.TemplateNodeId}/{binding.TargetFieldId}");
            }

            if (!schemaFields.TryGetValue(binding.TargetFieldId, out var schemaField)
                || !string.Equals(schemaField.TableId, node.OutputTableId, StringComparison.Ordinal))
            {
                throw Error(
                    "CANONICAL_TEMPLATE_TARGET_FIELD_INVALID",
                    $"Template binding target field does not belong to its output table: {binding.TargetFieldId}");
            }

            fields[schemaField.FieldName] = ResolveBindingValue(
                binding,
                schemaField,
                valueRegistryTable,
                generatedNodeIds,
                arguments);
        }

        return new CanonicalRecord(fields.ToImmutable());
    }

    private static bool HasSchemaField(
        ImmutableDictionary<string, TemplateSchemaField> schemaFields,
        string tableId,
        string fieldName) => schemaFields.Values.Any(field =>
        string.Equals(field.TableId, tableId, StringComparison.Ordinal)
        && string.Equals(field.FieldName, fieldName, StringComparison.Ordinal));

    private static JsonElement ResolveBindingValue(
        TemplateBinding binding,
        TemplateSchemaField schemaField,
        CanonicalTable valueRegistryTable,
        ImmutableDictionary<string, string> generatedNodeIds,
        ImmutableDictionary<string, CanonicalAbilityTemplateArgumentDefinition> arguments) =>
        binding.BindingKindId switch
        {
            "fixed_value" => ResolveFixedValue(binding, schemaField, valueRegistryTable),
            "generated_node_id" => ResolveGeneratedNodeId(binding, generatedNodeIds),
            "template_parameter" => ResolveTemplateParameter(binding, schemaField, arguments),
            _ => throw Error(
                "CANONICAL_TEMPLATE_BINDING_KIND_UNSUPPORTED",
                $"Unsupported template binding kind: {binding.BindingKindId}"),
        };

    private static JsonElement ResolveFixedValue(
        TemplateBinding binding,
        TemplateSchemaField schemaField,
        CanonicalTable valueRegistryTable)
    {
        RequireBindingShape(binding, requireParameter: false, requireSourceNode: false);
        var channels = new object?[]
        {
            binding.FixedBoolean,
            binding.FixedInteger,
            binding.FixedText,
            binding.FixedRegistryValueId,
            binding.FixedReferenceId,
        };
        if (channels.Count(value => value is not null) != 1)
        {
            throw Error(
                "CANONICAL_TEMPLATE_BINDING_VALUE_INVALID",
                $"fixed_value binding must use exactly one typed value channel: {binding.TemplateBindingId}");
        }

        if (binding.FixedBoolean is bool boolean)
        {
            RequireDataType(schemaField, "boolean", binding);
            return Json(boolean);
        }

        if (binding.FixedInteger is int integer)
        {
            RequireDataType(schemaField, "integer", binding);
            return Json(integer);
        }

        if (binding.FixedText is not null)
        {
            return Json(binding.FixedText);
        }

        if (binding.FixedReferenceId is not null)
        {
            return Json(binding.FixedReferenceId);
        }

        var registryValueId = binding.FixedRegistryValueId!;
        if (schemaField.AllowedGroupId is null)
        {
            return Json(registryValueId);
        }

        if (!valueRegistryTable.RecordsById.TryGetValue(registryValueId, out var registryValue)
            || !string.Equals(
                ReadRequiredString(registryValue, "group_id"),
                schemaField.AllowedGroupId,
                StringComparison.Ordinal))
        {
            throw Error(
                "CANONICAL_TEMPLATE_REGISTRY_VALUE_INVALID",
                $"Template registry binding does not satisfy the target field vocabulary: {binding.TemplateBindingId}");
        }

        return Json(ReadRequiredString(registryValue, "value_id"));
    }

    private static JsonElement ResolveGeneratedNodeId(
        TemplateBinding binding,
        ImmutableDictionary<string, string> generatedNodeIds)
    {
        RequireBindingShape(binding, requireParameter: false, requireSourceNode: true);
        if (!generatedNodeIds.TryGetValue(binding.SourceNodeKey!, out var generatedId))
        {
            throw Error(
                "CANONICAL_TEMPLATE_NODE_REFERENCE_INVALID",
                $"Template binding references an unknown source node: {binding.SourceNodeKey}");
        }

        return Json(generatedId);
    }

    private static JsonElement ResolveTemplateParameter(
        TemplateBinding binding,
        TemplateSchemaField schemaField,
        ImmutableDictionary<string, CanonicalAbilityTemplateArgumentDefinition> arguments)
    {
        RequireBindingShape(binding, requireParameter: true, requireSourceNode: false);
        if (!arguments.TryGetValue(binding.ParameterContractFieldId!, out var argument))
        {
            throw Error(
                "CANONICAL_TEMPLATE_ARGUMENT_MISSING",
                $"Template binding required argument is missing: {binding.ParameterContractFieldId}");
        }

        if (argument.ValueInteger is int integer)
        {
            RequireDataType(schemaField, "integer", binding);
            return Json(integer);
        }

        if (argument.ValueBoolean is bool boolean)
        {
            RequireDataType(schemaField, "boolean", binding);
            return Json(boolean);
        }

        if (argument.ValueText is not null)
        {
            return Json(argument.ValueText);
        }

        if (argument.ValueRegistryValueId is not null)
        {
            return Json(argument.ValueRegistryValueId);
        }

        if (argument.ValueReferenceId is not null)
        {
            return Json(argument.ValueReferenceId);
        }

        throw Error(
            "CANONICAL_TEMPLATE_ARGUMENT_TYPE_INVALID",
            $"Template argument cannot be written to the requested output field: {argument.ArgumentId}");
    }

    private static ImmutableDictionary<string, CanonicalAbilityTemplateArgumentDefinition> ValidateArguments(
        string abilityId,
        CanonicalAbilityTemplateDefinition template,
        ImmutableArray<CanonicalAbilityTemplateArgumentDefinition> arguments,
        ImmutableDictionary<string, TemplateContractField> contractFields)
    {
        var templateFields = contractFields.Values
            .Where(field => string.Equals(field.ContractSchemaId, template.ParameterSchemaId, StringComparison.Ordinal)
                            && string.Equals(field.Status, ActiveStatus, StringComparison.Ordinal))
            .OrderBy(field => field.FieldOrder)
            .ThenBy(field => field.ContractFieldId, StringComparer.Ordinal)
            .ToImmutableArray();
        var fieldsById = templateFields.ToImmutableDictionary(field => field.ContractFieldId, StringComparer.Ordinal);
        var result = ImmutableDictionary.CreateBuilder<string, CanonicalAbilityTemplateArgumentDefinition>(StringComparer.Ordinal);
        foreach (var argument in arguments)
        {
            if (!string.Equals(argument.Status, ActiveStatus, StringComparison.Ordinal)
                || !fieldsById.TryGetValue(argument.ContractFieldId, out var field))
            {
                throw Error(
                    "CANONICAL_TEMPLATE_ARGUMENT_UNKNOWN",
                    $"Template instance contains an unknown or inactive argument: {argument.ArgumentId}");
            }

            if (field.IsCollection || argument.ItemIndex != 1 || !result.TryAdd(argument.ContractFieldId, argument))
            {
                throw Error(
                    "CANONICAL_TEMPLATE_ARGUMENT_DUPLICATE",
                    $"Template argument cardinality is invalid: {abilityId}/{argument.ContractFieldId}");
            }

            ValidateArgumentChannel(argument, field);
        }

        foreach (var field in templateFields.Where(field => string.Equals(field.RequiredMode, "always", StringComparison.Ordinal)))
        {
            if (!result.ContainsKey(field.ContractFieldId))
            {
                throw Error(
                    "CANONICAL_TEMPLATE_ARGUMENT_MISSING",
                    $"Template instance is missing required argument: {abilityId}/{field.ContractFieldId}");
            }
        }

        return result.ToImmutable();
    }

    private static void ValidateArgumentChannel(
        CanonicalAbilityTemplateArgumentDefinition argument,
        TemplateContractField field)
    {
        var channelCount = new object?[]
        {
            argument.ValueBoolean,
            argument.ValueInteger,
            argument.ValueText,
            argument.ValueRegistryValueId,
            argument.ValueReferenceId,
            argument.ValueExpressionId,
        }.Count(value => value is not null);
        var valid = channelCount == 1 && field.DataType switch
        {
            "integer" => argument.ValueInteger is not null,
            "boolean" => argument.ValueBoolean is not null,
            "string" or "text" => argument.ValueText is not null,
            _ => false,
        };
        if (!valid)
        {
            throw Error(
                "CANONICAL_TEMPLATE_ARGUMENT_TYPE_INVALID",
                $"Template argument value channel does not match its contract: {argument.ArgumentId}");
        }
    }

    private static void ValidateTemplateModel(
        ImmutableDictionary<string, CanonicalAbilityTemplateDefinition> templates,
        ImmutableDictionary<string, TemplateNode> nodes,
        ImmutableDictionary<string, TemplateBinding> bindings,
        ImmutableDictionary<string, TemplateSchemaField> schemaFields)
    {
        foreach (var node in nodes.Values)
        {
            if (!templates.ContainsKey(node.TemplateId)
                || !string.Equals(node.Status, ActiveStatus, StringComparison.Ordinal)
                || !SupportedOutputTables.Contains(node.OutputTableId)
                || node.NodeOrder < 1
                || node.OutputSequence < 1)
            {
                throw Error(
                    "CANONICAL_TEMPLATE_NODE_INVALID",
                    $"Template node is invalid or requests unsupported nesting/output: {node.TemplateNodeId}");
            }
        }

        foreach (var group in nodes.Values.GroupBy(node => node.TemplateId, StringComparer.Ordinal))
        {
            if (group.Select(node => node.NodeKey).Distinct(StringComparer.Ordinal).Count() != group.Count()
                || group.Select(node => node.NodeOrder).Distinct().Count() != group.Count())
            {
                throw Error(
                    "CANONICAL_TEMPLATE_NODE_DUPLICATE",
                    $"Template node_key or node_order is duplicated: {group.Key}");
            }
        }

        foreach (var binding in bindings.Values)
        {
            if (!nodes.TryGetValue(binding.TemplateNodeId, out var node)
                || !string.Equals(binding.Status, ActiveStatus, StringComparison.Ordinal)
                || !schemaFields.TryGetValue(binding.TargetFieldId, out var field)
                || !string.Equals(field.TableId, node.OutputTableId, StringComparison.Ordinal))
            {
                throw Error(
                    "CANONICAL_TEMPLATE_BINDING_INVALID",
                    $"Template binding references an invalid node or target field: {binding.TemplateBindingId}");
            }
        }

        foreach (var group in bindings.Values.GroupBy(
                     binding => (binding.TemplateNodeId, binding.TargetFieldId)))
        {
            if (group.Count() != 1)
            {
                throw Error(
                    "CANONICAL_TEMPLATE_BINDING_DUPLICATE",
                    $"Template output field has duplicate bindings: {group.Key.TemplateNodeId}/{group.Key.TargetFieldId}");
            }
        }
    }

    private static void EnsureNoManualGraph(CanonicalCardDatabasePackage cardDatabase, string abilityId)
    {
        foreach (var tableId in SupportedOutputTables)
        {
            if (cardDatabase.Tables[tableId].Records.Any(record =>
                    record.Fields.TryGetValue("ability_id", out var value)
                    && value.ValueKind == JsonValueKind.String
                    && string.Equals(value.GetString(), abilityId, StringComparison.Ordinal)))
            {
                throw Error(
                    "CANONICAL_TEMPLATE_MANUAL_GRAPH_CONFLICT",
                    $"Template instance also contains a manual canonical graph: {abilityId}/{tableId}");
            }
        }
    }

    private static void RequireBindingShape(
        TemplateBinding binding,
        bool requireParameter,
        bool requireSourceNode)
    {
        if ((binding.ParameterContractFieldId is not null) != requireParameter
            || (binding.SourceNodeKey is not null) != requireSourceNode)
        {
            throw Error(
                "CANONICAL_TEMPLATE_BINDING_VALUE_INVALID",
                $"Template binding metadata does not match its binding kind: {binding.TemplateBindingId}");
        }
    }

    private static void RequireDataType(
        TemplateSchemaField field,
        string expected,
        TemplateBinding binding)
    {
        if (!string.Equals(field.DataType, expected, StringComparison.Ordinal))
        {
            throw Error(
                "CANONICAL_TEMPLATE_BINDING_VALUE_INVALID",
                $"Template binding value type does not match its target field: {binding.TemplateBindingId}");
        }
    }

    private static TemplateNode ParseNode(CanonicalRecord record) => new(
        ReadRequiredString(record, "template_node_id"),
        ReadRequiredString(record, "ability_template_id"),
        ReadRequiredString(record, "node_key"),
        ReadRequiredString(record, "output_table_id"),
        ReadRequiredInteger(record, "node_order"),
        ReadRequiredInteger(record, "output_sequence"),
        ReadRequiredString(record, "status"));

    private static TemplateBinding ParseBinding(CanonicalRecord record) => new(
        ReadRequiredString(record, "template_binding_id"),
        ReadRequiredString(record, "template_node_id"),
        ReadRequiredString(record, "target_field_id"),
        ReadRequiredString(record, "binding_kind_id"),
        ReadOptionalString(record, "parameter_contract_field_id"),
        ReadOptionalString(record, "source_node_key"),
        ReadOptionalBoolean(record, "fixed_boolean"),
        ReadOptionalInteger(record, "fixed_integer"),
        ReadOptionalText(record, "fixed_text"),
        ReadOptionalString(record, "fixed_registry_value_id"),
        ReadOptionalString(record, "fixed_reference_id"),
        ReadRequiredString(record, "status"));

    private static TemplateContractField ParseContractField(CanonicalRecord record) => new(
        ReadRequiredString(record, "contract_field_id"),
        ReadRequiredString(record, "contract_schema_id"),
        ReadRequiredInteger(record, "field_order"),
        ReadRequiredString(record, "data_type"),
        ReadRequiredString(record, "required_mode"),
        ReadRequiredBoolean(record, "nullable"),
        ReadRequiredBoolean(record, "is_collection"),
        ReadRequiredString(record, "status"));

    private static TemplateSchemaField ParseSchemaField(CanonicalRecord record) => new(
        ReadRequiredString(record, "field_id"),
        ReadRequiredString(record, "table_id"),
        ReadRequiredString(record, "field_name"),
        ReadRequiredString(record, "data_type"),
        ReadOptionalString(record, "allowed_group_id"));

    private static CanonicalTable RequireTable(
        ImmutableDictionary<string, CanonicalTable> tables,
        string tableId) =>
        tables.TryGetValue(tableId, out var table)
            ? table
            : throw Error(
                "CANONICAL_TEMPLATE_TABLE_MISSING",
                $"Template compilation requires canonical table: {tableId}");

    private static ImmutableDictionary<string, T> BuildUnique<T>(
        IEnumerable<T> values,
        Func<T, string> id,
        string errorCode)
    {
        var result = ImmutableDictionary.CreateBuilder<string, T>(StringComparer.Ordinal);
        foreach (var value in values)
        {
            if (!result.TryAdd(id(value), value))
            {
                throw Error(errorCode, "Template compiler found a duplicate stable identifier.");
            }
        }

        return result.ToImmutable();
    }

    private static string ReadRequiredString(CanonicalRecord record, string fieldName)
    {
        if (!record.Fields.TryGetValue(fieldName, out var value)
            || value.ValueKind != JsonValueKind.String
            || string.IsNullOrWhiteSpace(value.GetString()))
        {
            throw Error(
                "CANONICAL_TEMPLATE_FIELD_INVALID",
                $"Template field must be a non-empty string: {fieldName}");
        }

        return value.GetString()!;
    }

    private static string? ReadOptionalString(CanonicalRecord record, string fieldName) =>
        !record.Fields.TryGetValue(fieldName, out var value) || value.ValueKind == JsonValueKind.Null
            ? null
            : value.ValueKind == JsonValueKind.String && !string.IsNullOrWhiteSpace(value.GetString())
                ? value.GetString()
                : throw Error(
                    "CANONICAL_TEMPLATE_FIELD_INVALID",
                    $"Template field must be a non-empty string or null: {fieldName}");

    private static string? ReadOptionalText(CanonicalRecord record, string fieldName) =>
        !record.Fields.TryGetValue(fieldName, out var value) || value.ValueKind == JsonValueKind.Null
            ? null
            : value.ValueKind == JsonValueKind.String
                ? value.GetString()
                : throw Error(
                    "CANONICAL_TEMPLATE_FIELD_INVALID",
                    $"Template field must be text or null: {fieldName}");

    private static int ReadRequiredInteger(CanonicalRecord record, string fieldName) =>
        ReadOptionalInteger(record, fieldName)
        ?? throw Error(
            "CANONICAL_TEMPLATE_FIELD_INVALID",
            $"Template field must be an integer: {fieldName}");

    private static int? ReadOptionalInteger(CanonicalRecord record, string fieldName)
    {
        if (!record.Fields.TryGetValue(fieldName, out var value) || value.ValueKind == JsonValueKind.Null)
        {
            return null;
        }

        if (value.ValueKind != JsonValueKind.Number || !value.TryGetInt32(out var result))
        {
            throw Error(
                "CANONICAL_TEMPLATE_FIELD_INVALID",
                $"Template field must be an integer or null: {fieldName}");
        }

        return result;
    }

    private static bool ReadRequiredBoolean(CanonicalRecord record, string fieldName) =>
        ReadOptionalBoolean(record, fieldName)
        ?? throw Error(
            "CANONICAL_TEMPLATE_FIELD_INVALID",
            $"Template field must be a boolean: {fieldName}");

    private static bool? ReadOptionalBoolean(CanonicalRecord record, string fieldName)
    {
        if (!record.Fields.TryGetValue(fieldName, out var value) || value.ValueKind == JsonValueKind.Null)
        {
            return null;
        }

        if (value.ValueKind is not (JsonValueKind.True or JsonValueKind.False))
        {
            throw Error(
                "CANONICAL_TEMPLATE_FIELD_INVALID",
                $"Template field must be a boolean or null: {fieldName}");
        }

        return value.GetBoolean();
    }

    private static JsonElement Json(object? value) => JsonSerializer.SerializeToElement(value);

    private static EngineInputException Error(string code, string message) => new(code, message);

    private sealed record TemplateNode(
        string TemplateNodeId,
        string TemplateId,
        string NodeKey,
        string OutputTableId,
        int NodeOrder,
        int OutputSequence,
        string Status);

    private sealed record TemplateBinding(
        string TemplateBindingId,
        string TemplateNodeId,
        string TargetFieldId,
        string BindingKindId,
        string? ParameterContractFieldId,
        string? SourceNodeKey,
        bool? FixedBoolean,
        int? FixedInteger,
        string? FixedText,
        string? FixedRegistryValueId,
        string? FixedReferenceId,
        string Status);

    private sealed record TemplateContractField(
        string ContractFieldId,
        string ContractSchemaId,
        int FieldOrder,
        string DataType,
        string RequiredMode,
        bool Nullable,
        bool IsCollection,
        string Status);

    private sealed record TemplateSchemaField(
        string FieldId,
        string TableId,
        string FieldName,
        string DataType,
        string? AllowedGroupId);
}
