"""Tests for gitkit commands."""
# Test to check if the clean-branches command works.
import json
import os
import subprocess
import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner

from gitkit.cli import main
from gitkit.commands import clean_branches_impl, get_stats_impl


def test_clean_branches_dry_run():
    """Test dry-run doesn't actually delete."""
    # This is a placeholder test
    # Real tests would use a temporary git repo
    result = clean_branches_impl(dry_run=True)
    assert isinstance(result, list)


def test_get_stats():
    """Test stats generation."""
    # Placeholder test
    stats = get_stats_impl(branch="HEAD")
    assert "total_commits" in stats
    assert "branch" in stats


# CLI Integration Tests using CliRunner

@pytest.fixture
def git_repo():
    """Create a temporary git repo with test setup."""
    original_dir = os.getcwd()
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        os.chdir(repo_path)

        try:
            # Initialize git repo
            subprocess.run(["git", "init", "-b", "main"], check=True, capture_output=True)
            subprocess.run(
                ["git", "config", "user.email", "test@test.com"], check=True, capture_output=True
            )
            subprocess.run(
                ["git", "config", "user.name", "Test User"], check=True, capture_output=True
            )

            # Create initial commit on main
            (repo_path / "file.txt").write_text("initial")
            subprocess.run(["git", "add", "."], check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", "initial"], check=True, capture_output=True)

            yield repo_path
        finally:
            os.chdir(original_dir)


@pytest.fixture
def git_repo_with_merged_branches(git_repo):
    """Create a repo with a merged branch."""
    # Create and merge a branch
    subprocess.run(["git", "checkout", "-b", "feature/test"], check=True, capture_output=True)
    (git_repo / "feature.txt").write_text("feature")
    subprocess.run(["git", "add", "."], check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "feature"], check=True, capture_output=True)

    subprocess.run(["git", "checkout", "main"], check=True, capture_output=True)
    subprocess.run(["git", "merge", "feature/test"], check=True, capture_output=True)

    return git_repo


def test_clean_branches_happy_path(git_repo_with_merged_branches):
    """Happy path: clean_branches with dry-run on repo with merged branches."""
    runner = CliRunner()
    result = runner.invoke(main, ["clean-branches", "--dry-run"])

    assert result.exit_code == 0
    assert "Branches that would be deleted" in result.output
    assert "feature/test" in result.output


def test_clean_branches_edge_case(git_repo):
    """Edge case: clean_branches on repo with no merged branches."""
    runner = CliRunner()
    result = runner.invoke(main, ["clean-branches", "--dry-run"])

    assert result.exit_code == 0
    assert "No branches to delete" in result.output


def test_clean_branches_error_case():
    """Error case: clean_branches on non-git directory."""
    original_dir = os.getcwd()
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            os.chdir(tmpdir)
            runner = CliRunner()
            result = runner.invoke(main, ["clean-branches", "--dry-run"])

            assert result.exit_code != 0
            assert "Not a git repository" in result.output
        finally:
            os.chdir(original_dir)


def test_stats_happy_path(git_repo):
    """Happy path: stats command returns commit stats for a valid branch."""
    runner = CliRunner()
    result = runner.invoke(main, ["stats", "HEAD"])

    assert result.exit_code == 0
    assert "Stats for HEAD" in result.output
    assert "Total Commits" in result.output
    assert "all time" in result.output


def test_stats_edge_case_no_commits_in_period(git_repo):
    """Edge case: stats with a future --since returns zero commits."""
    runner = CliRunner()
    result = runner.invoke(main, ["stats", "HEAD", "--since", "3000-01-01"])

    assert result.exit_code == 0
    assert "Stats for HEAD" in result.output
    assert "Total Commits" in result.output
    assert "0" in result.output
    assert "3000-01-01" in result.output


def test_stats_error_case_invalid_branch(git_repo):
    """Error case: stats on a non-existent branch."""
    runner = CliRunner()
    result = runner.invoke(main, ["stats", "does-not-exist"])

    assert result.exit_code != 0
    assert "Branch 'does-not-exist' not found" in result.output


def test_stats_output_format_json(git_repo: Path) -> None:
    """Output format test: stats command supports machine-readable JSON output."""
    runner = CliRunner()
    result = runner.invoke(main, ["stats", "HEAD", "--json"])

    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["branch"] == "HEAD"
    assert data["since"] == "all time"
    assert isinstance(data["total_commits"], int)
    assert sorted(data.keys()) == ["branch", "since", "total_commits"]


