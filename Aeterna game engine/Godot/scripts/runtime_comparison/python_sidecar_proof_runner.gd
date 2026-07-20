extends Node


signal lifecycle_status_changed(key: String, status: String, detail: String)
signal log_message(message: String)
signal proof_completed(result: Dictionary)
signal cancellation_test_ready(context: Dictionary)

const Protocol = preload("res://scripts/runtime_comparison/python_sidecar_protocol.gd")
const SidecarClient = preload("res://scripts/runtime_comparison/python_sidecar_client.gd")
const SidecarProcess = preload("res://scripts/runtime_comparison/python_sidecar_process.gd")

const PROOF_SCHEMA_VERSION = "aeterna-godot-python-sidecar-visual-proof-v1"
const DEFAULT_FIXTURE_PATH = "minimal_draw_end_turn_v1/fixture.json"
const LOCAL_CONFIG_PATH = "res://../../TEMP/godot_local_runtime_config.json"
const LOCAL_CONFIG_SCHEMA_VERSION = "aeterna-local-runtime-config-v1"
const EXPECTED_RAW_BODY_BYTES = 130_123
const EXPECTED_RAW_BODY_SHA256 = "4ba84e68d98a629c46aeaf6f5eb5f262569233ce5acaf9652e3548038965486c"
const EXPECTED_RESULT_SHA256 = "650053262681f79d354867793194a4e49e7862bcccf2475b8cbd34aa03bada6d"
const CANDIDATE_SHA_METHOD = "verified through exact fixture response-body byte match"
const EMERGENCY_WORKER_GRACE_MSEC = 1_000
const DEFAULT_CANCELLATION_HOLD_MSEC = 30_000
const EXIT_CLEANUP_WORKER_LIMIT_MSEC = 750

const STATUS_NOT_STARTED = "NOT STARTED"
const STATUS_RUNNING = "RUNNING"
const STATUS_PASS = "PASS"
const STATUS_FAIL = "FAIL"
const STATUS_CANCELLED = "CANCELLED"
const STATUS_NOT_CHECKED = "NOT CHECKED"

const STATUS_KEYS = [
	"python_executable",
	"sidecar_process",
	"startup_handshake",
	"tcp_connection",
	"protocol_version",
	"health_request",
	"fixture_request",
	"raw_response_byte_preservation",
	"raw_response_byte_count",
	"raw_response_sha256",
	"expected_raw_response_sha256",
	"reference_canonical_result_sha256",
	"candidate_canonical_result_sha256",
	"shutdown_response",
	"sidecar_exit",
	"listener_state",
	"standard_output",
	"standard_error",
	"final_result",
]

var active := false
var cancel_requested := false
var last_result := {}

var _proof := {}
var _sidecar_process
var _sidecar_client
var _worker_thread: Thread
var _worker_started_msec := 0
var _emergency_fallback_used := false
var _parent_watchdog_options := {}


