extends Control


const ProofRunner = preload("res://scripts/runtime_comparison/python_sidecar_proof_runner.gd")
const VisualProofLog = preload("res://scripts/debug/python_sidecar_visual_proof_log.gd")
const VISUAL_PROOF_SCENE_PATH = (
	"res://scenes/runtime_comparison/python_sidecar_visual_proof.tscn"
)

const STATUS_COLORS = {
	"NOT STARTED": Color("9aa0a6"),
	"RUNNING": Color("f2c14e"),
	"PASS": Color("63d297"),
	"FAIL": Color("ff6b6b"),
	"CANCELLED": Color("f0a35e"),
	"NOT CHECKED": Color("9aa0a6"),
}

@onready var _run_button: Button = %RunFullProofButton
@onready var _f8_test_button: Button = %StartF8CancellationTestButton
@onready var _emergency_button: Button = %EmergencyShutdownButton
@onready var _clear_button: Button = %ClearLogButton
@onready var _f8_test_status_label: Label = %CancellationTestStatusLabel
@onready var _python_path_label: Label = %PythonExecutablePath
@onready var _python_source_label: Label = %PythonExecutableSource
@onready var _diagnostic_log_path_label: Label = %DiagnosticLogPath
@onready var _actual_raw_sha_label: Label = %ActualRawShaValue
@onready var _expected_raw_sha_label: Label = %ExpectedRawShaValue
@onready var _reference_sha_label: Label = %ReferenceResultShaValue
@onready var _candidate_sha_label: Label = %CandidateResultShaValue
@onready var _candidate_method_label: Label = %CandidateShaMethodValue
@onready var _log_text: RichTextLabel = %LogText
@onready var _final_result_label: Label = %FinalResultLabel
@onready var _failed_at_label: Label = %FailedAtLabel
@onready var _error_code_label: Label = %ErrorCodeLabel
@onready var _error_message_label: Label = %ErrorMessageLabel

var _runner
var _running := false
var _run_count := 0
var _status_labels := {}
var _file_log = VisualProofLog.new()


func _ready() -> void:
	_build_status_label_map()
	_runner = ProofRunner.new()
	add_child(_runner)
	_runner.lifecycle_status_changed.connect(_on_lifecycle_status_changed)
	_runner.log_message.connect(_append_log)
	_runner.cancellation_test_ready.connect(_on_cancellation_test_ready)
	_run_button.pressed.connect(_on_run_full_proof_pressed)
	_f8_test_button.pressed.connect(_on_start_f8_cancellation_test_pressed)
	_emergency_button.pressed.connect(_on_emergency_shutdown_pressed)
	_clear_button.pressed.connect(_on_clear_log_pressed)
	_emergency_button.disabled = true
	_expected_raw_sha_label.text = ProofRunner.EXPECTED_RAW_BODY_SHA256
	_reference_sha_label.text = ProofRunner.EXPECTED_RESULT_SHA256
	_diagnostic_log_path_label.text = VisualProofLog.LOG_RELATIVE_PATH
	_diagnostic_log_path_label.tooltip_text = VisualProofLog.LOG_RELATIVE_PATH
	_reset_visual_state()


func _exit_tree() -> void:
	var interrupted_run := _running and _file_log.is_open()
	var runtime_context: Dictionary = _runner.get_runtime_context() if _runner != null else {}
	if interrupted_run:
		_file_log.write_interruption_tombstone(runtime_context)
	var cleanup_summary := {}
	if _runner != null:
		cleanup_summary = _runner.cleanup_now()
	if interrupted_run:
		_file_log.finish_interrupted_cleanup(cleanup_summary)
	else:
		_file_log.close()


func run_full_proof() -> Dictionary:
	return await _run_visual_proof(0)


func run_f8_cancellation_test(
	hold_msec: int = ProofRunner.DEFAULT_CANCELLATION_HOLD_MSEC
) -> Dictionary:
	return await _run_visual_proof(hold_msec)


