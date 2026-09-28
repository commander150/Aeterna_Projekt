extends RefCounted


const PROTOCOL_VERSION = "aeterna-python-sidecar-protocol-v1"
const REQUEST_SCHEMA_VERSION = "aeterna-python-sidecar-request-v1"
const RESPONSE_SCHEMA_VERSION = "aeterna-python-sidecar-response-v1"
const STARTUP_SCHEMA_VERSION = "aeterna-python-sidecar-startup-v1"
const MAX_FRAME_SIZE = 8 * 1024 * 1024
const DEFAULT_TIMEOUT_MSEC = 10_000
const SUPPORTED_COMMANDS = [
	"health",
	"run_runtime_comparison_fixture",
	"shutdown",
]

const _REQUEST_FIELDS = [
	"schema_version",
	"protocol_version",
	"request_id",
	"command",
	"payload",
]
const _RESPONSE_FIELDS = [
	"schema_version",
	"protocol_version",
	"request_id",
	"command",
	"ok",
	"result",
	"error",
	"diagnostics",
]
const _ERROR_FIELDS = ["code", "category", "message", "retryable", "details"]
const _STARTUP_FIELDS = ["schema_version", "status", "protocol_version", "host", "port"]


static func build_request_frame(request_id: String, command: String, payload: Dictionary) -> Dictionary:
	if request_id.is_empty():
		return _failure("SIDECAR_REQUEST_ID_INVALID", "Sidecar request_id must be non-empty.")
	if not command in SUPPORTED_COMMANDS:
		return _failure("SIDECAR_COMMAND_UNSUPPORTED", "Sidecar command is not supported.")
	if command == "health" or command == "shutdown":
		if not payload.is_empty():
			return _failure("SIDECAR_PAYLOAD_INVALID", "This sidecar command requires an empty payload.")
	elif command == "run_runtime_comparison_fixture":
		if not _has_exact_fields(payload, ["fixture_path"]):
			return _failure("SIDECAR_FIXTURE_PAYLOAD_INVALID", "Fixture payload must contain only fixture_path.")
		if typeof(payload.get("fixture_path")) != TYPE_STRING or str(payload.get("fixture_path")).is_empty():
			return _failure("SIDECAR_FIXTURE_PAYLOAD_INVALID", "Fixture path must be a non-empty string.")

	var request := {
		"schema_version": REQUEST_SCHEMA_VERSION,
		"protocol_version": PROTOCOL_VERSION,
		"request_id": request_id,
		"command": command,
		"payload": payload.duplicate(true),
	}
	var body := JSON.stringify(request).to_utf8_buffer()
	if body.is_empty():
		return _failure("SIDECAR_FRAME_LENGTH_INVALID", "Sidecar frame body must not be empty.")
	if body.size() > MAX_FRAME_SIZE:
		return _failure("SIDECAR_FRAME_TOO_LARGE", "Sidecar frame exceeds the maximum size.")

	var frame := PackedByteArray()
	frame.resize(4)
	var body_size := body.size()
	frame[0] = (body_size >> 24) & 0xff
	frame[1] = (body_size >> 16) & 0xff
	frame[2] = (body_size >> 8) & 0xff
	frame[3] = body_size & 0xff
	frame.append_array(body)
	return {"ok": true, "frame": frame, "body": body}