func run_full_proof(
	fixture_path: String = DEFAULT_FIXTURE_PATH,
	cancellation_hold_msec: int = 0
) -> Dictionary:
	if active:
		return _standalone_failure(
			"PROOF_ALREADY_RUNNING",
			"A Python sidecar proof is already running."
		)
	active = true
	cancel_requested = false
	_emergency_fallback_used = false
	_sidecar_process = SidecarProcess.new()
	_sidecar_client = SidecarClient.new()
	_proof = _new_proof()
	_reset_statuses()
	_set_status("expected_raw_response_sha256", STATUS_PASS, EXPECTED_RAW_BODY_SHA256)
	_set_status("reference_canonical_result_sha256", STATUS_PASS, EXPECTED_RESULT_SHA256)

	_stage("RESOLVING PYTHON EXECUTABLE")
	_set_status("python_executable", STATUS_RUNNING, "Resolving executable.")
	var executable_result := resolve_python_executable()
	if not bool(executable_result.get("ok", false)):
		return await _finish_failure("PYTHON_EXECUTABLE", executable_result)
	_proof["python_executable"] = str(executable_result.get("path", ""))
	_proof["python_executable_source"] = str(executable_result.get("source", ""))
	_proof["python_executable_found"] = true
	_set_status(
		"python_executable",
		STATUS_PASS,
		"FOUND via %s" % _proof["python_executable_source"]
	)
	if _cancel_requested_now():
		return await _finish_cancelled("PYTHON_EXECUTABLE")

	_stage("STARTING SIDECAR")
	_set_status("sidecar_process", STATUS_RUNNING, "Starting Python sidecar.")
	_set_status("startup_handshake", STATUS_RUNNING, "WAITING FOR HANDSHAKE")
	var start_result = await _run_threaded(
		_start_process_with_environment.bind(_proof["python_executable"])
	)
	if _cancel_requested_now():
		return await _finish_cancelled("STARTUP_HANDSHAKE")
	if not bool(start_result.get("ok", false)):
		return await _finish_failure("STARTUP_HANDSHAKE", start_result)
	_proof["sidecar_pid"] = str(_sidecar_process.pid)
	_proof["host"] = str(start_result.get("host", ""))
	_proof["port"] = str(start_result.get("port", ""))
	_proof["startup_ok"] = true
	_proof["pythonpath_restored"] = bool(start_result.get("pythonpath_restored", false))
	_proof["bytecode_environment_restored"] = bool(
		start_result.get("bytecode_environment_restored", false)
	)
	_proof["python_executable_environment_restored"] = bool(
		start_result.get("python_executable_environment_restored", false)
	)
	_set_status("sidecar_process", STATUS_RUNNING, "PID %s" % _proof["sidecar_pid"])
	_set_status("startup_handshake", STATUS_PASS, "Startup handshake accepted.")

	_stage("CONNECTING TCP")
	_set_status("tcp_connection", STATUS_RUNNING, "Connecting to loopback listener.")
	var connect_result = await _run_threaded(
		_sidecar_client.connect_to_sidecar.bind(_sidecar_process.host, _sidecar_process.port)
	)
	if _cancel_requested_now():
		return await _finish_cancelled("TCP_CONNECT")
	if not bool(connect_result.get("ok", false)):
		return await _finish_failure("TCP_CONNECT", connect_result)
	_proof["tcp_connected"] = true
	_set_status("tcp_connection", STATUS_PASS, "%s:%s" % [_proof["host"], _proof["port"]])

	_stage("RUNNING HEALTH")
	_set_status("protocol_version", STATUS_RUNNING, "Checking protocol version.")
	_set_status("health_request", STATUS_RUNNING, "Sending health request.")
	var health = await _run_threaded(
		_sidecar_client.request.bind("godot_req_0001_health", "health", {})
	)
	if _cancel_requested_now():
		return await _finish_cancelled("HEALTH_RESPONSE")
	if not bool(health.get("ok", false)):
		return await _finish_failure("HEALTH_RESPONSE", health)
	var health_envelope = health.get("envelope", {})
	var health_result = health_envelope.get("result", {}) if typeof(health_envelope) == TYPE_DICTIONARY else {}
	if (
		typeof(health_envelope) != TYPE_DICTIONARY
		or not bool(health_envelope.get("ok", false))
		or typeof(health_result) != TYPE_DICTIONARY
		or health_result.get("status") != "ready"
		or health_result.get("protocol_version") != Protocol.PROTOCOL_VERSION
	):
		return await _finish_failure(
			"HEALTH_RESPONSE",
			_failure("SIDECAR_HEALTH_RESPONSE_INVALID", "Health response is invalid.")
		)
	_proof["health_ok"] = true
	_proof["protocol_version"] = Protocol.PROTOCOL_VERSION
	_set_status("protocol_version", STATUS_PASS, Protocol.PROTOCOL_VERSION)
	_set_status("health_request", STATUS_PASS, "Sidecar status is ready.")
	if cancellation_hold_msec > 0:
		return await _run_cancellation_hold(cancellation_hold_msec)

	_stage("RUNNING FIXTURE")
	_set_status("fixture_request", STATUS_RUNNING, fixture_path)
	var fixture = await _run_threaded(
		_sidecar_client.request.bind(
			"godot_req_0002_fixture",
			"run_runtime_comparison_fixture",
			{"fixture_path": fixture_path}
		)
	)
	if _cancel_requested_now():
		return await _finish_cancelled("FIXTURE_RESPONSE")
	if not bool(fixture.get("ok", false)):
		return await _finish_failure("FIXTURE_RESPONSE", fixture)
	var fixture_envelope = fixture.get("envelope", {})
	if typeof(fixture_envelope) != TYPE_DICTIONARY or not bool(fixture_envelope.get("ok", false)):
		return await _finish_failure(
			"FIXTURE_RESPONSE",
			_failure("SIDECAR_FIXTURE_RESPONSE_FAILED", "Fixture response was not successful.")
		)
	_proof["fixture_ok"] = true
	_set_status("fixture_request", STATUS_PASS, "Fixture response envelope accepted.")

	_stage("VERIFYING RAW BYTES")
	_set_status("raw_response_byte_preservation", STATUS_RUNNING, "Checking raw response bytes.")
	_set_status("raw_response_byte_count", STATUS_RUNNING, "Checking byte count.")
	_set_status("raw_response_sha256", STATUS_RUNNING, "Computing SHA-256 from received bytes.")
	var raw_bytes: PackedByteArray = fixture.get("raw_body_bytes", PackedByteArray())
	var raw_count := raw_bytes.size()
	var actual_raw_sha := Protocol.sha256_bytes(raw_bytes)
	var text_equal := bool(fixture.get("parsed_text_equal", false))
	var utf8_equal := bool(fixture.get("utf8_bytes_equal", false))
	var base64_equal := bool(fixture.get("base64_roundtrip_equal", false))
	var raw_bytes_preserved := (
		raw_count == EXPECTED_RAW_BODY_BYTES
		and actual_raw_sha == EXPECTED_RAW_BODY_SHA256
		and str(fixture.get("raw_body_sha256", "")) == actual_raw_sha
		and text_equal
		and utf8_equal
		and base64_equal
	)
	_proof["raw_fixture_response_body_bytes"] = raw_count
	_proof["raw_fixture_response_body_sha256"] = actual_raw_sha
	_proof["expected_raw_fixture_response_body_bytes"] = EXPECTED_RAW_BODY_BYTES
	_proof["expected_raw_fixture_response_body_sha256"] = EXPECTED_RAW_BODY_SHA256
	_proof["raw_fixture_text_equal"] = text_equal
	_proof["raw_fixture_bytes_equal"] = utf8_equal
	_proof["raw_fixture_base64_roundtrip_equal"] = base64_equal
	_proof["raw_response_bytes_preserved"] = raw_bytes_preserved
	_proof["fixture_result_reserialized"] = false
	_set_status(
		"raw_response_byte_count",
		STATUS_PASS if raw_count == EXPECTED_RAW_BODY_BYTES else STATUS_FAIL,
		"%d bytes" % raw_count
	)
	_set_status(
		"raw_response_sha256",
		STATUS_PASS if actual_raw_sha == EXPECTED_RAW_BODY_SHA256 else STATUS_FAIL,
		actual_raw_sha
	)
	_set_status(
		"raw_response_byte_preservation",
		STATUS_PASS if raw_bytes_preserved else STATUS_FAIL,
		"text=%s, utf8=%s, base64=%s" % [text_equal, utf8_equal, base64_equal]
	)
	if not raw_bytes_preserved:
		return await _finish_failure(
			"RAW_BYTE_VERIFICATION",
			_failure("SIDECAR_RAW_RESPONSE_MISMATCH", "Fixture response bytes do not match C.3B.1.")
		)
	_proof["reference_canonical_result_sha256"] = EXPECTED_RESULT_SHA256
	_proof["candidate_canonical_result_sha256"] = EXPECTED_RESULT_SHA256
	_proof["candidate_sha_verification_method"] = CANDIDATE_SHA_METHOD
	_set_status(
		"candidate_canonical_result_sha256",
		STATUS_PASS,
		CANDIDATE_SHA_METHOD
	)

	_stage("REQUESTING SHUTDOWN")
	_set_status("shutdown_response", STATUS_RUNNING, "Sending graceful shutdown request.")
	var shutdown = await _run_threaded(
		_sidecar_client.request.bind("godot_req_0003_shutdown", "shutdown", {})
	)
	if _cancel_requested_now():
		return await _finish_cancelled("SHUTDOWN")
	if not bool(shutdown.get("ok", false)):
		return await _finish_failure("SHUTDOWN", shutdown)
	var shutdown_envelope = shutdown.get("envelope", {})
	var shutdown_result = (
		shutdown_envelope.get("result", {})
		if typeof(shutdown_envelope) == TYPE_DICTIONARY
		else {}
	)
	if (
		typeof(shutdown_envelope) != TYPE_DICTIONARY
		or not bool(shutdown_envelope.get("ok", false))
		or typeof(shutdown_result) != TYPE_DICTIONARY
		or shutdown_result.get("status") != "shutting_down"
	):
		return await _finish_failure(
			"SHUTDOWN",
			_failure("SIDECAR_SHUTDOWN_RESPONSE_INVALID", "Shutdown response is invalid.")
		)
	_proof["shutdown_ok"] = true
	_proof["shutdown_response_received"] = true
	_set_status("shutdown_response", STATUS_PASS, "Graceful shutdown accepted.")
	_sidecar_client.close()

	_stage("WAITING FOR PROCESS EXIT")
	_set_status("sidecar_exit", STATUS_RUNNING, "Waiting for exit code.")
	var exit_result = await _run_threaded(_sidecar_process.wait_for_exit)
	if _cancel_requested_now():
		return await _finish_cancelled("PROCESS_EXIT")
	if not bool(exit_result.get("ok", false)):
		return await _finish_failure("PROCESS_EXIT", exit_result)
	_update_process_output_proof()
	_set_status(
		"sidecar_exit",
		STATUS_PASS if _proof["sidecar_exit_code"] == 0 else STATUS_FAIL,
		"exit code %d" % _proof["sidecar_exit_code"]
	)
	_set_status(
		"sidecar_process",
		STATUS_PASS if bool(_proof["process_stopped"]) else STATUS_FAIL,
		"Process stopped."
	)
	_set_status(
		"standard_output",
		STATUS_PASS if bool(_proof["stdout_remainder_empty"]) else STATUS_FAIL,
		"Remainder empty: %s" % _proof["stdout_remainder_empty"]
	)
	_set_status(
		"standard_error",
		STATUS_PASS if bool(_proof["stderr_empty"]) else STATUS_FAIL,
		"Empty: %s" % _proof["stderr_empty"]
	)

	_stage("CHECKING LISTENER")
	_set_status("listener_state", STATUS_RUNNING, "Checking that the loopback listener is closed.")
	var listener_closed = await _run_threaded(
		_listener_is_closed.bind(_sidecar_process.host, _sidecar_process.port)
	)
	_proof["listener_closed"] = bool(listener_closed)
	_set_status(
		"listener_state",
		STATUS_PASS if bool(listener_closed) else STATUS_FAIL,
		"CLOSED" if bool(listener_closed) else "STILL LISTENING"
	)

	var final_checks := [
		bool(_proof.get("python_executable_found", false)),
		bool(_proof.get("startup_ok", false)),
		bool(_proof.get("pythonpath_restored", false)),
		bool(_proof.get("bytecode_environment_restored", false)),
		bool(_proof.get("python_executable_environment_restored", false)),
		bool(_proof.get("tcp_connected", false)),
		bool(_proof.get("health_ok", false)),
		bool(_proof.get("fixture_ok", false)),
		bool(_proof.get("raw_response_bytes_preserved", false)),
		bool(_proof.get("shutdown_ok", false)),
		bool(_proof.get("process_stopped", false)),
		bool(_proof.get("listener_closed", false)),
		int(_proof.get("sidecar_exit_code", -1)) == 0,
		bool(_proof.get("stdout_remainder_empty", false)),
		bool(_proof.get("stderr_empty", false)),
		not bool(_proof.get("forced_kill_used", true)),
	]
	if not final_checks.all(func(value): return bool(value)):
		return await _finish_failure(
			"FINAL_CHECKS",
			_failure("SIDECAR_VISUAL_PROOF_FINAL_CHECK_FAILED", "One or more final checks failed.")
		)

	_stage("COMPLETE")
	_proof["success"] = true
	_set_status("final_result", STATUS_PASS, "FINAL RESULT: PASS")
	return _complete()


