extends SceneTree


const Protocol = preload("res://scripts/runtime_comparison/python_sidecar_protocol.gd")
const SidecarProcess = preload("res://scripts/runtime_comparison/python_sidecar_process.gd")
const SidecarClient = preload("res://scripts/runtime_comparison/python_sidecar_client.gd")

const PROOF_PREFIX = "AETERNA_GODOT_PYTHON_SIDECAR_PROOF_V1="
const PROOF_SCHEMA_VERSION = "aeterna-godot-python-sidecar-proof-v1"
const DEFAULT_FIXTURE_PATH = "minimal_draw_end_turn_v1/fixture.json"


func _init() -> void:
	var proof := _new_proof()
	var process = SidecarProcess.new()
	var client = SidecarClient.new()
	_run_proof(proof, process, client, _fixture_path_from_arguments())
	_finalize_lifecycle(proof, process, client)
	var proof_text := JSON.stringify(proof)
	print(PROOF_PREFIX + Marshalls.raw_to_base64(proof_text.to_utf8_buffer()))
	quit(0 if bool(proof.get("success", false)) else 1)


func _run_proof(proof: Dictionary, process, client, fixture_path: String) -> void:
	var start_result: Dictionary = process.start()
	proof["python_executable"] = process.python_executable
	proof["sidecar_pid"] = str(process.pid)
	if not _require_ok(proof, start_result, "startup"):
		return
	proof["startup_ok"] = true
	proof["host"] = str(start_result.get("host", ""))
	proof["port"] = str(start_result.get("port", ""))
	proof["startup_raw_text"] = str(start_result.get("startup_raw_text", ""))
	proof["port_projection"] = str(start_result.get("port_projection", ""))
	proof["pythonpath_restored"] = bool(start_result.get("pythonpath_restored", false))
	proof["bytecode_environment_restored"] = bool(start_result.get("bytecode_environment_restored", false))

	var connect_result: Dictionary = client.connect_to_sidecar(process.host, process.port)
	if not _require_ok(proof, connect_result, "tcp_connect"):
		return
	proof["tcp_connected"] = true

	var health: Dictionary = client.request("godot_req_0001_health", "health", {})
	if not _require_ok(proof, health, "health"):
		return
	var health_envelope: Dictionary = health.get("envelope", {})
	var health_result = health_envelope.get("result", {})
	if not bool(health_envelope.get("ok", false)) or typeof(health_result) != TYPE_DICTIONARY:
		_fail(proof, "health", "SIDECAR_HEALTH_RESPONSE_INVALID")
		return
	if health_result.get("status") != "ready" or health_result.get("protocol_version") != Protocol.PROTOCOL_VERSION:
		_fail(proof, "health", "SIDECAR_HEALTH_RESPONSE_INVALID")
		return
	proof["health_ok"] = true

	var fixture: Dictionary = client.request(
		"godot_req_0002_fixture",
		"run_runtime_comparison_fixture",
		{"fixture_path": fixture_path}
	)
	if not _require_ok(proof, fixture, "fixture"):
		return
	var fixture_envelope: Dictionary = fixture.get("envelope", {})
	if not bool(fixture_envelope.get("ok", false)):
		_fail(proof, "fixture", "SIDECAR_FIXTURE_RESPONSE_FAILED")
		return
	proof["fixture_ok"] = true
	proof["raw_fixture_response_body_base64"] = str(fixture.get("raw_body_base64", ""))
	proof["raw_fixture_response_body_sha256"] = str(fixture.get("raw_body_sha256", ""))
	proof["raw_fixture_response_body_bytes"] = str(fixture.get("raw_body_bytes", PackedByteArray()).size())
	proof["raw_fixture_text_equal"] = bool(fixture.get("parsed_text_equal", false))
	proof["raw_fixture_bytes_equal"] = bool(fixture.get("utf8_bytes_equal", false))
	proof["raw_fixture_base64_roundtrip_equal"] = bool(fixture.get("base64_roundtrip_equal", false))

	var shutdown: Dictionary = client.request("godot_req_0003_shutdown", "shutdown", {})
	if not _require_ok(proof, shutdown, "shutdown"):
		return
	var shutdown_envelope: Dictionary = shutdown.get("envelope", {})
	var shutdown_result = shutdown_envelope.get("result", {})
	if not bool(shutdown_envelope.get("ok", false)) or typeof(shutdown_result) != TYPE_DICTIONARY:
		_fail(proof, "shutdown", "SIDECAR_SHUTDOWN_RESPONSE_INVALID")
		return
	if shutdown_result.get("status") != "shutting_down":
		_fail(proof, "shutdown", "SIDECAR_SHUTDOWN_RESPONSE_INVALID")
		return
	proof["shutdown_ok"] = true
	client.close()

	var exit_result: Dictionary = process.wait_for_exit()
	if not _require_ok(proof, exit_result, "process_exit"):
		return
	proof["sidecar_exit_code"] = str(process.exit_code)
	proof["process_stopped"] = not process.is_running()
	proof["stdout_remainder_empty"] = process.stdout_remainder.is_empty()
	proof["stderr_empty"] = process.stderr_bytes.is_empty()
	proof["listener_check_requested"] = true
	proof["listener_closed"] = _listener_is_closed(process.host, process.port)


