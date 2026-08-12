using Aeterna.Engine.State;

namespace Aeterna.Engine.Runtime;

internal static class CanonicalTargetFilterEvaluator
{
    private const string ActiveStatus = "active";

    internal static void Validate(
        CanonicalAbilityDefinition ability,
        CanonicalAbilityTargetDefinition target)
    {
        if (target.FilterConditionId is null)
        {
            return;
        }

        var condition = ability.Conditions.SingleOrDefault(item => string.Equals(
            item.ConditionId,
            target.FilterConditionId,
            StringComparison.Ordinal));
        if (condition is null
            || !string.Equals(condition.Status, ActiveStatus, StringComparison.Ordinal)
            || condition.ParentConditionId is not null
            || !string.Equals(condition.ConditionKindId, "comparison", StringComparison.Ordinal)
            || condition.LogicalOperatorId is not null
            || condition.Negated
            || condition.LeftExpressionId is null
            || condition.RightExpressionId is null
            || condition.ComparisonOperatorId is not (
                "op_less_than" or
                "op_less_than_or_equal" or
                "op_equal" or
                "op_greater_than_or_equal" or
                "op_greater_than" or
                "op_contains"))
        {
            throw Unsupported("Target filter condition is outside numeric/effective-keyword comparison v1.");
        }

        if (string.Equals(condition.ComparisonOperatorId, "op_contains", StringComparison.Ordinal))
        {
            _ = ReadEffectiveKeywordFieldExpression(ability, condition.LeftExpressionId);
            _ = ReadKeywordLiteralExpression(ability, condition.RightExpressionId);
            return;
        }

        _ = ReadNumericFieldExpression(ability, condition.LeftExpressionId);
        _ = ReadIntegerLiteralExpression(ability, condition.RightExpressionId);
    }

    internal static bool Matches(
        CanonicalAbilityDefinition ability,
        CanonicalAbilityTargetDefinition target,
        CanonicalTargetCandidate candidate,
        MatchState state,
        CanonicalCardCatalog? canonicalCards,
        CanonicalAbilityCatalog? canonicalAbilities)
    {
        if (target.FilterConditionId is null)
        {
            return true;
        }

        Validate(ability, target);
        var condition = ability.Conditions.Single(item => string.Equals(
            item.ConditionId,
            target.FilterConditionId,
            StringComparison.Ordinal));
        if (string.Equals(condition.ComparisonOperatorId, "op_contains", StringComparison.Ordinal))
        {
            _ = ReadEffectiveKeywordFieldExpression(ability, condition.LeftExpressionId!);
            var keywordLiteral = ReadKeywordLiteralExpression(ability, condition.RightExpressionId!);
            if (canonicalAbilities is null)
            {
                throw new CanonicalAbilityExecutionException(
                    "CANONICAL_ABILITY_CATALOG_REQUIRED",
                    "card_effective_keywords requires canonical intrinsic-keyword authority.");
            }

            var candidateCard = state.GetCardInstance(candidate.CardInstanceId);
            var keywordId = CanonicalContinuousEffects.ResolveKeywordRegistryValue(
                keywordLiteral.LiteralRegistryValueId!);
            return CanonicalContinuousEffects.HasEffectiveKeyword(
                state,
                candidateCard,
                canonicalAbilities,
                keywordId);
        }

        var field = ReadNumericFieldExpression(ability, condition.LeftExpressionId!);
        var literal = ReadIntegerLiteralExpression(ability, condition.RightExpressionId!);
        if (canonicalCards is null)
        {
            throw new CanonicalAbilityExecutionException(
                "CANONICAL_CARD_STATS_REQUIRED",
                "Canonical target filters require canonical card-stat authority.");
        }

        var card = state.GetCardInstance(candidate.CardInstanceId);
        var value = field.FieldId switch
        {
            "entity_max_hp" => CanonicalVitals.GetEffectiveMaxHp(state, card, canonicalCards),
            "card_magnitude" => canonicalCards.DefinitionsById.TryGetValue(card.CardId, out var definition)
                && string.Equals(definition.Status, ActiveStatus, StringComparison.Ordinal)
                    ? definition.Magnitude
                    : throw new EngineStateException(
                        "CANONICAL_CARD_STATS_INVALID",
                        "Card magnitude requires an active canonical card definition."),
            _ => throw Unsupported("Target filter field is outside numeric field authority v1."),
        };
        return condition.ComparisonOperatorId switch
        {
            "op_less_than" => value < literal.LiteralNumber,
            "op_less_than_or_equal" => value <= literal.LiteralNumber,
            "op_equal" => value == literal.LiteralNumber,
            "op_greater_than_or_equal" => value >= literal.LiteralNumber,
            "op_greater_than" => value > literal.LiteralNumber,
            _ => throw Unsupported("Target filter comparator is unsupported."),
        };
    }