func request_emergency_shutdown() -> void:
	if not active:
		return
	cancel_requested = true
	_proof["cancelled"] = true
	_log("Emergency shutdown requested; graceful cleanup will run at the next safe boundary.")


func run_cancellation_test(hold_msec: int = DEFAULT_CANCELLATION_HOLD_MSEC) -> Dictionary:
	if hold_msec <= 0:
		return _standalone_failure(
			"CANCELLATION_HOLD_INVALID",
			"Cancellation test hold must be a positive duration."
		)
	return await run_full_proof(DEFAULT_FIXTURE_PATH, hold_msec)


func configure_parent_watchdog(parent_pid: int, exit_log_path: String, run_id: String) -> Dictionary:
	if active:
		return _failure(
			"SIDECAR_PARENT_WATCHDOG_ALREADY_ACTIVE",
			"Parent watchdog must be configured before the proof starts."
		)
	if parent_pid <= 0 or exit_log_path.is_empty() or not exit_log_path.is_absolute_path():
		return _failure(
			"SIDECAR_PARENT_WATCHDOG_ARGUMENTS_INVALID",
			"Parent watchdog requires a positive PID and absolute exit log path."
		)
	if run_id.is_empty():
		return _failure("SIDECAR_PARENT_RUN_ID_INVALID", "Parent run ID must not be empty.")
	_parent_watchdog_options = {
		"parent_pid": parent_pid,
		"parent_exit_log": exit_log_path,
		"parent_run_id": run_id,
	}
	return {"ok": true}


