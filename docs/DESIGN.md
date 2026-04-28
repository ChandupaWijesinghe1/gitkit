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

---

## Command Execution Flow

### Architecture Overview: Three-Layer Design

gitkit follows a clean separation of concerns across three layers:

**Layer 1: CLI Interface (`cli.py`)**
- Handles user input and option parsing via Click
- Routes commands to appropriate implementation functions
- Formats and displays output using Rich

**Layer 2: Implementation (`commands.py`)**
- Contains business logic for each command
- Executes Git operations via subprocess
- Processes and structures data for display

**Layer 3: Git Subprocess**
- Direct execution of native Git commands
- Returns raw output (stdout/stderr)
- Communicates with the Git repository

### Flow: `clean-branches` Command

**Command:** `gitkit clean-branches --no-dry-run --remote`

```
1. User Input
   └─> gitkit clean-branches --no-dry-run --remote

2. CLI Parser (Click)
   └─> Parse: dry_run=False, remote=True

3. Route to Command
   └─> clean_branches() function

4. Implementation Layer
   ├─> get_current_branch()
   │   └─> subprocess: git rev-parse --abbrev-ref HEAD
   │
   ├─> get_git_branches()
   │   └─> subprocess: git branch --merged
   │
   ├─> Filter branches
   │   ├─> Remove: main, master, current branch
   │   └─> Keep: merged branches only
   │
   ├─> Conditionally delete
   │   ├─> If dry_run=True: return list (no deletion)
   │   └─> If dry_run=False: subprocess git branch -d [branch]
   │
   └─> Return: List of deleted branch names

5. Output Formatting (Rich)
   ├─> Create colored console table
   ├─> Apply styling (cyan for dry-run, green for actual)
   └─> Display branch names with bullets

6. Terminal Output
   └─> User sees formatted result
```

### Flow: `stats` Command

**Command:** `gitkit stats main --since "1 week ago"`

```
1. User Input
   └─> gitkit stats main --since "1 week ago"

2. CLI Parser (Click)
   └─> Parse: branch='main', since='1 week ago'

3. Route to Command
   └─> stats() function

4. Implementation Layer
   ├─> Build git command
   │   └─> ["git", "log", "main", "--oneline", "--since=1 week ago"]
   │
   ├─> Execute subprocess
   │   └─> subprocess.run() → Git process
   │
   ├─> Parse output
   │   ├─> Split by newline
   │   └─> Count commit lines
   │
   └─> Build statistics dict
       ├─> total_commits: integer count
       ├─> branch: "main"
       └─> since: "1 week ago"

5. Output Formatting (Rich)
   ├─> Create Table with title "Stats for main"
   ├─> Add rows: [Metric | Value]
   │   ├─> "Total Commits" | 42
   │   └─> "Period" | "1 week ago"
   └─> Apply colors (cyan/green)

6. Terminal Output
   └─> Formatted table displayed
```

### Execution Flow Diagram: clean-branches

```
┌─────────────────────────────────────────────────────────────┐
│ 👤 User Input: gitkit clean-branches --no-dry-run --remote  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │ 🔍 Click CLI Parser  │
            └──────────┬───────────┘
                       │ Parse args
                       ▼
        ┌─────────────────────────────┐
        │ Parse: dry_run=False        │
        │        remote=True          │
        └──────────┬──────────────────┘
                   │
                   ▼
      ┌────────────────────────────┐
      │ 🎯 Route to Command        │
      │ clean_branches()           │
      └────────┬───────────────────┘
               │
               ▼
  ┌───────────────────────────────────┐
  │ ⚙️ Implementation Function         │
  │ clean_branches_impl()             │
  └────────┬────────────────────────┘
           │
           ├─▶ 📊 Get Current Branch
           │   subprocess: git rev-parse --abbrev-ref HEAD
           │
           ├─▶ 🌿 Get Merged Branches
           │   subprocess: git branch --merged
           │
           ├─▶ 🔄 Filter Branches
           │   (exclude main, master, current)
           │
           └─▶ ❓ Check Dry-Run Mode
               │
         ┌─────┴─────┐
         │           │
    ✅ Yes       ❌ No
         │           │
         │           ▼
         │    🗑️ Delete Branches
         │    subprocess: git branch -d [branch]
         │           │
         └─────┬─────┘
               │
               ▼
        📝 Return List of Branches
               │
               ▼
      🎨 Format with Rich Console
      (colors: cyan/green)
               │
               ▼
      🖥️ Display Terminal Output
               │
               ▼
        ✨ Complete (exit 0)
```

