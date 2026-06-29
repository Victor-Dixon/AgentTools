param(
  [ValidateSet("Start", "Stop", "Restart", "Verify", "InstallStartup")]
  [string]$Action = "Verify"
)

$ErrorActionPreference = "Continue"

$Root = "D:\agent-tools"
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$ReportDir = Join-Path $Root "runtime\reports"
$Report = Join-Path $ReportDir "dream_workers_hidden_control_$Stamp.txt"

New-Item -ItemType Directory -Force $ReportDir | Out-Null

function Log {
  param([string]$Text = "")
  $Text | Tee-Object -FilePath $Report -Append
}

function Get-PythonExe {
  $cmd = Get-Command python.exe -ErrorAction SilentlyContinue
  if ($cmd -and $cmd.Source) {
    return $cmd.Source
  }

  $fallback = "C:\Users\USER\AppData\Local\Programs\Python\Python311\python.exe"
  if (Test-Path $fallback) {
    return $fallback
  }

  throw "python.exe not found"
}

$Python = Get-PythonExe

$Workers = @(
  [pscustomobject]@{
    Name = "discord_queue_processor"
    Cwd = $Root
    Script = "D:\agent-tools\tools\discord_commander\start_message_queue_processor.py"
    Match = "start_message_queue_processor.py"
    LogPath = "D:\agent-tools\runtime\logs\discord_commander_queue.log"
  },
  [pscustomobject]@{
    Name = "discord_bot_restart_wrapper"
    Cwd = $Root
    Script = "D:\agent-tools\tools\discord_commander\run_unified_discord_bot_with_restart.py"
    Match = "run_unified_discord_bot_with_restart.py|bot_runner|unified_discord_bot"
    LogPath = "D:\agent-tools\runtime\logs\discord_commander_bot.log"
  }
)

function Get-DreamWorkerProcesses {
  $results = @()
  $all = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue

  foreach ($w in $Workers) {
    foreach ($p in $all) {
      if (-not $p.CommandLine) {
        continue
      }

      if ($p.Name -notmatch "python|pythonw|powershell|cmd") {
        continue
      }

      if ($p.CommandLine -match $w.Match) {
        $results += [pscustomobject]@{
          Worker = $w.Name
          ProcessId = $p.ProcessId
          Name = $p.Name
          CommandLine = $p.CommandLine
        }
      }
    }
  }

  $dedup = @{}
  foreach ($r in $results) {
    $dedup[[string]$r.ProcessId] = $r
  }

  return $dedup.Values | Sort-Object ProcessId
}

function Stop-DreamWorkers {
  Log "STOP"
  Log "----"

  $procs = @(Get-DreamWorkerProcesses)

  if ($procs.Count -eq 0) {
    Log "VERIFY=SKIP_NO_WORKERS_RUNNING"
    return
  }

  foreach ($p in $procs) {
    Log "STOPPING worker=$($p.Worker) pid=$($p.ProcessId)"
    Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
  }

  Start-Sleep -Seconds 2

  $after = @(Get-DreamWorkerProcesses)
  if ($after.Count -eq 0) {
    Log "VERIFY=PASS_WORKERS_STOPPED"
  } else {
    Log "VERIFY=WARN_SOME_WORKERS_STILL_RUNNING"
    foreach ($p in $after) {
      Log "STILL_RUNNING worker=$($p.Worker) pid=$($p.ProcessId)"
    }
  }
}

