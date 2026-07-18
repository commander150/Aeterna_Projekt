"""Thin transport-only client for the Python sidecar proof."""

from __future__ import annotations

import socket
from copy import deepcopy

from tools.runtime_comparison.sidecar_protocol import (
    DEFAULT_SOCKET_TIMEOUT,
    SidecarProtocolError,
    build_request,
    read_frame,
    send_frame,
    validate_response,
)


class PythonSidecarClientError(Exception):
    """Stable client or remote-response failure."""

    def __init__(self, code, message, *, response=None):
        self.code = str(code)
        self.message = str(message)
        self.response = deepcopy(response)
        super().__init__("%s: %s" % (self.code, self.message))


class PythonSidecarClient:
    """Synchronous request/response client with no engine dependencies."""

    def __init__(self, host, port, *, timeout=DEFAULT_SOCKET_TIMEOUT):
        if host != "127.0.0.1":
            raise PythonSidecarClientError(
                "SIDECAR_CLIENT_HOST_NOT_ALLOWED",
                "Sidecar proof client only accepts host 127.0.0.1.",
            )
        if type(port) is not int or not 1 <= port <= 65535:
            raise PythonSidecarClientError(
                "SIDECAR_CLIENT_PORT_INVALID",
                "Sidecar client port must be between 1 and 65535.",
            )
        if not isinstance(timeout, (int, float)) or isinstance(timeout, bool) or timeout <= 0:
            raise PythonSidecarClientError(
                "SIDECAR_CLIENT_TIMEOUT_INVALID",
                "Sidecar client timeout must be a positive number.",
            )
        self.host = host
        self.port = port
        self.timeout = float(timeout)
        self._connection = None

    @property
    def connected(self):
        return self._connection is not None

    def connect(self):
        if self._connection is not None:
            return self
        try:
            connection = socket.create_connection(
                (self.host, self.port),
                timeout=self.timeout,
            )
            connection.settimeout(self.timeout)
        except (OSError, socket.timeout):
            raise PythonSidecarClientError(
                "SIDECAR_CLIENT_CONNECT_FAILED",
                "Could not connect to the Python sidecar.",
            ) from None
        self._connection = connection
        return self

    def close(self):
        connection = self._connection
        self._connection = None
        if connection is not None:
            try:
                connection.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            connection.close()

    def request(self, request_id, command, payload=None):
        if self._connection is None:
            raise PythonSidecarClientError(
                "SIDECAR_CLIENT_NOT_CONNECTED",
                "Sidecar client is not connected.",
            )
        try:
            request = build_request(request_id, command, payload)
            send_frame(self._connection, request)
            response = read_frame(self._connection)
            validate_response(
                response,
                expected_request_id=request_id,
                expected_command=command,
            )
        except SidecarProtocolError as exc:
            raise PythonSidecarClientError(exc.code, exc.message) from None
        if not response["ok"]:
            error = response["error"]
            raise PythonSidecarClientError(
                error["code"],
                error["message"],
                response=response,
            )
        return response

    def health(self, request_id):
        return self.request(request_id, "health", {})

    def run_runtime_comparison_fixture(self, request_id, fixture_path):
        return self.request(
            request_id,
            "run_runtime_comparison_fixture",
            {"fixture_path": fixture_path},
        )

    def shutdown(self, request_id):
        return self.request(request_id, "shutdown", {})

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return False


__all__ = ["PythonSidecarClient", "PythonSidecarClientError"]
