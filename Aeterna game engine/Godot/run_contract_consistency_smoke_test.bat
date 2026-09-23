@echo off
call "%~dp0_run_godot_smoke.bat" "contract_consistency_smoke.log" "res://scripts/debug/contract_consistency_smoke_test.gd"
exit /b %ERRORLEVEL%
