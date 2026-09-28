@echo off
call "%~dp0_run_godot_smoke.bat" "action_request_smoke.log" "res://scripts/debug/action_request_smoke_test.gd"
exit /b %ERRORLEVEL%
