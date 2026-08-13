using System.Collections.Immutable;

namespace Aeterna.Engine.Rules;

public static class CanonicalPhaseIds
{
    public const string Awakening = "awakening";
    public const string Infusion = "infusion";
    public const string Manifestation = "manifestation";
    public const string Incursion = "incursion";
    public const string Distribution = "distribution";

    internal const string LegacyMain = "main";

    public static ImmutableArray<string> Ordered { get; } =
    [
        Awakening,
        Infusion,
        Manifestation,
        Incursion,
        Distribution,
    ];

    internal static bool IsCanonical(string phaseId) =>
        Ordered.Contains(phaseId, StringComparer.Ordinal);

    internal static string Next(string phaseId) => phaseId switch
    {
        Awakening => Infusion,
        Infusion => Manifestation,
        Manifestation => Incursion,
        Incursion => Distribution,
        Distribution => Awakening,
        _ => throw new EngineStateException($"Unknown canonical phase ID: {phaseId}"),
    };
}
