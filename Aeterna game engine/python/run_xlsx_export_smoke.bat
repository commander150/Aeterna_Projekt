@echo off
cd /d "%~dp0"
python -m unittest tests.test_xlsx_export_smoke
exit /b %ERRORLEVEL%