    private static CanonicalAbilityExpressionDefinition ReadNumericFieldExpression(
        CanonicalAbilityDefinition ability,
        string expressionId)
    {
        var expression = ability.Expressions.SingleOrDefault(item => string.Equals(
            item.ExpressionId,
            expressionId,
            StringComparison.Ordinal));
        if (expression is null
            || !string.Equals(expression.Status, ActiveStatus, StringComparison.Ordinal)
            || expression.ParentExpressionId is not null
            || !string.Equals(expression.ExpressionKindId, "field_reference", StringComparison.Ordinal)
            || !string.Equals(expression.ReferenceTypeId, "ref_target_candidate_card", StringComparison.Ordinal)
            || expression.FieldId is not ("entity_max_hp" or "card_magnitude")
            || expression.OperatorId is not null
            || expression.AggregateTypeId is not null
            || expression.LiteralDataTypeId is not null
            || expression.LiteralNumber is not null
            || expression.LiteralText is not null
            || expression.LiteralRegistryValueId is not null
            || expression.TargetId is not null)
        {
            throw Unsupported("Target filter left expression is outside canonical field-reference v1.");
        }

        return expression;
    }

    private static CanonicalAbilityExpressionDefinition ReadIntegerLiteralExpression(
        CanonicalAbilityDefinition ability,
        string expressionId)
    {
        var expression = ability.Expressions.SingleOrDefault(item => string.Equals(
            item.ExpressionId,
            expressionId,
            StringComparison.Ordinal));
        if (expression is null
            || !string.Equals(expression.Status, ActiveStatus, StringComparison.Ordinal)
            || expression.ParentExpressionId is not null
            || !string.Equals(expression.ExpressionKindId, "literal", StringComparison.Ordinal)
            || !string.Equals(expression.LiteralDataTypeId, "integer", StringComparison.Ordinal)
            || expression.LiteralNumber is null
            || expression.OperatorId is not null
            || expression.ReferenceTypeId is not null
            || expression.FieldId is not null
            || expression.AggregateTypeId is not null
            || expression.LiteralText is not null
            || expression.LiteralRegistryValueId is not null
            || expression.TargetId is not null)
        {
            throw Unsupported("Target filter right expression is outside integer literal v1.");
        }

        return expression;
    }

    private static CanonicalAbilityExpressionDefinition ReadEffectiveKeywordFieldExpression(
        CanonicalAbilityDefinition ability,
        string expressionId)
    {
        var expression = ability.Expressions.SingleOrDefault(item => string.Equals(
            item.ExpressionId,
            expressionId,
            StringComparison.Ordinal));
        if (expression is null
            || !string.Equals(expression.Status, ActiveStatus, StringComparison.Ordinal)
            || expression.ParentExpressionId is not null
            || !string.Equals(expression.ExpressionKindId, "field_reference", StringComparison.Ordinal)
            || !string.Equals(expression.ReferenceTypeId, "ref_target_candidate_card", StringComparison.Ordinal)
            || !string.Equals(expression.FieldId, "card_effective_keywords", StringComparison.Ordinal)
            || expression.OperatorId is not null
            || expression.AggregateTypeId is not null
            || expression.LiteralDataTypeId is not null
            || expression.LiteralNumber is not null
            || expression.LiteralText is not null
            || expression.LiteralRegistryValueId is not null
            || expression.TargetId is not null)
        {
            throw Unsupported("Target filter left expression is outside effective-keyword field-reference v1.");
        }

        return expression;
    }

    private static CanonicalAbilityExpressionDefinition ReadKeywordLiteralExpression(
        CanonicalAbilityDefinition ability,
        string expressionId)
    {
        var expression = ability.Expressions.SingleOrDefault(item => string.Equals(
            item.ExpressionId,
            expressionId,
            StringComparison.Ordinal));
        if (expression is null
            || !string.Equals(expression.Status, ActiveStatus, StringComparison.Ordinal)
            || expression.ParentExpressionId is not null
            || !string.Equals(expression.ExpressionKindId, "literal", StringComparison.Ordinal)
            || !string.Equals(expression.LiteralDataTypeId, "string", StringComparison.Ordinal)
            || expression.LiteralRegistryValueId is null
            || expression.OperatorId is not null
            || expression.ReferenceTypeId is not null
            || expression.FieldId is not null
            || expression.AggregateTypeId is not null
            || expression.LiteralNumber is not null
            || expression.LiteralText is not null
            || expression.TargetId is not null)
        {
            throw Unsupported("Target filter right expression is outside keyword registry-literal v1.");
        }

        _ = CanonicalContinuousEffects.ResolveKeywordRegistryValue(expression.LiteralRegistryValueId);
        return expression;
    }

    private static CanonicalAbilityExecutionException Unsupported(string message) => new(
        "CANONICAL_TARGET_FILTER_UNSUPPORTED",
        message);
}
