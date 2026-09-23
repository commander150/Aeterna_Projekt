@echo off
call "%~dp0_run_godot_smoke.bat" "unified_debug_dashboard_smoke.log" "res://scripts/debug/unified_debug_dashboard_smoke_test.gd"
exit /b %ERRORLEVEL%
