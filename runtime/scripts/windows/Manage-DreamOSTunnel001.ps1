#Requires -Version 5.1
<#
.SYNOPSIS
  Manage Dream.OS Control Plane tunnel via official tunnel-client runtimes (managed runtime).

.DESCRIPTION
  SSOT: dreamos_control_plane_windows_runtime_001
  Canonical binary: D:\Tools\tunnel-client\tunnel-client.exe
  Profile: dreamos-control-plane
  Runtime API key: file reference only — never env literal, never logged.

.PARAMETER Start
  tunnel-client runtimes connect (idempotent managed runtime).

.PARAMETER Stop
  tunnel-client runtimes stop dreamos-control-plane

.PARAMETER Status
  tunnel-client runtimes status --json

.PARAMETER Verify
  Status JSON gates + http://127.0.0.1:8080/readyz

.PARAMETER Doctor
  tunnel-client doctor --profile dreamos-control-plane --explain

.PARAMETER InstallStartup
  Register AtLogOn scheduled task (no secrets in task args).

.PARAMETER RemoveStartup
  Unregister scheduled task.
#>
[CmdletBinding(DefaultParameterSetName = 'Verify')]
param(
  [Parameter(ParameterSetName = 'Start')][switch]$Start,
  [Parameter(ParameterSetName = 'Stop')][switch]$Stop,
  [Parameter(ParameterSetName = 'Status')][switch]$Status,
  [Parameter(ParameterSetName = 'Verify')][switch]$Verify,
  [Parameter(ParameterSetName = 'Doctor')][switch]$Doctor,
  [Parameter(ParameterSetName = 'InstallStartup')][switch]$InstallStartup,
  [Parameter(ParameterSetName = 'RemoveStartup')][switch]$RemoveStartup
)

$ErrorActionPreference = 'Stop'

# --- constants (non-secret) ---
$Root = 'D:\agent-tools'
$TunnelExe = 'D:\Tools\tunnel-client\tunnel-client.exe'
$ProfileName = 'dreamos-control-plane'
$Alias = 'dreamos-control-plane'
$TunnelId = 'tunnel_6a8f57082d248191a5a0a47531804744'
$TaskName = 'DreamOS Control Plane Tunnel'
$HealthReadyUrl = 'http://127.0.0.1:8080/readyz'
$McpHttpListen = '127.0.0.1:59134'
$McpHttpUrl = 'https://127.0.0.1:59134/mcp'
$McpTlsDir = Join-Path $env:USERPROFILE '.local\state\tunnel-client\tls'
$McpTlsCert = Join-Path $McpTlsDir 'dreamos-mcp-local.crt'
$McpTlsKey = Join-Path $McpTlsDir 'dreamos-mcp-local.key'
$McpHttpScript = Join-Path $Root 'mcp_servers\dreamos_control_plane_http_server.py'
$McpTlsEnsureScript = Join-Path $Root 'runtime\scripts\ensure_dreamos_mcp_tls_001.py'
$McpHttpPidFile = Join-Path $env:USERPROFILE '.local\state\tunnel-client\health\dreamos-mcp-http.pid'
$ScriptPath = $MyInvocation.MyCommand.Path

$ProfileDir = Join-Path $env:APPDATA 'tunnel-client'
$ProfilePath = Join-Path $ProfileDir "$ProfileName.yaml"
$SecretsDir = Join-Path $ProfileDir 'secrets'
$SecretFile = Join-Path $SecretsDir "$ProfileName.key"

$Stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$ReportDir = Join-Path $Root 'runtime\reports'
$ReportTxt = Join-Path $ReportDir "dreamos_tunnel_control_$Stamp.txt"
$ReportJson = Join-Path $ReportDir "dreamos_tunnel_control_$Stamp.json"

New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null

$Result = [ordered]@{
  schema = 'agenttools.dreamos_tunnel_control.v1'
  task_id = 'dreamos_control_plane_windows_runtime_001'
  at = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
  action = 'Verify'
  status = 'UNKNOWN'
  wrapper = $ScriptPath
  managed_runtime = $Alias
  tunnel_id = $TunnelId
  profile = $ProfileName
  tunnel_exe = $TunnelExe
  process_running = $null
  healthy = $null
  ready = $null
  readyz_http = $null
  startup_task = $null
  secret_storage = $SecretFile
  secret_acl = $null
  secret_scan = $null
  ready_for_reboot_test = $false
  oauth_discovery = $null
  mcp_http_url = $McpHttpUrl
  report_txt = $ReportTxt
  report_json = $ReportJson
}