func get_runtime_context() -> Dictionary:
	return {
		"godot_pid": OS.get_process_id(),
		"sidecar_pid": (
			_sidecar_process.pid
			if _sidecar_process != null and _sidecar_process.pid > 0
			else -1
		),
		"host": (
			_sidecar_process.host
			if _sidecar_process != null and not _sidecar_process.host.is_empty()
			else str(_proof.get("host", "unknown"))
		),
		"port": (
			_sidecar_process.port
			if _sidecar_process != null and _sidecar_process.port > 0
			else int(_proof.get("port", -1))
		),
	}


func has_active_sidecar_process() -> bool:
	return _sidecar_process != null and _sidecar_process.is_running()


func _run_cancellation_hold(hold_msec: int) -> Dictionary:
	_proof["cancellation_test_mode"] = true
	_proof["cancellation_test_ready"] = true
	var context := get_runtime_context()
	context["hold_msec"] = hold_msec
	_log("READY FOR F8 CANCELLATION TEST")
	_log("PRESS F8 NOW")
	_log("Sidecar PID: %s" % context["sidecar_pid"])
	_log("Port: %s" % context["port"])
	cancellation_test_ready.emit(context)
	var deadline := Time.get_ticks_msec() + hold_msec
	while not cancel_requested and Time.get_ticks_msec() < deadline:
		await get_tree().process_frame
	if not cancel_requested:
		request_emergency_shutdown()
	return await _finish_cancelled("CANCELLATION_HOLD")


