$ErrorActionPreference = "Continue"

$Root = "D:\agent-tools"
$EnvFiles = @(
  "$Root\.env",
  "$Root\.env.local",
  "$Root\runtime\.env",
  "$Root\runtime\config\.env"
)

$Needed = @(
  "DISCORD_BOT_TOKEN",
  "DISCORD_TOKEN",
  "DISCORD_GUILD_ID"
)

Write-Host "DREAM_DISCORD_ENV_CHECK"
Write-Host "======================="

foreach ($f in $EnvFiles) {
  if (Test-Path $f) {
    Write-Host "ENV_FILE_FOUND=$f"
    Get-Content $f | ForEach-Object {
      $line = $_.Trim()
      if (-not $line -or $line.StartsWith("#")) { return }

      if ($line -match "^\s*([^=]+)\s*=\s*(.*)\s*$") {
        $k = $matches[1].Trim()
        $v = $matches[2].Trim().Trim('"').Trim("'")

        if ($k -match "TOKEN|SECRET|KEY|WEBHOOK") {
          if ($v.Length -gt 8) {
            Write-Host "$k=SET_REDACTED len=$($v.Length)"
          } else {
            Write-Host "$k=SET_REDACTED"
          }
        } else {
          Write-Host "$k=$v"
        }
      }
    }
  }
}

Write-Host ""
Write-Host "PROCESS_ENV_VISIBLE_TO_THIS_SHELL"
Write-Host "---------------------------------"
foreach ($k in $Needed) {
  $v = [Environment]::GetEnvironmentVariable($k, "Process")
  $u = [Environment]::GetEnvironmentVariable($k, "User")
  $m = [Environment]::GetEnvironmentVariable($k, "Machine")

  Write-Host "$k process=$([bool]$v) user=$([bool]$u) machine=$([bool]$m)"
}

Write-Host ""
Write-Host "RECENT_BOT_LOG_ERRORS"
Write-Host "---------------------"
$botLog = "$Root\runtime\logs\discord_commander_bot.log"
if (Test-Path $botLog) {
  Get-Content $botLog -Tail 30
} else {
  Write-Host "WARN_BOT_LOG_MISSING=$botLog"
}
