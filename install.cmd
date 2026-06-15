@echo off
chcp 65001 >nul
setlocal

set "SCRIPT_DIR=%~dp0"
set "PS_SCRIPT=%SCRIPT_DIR%install.ps1"

echo ============================================
echo     神经情绪光谱仪 - 安装程序
echo ============================================
echo.

powershell.exe -ExecutionPolicy Bypass -File "%PS_SCRIPT%"

endlocal
pause
