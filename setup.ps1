#!/usr/bin/env pwsh
#
# Development environment setup for Windows.
#
#   .\setup.ps1              install what is missing, set up both environments, run the tests
#   .\setup.ps1 --check      report what is installed and what is out of date, change nothing
#   .\setup.ps1 --tauri      also check the Rust toolchain for desktop development
#   .\setup.ps1 --help       full option list
#
# This script only bootstraps bun and uv, because the rest of the setup is
# written in TypeScript and needs bun to run. Everything after that lives in
# scripts/setup.ts, so there is one copy of the real logic rather than one per
# platform.
#
# If PowerShell refuses to run this file, either unblock it for the session:
#   powershell -ExecutionPolicy Bypass -File .\setup.ps1
# or run the underlying steps by hand — see
# docs/content/Development/Start Here.md

$ErrorActionPreference = "Stop"

$checkOnly = $args -contains "--check"
$assumeYes = ($args -contains "--yes") -or ($args -contains "-y")
$missing = $false

function Test-Tool([string] $Name) {
    return $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

if (-not (Test-Tool "git")) {
    Write-Error "git is not installed. Install Git for Windows, then re-run."
    exit 1
}

# Make sure a tool is available, offering to install it if it is not. $BinDir is
# the directory its installer drops binaries into, so a tool installed in this
# same session can be used without opening a new shell.
function Ensure-Tool([string] $Name, [string] $Installer, [string] $BinDir) {
    if (Test-Tool $Name) { return }

    # Installed previously, but this shell's PATH predates it.
    if (Test-Path (Join-Path $BinDir "$Name.exe")) {
        $env:PATH = "$BinDir;$env:PATH"
        Write-Host "note: using $BinDir\$Name.exe (not on your PATH - add it to your environment)"
        return
    }

    if ($script:checkOnly) {
        Write-Host "  missing: $Name"
        $script:missing = $true
        return
    }

    if (-not $script:assumeYes) {
        Write-Host ""
        Write-Host "$Name is not installed. It can be installed with:"
        Write-Host "  $Installer"
        $reply = Read-Host "Install it now? [y/N]"
        if ($reply -notmatch '^(y|yes)$') {
            Write-Host "Aborted. Install $Name yourself, then re-run this script."
            exit 1
        }
    }

    Write-Host ">>> Installing $Name"
    Invoke-Expression $Installer
    $env:PATH = "$BinDir;$env:PATH"

    if (-not (Test-Tool $Name)) {
        Write-Error "$Name still is not on PATH after installing. Open a new terminal and re-run."
        exit 1
    }
}

Ensure-Tool "bun" 'Invoke-RestMethod bun.sh/install.ps1 | Invoke-Expression' "$env:USERPROFILE\.bun\bin"
Ensure-Tool "uv" 'Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression' "$env:USERPROFILE\.local\bin"

if ($checkOnly -and $missing) {
    Write-Host ""
    Write-Host "Install the missing tools by running .\setup.ps1 without --check."
    exit 1
}

& bun (Join-Path $PSScriptRoot "scripts\setup.ts") @args
exit $LASTEXITCODE
