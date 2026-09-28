using System.Text.Json.Nodes;
using Aeterna.Engine.Serialization;

var failures = new JsonArray();
var passed = 0;
foreach (var test in ProductionEngineTests.All)
{
    try
    {
        test.Body();
        passed += 1;
        Console.Out.WriteLine($"PASS {test.Name}");
    }
    catch (Exception exception)
    {
        failures.Add(new JsonObject
        {
            ["test"] = test.Name,
            ["exception_type"] = exception.GetType().FullName,
            ["message"] = exception.Message,
        });
        Console.Error.WriteLine($"FAIL {test.Name}: {exception.Message}");
    }
}

var summary = new JsonObject
{
    ["schema_version"] = "aeterna-csharp-production-tests-v1",
    ["passed"] = passed,
    ["failed"] = failures.Count,
    ["total"] = ProductionEngineTests.All.Count,
    ["failures"] = failures,
};
Console.Out.WriteLine("AETERNA_CSHARP_PRODUCTION_TESTS " + CanonicalJson.Compact(summary));
return failures.Count == 0 ? 0 : 1;
