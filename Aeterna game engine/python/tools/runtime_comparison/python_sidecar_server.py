"""Single-process, loopback-only server proof for the Python reference fixture."""

from __future__ import annotations

import argparse
import sys
import socket
from pathlib import Path, PurePosixPath

from tools.runtime_comparison.python_reference_fixture import (
    RuntimeComparisonFixtureError,
    run_python_reference_fixture,
)
from tools.runtime_comparison.sidecar_protocol import (
    DEFAULT_SOCKET_TIMEOUT,
    PROTOCOL_VERSION,
    REQUEST_SCHEMA_VERSION,
    RESPONSE_SCHEMA_VERSION,
    SUPPORTED_COMMANDS,
    SidecarProtocolError,
    build_error_response,
    build_startup_handshake,
    build_success_response,
    compact_json_object_bytes,
    read_frame,
    send_frame,
    validate_request,
)


LOOPBACK_HOST = "127.0.0.1"
RUNTIME_CANDIDATE = "python_sidecar_headless"
DEFAULT_FIXTURE_ROOT = (
    Path(__file__).resolve().parents[3] / "runtime_comparison" / "fixtures"
)


class SidecarServerInputError(ValueError):
    def __init__(self, code, message):
        self.code = str(code)
        self.message = str(message)
        super().__init__("%s: %s" % (self.code, self.message))


def serve_sidecar(host, port, *, fixture_root=DEFAULT_FIXTURE_ROOT):
    """Bind the proof server, print one startup line, then serve until shutdown."""

    _validate_bind_address(host, port)
    fixture_root = Path(fixture_root).resolve(strict=True)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind((host, port))
        listener.listen(1)
        bound_port = listener.getsockname()[1]
        startup = build_startup_handshake(host, bound_port)
        sys.stdout.write(compact_json_object_bytes(startup).decode("utf-8") + "\n")
        sys.stdout.flush()

        shutdown_requested = False
        while not shutdown_requested:
            connection, _ = listener.accept()
            with connection:
                connection.settimeout(DEFAULT_SOCKET_TIMEOUT)
                shutdown_requested = _serve_connection(connection, fixture_root)
    return 0


def _serve_connection(connection, fixture_root):
    used_request_ids = set()
    while True:
        try:
            request = read_frame(connection)
        except SidecarProtocolError as exc:
            if exc.code == "SIDECAR_CONNECTION_CLOSED":
                return False
            _try_send_error(connection, "", "protocol_error", exc)
            return False

        request_id = request.get("request_id") if isinstance(request, dict) else ""
        command = request.get("command") if isinstance(request, dict) else "unknown"
        try:
            validate_request(request)
            if request_id in used_request_ids:
                raise SidecarProtocolError(
                    "SIDECAR_REQUEST_ID_REUSED",
                    "Sidecar request_id was already used on this connection.",
                    category="request_validation",
                )
            used_request_ids.add(request_id)
            response, should_shutdown = _dispatch_request(request, fixture_root)
        except SidecarProtocolError as exc:
            response = build_error_response(request_id, command, exc)
            should_shutdown = False
        except Exception:
            response = build_error_response(
                request_id,
                command,
                SidecarProtocolError(
                    "SIDECAR_INTERNAL_ERROR",
                    "Sidecar request failed unexpectedly.",
                    category="internal",
                ),
            )
            should_shutdown = False

        try:
            send_frame(connection, response)
        except SidecarProtocolError:
            return False
        if should_shutdown:
            return True


