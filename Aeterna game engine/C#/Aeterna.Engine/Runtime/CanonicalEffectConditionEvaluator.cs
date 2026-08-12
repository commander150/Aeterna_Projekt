using System.Collections.Immutable;

namespace Aeterna.Engine.Runtime;

internal static class CanonicalEffectConditionEvaluator
{
    private const string ActiveStatus = "active";

    internal static void Validate(CanonicalAbilityDefinition ability, string conditionId)
    {
        _ = ReadContract(ability, conditionId);
    }

    internal static bool Evaluate(
        CanonicalAbilityDefinition ability,
        string conditionId,
        IReadOnlyDictionary<string, CanonicalResolvedTargetSet> resolvedTargets)
    {
        ArgumentNullException.ThrowIfNull(resolvedTargets);
        var contract = ReadContract(ability, conditionId);
        if (!resolvedTargets.TryGetValue(contract.TargetId, out var targetSet)
            || targetSet.Value is not CanonicalResolvedCardTargets cards)
        {
            throw Unsupported("Effect-condition aggregate does not reference a resolved card target set.");
        }

        // The aggregate consumes the already materialized identity snapshot. It never
        // re-enumerates the authoritative board while the effect sequence executes.
        return cards.Cards.Length >= contract.RightValue;
    }

    private static CountGreaterThanOrEqualContract ReadContract(
        CanonicalAbilityDefinition ability,
        string conditionId)
    {
        ArgumentNullException.ThrowIfNull(ability);
        var condition = ability.Conditions.SingleOrDefault(item => string.Equals(
            item.ConditionId,
            conditionId,
            StringComparison.Ordinal));
        if (condition is null
            || !string.Equals(condition.Status, ActiveStatus, StringComparison.Ordinal)
            || condition.ParentConditionId is not null
            || !string.Equals(condition.ConditionKindId, "comparison", StringComparison.Ordinal)
            || condition.LogicalOperatorId is not null
            || condition.Negated
            || condition.LeftExpressionId is null
            || !string.Equals(condition.ComparisonOperatorId, "op_greater_than_or_equal", StringComparison.Ordinal)
            || condition.RightExpressionId is null)
        {
            throw Unsupported("Only a non-negated count(target-set) >= integer effect condition is supported.");
        }

        var aggregate = ability.Expressions.SingleOrDefault(item => string.Equals(
            item.ExpressionId,
            condition.LeftExpressionId,
            StringComparison.Ordinal));
        if (aggregate is null
            || !string.Equals(aggregate.Status, ActiveStatus, StringComparison.Ordinal)
            || aggregate.ParentExpressionId is not null
            || !string.Equals(aggregate.ExpressionKindId, "aggregate", StringComparison.Ordinal)
            || aggregate.OperatorId is not null
            || !string.Equals(
                aggregate.ReferenceTypeId,
                "ref_all_matching_cards_zero_or_more",
                StringComparison.Ordinal)
            || aggregate.FieldId is not null
            || !string.Equals(aggregate.AggregateTypeId, "count", StringComparison.Ordinal)
            || aggregate.LiteralDataTypeId is not null
            || aggregate.LiteralNumber is not null
            || aggregate.LiteralText is not null
            || aggregate.LiteralRegistryValueId is not null
            || aggregate.TargetId is not null)
        {
            throw Unsupported("Effect-condition left expression is outside resolved target-set count v1.");
        }

        var children = ability.Expressions
            .Where(item => string.Equals(item.ParentExpressionId, aggregate.ExpressionId, StringComparison.Ordinal))
            .OrderBy(item => item.Sequence)
            .ThenBy(item => item.ExpressionId, StringComparer.Ordinal)
            .ToImmutableArray();
        if (children.Length != 1)
        {
            throw Unsupported("Resolved target-set count requires exactly one reference child expression.");
        }

        var reference = children[0];
        if (!string.Equals(reference.Status, ActiveStatus, StringComparison.Ordinal)
            || !string.Equals(reference.ExpressionKindId, "reference", StringComparison.Ordinal)
            || reference.OperatorId is not null
            || !string.Equals(reference.ReferenceTypeId, aggregate.ReferenceTypeId, StringComparison.Ordinal)
            || reference.FieldId is not null
            || reference.AggregateTypeId is not null
            || reference.LiteralDataTypeId is not null
            || reference.LiteralNumber is not null
            || reference.LiteralText is not null
            || reference.LiteralRegistryValueId is not null
            || string.IsNullOrWhiteSpace(reference.TargetId))
        {
            throw Unsupported("Resolved target-set count reference child is malformed.");
        }

        var target = ability.Targets.SingleOrDefault(item => string.Equals(
            item.TargetId,
            reference.TargetId,
            StringComparison.Ordinal));
        if (target is null
            || !string.Equals(target.Status, ActiveStatus, StringComparison.Ordinal)
            || !string.Equals(target.ReferenceTypeId, reference.ReferenceTypeId, StringComparison.Ordinal)
            || !CanonicalTargetResolver.IsAutomaticCollection(target))
        {
            throw Unsupported("Resolved target-set count reference does not identify an automatic card collection.");
        }

        var literal = ability.Expressions.SingleOrDefault(item => string.Equals(
            item.ExpressionId,
            condition.RightExpressionId,
            StringComparison.Ordinal));
        if (literal is null
            || !string.Equals(literal.Status, ActiveStatus, StringComparison.Ordinal)
            || literal.ParentExpressionId is not null
            || !string.Equals(literal.ExpressionKindId, "literal", StringComparison.Ordinal)
            || literal.OperatorId is not null
            || literal.ReferenceTypeId is not null
            || literal.FieldId is not null
            || literal.AggregateTypeId is not null
            || !string.Equals(literal.LiteralDataTypeId, "integer", StringComparison.Ordinal)
            || literal.LiteralNumber is not int rightValue
            || rightValue < 0
            || literal.LiteralText is not null
            || literal.LiteralRegistryValueId is not null
            || literal.TargetId is not null)
        {
            throw Unsupported("Effect-condition right expression is outside non-negative integer literal v1.");
        }

        return new CountGreaterThanOrEqualContract(reference.TargetId, rightValue);
    }

    private static CanonicalAbilityExecutionException Unsupported(string message) => new(
        "CANONICAL_EFFECT_CONDITION_UNSUPPORTED",
        message);

    private sealed record CountGreaterThanOrEqualContract(string TargetId, int RightValue);
}