func cleanup_now() -> Dictionary:
	var summary := {
		"cleanup_requested": true,
		"graceful_shutdown_attempted": false,
		"graceful_shutdown_accepted": false,
		"active_connection_closed": true,
		"worker_joined": true,
		"worker_join_timed_out": false,
		"forced_kill_used": false,
		"process_stopped": true,
		"listener_closed": true,
		"sidecar_exit_code": "unavailable",
	}
	if not active and (_sidecar_process == null or not _sidecar_process.is_running()):
		return summary
	cancel_requested = true
	if _worker_thread != null and _worker_thread.is_alive():
		if _sidecar_process != null and _sidecar_process.is_running():
			_sidecar_process.force_stop(500)
		var worker_deadline := Time.get_ticks_msec() + EXIT_CLEANUP_WORKER_LIMIT_MSEC
		while _worker_thread.is_alive() and Time.get_ticks_msec() < worker_deadline:
			OS.delay_msec(5)
		if _worker_thread.is_alive():
			summary["worker_joined"] = false
			summary["worker_join_timed_out"] = true
		else:
			_worker_thread.wait_to_finish()
			_worker_thread = null
	elif _sidecar_client != null and _sidecar_client.has_tcp_connection():
		summary["graceful_shutdown_attempted"] = true
		var shutdown_result: Dictionary = _sidecar_client.request(
			"visual_cleanup_shutdown",
			"shutdown",
			{},
			500
		)
		summary["graceful_shutdown_accepted"] = bool(shutdown_result.get("ok", false))
	if _sidecar_client != null:
		_sidecar_client.close()
	if _sidecar_process != null and _sidecar_process.pid > 0:
		var wait_result: Dictionary = _sidecar_process.wait_for_exit(500)
		if not bool(wait_result.get("ok", false)) and _sidecar_process.is_running():
			_sidecar_process.force_stop(500)
		if _sidecar_process.exit_code == -1 and not _sidecar_process.is_running():
			_sidecar_process.wait_for_exit(0)
		_update_process_output_proof()
		summary["forced_kill_used"] = _sidecar_process.forced_kill_used
		summary["process_stopped"] = not _sidecar_process.is_running()
		summary["sidecar_exit_code"] = (
			"unavailable" if _sidecar_process.exit_code == -1 else _sidecar_process.exit_code
		)
		if not _sidecar_process.host.is_empty() and _sidecar_process.port > 0:
			summary["listener_closed"] = _listener_is_closed(
				_sidecar_process.host,
				_sidecar_process.port
			)
	active = false
	return summary


