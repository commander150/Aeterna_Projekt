namespace Aeterna.Engine.Headless;

public static class FixtureLocator
{
    private const string RelativeFixturePath =
        "runtime_comparison/fixtures/minimal_draw_end_turn_v1/fixture.json";

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

                var underEngine = Path.Combine(directory.FullName, "Aeterna game engine", RelativeFixturePath);
                if (File.Exists(underEngine))
                {
                    return underEngine;
                }

                directory = directory.Parent;
            }
        }

        throw new FileNotFoundException("Canonical minimal runtime comparison fixture could not be located.");
    }
}
