# gitkit

`gitkit` is a lightweight command-line tool for common Git maintenance tasks.
It helps with branch cleanup, repository statistics, and syncing a fork from an upstream remote.

## Table of Contents

- [Purpose](#purpose)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Commands](#commands)
- [Configuration Support](#configuration-support)
- [Development](#development)
- [Packaging and Distribution](#packaging-and-distribution)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Purpose

This section explains why `gitkit` exists.

- Reduce repetitive Git command sequences.
- Provide readable CLI output for common workflows.
- Offer a JSON output mode for machine-readable stats.

## Features

This section summarizes what the tool can do.

- Clean merged branches with safe dry-run behavior.
- Show commit statistics for a branch and optional time range.
- Sync local branch from `upstream/main` or `upstream/master`.
- Export stats in JSON using `--json`.

## Requirements

This section lists runtime prerequisites.

- Python `>=3.12`
- Git installed and available on `PATH`
- A Git repository for command execution

## Installation

This section shows different ways to install `gitkit`.

### Install from local source (development mode)

Use this for local development where code changes are reflected immediately.

```bash
pip install -e .
```

### Install with development dependencies

Use this if you want testing, linting, and type-checking tools.

```bash
pip install -e ".[dev]"
```

### Install from GitHub

Use this to test installation from a remote Git repository.

```bash
pip install "git+https://github.com/chandupawijesinghe1/gitkit.git"
```

### Install from built wheel

Use this to verify production-like installation behavior.

```bash
pip install dist/gitkit-0.1.0-py3-none-any.whl
```

## Quick Start

This section gives minimal commands to verify the tool is working.

```bash
# Show root help
gitkit --help

# Dry-run merged branch cleanup
gitkit clean-branches --dry-run

# Show stats for current HEAD
gitkit stats HEAD

# Show machine-readable stats
gitkit stats HEAD --json

# Sync from upstream
gitkit sync-fork
```

## Commands

This section documents each command and its purpose.

### `clean-branches`

Purpose: identify and optionally delete merged local branches.

```bash
gitkit clean-branches --dry-run
gitkit clean-branches
```

Options:

- `--dry-run`: show branches that would be deleted without deleting them.
- `--remote`: reserved flag in current implementation (future remote cleanup support).

### `stats`

Purpose: show commit count information for a branch.

```bash
gitkit stats
gitkit stats HEAD --since "2 weeks ago"
gitkit stats main --json
```

Arguments and options:

- `BRANCH` (optional): target branch, default is `HEAD`.
- `--since`: filter commits by a date expression.
- `--json`: output stats in JSON format.

### `sync-fork`

Purpose: fast-forward local branch from upstream default branch.

```bash
gitkit sync-fork
```

Behavior:

- Fetches from `upstream`.
- Detects `upstream/main` or `upstream/master`.
- Fast-forwards if local branch is behind.
- Shows "already up to date" when no new commits exist.

## Configuration Support

This section clarifies supported configuration mechanisms.

- CLI flags/options: supported.
- Environment variables: not currently implemented for runtime behavior.
- External runtime config file: not currently implemented.
- Project/tool configuration is defined in `pyproject.toml`.

## Development

This section explains how to work on the project locally.

### Run tests

```bash
pytest
```

### Run linter

```bash
ruff check .
```

### Run type checks

```bash
mypy src
```

## Packaging and Distribution

This section explains how to build and validate distributable artifacts.

### Build package artifacts

```bash
python -m build
```

Outputs:

- `dist/*.whl`
- `dist/*.tar.gz`

### Validate package metadata and archives

```bash
python -m twine check dist/*
```

### Test install in a fresh virtual environment

```bash
python -m venv .venv-install-test
. .venv-install-test/bin/activate  # Linux/macOS
# On Windows PowerShell use:
# .\.venv-install-test\Scripts\Activate.ps1

pip install dist/gitkit-0.1.0-py3-none-any.whl
gitkit --help
```

## Troubleshooting

This section lists common issues and how to resolve them.

- **`gitkit` not recognized**
  - Ensure the Python Scripts directory is on `PATH`, or run via `python -m gitkit.cli`.
- **`Error: Upstream remote not configured`**
  - Add upstream remote:
    - `git remote add upstream <original-repo-url>`
- **`Error: Upstream remote is not accessible`**
  - Verify upstream URL and repository permissions.
- **`Not a git repository`**
  - Run command inside a valid Git repository directory.

## License

This section states the project license.

MIT