# gitkit
new CLI  tool for managing branches and commits


# gitkit

Fast Git workflow CLI tool for managing branches, commits, and repository maintenance.

## Installation

```bash
pip install -e .
```

## Quick Start

```bash
# See all commands
gitkit --help

# Delete merged branches (dry-run mode by default)
gitkit clean-branches

# Show commit statistics
gitkit stats main --since "1 week"

# Sync fork with upstream
gitkit sync-fork --main
```

## Commands

- `clean-branches`: Delete merged local/remote branches
- `stats`: Show commit statistics per branch/author
- `sync-fork`: Sync fork with upstream repository

## Development

Install with dev dependencies:
```bash
pip install -e ".[dev]"
```

Run tests:
```bash
pytest --cov=src/gitkit
```

Lint code:
```bash
ruff check src/
```

Format code:
```bash
ruff format src/
```

## License

MIT