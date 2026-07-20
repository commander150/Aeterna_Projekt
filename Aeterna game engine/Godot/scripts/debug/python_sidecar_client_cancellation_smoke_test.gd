extends SceneTree


const SidecarClient = preload(
	"res://scripts/runtime_comparison/python_sidecar_client.gd"
)

var _failed := false
var _next_probe_port := 62_300


func _init() -> void:
	call_deferred("_run")


func _run() -> void:
	print("Running AETERNA Python sidecar client cancellation smoke test...")
	await _check_intentional_cancellation()
	await _check_unexpected_peer_close()
	if _failed:
		print("AETERNA Python sidecar client cancellation smoke test: FAILED")
		quit(1)
		return
	print("AETERNA Python sidecar client cancellation smoke test: OK")
	quit(0)


func _check_intentional_cancellation() -> void:
	var connection := _open_probe_connection()
	if connection.is_empty():
		return
	var client = connection["client"]
	var server: TCPServer = connection["server"]
	var server_peer: StreamPeerTCP = connection["server_peer"]
	var worker := Thread.new()
	if worker.start(_request_without_response.bind(client)) != OK:
		_fail("Could not start the intentional-cancellation request worker.")
		_cleanup_probe(client, server_peer, server)
		return
	await create_timer(0.1).timeout
	client.close()
	var result = worker.wait_to_finish()
	_check_equal(typeof(result), TYPE_DICTIONARY, "intentional cancellation result type")
	if typeof(result) == TYPE_DICTIONARY:
		_check_equal(result.get("ok", true), false, "intentional cancellation ok")
		_check_equal(
			result.get("code", ""),
			"SIDECAR_REQUEST_CANCELLED",
			"intentional cancellation code"
		)
	_cleanup_probe(client, server_peer, server)


func _check_unexpected_peer_close() -> void:
	var connection := _open_probe_connection()
	if connection.is_empty():
		return
	var client = connection["client"]
	var server: TCPServer = connection["server"]
	var server_peer: StreamPeerTCP = connection["server_peer"]
	var worker := Thread.new()
	if worker.start(_request_without_response.bind(client)) != OK:
		_fail("Could not start the unexpected-close request worker.")
		_cleanup_probe(client, server_peer, server)
		return
	await create_timer(0.1).timeout
	server_peer.disconnect_from_host()
	var result = worker.wait_to_finish()
	_check_equal(typeof(result), TYPE_DICTIONARY, "unexpected close result type")
	if typeof(result) == TYPE_DICTIONARY:
		_check_equal(result.get("ok", true), false, "unexpected close ok")
		_check_equal(
			result.get("code", ""),
			"SIDECAR_FRAME_HEADER_INCOMPLETE",
			"unexpected close code"
		)
		_check_equal(
			result.get("code", "") == "SIDECAR_REQUEST_CANCELLED",
			false,
			"unexpected close is not cancellation"
		)
	_cleanup_probe(client, server_peer, server)


func _open_probe_connection() -> Dictionary:
	var server := TCPServer.new()
	var port := _listen_on_probe_port(server)
	if port <= 0:
		_fail("Could not open a loopback probe listener.")
		return {}
	var client = SidecarClient.new()
	var connect_result: Dictionary = client.connect_to_sidecar("127.0.0.1", port, 1_000)
	if not bool(connect_result.get("ok", false)):
		_fail("Could not connect the probe client: %s" % JSON.stringify(connect_result))
		server.stop()
		return {}
	var deadline := Time.get_ticks_msec() + 1_000
	while not server.is_connection_available() and Time.get_ticks_msec() < deadline:
		OS.delay_msec(1)
	var server_peer := server.take_connection()
	if server_peer == null:
		_fail("Probe listener did not accept the client connection.")
		client.close()
		server.stop()
		return {}
	return {
		"client": client,
		"server": server,
		"server_peer": server_peer,
	}


func _listen_on_probe_port(server: TCPServer) -> int:
	while _next_probe_port < 62_500:
		var candidate := _next_probe_port
		_next_probe_port += 1
		if server.listen(candidate, "127.0.0.1") == OK:
			return candidate
	return -1


func _request_without_response(client):
	return client.request("client_cancellation_smoke", "health", {}, 2_000)


func _cleanup_probe(client, server_peer: StreamPeerTCP, server: TCPServer) -> void:
	client.close()
	if server_peer != null:
		server_peer.disconnect_from_host()
	server.stop()


func _check_equal(actual, expected, label: String) -> void:
	if actual != expected:
		_fail("%s expected %s, got %s" % [label, str(expected), str(actual)])


func _fail(message: String) -> void:
	_failed = true
	push_error(message)
