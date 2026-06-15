# Emotion Spectrum Analyzer Installer
$ErrorActionPreference = "Continue"

# Get script directory
$SCRIPT_DIR = Split-Path $MyInvocation.MyCommand.Path -Parent
Set-Location $SCRIPT_DIR

$VENV_DIR = Join-Path $SCRIPT_DIR "venv"
$PYTHON_MIN_VERSION = [version]"3.13.0"
$PYTHON_URL = "https://www.python.org/ftp/python/3.13.0/python-3.13.0-amd64.exe"
$PYTHON_INSTALLER = Join-Path $env:TEMP "python_installer.exe"

Write-Host "`n=== Emotion Spectrum Analyzer Setup ==="

# Step 1: Check Python
Write-Host "`n[1/6] Checking Python..."
$pythonFound = $false
try {
    $versionOutput = python --version 2>&1
    $versionMatch = [regex]::Match($versionOutput, "Python (\d+\.\d+\.\d+)")
    if ($versionMatch.Success) {
        $currentVersion = [version]$versionMatch.Groups[1].Value
        Write-Host "Found Python $currentVersion"
        if ($currentVersion -ge $PYTHON_MIN_VERSION) {
            $pythonFound = $true
            Write-Host "OK: Python version OK" -ForegroundColor Green
        }
    }
} catch {}

# Step 2: Install Python if needed
if (-not $pythonFound) {
    Write-Host "`n[2/6] Installing Python 3.13..."
    Write-Host "Downloading..."
    try {
        (New-Object System.Net.WebClient).DownloadFile($PYTHON_URL, $PYTHON_INSTALLER)
        Write-Host "Installing..."
        Start-Process -FilePath $PYTHON_INSTALLER -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait -NoNewWindow
        Remove-Item $PYTHON_INSTALLER -Force
        $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
        Write-Host "OK: Python installed" -ForegroundColor Green
    } catch {
        Write-Host "ERROR: Failed to install Python" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Step 3: Create venv
Write-Host "`n[3/6] Creating virtual environment..."
try {
    if (Test-Path $VENV_DIR) { 
        Write-Host "Removing existing venv..."
        Remove-Item $VENV_DIR -Recurse -Force -ErrorAction SilentlyContinue
    }
    python -m venv $VENV_DIR
    Write-Host "OK: Virtual environment created" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed to create venv" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Step 4: Install dependencies
Write-Host "`n[4/6] Installing dependencies..."
try {
    $pip = Join-Path $VENV_DIR "Scripts\pip.exe"
    & $pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
    & $pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    Write-Host "OK: Dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Step 5: Initialize model
Write-Host "`n[5/6] Initializing ML model..."
try {
    $python = Join-Path $VENV_DIR "Scripts\python.exe"
    & $python -c "from src.ml_model import get_ml_classifier; get_ml_classifier()"
    Write-Host "OK: ML model initialized" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed to initialize ML model" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Step 6: Create shortcut
Write-Host "`n[6/6] Creating shortcut..."
try {
    $desktopPath = [Environment]::GetFolderPath("Desktop")
    $shortcutPath = $desktopPath + "\EmotionAnalyzer.lnk"
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = $SCRIPT_DIR + "\start.cmd"
    $shortcut.WorkingDirectory = $SCRIPT_DIR
    $shortcut.Save()
    Write-Host "OK: Shortcut created" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed to create shortcut" -ForegroundColor Red
}

Write-Host "`n=== Installation Complete ==="
Write-Host "Run start.cmd to launch the application"
Read-Host "Press Enter to exit"
