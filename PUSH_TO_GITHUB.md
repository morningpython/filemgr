# How to create a GitHub repository and push this project

1. Create a repository on GitHub (use web UI) with the name you prefer (e.g. `filemgr`). Choose `Public` or `Private` depending on your preference.

2. Add the remote and push
```powershell
# Replace youruser with your GitHub username and repo name
git remote add origin git@github.com:youruser/filemgr.git
# or HTTP: git remote add origin https://github.com/youruser/filemgr.git

git push -u origin main
git push -u origin develop
```

3. Create a pull request on GitHub from `feature/*` branches into `develop` or `main` as your workflow demands.

4. Optional: Set branch protection rules, required CI (Actions) checks, and PR templates in GitHub repository settings.

5. If you prefer to use a personal access token (PAT) for HTTPS pushes, configure credential manager or use the token in remote URL.

### Helper script for HTTPS push
If you prefer an automated script that pushes to an HTTPS remote, use the included script:

```powershell
.\scripts\push_to_github_https.ps1 -RepoUrl https://github.com/youruser/filemgr.git
```

This script will:
- Initialize the repo if needed
- Add the provided HTTPS remote as `origin` (or overwrite if `origin` exists)
- Push `main` and `develop` branches

Note: because this is a PowerShell script, it is ignored by default in the repo. We force-add it so you can run locally for convenience.

---

If you want me to attempt to create a GitHub repository using the GitHub API, provide me with a personal access token and the repository name, and I will create and push (but I cannot store your token here). Alternatively, follow the steps above to push yourself.