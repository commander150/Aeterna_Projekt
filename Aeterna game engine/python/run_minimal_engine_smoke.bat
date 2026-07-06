@echo off
setlocal
cd /d "%~dp0"
echo AETERNA minimal Python engine smoke
echo.
python tools\engine\run_minimal_engine_smoke.py %*
set SMOKE_EXIT_CODE=%ERRORLEVEL%
echo.
echo Press any key to close this window.
pause >nul
exit /b %SMOKE_EXIT_CODE%
