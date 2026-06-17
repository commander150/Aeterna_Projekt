@echo off
chcp 65001 >nul
cd /d "%~dp0"
python xlsx_export.py
echo.
pause
