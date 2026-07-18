"""Versioned loopback sidecar framing and envelope contracts."""

from __future__ import annotations

import json
import socket
import struct
from copy import deepcopy


PROTOCOL_VERSION = "aeterna-python-sidecar-protocol-v1"
REQUEST_SCHEMA_VERSION = "aeterna-python-sidecar-request-v1"
RESPONSE_SCHEMA_VERSION = "aeterna-python-sidecar-response-v1"
STARTUP_SCHEMA_VERSION = "aeterna-python-sidecar-startup-v1"
MAX_FRAME_SIZE = 8 * 1024 * 1024
DEFAULT_SOCKET_TIMEOUT = 10.0
SUPPORTED_COMMANDS = (
    "health",
    "run_runtime_comparison_fixture",
    "shutdown",
)

_REQUEST_FIELDS = {
    "schema_version",
    "protocol_version",
    "request_id",
    "command",
    "payload",
}
_RESPONSE_FIELDS = {
    "schema_version",
    "protocol_version",
    "request_id",
    "command",
    "ok",
    "result",
    "error",
    "diagnostics",
}
_ERROR_FIELDS = {"code", "category", "message", "retryable", "details"}
_STARTUP_FIELDS = {"schema_version", "status", "protocol_version", "host", "port"}


class SidecarProtocolError(Exception):
    """Stable transport or envelope failure without implementation details."""

    def __init__(self, code, message, *, category="protocol", retryable=False, details=None):
        self.code = str(code)
        self.message = str(message)
        self.category = str(category)
        self.retryable = bool(retryable)
        self.details = deepcopy(details or {})
        super().__init__("%s: %s" % (self.code, self.message))

    def to_error_object(self):
        return {
            "code": self.code,
            "category": self.category,
            "message": self.message,
            "retryable": self.retryable,
            "details": deepcopy(self.details),
        }


def compact_json_object_bytes(value):
    """Encode one JSON object to deterministic compact UTF-8 bytes."""

    if not isinstance(value, dict):
        raise SidecarProtocolError(
            "SIDECAR_FRAME_ROOT_INVALID",
            "Sidecar frame root must be a JSON object.",
        )
    try:
        text = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError):
        raise SidecarProtocolError(
            "SIDECAR_FRAME_JSON_INVALID",
            "Sidecar frame value is not JSON-compatible.",
        ) from None
    return text.encode("utf-8")


def encode_frame(value, *, max_frame_size=MAX_FRAME_SIZE):
    """Return a four-byte big-endian length prefix followed by JSON bytes."""

    payload = compact_json_object_bytes(value)
    if len(payload) == 0:
        raise SidecarProtocolError(
            "SIDECAR_FRAME_LENGTH_INVALID",
            "Sidecar frame length must be greater than zero.",
        )
    if len(payload) > max_frame_size:
        raise SidecarProtocolError(
            "SIDECAR_FRAME_TOO_LARGE",
            "Sidecar frame exceeds the configured maximum size.",
            details={"maximum_bytes": max_frame_size, "payload_bytes": len(payload)},
        )
    return struct.pack("!I", len(payload)) + payload


def send_frame(connection, value, *, max_frame_size=MAX_FRAME_SIZE):
    """Send exactly one encoded frame without mutating the input object."""

    frame = encode_frame(value, max_frame_size=max_frame_size)
    try:
        connection.sendall(frame)
    except socket.timeout:
        raise SidecarProtocolError(
            "SIDECAR_SOCKET_TIMEOUT",
            "Socket timed out while sending a sidecar frame.",
            retryable=True,
        ) from None
    except OSError:
        raise SidecarProtocolError(
            "SIDECAR_CONNECTION_CLOSED",
            "Connection closed while sending a sidecar frame.",
            retryable=True,
        ) from None


def read_frame(connection, *, max_frame_size=MAX_FRAME_SIZE):
    """Read one complete frame while tolerating partial socket reads."""

    header = _receive_exact(
        connection,
        4,
        incomplete_code="SIDECAR_FRAME_HEADER_INCOMPLETE",
        initial_close_code="SIDECAR_CONNECTION_CLOSED",
    )
    length = struct.unpack("!I", header)[0]
    if length <= 0:
        raise SidecarProtocolError(
            "SIDECAR_FRAME_LENGTH_INVALID",
            "Sidecar frame length must be greater than zero.",
        )
    if length > max_frame_size:
        raise SidecarProtocolError(
            "SIDECAR_FRAME_TOO_LARGE",
            "Sidecar frame exceeds the configured maximum size.",
            details={"maximum_bytes": max_frame_size, "payload_bytes": length},
        )
    payload = _receive_exact(
        connection,
        length,
        incomplete_code="SIDECAR_FRAME_BODY_INCOMPLETE",
        initial_close_code="SIDECAR_FRAME_BODY_INCOMPLETE",
    )
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError:
        raise SidecarProtocolError(
            "SIDECAR_FRAME_UTF8_INVALID",
            "Sidecar frame body is not valid UTF-8.",
        ) from None
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        raise SidecarProtocolError(
            "SIDECAR_FRAME_JSON_INVALID",
            "Sidecar frame body is not valid JSON.",
        ) from None
    if not isinstance(value, dict):
        raise SidecarProtocolError(
            "SIDECAR_FRAME_ROOT_INVALID",
            "Sidecar frame root must be a JSON object.",
        )
    return value


