namespace Aeterna.Engine.Rules;

internal sealed record MagnitudePreflightResult(
    string PlayerId,
    string CardInstanceId,
    string CardId,
    int RequiredMagnitude,
    int CurrentMagnitude,
    bool RequirementMet,
    string? FailureReason);

internal sealed class MagnitudePreflightException : Exception
{
    internal MagnitudePreflightException(string code, string message, Exception? innerException = null)
        : base(message, innerException)
    {
        Code = code;
    }

    internal string Code { get; }
}
