@echo off
setlocal
cd /d "%~dp0"
python ..\ai_vs_ai\run_ai_smoke_scenario.py %*
exit /b %ERRORLEVEL%
