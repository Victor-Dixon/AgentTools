$ErrorActionPreference = "Continue"

$Root = "D:\agent-tools"
$Keys = @("DISCORD_BOT_TOKEN", "DISCORD_TOKEN")

function TokenReport($Scope, $Key, $Value) {
  if (-not $Value) {
    Write-Host "$Scope $Key MISSING"
    return
  }

  $trimmed = $Value.Trim()
  $hasBotPrefix = $trimmed.StartsWith("Bot ")
  $hasQuotes = ($trimmed.StartsWith('"') -or $trimmed.StartsWith("'") -or $trimmed.EndsWith('"') -or $trimmed.EndsWith("'"))
  $dotCount = ([regex]::Matches($trimmed, "\.")).Count

  $sha = [System.Security.Cryptography.SHA256]::Create()
  $bytes = [System.Text.Encoding]::UTF8.GetBytes($trimmed)
  $hash = [BitConverter]::ToString($sha.ComputeHash($bytes)).Replace("-", "").Substring(0, 12)

  Write-Host "$Scope $Key SET len=$($trimmed.Length) dots=$dotCount bot_prefix=$hasBotPrefix quotes=$hasQuotes hash12=$hash"
}

Write-Host "PROCESS_AND_USER_ENV"
Write-Host "--------------------"
foreach ($key in $Keys) {
  TokenReport "PROCESS" $key ([Environment]::GetEnvironmentVariable($key, "Process"))
  TokenReport "USER" $key ([Environment]::GetEnvironmentVariable($key, "User"))
  TokenReport "MACHINE" $key ([Environment]::GetEnvironmentVariable($key, "Machine"))
}

Write-Host ""
Write-Host "LOCAL_ENV_FILES"
Write-Host "---------------"
$EnvFiles = @(
  "$Root\.env",
  "$Root\.env.local",
  "$Root\runtime\.env",
  "$Root\runtime\config\.env"
)

foreach ($f in $EnvFiles) {
  if (-not (Test-Path $f)) { continue }

  Write-Host "ENV_FILE=$f"
  foreach ($line in Get-Content $f) {
    if ($line -match "^\s*(DISCORD_BOT_TOKEN|DISCORD_TOKEN)\s*=\s*(.*)\s*$") {
      $key = $matches[1]
      $val = $matches[2].Trim().Trim('"').Trim("'")
      TokenReport "FILE:$f" $key $val
    }
  }
}

Write-Host ""
Write-Host "CODE_TOKEN_REFERENCES"
Write-Host "---------------------"
Get-ChildItem tools,src,agent_tools -Recurse -File -ErrorAction SilentlyContinue |
  Where-Object { $_.Length -lt 500000 -and $_.FullName -notmatch "\\(__pycache__|\.venv|node_modules)(\\|$)" } |
  Select-String -Pattern "DISCORD_BOT_TOKEN|DISCORD_TOKEN|getenv" -ErrorAction SilentlyContinue |
  Select-Object -First 80 |
  ForEach-Object { Write-Host "$($_.Path):$($_.LineNumber): $($_.Line)" }
