"""Git commands implementation."""

import subprocess
from typing import List

from rich.console import Console

console = Console()


def _run_git(args: list[str]) -> subprocess.CompletedProcess[str]:
    """Run a git command and convert process startup errors."""
    try:
        return subprocess.run(args, capture_output=True, text=True, check=False)
    except OSError as exc:
        raise RuntimeError("Failed to execute git command") from exc


def get_git_branches() -> List[str]:
    """Get all local git branches."""
    result = _run_git(["git", "branch", "--list"])
    if result.returncode != 0:
        raise RuntimeError("Not a git repository")

    branches = [b.strip().lstrip("*").strip() for b in result.stdout.split("\n") if b.strip()]
    return branches


def get_current_branch() -> str:
    """Get current branch name."""
    result = _run_git(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    if result.returncode != 0:
        raise RuntimeError("Not a git repository")
    return result.stdout.strip()


def clean_branches_impl(dry_run: bool = True, remote: bool = False) -> List[str]:
    """Delete merged branches."""
    current = get_current_branch()

    result = _run_git(["git", "branch", "--merged"])

    if result.returncode != 0:
        raise RuntimeError("Failed to get merged branches")

    branches = [b.strip().lstrip("*").strip() for b in result.stdout.split("\n") if b.strip()]
    deletable = [b for b in branches if b != current and b not in ["main", "master"]]

    if dry_run:
        return deletable

    deleted = []
    for branch in deletable:
        delete_result = _run_git(["git", "branch", "-d", branch])
        if delete_result.returncode != 0:
            raise RuntimeError(f"Failed to delete branch '{branch}'")
        deleted.append(branch)

    return deleted


def get_stats_impl(branch: str = "HEAD", since: str | None = None) -> dict:
    """Get git statistics for a branch."""
    cmd = ["git", "log", branch, "--oneline"]
    if since:
        cmd.extend([f"--since={since}"])

    result = _run_git(cmd)

    if result.returncode != 0:
        stderr = result.stderr.lower()
        if "not a git repository" in stderr:
            raise RuntimeError("Not a git repository")
        raise RuntimeError(f"Branch '{branch}' not found")

    commits = [c for c in result.stdout.strip().split("\n") if c]

    return {"total_commits": len(commits), "branch": branch, "since": since or "all time"}


def sync_fork_impl() -> dict:
    """Sync local branch with upstream default branch."""
    repo_check = _run_git(["git", "rev-parse", "--is-inside-work-tree"])
    if repo_check.returncode != 0:
        raise RuntimeError("Not a git repository")

    fetch_result = _run_git(["git", "fetch", "upstream"])
    if fetch_result.returncode != 0:
        stderr = fetch_result.stderr.lower()
        if "no such remote" in stderr or "does not appear to be a git repository" in stderr:
            raise RuntimeError("Upstream remote not configured")
        if "repository not found" in stderr or "could not read from remote repository" in stderr:
            raise RuntimeError("Upstream remote is not accessible")
        raise RuntimeError("Failed to fetch from upstream")

    upstream_branch = None
    for candidate in ["main", "master"]:
        branch_check = _run_git(["git", "rev-parse", "--verify", f"upstream/{candidate}"])
        if branch_check.returncode == 0:
            upstream_branch = candidate
            break

    if upstream_branch is None:
        raise RuntimeError("Upstream branch not found (expected upstream/main or upstream/master)")

    behind_result = _run_git(["git", "rev-list", "--count", f"HEAD..upstream/{upstream_branch}"])
    if behind_result.returncode != 0:
        raise RuntimeError("Failed to compare local branch with upstream")

    try:
        commits_behind = int(behind_result.stdout.strip() or "0")
    except ValueError as exc:
        raise RuntimeError("Failed to parse upstream comparison result") from exc
    if commits_behind == 0:
        return {"updated": False, "upstream_branch": upstream_branch, "commits": 0}

    merge_result = _run_git(["git", "merge", "--ff-only", f"upstream/{upstream_branch}"])
    if merge_result.returncode != 0:
        raise RuntimeError("Failed to fast-forward from upstream")

    return {"updated": True, "upstream_branch": upstream_branch, "commits": commits_behind}
