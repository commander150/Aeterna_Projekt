import socket
import struct
import unittest
from copy import deepcopy

from tools.runtime_comparison.sidecar_protocol import (
    MAX_FRAME_SIZE,
    PROTOCOL_VERSION,
    REQUEST_SCHEMA_VERSION,
    RESPONSE_SCHEMA_VERSION,
    SidecarProtocolError,
    build_error_response,
    build_request,
    build_success_response,
    compact_json_object_bytes,
    encode_frame,
    read_frame,
    send_frame,
    validate_response,
)


class TestRuntimeComparisonSidecarProtocol(unittest.TestCase):
    def test_frame_roundtrip_is_compact_utf8_and_does_not_mutate_input(self):
        value = {"message": "árvíztűrő tükörfúrógép", "nested": {"ok": True}}
        before = deepcopy(value)

        frame = encode_frame(value)
        decoded = read_frame(_ChunkedSocket(frame))

        self.assertEqual(decoded, value)
        self.assertEqual(value, before)
        payload = frame[4:]
        self.assertEqual(struct.unpack("!I", frame[:4])[0], len(payload))
        self.assertFalse(payload.startswith(b"\xef\xbb\xbf"))
        self.assertNotIn(b"\n", payload)

    def test_partial_header_and_body_reads_are_supported(self):
        value = {"schema_version": PROTOCOL_VERSION, "items": [1, 2, 3]}
        frame = encode_frame(value)

        decoded = read_frame(_ChunkedSocket(frame, chunks=[1, 2, 1, 3, 2, 1]))

        self.assertEqual(decoded, value)

    def test_multiple_consecutive_frames_are_read_independently(self):
        first = {"index": 1}
        second = {"index": 2, "text": "második"}
        connection = _ChunkedSocket(encode_frame(first) + encode_frame(second), chunks=[2, 1, 5])

        self.assertEqual(read_frame(connection), first)
        self.assertEqual(read_frame(connection), second)

    def test_send_frame_uses_sendall_without_mutation(self):
        value = {"payload": {"value": 1}}
        before = deepcopy(value)
        connection = _SendSocket()

        send_frame(connection, value)

        self.assertEqual(connection.data, encode_frame(value))
        self.assertEqual(value, before)

    def test_incomplete_or_closed_header_has_stable_errors(self):
        with self.assertRaises(SidecarProtocolError) as closed:
            read_frame(_ChunkedSocket(b""))
        self.assertEqual(closed.exception.code, "SIDECAR_CONNECTION_CLOSED")

        with self.assertRaises(SidecarProtocolError) as incomplete:
            read_frame(_ChunkedSocket(b"\x00\x00"))
        self.assertEqual(incomplete.exception.code, "SIDECAR_FRAME_HEADER_INCOMPLETE")

    def test_invalid_and_oversized_lengths_are_rejected_before_body_read(self):
        self.assertEqual(MAX_FRAME_SIZE, 8 * 1024 * 1024)
        with self.assertRaises(SidecarProtocolError) as invalid:
            read_frame(_ChunkedSocket(struct.pack("!I", 0)))
        self.assertEqual(invalid.exception.code, "SIDECAR_FRAME_LENGTH_INVALID")

        with self.assertRaises(SidecarProtocolError) as oversized:
            read_frame(_ChunkedSocket(struct.pack("!I", MAX_FRAME_SIZE + 1)))
        self.assertEqual(oversized.exception.code, "SIDECAR_FRAME_TOO_LARGE")

        with self.assertRaises(SidecarProtocolError) as outbound:
            encode_frame({"value": "1234"}, max_frame_size=2)
        self.assertEqual(outbound.exception.code, "SIDECAR_FRAME_TOO_LARGE")

    def test_incomplete_body_is_rejected(self):
        with self.assertRaises(SidecarProtocolError) as raised:
            read_frame(_ChunkedSocket(struct.pack("!I", 5) + b"{}"))
        self.assertEqual(raised.exception.code, "SIDECAR_FRAME_BODY_INCOMPLETE")

    def test_invalid_utf8_json_and_non_object_root_are_distinct(self):
        cases = (
            (b"\xff", "SIDECAR_FRAME_UTF8_INVALID"),
            (b"{broken", "SIDECAR_FRAME_JSON_INVALID"),
            (b"[]", "SIDECAR_FRAME_ROOT_INVALID"),
        )
        for body, code in cases:
            with self.subTest(code=code):
                with self.assertRaises(SidecarProtocolError) as raised:
                    read_frame(_ChunkedSocket(struct.pack("!I", len(body)) + body))
                self.assertEqual(raised.exception.code, code)

    def test_socket_timeout_is_stable(self):
        with self.assertRaises(SidecarProtocolError) as raised:
            read_frame(_TimeoutSocket())
        self.assertEqual(raised.exception.code, "SIDECAR_SOCKET_TIMEOUT")
        self.assertTrue(raised.exception.retryable)

    def test_request_and_response_envelopes_are_versioned(self):
        request = build_request("req_1", "health", {})
        response = build_success_response("req_1", "health", {"status": "ready"})

        self.assertEqual(request["schema_version"], REQUEST_SCHEMA_VERSION)
        self.assertEqual(request["protocol_version"], PROTOCOL_VERSION)
        self.assertEqual(response["schema_version"], RESPONSE_SCHEMA_VERSION)
        self.assertEqual(response["protocol_version"], PROTOCOL_VERSION)
        self.assertIs(validate_response(response, expected_request_id="req_1", expected_command="health"), response)

        with self.assertRaises(SidecarProtocolError) as invalid_payload:
            build_request("req_invalid_payload", "health", [])
        self.assertEqual(invalid_payload.exception.code, "SIDECAR_PAYLOAD_INVALID")

    def test_error_response_has_stable_machine_readable_shape(self):
        error = SidecarProtocolError(
            "SIDECAR_TEST_ERROR",
            "Synthetic protocol error.",
            category="test",
            details={"field": "payload"},
        )

        response = build_error_response("req_error", "health", error)

        self.assertFalse(response["ok"])
        self.assertIsNone(response["result"])
        self.assertEqual(response["error"]["code"], "SIDECAR_TEST_ERROR")
        self.assertEqual(response["error"]["details"], {"field": "payload"})
        validate_response(response, expected_request_id="req_error", expected_command="health")

    def test_response_correlation_mismatches_are_rejected(self):
        response = build_success_response("actual", "health", {"status": "ready"})
        with self.assertRaises(SidecarProtocolError) as request_id_error:
            validate_response(response, expected_request_id="expected", expected_command="health")
        self.assertEqual(request_id_error.exception.code, "SIDECAR_RESPONSE_REQUEST_ID_MISMATCH")

        with self.assertRaises(SidecarProtocolError) as command_error:
            validate_response(response, expected_request_id="actual", expected_command="shutdown")
        self.assertEqual(command_error.exception.code, "SIDECAR_RESPONSE_COMMAND_MISMATCH")

    def test_compact_encoder_rejects_non_object_root(self):
        with self.assertRaises(SidecarProtocolError) as raised:
            compact_json_object_bytes(["not", "an", "object"])
        self.assertEqual(raised.exception.code, "SIDECAR_FRAME_ROOT_INVALID")


class _ChunkedSocket:
    def __init__(self, data, chunks=None):
        self.data = bytearray(data)
        self.chunks = list(chunks or [])

    def recv(self, size):
        if not self.data:
            return b""
        requested = self.chunks.pop(0) if self.chunks else size
        count = min(size, requested, len(self.data))
        result = bytes(self.data[:count])
        del self.data[:count]
        return result


class _SendSocket:
    def __init__(self):
        self.data = b""

    def sendall(self, data):
        self.data += data


class _TimeoutSocket:
    def recv(self, size):
        raise socket.timeout()


if __name__ == "__main__":
    unittest.main()
