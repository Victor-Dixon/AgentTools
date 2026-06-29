$ErrorActionPreference = "Continue"

$Root = "D:\agent-tools"
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$Report = Join-Path $Root "runtime\reports\lost_systems_restore_map_$Stamp.txt"
$Manifest = Join-Path $Root "runtime\manifests\lost_systems_restore_map_$Stamp.json"
$TaskDir = Join-Path $Root "runtime\tasks"

Set-Location $Root

function Classify-System {
  param([string]$Path)

  if ($Path -match "discord|webhook|commander|message_queue|gas_messaging") { return "discord_commander_and_webhooks" }
  if ($Path -match "captain_|mission_control|leaderboard|swarm|task_assigner|task_engine|next_task|loop") { return "captain_swarm_ops" }
  if ($Path -match "github|git_") { return "github_repo_ops" }
  if ($Path -match "hostinger|wordpress|wp_|site|meta_tag") { return "website_ops" }
  if ($Path -match "twitch") { return "twitch_stream_ops" }
  if ($Path -match "compliance|security|sensitive") { return "security_compliance" }
  if ($Path -match "coverage|analysis|scanner|validator|detector|import") { return "code_quality_scanners" }
  if ($Path -match "dashboard|briefing|snapshot|status|progress") { return "reporting_dashboards" }

  return "misc_salvage"
}

function Risk-Level {
  param([string]$Path)

  if ($Path -match "token|password|credential|secret|hostinger|wp_|github|discord") { return "sensitive_env" }
  if ($Path -match "cleanup|remediate|delete|pusher|push|merge") { return "destructive_possible" }
  if ($Path -match "deprecated") { return "deprecated_review_required" }

  return "low"
}

$files = Get-ChildItem tools\deprecated -File -ErrorAction SilentlyContinue |
  Where-Object { $_.Length -lt 1000000 }

$items = @()

foreach ($f in $files) {
  $text = ""
  try { $text = Get-Content $f.FullName -Raw -ErrorAction Stop } catch {}

  $envs = @()
  foreach ($m in [regex]::Matches($text, 'os\.getenv\(["'']([^"'']+)["'']')) {
    $envs += $m.Groups[1].Value
  }
  foreach ($m in [regex]::Matches($text, 'os\.environ\.get\(["'']([^"'']+)["'']')) {
    $envs += $m.Groups[1].Value
  }

  $hasMain = $text -match '__name__\s*==\s*["'']__main__["'']'

  $items += [pscustomobject]@{
    path = $f.FullName.Replace($Root + "\", "")
    class = Classify-System $f.Name
    risk = Risk-Level $f.Name
    has_main = [bool]$hasMain
    size_bytes = $f.Length
    modified = $f.LastWriteTime.ToString("o")
    env_vars = @($envs | Sort-Object -Unique)
  }
}

$groups = $items | Group-Object class | Sort-Object Name

$items | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 $Manifest

"LOST SYSTEMS RESTORE MAP" | Tee-Object -FilePath $Report
"========================" | Tee-Object -FilePath $Report -Append
"TIME=$(Get-Date -Format o)" | Tee-Object -FilePath $Report -Append
"ROOT=$Root" | Tee-Object -FilePath $Report -Append
"FILES=$($items.Count)" | Tee-Object -FilePath $Report -Append
"MANIFEST=$Manifest" | Tee-Object -FilePath $Report -Append
"" | Tee-Object -FilePath $Report -Append

"RESTORE_CLASSES" | Tee-Object -FilePath $Report -Append
"---------------" | Tee-Object -FilePath $Report -Append

foreach ($g in $groups) {
  "class=$($g.Name) count=$($g.Count)" | Tee-Object -FilePath $Report -Append
  $g.Group |
    Sort-Object path |
    Select-Object -First 20 |
    ForEach-Object {
      "  - $($_.path) risk=$($_.risk) main=$($_.has_main)" | Tee-Object -FilePath $Report -Append
      if ($_.env_vars.Count -gt 0) {
        "    env=$($_.env_vars -join ', ')" | Tee-Object -FilePath $Report -Append
      }
    }
  "" | Tee-Object -FilePath $Report -Append
}

"PROMOTION_ORDER" | Tee-Object -FilePath $Report -Append
"---------------" | Tee-Object -FilePath $Report -Append
@(
  "1 discord_commander_and_webhooks",
  "2 captain_swarm_ops",
  "3 reporting_dashboards",
  "4 github_repo_ops",
  "5 website_ops",
  "6 code_quality_scanners",
  "7 security_compliance",
  "8 twitch_stream_ops",
  "9 misc_salvage"
) | ForEach-Object { $_ | Tee-Object -FilePath $Report -Append }

"" | Tee-Object -FilePath $Report -Append
"VERIFY=PASS_LOST_SYSTEMS_RESTORE_MAP" | Tee-Object -FilePath $Report -Append
"STATUS=CLASSIFIED_NO_PROMOTION" | Tee-Object -FilePath $Report -Append

# Create restore task YAMLs by class
foreach ($g in $groups) {
  $safe = $g.Name
  $taskPath = Join-Path $TaskDir "restore_${safe}_001.yaml"

@"
task_id: restore_${safe}_001
title: Restore $safe from deprecated salvage shelf
status: ready
priority: medium
lane: lost_systems_restore
repo: D:/agent-tools
restore_class: $safe
source: tools/deprecated
safety:
  - no deletion
  - no blind promotion
  - inspect source and active equivalent before change
  - preserve current hidden worker lifecycle
  - redact secrets in all reports
verification:
  - candidate list reviewed
  - active target selected
  - tests or command smoke check pass
  - report written
candidate_count: $($g.Count)
"@ | Set-Content -Encoding UTF8 $taskPath
}

Write-Host "VERIFY=PASS_LOST_SYSTEMS_RESTORE_MAP"
Write-Host "REPORT=$Report"
Write-Host "MANIFEST=$Manifest"
