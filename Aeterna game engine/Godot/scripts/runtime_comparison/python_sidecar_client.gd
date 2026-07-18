extends RefCounted


const Protocol = preload("res://scripts/runtime_comparison/python_sidecar_protocol.gd")

var _peer: StreamPeerTCP


func connect_to_sidecar(host: String, port: int, timeout_msec: int = Protocol.DEFAULT_TIMEOUT_MSEC) -> Dictionary:
	if host != "127.0.0.1":
		return _failure("SIDECAR_CLIENT_HOST_NOT_ALLOWED", "Sidecar client accepts only IPv4 loopback.")
	if port < 1 or port > 65535:
		return _failure("SIDECAR_CLIENT_PORT_INVALID", "Sidecar client port is invalid.")
	_peer = StreamPeerTCP.new()
	var connect_error := _peer.connect_to_host(host, port)
	if connect_error != OK:
		_peer = null
		return _failure("SIDECAR_CLIENT_CONNECT_FAILED", "Could not begin sidecar TCP connection.")
	var deadline := Time.get_ticks_msec() + timeout_msec
	while Time.get_ticks_msec() <= deadline:
		_peer.poll()
		var status := _peer.get_status()
		if status == StreamPeerTCP.STATUS_CONNECTED:
			return {"ok": true}
		if status == StreamPeerTCP.STATUS_ERROR or status == StreamPeerTCP.STATUS_NONE:
			close()
			return _failure("SIDECAR_CLIENT_CONNECT_FAILED", "Could not connect to the Python sidecar.")
		OS.delay_msec(1)
	close()
	return _failure("SIDECAR_CLIENT_CONNECT_TIMEOUT", "Sidecar TCP connection timed out.")


func request(
	request_id: String,
	command: String,
	payload: Dictionary,
	timeout_msec: int = Protocol.DEFAULT_TIMEOUT_MSEC
) -> Dictionary:
	if not has_tcp_connection():
		return _failure("SIDECAR_CLIENT_NOT_CONNECTED", "Sidecar client is not connected.")
	var frame_result := Protocol.build_request_frame(request_id, command, payload)
	if not bool(frame_result.get("ok", false)):
		return frame_result
	var send_result := _write_frame(frame_result.get("frame", PackedByteArray()), timeout_msec)
	if not bool(send_result.get("ok", false)):
		return send_result
	var read_result := _read_frame(timeout_msec)
	if not bool(read_result.get("ok", false)):
		return read_result
	return Protocol.decode_response_body(
		read_result.get("raw_body_bytes", PackedByteArray()),
		request_id,
		command
	)


func has_tcp_connection() -> bool:
	if _peer == null:
		return false
	_peer.poll()
	return _peer.get_status() == StreamPeerTCP.STATUS_CONNECTED


func close() -> void:
	if _peer != null:
		_peer.disconnect_from_host()
		_peer = null


func _write_frame(frame: PackedByteArray, timeout_msec: int) -> Dictionary:
	var offset := 0
	var deadline := Time.get_ticks_msec() + timeout_msec
	while offset < frame.size() and Time.get_ticks_msec() <= deadline:
		_peer.poll()
		if _peer.get_status() != StreamPeerTCP.STATUS_CONNECTED:
			return _failure("SIDECAR_CONNECTION_CLOSED", "Connection closed while writing a sidecar frame.")
		var partial: Array = _peer.put_partial_data(frame.slice(offset))
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


func _read_frame(timeout_msec: int) -> Dictionary:
	var header := PackedByteArray()
	var body := PackedByteArray()
	var expected_body_size := -1
	var deadline := Time.get_ticks_msec() + timeout_msec
	while Time.get_ticks_msec() <= deadline:
		_peer.poll()
		var status := _peer.get_status()
		var available := _peer.get_available_bytes()
		if available > 0:
			var needed := 4 - header.size() if expected_body_size < 0 else expected_body_size - body.size()
			var partial: Array = _peer.get_partial_data(min(available, needed))
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
		elif status != StreamPeerTCP.STATUS_CONNECTED:
			var code := "SIDECAR_FRAME_HEADER_INCOMPLETE" if expected_body_size < 0 else "SIDECAR_FRAME_BODY_INCOMPLETE"
			return _failure(code, "Connection closed before a complete sidecar frame was received.")
		else:
			OS.delay_msec(1)
	return _failure("SIDECAR_FRAME_READ_TIMEOUT", "Sidecar frame read timed out.")


func _failure(code: String, message: String) -> Dictionary:
	return {"ok": false, "code": code, "message": message}