func resolve_python_executable() -> Dictionary:
	if OS.has_environment("AETERNA_PYTHON_EXECUTABLE"):
		return _validate_python_executable(
			OS.get_environment("AETERNA_PYTHON_EXECUTABLE"),
			"environment"
		)
	var config_path := ProjectSettings.globalize_path(LOCAL_CONFIG_PATH).simplify_path()
	if not FileAccess.file_exists(config_path):
		return _failure(
			"VISUAL_PROOF_PYTHON_NOT_CONFIGURED",
			"Set AETERNA_PYTHON_EXECUTABLE or create %s." % config_path
		)
	var config_file := FileAccess.open(config_path, FileAccess.READ)
	if config_file == null:
		return _failure("VISUAL_PROOF_LOCAL_CONFIG_UNREADABLE", "Local runtime config cannot be read.")
	var parser := JSON.new()
	if parser.parse(config_file.get_as_text()) != OK or typeof(parser.data) != TYPE_DICTIONARY:
		return _failure("VISUAL_PROOF_LOCAL_CONFIG_INVALID", "Local runtime config is not valid JSON.")
	var config: Dictionary = parser.data
	if config.get("schema_version") != LOCAL_CONFIG_SCHEMA_VERSION:
		return _failure("VISUAL_PROOF_LOCAL_CONFIG_INVALID", "Local runtime config schema is unsupported.")
	return _validate_python_executable(str(config.get("python_executable", "")), "local_config")


func shared_transport_paths() -> PackedStringArray:
	return PackedStringArray([
		"res://scripts/runtime_comparison/python_sidecar_protocol.gd",
		"res://scripts/runtime_comparison/python_sidecar_client.gd",
		"res://scripts/runtime_comparison/python_sidecar_process.gd",
	])


func _run_threaded(callable: Callable):
	if _worker_thread != null:
		return _failure("VISUAL_PROOF_WORKER_BUSY", "A proof worker is already active.")
	_worker_thread = Thread.new()
	_worker_started_msec = Time.get_ticks_msec()
	var thread_error := _worker_thread.start(callable)
	if thread_error != OK:
		_worker_thread = null
		return _failure("VISUAL_PROOF_WORKER_START_FAILED", "Proof worker thread could not start.")
	while _worker_thread.is_alive():
		if (
			cancel_requested
			and not _emergency_fallback_used
			and Time.get_ticks_msec() - _worker_started_msec > EMERGENCY_WORKER_GRACE_MSEC
			and _sidecar_process != null
			and _sidecar_process.is_running()
		):
			_emergency_fallback_used = true
			_sidecar_process.force_stop(500)
		await get_tree().process_frame
	var result = _worker_thread.wait_to_finish()
	_worker_thread = null
	return result


func _start_process_with_environment(executable: String) -> Dictionary:
	var state := _capture_environment("AETERNA_PYTHON_EXECUTABLE")
	OS.set_environment("AETERNA_PYTHON_EXECUTABLE", executable)
	var result: Dictionary = _sidecar_process.start(
		Protocol.DEFAULT_TIMEOUT_MSEC,
		_parent_watchdog_options
	)
	_restore_environment("AETERNA_PYTHON_EXECUTABLE", state)
	result["python_executable_environment_restored"] = _environment_matches(
		"AETERNA_PYTHON_EXECUTABLE",
		state
	)
	return result


func _finish_failure(stage: String, result: Dictionary) -> Dictionary:
	_fail(stage, str(result.get("code", "VISUAL_PROOF_STAGE_FAILED")), str(result.get("message", "")))
	var status_key := _status_key_for_failure_stage(stage)
	if not status_key.is_empty():
		_set_status(status_key, STATUS_FAIL, str(result.get("message", "")))
	await _cleanup_after_run(false)
	_set_status("final_result", STATUS_FAIL, "FINAL RESULT: FAIL")
	return _complete()


func _finish_cancelled(stage: String) -> Dictionary:
	_proof["cancelled"] = true
	_proof["failure_stage"] = stage
	_proof["error_code"] = "VISUAL_PROOF_CANCELLED"
	_proof["error_message"] = "Proof cancelled by emergency shutdown."
	await _cleanup_after_run(true)
	for key in STATUS_KEYS:
		if str(_proof["lifecycle_statuses"].get(key, STATUS_NOT_STARTED)) in [STATUS_RUNNING, STATUS_NOT_STARTED]:
			_set_status(key, STATUS_CANCELLED, "Cancelled by user.")
	_set_status("final_result", STATUS_CANCELLED, "FINAL RESULT: CANCELLED")
	return _complete()


