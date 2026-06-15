@echo off
chcp 65001 >nul
setlocal

set "SCRIPT_DIR=%~dp0"
set "PS_SCRIPT=%SCRIPT_DIR%start.ps1"

powershell.exe -ExecutionPolicy Bypass -File "%PS_SCRIPT%"

endlocal
