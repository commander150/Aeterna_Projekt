@echo off
for %%I in ("%~dp0..\..\..") do set "REPOSITORY_ROOT=%%~fI"
cd /d "%REPOSITORY_ROOT%"
python -m unittest discover -s tests\data\python -p "test_xlsx_export_smoke.py"
exit /b %ERRORLEVEL%
