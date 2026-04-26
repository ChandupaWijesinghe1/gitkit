# gitkit - Design Document

## Overview
Fast Git workflow CLI tool for managing branches, commits, and repository maintenance.

## Commands

### 1. `gitkit clean-branches`
**Purpose**: Delete merged branches locally and remotely

**Usage**:
```bash
gitkit clean-branches [OPTIONS]
```

**Options**:
- `--dry-run`: Show what would be deleted without actually deleting
- `--remote`: Also delete from remote (requires confirmation)
- `--exclude BRANCH`: Don't delete specified branches (e.g., main, develop)

**Input**: None (reads Git repository state)
**Output**: List of deleted branches

**Example**:
```bash
$ gitkit clean-branches --dry-run
Would delete: feature/login, feature/auth, bugfix/typo
```

**Edge Case**: What if current branch is merged?
→ Checkout `main` first, don't delete current branch

---

### 2. `gitkit stats`
**Purpose**: Show Git commit statistics

**Usage**:
```bash
gitkit stats [OPTIONS] [BRANCH]
```

**Options**:
- `--since DATE`: Show commits since date (e.g., "2 weeks ago")
- `--author NAME`: Filter by author
- `--format TABLE|JSON`: Output format

**Input**: Branch name (optional, defaults to current)
**Output**: Commit count, author stats, file changes

**Example**:
```bash
$ gitkit stats main --since "1 week"
Total commits: 42
Authors:
  Alice: 25 commits
  Bob: 17 commits
Files changed: 156
```

**Edge Case**: What if branch doesn't exist?
→ Show error: "Branch 'xyz' not found. Available branches: main, develop, ..."

---

### 3. `gitkit sync-fork`
**Purpose**: Sync local fork with upstream repository

**Usage**:
```bash
gitkit sync-fork [OPTIONS]
```

**Options**:
- `--main`: Sync main branch only (default)
- `--all`: Sync all branches
- `--upstream URL`: Specify custom upstream (default: origin)
- `--push`: Auto-push synced branches to fork

**Input**: None (reads Git config)
**Output**: Sync status and branch updates

**Example**:
```bash
$ gitkit sync-fork --main --push
Syncing fork from upstream...
main: +5 commits, -2 commits
Pushed to origin/main
```

**Edge Case**: What if upstream remote doesn't exist?
→ Auto-add: `git remote add upstream <url>` (with confirmation)

---

## Implementation Notes

### Dependencies
- `click>=8.0`: CLI framework
- `rich>=13.0`: Pretty terminal output

### Error Handling
- Git command failures → Show user-friendly error with suggestion
- Permission denied → Explain why (permissions issue)
- Network errors → Hint to check connection

### Exit Codes
- 0: Success
- 1: General error
- 2: Git operation failed
- 3: Invalid arguments

## Testing Strategy
- Unit tests: Command logic without Git
- Integration tests: Real Git repo in temp directory
- Fixture: Temporary Git repository for testing