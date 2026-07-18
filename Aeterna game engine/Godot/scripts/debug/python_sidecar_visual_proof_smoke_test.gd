extends SceneTree


const VisualProofScene = preload(
	"res://scenes/runtime_comparison/python_sidecar_visual_proof.tscn"
)
const PROOF_PREFIX = "AETERNA_GODOT_VISUAL_SIDECAR_PROOF_V1="

var _failed := false


func _init() -> void:
	call_deferred("_run")


func _run() -> void:
	print("Running AETERNA Python sidecar visual proof smoke test...")
	var visual = VisualProofScene.instantiate()
	root.add_child(visual)
	await process_frame
	_check_required_nodes(visual)
	_check_shared_transport(visual)

	var first: Dictionary = await visual.run_full_proof()
	_check_proof(first, visual, "visual_run_1")
	_print_proof(first, "visual_run_1")

	var second: Dictionary = await visual.run_full_proof()
	_check_proof(second, visual, "visual_run_2")
	_print_proof(second, "visual_run_2")

	_check_not_equal(first.get("sidecar_pid", ""), second.get("sidecar_pid", ""), "sidecar PID")
	_check_not_equal(first.get("port", ""), second.get("port", ""), "listener port")
	_check_equal(
		first.get("raw_fixture_response_body_sha256", ""),
		second.get("raw_fixture_response_body_sha256", ""),
		"raw SHA across runs"
	)
	_check_equal(
		first.get("candidate_canonical_result_sha256", ""),
		second.get("candidate_canonical_result_sha256", ""),
		"candidate SHA across runs"
	)
	_check_equal(visual.get_run_count(), 2, "visual run count")

	visual.queue_free()
	await process_frame
	if _failed:
		print("AETERNA Python sidecar visual proof smoke test: FAILED")
		quit(1)
		return
	print("AETERNA Python sidecar visual proof smoke test: OK")
	quit(0)


func _check_required_nodes(visual) -> void:
	var required := [
		"RunFullProofButton",
		"EmergencyShutdownButton",
		"ClearLogButton",
		"StatusGrid",
		"HashPanel",
		"LogText",
		"FinalResultLabel",
		"FailedAtLabel",
		"ErrorCodeLabel",
		"ErrorMessageLabel",
	]
	for node_name in required:
		if visual.find_child(node_name, true, false) == null:
			_fail("Required visual node is missing: %s" % node_name)


func _check_shared_transport(visual) -> void:
	var runner = visual.get_proof_runner()
	var expected := PackedStringArray([
		"res://scripts/runtime_comparison/python_sidecar_protocol.gd",
		"res://scripts/runtime_comparison/python_sidecar_client.gd",
		"res://scripts/runtime_comparison/python_sidecar_process.gd",
	])
	_check_equal(runner.shared_transport_paths(), expected, "shared transport paths")


func _check_proof(result: Dictionary, visual, label: String) -> void:
	_check_equal(result.get("success", false), true, "%s.success" % label)
	_check_equal(result.get("cancelled", true), false, "%s.cancelled" % label)
	_check_equal(
		result.get("protocol_version", ""),
		"aeterna-python-sidecar-protocol-v1",
		"%s.protocol_version" % label
	)
	_check_equal(result.get("python_executable_found", false), true, "%s.python found" % label)
	_check_equal(result.get("startup_ok", false), true, "%s.startup" % label)
	_check_equal(result.get("tcp_connected", false), true, "%s.tcp" % label)
	_check_equal(result.get("health_ok", false), true, "%s.health" % label)
	_check_equal(result.get("fixture_ok", false), true, "%s.fixture" % label)
	_check_equal(result.get("shutdown_ok", false), true, "%s.shutdown" % label)
	_check_equal(result.get("process_stopped", false), true, "%s.process stopped" % label)
	_check_equal(result.get("listener_closed", false), true, "%s.listener closed" % label)
	_check_equal(result.get("sidecar_exit_code", -1), 0, "%s.exit code" % label)
	_check_equal(result.get("stdout_remainder_empty", false), true, "%s.stdout" % label)
	_check_equal(result.get("stderr_empty", false), true, "%s.stderr" % label)
	_check_equal(result.get("forced_kill_used", true), false, "%s.forced kill" % label)
	_check_equal(
		result.get("raw_fixture_response_body_bytes", 0),
		130123,
		"%s.raw byte count" % label
	)
	_check_equal(
		result.get("raw_fixture_response_body_sha256", ""),
		"4ba84e68d98a629c46aeaf6f5eb5f262569233ce5acaf9652e3548038965486c",
		"%s.raw SHA" % label
	)
	_check_equal(result.get("raw_fixture_text_equal", false), true, "%s.raw text" % label)
	_check_equal(result.get("raw_fixture_bytes_equal", false), true, "%s.raw UTF-8" % label)
	_check_equal(
		result.get("raw_fixture_base64_roundtrip_equal", false),
		true,
		"%s.Base64 round-trip" % label
	)
	_check_equal(result.get("raw_response_bytes_preserved", false), true, "%s.raw proof" % label)
	_check_equal(
		result.get("reference_canonical_result_sha256", ""),
		"650053262681f79d354867793194a4e49e7862bcccf2475b8cbd34aa03bada6d",
		"%s.reference SHA" % label
	)
	_check_equal(
		result.get("candidate_canonical_result_sha256", ""),
		"650053262681f79d354867793194a4e49e7862bcccf2475b8cbd34aa03bada6d",
		"%s.candidate SHA" % label
	)
	_check_equal(
		result.get("candidate_sha_verification_method", ""),
		"verified through exact fixture response-body byte match",
		"%s.candidate SHA method" % label
	)
	_check_equal(
		result.get("fixture_result_reserialized", true),
		false,
		"%s.no fixture result reserialization" % label
	)
	_check_equal(
		visual.get_lifecycle_status("final_result"),
		"PASS",
		"%s.visual final status" % label
	)
	_check_equal(
		visual.get_node("%FinalResultLabel").text,
		"FINAL RESULT: PASS",
		"%s.final label" % label
	)


func _print_proof(result: Dictionary, run_label: String) -> void:
	var output := result.duplicate(true)
	output["run_label"] = run_label
	var encoded := Marshalls.raw_to_base64(JSON.stringify(output).to_utf8_buffer())
	print(PROOF_PREFIX + encoded)


func _check_equal(actual, expected, label: String) -> void:
	if actual != expected:
		_fail("%s expected %s, got %s" % [label, str(expected), str(actual)])


func _check_not_equal(first, second, label: String) -> void:
	if first == second or str(first).is_empty() or str(second).is_empty():
		_fail("%s must be non-empty and differ across runs." % label)


func _fail(message: String) -> void:
	_failed = true
	push_error(message)
