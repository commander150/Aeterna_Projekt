@echo off
call "%~dp0_run_godot_smoke.bat" "debug_contracts_smoke.log" "res://scripts/debug/debug_contracts_smoke_test.gd"
exit /b %ERRORLEVEL%
