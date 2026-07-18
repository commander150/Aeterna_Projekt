extends SceneTree


const VisualProofScene = preload(
	"res://scenes/runtime_comparison/python_sidecar_visual_proof.tscn"
)
const PROOF_PREFIX = "AETERNA_GODOT_VISUAL_SIDECAR_PROOF_V1="
const EXPECTED_RAW_SHA = "4ba84e68d98a629c46aeaf6f5eb5f262569233ce5acaf9652e3548038965486c"
const EXPECTED_CANONICAL_SHA = "650053262681f79d354867793194a4e49e7862bcccf2475b8cbd34aa03bada6d"
const EXPECTED_CANDIDATE_METHOD = "verified through exact fixture response-body byte match"
const EXPECTED_LOG_PATH = "TEMP/godot_visual_sidecar_proof_latest.log"

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
	await _check_layout(visual, Vector2i(800, 600))
	await _check_layout(visual, Vector2i(1152, 648))
	_check_diagnostic_log(visual)

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
		"StartF8CancellationTestButton",
		"EmergencyShutdownButton",
		"ClearLogButton",
		"CancellationTestStatusLabel",
		"ButtonRow",
		"BodyScroll",
		"StatusGrid",
		"HashPanel",
		"CandidateResultShaValue",
		"CandidateShaMethodValue",
		"DiagnosticLogPath",
		"LogText",
		"FinalPanel",
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
		EXPECTED_RAW_SHA,
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
		EXPECTED_CANONICAL_SHA,
		"%s.reference SHA" % label
	)
	_check_equal(
		result.get("candidate_canonical_result_sha256", ""),
		EXPECTED_CANONICAL_SHA,
		"%s.candidate SHA" % label
	)
	_check_equal(
		result.get("candidate_sha_verification_method", ""),
		EXPECTED_CANDIDATE_METHOD,
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
	_check_equal(
		visual.get_node("%CandidateResultShaValue").text,
		EXPECTED_CANONICAL_SHA,
		"%s.candidate SHA label" % label
	)
	_check_equal(
		visual.get_node("%CandidateShaMethodValue").text,
		EXPECTED_CANDIDATE_METHOD,
		"%s.candidate SHA method label" % label
	)
	_check_equal(
		visual.get_node("%BodyScroll").is_ancestor_of(
			visual.get_node("%CandidateResultShaValue")
		),
		true,
		"%s.candidate SHA is scroll-reachable" % label
	)


func _check_layout(visual, requested_size: Vector2i) -> void:
	var window: Window = visual.get_window()
	window.size = requested_size
	await process_frame
	await process_frame
	var actual_size := window.size
	_check_equal(actual_size, requested_size, "%s viewport size" % str(requested_size))
	var viewport_rect := Rect2(Vector2.ZERO, Vector2(actual_size))
	var final_panel: Control = visual.get_node("%FinalPanel")
	var button_row: Control = visual.get_node("%ButtonRow")
	var body_scroll: ScrollContainer = visual.get_node("%BodyScroll")
	_check_rect_inside(final_panel.get_global_rect(), viewport_rect, "FinalPanel", requested_size)
	_check_rect_inside(button_row.get_global_rect(), viewport_rect, "ButtonRow", requested_size)
	_check_rect_inside(body_scroll.get_global_rect(), viewport_rect, "BodyScroll", requested_size)
	_check_equal(final_panel.is_visible_in_tree(), true, "%s FinalPanel visible" % str(requested_size))
	_check_equal(button_row.is_visible_in_tree(), true, "%s ButtonRow visible" % str(requested_size))
	_check_equal(
		body_scroll.vertical_scroll_mode != ScrollContainer.SCROLL_MODE_DISABLED,
		true,
		"%s BodyScroll vertical mode" % str(requested_size)
	)
	_check_equal(
		body_scroll.get_v_scroll_bar().max_value > body_scroll.get_v_scroll_bar().page,
		true,
		"%s BodyScroll has scrollable vertical content" % str(requested_size)
	)
	for node_name in [
		"FinalResultLabel",
		"CandidateResultShaValue",
		"CandidateShaMethodValue",
		"DiagnosticLogPath",
	]:
		var important_label: Label = visual.get_node("%%%s" % node_name)
		_check_equal(
			important_label.size.x > 0.0 and important_label.size.y > 0.0,
			true,
			"%s %s has positive size" % [str(requested_size), node_name]
		)
	print(
		"AETERNA_VISUAL_LAYOUT_PROBE=%dx%d PASS final_bottom=%.1f viewport_bottom=%d" % [
			actual_size.x,
			actual_size.y,
			final_panel.get_global_rect().end.y,
			actual_size.y,
		]
	)


func _check_rect_inside(
	control_rect: Rect2,
	viewport_rect: Rect2,
	control_name: String,
	viewport_size: Vector2i
) -> void:
	var tolerance := 0.5
	var inside := (
		control_rect.size.x > 0.0
		and control_rect.size.y > 0.0
		and control_rect.position.x >= viewport_rect.position.x - tolerance
		and control_rect.position.y >= viewport_rect.position.y - tolerance
		and control_rect.end.x <= viewport_rect.end.x + tolerance
		and control_rect.end.y <= viewport_rect.end.y + tolerance
	)
	_check_equal(
		inside,
		true,
		"%s is inside %s (rect=%s)" % [control_name, str(viewport_size), str(control_rect)]
	)


func _check_diagnostic_log(visual) -> void:
	_check_equal(visual.get_diagnostic_log_path(), EXPECTED_LOG_PATH, "diagnostic log path")
	_check_equal(
		visual.get_node("%DiagnosticLogPath").text,
		EXPECTED_LOG_PATH,
		"diagnostic log path label"
	)
	var absolute_path := ProjectSettings.globalize_path("res://../../" + EXPECTED_LOG_PATH)
	if not FileAccess.file_exists(absolute_path):
		_fail("Diagnostic log is missing: %s" % absolute_path)
		return
	var bytes := FileAccess.get_file_as_bytes(absolute_path)
	var text := bytes.get_string_from_utf8()
	_check_equal(text.to_utf8_buffer(), bytes, "diagnostic log UTF-8 round-trip")
	if bytes.size() >= 3:
		_check_equal(
			bytes.slice(0, 3) == PackedByteArray([0xef, 0xbb, 0xbf]),
			false,
			"diagnostic log has no UTF-8 BOM"
		)
	for required_text in [
		"AETERNA GODOT VISUAL PYTHON SIDECAR PROOF LOG",
		"log_schema_version:",
		"run_id:",
		"started_at:",
		"godot_version: 4.7.1",
		"visual_proof_scene:",
		"python_executable_source:",
		"python_executable:",
		"godot_pid:",
		"sidecar_pid:",
		"host:",
		"port:",
		"LIFECYCLE",
		"health_ok: true",
		"fixture_ok: true",
		"raw_response_body_bytes: 130123",
		"actual_raw_sha256: %s" % EXPECTED_RAW_SHA,
		"expected_raw_sha256: %s" % EXPECTED_RAW_SHA,
		"raw_text_equal: true",
		"utf8_bytes_equal: true",
		"base64_roundtrip_equal: true",
		"reference_canonical_result_sha256: %s" % EXPECTED_CANONICAL_SHA,
		"candidate_canonical_result_sha256: %s" % EXPECTED_CANONICAL_SHA,
		"candidate_sha_verification_method: %s" % EXPECTED_CANDIDATE_METHOD,
		"shutdown_ok: true",
		"shutdown_response_received: true",
		"sidecar_exit_code: 0",
		"process_stopped: true",
		"listener_closed: true",
		"stdout_remainder_empty: true",
		"stderr_empty: true",
		"forced_kill_used: false",
		"FINAL RESULT: PASS",
		"FAILED AT: none",
		"ERROR CODE: none",
		"ERROR: none",
		"finished_at:",
	]:
		_check_equal(
			text.contains(required_text),
			true,
			"diagnostic log contains %s" % required_text
		)
	_check_equal(text.contains("PARENT WATCHDOG SUMMARY"), false, "normal proof has no watchdog tombstone")
	print("AETERNA_VISUAL_LOG_PROOF=PASS path=%s bytes=%d" % [EXPECTED_LOG_PATH, bytes.size()])


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