func _finalize_lifecycle(proof: Dictionary, process, client) -> void:
	if process.is_running() and client.has_tcp_connection() and not bool(proof.get("shutdown_ok", false)):
		client.request("godot_req_0003_shutdown", "shutdown", {}, 1_000)
	client.close()
	if process.is_running():
		var wait_result: Dictionary = process.wait_for_exit(1_000)
		if not bool(wait_result.get("ok", false)):
			process.force_stop()
	if process.pid > 0:
		proof["sidecar_pid"] = str(process.pid)
		proof["sidecar_exit_code"] = str(process.exit_code)
		proof["process_stopped"] = not process.is_running()
		proof["stdout_remainder_empty"] = process.stdout_remainder.is_empty()
		proof["stderr_empty"] = process.stderr_bytes.is_empty()
		proof["forced_kill_used"] = process.forced_kill_used
		proof["listener_check_requested"] = true
		if not process.host.is_empty() and process.port > 0:
			proof["listener_closed"] = _listener_is_closed(process.host, process.port)
	if bool(proof.get("failure_stage", "").is_empty()):
		var checks := [
			bool(proof.get("startup_ok", false)),
			bool(proof.get("pythonpath_restored", false)),
			bool(proof.get("bytecode_environment_restored", false)),
			bool(proof.get("tcp_connected", false)),
			bool(proof.get("health_ok", false)),
			bool(proof.get("fixture_ok", false)),
			bool(proof.get("shutdown_ok", false)),
			bool(proof.get("process_stopped", false)),
			bool(proof.get("listener_closed", false)),
			str(proof.get("sidecar_exit_code", "")) == "0",
			bool(proof.get("stdout_remainder_empty", false)),
			bool(proof.get("stderr_empty", false)),
			bool(proof.get("raw_fixture_text_equal", false)),
			bool(proof.get("raw_fixture_bytes_equal", false)),
			bool(proof.get("raw_fixture_base64_roundtrip_equal", false)),
			not bool(proof.get("forced_kill_used", true)),
		]
		if checks.all(func(value): return bool(value)):
			proof["success"] = true
		else:
			_fail(proof, "final_checks", "SIDECAR_PROOF_FINAL_CHECK_FAILED")


func _listener_is_closed(host: String, port: int) -> bool:
	var probe := StreamPeerTCP.new()
	if probe.connect_to_host(host, port) != OK:
		return true
	var deadline := Time.get_ticks_msec() + 500
	while Time.get_ticks_msec() <= deadline:
		probe.poll()
		var status := probe.get_status()
		if status == StreamPeerTCP.STATUS_CONNECTED:
			probe.disconnect_from_host()
			return false
		if status == StreamPeerTCP.STATUS_ERROR or status == StreamPeerTCP.STATUS_NONE:
			probe.disconnect_from_host()
			return true
		OS.delay_msec(1)
	probe.disconnect_from_host()
	return true


func _fixture_path_from_arguments() -> String:
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--fixture="):
			return argument.trim_prefix("--fixture=")
	return DEFAULT_FIXTURE_PATH


func _require_ok(proof: Dictionary, result: Dictionary, stage: String) -> bool:
	if bool(result.get("ok", false)):
		return true
	_fail(proof, stage, str(result.get("code", "SIDECAR_PROOF_STAGE_FAILED")))
	return false


func _fail(proof: Dictionary, stage: String, code: String) -> void:
	if str(proof.get("failure_stage", "")).is_empty():
		proof["failure_stage"] = stage
	var diagnostics: Array = proof.get("diagnostic_codes", [])
	if not code in diagnostics:
		diagnostics.append(code)
	proof["diagnostic_codes"] = diagnostics
	proof["success"] = false


func _new_proof() -> Dictionary:
	return {
		"schema_version": PROOF_SCHEMA_VERSION,
		"success": false,
		"protocol_version": Protocol.PROTOCOL_VERSION,
		"python_executable": "",
		"godot_pid": str(OS.get_process_id()),
		"sidecar_pid": "",
		"host": "",
		"port": "",
		"startup_ok": false,
		"startup_raw_text": "",
		"port_projection": "",
		"pythonpath_restored": false,
		"bytecode_environment_restored": false,
		"tcp_connected": false,
		"health_ok": false,
		"fixture_ok": false,
		"shutdown_ok": false,
		"process_stopped": false,
		"listener_check_requested": false,
		"listener_closed": false,
		"sidecar_exit_code": "",
		"stdout_remainder_empty": false,
		"stderr_empty": false,
		"forced_kill_used": false,
		"raw_fixture_response_body_base64": "",
		"raw_fixture_response_body_sha256": "",
		"raw_fixture_response_body_bytes": "",
		"raw_fixture_text_equal": false,
		"raw_fixture_bytes_equal": false,
		"raw_fixture_base64_roundtrip_equal": false,
		"failure_stage": "",
		"diagnostic_codes": [],
	}
