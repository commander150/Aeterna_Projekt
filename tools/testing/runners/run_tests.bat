@echo off
setlocal
cd /d "%~dp0\..\..\.."
python -m unittest discover -s tests\data\python -p "test_build_sample_runtime_package.py"
set "TEST_EXIT_CODE=%ERRORLEVEL%"
pause
exit /b %TEST_EXIT_CODE%