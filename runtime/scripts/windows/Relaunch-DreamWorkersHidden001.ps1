param(
  [switch]$CaptureOnly,
  [switch]$ReplaceVisible
)

$ErrorActionPreference = "Continue"

$Root = (Get-Location).Path
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$Report = Join-Path $Root "runtime\reports\hidden_worker_relaunch_$Stamp.txt"
$Manifest = Join-Path $Root "runtime\manifests\hidden_worker_processes_$Stamp.json"

$Patterns = @(
  "dreamvault.message_bus.processor",
  "agent_tools.discord_commander.message_queue_processor",
  "agent_tools.discord_commander.unified_discord_bot",
  "discord_commander_queue",
  "discord_commander_bot",
  "message_queue_processor",
  "unified_discord_bot"
)

function Log($Text = "") {
  $Text | Tee-Object -FilePath $Report -Append
}

function IsDreamWorker($Process) {
  if (-not $Process.CommandLine) { return $false }

  foreach ($pattern in $Patterns) {
    if ($Process.CommandLine -match [regex]::Escape($pattern)) {
      return $true
    }
  }

  return $false
}

function GetWorkerProcesses {
  Get-CimInstance Win32_Process |
    Where-Object {
      $_.Name -match "python|pythonw|powershell|cmd" -and
      (IsDreamWorker $_)
    } |
    Sort-Object ProcessId |
    Select-Object ProcessId, Name, ExecutablePath, CommandLine
}

function GetWorkingDirFromCommandLine($cmd) {
  if ($cmd -match "D:\\agent-tools") {
    return "D:\agent-tools"
  }

  if ($cmd -match "D:\\DreamVault") {
    return "D:\DreamVault"
  }

  if ($cmd -match "D:\\dreamos-brain") {
    return "D:\dreamos-brain"
  }

  return $Root
}

Log "DREAM WORKER HIDDEN RELAUNCH"
Log "============================"
Log "TIME=$(Get-Date -Format o)"
Log "ROOT=$Root"
Log "CAPTURE_ONLY=$($CaptureOnly.IsPresent)"
Log "REPLACE_VISIBLE=$($ReplaceVisible.IsPresent)"
Log ""

$workers = @(GetWorkerProcesses)

if ($workers.Count -eq 0) {
  Log "VERIFY=FAIL_NO_DREAM_WORKERS_FOUND"
  Log "STATUS=NOOP"
  Write-Host "REPORT=$Report"
  exit 1
}

$workers | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 $Manifest

Log "MATCHED_WORKERS"
Log "---------------"

foreach ($w in $workers) {
  Log "PID=$($w.ProcessId)"
  Log "NAME=$($w.Name)"
  Log "EXE=$($w.ExecutablePath)"
  Log "CMD=$($w.CommandLine)"
  Log ""
}

Log "MANIFEST=$Manifest"
Log ""

if ($CaptureOnly -or -not $ReplaceVisible) {
  Log "VERIFY=PASS_CAPTURE_ONLY"
  Log "STATUS=NO_PROCESS_CHANGED"
  Write-Host "REPORT=$Report"
  Write-Host "MANIFEST=$Manifest"
  exit 0
}

Log "STOPPING_VISIBLE_WORKERS"
Log "------------------------"

foreach ($w in $workers) {
  Log "STOPPING_PID=$($w.ProcessId)"
  Stop-Process -Id $w.ProcessId -Force -ErrorAction SilentlyContinue
}

Start-Sleep -Seconds 2

Log ""
Log "STARTING_HIDDEN_WORKERS"
Log "-----------------------"

$shell = New-Object -ComObject WScript.Shell

foreach ($w in $workers) {
  $cmd = $w.CommandLine
  if (-not $cmd) {
    Log "SKIP_EMPTY_COMMAND_PID=$($w.ProcessId)"
    continue
  }

  $cwd = GetWorkingDirFromCommandLine $cmd
  $shell.CurrentDirectory = $cwd

  Log "CWD=$cwd"
  Log "START_HIDDEN=$cmd"

  # 0 = hidden window, false = do not wait
  $null = $shell.Run($cmd, 0, $false)

  Start-Sleep -Milliseconds 900
}

Start-Sleep -Seconds 4

Log ""
Log "POSTCHECK"
Log "---------"

$post = @(GetWorkerProcesses)

foreach ($p in $post) {
  Log "RUNNING_PID=$($p.ProcessId) NAME=$($p.Name)"
  Log "CMD=$($p.CommandLine)"
}

if ($post.Count -gt 0) {
  Log "VERIFY=PASS_HIDDEN_WORKERS_RELAUNCHED"
  Log "STATUS=BACKGROUND_CONVERSION_COMPLETE"
} else {
  Log "VERIFY=FAIL_WORKERS_NOT_RUNNING_AFTER_RELAUNCH"
  Log "STATUS=FAILED"
  exit 2
}

Write-Host "REPORT=$Report"
Write-Host "MANIFEST=$Manifest"