static func decode_startup_line(raw_line: PackedByteArray) -> Dictionary:
	if raw_line.is_empty():
		return _failure("SIDECAR_STARTUP_MISSING", "Sidecar startup line is empty.")
	var text := raw_line.get_string_from_utf8()
	if text.to_utf8_buffer() != raw_line:
		return _failure("SIDECAR_STARTUP_UTF8_INVALID", "Sidecar startup line is not valid UTF-8.")
	var parser := JSON.new()
	if parser.parse(text, true) != OK:
		return _failure("SIDECAR_STARTUP_JSON_INVALID", "Sidecar startup line is not valid JSON.")
	if parser.get_parsed_text() != text or parser.get_parsed_text().to_utf8_buffer() != raw_line:
		return _failure("SIDECAR_STARTUP_TEXT_CHANGED", "Sidecar startup JSON text was not preserved.")
	var startup = parser.data
	if typeof(startup) != TYPE_DICTIONARY or not _has_exact_fields(startup, _STARTUP_FIELDS):
		return _failure("SIDECAR_STARTUP_SHAPE_INVALID", "Sidecar startup fields are invalid.")
	if startup.get("schema_version") != STARTUP_SCHEMA_VERSION:
		return _failure("SIDECAR_STARTUP_SCHEMA_UNSUPPORTED", "Sidecar startup schema is unsupported.")
	if startup.get("status") != "ready":
		return _failure("SIDECAR_STARTUP_STATUS_INVALID", "Sidecar startup status is not ready.")
	if startup.get("protocol_version") != PROTOCOL_VERSION:
		return _failure("SIDECAR_PROTOCOL_VERSION_UNSUPPORTED", "Sidecar protocol version is unsupported.")
	if startup.get("host") != "127.0.0.1":
		return _failure("SIDECAR_STARTUP_HOST_INVALID", "Sidecar startup host is not IPv4 loopback.")

	var port_value = startup.get("port")
	if typeof(port_value) != TYPE_INT and typeof(port_value) != TYPE_FLOAT:
		return _failure("SIDECAR_STARTUP_PORT_INVALID", "Sidecar startup port is not numeric.")
	var port_float := float(port_value)
	if not is_finite(port_float) or floor(port_float) != port_float:
		return _failure("SIDECAR_STARTUP_PORT_INVALID", "Sidecar startup port is not a finite integer value.")
	var port := int(port_float)
	if port < 1 or port > 65535:
		return _failure("SIDECAR_STARTUP_PORT_INVALID", "Sidecar startup port is outside the valid range.")
	return {
		"ok": true,
		"startup": startup,
		"raw_text": text,
		"raw_bytes": raw_line,
		"host": "127.0.0.1",
		"port": port,
		"port_projection": "finite_integral_transport_port_to_int",
	}


static func decode_response_body(
	raw_body: PackedByteArray,
	expected_request_id: String,
	expected_command: String
) -> Dictionary:
	if raw_body.is_empty():
		return _failure("SIDECAR_FRAME_LENGTH_INVALID", "Sidecar response body must not be empty.")
	if raw_body.size() > MAX_FRAME_SIZE:
		return _failure("SIDECAR_FRAME_TOO_LARGE", "Sidecar response exceeds the maximum size.")

	var raw_text := raw_body.get_string_from_utf8()
	var utf8_bytes_equal := raw_text.to_utf8_buffer() == raw_body
	if not utf8_bytes_equal:
		return _failure("SIDECAR_FRAME_UTF8_INVALID", "Sidecar response body is not valid UTF-8.")
	var parser := JSON.new()
	if parser.parse(raw_text, true) != OK:
		return _failure("SIDECAR_FRAME_JSON_INVALID", "Sidecar response body is not valid JSON.")
	var parsed_text_equal := parser.get_parsed_text() == raw_text
	var parsed_bytes_equal := parser.get_parsed_text().to_utf8_buffer() == raw_body
	if not parsed_text_equal or not parsed_bytes_equal:
		return _failure("SIDECAR_RESPONSE_RAW_TEXT_CHANGED", "Parsed sidecar response text differs from the received body.")

	var envelope = parser.data
	var envelope_check := validate_response_envelope(envelope, expected_request_id, expected_command)
	if not bool(envelope_check.get("ok", false)):
		return envelope_check
	var base64 := Marshalls.raw_to_base64(raw_body)
	var base64_roundtrip_equal := Marshalls.base64_to_raw(base64) == raw_body
	if not base64_roundtrip_equal:
		return _failure("SIDECAR_RESPONSE_BASE64_ROUNDTRIP_FAILED", "Sidecar response Base64 round-trip changed bytes.")
	return {
		"ok": true,
		"envelope": envelope,
		"raw_body_bytes": raw_body,
		"raw_body_text": raw_text,
		"raw_body_base64": base64,
		"raw_body_sha256": sha256_bytes(raw_body),
		"parsed_text_equal": parsed_text_equal,
		"utf8_bytes_equal": utf8_bytes_equal and parsed_bytes_equal,
		"base64_roundtrip_equal": base64_roundtrip_equal,
	}


