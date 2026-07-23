using System.Collections.Immutable;

namespace Aeterna.Engine.Runtime;

public sealed record RuntimeLookupGroup(
    string LookupGroup,
    ImmutableDictionary<string, string> ActiveAliases)
{
    public ImmutableHashSet<string> CanonicalValues =>
        ActiveAliases.Values.ToImmutableHashSet(StringComparer.Ordinal);

    public bool TryResolve(string alias, out string canonicalValue)
    {
        if (ActiveAliases.TryGetValue(alias, out var resolved))
        {
            canonicalValue = resolved;
            return true;
        }

        canonicalValue = string.Empty;
        return false;
    }

    public bool ContainsCanonicalValue(string canonicalValue) =>
        ActiveAliases.Values.Contains(canonicalValue, StringComparer.Ordinal);
}

public sealed record RuntimeLookupCatalog(
    ImmutableDictionary<string, RuntimeLookupGroup> Groups)
{
    public bool TryResolve(string lookupGroup, string alias, out string canonicalValue)
    {
        if (Groups.TryGetValue(lookupGroup, out var group))
        {
            return group.TryResolve(alias, out canonicalValue);
        }

        canonicalValue = string.Empty;
        return false;
    }

    public bool ContainsCanonicalValue(string lookupGroup, string canonicalValue) =>
        Groups.TryGetValue(lookupGroup, out var group)
        && group.ContainsCanonicalValue(canonicalValue);
}