def test_stats_git_repository_state(git_repo: Path) -> None:
    """Git repository state test: commit count reflects current repo state."""
    (git_repo / "state.txt").write_text("state-change")
    subprocess.run(["git", "add", "."], check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "state commit"], check=True, capture_output=True)

    runner = CliRunner()
    result = runner.invoke(main, ["stats", "HEAD", "--json"])

    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["total_commits"] == 2


def test_stats_not_a_repo_error_handling() -> None:
    """Not-a-repo error handling test for stats command."""
    original_dir = os.getcwd()
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            os.chdir(tmpdir)
            runner = CliRunner()
            result = runner.invoke(main, ["stats", "HEAD"])

            assert result.exit_code != 0
            assert "Not a git repository" in result.output
        finally:
            os.chdir(original_dir)


def test_sync_fork_happy_path():
    """Happy path: sync-fork fast-forwards from upstream/main."""
    original_dir = os.getcwd()
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        upstream_work = root / "upstream-work"
        upstream_bare = root / "upstream.git"
        fork_repo = root / "fork"

        try:
            subprocess.run(
                ["git", "init", "-b", "main", str(upstream_work)], check=True, capture_output=True
            )
            os.chdir(upstream_work)
            subprocess.run(
                ["git", "config", "user.email", "test@test.com"], check=True, capture_output=True
            )
            subprocess.run(
                ["git", "config", "user.name", "Test User"], check=True, capture_output=True
            )
            (upstream_work / "file.txt").write_text("initial")
            subprocess.run(["git", "add", "."], check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", "initial"], check=True, capture_output=True)

            os.chdir(root)
            subprocess.run(
                ["git", "clone", "--bare", str(upstream_work), str(upstream_bare)],
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "clone", str(upstream_bare), str(fork_repo)],
                check=True,
                capture_output=True,
            )

            os.chdir(upstream_work)
            subprocess.run(
                ["git", "remote", "add", "origin", str(upstream_bare)],
                check=True,
                capture_output=True,
            )
            (upstream_work / "file.txt").write_text("second")
            subprocess.run(["git", "add", "."], check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", "second"], check=True, capture_output=True)
            subprocess.run(["git", "push", "-u", "origin", "main"], check=True, capture_output=True)

            os.chdir(fork_repo)
            subprocess.run(
                ["git", "remote", "add", "upstream", str(upstream_bare)],
                check=True,
                capture_output=True,
            )
            runner = CliRunner()
            result = runner.invoke(main, ["sync-fork"])

            assert result.exit_code == 0
            assert "Synced from upstream/main" in result.output
        finally:
            os.chdir(original_dir)


def test_sync_fork_edge_case_already_up_to_date():
    """Edge case: sync-fork reports when no new upstream commits exist."""
    original_dir = os.getcwd()
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        upstream_work = root / "upstream-work"
        upstream_bare = root / "upstream.git"
        fork_repo = root / "fork"

        try:
            subprocess.run(
                ["git", "init", "-b", "main", str(upstream_work)], check=True, capture_output=True
            )
            os.chdir(upstream_work)
            subprocess.run(
                ["git", "config", "user.email", "test@test.com"], check=True, capture_output=True
            )
            subprocess.run(
                ["git", "config", "user.name", "Test User"], check=True, capture_output=True
            )
            (upstream_work / "file.txt").write_text("initial")
            subprocess.run(["git", "add", "."], check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", "initial"], check=True, capture_output=True)

            os.chdir(root)
            subprocess.run(
                ["git", "clone", "--bare", str(upstream_work), str(upstream_bare)],
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "clone", str(upstream_bare), str(fork_repo)],
                check=True,
                capture_output=True,
            )

            os.chdir(fork_repo)
            subprocess.run(
                ["git", "remote", "add", "upstream", str(upstream_bare)],
                check=True,
                capture_output=True,
            )
            runner = CliRunner()
            result = runner.invoke(main, ["sync-fork"])

            assert result.exit_code == 0
            assert "Already up to date with upstream/main" in result.output
        finally:
            os.chdir(original_dir)


def test_sync_fork_error_case_missing_upstream(git_repo):
    """Error case: sync-fork fails when upstream remote is missing."""
    runner = CliRunner()
    result = runner.invoke(main, ["sync-fork"])

    assert result.exit_code != 0
    assert "Upstream remote not configured" in result.output

