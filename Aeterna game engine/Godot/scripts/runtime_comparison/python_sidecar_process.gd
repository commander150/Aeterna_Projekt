extends RefCounted


const Protocol = preload("res://scripts/runtime_comparison/python_sidecar_protocol.gd")
const MAX_STARTUP_LINE_BYTES = 64 * 1024

var python_executable := ""
var python_project_root := ""
var pid := -1
var host := ""
var port := -1
var startup := {}
var startup_raw_text := ""
var startup_raw_bytes := PackedByteArray()
var startup_stdout_remainder := PackedByteArray()
var stdout_remainder := PackedByteArray()
var stderr_bytes := PackedByteArray()
var exit_code := -1
var forced_kill_used := false
var pythonpath_restored := false
var bytecode_environment_restored := false

var _stdio: FileAccess
var _stderr: FileAccess


func start(timeout_msec: int = Protocol.DEFAULT_TIMEOUT_MSEC) -> Dictionary:
	if pid > 0:
		return _failure("SIDECAR_PROCESS_ALREADY_STARTED", "Sidecar process can only be started once.")
	var executable_result := _resolve_python_executable()
	if not bool(executable_result.get("ok", false)):
		return executable_result
	var project_result := _resolve_python_project_root()
	if not bool(project_result.get("ok", false)):
		return project_result

	var pythonpath_state := _capture_environment("PYTHONPATH")
	var bytecode_state := _capture_environment("PYTHONDONTWRITEBYTECODE")
	OS.set_environment("PYTHONPATH", python_project_root)
	OS.set_environment("PYTHONDONTWRITEBYTECODE", "1")
	var arguments := PackedStringArray([
		"-B",
		"-m",
		"tools.runtime_comparison.python_sidecar_server",
		"--host",
		"127.0.0.1",
		"--port",
		"0",
	])
	var pipe_result := OS.execute_with_pipe(python_executable, arguments, false)
	_restore_environment("PYTHONPATH", pythonpath_state)
	_restore_environment("PYTHONDONTWRITEBYTECODE", bytecode_state)
	pythonpath_restored = _environment_matches("PYTHONPATH", pythonpath_state)
	bytecode_environment_restored = _environment_matches("PYTHONDONTWRITEBYTECODE", bytecode_state)

	if pipe_result.is_empty():
		return _failure("SIDECAR_PROCESS_START_FAILED", "Godot could not start the Python sidecar process.")
	if not pipe_result.has("stdio") or not pipe_result.has("stderr") or not pipe_result.has("pid"):
		return _failure("SIDECAR_PROCESS_PIPE_INVALID", "Sidecar process pipe result is incomplete.")
	if not (pipe_result.get("stdio") is FileAccess) or not (pipe_result.get("stderr") is FileAccess):
		return _failure("SIDECAR_PROCESS_PIPE_INVALID", "Sidecar process pipes are not FileAccess instances.")
	if typeof(pipe_result.get("pid")) != TYPE_INT or int(pipe_result.get("pid")) <= 0:
		return _failure("SIDECAR_PROCESS_PID_INVALID", "Sidecar process PID is invalid.")
	_stdio = pipe_result.get("stdio")
	_stderr = pipe_result.get("stderr")
	pid = int(pipe_result.get("pid"))

	var startup_result := _read_startup_line(timeout_msec)
	if not bool(startup_result.get("ok", false)):
		return startup_result
	startup = startup_result.get("startup", {})
	startup_raw_text = str(startup_result.get("raw_text", ""))
	startup_raw_bytes = startup_result.get("raw_bytes", PackedByteArray())
	host = str(startup_result.get("host", ""))
	port = int(startup_result.get("port", -1))
	return {
		"ok": true,
		"pid": pid,
		"host": host,
		"port": port,
		"startup": startup,
		"startup_raw_text": startup_raw_text,
		"port_projection": startup_result.get("port_projection", ""),
		"pythonpath_restored": pythonpath_restored,
		"bytecode_environment_restored": bytecode_environment_restored,
	}


func wait_for_exit(timeout_msec: int = Protocol.DEFAULT_TIMEOUT_MSEC) -> Dictionary:
	if pid <= 0:
		return _failure("SIDECAR_PROCESS_NOT_STARTED", "Sidecar process was not started.")
	var deadline := Time.get_ticks_msec() + timeout_msec
	while OS.is_process_running(pid) and Time.get_ticks_msec() <= deadline:
		_drain_pipe(_stdio, stdout_remainder)
		_drain_pipe(_stderr, stderr_bytes)
		OS.delay_msec(1)
	if OS.is_process_running(pid):
		return _failure("SIDECAR_PROCESS_EXIT_TIMEOUT", "Sidecar process did not stop in time.")
	exit_code = OS.get_process_exit_code(pid)
	return {"ok": true, "exit_code": exit_code}