func _cleanup_after_run(cancelled: bool) -> void:
	if _sidecar_client != null and _sidecar_client.has_tcp_connection():
		if _sidecar_process != null and _sidecar_process.is_running():
			var shutdown = await _run_threaded(
				_sidecar_client.request.bind("visual_cleanup_shutdown", "shutdown", {}, 1_000)
			)
			if bool(shutdown.get("ok", false)):
				_proof["shutdown_response_received"] = true
			if bool(shutdown.get("ok", false)) and not cancelled:
				_proof["shutdown_ok"] = true
				_set_status("shutdown_response", STATUS_PASS, "Cleanup shutdown accepted.")
			elif bool(shutdown.get("ok", false)):
				_set_status("shutdown_response", STATUS_CANCELLED, "Cleanup shutdown accepted.")
		_sidecar_client.close()
	if _sidecar_process != null and _sidecar_process.pid > 0:
		if _sidecar_process.is_running():
			var wait_result = await _run_threaded(_sidecar_process.wait_for_exit.bind(1_000))
			if not bool(wait_result.get("ok", false)) and _sidecar_process.is_running():
				await _run_threaded(_sidecar_process.force_stop)
		elif _sidecar_process.exit_code == -1:
			_sidecar_process.wait_for_exit(0)
	_update_process_output_proof()
	if _sidecar_process != null and _sidecar_process.pid > 0:
		_set_status(
			"sidecar_process",
			STATUS_CANCELLED if cancelled else (STATUS_PASS if bool(_proof["process_stopped"]) else STATUS_FAIL),
			"Process stopped: %s" % _proof["process_stopped"]
		)
		_set_status(
			"sidecar_exit",
			STATUS_CANCELLED if cancelled else (STATUS_PASS if int(_proof["sidecar_exit_code"]) == 0 else STATUS_FAIL),
			"exit code %d" % int(_proof["sidecar_exit_code"])
		)
		_set_status(
			"standard_output",
			STATUS_PASS if bool(_proof["stdout_remainder_empty"]) else STATUS_FAIL,
			"Remainder empty: %s" % _proof["stdout_remainder_empty"]
		)
		_set_status(
			"standard_error",
			STATUS_PASS if bool(_proof["stderr_empty"]) else STATUS_FAIL,
			"Empty: %s" % _proof["stderr_empty"]
		)
	if _sidecar_process != null and not _sidecar_process.host.is_empty() and _sidecar_process.port > 0:
		_proof["listener_closed"] = bool(await _run_threaded(
			_listener_is_closed.bind(_sidecar_process.host, _sidecar_process.port)
		))
		_set_status(
			"listener_state",
			STATUS_PASS if bool(_proof["listener_closed"]) else STATUS_FAIL,
			"CLOSED" if bool(_proof["listener_closed"]) else "STILL LISTENING"
		)


func _listener_is_closed(host: String, port: int) -> bool:
	var probe = SidecarClient.new()
	var result: Dictionary = probe.connect_to_sidecar(host, port, 500)
	var closed := not bool(result.get("ok", false))
	probe.close()
	return closed


func _update_process_output_proof() -> void:
	if _sidecar_process == null:
		return
	_proof["sidecar_exit_code"] = _sidecar_process.exit_code
	_proof["process_stopped"] = not _sidecar_process.is_running()
	_proof["stdout_remainder_empty"] = _sidecar_process.stdout_remainder.is_empty()
	_proof["stderr_empty"] = _sidecar_process.stderr_bytes.is_empty()
	_proof["forced_kill_used"] = _sidecar_process.forced_kill_used or _emergency_fallback_used


func _complete() -> Dictionary:
	active = false
	last_result = _proof.duplicate(true)
	proof_completed.emit(last_result)
	return last_result


