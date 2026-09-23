@echo off
call "%~dp0_run_godot_smoke.bat" "legal_action_debug_panel_smoke.log" "res://scripts/debug/legal_action_debug_panel_smoke_test.gd"
exit /b %ERRORLEVEL%
