# Branch Protection Setup Guide (Manual)

This repository has GitHub Actions to run tests. To enable PR-based development with CI checks, set branch protection rules for the `main` branch:

1. Go to your repository on GitHub.
2. Settings -> Branches -> Add rule.
3. Branch name pattern: `main`.
4. Check "Require status checks to pass before merging".
   - Under "Status checks found in the last week for this repository", select: `Python CI` (or the appropriate check name) if it appears.
5. Optionally: Require pull requests before merging, require approvals, dismiss stale reviews, require linear history, etc.
6. Save changes.

You can also use GitHub API to set branch protection if you prefer automation.
