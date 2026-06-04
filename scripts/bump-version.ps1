param([string]$Notes = "content update")
# Bump version: sync version.json / sw.js BUILD_VERSION / index.html APP_VERSION (UTF-8 no BOM).
# version = date+time (yyyy.MM.dd.HHmm); always increments, no need to read old file.
# Usage: powershell -ExecutionPolicy Bypass -File scripts\bump-version.ps1
# NOTE: keep $Notes ASCII. PowerShell 5.1 reads a no-BOM .ps1 as ANSI/cp950, so Chinese
#       string literals here would be mangled. For Chinese notes, edit version.json directly.
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$enc  = New-Object System.Text.UTF8Encoding($false)
$ver  = Get-Date -Format "yyyy.MM.dd.HHmm"

# version.json
$vp = Join-Path $root "version.json"
[System.IO.File]::WriteAllText($vp, ([ordered]@{ version = $ver; notes = $Notes } | ConvertTo-Json), $enc)

# 同步 sw.js / index.html
foreach ($f in @(
  @("sw.js",      "const BUILD_VERSION = '[^']*';", "const BUILD_VERSION = '$ver';"),
  @("index.html", "var APP_VERSION='[^']*';",       "var APP_VERSION='$ver';")
)) {
  $p = Join-Path $root $f[0]
  $t = [System.IO.File]::ReadAllText($p, [System.Text.Encoding]::UTF8)
  [System.IO.File]::WriteAllText($p, [regex]::Replace($t, $f[1], $f[2]), $enc)
}
Write-Host "bumped -> $ver"
Write-Host "接著：git add -A; git commit; git push"