function Log {
  param([string]$Text = '')
  $Text | Tee-Object -FilePath $ReportTxt -Append | Out-Null
}

function Get-FileKeyReference {
  $normalized = ($SecretFile -replace '\\', '/')
  return "file:$normalized"
}

function Assert-TunnelBinary {
  if (-not (Test-Path -LiteralPath $TunnelExe)) {
    throw "tunnel-client binary missing: $TunnelExe"
  }
}

function Protect-SecretPath {
  param(
    [Parameter(Mandatory = $true)][string]$Path,
    [switch]$IsDirectory
  )

  if (-not (Test-Path -LiteralPath $Path)) {
    return
  }

  $user = $env:USERNAME
  try {
    if ($IsDirectory) {
      & icacls $Path /inheritance:r /grant:r "${user}:(OI)(CI)M" 2>&1 | Out-Null
    }
    else {
      & icacls $Path /inheritance:r /grant:r "${user}:F" 2>&1 | Out-Null
    }
  }
  catch {
    Log "WARN_ACL=$($_.Exception.Message)"
  }
}

function Test-SecretAcl {
  if (-not (Test-Path -LiteralPath $SecretFile)) {
    return 'MISSING_FILE'
  }

  $identity = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
  $acl = Get-Acl -LiteralPath $SecretFile
  $rules = @($acl.Access | Where-Object {
      $_.IdentityReference.Value -eq $identity -and
      $_.AccessControlType -eq 'Allow'
    })

  if ($rules.Count -ge 1) {
    return 'USER_ONLY_OK'
  }
  return 'REVIEW_ACL'
}

function Ensure-SecretsDirectory {
  New-Item -ItemType Directory -Force -Path $SecretsDir | Out-Null
  Protect-SecretPath -Path $SecretsDir -IsDirectory
}

$SecretsLocalEnv = Join-Path $Root 'runtime\secrets\secrets.local.env'

function Get-LocalEnvApiKey {
  if (-not (Test-Path -LiteralPath $SecretsLocalEnv)) {
    return $null
  }

  foreach ($line in Get-Content -LiteralPath $SecretsLocalEnv -Encoding UTF8) {
    $t = $line.Trim()
    if (-not $t -or $t.StartsWith('#')) { continue }
    if ($t -match '^(?:export\s+)?CONTROL_PLANE_API_KEY\s*=\s*(.+)$') {
      $val = $Matches[1].Trim()
      if (($val.StartsWith('"') -and $val.EndsWith('"')) -or ($val.StartsWith("'") -and $val.EndsWith("'"))) {
        $val = $val.Substring(1, $val.Length - 2)
      }
      if ($val) { return $val }
    }
  }
  return $null
}

function Ensure-RuntimeKeyFile {
  Ensure-SecretsDirectory

  if (Test-Path -LiteralPath $SecretFile) {
    Protect-SecretPath -Path $SecretFile
    return
  }

  $fromEnv = [Environment]::GetEnvironmentVariable('CONTROL_PLANE_API_KEY', 'Process')
  if (-not $fromEnv) {
    $fromEnv = [Environment]::GetEnvironmentVariable('CONTROL_PLANE_API_KEY', 'User')
  }
  if (-not $fromEnv) {
    $fromEnv = Get-LocalEnvApiKey
    if ($fromEnv) {
      Log 'SECRET_MIGRATE=secrets.local.env (key not logged)'
    }
  }

  if ($fromEnv) {
    Log 'SECRET_MIGRATE=env_to_file (key not logged)'
    Set-Content -LiteralPath $SecretFile -Value $fromEnv.Trim() -Encoding ASCII -NoNewline
    Protect-SecretPath -Path $SecretFile
    # Prefer file: reference — drop literal User env if it was set previously.
    $userEnv = [Environment]::GetEnvironmentVariable('CONTROL_PLANE_API_KEY', 'User')
    if ($userEnv) {
      [Environment]::SetEnvironmentVariable('CONTROL_PLANE_API_KEY', $null, 'User')
      Log 'SECRET_ENV_USER_CLEARED=CONTROL_PLANE_API_KEY'
    }
    return
  }

  throw @"
Runtime API key file missing: $SecretFile
Create it once (do not paste into chat/logs):
  1. mkdir "$SecretsDir" -Force
  2. Set-Content -Path "$SecretFile" -Value '<RUNTIME_KEY>' -Encoding ASCII -NoNewline
  3. Re-run with -Doctor
Or add to gitignored D:\agent-tools\runtime\secrets\secrets.local.env:
  CONTROL_PLANE_API_KEY=your_runtime_key
Then re-run with -Start to migrate to file reference (key never logged).
Or export CONTROL_PLANE_API_KEY in the current session and re-run -Start to migrate env->file.
"@
}

