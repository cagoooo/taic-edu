param([string]$Notes = "內容更新")
# 一鍵升版：同步 version.json / sw.js 的 BUILD_VERSION / index.html 的 APP_VERSION（UTF-8 無 BOM）
# 用法：powershell -ExecutionPolicy Bypass -File scripts\bump-version.ps1 -Notes "改了什麼"
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$enc  = New-Object System.Text.UTF8Encoding($false)
$today = Get-Date -Format "yyyy.MM.dd"

$vp = Join-Path $root "version.json"; $seq = 1
if (Test-Path $vp) {
  $old = (Get-Content $vp -Raw | ConvertFrom-Json).version
  if ($old -match "^$([regex]::Escape($today))-(\d+)$") { $seq = [int]$Matches[1] + 1 }
}
$ver = "$today-$seq"
[System.IO.File]::WriteAllText($vp, ([ordered]@{version=$ver; notes=$Notes} | ConvertTo-Json), $enc)

foreach ($f in @(
  @("sw.js",      "const BUILD_VERSION = '[^']*';", "const BUILD_VERSION = '$ver';"),
  @("index.html", "var APP_VERSION='[^']*';",       "var APP_VERSION='$ver';")
)) {
  $p = Join-Path $root $f[0]
  $t = [System.IO.File]::ReadAllText($p, [System.Text.Encoding]::UTF8)
  [System.IO.File]::WriteAllText($p, [regex]::Replace($t, $f[1], $f[2]), $enc)
}
Write-Host "bumped -> $ver"
Write-Host "接著：git add -A; git commit -m '...'; git push"
