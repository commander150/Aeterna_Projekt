using Aeterna.GodotRuntime.RuntimeComparison;
using Aeterna.RuntimeCandidate;
using Godot;

namespace Aeterna.GodotRuntime.DebugProof;

public partial class CsharpMinimalRuntimeProof : Control
{
	private Button _runButton = null!;
	private Button _clearButton = null!;
	private Label _environmentValue = null!;
	private Label _fixtureValue = null!;
	private Label _actualShaValue = null!;
	private Label _shaMatchValue = null!;
	private Label _elapsedValue = null!;
	private Label _finalResultValue = null!;
	private RichTextLabel _log = null!;

	public override void _Ready()
	{
		_runButton = GetNode<Button>("Margin/Content/Buttons/RunButton");
		_clearButton = GetNode<Button>("Margin/Content/Buttons/ClearButton");
		_environmentValue = GetNode<Label>("Margin/Content/Details/EnvironmentValue");
		_fixtureValue = GetNode<Label>("Margin/Content/Details/FixtureValue");
		_actualShaValue = GetNode<Label>("Margin/Content/Details/ActualShaValue");
		_shaMatchValue = GetNode<Label>("Margin/Content/Details/ShaMatchValue");
		_elapsedValue = GetNode<Label>("Margin/Content/Details/ElapsedValue");
		_finalResultValue = GetNode<Label>("Margin/Content/FinalResultValue");
		_log = GetNode<RichTextLabel>("Margin/Content/Log");

		_runButton.Pressed += RunProof;
		_clearButton.Pressed += ClearLog;
		_environmentValue.Text = $"Godot {Engine.GetVersionInfo()["string"].AsString()} | .NET {System.Environment.Version} | net8.0";
		_fixtureValue.Text = "minimal_draw_end_turn_v1";

		var automatedRuns = ReadPositiveIntArgument("--visual-smoke-runs", defaultValue: 0);
		if (automatedRuns > 0)
		{
			RunAutomatedProof(automatedRuns);
		}
	}

	private void RunProof()
	{
		_runButton.Disabled = true;
		try
		{
			var proof = CsharpRuntimeCandidateBridge.Run();
			ApplyProof(proof);
		}
		catch (Exception exception)
		{
			_actualShaValue.Text = "unavailable";
			_shaMatchValue.Text = "NO";
			_elapsedValue.Text = "unavailable";
			_finalResultValue.Text = "FINAL RESULT: FAIL";
			_log.AppendText($"FAIL | {exception.GetType().Name}: {exception.Message}\n");
		}
		finally
		{
			_runButton.Disabled = false;
		}
	}

	private void RunAutomatedProof(int runCount)
	{
		GodotProofResult? finalProof = null;
		var deterministic = true;
		string? firstSha = null;
		for (var index = 0; index < runCount; index++)
		{
			finalProof = CsharpRuntimeCandidateBridge.Run();
			firstSha ??= finalProof.Candidate.Sha256;
			deterministic &= string.Equals(firstSha, finalProof.Candidate.Sha256, StringComparison.Ordinal);
			ApplyProof(finalProof);
		}

		if (finalProof is null)
		{
			GetTree().Quit(1);
			return;
		}

		var summary = CsharpRuntimeCandidateBridge.BuildSummary(finalProof, runCount);
		summary["deterministic"] = deterministic;
		summary["ui_run_button_reenabled"] = !_runButton.Disabled;
		summary["visual_controls_resolved"] = true;
		GD.Print(CsharpRuntimeCandidateBridge.VisualProofPrefix + CanonicalJson.Compact(summary));
		GetTree().Quit(finalProof.ShaMatch && deterministic ? 0 : 1);
	}

	private void ApplyProof(GodotProofResult proof)
	{
		_actualShaValue.Text = proof.Candidate.Sha256;
		_shaMatchValue.Text = proof.ShaMatch ? "YES" : "NO";
		_elapsedValue.Text = $"{proof.ElapsedMilliseconds} ms";
		_finalResultValue.Text = proof.ShaMatch ? "FINAL RESULT: PASS" : "FINAL RESULT: FAIL";
		_log.AppendText(
			$"{DateTimeOffset.Now:HH:mm:ss} | SHA {proof.Candidate.Sha256} | "
			+ $"bytes {proof.Candidate.CanonicalByteCount} | {(proof.ShaMatch ? "PASS" : "FAIL")}\n");
	}

	private void ClearLog()
	{
		_log.Clear();
	}

	private static int ReadPositiveIntArgument(string option, int defaultValue)
	{
		foreach (var argument in OS.GetCmdlineUserArgs())
		{
			var prefix = option + "=";
			if (!argument.StartsWith(prefix, StringComparison.Ordinal))
			{
				continue;
			}

			return int.TryParse(argument[prefix.Length..], out var value) && value > 0
				? value
				: defaultValue;
		}

		return defaultValue;
	}
}
