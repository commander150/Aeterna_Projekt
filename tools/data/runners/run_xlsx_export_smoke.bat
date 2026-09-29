@echo off
for %%I in ("%~dp0..\..\..") do set "REPOSITORY_ROOT=%%~fI"
cd /d "%REPOSITORY_ROOT%\Aeterna game engine\python"
python -m unittest tests.test_xlsx_export_smoke
exit /b %ERRORLEVEL%
