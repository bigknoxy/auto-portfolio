"""Unit tests for profile importer module."""
import pytest

from core.github_client import MockGitHubClient
from core.profile_importer import (
    create_project_from_github,
    import_github_profile,
    parse_github_profile,
    select_repos_interactive,
)


class TestParseGitHubProfile:
    """Tests for profile parsing function."""
  
    def test_parse_full_profile(self):
        raw = {
            "name": "John Doe",
            "bio": "Software engineer",
            "avatar_url": "https://example.com/avatar.png",
            "location": "NYC",
            "company": "Acme",
            "blog": "https://blog.com",
            "twitter_username": "johndoe"
        }
        result = parse_github_profile(raw)
        assert result.name == "John Doe"
        assert result.bio == "Software engineer"
        assert result.avatar_url == "https://example.com/avatar.png"
  
    def test_parse_missing_name_uses_login(self):
        raw = {"login": "fallbackuser", "bio": "Bio"}
        result = parse_github_profile(raw)
        assert result.name == "fallbackuser"
  
    def test_parse_empty_bio_uses_default(self):
        raw = {"name": "User"}
        result = parse_github_profile(raw)
        assert result.bio == "Building cool things"


class TestImportGitHubProfile:
    """Tests for GitHub profile import."""
  
    def test_import_profile_uses_mock_client(self):
        client = MockGitHubClient(profile_data={"name": "Test"})
        result = import_github_profile("https://github.com/testuser", client=client)
        assert result.name == "Test"
  
    def test_import_profile_invalid_url_raises_error(self):
        with pytest.raises(ValueError, match="Invalid GitHub URL"):
            import_github_profile("not-a-url")


class TestSelectReposInteractive:
    """Tests for interactive repo selection."""
  
    def test_select_all_repos_when_empty_input(self, monkeypatch):
        import io
        from unittest.mock import patch
        
        # Mock user pressing Enter (empty input)
        with patch('sys.stdin', io.StringIO('\n')):
            client = MockGitHubClient(repos=[{"name": "r1"}, {"name": "r2"}])
            result = select_repos_interactive("test", client=client)
            assert len(result) == 2
  
    def test_select_no_repos_empty_list(self):
        client = MockGitHubClient(repos=[])
        result = select_repos_interactive("test", client=client)
        assert result == []


class TestCreateProjectFromGitHub:
    """Tests for project creation from GitHub."""
  
    def test_create_project_from_repo_metadata(self):
        repo = {
            "name": "test-repo",
            "owner": {"login": "testuser"},
            "description": "Test description",
            "language": "Python",
            "updated_at": "2024-01-01T00:00:00Z",
            "created_at": "2023-01-01T00:00:00Z",
            "size": 1000
        }
        result = create_project_from_github(repo, "testuser")
        assert result.id == "test-repo"
        assert result.name == "test-repo"
        assert result.slug == "test-repo"
        assert result.description == "Test description"
        assert result.primary_language == "Python"
  
    def test_create_project_handles_missing_fields(self):
        repo = {"name": "simple", "owner": {"login": "user"}}
        result = create_project_from_github(repo, "user")
        assert result.name == "simple"
        assert result.description is None