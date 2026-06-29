$ErrorActionPreference = "Stop"

$Root = "D:\agent-tools"
$Manager = Join-Path $Root "runtime\scripts\windows\Manage-DreamWorkersHidden001.ps1"
$StartupDir = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Startup"
$StartupFile = Join-Path $StartupDir "DreamOS-AgentTools-Hidden-Workers.vbs"

New-Item -ItemType Directory -Force $StartupDir | Out-Null

$Line = 'CreateObject("WScript.Shell").Run "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File ""' + $Manager + '"" -Action Restart", 0, False'

$Line | Set-Content -Encoding ASCII $StartupFile

if (Test-Path $StartupFile) {
  Write-Host "VERIFY=PASS_STARTUP_VBS_INSTALLED"
  Write-Host "STARTUP_FILE=$StartupFile"
  Get-Content $StartupFile
} else {
  Write-Host "VERIFY=FAIL_STARTUP_VBS_INSTALL"
  exit 1
}
