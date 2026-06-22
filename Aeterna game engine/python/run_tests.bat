@echo off
cd /d "%~dp0"
python -m unittest tests.test_build_sample_runtime_package
pause
