param(
    [Parameter(Mandatory=$true)]
    [string]$RepoName,
    [ValidateSet("public", "private")]
    [string]$Visibility = "public",
    [string]$Owner = ""
)

# Creates a GitHub repository using gh CLI if available, otherwise prints instruction
$ErrorActionPreference = 'Stop'

function Check-GhCli {
    $gh = Get-Command gh -ErrorAction SilentlyContinue
    return $gh -ne $null
}

if (-not (Test-Path -Path .git)) {
    Write-Host "Local git repo not found. Initializing..."
    git init -b main
    git add .
    git commit -m "Initial commit: FileMgr CLI prototype" -q
}

if (Check-GhCli) {
    Write-Host "gh CLI detected. Creating remote repo and pushing..."
    $createFlags = @()
    if ($Visibility -eq 'private') { $createFlags += '--private' } else { $createFlags += '--public' }

    if ($Owner -ne '') {
        $full = "$Owner/$RepoName"
        gh repo create $full $createFlags --source . --remote origin --push -y
    }
    else {
        gh repo create $RepoName $createFlags --source . --remote origin --push -y
    }

    Write-Host "Repository created and pushed. You can create pull requests with 'gh pr create' or via the GitHub web UI."
    exit 0
}
else {
    Write-Host "gh CLI not found. Please either install GitHub CLI (https://cli.github.com/) and run this script again, or create a remote repository manually in GitHub and run the following commands:" 
    Write-Host "\n# Example (SSH):\n git remote add origin git@github.com:YOUR_GITHUB_USER/$RepoName.git\n git push -u origin main\n git push -u origin develop\n"
    exit 1
}