function Start-DreamWorkersHidden {
  Log "START_HIDDEN"
  Log "------------"

  $shell = New-Object -ComObject WScript.Shell

  foreach ($w in $Workers) {
    if (-not (Test-Path $w.Script)) {
      Log "VERIFY=FAIL_SCRIPT_MISSING worker=$($w.Name) script=$($w.Script)"
      continue
    }

    $current = @(Get-DreamWorkerProcesses)
    $already = @($current | Where-Object { $_.Worker -eq $w.Name })

    if ($already.Count -gt 0) {
      Log "SKIP_ALREADY_RUNNING worker=$($w.Name)"
      continue
    }

    $shell.CurrentDirectory = $w.Cwd
    $cmd = "`"$Python`" `"$($w.Script)`""

    Log "STARTING worker=$($w.Name)"
    Log "CWD=$($w.Cwd)"
    Log "CMD=$cmd"

    # WScript.Shell.Run args:
    # 0 = hidden window
    # false = launch and do not wait
    $null = $shell.Run($cmd, 0, $false)

    Start-Sleep -Milliseconds 900
  }

  Start-Sleep -Seconds 4
}

function Verify-DreamWorkers {
  Log "VERIFY"
  Log "------"

  $procs = @(Get-DreamWorkerProcesses)

  if ($procs.Count -eq 0) {
    Log "VERIFY=FAIL_NO_DREAM_WORKERS_RUNNING"
    Log "STATUS=FAILED"
    return
  }

  foreach ($p in $procs) {
    Log "RUNNING worker=$($p.Worker) pid=$($p.ProcessId) name=$($p.Name)"
    Log "CMD=$($p.CommandLine)"

    $gp = Get-Process -Id $p.ProcessId -ErrorAction SilentlyContinue
    if ($gp) {
      Log "WINDOW_HANDLE=$($gp.MainWindowHandle)"
      Log "WINDOW_TITLE=$($gp.MainWindowTitle)"
    }

    Log ""
  }

  foreach ($w in $Workers) {
    Log "LOG_CHECK worker=$($w.Name) path=$($w.LogPath)"

    if (Test-Path $w.LogPath) {
      $item = Get-Item $w.LogPath
      Log "LOG_LAST_WRITE=$($item.LastWriteTime.ToString('o'))"
      Log "LOG_SIZE=$($item.Length)"
      Log "LOG_TAIL:"

      $tail = Get-Content $w.LogPath -Tail 8 -ErrorAction SilentlyContinue
      foreach ($line in $tail) {
        Log "  $line"
      }
    } else {
      Log "WARN_LOG_MISSING path=$($w.LogPath)"
    }

    Log ""
  }

  Log "VERIFY=PASS_DREAM_WORKERS_PRESENT"
  Log "STATUS=VERIFY_COMPLETE"
}

function Install-StartupTask {
  Log "INSTALL_STARTUP"
  Log "---------------"

  $TaskName = "DreamOS AgentTools Hidden Workers"
  $ScriptPath = Join-Path $Root "runtime\scripts\windows\Manage-DreamWorkersHidden001.ps1"

  $TaskAction = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$ScriptPath`" -Action Restart" `
    -WorkingDirectory $Root

  $TaskTrigger = New-ScheduledTaskTrigger -AtLogOn

  $TaskSettings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Hours 0)

  Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $TaskAction `
    -Trigger $TaskTrigger `
    -Settings $TaskSettings `
    -Description "Starts DreamOS AgentTools workers hidden in the logged-in Windows user session." `
    -Force | Out-Null

  Log "VERIFY=PASS_STARTUP_TASK_INSTALLED"
  Log "TASK_NAME=$TaskName"
}

Log "DREAM WORKERS HIDDEN CONTROL"
Log "============================"
Log "TIME=$(Get-Date -Format o)"
Log "ROOT=$Root"
Log "ACTION=$Action"
Log "PYTHON=$Python"
Log ""

if ($Action -eq "Stop") {
  Stop-DreamWorkers
}
elseif ($Action -eq "Start") {
  Start-DreamWorkersHidden
  Verify-DreamWorkers
}
elseif ($Action -eq "Restart") {
  Stop-DreamWorkers
  Start-DreamWorkersHidden
  Verify-DreamWorkers
}
elseif ($Action -eq "Verify") {
  Verify-DreamWorkers
}
elseif ($Action -eq "InstallStartup") {
  Install-StartupTask
  Verify-DreamWorkers
}

Log ""
Log "REPORT=$Report"

Write-Host "REPORT=$Report"