def _dispatch_request(request, fixture_root):
    command = request["command"]
    request_id = request["request_id"]
    payload = request["payload"]
    if command == "health":
        _require_empty_payload(payload)
        result = {
            "status": "ready",
            "protocol_version": PROTOCOL_VERSION,
            "supported_request_schema": REQUEST_SCHEMA_VERSION,
            "supported_response_schema": RESPONSE_SCHEMA_VERSION,
            "supported_commands": list(SUPPORTED_COMMANDS),
            "runtime_candidate": RUNTIME_CANDIDATE,
            "implementation_language": "python",
        }
        return build_success_response(request_id, command, result), False
    if command == "run_runtime_comparison_fixture":
        if set(payload) != {"fixture_path"}:
            raise SidecarProtocolError(
                "SIDECAR_FIXTURE_PAYLOAD_INVALID",
                "Fixture command payload must contain only fixture_path.",
                category="request_validation",
            )
        fixture_path = resolve_fixture_path(payload["fixture_path"], fixture_root)
        try:
            result = run_python_reference_fixture(fixture_path)
        except RuntimeComparisonFixtureError as exc:
            raise SidecarProtocolError(
                "SIDECAR_FIXTURE_RUN_FAILED",
                "Runtime comparison fixture execution failed.",
                category="fixture",
                details={"fixture_code": exc.code, "fixture_step_id": exc.step_id},
            ) from None
        return build_success_response(request_id, command, result), False
    if command == "shutdown":
        _require_empty_payload(payload)
        return build_success_response(
            request_id,
            command,
            {"status": "shutting_down"},
        ), True
    raise SidecarProtocolError(
        "SIDECAR_COMMAND_UNSUPPORTED",
        "Sidecar command is not supported.",
        category="request_validation",
    )


def resolve_fixture_path(relative_path, fixture_root=DEFAULT_FIXTURE_ROOT):
    fixture_root = Path(fixture_root).resolve(strict=True)
    if not isinstance(relative_path, str) or relative_path == "":
        raise _fixture_path_error()
    if "\\" in relative_path or ":" in relative_path:
        raise _fixture_path_error()
    pure_path = PurePosixPath(relative_path)
    if pure_path.is_absolute() or any(part in {"", ".", ".."} for part in pure_path.parts):
        raise _fixture_path_error()
    if pure_path.name != "fixture.json":
        raise _fixture_path_error("SIDECAR_FIXTURE_NOT_FOUND", "Fixture file is not allowed.")
    candidate = fixture_root.joinpath(*pure_path.parts)
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(fixture_root)
    except (OSError, RuntimeError, ValueError):
        raise _fixture_path_error(
            "SIDECAR_FIXTURE_NOT_FOUND",
            "Fixture file was not found inside the allowed fixture root.",
        ) from None
    if not resolved.is_file():
        raise _fixture_path_error(
            "SIDECAR_FIXTURE_NOT_FOUND",
            "Fixture file was not found inside the allowed fixture root.",
        )
    return resolved


def _fixture_path_error(code="SIDECAR_FIXTURE_PATH_INVALID", message=None):
    return SidecarProtocolError(
        code,
        message or "Fixture path must be a confined repository-relative path.",
        category="security",
    )


def _require_empty_payload(payload):
    if payload:
        raise SidecarProtocolError(
            "SIDECAR_PAYLOAD_INVALID",
            "This sidecar command requires an empty payload object.",
            category="request_validation",
        )


def _try_send_error(connection, request_id, command, error):
    try:
        send_frame(connection, build_error_response(request_id, command, error))
    except SidecarProtocolError:
        pass


def _validate_bind_address(host, port):
    if host != LOOPBACK_HOST:
        raise SidecarServerInputError(
            "SIDECAR_HOST_NOT_ALLOWED",
            "Sidecar proof server only accepts host 127.0.0.1.",
        )
    if type(port) is not int or not 0 <= port <= 65535:
        raise SidecarServerInputError(
            "SIDECAR_PORT_INVALID",
            "Sidecar proof server port must be between 0 and 65535.",
        )


class _ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise SidecarServerInputError(
            "SIDECAR_SERVER_CLI_INVALID",
            "Sidecar server CLI arguments are invalid.",
        )


def _build_parser():
    parser = _ArgumentParser(description="Run the AETERNA Python loopback sidecar proof.")
    parser.add_argument("--host", default=LOOPBACK_HOST)
    parser.add_argument("--port", type=int, default=0)
    return parser


def main(argv=None):
    try:
        arguments = _build_parser().parse_args(argv)
        return serve_sidecar(arguments.host, arguments.port)
    except SidecarServerInputError as exc:
        print("%s: %s" % (exc.code, exc.message), file=sys.stderr)
        return 2
    except (OSError, ValueError):
        print(
            "SIDECAR_SERVER_START_FAILED: Sidecar server could not start.",
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "DEFAULT_FIXTURE_ROOT",
    "LOOPBACK_HOST",
    "RUNTIME_CANDIDATE",
    "SidecarServerInputError",
    "main",
    "resolve_fixture_path",
    "serve_sidecar",
]
