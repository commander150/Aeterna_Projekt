extends Control


const ProofRunner = preload("res://scripts/runtime_comparison/python_sidecar_proof_runner.gd")

const STATUS_COLORS = {
	"NOT STARTED": Color("9aa0a6"),
	"RUNNING": Color("f2c14e"),
	"PASS": Color("63d297"),
	"FAIL": Color("ff6b6b"),
	"CANCELLED": Color("f0a35e"),
	"NOT CHECKED": Color("9aa0a6"),
}

@onready var _run_button: Button = %RunFullProofButton
@onready var _emergency_button: Button = %EmergencyShutdownButton
@onready var _clear_button: Button = %ClearLogButton
@onready var _python_path_label: Label = %PythonExecutablePath
@onready var _python_source_label: Label = %PythonExecutableSource
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


func _ready() -> void:
	_build_status_label_map()
	_runner = ProofRunner.new()
	add_child(_runner)
	_runner.lifecycle_status_changed.connect(_on_lifecycle_status_changed)
	_runner.log_message.connect(_append_log)
	_run_button.pressed.connect(_on_run_full_proof_pressed)
	_emergency_button.pressed.connect(_on_emergency_shutdown_pressed)
	_clear_button.pressed.connect(_on_clear_log_pressed)
	_emergency_button.disabled = true
	_expected_raw_sha_label.text = ProofRunner.EXPECTED_RAW_BODY_SHA256
	_reference_sha_label.text = ProofRunner.EXPECTED_RESULT_SHA256
	_reset_visual_state()
	_ensure_readable_window_size()


func _exit_tree() -> void:
	if _runner != null:
		_runner.cleanup_now()


func run_full_proof() -> Dictionary:
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
	_emergency_button.disabled = true
	_append_log("VISUAL PROOF RUN %d" % _run_count)
	var result: Dictionary = await _runner.run_full_proof()
	_apply_result(result)
	_running = false
	_run_button.disabled = false
	_emergency_button.disabled = true
	return result


func get_lifecycle_status(key: String) -> String:
	var label: Label = _status_labels.get(key)
	return label.text if label != null else ""


func get_run_count() -> int:
	return _run_count


func get_proof_runner():
	return _runner


func _on_run_full_proof_pressed() -> void:
	await run_full_proof()


func _on_emergency_shutdown_pressed() -> void:
	if not _running:
		return
	_emergency_button.disabled = true
	_runner.request_emergency_shutdown()
	_append_log("Emergency shutdown requested.")


func _on_clear_log_pressed() -> void:
	_log_text.clear()


func _on_lifecycle_status_changed(key: String, status: String, detail: String) -> void:
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
	_candidate_sha_label.text = str(
		result.get("candidate_canonical_result_sha256", "NOT CHECKED")
	)
	_candidate_method_label.text = str(
		result.get("candidate_sha_verification_method", "NOT CHECKED")
	)
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


func _append_log(message: String) -> void:
	_log_text.append_text("[%s] %s\n" % [Time.get_time_string_from_system(), message])


func _ensure_readable_window_size() -> void:
	var window := get_window()
	window.min_size = Vector2i(960, 700)
	if window.size.x < 1100 or window.size.y < 760:
		window.size = Vector2i(max(window.size.x, 1100), max(window.size.y, 760))


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
