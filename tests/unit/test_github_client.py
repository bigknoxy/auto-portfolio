"""Unit tests for GitHub client module."""
import pytest

from core.github_client import MockGitHubClient


class TestMockGitHubClient:
    """Test mock client for testing purposes."""
    
    def test_get_user_profile_returns_profile_data(self):
        """Mock client returns profile data correctly."""
        client = MockGitHubClient(
            profile_data={"name": "Test User", "bio": "Test bio"}
        )
        result = client.get_user_profile("testuser")
        assert result["name"] == "Test User"
        assert result["bio"] == "Test bio"
    
    def test_get_user_repos_returns_repos_list(self):
        """Mock client returns repos list."""
        client = MockGitHubClient(repos=[{"name": "repo1"}, {"name": "repo2"}])
        result = client.get_user_repos("testuser")
        assert len(result) == 2
        assert result[0]["name"] == "repo1"
    
    def test_get_user_repos_empty_returns_empty_list(self):
        """Mock client returns empty list when no repos."""
        client = MockGitHubClient(repos=[])
        result = client.get_user_repos("testuser")
        assert result == []


class TestGHCLIClient:
    """Test real GitHub CLI client."""
    
    @pytest.mark.skipif(
        not pytest.importorskip("shutil", reason="gh not available").which("gh"),
        reason="gh CLI not installed"
    )
    def test_get_user_profile_requires_gh(self):
        """Real client requires gh CLI (skip if not available)."""
        # This test is skipped if gh is not installed
        pass