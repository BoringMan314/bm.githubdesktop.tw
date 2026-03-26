# 將 Windows\main.js、Windows\renderer.js 覆蓋到目前本機最新的 GitHub Desktop app 目錄。
# 請先完全關閉 GitHub Desktop 再執行（建議工作管理員結束所有 GitHubDesktop / git 相關處理序）。

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$srcMain = Join-Path $root "Windows\main.js"
$srcRen = Join-Path $root "Windows\renderer.js"

if (-not (Test-Path $srcMain) -or -not (Test-Path $srcRen)) {
    Write-Error "找不到 $srcMain 或 $srcRen，請先執行 python scripts\apply_zh_patch.py"
}

$apps = Get-ChildItem -Path "$env:LOCALAPPDATA\GitHubDesktop\app-*" -Directory -ErrorAction SilentlyContinue |
    Sort-Object { $_.Name } -Descending
if (-not $apps) {
    Write-Error "找不到 $env:LOCALAPPDATA\GitHubDesktop\app-* ，請確認已安裝 GitHub Desktop。"
}

$appDir = $apps[0].FullName
$dest = Join-Path $appDir "resources\app"
if (-not (Test-Path $dest)) {
    Write-Error "找不到目錄: $dest"
}

$pkg = Join-Path $dest "package.json"
$idx = Join-Path $dest "index.html"
if (-not (Test-Path $pkg)) {
    Write-Error "目錄內沒有 package.json，可能不是 GitHub Desktop 的 resources\app（請勿只複製到空資料夾）。`n$dest"
}
if (-not (Test-Path $idx)) {
    Write-Warning "未找到 index.html（少數版本路徑不同）；若仍白屏請確認是否選錯 app-* 資料夾。"
}

$asar = Join-Path $appDir "resources\app.asar"
if (Test-Path $asar) {
    Write-Warning "偵測到 app.asar。一般仍會讀取同層 app\ 內的 main.js；若覆蓋後仍白屏，請改從安裝目錄再確認實際載入的是哪一份 bundle。"
}

Write-Host "目標: $dest"
Copy-Item -LiteralPath $srcMain -Destination (Join-Path $dest "main.js") -Force
Copy-Item -LiteralPath $srcRen -Destination (Join-Path $dest "renderer.js") -Force
Write-Host "已覆蓋 main.js 與 renderer.js。請重新啟動 GitHub Desktop。"
