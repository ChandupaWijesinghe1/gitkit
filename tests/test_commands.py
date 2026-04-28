"""Tests for gitkit commands."""

import os
import subprocess
import tempfile
from pathlib import Path

from click.testing import CliRunner
import pytest

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
            subprocess.run(["git", "init"], check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@test.com"], check=True, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Test User"], check=True, capture_output=True)
            
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
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        runner = CliRunner()
        result = runner.invoke(main, ["clean-branches", "--dry-run"])
        
        assert result.exit_code != 0
        assert "Not a git repository" in result.output

