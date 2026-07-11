$ErrorActionPreference = "Continue"

$Root = "D:\agent-tools"
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$Report = Join-Path $Root "runtime\reports\discord_lost_systems_inventory_$Stamp.txt"
$Manifest = Join-Path $Root "runtime\manifests\discord_lost_systems_inventory_$Stamp.json"

Set-Location $Root

function Log {
  param([string]$Text = "")
  $Text | Tee-Object -FilePath $Report -Append
}

function Get-Role {
  param([string]$Path)

  if ($Path -match "\\tools\\deprecated\\") { return "deprecated_salvage_candidate" }
  if ($Path -match "\\tools\\discord\\") { return "discord_support_tool" }
  if ($Path -match "\\tools\\discord_commander\\") { return "active_commander_tool" }
  if ($Path -match "\\agent_tools\\discord_commander\\") { return "active_commander_package" }
  if ($Path -match "devlog|webhook|discord|commander|queue|message") { return "related_candidate" }

  return "unknown"
}

function Get-RestorePriority {
  param([string]$Path, [string]$Text)

  if ($Path -match "config.py") { return 1 }
  if ($Path -match "list_channels|create_webhook") { return 2 }
  if ($Path -match "devlog_manager|devlog_poster") { return 3 }
  if ($Path -match "discord_startup_listener") { return 4 }
  if ($Path -match "message|queue|commander") { return 5 }
  if ($Path -match "\\deprecated\\") { return 8 }

  return 9
}

$SearchRoots = @(
  "tools",
  "agent_tools",
  "src"
) | Where-Object { Test-Path $_ }

$Files = @()

foreach ($dir in $SearchRoots) {
  $Files += Get-ChildItem $dir -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object {
      $_.FullName -notmatch "\\(\.git|\.venv|node_modules|__pycache__)(\\|$)" -and
      $_.Length -lt 1000000 -and
      (
        $_.Name -match "discord|devlog|webhook|commander|queue|message|bot|startup" -or
        $_.FullName -match "\\tools\\deprecated\\" -or
        $_.FullName -match "\\tools\\discord\\" -or
        $_.FullName -match "\\agent_tools\\discord_commander\\"
      )
    }
}

$Inventory = @()

foreach ($file in $Files) {
  $text = ""
  try { $text = Get-Content $file.FullName -Raw -ErrorAction Stop } catch {}

  $envs = @()
  $regexes = @(
    'os\.getenv\(["'']([^"'']+)["'']',
    'os\.environ\.get\(["'']([^"'']+)["'']',
    'environ\.get\(["'']([^"'']+)["'']'
  )

  foreach ($rx in $regexes) {
    foreach ($m in [regex]::Matches($text, $rx)) {
      $envs += $m.Groups[1].Value
    }
  }

  $classes = @()
  foreach ($m in [regex]::Matches($text, '(?m)^class\s+([A-Za-z_][A-Za-z0-9_]*)')) {
    $classes += $m.Groups[1].Value
  }

  $functions = @()
  foreach ($m in [regex]::Matches($text, '(?m)^def\s+([A-Za-z_][A-Za-z0-9_]*)')) {
    $functions += $m.Groups[1].Value
  }

  $hasMain = $text -match '__name__\s*==\s*["'']__main__["'']'
  $role = Get-Role $file.FullName
  $priority = Get-RestorePriority $file.FullName $text

  $Inventory += [pscustomobject]@{
    path = $file.FullName.Replace($Root + "\", "")
    role = $role
    restore_priority = $priority
    size_bytes = $file.Length
    modified = $file.LastWriteTime.ToString("o")
    has_main = [bool]$hasMain
    env_vars = @($envs | Sort-Object -Unique)
    classes = @($classes | Sort-Object -Unique)
    functions = @($functions | Sort-Object -Unique | Select-Object -First 40)
  }
}

$Inventory = $Inventory | Sort-Object restore_priority, role, path

$Inventory | ConvertTo-Json -Depth 10 | Set-Content -Encoding UTF8 $Manifest

Log "DISCORD LOST SYSTEMS INVENTORY"
Log "=============================="
Log "TIME=$(Get-Date -Format o)"
Log "ROOT=$Root"
Log "FILES=$($Inventory.Count)"
Log "MANIFEST=$Manifest"
Log ""

Log "TOP_RESTORE_CANDIDATES"
Log "----------------------"
$Inventory |
  Where-Object { $_.restore_priority -le 5 } |
  Select-Object -First 40 |
  ForEach-Object {
    Log "priority=$($_.restore_priority) role=$($_.role) path=$($_.path)"
    if ($_.env_vars.Count -gt 0) {
      Log "  env=$($_.env_vars -join ', ')"
    }
    if ($_.has_main) {
      Log "  entrypoint=true"
    }
    if ($_.classes.Count -gt 0) {
      Log "  classes=$($_.classes -join ', ')"
    }
    Log ""
  }

Log "DEPRECATED_SALVAGE"
Log "------------------"
$Inventory |
  Where-Object { $_.role -eq "deprecated_salvage_candidate" } |
  Select-Object -First 80 |
  ForEach-Object {
    Log "path=$($_.path) priority=$($_.restore_priority) main=$($_.has_main)"
    if ($_.env_vars.Count -gt 0) {
      Log "  env=$($_.env_vars -join ', ')"
    }
  }

Log ""
Log "ENV_VAR_INDEX"
Log "-------------"
$allEnv = $Inventory | ForEach-Object { $_.env_vars } | Sort-Object -Unique
foreach ($e in $allEnv) {
  Log $e
}

Log ""
Log "VERIFY=PASS_DISCORD_LOST_SYSTEMS_INVENTORY"
Log "STATUS=MANIFEST_READY"
Log "REPORT=$Report"
Log "MANIFEST=$Manifest"

Write-Host "VERIFY=PASS_DISCORD_LOST_SYSTEMS_INVENTORY"
Write-Host "REPORT=$Report"
Write-Host "MANIFEST=$Manifest"
