@echo off
setlocal
cd /d "%~dp0"
python tools\engine\run_minimal_engine_smoke.py %*
exit /b %ERRORLEVEL%
