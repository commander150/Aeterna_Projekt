@echo off
call "%~dp0_run_godot_smoke.bat" "snapshot_viewer_smoke.log" "res://scripts/debug/snapshot_viewer_smoke_test.gd"
exit /b %ERRORLEVEL%