func force_stop(timeout_msec: int = 2_000) -> Dictionary:
	if pid <= 0 or not OS.is_process_running(pid):
		return {"ok": true}
	_drain_pipe(_stdio, stdout_remainder)
	_drain_pipe(_stderr, stderr_bytes)
	forced_kill_used = true
	var kill_error := OS.kill(pid)
	if kill_error != OK:
		return _failure("SIDECAR_PROCESS_KILL_FAILED", "Sidecar process could not be terminated.")
	var deadline := Time.get_ticks_msec() + timeout_msec
	while OS.is_process_running(pid) and Time.get_ticks_msec() <= deadline:
		OS.delay_msec(1)
	if OS.is_process_running(pid):
		return _failure("SIDECAR_PROCESS_STILL_RUNNING", "Sidecar process remained alive after kill fallback.")
	exit_code = OS.get_process_exit_code(pid)
	return {"ok": true}


func is_running() -> bool:
	return pid > 0 and OS.is_process_running(pid)


func _resolve_python_executable() -> Dictionary:
	if not OS.has_environment("AETERNA_PYTHON_EXECUTABLE"):
		return _failure("SIDECAR_PYTHON_EXECUTABLE_MISSING", "AETERNA_PYTHON_EXECUTABLE is required.")
	python_executable = OS.get_environment("AETERNA_PYTHON_EXECUTABLE")
	if python_executable.is_empty() or not python_executable.is_absolute_path():
		return _failure("SIDECAR_PYTHON_EXECUTABLE_INVALID", "Python executable must be an absolute path.")
	if not FileAccess.file_exists(python_executable) or DirAccess.dir_exists_absolute(python_executable):
		return _failure("SIDECAR_PYTHON_EXECUTABLE_INVALID", "Python executable does not name a regular file.")
	return {"ok": true}


func _resolve_python_project_root() -> Dictionary:
	python_project_root = ProjectSettings.globalize_path("res://../python").simplify_path()
	if not DirAccess.dir_exists_absolute(python_project_root):
		return _failure("SIDECAR_PYTHON_ROOT_INVALID", "Python project root does not exist.")
	var server_path := python_project_root.path_join("tools/runtime_comparison/python_sidecar_server.py")
	if not FileAccess.file_exists(server_path):
		return _failure("SIDECAR_PYTHON_ROOT_INVALID", "Python sidecar server module is missing.")
	return {"ok": true}


func _read_startup_line(timeout_msec: int) -> Dictionary:
	var buffer := PackedByteArray()
	var deadline := Time.get_ticks_msec() + timeout_msec
	while Time.get_ticks_msec() <= deadline:
		_drain_pipe(_stdio, buffer)
		if buffer.size() > MAX_STARTUP_LINE_BYTES:
			return _failure("SIDECAR_STARTUP_TOO_LARGE", "Sidecar startup line exceeds the size limit.")
		var newline_index := _find_byte(buffer, 10)
		if newline_index >= 0:
			var line := buffer.slice(0, newline_index)
			if not line.is_empty() and line[line.size() - 1] == 13:
				line.resize(line.size() - 1)
			startup_stdout_remainder = buffer.slice(newline_index + 1)
			stdout_remainder.append_array(startup_stdout_remainder)
			return Protocol.decode_startup_line(line)
		if pid > 0 and not OS.is_process_running(pid):
			return _failure("SIDECAR_STARTUP_MISSING", "Sidecar exited before its startup handshake.")
		OS.delay_msec(1)
	return _failure("SIDECAR_STARTUP_TIMEOUT", "Sidecar startup handshake timed out.")


func _drain_pipe(pipe: FileAccess, target: PackedByteArray) -> void:
	if pipe == null:
		return
	var available := pipe.get_length()
	if available <= 0:
		return
	var chunk := pipe.get_buffer(available)
	if not chunk.is_empty():
		target.append_array(chunk)


func _capture_environment(name: String) -> Dictionary:
	return {
		"present": OS.has_environment(name),
		"value": OS.get_environment(name) if OS.has_environment(name) else "",
	}


func _restore_environment(name: String, state: Dictionary) -> void:
	if bool(state.get("present", false)):
		OS.set_environment(name, str(state.get("value", "")))
	else:
		OS.unset_environment(name)


func _environment_matches(name: String, state: Dictionary) -> bool:
	var expected_present := bool(state.get("present", false))
	if OS.has_environment(name) != expected_present:
		return false
	return not expected_present or OS.get_environment(name) == str(state.get("value", ""))


func _find_byte(buffer: PackedByteArray, value: int) -> int:
	for index in range(buffer.size()):
		if int(buffer[index]) == value:
			return index
	return -1


func _failure(code: String, message: String) -> Dictionary:
	return {"ok": false, "code": code, "message": message}