func _run_visual_proof(cancellation_hold_msec: int) -> Dictionary:
	if _running:
		return {
			"success": false,
			"error_code": "VISUAL_PROOF_ALREADY_RUNNING",
			"error_message": "A visual proof is already running.",
		}
	_running = true
	_run_count += 1
	_reset_visual_state()
	_run_button.disabled = true
	_f8_test_button.disabled = true
	_emergency_button.disabled = true
	var run_id := "visual-proof-%d-%d-%d" % [
		OS.get_process_id(),
		_run_count,
		Time.get_ticks_usec(),
	]
	var log_start: Dictionary = _file_log.begin(_run_count, VISUAL_PROOF_SCENE_PATH, run_id)
	if not bool(log_start.get("ok", false)):
		var log_failure := {
			"success": false,
			"cancelled": false,
			"failure_stage": "DIAGNOSTIC_LOG",
			"error_code": str(log_start.get("code", "VISUAL_PROOF_LOG_FAILED")),
			"error_message": str(log_start.get("message", "Could not start the proof log.")),
		}
		_apply_result(log_failure)
		_running = false
		_run_button.disabled = false
		_f8_test_button.disabled = false
		return log_failure
	var watchdog_result: Dictionary = _runner.configure_parent_watchdog(
		OS.get_process_id(),
		_file_log.absolute_path(),
		run_id
	)
	if not bool(watchdog_result.get("ok", false)):
		var watchdog_failure := {
			"success": false,
			"cancelled": false,
			"failure_stage": "PARENT_WATCHDOG",
			"error_code": str(watchdog_result.get("code", "SIDECAR_PARENT_WATCHDOG_FAILED")),
			"error_message": str(watchdog_result.get("message", "Parent watchdog setup failed.")),
		}
		_apply_result(watchdog_failure)
		_file_log.finish(watchdog_failure)
		_running = false
		_run_button.disabled = false
		_f8_test_button.disabled = false
		return watchdog_failure
	_append_log("VISUAL PROOF RUN %d" % _run_count)
	var result: Dictionary
	if cancellation_hold_msec > 0:
		result = await _runner.run_cancellation_test(cancellation_hold_msec)
	else:
		result = await _runner.run_full_proof()
	_apply_result(result)
	_file_log.finish(result)
	_running = false
	_run_button.disabled = false
	_f8_test_button.disabled = false
	_emergency_button.disabled = true
	return result


func get_lifecycle_status(key: String) -> String:
	var label: Label = _status_labels.get(key)
	return label.text if label != null else ""


func get_run_count() -> int:
	return _run_count


func get_proof_runner():
	return _runner


func get_diagnostic_log_path() -> String:
	return VisualProofLog.LOG_RELATIVE_PATH


func _on_run_full_proof_pressed() -> void:
	await run_full_proof()


func _on_start_f8_cancellation_test_pressed() -> void:
	await run_f8_cancellation_test()


func _on_emergency_shutdown_pressed() -> void:
	if not _running:
		return
	_emergency_button.disabled = true
	_runner.request_emergency_shutdown()
	_append_log("Emergency shutdown requested.")


func _on_clear_log_pressed() -> void:
	_log_text.clear()


func _on_cancellation_test_ready(context: Dictionary) -> void:
	var hold_seconds := ceili(float(context.get("hold_msec", 0)) / 1_000.0)
	_f8_test_status_label.text = "READY FOR F8 CANCELLATION TEST\nPRESS F8 NOW\nSidecar PID: %s | Port: %s\nMANUAL HOLD ACTIVE (%d seconds)" % [
		context.get("sidecar_pid", "unknown"),
		context.get("port", "unknown"),
		hold_seconds,
	]
	_f8_test_status_label.add_theme_color_override("font_color", STATUS_COLORS["RUNNING"])
	_file_log.write_cancellation_test_ready(context)


func _on_lifecycle_status_changed(key: String, status: String, detail: String) -> void:
	_file_log.write_lifecycle(key, status, detail)
	var label: Label = _status_labels.get(key)
	if label != null:
		label.text = status
		label.tooltip_text = detail
		label.add_theme_color_override(
			"font_color",
			STATUS_COLORS.get(status, Color.WHITE)
		)
	if key == "sidecar_process":
		_emergency_button.disabled = not _runner.has_active_sidecar_process()
	if key == "candidate_canonical_result_sha256" and status == ProofRunner.STATUS_PASS:
		_candidate_sha_label.text = ProofRunner.EXPECTED_RESULT_SHA256
		_candidate_sha_label.tooltip_text = _candidate_sha_label.text
		_candidate_method_label.text = detail
		_candidate_method_label.tooltip_text = detail
	if not detail.is_empty() and status != ProofRunner.STATUS_NOT_STARTED:
		_append_log("%s: %s | %s" % [key, status, detail])


