param(
    [Parameter(Mandatory=$true)]
    [string]$RepoUrl,
    [string]$MainBranch = 'main',
    [string]$DevelopBranch = 'develop'
)

# Push current repository to an HTTPS remote origin.
# Usage: .\push_to_github_https.ps1 -RepoUrl https://github.com/YOUR_USER/filemgr.git

Set-Location -Path (Join-Path $PSScriptRoot '..')

if (-not (Test-Path -Path .git)) {
    Write-Host "No git repo found. Initialize and commit current files? (Y/N)"
    $ans = Read-Host
    if ($ans -ne 'Y') { Write-Host "Aborted"; exit 1 }
    git init -b $MainBranch
    git add .
    git commit -m 'Initial commit: FileMgr CLI prototype' -q
} else {
    Write-Host 'Git repo found.'
}

# Check existing remote
$existing = git remote -v | Select-String -Pattern '^origin\s' -Quiet
if ($existing) {
    Write-Host 'A remote named origin already exists. Use `git remote remove origin` and re-run or press Y to overwrite.'
    $overwrite = Read-Host -Prompt "Overwrite remote 'origin'? (Y/N)"
    if ($overwrite -eq 'Y') {
        git remote remove origin
    } else {
        Write-Host 'Aborted by user.'
        exit 0
    }
}

# Add remote
Write-Host "Adding origin: $RepoUrl"
git remote add origin $RepoUrl

# Push main and develop branches
Write-Host "Pushing $MainBranch and $DevelopBranch to origin..."
git push -u origin $MainBranch
if (git rev-parse --verify $DevelopBranch 2>$null) {
    git push -u origin $DevelopBranch
} else {
    Write-Host "$DevelopBranch not present locally; creating and pushing from current HEAD"
    git checkout -b $DevelopBranch
    git push -u origin $DevelopBranch
    git checkout $MainBranch
}

Write-Host 'Push complete. Create a Pull Request via the GitHub web UI or gh CLI.'
