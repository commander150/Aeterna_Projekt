extends RefCounted


const LOG_SCHEMA_VERSION = "aeterna-godot-visual-sidecar-proof-log-v1"
const LOG_RELATIVE_PATH = "TEMP/godot_visual_sidecar_proof_latest.log"
const LOG_GODOT_PATH = "res://../../TEMP/godot_visual_sidecar_proof_latest.log"

var _file: FileAccess
var _finished := false
var _run_id := ""
var _interruption_tombstone_written := false


func begin(run_number: int, scene_path: String, proof_run_id: String) -> Dictionary:
	close()
	_finished = false
	_run_id = proof_run_id
	_interruption_tombstone_written = false
	var resolved_absolute_path := ProjectSettings.globalize_path(LOG_GODOT_PATH).simplify_path()
	var directory_error := DirAccess.make_dir_recursive_absolute(
		resolved_absolute_path.get_base_dir()
	)
	if directory_error != OK and directory_error != ERR_ALREADY_EXISTS:
		return _failure("VISUAL_PROOF_LOG_DIRECTORY_FAILED", "Could not prepare the TEMP log directory.")
	_file = FileAccess.open(resolved_absolute_path, FileAccess.WRITE)
	if _file == null:
		return _failure("VISUAL_PROOF_LOG_OPEN_FAILED", "Could not open the visual proof log file.")
	_write_line("AETERNA GODOT VISUAL PYTHON SIDECAR PROOF LOG")
	_write_field("log_schema_version", LOG_SCHEMA_VERSION)
	_write_field("run_number", run_number)
	_write_field("run_id", proof_run_id)
	_write_field("started_at", Time.get_datetime_string_from_system(true))
	_write_field("godot_version", str(Engine.get_version_info().get("string", "")))
	_write_field("visual_proof_scene", scene_path)
	_write_field("godot_pid", OS.get_process_id())
	_write_field("log_path", LOG_RELATIVE_PATH)
	_write_line("")
	return {
		"ok": true,
		"path": resolved_absolute_path,
		"relative_path": LOG_RELATIVE_PATH,
	}


func write_lifecycle(key: String, status: String, detail: String) -> void:
	_write_line("%s | LIFECYCLE | %s | %s | %s" % [
		Time.get_datetime_string_from_system(true),
		key,
		status,
		detail,
	])


func write_message(message: String) -> void:
	_write_line("%s | MESSAGE | %s" % [Time.get_datetime_string_from_system(true), message])


func finish(result: Dictionary) -> void:
	if _file == null or _finished:
		return
	_write_line("")
	_write_line("PROOF SUMMARY")
	_write_field("python_executable_source", result.get("python_executable_source", ""))
	_write_field("python_executable", result.get("python_executable", ""))
	_write_field("sidecar_pid", result.get("sidecar_pid", ""))
	_write_field("host", result.get("host", ""))
	_write_field("port", result.get("port", ""))
	_write_field("health_ok", result.get("health_ok", false))
	_write_field("fixture_ok", result.get("fixture_ok", false))
	_write_field("raw_response_body_bytes", result.get("raw_fixture_response_body_bytes", 0))
	_write_field("actual_raw_sha256", result.get("raw_fixture_response_body_sha256", ""))
	_write_field("expected_raw_sha256", result.get("expected_raw_fixture_response_body_sha256", ""))
	_write_field("raw_text_equal", result.get("raw_fixture_text_equal", false))
	_write_field("utf8_bytes_equal", result.get("raw_fixture_bytes_equal", false))
	_write_field("base64_roundtrip_equal", result.get("raw_fixture_base64_roundtrip_equal", false))
	_write_field("reference_canonical_result_sha256", result.get("reference_canonical_result_sha256", ""))
	_write_field("candidate_canonical_result_sha256", result.get("candidate_canonical_result_sha256", ""))
	_write_field("candidate_sha_verification_method", result.get("candidate_sha_verification_method", ""))
	_write_field("shutdown_ok", result.get("shutdown_ok", false))
	_write_field("shutdown_response_received", result.get("shutdown_response_received", false))
	_write_field("sidecar_exit_code", result.get("sidecar_exit_code", -1))
	_write_field("process_stopped", result.get("process_stopped", false))
	_write_field("listener_closed", result.get("listener_closed", false))
	_write_field("stdout_remainder_empty", result.get("stdout_remainder_empty", false))
	_write_field("stderr_empty", result.get("stderr_empty", false))
	_write_field("forced_kill_used", result.get("forced_kill_used", false))
	var final_result := "PASS" if bool(result.get("success", false)) else (
		"CANCELLED" if bool(result.get("cancelled", false)) else "FAIL"
	)
	_write_field("FINAL RESULT", final_result)
	_write_field("FAILED AT", _nonempty_or(result.get("failure_stage", ""), "none"))
	_write_field("ERROR CODE", _nonempty_or(result.get("error_code", ""), "none"))
	_write_field("ERROR", _nonempty_or(result.get("error_message", ""), "none"))
	_write_field("finished_at", Time.get_datetime_string_from_system(true))
	_finished = true
	close()


