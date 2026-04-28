# gitkit - Fast Git Workflow CLI Tool
## Technical Documentation & Thesis

---

## Overview

**gitkit** is a lightweight, command-line tool designed to streamline Git workflow management and repository maintenance. It provides developers with fast, intuitive commands to clean up merged branches, analyze commit statistics, and synchronize forked repositories without leaving the terminal. Built with Python, Click, and Rich, gitkit simplifies repetitive Git operations and enhances developer productivity by reducing context switching between Git and custom scripts.

---

## Installation

### Prerequisites
- Python 3.12 or higher
- Git installed and accessible from terminal
- pip package manager

### Standard Installation
```bash
# Clone the repository
git clone https://github.com/ChandupaWijesinghe1/gitkit.git
cd gitkit

# Install in development mode
pip install -e .
```

### Installation with Development Dependencies
```bash
# Install with testing, linting, and type-checking tools
pip install -e ".[dev]"
```

### Verify Installation
```bash
gitkit --version
gitkit --help
```

---

## Usage / CLI Reference

### Command: `gitkit clean-branches`
Identifies and deletes merged branches to maintain a clean repository.

```bash
# Dry-run mode (default) - shows branches that would be deleted
gitkit clean-branches

# Actually delete merged branches from local repository
gitkit clean-branches --no-dry-run

# Delete merged branches from both local and remote
gitkit clean-branches --no-dry-run --remote
```

**Features:**
- Preserves `main` and `master` branches (cannot be deleted)
- Dry-run mode enabled by default for safety
- Shows formatted output with branch names
- Handles remote branch deletion with `--remote` flag

---

### Command: `gitkit stats`
Displays commit statistics for a given branch.

```bash
# Show total commits on current branch (HEAD)
gitkit stats

# Show stats for a specific branch
gitkit stats main

# Show commits from a specific timeframe
gitkit stats main --since "1 week ago"

# Other time formats: "2 weeks", "1 month", "2024-01-01"
gitkit stats develop --since "3 days ago"
```

**Features:**
- Displays total commit count
- Shows filtered commits by time period
- Formatted table output using Rich library
- Supports Git date formats (e.g., "1 week ago", "2024-01-15")

---

### Command: `gitkit sync-fork`
Synchronizes a forked repository with its upstream original repository.

```bash
# Placeholder implementation - provides guidance
gitkit sync-fork
```

**Output Guidance:**
```
Run: git remote add upstream <original-repo-url>
Then: git pull upstream main
```

**Status:** Currently a placeholder; will be fully implemented in v0.2.0

---

### Global Options
```bash
# Display version information
gitkit --version

# Show help for all commands
gitkit --help

# Show help for specific command
gitkit clean-branches --help
```

---

## Architecture

### System Design

**gitkit** follows a modular, subprocess-based architecture that wraps native Git commands. The design consists of three core layers:

#### Layer 1: CLI Interface (`cli.py`)
- **Framework:** Click (Python CLI framework)
- **Responsibility:** Command parsing, user interaction, output formatting
- **Features:**
  - Group-based command structure (`@click.group`)
  - Option parsing and validation
  - Rich-formatted console output with colors and tables
  - Error handling with user-friendly messages

#### Layer 2: Command Implementation (`commands.py`)
- **Responsibility:** Business logic and Git operations
- **Architecture:**
  - Each command has a corresponding `*_impl()` function
  - Uses Python's `subprocess` module to execute Git commands
  - Type-safe implementation with type hints (`str`, `List[str]`, `dict`)
  - Error handling with try-catch patterns

#### Layer 3: Git Subprocess Integration
```
gitkit command → CLI Parser → Implementation Function → 
subprocess.run(["git", ...]) → Git Process → Repository
```

### Key Technical Decisions

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| CLI Framework | Click | Lightweight, intuitive, widely-used in Python CLI ecosystem |
| Output Formatting | Rich | Beautiful terminal output with colors, tables, and markdown |
| Subprocess Management | Python `subprocess` | Direct Git command execution without dependencies |
| Type Checking | Type Hints + mypy | Ensure code quality and catch type errors early |
| Python Version | 3.12+ | Access to latest Python features (e.g., `str \| None` syntax) |

### Command Execution Flow: `clean-branches`

```
User input: gitkit clean-branches --no-dry-run --remote
    ↓
CLI @click.command() parses options
    ↓
clean_branches_impl(dry_run=False, remote=True) called
    ↓
Subprocess calls: git branch --list, git branch --merged
    ↓
Branches filtered (exclude main/master, find merged)
    ↓
If not dry-run: subprocess calls git branch -d [branch]
    ↓
Returns list of deleted branches
    ↓
Rich console prints formatted output (green/cyan colors)
```

---

## Development Setup

### Running Tests
```bash
# Run all tests with coverage report
pytest --cov=src/gitkit --cov-report=html

# Run specific test file
pytest tests/test_commands.py -v

# Generate HTML coverage report
open htmlcov/index.html
```

### Code Quality Tools
```bash
# Lint code with Ruff
ruff check src/

# Type check with mypy
mypy src/gitkit/

# Fix linting issues automatically
ruff check src/ --fix
```

### Project Structure
```
gitkit/
├── src/gitkit/
│   ├── __init__.py          # Version and metadata
│   ├── cli.py               # Click CLI commands
│   └── commands.py          # Business logic implementation
├── tests/
│   ├── __init__.py
│   └── test_commands.py     # Unit tests
├── pyproject.toml           # Project configuration
├── README.md                # Quick start guide
└── LICENSE                  # MIT License
```

---

## Roadmap & Future Features

### Version 0.1.0 (Current - Stable)
✅ **Completed:**
- `clean-branches` command with dry-run mode
- `stats` command with time-based filtering
- Comprehensive type hints and mypy support
- Full test coverage with pytest
- Code quality standards (ruff linting)
- Rich console output formatting

### Version 0.2.0 (Planned)
🎯 **In Development:**
- Full `sync-fork` implementation
  - Auto-detect upstream repository
  - Pull and merge upstream changes
  - Handle merge conflicts gracefully
- Author-based commit statistics
- Branch comparison metrics

### Version 0.3.0 (Future)
🚀 **Proposed Features:**
- Interactive branch selection menu
- Commit history visualization
- Integration with GitHub/GitLab APIs
- Configuration file support (`.gitkit.toml`)
- Batch operations on multiple branches
- Commit message templates

### Long-term Vision
- Cross-platform support (Windows, macOS, Linux)
- Plugin system for custom commands
- Integration with CI/CD workflows
- Web UI dashboard for repository management

---

## Dependencies

### Core Dependencies
```
click>=8.0              # CLI framework
rich>=13.0              # Terminal output formatting
```

### Development Dependencies
```
pytest>=7.0             # Testing framework
pytest-cov>=4.0         # Code coverage
ruff>=0.1               # Fast Python linter
mypy>=1.0               # Static type checker
```

---

## Performance Considerations

- **Subprocess Overhead:** Each Git command spawns a new process (~50-100ms)
- **Large Repositories:** `clean-branches` on repos with 1000+ branches takes 1-2 seconds
- **Future Optimization:** Consider GitPython library for better performance on large operations

---

## Author & License

**Author:** Chandupa Wijesinghe  
**Version:** 0.1.0  
**License:** MIT  
**Repository:** [ChandupaWijesinghe1/gitkit](https://github.com/ChandupaWijesinghe1/gitkit)

---

**Last Updated:** April 27, 2026  
**Documentation Status:** Complete for v0.1.0
