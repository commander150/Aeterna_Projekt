@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Deprecated pipeline note:
echo   This is a raw/debug XLSX export runner, not the primary Godot runtime package pipeline.
echo   Use publish_runtime_package_to_godot.bat for validated XLSX -^> runtime package -^> Godot publish.
echo.
python tools\xlsx_export\xlsx_export.py "..\..\Aeterna dokumentációk\AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.9v.xlsx" --profile runtime_cards --output-dir ".\exports\jsonl"
pause