def build_request(request_id, command, payload=None):
    request = {
        "schema_version": REQUEST_SCHEMA_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "request_id": request_id,
        "command": command,
        "payload": deepcopy({} if payload is None else payload),
    }
    validate_request(request)
    return request


def validate_request(request):
    """Validate a complete request envelope and return it unchanged."""

    if not isinstance(request, dict) or set(request) != _REQUEST_FIELDS:
        raise SidecarProtocolError(
            "SIDECAR_REQUEST_SHAPE_INVALID",
            "Sidecar request fields do not match the request contract.",
            category="request_validation",
        )
    if request.get("schema_version") != REQUEST_SCHEMA_VERSION:
        raise SidecarProtocolError(
            "SIDECAR_REQUEST_SCHEMA_UNSUPPORTED",
            "Sidecar request schema_version is not supported.",
            category="request_validation",
        )
    if request.get("protocol_version") != PROTOCOL_VERSION:
        raise SidecarProtocolError(
            "SIDECAR_PROTOCOL_VERSION_UNSUPPORTED",
            "Sidecar protocol_version is not supported.",
            category="request_validation",
        )
    request_id = request.get("request_id")
    if not isinstance(request_id, str) or request_id == "":
        raise SidecarProtocolError(
            "SIDECAR_REQUEST_ID_INVALID",
            "Sidecar request_id must be a non-empty string.",
            category="request_validation",
        )
    command = request.get("command")
    if not isinstance(command, str) or command not in SUPPORTED_COMMANDS:
        raise SidecarProtocolError(
            "SIDECAR_COMMAND_UNSUPPORTED",
            "Sidecar command is not supported.",
            category="request_validation",
        )
    if not isinstance(request.get("payload"), dict):
        raise SidecarProtocolError(
            "SIDECAR_PAYLOAD_INVALID",
            "Sidecar request payload must be a JSON object.",
            category="request_validation",
        )
    return request


def build_success_response(request_id, command, result, diagnostics=None):
    response = {
        "schema_version": RESPONSE_SCHEMA_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "request_id": request_id,
        "command": command,
        "ok": True,
        "result": deepcopy(result),
        "error": None,
        "diagnostics": deepcopy([] if diagnostics is None else diagnostics),
    }
    validate_response(response)
    return response


def build_error_response(request_id, command, error, diagnostics=None):
    error_object = error.to_error_object() if isinstance(error, SidecarProtocolError) else error
    response = {
        "schema_version": RESPONSE_SCHEMA_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "request_id": request_id if isinstance(request_id, str) else "",
        "command": command if isinstance(command, str) else "unknown",
        "ok": False,
        "result": None,
        "error": deepcopy(error_object),
        "diagnostics": deepcopy([] if diagnostics is None else diagnostics),
    }
    validate_response(response)
    return response