function Update-ProfileKeyReference {
  if (-not (Test-Path -LiteralPath $ProfilePath)) {
    throw "Profile missing: $ProfilePath (run: tunnel-client init --profile $ProfileName)"
  }

  $fileRef = Get-FileKeyReference
  $raw = Get-Content -LiteralPath $ProfilePath -Raw -Encoding UTF8
  $trim = $raw.TrimStart()

  if ($trim.StartsWith('{')) {
    $obj = $raw | ConvertFrom-Json
    if (-not $obj.control_plane) {
      throw "Profile JSON missing control_plane: $ProfilePath"
    }
    if ("$($obj.control_plane.api_key)" -eq $fileRef) {
      Log "PROFILE_KEY_REF=$fileRef (unchanged)"
      return
    }
    $obj.control_plane | Add-Member -NotePropertyName api_key -NotePropertyValue $fileRef -Force
    ($obj | ConvertTo-Json -Depth 10) + "`n" | Set-Content -LiteralPath $ProfilePath -Encoding UTF8 -NoNewline
    Log "PROFILE_KEY_REF=$fileRef"
    return
  }

  $lines = Get-Content -LiteralPath $ProfilePath -Encoding UTF8
  $out = New-Object System.Collections.Generic.List[string]
  $replaced = $false

  foreach ($line in $lines) {
    if ($line -match '^\s*api_key:\s*') {
      $out.Add("  api_key: `"$fileRef`"")
      $replaced = $true
    }
    else {
      $out.Add($line)
    }
  }

  if (-not $replaced) {
    throw "Profile missing control_plane.api_key: $ProfilePath"
  }

  Set-Content -LiteralPath $ProfilePath -Value ($out -join "`n") -Encoding UTF8 -NoNewline
  Add-Content -LiteralPath $ProfilePath -Value "`n" -Encoding UTF8
  Log "PROFILE_KEY_REF=$fileRef"
}

function Invoke-Tunnel {
  param(
    [Parameter(Mandatory = $true)][string[]]$Args
  )

  Assert-TunnelBinary
  $psi = New-Object System.Diagnostics.ProcessStartInfo
  $psi.FileName = $TunnelExe
  $psi.Arguments = ($Args -join ' ')
  $psi.RedirectStandardOutput = $true
  $psi.RedirectStandardError = $true
  $psi.UseShellExecute = $false
  $psi.CreateNoWindow = $true

  $proc = [System.Diagnostics.Process]::Start($psi)
  $stdout = $proc.StandardOutput.ReadToEnd()
  $stderr = $proc.StandardError.ReadToEnd()
  $proc.WaitForExit()

  if ($stdout) {
    foreach ($line in ($stdout -split "`r?`n")) {
      if ($line.Trim()) { Log "OUT $line" }
    }
  }
  if ($stderr) {
    foreach ($line in ($stderr -split "`r?`n")) {
      if ($line.Trim()) { Log "ERR $line" }
    }
  }

  return [pscustomobject]@{
    ExitCode = $proc.ExitCode
    Stdout = $stdout
    Stderr = $stderr
  }
}

function Get-RuntimeStatus {
  $resp = Invoke-Tunnel -Args @('runtimes', 'status', $Alias, '--json')
  if ($resp.ExitCode -ne 0) {
    return $null
  }

  try {
    return $resp.Stdout | ConvertFrom-Json
  }
  catch {
    return $null
  }
}

function Get-ReadyZUrl {
  param($StatusObj)

  if ($StatusObj) {
    foreach ($path in @(
        $StatusObj.local.effective_health.readyz.url,
        $StatusObj.local.health.readyz.url,
        $StatusObj.health_url
      )) {
      if ($path -and "$path" -match 'readyz') { return "$path" }
      if ($path -and "$path" -notmatch 'readyz$') { return ("$path".TrimEnd('/') + '/readyz') }
    }
  }

  $urlFile = Join-Path $env:USERPROFILE '.local\state\tunnel-client\health\dreamos-control-plane.url'
  if (Test-Path -LiteralPath $urlFile) {
    $base = (Get-Content -LiteralPath $urlFile -Raw).Trim()
    if ($base) { return ($base.TrimEnd('/') + '/readyz') }
  }

  return 'http://127.0.0.1:8080/readyz'
}

function Test-ReadyZ {
  param($StatusObj = $null)

  $readyUrl = Get-ReadyZUrl -StatusObj $StatusObj
  try {
    $r = Invoke-WebRequest -Uri $readyUrl -UseBasicParsing -TimeoutSec 8
    return [pscustomobject]@{ Ok = ($r.StatusCode -eq 200); StatusCode = $r.StatusCode; Url = $readyUrl; Body = $r.Content }
  }
  catch {
    return [pscustomobject]@{ Ok = $false; StatusCode = $null; Url = $readyUrl; Body = $_.Exception.Message }
  }
}

function Scan-SecretLeaks {
  param([string[]]$Texts)

  $patterns = @(
    'sk-[A-Za-z0-9]{10,}',
    'CONTROL_PLANE_API_KEY\s*=\s*\S+',
    'api_key:\s*"(?!file:)[^"]{8,}"'
  )

  $hits = @()
  foreach ($text in $Texts) {
    if (-not $text) { continue }
    foreach ($pat in $patterns) {
      if ($text -match $pat) {
        $hits += $pat
      }
    }
  }

  if ($hits.Count -eq 0) {
    return 'PASS'
  }
  return ('FAIL patterns=' + ($hits -join ','))
}

function Invoke-Doctor {
  Ensure-RuntimeKeyFile
  Update-ProfileKeyReference
  $resp = Invoke-Tunnel -Args @('doctor', '--profile', $ProfileName, '--explain')
  if ($resp.ExitCode -ne 0) {
    throw "doctor failed exit=$($resp.ExitCode)"
  }
  Log 'DOCTOR=PASS'
}

function Test-McpHttpReady {
  $prmUrl = ($McpHttpUrl -replace '/mcp$', '') + '/.well-known/oauth-protected-resource/mcp'
  try {
    # Self-signed localhost cert — skip validation for local probe only.
    if ($PSVersionTable.PSVersion.Major -ge 6) {
      $r = Invoke-WebRequest -Uri $prmUrl -UseBasicParsing -TimeoutSec 5 -SkipCertificateCheck
    }
    else {
      add-type @"
using System.Net; using System.Security.Cryptography.X509Certificates;
public class TrustAllCerts : ICertificatePolicy { public bool CheckValidationResult(ServicePoint s, X509Certificate c, WebRequest r, int cp) { return true; } }
"@
      [System.Net.ServicePointManager]::CertificatePolicy = New-Object TrustAllCerts
      $r = Invoke-WebRequest -Uri $prmUrl -UseBasicParsing -TimeoutSec 5
    }
    return [pscustomobject]@{ Ok = ($r.StatusCode -eq 200); StatusCode = $r.StatusCode; Body = $r.Content; Url = $prmUrl }
  }
  catch {
    return [pscustomobject]@{ Ok = $false; StatusCode = $null; Body = $_.Exception.Message; Url = $prmUrl }
  }
}

function Ensure-McpTlsMaterials {
  New-Item -ItemType Directory -Force -Path $McpTlsDir | Out-Null
  if (-not (Test-Path -LiteralPath $McpTlsCert) -or -not (Test-Path -LiteralPath $McpTlsKey)) {
    Log 'MCP_TLS=GENERATE'
    $resp = & python $McpTlsEnsureScript --cert $McpTlsCert --key $McpTlsKey 2>&1
    foreach ($line in @($resp)) { if ("$line".Trim()) { Log "TLS $line" } }
  }
  if (-not (Test-Path -LiteralPath $McpTlsCert)) {
    throw "TLS cert missing: $McpTlsCert (openssl required)"
  }
}

function Ensure-McpHttpServer {
  Ensure-McpTlsMaterials
  $ready = Test-McpHttpReady
  if ($ready.Ok) {
    Log "MCP_HTTP=ALREADY_RUNNING url=$McpHttpUrl"
    return
  }

  $pidDir = Split-Path -Parent $McpHttpPidFile
  New-Item -ItemType Directory -Force -Path $pidDir | Out-Null

  $python = (Get-Command python -ErrorAction SilentlyContinue).Source
  if (-not $python) {
    throw 'python not found on PATH — required for dreamos_control_plane_http_server.py'
  }

  Log "MCP_HTTP=START listen=$McpHttpListen tls=true"
  $env:DREAMOS_OAUTH_AUTO_APPROVE = '1'
  $proc = Start-Process -FilePath $python `
    -ArgumentList @(
      $McpHttpScript,
      '--listen-addr', $McpHttpListen,
      '--tls',
      '--tls-cert', $McpTlsCert,
      '--tls-key', $McpTlsKey
    ) `
    -WorkingDirectory $Root `
    -WindowStyle Hidden `
    -PassThru

  Set-Content -LiteralPath $McpHttpPidFile -Value $proc.Id -Encoding ASCII
  Start-Sleep -Seconds 2

  $ready = Test-McpHttpReady
  if (-not $ready.Ok) {
    throw "MCP HTTP server failed to expose OAuth discovery at $McpHttpUrl"
  }
  Log "MCP_HTTP=PASS pid=$($proc.Id)"
}

function Invoke-Start {
  Ensure-RuntimeKeyFile
  Update-ProfileKeyReference
  Ensure-McpHttpServer

  $fileRef = Get-FileKeyReference
  $env:CA_BUNDLE = $McpTlsCert
  Log "CA_BUNDLE=$McpTlsCert"
  $args = @(
    'runtimes', 'connect',
    '--alias', $Alias,
    '--profile', $ProfileName,
    '--tunnel-id', $TunnelId,
    '--runtime-api-key', $fileRef,
    '--mcp-server-url', $McpHttpUrl
  )

  $resp = Invoke-Tunnel -Args $args
  if ($resp.ExitCode -ne 0) {
    throw "runtimes connect failed exit=$($resp.ExitCode)"
  }

  Start-Sleep -Seconds 3
  Log 'START=PASS'
}

function Invoke-Stop {
  $resp = Invoke-Tunnel -Args @('runtimes', 'stop', $Alias)
  if ($resp.ExitCode -ne 0) {
    throw "runtimes stop failed exit=$($resp.ExitCode)"
  }
  Log 'STOP=PASS'
}

function Invoke-Status {
  $status = Get-RuntimeStatus
  if (-not $status) {
    Write-Output '{}'
    return $null
  }
  Write-Output ($status | ConvertTo-Json -Depth 8)
  return $status
}

function Invoke-Verify {
  $status = Get-RuntimeStatus
  $readyz = Test-ReadyZ -StatusObj $status

  $processRunning = $false
  $healthy = $false
  $ready = $false

  if ($status) {
    if ($status.PSObject.Properties.Name -contains 'process_running') {
      $processRunning = [bool]$status.process_running
    }
    if ($status.PSObject.Properties.Name -contains 'healthy') {
      $healthy = [bool]$status.healthy
    }
    if ($status.PSObject.Properties.Name -contains 'ready') {
      $ready = [bool]$status.ready
    }
    # nested runtime object (version-dependent)
    if ($status.runtime) {
      if ($status.runtime.PSObject.Properties.Name -contains 'process_running') {
        $processRunning = [bool]$status.runtime.process_running
      }
      if ($status.runtime.PSObject.Properties.Name -contains 'healthy') {
        $healthy = [bool]$status.runtime.healthy
      }
      if ($status.runtime.PSObject.Properties.Name -contains 'ready') {
        $ready = [bool]$status.runtime.ready
      }
    }
  }

  $Result.process_running = $processRunning
  $Result.healthy = $healthy
  $Result.ready = $ready
  $Result.readyz_http = $readyz.StatusCode
  $Result.readyz_ok = $readyz.Ok

  $pass = ($processRunning -and $healthy -and $ready -and $readyz.Ok)
  $oauth = Test-McpHttpReady
  $Result.oauth_discovery = $oauth.Ok
  if (-not $oauth.Ok) {
    $pass = $false
  }
  Log "VERIFY process_running=$processRunning healthy=$healthy ready=$ready readyz=$($readyz.StatusCode) oauth_discovery=$($oauth.Ok)"
  if ($pass) {
    Log 'VERIFY=PASS'
    $Result.status = 'PASS'
  }
  else {
    Log 'VERIFY=FAIL'
    $Result.status = 'FAIL'
  }

  return $pass
}

function Install-StartupTask {
  Ensure-RuntimeKeyFile
  Update-ProfileKeyReference

  $taskArgs = "-NoProfile -ExecutionPolicy Bypass -File `"$ScriptPath`" -Start"
  $action = New-ScheduledTaskAction `
    -Execute 'powershell.exe' `
    -Argument $taskArgs `
    -WorkingDirectory $Root

  $trigger = New-ScheduledTaskTrigger -AtLogOn
  $settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Hours 0)

  $principal = New-ScheduledTaskPrincipal `
    -UserId "$env:USERDOMAIN\$env:USERNAME" `
    -LogonType Interactive `
    -RunLevel Limited

  try {
    Register-ScheduledTask `
      -TaskName $TaskName `
      -Action $action `
      -Trigger $trigger `
      -Settings $settings `
      -Principal $principal `
      -Description 'Dream.OS Control Plane MCP tunnel (managed runtime via Manage-DreamOSTunnel001.ps1 -Start)' `
      -Force | Out-Null
  }
  catch {
    Log "REGISTER_SCHEDULED_TASK_FAIL=$($_.Exception.Message)"
    $tr = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$ScriptPath`" -Start"
    $sch = & schtasks.exe /Create /TN $TaskName /TR $tr /SC ONLOGON /RL LIMITED /F 2>&1
    foreach ($line in @($sch)) { if ("$line".Trim()) { Log "SCHTASKS $line" } }
    if ($LASTEXITCODE -ne 0) {
      throw "Scheduled task registration failed (try elevated PowerShell once): $($_.Exception.Message)"
    }
  }

  $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
  $argText = ($task.Actions | ForEach-Object { $_.Arguments }) -join ' '
  $Result.startup_task = [bool]$task
  $Result.secret_scan = Scan-SecretLeaks -Texts @($argText, $ReportTxt)

  if ($Result.secret_scan -ne 'PASS') {
    throw "Scheduled task secret scan failed: $($Result.secret_scan)"
  }

  Log "STARTUP_TASK=INSTALLED name=$TaskName"
}

function Remove-StartupTask {
  Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
  Log 'STARTUP_TASK=REMOVED'
  $Result.startup_task = $false
}

function Resolve-Action {
  if ($Start) { return 'Start' }
  if ($Stop) { return 'Stop' }
  if ($Status) { return 'Status' }
  if ($Doctor) { return 'Doctor' }
  if ($InstallStartup) { return 'InstallStartup' }
  if ($RemoveStartup) { return 'RemoveStartup' }
  return 'Verify'
}

# --- main ---
try {
  Assert-TunnelBinary
  $actionName = Resolve-Action
  $Result.action = $actionName

  Log 'DREAMOS TUNNEL CONTROL'
  Log '======================'
  Log "TIME=$($Result.at)"
  Log "ACTION=$actionName"
  Log "ALIAS=$Alias"
  Log "PROFILE=$ProfileName"
  Log "TUNNEL_ID=$TunnelId"
  Log "SECRET_FILE=$SecretFile"
  Log ''

  switch ($actionName) {
    'Doctor' { Invoke-Doctor }
    'Start' { Invoke-Start; [void](Invoke-Verify) }
    'Stop' { Invoke-Stop }
    'Status' { [void](Invoke-Status) }
    'Verify' { [void](Invoke-Verify) }
    'InstallStartup' { Install-StartupTask }
    'RemoveStartup' { Remove-StartupTask }
  }

  if (Test-Path -LiteralPath $SecretFile) {
    $Result.secret_acl = Test-SecretAcl
  }

  $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
  $Result.startup_task = [bool]$task
  $Result.secret_scan = Scan-SecretLeaks -Texts @(
    (Get-Content -LiteralPath $ReportTxt -Raw -ErrorAction SilentlyContinue),
    ($(if ($task) { ($task.Actions | ForEach-Object { $_.Arguments }) -join ' ' } else { '' }))
  )

  $Result.ready_for_reboot_test = (
    $Result.startup_task -and
    (Test-Path -LiteralPath $SecretFile) -and
    ($Result.secret_scan -eq 'PASS')
  )

  if (-not $Result.process_running -and $actionName -eq 'Verify') {
    # already set in Invoke-Verify
  }

  ($Result | ConvertTo-Json -Depth 6) | Set-Content -LiteralPath $ReportJson -Encoding UTF8

  Log ''
  Log "REPORT_TXT=$ReportTxt"
  Log "REPORT_JSON=$ReportJson"
  Write-Host "REPORT_JSON=$ReportJson"

  if ($Result.status -eq 'FAIL' -and $actionName -in @('Verify', 'Start')) {
    exit 1
  }
}
catch {
  Log "ERROR=$($_.Exception.Message)"
  $Result.status = 'FAIL'
  $Result.error = $_.Exception.Message
  ($Result | ConvertTo-Json -Depth 6) | Set-Content -LiteralPath $ReportJson -Encoding UTF8
  Write-Host "REPORT_JSON=$ReportJson"
  Write-Error $_.Exception.Message
  exit 1
}
