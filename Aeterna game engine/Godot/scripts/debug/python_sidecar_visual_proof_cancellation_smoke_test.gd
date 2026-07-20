extends SceneTree


const VisualProofScene = preload(
	"res://scenes/runtime_comparison/python_sidecar_visual_proof.tscn"
)
const LOG_PATH = "res://../../TEMP/godot_visual_sidecar_proof_latest.log"

var _failed := false
var _emergency_ready_context := {}


func _init() -> void:
	call_deferred("_run")


func _run() -> void:
	print("Running AETERNA Python sidecar visual cancellation smoke test...")
	var visual = VisualProofScene.instantiate()
	root.add_child(visual)
	await process_frame
	var mode := _requested_mode()
	var expected_runs := 0
	if mode in ["all", "timeout"]:
		expected_runs += 1
		var timeout_result: Dictionary = await visual.run_f8_cancellation_test(150)
		_check_cancelled_result(timeout_result, "hold timeout")
		_check_cancellation_log("hold timeout")
	if mode in ["all", "emergency"]:
		expected_runs += 1
		var runner = visual.get_proof_runner()
		runner.cancellation_test_ready.connect(
			_on_emergency_ready.bind(visual),
			CONNECT_ONE_SHOT
		)
		var emergency_result: Dictionary = await visual.run_f8_cancellation_test()
		_check_equal(
			_emergency_ready_context.get("hold_msec", 0),
			30_000,
			"manual cancellation hold"
		)
		_check_equal(
			visual.get_node("%CancellationTestStatusLabel").text.contains(
				"MANUAL HOLD ACTIVE (30 seconds)"
			),
			true,
			"manual hold status"
		)
		_check_cancelled_result(emergency_result, "emergency shutdown")
		_check_cancellation_log("emergency shutdown")
	if expected_runs == 0:
		_fail("Unknown visual cancellation smoke mode: %s" % mode)
	_check_equal(visual.get_run_count(), expected_runs, "visual cancellation run count")

	visual.queue_free()
	await process_frame
	if _failed:
		print("AETERNA Python sidecar visual cancellation smoke test: FAILED")
		quit(1)
		return
	print("AETERNA Python sidecar visual cancellation smoke test: OK")
	quit(0)


func _on_emergency_ready(context: Dictionary, visual) -> void:
	_emergency_ready_context = context.duplicate(true)
	visual.get_proof_runner().request_emergency_shutdown()


func _requested_mode() -> String:
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--mode="):
			return argument.trim_prefix("--mode=")
	return "all"


func _check_cancelled_result(result: Dictionary, label: String) -> void:
	_check_equal(result.get("success", true), false, "%s.success" % label)
	_check_equal(result.get("cancelled", false), true, "%s.cancelled" % label)
	_check_equal(
		result.get("error_code", ""),
		"VISUAL_PROOF_CANCELLED",
		"%s.error_code" % label
	)
	_check_equal(
		result.get("failure_stage", ""),
		"CANCELLATION_HOLD",
		"%s.failure_stage" % label
	)
	_check_equal(result.get("process_stopped", false), true, "%s.process stopped" % label)
	_check_equal(result.get("listener_closed", false), true, "%s.listener closed" % label)
	_check_equal(result.get("stderr_empty", false), true, "%s.stderr empty" % label)
	_check_equal(result.get("forced_kill_used", true), false, "%s.forced kill" % label)
	var sidecar_pid := int(result.get("sidecar_pid", -1))
	_check_equal(
		sidecar_pid > 0 and OS.is_process_running(sidecar_pid),
		false,
		"%s.orphan process" % label
	)


func _check_cancellation_log(label: String) -> void:
	var absolute_log_path := ProjectSettings.globalize_path(LOG_PATH)
	if not FileAccess.file_exists(absolute_log_path):
		_fail("%s diagnostic log is missing." % label)
		return
	var text := FileAccess.get_file_as_string(absolute_log_path)
	for required_text in [
		"FINAL RESULT: CANCELLED",
		"FAILED AT: CANCELLATION_HOLD",
		"ERROR CODE: VISUAL_PROOF_CANCELLED",
		"process_stopped: true",
		"listener_closed: true",
		"stderr_empty: true",
		"forced_kill_used: false",
		"finished_at:",
	]:
		_check_equal(
			text.contains(required_text),
			true,
			"%s log contains %s" % [label, required_text]
		)


func _check_equal(actual, expected, label: String) -> void:
	if actual != expected:
		_fail("%s expected %s, got %s" % [label, str(expected), str(actual)])


func _fail(message: String) -> void:
	_failed = true
	push_error(message)
