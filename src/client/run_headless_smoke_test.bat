@echo off
call "%~dp0_run_godot_smoke.bat" "headless_smoke.log" "res://scripts/debug/package_loader_smoke_test.gd"
exit /b %ERRORLEVEL%
