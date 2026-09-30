namespace Aeterna.Engine.Headless;

public static class FixtureLocator
{
    private const string RelativeFixturePath =
        "tests/fixtures/runtime_comparison/minimal_draw_end_turn_v2/fixture.json";

    public static string LocateCanonicalFixture()
    {
        foreach (var start in new[] { Directory.GetCurrentDirectory(), AppContext.BaseDirectory })
        {
            var directory = new DirectoryInfo(Path.GetFullPath(start));
            while (directory is not null)
            {
                var direct = Path.Combine(directory.FullName, RelativeFixturePath);
                if (File.Exists(direct))
                {
                    return direct;
                }

                directory = directory.Parent;
            }
        }

        throw new FileNotFoundException("Canonical minimal runtime comparison fixture could not be located.");
    }
}
