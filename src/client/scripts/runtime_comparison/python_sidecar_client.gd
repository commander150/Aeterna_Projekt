extends RefCounted


const Protocol = preload("res://scripts/runtime_comparison/python_sidecar_protocol.gd")

var _peer: StreamPeerTCP
var _state_mutex := Mutex.new()
var _active_operations := 0
var _close_requested := false


func connect_to_sidecar(host: String, port: int, timeout_msec: int = Protocol.DEFAULT_TIMEOUT_MSEC) -> Dictionary:
	if host != "127.0.0.1":
		return _failure("SIDECAR_CLIENT_HOST_NOT_ALLOWED", "Sidecar client accepts only IPv4 loopback.")
	if port < 1 or port > 65535:
		return _failure("SIDECAR_CLIENT_PORT_INVALID", "Sidecar client port is invalid.")
	var peer := StreamPeerTCP.new()
	if not _begin_connect_operation(peer):
		return _failure("SIDECAR_CLIENT_ALREADY_CONNECTED", "Sidecar client already owns a connection.")
	var connect_error := peer.connect_to_host(host, port)
	if connect_error != OK:
		_end_operation(peer, true)
		return _failure("SIDECAR_CLIENT_CONNECT_FAILED", "Could not begin sidecar TCP connection.")
	var deadline := Time.get_ticks_msec() + timeout_msec
	while Time.get_ticks_msec() <= deadline:
		if _operation_cancelled(peer):
			_end_operation(peer, true)
			return _cancelled_failure()
		peer.poll()
		if _operation_cancelled(peer):
			_end_operation(peer, true)
			return _cancelled_failure()
		var status := peer.get_status()
		if status == StreamPeerTCP.STATUS_CONNECTED:
			if _end_operation(peer, false):
				return _cancelled_failure()
			return {"ok": true}
		if status == StreamPeerTCP.STATUS_ERROR or status == StreamPeerTCP.STATUS_NONE:
			_end_operation(peer, true)
			return _failure("SIDECAR_CLIENT_CONNECT_FAILED", "Could not connect to the Python sidecar.")
		OS.delay_msec(1)
	var cancelled := _end_operation(peer, true)
	if cancelled:
		return _cancelled_failure()
	return _failure("SIDECAR_CLIENT_CONNECT_TIMEOUT", "Sidecar TCP connection timed out.")


func request(
	request_id: String,
	command: String,
	payload: Dictionary,
	timeout_msec: int = Protocol.DEFAULT_TIMEOUT_MSEC
) -> Dictionary:
	var begin_result := _begin_peer_operation()
	if not bool(begin_result.get("ok", false)):
		return begin_result
	var peer: StreamPeerTCP = begin_result["peer"]
	var frame_result := Protocol.build_request_frame(request_id, command, payload)
	if not bool(frame_result.get("ok", false)):
		return _finish_request(peer, frame_result)
	var send_result := _write_frame(peer, frame_result.get("frame", PackedByteArray()), timeout_msec)
	if not bool(send_result.get("ok", false)):
		return _finish_request(peer, send_result)
	var read_result := _read_frame(peer, timeout_msec)
	if not bool(read_result.get("ok", false)):
		return _finish_request(peer, read_result)
	var decode_result := Protocol.decode_response_body(
		read_result.get("raw_body_bytes", PackedByteArray()),
		request_id,
		command
	)
	return _finish_request(peer, decode_result)


func has_tcp_connection() -> bool:
	var begin_result := _begin_peer_operation()
	if not bool(begin_result.get("ok", false)):
		return false
	var peer: StreamPeerTCP = begin_result["peer"]
	if _operation_cancelled(peer):
		_end_operation(peer, false)
		return false
	peer.poll()
	var connected := (
		not _operation_cancelled(peer)
		and peer.get_status() == StreamPeerTCP.STATUS_CONNECTED
	)
	var cancelled := _end_operation(peer, false)
	return connected and not cancelled


func close() -> void:
	var peer_to_close: StreamPeerTCP
	_state_mutex.lock()
	if _peer != null:
		_close_requested = true
		if _active_operations == 0:
			peer_to_close = _peer
			_peer = null
			_close_requested = false
	_state_mutex.unlock()
	if peer_to_close != null:
		peer_to_close.disconnect_from_host()