func _apply_result(result: Dictionary) -> void:
	_python_path_label.text = str(result.get("python_executable", "NOT FOUND"))
	_python_path_label.tooltip_text = _python_path_label.text
	var executable_found := bool(result.get("python_executable_found", false))
	_python_source_label.text = "%s | %s" % [
		str(result.get("python_executable_source", "not resolved")),
		"FOUND" if executable_found else "NOT FOUND",
	]
	_actual_raw_sha_label.text = str(result.get("raw_fixture_response_body_sha256", "NOT CHECKED"))
	_expected_raw_sha_label.text = str(
		result.get("expected_raw_fixture_response_body_sha256", ProofRunner.EXPECTED_RAW_BODY_SHA256)
	)
	_reference_sha_label.text = str(
		result.get("reference_canonical_result_sha256", ProofRunner.EXPECTED_RESULT_SHA256)
	)
	var candidate_sha := str(result.get("candidate_canonical_result_sha256", ""))
	var candidate_method := str(result.get("candidate_sha_verification_method", ""))
	_candidate_sha_label.text = candidate_sha if not candidate_sha.is_empty() else "NOT CHECKED"
	_candidate_method_label.text = (
		candidate_method if not candidate_method.is_empty() else "NOT CHECKED"
	)
	_candidate_sha_label.tooltip_text = _candidate_sha_label.text
	_candidate_method_label.tooltip_text = _candidate_method_label.text
	if bool(result.get("success", false)):
		_final_result_label.text = "FINAL RESULT: PASS"
		_final_result_label.add_theme_color_override("font_color", STATUS_COLORS["PASS"])
		_failed_at_label.text = "FAILED AT: none"
		_error_code_label.text = "ERROR CODE: none"
		_error_message_label.text = "ERROR: none"
	elif bool(result.get("cancelled", false)):
		_final_result_label.text = "FINAL RESULT: CANCELLED"
		_final_result_label.add_theme_color_override("font_color", STATUS_COLORS["CANCELLED"])
		_failed_at_label.text = "FAILED AT: %s" % str(result.get("failure_stage", "CANCELLED"))
		_error_code_label.text = "ERROR CODE: %s" % str(result.get("error_code", ""))
		_error_message_label.text = "ERROR: %s" % str(result.get("error_message", ""))
	else:
		_final_result_label.text = "FINAL RESULT: FAIL"
		_final_result_label.add_theme_color_override("font_color", STATUS_COLORS["FAIL"])
		_failed_at_label.text = "FAILED AT: %s" % str(result.get("failure_stage", "UNKNOWN"))
		_error_code_label.text = "ERROR CODE: %s" % str(result.get("error_code", ""))
		_error_message_label.text = "ERROR: %s" % str(result.get("error_message", ""))


func _reset_visual_state() -> void:
	for label in _status_labels.values():
		label.text = ProofRunner.STATUS_NOT_STARTED
		label.tooltip_text = ""
		label.add_theme_color_override("font_color", STATUS_COLORS["NOT STARTED"])
	_python_path_label.text = "Not resolved"
	_python_source_label.text = "not resolved"
	_actual_raw_sha_label.text = "NOT CHECKED"
	_expected_raw_sha_label.text = ProofRunner.EXPECTED_RAW_BODY_SHA256
	_reference_sha_label.text = ProofRunner.EXPECTED_RESULT_SHA256
	_candidate_sha_label.text = "NOT CHECKED"
	_candidate_method_label.text = "NOT CHECKED"
	_final_result_label.text = "FINAL RESULT: NOT STARTED"
	_final_result_label.add_theme_color_override("font_color", STATUS_COLORS["NOT STARTED"])
	_failed_at_label.text = "FAILED AT: none"
	_error_code_label.text = "ERROR CODE: none"
	_error_message_label.text = "ERROR: none"
	_f8_test_status_label.text = "F8 cancellation test: NOT STARTED"
	_f8_test_status_label.add_theme_color_override("font_color", STATUS_COLORS["NOT STARTED"])


func _append_log(message: String) -> void:
	_log_text.append_text("[%s] %s\n" % [Time.get_time_string_from_system(), message])
	_file_log.write_message(message)


func _build_status_label_map() -> void:
	_status_labels = {
		"python_executable": %PythonExecutableStatus,
		"sidecar_process": %SidecarProcessStatus,
		"startup_handshake": %StartupHandshakeStatus,
		"tcp_connection": %TcpConnectionStatus,
		"protocol_version": %ProtocolVersionStatus,
		"health_request": %HealthRequestStatus,
		"fixture_request": %FixtureRequestStatus,
		"raw_response_byte_preservation": %RawPreservationStatus,
		"raw_response_byte_count": %RawByteCountStatus,
		"raw_response_sha256": %RawShaStatus,
		"expected_raw_response_sha256": %ExpectedRawShaStatus,
		"reference_canonical_result_sha256": %ReferenceResultShaStatus,
		"candidate_canonical_result_sha256": %CandidateResultShaStatus,
		"shutdown_response": %ShutdownResponseStatus,
		"sidecar_exit": %SidecarExitStatus,
		"listener_state": %ListenerStateStatus,
		"standard_output": %StandardOutputStatus,
		"standard_error": %StandardErrorStatus,
		"final_result": %FinalResultStatus,
	}
