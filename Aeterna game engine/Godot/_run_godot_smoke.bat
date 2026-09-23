@echo off
setlocal

if "%~1"=="" (
    >&2 echo ERROR: Missing smoke log filename.
    exit /b 2
)
if "%~2"=="" (
    >&2 echo ERROR: Missing Godot smoke script path.
    exit /b 2
)

cd /d "%~dp0"
if errorlevel 1 exit /b %ERRORLEVEL%

call "%~dp0_resolve_godot_exe.bat"
set "AETERNA_RESOLVE_EXIT=%ERRORLEVEL%"
if not "%AETERNA_RESOLVE_EXIT%"=="0" exit /b %AETERNA_RESOLVE_EXIT%

if not exist "logs" mkdir "logs"
if errorlevel 1 exit /b %ERRORLEVEL%

"%AETERNA_RESOLVED_GODOT_EXE%" --verbose --headless --log-file "logs/%~1" --path "." --script "%~2"
set "AETERNA_GODOT_EXIT=%ERRORLEVEL%"
exit /b %AETERNA_GODOT_EXIT%