### Execution Flow Diagram: stats

```
┌──────────────────────────────────────────────────────┐
│ 👤 User Input: gitkit stats main --since "1 week"   │
└──────────────────┬─────────────────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │ 🔍 Click CLI Parser  │
        └──────────┬───────────┘
                   │
                   ▼
      ┌──────────────────────────┐
      │ branch='main'            │
      │ since='1 week ago'       │
      └──────────┬───────────────┘
                 │
                 ▼
    ┌──────────────────────────┐
    │ 🎯 Route: stats()        │
    └──────────┬───────────────┘
               │
               ▼
  ┌──────────────────────────────────┐
  │ ⚙️ get_stats_impl()              │
  └────────┬─────────────────────────┘
           │
           ▼
  📊 Build Git Command
  └─▶ git log main --oneline --since=1 week ago
           │
           ▼
  🔄 subprocess.run(cmd)
           │
      ┌────┴────┐
      │         │
   Error?   Success?
      │         │
   ❌ No      ✅ Yes
      │         │
      │         ▼
      │    📝 Parse Output
      │    (split & count commits)
      │         │
      │         ▼
      │    📊 Build Statistics Dict
      │    {total_commits, branch, since}
      │         │
      ▼         ▼
  RuntimeError  │
      │         │
      └────┬────┘
           │
           ▼
    🎨 Create Rich Table
    ├─ Title: "Stats for main"
    ├─ Row: Metric | Value
    └─ Colors: cyan/green
           │
           ▼
    🖥️ Display Table
           │
           ▼
      ✨ Complete
```

### Architecture: Three-Layer Model

```
┌──────────────────────────────────────────────────────────────┐
│ 👤 User Terminal: gitkit [command] [options]                │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
        ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃ 🎯 CLI Layer (cli.py)    ┃
        ┃ ━━━━━━━━━━━━━━━━━━━━━━   ┃
        ┃ • Click decorators        ┃
        ┃ • Argument parsing        ┃
        ┃ • Help text               ┃
        ┃ • Error handling          ┃
        ┗━━━━━━━━┬───────────────━━┛
                 │
                 ▼
        ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃ ⚙️ Implementation (commands.py)┃
        ┃ ━━━━━━━━━━━━━━━━━━━━━━━━━━   ┃
        ┃ • Business logic              ┃
        ┃ • Type hints                  ┃
        ┃ • Data processing             ┃
        ┃ • Error handling              ┃
        ┗━━━━━━━━┬─────────────────━━┛
                 │
                 ▼
        ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃ 🔧 Git Subprocess Layer    ┃
        ┃ ━━━━━━━━━━━━━━━━━━━━━━━   ┃
        ┃ subprocess.run(["git", ...])┃
        ┃ • git branch                ┃
        ┃ • git log                   ┃
        ┃ • git pull                  ┃
        ┃ • git push                  ┃
        ┗━━━━━━━━┬──────────────━━┛
                 │
                 ▼
        ┌──────────────────────┐
        │ 📦 Git Repository    │
        │ • Branches           │
        │ • Commits            │
        │ • References         │
        └──────────────────────┘


Output Path:
┌──────────┬──────────────┬──────────────┐
│          │              │              │
▼          ▼              ▼              ▼
Rich      Data          Git        Terminal
Output    Processing    Response    Display
│         │             │          │
└─────────┴─────────────┴──────────┘
          │
          ▼
    🖥️ User sees result
```

---

## Data Flow Summary

| Stage | Input | Processing | Output |
|-------|-------|-----------|--------|
| CLI | User args | Click parsing | Parsed options dict |
| Impl | Options | Business logic | Python dict/list |
| Git | Command list | subprocess execution | stdout/stderr |
| Output | Raw data | Rich formatting | Terminal table |