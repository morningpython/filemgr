This folder contains helper scripts used during repository setup, branch protection management, and quick merges.

Key scripts
- manage_protection.ps1: Orchestrates backup -> contexts update -> merge -> restore. Usage:
  - Dry run: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/manage_protection.ps1 -Pr 1 -ContextName 'test' -MergeStyle 'merge' -DryRun`
  - Actual merge: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/manage_protection.ps1 -Pr 1 -ContextName 'test' -MergeStyle 'merge'`

- update_contexts.ps1: Updates required_status_checks contexts for the 'main' branch. This is used when required check or workflow name needs to be changed.

- restore_protection.ps1: Restores branch protection from `scripts/protection-backup.json`

- write_nobom.ps1: Re-writes JSON files to UTF-8 w/o BOM. Use it if you see "problems parsing JSON" errors from GitHub REST API.

- inspect_protection_backup.ps1: Helpful to inspect the loaded protection backup shape.

Notes:
- These scripts assume 'gh' is installed and an authenticated session is active.
- Use these scripts carefully; they temporarily adjust branch protection. Backup will be written to `scripts/protection-backup.json`.
- The scripts are intended for repository owners or maintainers who have admin rights.
