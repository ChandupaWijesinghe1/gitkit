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


def sync_fork_impl() -> dict:
    """Sync local branch with upstream default branch."""
    repo_check = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"], capture_output=True, text=True, check=False
    )
    if repo_check.returncode != 0:
        raise RuntimeError("Not a git repository")

    fetch_result = subprocess.run(
        ["git", "fetch", "upstream"], capture_output=True, text=True, check=False
    )
    if fetch_result.returncode != 0:
        raise RuntimeError("Upstream remote not configured")

    upstream_branch = None
    for candidate in ["main", "master"]:
        branch_check = subprocess.run(
            ["git", "rev-parse", "--verify", f"upstream/{candidate}"],
            capture_output=True,
            text=True,
            check=False,
        )
        if branch_check.returncode == 0:
            upstream_branch = candidate
            break

    if upstream_branch is None:
        raise RuntimeError("Upstream branch not found (expected upstream/main or upstream/master)")

    behind_result = subprocess.run(
        ["git", "rev-list", "--count", f"HEAD..upstream/{upstream_branch}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if behind_result.returncode != 0:
        raise RuntimeError("Failed to compare local branch with upstream")

    commits_behind = int(behind_result.stdout.strip() or "0")
    if commits_behind == 0:
        return {"updated": False, "upstream_branch": upstream_branch, "commits": 0}

    merge_result = subprocess.run(
        ["git", "merge", "--ff-only", f"upstream/{upstream_branch}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if merge_result.returncode != 0:
        raise RuntimeError("Failed to fast-forward from upstream")

    return {"updated": True, "upstream_branch": upstream_branch, "commits": commits_behind}
