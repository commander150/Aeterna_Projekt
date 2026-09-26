@echo off
cd /d "%~dp0"
python tools\runtime_package\publish_runtime_package_to_godot.py %*
exit /b %ERRORLEVEL%
