# Emotion Spectrum Analyzer - Start Script
$SCRIPT_DIR = Split-Path $MyInvocation.MyCommand.Path -Parent
Set-Location $SCRIPT_DIR

$PYTHON = Join-Path $SCRIPT_DIR "venv\Scripts\python.exe"

if (-not (Test-Path $PYTHON)) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run install.cmd first"
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "`n=== Starting Emotion Spectrum Analyzer ==="
Write-Host "Access: http://localhost:7861"
Write-Host "Mode: Local ML Model"
& $PYTHON -m src.main
