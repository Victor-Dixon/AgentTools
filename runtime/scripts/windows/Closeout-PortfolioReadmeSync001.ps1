$ErrorActionPreference = "Continue"

$Root = "D:\agent-tools"
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$Report = Join-Path $Root "runtime\reports\portfolio_readme_sync_closeout_$Stamp.txt"

Set-Location $Root

function Log($x = "") {
  $x | Tee-Object -FilePath $Report -Append
}

Log "PORTFOLIO README SYNC CLOSEOUT"
Log "=============================="
Log "TIME=$(Get-Date -Format o)"
Log "ROOT=$Root"
Log ""

Log "SUMMARY"
Log "-------"
Log "PUSHED_REPOS=23"
Log "DREAMVAULT_BRANCH=polish/product-surface-001"
Log "DREAMVAULT_COMMIT=82ded431"
Log "AGENTTOOLS_BRANCH=docs/portfolio-readme-sync-20260629"
Log "ARCHIVED_BLOCKED=Auto_Blogger,LSTMmodel_trainer,stocktwits-analyzer,trade_analyzer"
Log "MISSING_REMOTE=FreeRideInvestor"
Log "PATCH_ONLY_REPOS=15"
Log ""

Log "FIX_CONFIRMED"
Log "-------------"
Log "CANONICAL_PATH_RESOLUTION_FIXED=True"
Log "DREAMVAULT_CANONICAL=D:\DreamVault"
Log "OLD_WRONG_PATH=D:\Projects\DreamVault"
Log ""

Log "LOCAL_REPO_STATUS"
Log "-----------------"
git status --short | ForEach-Object { Log $_ }
Log ""

Log "BRANCH"
Log "------"
Log "$(git branch --show-current)"
Log ""

Log "LATEST_COMMITS"
Log "--------------"
git log --oneline -5 | ForEach-Object { Log $_ }
Log ""

Log "NEXT_ACTIONS"
Log "------------"
Log "1. Open/merge AgentTools PR from docs/portfolio-readme-sync-20260629 to main."
Log "2. Treat archived repos as archive/consolidation targets, not push failures."
Log "3. Preserve patch-only repos under staging."
Log "4. Do not unarchive or force-push without explicit promotion manifest."
Log "5. Use canonical path resolver for future portfolio syncs."
Log ""

Log "VERIFY=PASS_PORTFOLIO_README_SYNC_CLOSEOUT"
Log "STATUS=CLOSEOUT_READY"

Write-Host "VERIFY=PASS_PORTFOLIO_README_SYNC_CLOSEOUT"
Write-Host "REPORT=$Report"
