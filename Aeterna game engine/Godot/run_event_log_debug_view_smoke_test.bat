@echo off
call "%~dp0_run_godot_smoke.bat" "event_log_debug_view_smoke.log" "res://scripts/debug/event_log_debug_view_smoke_test.gd"
exit /b %ERRORLEVEL%
