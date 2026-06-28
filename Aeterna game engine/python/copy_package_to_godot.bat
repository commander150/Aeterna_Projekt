@echo off
cd /d "%~dp0"
robocopy ".\sample_runtime_package" "..\Godot\runtime_package" /E
pause