func _write_frame(peer: StreamPeerTCP, frame: PackedByteArray, timeout_msec: int) -> Dictionary:
	var offset := 0
	var deadline := Time.get_ticks_msec() + timeout_msec
	while offset < frame.size() and Time.get_ticks_msec() <= deadline:
		if _operation_cancelled(peer):
			return _cancelled_failure()
		peer.poll()
		if _operation_cancelled(peer):
			return _cancelled_failure()
		if peer.get_status() != StreamPeerTCP.STATUS_CONNECTED:
			return _failure("SIDECAR_CONNECTION_CLOSED", "Connection closed while writing a sidecar frame.")
		var partial: Array = peer.put_partial_data(frame.slice(offset))
		if partial.size() != 2 or int(partial[0]) != OK:
			return _failure("SIDECAR_FRAME_WRITE_FAILED", "Sidecar frame write failed.")
		var written := int(partial[1])
		if written < 0 or written > frame.size() - offset:
			return _failure("SIDECAR_FRAME_WRITE_FAILED", "Sidecar frame write returned an invalid byte count.")
		offset += written
		if written == 0:
			OS.delay_msec(1)
	if offset != frame.size():
		return _failure("SIDECAR_FRAME_WRITE_TIMEOUT", "Sidecar frame write timed out.")
	return {"ok": true, "bytes_written": offset}


func _read_frame(peer: StreamPeerTCP, timeout_msec: int) -> Dictionary:
	var header := PackedByteArray()
	var body := PackedByteArray()
	var expected_body_size := -1
	var deadline := Time.get_ticks_msec() + timeout_msec
	while Time.get_ticks_msec() <= deadline:
		if _operation_cancelled(peer):
			return _cancelled_failure()
		peer.poll()
		if _operation_cancelled(peer):
			return _cancelled_failure()
		var status := peer.get_status()
		if status != StreamPeerTCP.STATUS_CONNECTED:
			var code := (
				"SIDECAR_FRAME_HEADER_INCOMPLETE"
				if expected_body_size < 0
				else "SIDECAR_FRAME_BODY_INCOMPLETE"
			)
			return _failure(code, "Connection closed before a complete sidecar frame was received.")
		var available := peer.get_available_bytes()
		if available > 0:
			var needed := 4 - header.size() if expected_body_size < 0 else expected_body_size - body.size()
			var partial: Array = peer.get_partial_data(min(available, needed))
			if partial.size() != 2 or int(partial[0]) != OK:
				return _failure("SIDECAR_FRAME_READ_FAILED", "Sidecar frame read failed.")
			var chunk: PackedByteArray = partial[1]
			if chunk.is_empty():
				OS.delay_msec(1)
				continue
			if expected_body_size < 0:
				header.append_array(chunk)
				if header.size() == 4:
					var length_result := Protocol.parse_frame_length(header)
					if not bool(length_result.get("ok", false)):
						return length_result
					expected_body_size = int(length_result.get("length", -1))
			else:
				body.append_array(chunk)
				if body.size() == expected_body_size:
					return {"ok": true, "raw_body_bytes": body}
		else:
			OS.delay_msec(1)
	if _operation_cancelled(peer):
		return _cancelled_failure()
	return _failure("SIDECAR_FRAME_READ_TIMEOUT", "Sidecar frame read timed out.")


func _begin_connect_operation(peer: StreamPeerTCP) -> bool:
	_state_mutex.lock()
	var available := _peer == null
	if available:
		_peer = peer
		_close_requested = false
		_active_operations += 1
	_state_mutex.unlock()
	return available


func _begin_peer_operation() -> Dictionary:
	_state_mutex.lock()
	var peer := _peer
	var close_requested := _close_requested
	if peer != null and not close_requested:
		_active_operations += 1
	_state_mutex.unlock()
	if close_requested:
		return _cancelled_failure()
	if peer == null:
		return _failure("SIDECAR_CLIENT_NOT_CONNECTED", "Sidecar client is not connected.")
	return {"ok": true, "peer": peer}


func _operation_cancelled(peer: StreamPeerTCP) -> bool:
	_state_mutex.lock()
	var cancelled := _close_requested or _peer != peer
	_state_mutex.unlock()
	return cancelled


func _end_operation(peer: StreamPeerTCP, clear_peer: bool) -> bool:
	var peer_to_close: StreamPeerTCP
	_state_mutex.lock()
	var cancelled := _close_requested or _peer != peer
	_active_operations = maxi(0, _active_operations - 1)
	if _peer == peer and (clear_peer or _close_requested) and _active_operations == 0:
		peer_to_close = _peer
		_peer = null
		_close_requested = false
	_state_mutex.unlock()
	if peer_to_close != null:
		peer_to_close.disconnect_from_host()
	return cancelled


func _finish_request(peer: StreamPeerTCP, result: Dictionary) -> Dictionary:
	if _end_operation(peer, false):
		return _cancelled_failure()
	return result


func _cancelled_failure() -> Dictionary:
	return _failure("SIDECAR_REQUEST_CANCELLED", "Sidecar request was cancelled during connection cleanup.")


func _failure(code: String, message: String) -> Dictionary:
	return {"ok": false, "code": code, "message": message}
