@echo off
chcp 65001 >nul
cd /d "%~dp0"
python tools\xlsx_export\xlsx_export.py --source-dir "..\..\XLSX export\source" --output-dir ".\exports\jsonl"
pause
