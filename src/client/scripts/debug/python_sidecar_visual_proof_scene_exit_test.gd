extends SceneTree


const VisualProofScene = preload(
	"res://scenes/runtime_comparison/python_sidecar_visual_proof.tscn"
)
const LOG_PATH = "res://../../TEMP/godot_visual_sidecar_proof_latest.log"

var _ready_context := {}
var _failed := false


func _init() -> void:
	call_deferred("_run")


func _run() -> void:
	var visual = VisualProofScene.instantiate()
	root.add_child(visual)
	await process_frame
	var runner = visual.get_proof_runner()
	runner.cancellation_test_ready.connect(_on_cancellation_test_ready)
	_start_cancellation_test(visual)
	var deadline := Time.get_ticks_msec() + 10_000
	while _ready_context.is_empty() and Time.get_ticks_msec() < deadline:
		await process_frame
	if _ready_context.is_empty():
		_fail("Cancellation test did not reach READY.")
		visual.queue_free()
		await process_frame
		_finish()
		return

	var sidecar_pid := int(_ready_context.get("sidecar_pid", -1))
	var host := str(_ready_context.get("host", ""))
	var port := int(_ready_context.get("port", -1))
	visual.queue_free()
	await process_frame
	await process_frame
	var stop_deadline := Time.get_ticks_msec() + 3_000
	while sidecar_pid > 0 and OS.is_process_running(sidecar_pid) and Time.get_ticks_msec() < stop_deadline:
		await create_timer(0.05).timeout
	var process_stopped := sidecar_pid > 0 and not OS.is_process_running(sidecar_pid)
	var listener_closed := _listener_is_closed(host, port)
	if not process_stopped:
		_fail("Scene-exit cleanup left the sidecar running.")
		if sidecar_pid > 0:
			OS.kill(sidecar_pid)
	if not listener_closed:
		_fail("Scene-exit cleanup left the listener open.")
	_check_log()
	print("AETERNA_SCENE_EXIT_CANCELLATION=%s" % JSON.stringify({
		"sidecar_pid": sidecar_pid,
		"host": host,
		"port": port,
		"process_stopped": process_stopped,
		"listener_closed": listener_closed,
	}))
	_finish()


func _start_cancellation_test(visual) -> void:
	await visual.run_f8_cancellation_test(30_000)


func _on_cancellation_test_ready(context: Dictionary) -> void:
	_ready_context = context.duplicate(true)


func _check_log() -> void:
	var absolute_path := ProjectSettings.globalize_path(LOG_PATH)
	if not FileAccess.file_exists(absolute_path):
		_fail("Scene-exit cancellation log is missing.")
		return
	var text := FileAccess.get_file_as_string(absolute_path)
	for required_text in [
		"MESSAGE | SCENE EXIT REQUESTED",
		"MESSAGE | ACTIVE PROOF INTERRUPTED",
		"LIFECYCLE | final_result | CANCELLED | FINAL RESULT: CANCELLED",
		"interruption_origin: godot_exit_callback",
		"interruption_reason: scene_exit",
		"cleanup_requested: true",
		"FINAL RESULT: CANCELLED",
		"FAILED AT: interrupted_by_scene_exit",
		"ERROR CODE: USER_INTERRUPTED",
		"GODOT EXIT CLEANUP SUMMARY",
		"process_stopped: true",
		"listener_closed: true",
		"finished_at:",
	]:
		if not text.contains(required_text):
			_fail("Scene-exit log is missing: %s" % required_text)
	if text.contains("PARENT WATCHDOG SUMMARY"):
		_fail("Controlled scene exit unexpectedly triggered the Python parent watchdog.")


func _listener_is_closed(host: String, port: int) -> bool:
	if host.is_empty() or port <= 0:
		return false
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
		if status in [StreamPeerTCP.STATUS_ERROR, StreamPeerTCP.STATUS_NONE]:
			probe.disconnect_from_host()
			return true
		OS.delay_msec(1)
	probe.disconnect_from_host()
	return true


func _fail(message: String) -> void:
	_failed = true
	push_error(message)


func _finish() -> void:
	print("AETERNA Python sidecar scene-exit cancellation test: %s" % ("FAILED" if _failed else "OK"))
	quit(1 if _failed else 0)