func write_interruption_tombstone(context: Dictionary) -> bool:
	if _file == null or _finished or _interruption_tombstone_written:
		return false
	_interruption_tombstone_written = true
	_write_line("")
	_write_line("MESSAGE | SCENE EXIT REQUESTED")
	_write_line("MESSAGE | ACTIVE PROOF INTERRUPTED")
	_write_line("LIFECYCLE | final_result | CANCELLED | FINAL RESULT: CANCELLED")
	_write_line("")
	_write_line("INTERRUPTION SUMMARY")
	_write_field("run_id", _run_id)
	_write_field("interruption_origin", "godot_exit_callback")
	_write_field("interruption_reason", "scene_exit")
	_write_field("cleanup_requested", true)
	_write_field("godot_pid", OS.get_process_id())
	_write_field("sidecar_pid", _known_or_unknown(context.get("sidecar_pid", -1)))
	_write_field("host", _known_or_unknown(context.get("host", "")))
	_write_field("port", _known_or_unknown(context.get("port", -1)))
	_write_field("FINAL RESULT", "CANCELLED")
	_write_field("FAILED AT", "interrupted_by_scene_exit")
	_write_field("ERROR CODE", "USER_INTERRUPTED")
	_write_field("ERROR", "Visual proof was interrupted before completion.")
	_write_field("interrupted_at", Time.get_datetime_string_from_system(true))
	return true


func write_cancellation_test_ready(context: Dictionary) -> void:
	if _file == null or _finished:
		return
	_write_line("")
	_write_line("CANCELLATION TEST READY")
	_write_field("run_id", _run_id)
	_write_line("READY FOR F8 CANCELLATION TEST")
	_write_line("PRESS F8 NOW")
	_write_field("sidecar_pid", context.get("sidecar_pid", "unknown"))
	_write_field("host", context.get("host", "unknown"))
	_write_field("port", context.get("port", "unknown"))


func finish_interrupted_cleanup(summary: Dictionary) -> void:
	if _file == null or _finished:
		return
	_write_line("")
	_write_line("GODOT EXIT CLEANUP SUMMARY")
	for field_name in [
		"cleanup_requested",
		"graceful_shutdown_attempted",
		"graceful_shutdown_accepted",
		"active_connection_closed",
		"worker_joined",
		"worker_join_timed_out",
		"forced_kill_used",
		"process_stopped",
		"listener_closed",
		"sidecar_exit_code",
	]:
		_write_field(field_name, summary.get(field_name, "unavailable"))
	_write_field("finished_at", Time.get_datetime_string_from_system(true))
	_finished = true
	close()


func close() -> void:
	if _file != null:
		_file.flush()
		_file.close()
		_file = null


func is_open() -> bool:
	return _file != null


func absolute_path() -> String:
	return ProjectSettings.globalize_path(LOG_GODOT_PATH).simplify_path()


func run_id() -> String:
	return _run_id


func _write_field(field_name: String, value) -> void:
	_write_line("%s: %s" % [field_name, str(value)])


func _write_line(line: String) -> void:
	if _file == null:
		return
	_file.store_string(line + "\n")
	_file.flush()


func _failure(code: String, message: String) -> Dictionary:
	return {"ok": false, "code": code, "message": message}


func _nonempty_or(value, fallback: String) -> String:
	var text := str(value)
	return fallback if text.is_empty() else text


func _known_or_unknown(value) -> String:
	var text := str(value)
	return "unknown" if text.is_empty() or text in ["-1", "0"] else text
