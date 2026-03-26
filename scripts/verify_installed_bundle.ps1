# Compare installed GitHub Desktop main.js / renderer.js with project Windows\ outputs (hash + size).
# Run from repo root:
#   powershell -ExecutionPolicy Bypass -File scripts\verify_installed_bundle.ps1
# Optional: pin folder under %LOCALAPPDATA%\GitHubDesktop\
#   powershell -ExecutionPolicy Bypass -File scripts\verify_installed_bundle.ps1 -AppFolderName "app-3.5.6"

param(
    [string]$AppFolderName = ""
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$srcMain = Join-Path $root "Windows\main.js"
$srcRen = Join-Path $root "Windows\renderer.js"

if (-not (Test-Path $srcMain) -or -not (Test-Path $srcRen)) {
    Write-Error "Missing $srcMain or $srcRen. Run: python scripts\apply_zh_patch.py"
}

if ($AppFolderName) {
    $appDir = Join-Path $env:LOCALAPPDATA "GitHubDesktop\$AppFolderName"
    if (-not (Test-Path $appDir)) {
        Write-Error "Not found: $appDir"
    }
} else {
    $apps = Get-ChildItem -Path "$env:LOCALAPPDATA\GitHubDesktop\app-*" -Directory -ErrorAction SilentlyContinue |
        Sort-Object { $_.Name } -Descending
    if (-not $apps) {
        Write-Error "No $env:LOCALAPPDATA\GitHubDesktop\app-* found."
    }
    $appDir = $apps[0].FullName
}

$dest = Join-Path $appDir "resources\app"
$dstMain = Join-Path $dest "main.js"
$dstRen = Join-Path $dest "renderer.js"

foreach ($p in @($dstMain, $dstRen)) {
    if (-not (Test-Path -LiteralPath $p)) {
        Write-Error "Not found: $p"
    }
}

Write-Host "GitHub Desktop app folder: $appDir"
Write-Host ""

function Show-FileInfo($label, $path) {
    $item = Get-Item -LiteralPath $path
    $h = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash
    Write-Host $label
    Write-Host "  Path: $path"
    Write-Host "  Size: $($item.Length) bytes"
    Write-Host "  SHA256: $h"
}

Show-FileInfo "Project main.js" $srcMain
Show-FileInfo "Installed main.js" $dstMain
Write-Host ""
Show-FileInfo "Project renderer.js" $srcRen
Show-FileInfo "Installed renderer.js" $dstRen
Write-Host ""

$mainMatch = ((Get-FileHash -LiteralPath $srcMain -Algorithm SHA256).Hash -eq (Get-FileHash -LiteralPath $dstMain -Algorithm SHA256).Hash)
$renMatch = ((Get-FileHash -LiteralPath $srcRen -Algorithm SHA256).Hash -eq (Get-FileHash -LiteralPath $dstRen -Algorithm SHA256).Hash)

if ($mainMatch -and $renMatch) {
    Write-Host "OK: Installed files match project Windows\ outputs exactly."
    Write-Host "If main-process error persists, try a clean reinstall of GitHub Desktop, then copy only these two files again."
} else {
    Write-Host "MISMATCH: Installed bundle is not the same as project output."
    if (-not $mainMatch) { Write-Host "  - main.js differs" }
    if (-not $renMatch) { Write-Host "  - renderer.js differs" }
    Write-Host "Close GitHub Desktop, then run: powershell -ExecutionPolicy Bypass -File scripts\copy_to_github_desktop.ps1"
}

$bytes = [System.IO.File]::ReadAllBytes($dstMain)
if ($bytes.Length -eq 0) {
    Write-Warning 'main.js is empty.'
    exit 1
}
if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
    Write-Warning 'main.js has UTF-8 BOM; project output should be no BOM.'
}
$off = 0
if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) { $off = 3 }
$end = [Math]::Min($off + 100, $bytes.Length - 1)
$slice = $bytes[$off..$end]
$headAscii = -join ($slice | ForEach-Object { if ($_ -ge 32 -and $_ -le 126) { [char]$_ } else { ' ' } })
if ($headAscii -notmatch '/\*!') {
    Write-Warning 'main.js header does not contain /*! (unexpected file).'
}
