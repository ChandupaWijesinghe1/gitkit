"""Tests for gitkit commands."""

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