def validate_response(response, *, expected_request_id=None, expected_command=None):
    """Validate a response envelope and optional correlation fields."""

    if not isinstance(response, dict) or set(response) != _RESPONSE_FIELDS:
        raise SidecarProtocolError(
            "SIDECAR_RESPONSE_SHAPE_INVALID",
            "Sidecar response fields do not match the response contract.",
            category="response_validation",
        )
    if response.get("schema_version") != RESPONSE_SCHEMA_VERSION:
        raise SidecarProtocolError(
            "SIDECAR_RESPONSE_SCHEMA_UNSUPPORTED",
            "Sidecar response schema_version is not supported.",
            category="response_validation",
        )
    if response.get("protocol_version") != PROTOCOL_VERSION:
        raise SidecarProtocolError(
            "SIDECAR_PROTOCOL_VERSION_UNSUPPORTED",
            "Sidecar response protocol_version is not supported.",
            category="response_validation",
        )
    if not isinstance(response.get("request_id"), str):
        raise SidecarProtocolError(
            "SIDECAR_RESPONSE_REQUEST_ID_INVALID",
            "Sidecar response request_id must be a string.",
            category="response_validation",
        )
    if not isinstance(response.get("command"), str):
        raise SidecarProtocolError(
            "SIDECAR_RESPONSE_COMMAND_INVALID",
            "Sidecar response command must be a string.",
            category="response_validation",
        )
    if expected_request_id is not None and response["request_id"] != expected_request_id:
        raise SidecarProtocolError(
            "SIDECAR_RESPONSE_REQUEST_ID_MISMATCH",
            "Sidecar response request_id does not match its request.",
            category="response_validation",
        )
    if expected_command is not None and response["command"] != expected_command:
        raise SidecarProtocolError(
            "SIDECAR_RESPONSE_COMMAND_MISMATCH",
            "Sidecar response command does not match its request.",
            category="response_validation",
        )
    if type(response.get("ok")) is not bool:
        raise SidecarProtocolError(
            "SIDECAR_RESPONSE_STATUS_INVALID",
            "Sidecar response ok field must be boolean.",
            category="response_validation",
        )
    diagnostics = response.get("diagnostics")
    if not isinstance(diagnostics, list) or any(not isinstance(item, dict) for item in diagnostics):
        raise SidecarProtocolError(
            "SIDECAR_RESPONSE_DIAGNOSTICS_INVALID",
            "Sidecar response diagnostics must be a list of objects.",
            category="response_validation",
        )
    if response["ok"]:
        if not isinstance(response.get("result"), dict) or response.get("error") is not None:
            raise SidecarProtocolError(
                "SIDECAR_RESPONSE_SUCCESS_INVALID",
                "Successful sidecar response must contain an object result and null error.",
                category="response_validation",
            )
    else:
        if response.get("result") is not None or not _valid_error_object(response.get("error")):
            raise SidecarProtocolError(
                "SIDECAR_RESPONSE_ERROR_INVALID",
                "Failed sidecar response must contain a valid error object and null result.",
                category="response_validation",
            )
    return response


def build_startup_handshake(host, port):
    startup = {
        "schema_version": STARTUP_SCHEMA_VERSION,
        "status": "ready",
        "protocol_version": PROTOCOL_VERSION,
        "host": host,
        "port": port,
    }
    validate_startup_handshake(startup)
    return startup


def validate_startup_handshake(startup):
    if not isinstance(startup, dict) or set(startup) != _STARTUP_FIELDS:
        raise SidecarProtocolError(
            "SIDECAR_STARTUP_SHAPE_INVALID",
            "Sidecar startup handshake fields are invalid.",
            category="startup",
        )
    valid = (
        startup.get("schema_version") == STARTUP_SCHEMA_VERSION
        and startup.get("status") == "ready"
        and startup.get("protocol_version") == PROTOCOL_VERSION
        and startup.get("host") == "127.0.0.1"
        and type(startup.get("port")) is int
        and 1 <= startup["port"] <= 65535
    )
    if not valid:
        raise SidecarProtocolError(
            "SIDECAR_STARTUP_INVALID",
            "Sidecar startup handshake values are invalid.",
            category="startup",
        )
    return startup


def _receive_exact(connection, count, *, incomplete_code, initial_close_code):
    chunks = bytearray()
    while len(chunks) < count:
        try:
            chunk = connection.recv(count - len(chunks))
        except socket.timeout:
            raise SidecarProtocolError(
                "SIDECAR_SOCKET_TIMEOUT",
                "Socket timed out while reading a sidecar frame.",
                retryable=True,
            ) from None
        except OSError:
            raise SidecarProtocolError(
                "SIDECAR_CONNECTION_CLOSED",
                "Connection closed while reading a sidecar frame.",
                retryable=True,
            ) from None
        if not chunk:
            code = initial_close_code if not chunks else incomplete_code
            message = (
                "Connection closed before a sidecar frame was received."
                if code == "SIDECAR_CONNECTION_CLOSED"
                else "Connection closed before a complete sidecar frame was received."
            )
            raise SidecarProtocolError(code, message, retryable=True)
        chunks.extend(chunk)
    return bytes(chunks)


def _valid_error_object(error):
    return (
        isinstance(error, dict)
        and set(error) == _ERROR_FIELDS
        and isinstance(error.get("code"), str)
        and error["code"] != ""
        and isinstance(error.get("category"), str)
        and isinstance(error.get("message"), str)
        and type(error.get("retryable")) is bool
        and isinstance(error.get("details"), dict)
    )


__all__ = [
    "DEFAULT_SOCKET_TIMEOUT",
    "MAX_FRAME_SIZE",
    "PROTOCOL_VERSION",
    "REQUEST_SCHEMA_VERSION",
    "RESPONSE_SCHEMA_VERSION",
    "STARTUP_SCHEMA_VERSION",
    "SUPPORTED_COMMANDS",
    "SidecarProtocolError",
    "build_error_response",
    "build_request",
    "build_startup_handshake",
    "build_success_response",
    "compact_json_object_bytes",
    "encode_frame",
    "read_frame",
    "send_frame",
    "validate_request",
    "validate_response",
    "validate_startup_handshake",
]
