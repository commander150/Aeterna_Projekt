@echo off
cd /d "%~dp0"
echo Deprecated: this script no longer performs unsafe direct copy.
echo Use publish_runtime_package_to_godot.bat for validated publish.
call publish_runtime_package_to_godot.bat %*
exit /b %ERRORLEVEL%