static func validate_response_envelope(
	envelope,
	expected_request_id: String,
	expected_command: String
) -> Dictionary:
	if typeof(envelope) != TYPE_DICTIONARY or not _has_exact_fields(envelope, _RESPONSE_FIELDS):
		return _failure("SIDECAR_RESPONSE_SHAPE_INVALID", "Sidecar response fields are invalid.")
	if envelope.get("schema_version") != RESPONSE_SCHEMA_VERSION:
		return _failure("SIDECAR_RESPONSE_SCHEMA_UNSUPPORTED", "Sidecar response schema is unsupported.")
	if envelope.get("protocol_version") != PROTOCOL_VERSION:
		return _failure("SIDECAR_PROTOCOL_VERSION_UNSUPPORTED", "Sidecar response protocol is unsupported.")
	if typeof(envelope.get("request_id")) != TYPE_STRING or envelope.get("request_id") != expected_request_id:
		return _failure("SIDECAR_RESPONSE_REQUEST_ID_MISMATCH", "Sidecar response request_id does not match.")
	if typeof(envelope.get("command")) != TYPE_STRING or envelope.get("command") != expected_command:
		return _failure("SIDECAR_RESPONSE_COMMAND_MISMATCH", "Sidecar response command does not match.")
	if typeof(envelope.get("ok")) != TYPE_BOOL:
		return _failure("SIDECAR_RESPONSE_STATUS_INVALID", "Sidecar response ok field is not boolean.")
	var diagnostics = envelope.get("diagnostics")
	if typeof(diagnostics) != TYPE_ARRAY:
		return _failure("SIDECAR_RESPONSE_DIAGNOSTICS_INVALID", "Sidecar diagnostics is not an array.")
	for item in diagnostics:
		if typeof(item) != TYPE_DICTIONARY:
			return _failure("SIDECAR_RESPONSE_DIAGNOSTICS_INVALID", "Sidecar diagnostics contains a non-object value.")
	if bool(envelope.get("ok")):
		if typeof(envelope.get("result")) != TYPE_DICTIONARY or envelope.get("error") != null:
			return _failure("SIDECAR_RESPONSE_SUCCESS_INVALID", "Successful sidecar response shape is invalid.")
	else:
		if envelope.get("result") != null or not _valid_error_object(envelope.get("error")):
			return _failure("SIDECAR_RESPONSE_ERROR_INVALID", "Failed sidecar response shape is invalid.")
	return {"ok": true}


static func parse_frame_length(header: PackedByteArray) -> Dictionary:
	if header.size() != 4:
		return _failure("SIDECAR_FRAME_HEADER_INCOMPLETE", "Sidecar frame header must contain four bytes.")
	var length := (int(header[0]) << 24) | (int(header[1]) << 16) | (int(header[2]) << 8) | int(header[3])
	if length <= 0:
		return _failure("SIDECAR_FRAME_LENGTH_INVALID", "Sidecar frame length must be greater than zero.")
	if length > MAX_FRAME_SIZE:
		return _failure("SIDECAR_FRAME_TOO_LARGE", "Sidecar frame exceeds the maximum size.")
	return {"ok": true, "length": length}


static func sha256_bytes(value: PackedByteArray) -> String:
	var context := HashingContext.new()
	if context.start(HashingContext.HASH_SHA256) != OK:
		return ""
	if context.update(value) != OK:
		return ""
	return context.finish().hex_encode()


static func _valid_error_object(error) -> bool:
	return (
		typeof(error) == TYPE_DICTIONARY
		and _has_exact_fields(error, _ERROR_FIELDS)
		and typeof(error.get("code")) == TYPE_STRING
		and not str(error.get("code")).is_empty()
		and typeof(error.get("category")) == TYPE_STRING
		and typeof(error.get("message")) == TYPE_STRING
		and typeof(error.get("retryable")) == TYPE_BOOL
		and typeof(error.get("details")) == TYPE_DICTIONARY
	)


static func _has_exact_fields(value: Dictionary, fields: Array) -> bool:
	if value.size() != fields.size():
		return false
	for field in fields:
		if not value.has(field):
			return false
	return true


static func _failure(code: String, message: String) -> Dictionary:
	return {"ok": false, "code": code, "message": message}
