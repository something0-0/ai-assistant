# ============================================================
#  AI ASSISTANT - One-Liner Installer
# ============================================================

$ErrorActionPreference = "Stop"
$repoUrl = "https://github.com/something0-0/ai-assistant.git"
$projectName = "ai-assistant"
$installDir = Join-Path $HOME $projectName

function Show-Banner {
    Clear-Host
    Write-Host ""
    Write-Host "  ============================================" -ForegroundColor Cyan
    Write-Host "        AI ASSISTANT - INSTALLER              " -ForegroundColor Cyan
    Write-Host "   Chat . Voice . Memory . RAG . API          " -ForegroundColor Cyan
    Write-Host "  ============================================" -ForegroundColor Cyan
    Write-Host ""
}

function Step($n, $msg) {
    Write-Host "[$n/6] " -ForegroundColor Yellow -NoNewline
    Write-Host $msg
}

function Ensure-Python {
    try {
        $pyVer = & python --version 2>&1
        if ($pyVer -match "Python 3\.(1[0-9]|[2-9][0-9])") {
            Write-Host "       Found: $pyVer" -ForegroundColor Green
            return $true
        }
    } catch {}
    return $false
}

function Ensure-Git {
    try {
        $gitVer = & git --version 2>&1
        Write-Host "       Found: $gitVer" -ForegroundColor Green
        return $true
    } catch {
        return $false
    }
}

Show-Banner

Step 1 "Checking Python..."
if (-not (Ensure-Python)) {
    Write-Host "       Python 3.10+ not found." -ForegroundColor Red
    Write-Host "       Please install Python 3.11 from python.org" -ForegroundColor Yellow
    Write-Host "       CHECK 'Add Python to PATH' during install!" -ForegroundColor Yellow
    Read-Host "Press Enter to open the download page..."
    Start-Process "https://www.python.org/downloads/"
    exit 1
}

Step 2 "Checking Git..."
if (-not (Ensure-Git)) {
    Write-Host "       Git not found. Please install from git-scm.com" -ForegroundColor Red
    exit 1
}

Step 3 "Downloading AI Assistant..."
if (Test-Path $installDir) {
    Write-Host "       Folder exists. Updating..." -ForegroundColor Yellow
    Push-Location $installDir
    git pull --quiet
    Pop-Location
} else {
    git clone $repoUrl $installDir
    if ($LASTEXITCODE -ne 0) {
        Write-Host "       Download failed." -ForegroundColor Red
        exit 1
    }
}
Write-Host "       OK" -ForegroundColor Green

Push-Location $installDir

Step 4 "Setting up environment (this may take a few minutes)..."
if (-not (Test-Path "venv")) {
    python -m venv venv
}
& ".\venv\Scripts\Activate.ps1"
python -m pip install --upgrade pip --quiet 2>$null
pip install -r requirements.txt --quiet
Write-Host "       OK" -ForegroundColor Green

Step 5 "Configuration..."
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host ""
    Write-Host "  ============================================" -ForegroundColor Magenta
    Write-Host "  Add your OpenAI API key to .env" -ForegroundColor Magenta
    Write-Host "  Get one at: https://platform.openai.com/api" -ForegroundColor Magenta
    Write-Host "  ============================================" -ForegroundColor Magenta
    Write-Host ""
    $key = Read-Host "  Paste your OpenAI API key (or press Enter to skip)"
    if ($key -ne "") {
        (Get-Content ".env") -replace 'OPENAI_API_KEY=.*', "OPENAI_API_KEY=$key" | Set-Content ".env"
        Write-Host "       Key saved." -ForegroundColor Green
    } else {
        Write-Host "       Skipped. Edit .env later." -ForegroundColor Yellow
    }
}

Step 6 "Launching AI Assistant..."
Write-Host ""
Write-Host "  Type /quit to exit, /voice for voice mode" -ForegroundColor Cyan
Write-Host ""

& ".\venv\Scripts\Activate.ps1"
python main.py
