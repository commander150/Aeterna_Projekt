@echo off
set "AETERNA_RESOLVED_GODOT_EXE="

if defined AETERNA_GODOT_EXE (
    if not exist "%AETERNA_GODOT_EXE%" (
        >&2 echo ERROR: AETERNA_GODOT_EXE does not point to an existing file: "%AETERNA_GODOT_EXE%"
        exit /b 2
    )
    if exist "%AETERNA_GODOT_EXE%\NUL" (
        >&2 echo ERROR: AETERNA_GODOT_EXE must point to a file, not a directory: "%AETERNA_GODOT_EXE%"
        exit /b 2
    )
    set "AETERNA_RESOLVED_GODOT_EXE=%AETERNA_GODOT_EXE%"
    exit /b 0
)

for /f "delims=" %%G in ('where.exe godot4 2^>nul') do if not defined AETERNA_RESOLVED_GODOT_EXE set "AETERNA_RESOLVED_GODOT_EXE=%%G"
if defined AETERNA_RESOLVED_GODOT_EXE exit /b 0

for /f "delims=" %%G in ('where.exe godot 2^>nul') do if not defined AETERNA_RESOLVED_GODOT_EXE set "AETERNA_RESOLVED_GODOT_EXE=%%G"
if defined AETERNA_RESOLVED_GODOT_EXE exit /b 0

>&2 echo ERROR: Godot executable not found. Set AETERNA_GODOT_EXE to a valid file or add godot4 or godot to PATH.
exit /b 2
