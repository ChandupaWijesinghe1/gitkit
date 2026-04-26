"""Git commands implementation."""

import subprocess
from typing import List

from rich.console import Console

console = Console()


def get_git_branches() -> List[str]:
    """Get all local git branches."""
    result = subprocess.run(
        ["git", "branch", "--list"], capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        raise RuntimeError("Not a git repository")

    branches = [b.strip().lstrip("*").strip() for b in result.stdout.split("\n") if b.strip()]
    return branches


def get_current_branch() -> str:
    """Get current branch name."""
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        raise RuntimeError("Not a git repository")
    return result.stdout.strip()


def clean_branches_impl(dry_run: bool = True, remote: bool = False) -> List[str]:
    """Delete merged branches."""
    current = get_current_branch()

    result = subprocess.run(
        ["git", "branch", "--merged"], capture_output=True, text=True, check=False
    )

    if result.returncode != 0:
        raise RuntimeError("Failed to get merged branches")

    branches = [b.strip().lstrip("*").strip() for b in result.stdout.split("\n") if b.strip()]
    deletable = [b for b in branches if b != current and b not in ["main", "master"]]

    if dry_run:
        return deletable

    deleted = []
    for branch in deletable:
        subprocess.run(["git", "branch", "-d", branch], check=False)
        deleted.append(branch)

    return deleted


def get_stats_impl(branch: str = "HEAD", since: str | None = None) -> dict:
    """Get git statistics for a branch."""
    cmd = ["git", "log", branch, "--oneline"]
    if since:
        cmd.extend([f"--since={since}"])

    result = subprocess.run(cmd, capture_output=True, text=True, check=False)

    if result.returncode != 0:
        raise RuntimeError(f"Branch '{branch}' not found")

    commits = [c for c in result.stdout.strip().split("\n") if c]

    return {"total_commits": len(commits), "branch": branch, "since": since or "all time"}