func _new_proof() -> Dictionary:
	return {
		"schema_version": PROOF_SCHEMA_VERSION,
		"success": false,
		"cancelled": false,
		"protocol_version": Protocol.PROTOCOL_VERSION,
		"python_executable": "",
		"python_executable_source": "",
		"python_executable_found": false,
		"godot_pid": str(OS.get_process_id()),
		"sidecar_pid": "",
		"host": "",
		"port": "",
		"startup_ok": false,
		"pythonpath_restored": false,
		"bytecode_environment_restored": false,
		"python_executable_environment_restored": false,
		"tcp_connected": false,
		"health_ok": false,
		"fixture_ok": false,
		"shutdown_ok": false,
		"shutdown_response_received": false,
		"process_stopped": false,
		"listener_closed": false,
		"sidecar_exit_code": -1,
		"stdout_remainder_empty": false,
		"stderr_empty": false,
		"forced_kill_used": false,
		"parent_watchdog_enabled": not _parent_watchdog_options.is_empty(),
		"cancellation_test_mode": false,
		"cancellation_test_ready": false,
		"raw_fixture_response_body_bytes": 0,
		"raw_fixture_response_body_sha256": "",
		"expected_raw_fixture_response_body_bytes": EXPECTED_RAW_BODY_BYTES,
		"expected_raw_fixture_response_body_sha256": EXPECTED_RAW_BODY_SHA256,
		"raw_fixture_text_equal": false,
		"raw_fixture_bytes_equal": false,
		"raw_fixture_base64_roundtrip_equal": false,
		"raw_response_bytes_preserved": false,
		"reference_canonical_result_sha256": EXPECTED_RESULT_SHA256,
		"candidate_canonical_result_sha256": "",
		"candidate_sha_verification_method": "",
		"fixture_result_reserialized": false,
		"failure_stage": "",
		"error_code": "",
		"error_message": "",
		"diagnostic_codes": [],
		"lifecycle_statuses": {},
		"lifecycle_events": [],
	}


func _reset_statuses() -> void:
	for key in STATUS_KEYS:
		_set_status(key, STATUS_NOT_STARTED, "")


func _set_status(key: String, status: String, detail: String) -> void:
	_proof["lifecycle_statuses"][key] = status
	_proof["lifecycle_events"].append({
		"key": key,
		"status": status,
		"detail": detail,
	})
	lifecycle_status_changed.emit(key, status, detail)


func _stage(message: String) -> void:
	_log(message)


func _log(message: String) -> void:
	log_message.emit(message)


func _fail(stage: String, code: String, message: String) -> void:
	if str(_proof.get("failure_stage", "")).is_empty():
		_proof["failure_stage"] = stage
		_proof["error_code"] = code
		_proof["error_message"] = message
	if not code in _proof["diagnostic_codes"]:
		_proof["diagnostic_codes"].append(code)
	_proof["success"] = false
	_log("FAILED AT: %s | %s | %s" % [stage, code, message])


func _cancel_requested_now() -> bool:
	return cancel_requested


func _status_key_for_failure_stage(stage: String) -> String:
	return {
		"PYTHON_EXECUTABLE": "python_executable",
		"STARTUP_HANDSHAKE": "startup_handshake",
		"TCP_CONNECT": "tcp_connection",
		"HEALTH_RESPONSE": "health_request",
		"FIXTURE_RESPONSE": "fixture_request",
		"RAW_BYTE_VERIFICATION": "raw_response_byte_preservation",
		"SHUTDOWN": "shutdown_response",
		"PROCESS_EXIT": "sidecar_exit",
		"FINAL_CHECKS": "final_result",
	}.get(stage, "")


func _validate_python_executable(path: String, source: String) -> Dictionary:
	if path.is_empty() or not path.is_absolute_path():
		return _failure("VISUAL_PROOF_PYTHON_INVALID", "Python executable must be an absolute path.")
	if not FileAccess.file_exists(path) or DirAccess.dir_exists_absolute(path):
		return _failure("VISUAL_PROOF_PYTHON_NOT_FOUND", "Python executable was not found.")
	return {"ok": true, "path": path, "source": source}


func _capture_environment(environment_name: String) -> Dictionary:
	return {
		"present": OS.has_environment(environment_name),
		"value": OS.get_environment(environment_name) if OS.has_environment(environment_name) else "",
	}


func _restore_environment(environment_name: String, state: Dictionary) -> void:
	if bool(state.get("present", false)):
		OS.set_environment(environment_name, str(state.get("value", "")))
	else:
		OS.unset_environment(environment_name)


func _environment_matches(environment_name: String, state: Dictionary) -> bool:
	var expected_present := bool(state.get("present", false))
	if OS.has_environment(environment_name) != expected_present:
		return false
	return not expected_present or OS.get_environment(environment_name) == str(state.get("value", ""))


func _failure(code: String, message: String) -> Dictionary:
	return {"ok": false, "code": code, "message": message}


func _standalone_failure(code: String, message: String) -> Dictionary:
	return {
		"schema_version": PROOF_SCHEMA_VERSION,
		"success": false,
		"cancelled": false,
		"error_code": code,
		"error_message": message,
	}
