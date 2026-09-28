using System.Collections.Immutable;

namespace Aeterna.Engine.Rules;

internal sealed record AuraSourceCandidate(
    string CardInstanceId,
    string Realm,
    int ZoneIndex,
    string ActivityState);

internal sealed record AuraPaymentPreflightResult(
    string PlayerId,
    string CardInstanceId,
    string CardId,
    string CardType,
    string CardRealm,
    int PrintedAuraCost,
    int NormalizedPayableAuraCost,
    int EligibleSourceCount,
    bool PaymentPossible,
    string? SelectionMode,
    string? FailureReason,
    ImmutableArray<AuraSourceCandidate> EligibleSources,
    ImmutableArray<string> ForcedSourceInstanceIds);

internal sealed record AuraPaymentSelectionValidationResult(
    string PlayerId,
    string CardInstanceId,
    int RequiredSourceCount,
    string? SelectionMode,
    bool SelectionValid,
    string? FailureReason,
    ImmutableArray<string> ResolvedSourceInstanceIds);

internal sealed class AuraPaymentException : Exception
{
    internal AuraPaymentException(string code, string message, Exception? innerException = null)
        : base(message, innerException)
    {
        Code = code;
    }

    internal string Code { get; }
}
