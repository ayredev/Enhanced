# Enhanced Language Installer for Windows
# Run as Administrator: powershell -ExecutionPolicy Bypass -File install.ps1

$ErrorActionPreference = "Stop"
$Version = "0.1.0"
$InstallDir = "$env:ProgramFiles\Enhanced"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$SourceDir = Split-Path -Parent $ScriptDir

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " Enhanced $Version — Windows Installer" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check Python
Write-Host "[1/6] Checking Python..." -ForegroundColor Yellow
try {
    $pyVersion = python --version 2>&1
    Write-Host "  Found: $pyVersion" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Python not found. Install Python 3.10+ first." -ForegroundColor Red
    exit 1
}

# 2. Check LLVM/clang
Write-Host "[2/6] Checking LLVM/clang..." -ForegroundColor Yellow
try {
    $clangVersion = clang --version 2>&1 | Select-Object -First 1
    Write-Host "  Found: $clangVersion" -ForegroundColor Green
} catch {
    Write-Host "  WARNING: clang not found. Native compilation will not work." -ForegroundColor Yellow
    Write-Host "  The REPL and IR generation will still work." -ForegroundColor Yellow
}

# 3. Create install directory
Write-Host "[3/6] Installing to $InstallDir..." -ForegroundColor Yellow
if (Test-Path $InstallDir) {
    Remove-Item -Recurse -Force $InstallDir
}
New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null

# Copy entire enhanced/ folder
Copy-Item -Recurse -Force "$SourceDir\*" "$InstallDir\"
Write-Host "  Files copied." -ForegroundColor Green

# 4. Create enhc.bat launcher
Write-Host "[4/6] Creating 'enhc' command..." -ForegroundColor Yellow
$enhcBat = @"
@echo off
python "$InstallDir\enhc.py" %*
"@
$enhcBat | Out-File -FilePath "$InstallDir\enhc.bat" -Encoding ASCII
Copy-Item "$InstallDir\enhc.bat" "$env:SystemRoot\enhc.bat" -Force
Write-Host "  enhc command installed." -ForegroundColor Green

# 5. Create enhanced.bat launcher (REPL)
Write-Host "[5/6] Creating 'enhanced' command..." -ForegroundColor Yellow
$replBat = @"
@echo off
python "$InstallDir\repl\repl.py" %*
"@
$replBat | Out-File -FilePath "$InstallDir\enhanced.bat" -Encoding ASCII
Copy-Item "$InstallDir\enhanced.bat" "$env:SystemRoot\enhanced.bat" -Force
Write-Host "  enhanced command installed." -ForegroundColor Green

# 6. Register .en file extension
Write-Host "[6/6] Registering .en file extension..." -ForegroundColor Yellow
try {
    $null = New-Item -Path "HKCU:\Software\Classes\.en" -Force
    Set-ItemProperty -Path "HKCU:\Software\Classes\.en" -Name "(Default)" -Value "EnhancedFile"
    $null = New-Item -Path "HKCU:\Software\Classes\EnhancedFile" -Force
    Set-ItemProperty -Path "HKCU:\Software\Classes\EnhancedFile" -Name "(Default)" -Value "Enhanced Source File"
    $null = New-Item -Path "HKCU:\Software\Classes\EnhancedFile\shell\open\command" -Force
    Set-ItemProperty -Path "HKCU:\Software\Classes\EnhancedFile\shell\open\command" -Name "(Default)" -Value "python `"$InstallDir\enhc.py`" `"%1`""
    Write-Host "  .en extension registered." -ForegroundColor Green
} catch {
    Write-Host "  WARNING: Could not register .en extension." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host " Enhanced $Version installed successfully!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "  enhc hello.en    — compile a program" -ForegroundColor White
Write-Host "  enhanced         — open the REPL" -ForegroundColor White
Write-Host ""
