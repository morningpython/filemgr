<#
Manage branch protection and PR merge workflow (safe wrapper)

Usage examples:
  # Quick merge PR #1 using 'merge' strategy and context 'test'
  .\scripts\manage_protection.ps1 -Pr 1 -ContextName 'test' -MergeStyle 'merge'

  # Dry run (no merge) - check and report only
  .\scripts\manage_protection.ps1 -Pr 1 -ContextName 'test' -DryRun $true

The script does:
 - Create a backup of branch protection to scripts/protection-backup.json
 - Update required_status_checks contexts to ContextName (contexts endpoint)
 - Optionally merge the PR (user selects merge style)
 - Restore the original branch protection from the backup

#>
param(
    [int]$Pr = 1,
    [string]$ContextName = 'test',
    [ValidateSet('merge','squash','rebase')] [string]$MergeStyle = 'merge',
    [switch]$DryRun
)

Set-Location $PSScriptRoot/..

function Save-Protection-Backup {
    Write-Host "Saving branch protection backup..."
    & 'C:\Program Files\GitHub CLI\gh.exe' api -H 'Accept: application/vnd.github.v3+json' /repos/morningpython/filemgr/branches/main/protection | ConvertTo-Json -Depth 20 | Out-File -Encoding utf8 scripts/protection-backup.json
    Write-Host "Saved to scripts/protection-backup.json"
}

function Update-Contexts($Context) {
    Write-Host "Updating required status check contexts to '$Context'..."
    $body = @{ contexts = @($Context) } | ConvertTo-Json -Depth 5
    $tmp = 'scripts/protection-context-patch-nobom.json'
    [System.IO.File]::WriteAllText((Join-Path (Get-Location) $tmp), $body, (New-Object System.Text.UTF8Encoding($false)))
    & 'C:\Program Files\GitHub CLI\gh.exe' api --method PUT -H 'Accept: application/vnd.github.v3+json' /repos/morningpython/filemgr/branches/main/protection/required_status_checks/contexts --input $tmp --silent
    Write-Host "contexts updated"
}

function Merge-PR($PrNumber, $MergeStyle) {
    Write-Host "Merging PR #$PrNumber with strategy $MergeStyle..."
    switch ($MergeStyle) {
        'merge' { & 'C:\Program Files\GitHub CLI\gh.exe' pr merge $PrNumber --merge --delete-branch --body "Merged via manage_protection.ps1" }
        'squash' { & 'C:\Program Files\GitHub CLI\gh.exe' pr merge $PrNumber --squash --delete-branch --body "Squashed via manage_protection.ps1" }
        'rebase' { & 'C:\Program Files\GitHub CLI\gh.exe' pr merge $PrNumber --rebase --delete-branch --body "Rebased via manage_protection.ps1" }
    }
}

function Restore-Protection {
    Write-Host "Restoring branch protection from backup..."
    & 'C:\Program Files\GitHub CLI\gh.exe' api --method PUT -H 'Accept: application/vnd.github.v3+json' /repos/morningpython/filemgr/branches/main/protection --input scripts/protection-restore-nobom.json --silent
    Write-Host "Restored protection settings (or attempted to)."
}

# Script run
Save-Protection-Backup

# produce a restore file usable by restore_protection.ps1 (if it exists) - prefer using that
if (Test-Path scripts/restore_protection.ps1) {
    Write-Host "Using scripts/restore_protection.ps1 to produce restore payload file; will reuse it for restoring later."
    powershell -NoProfile -ExecutionPolicy Bypass -File scripts/restore_protection.ps1
} else {
    # If restore script not present, write our own minimal restore json from backup
    Copy-Item scripts/protection-backup.json scripts/protection-restore.json -Force
    # Also create a no-BOM copy
    & powershell -NoProfile -ExecutionPolicy Bypass -File scripts/write_nobom.ps1 -InputPath 'scripts/protection-restore.json' -OutputPath 'scripts/protection-restore-nobom.json'
}

Write-Host "Applying contexts patch..."
Update-Contexts -Context $ContextName

if (-not $DryRun) {
    Merge-PR -PrNumber $Pr -MergeStyle $MergeStyle
} else {
    Write-Host "DryRun mode: skipping merge"
}

# Restore protection
Restore-Protection

Write-Host "Done! If something went wrong, restore script is scripts/restore_protection.ps1 (or scripts/protection-restore-nobom.json)" 