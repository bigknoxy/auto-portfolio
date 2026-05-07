"""GitHub API client for profile/portfolio generation.

This module provides a clean, testable interface to GitHub's REST API
for importing user profiles and repository data.
"""
import json
import subprocess
from typing import Any, Protocol

from typing_extensions import runtime_checkable


@runtime_checkable
class GitHubAPIClient(Protocol):
    """Protocol defining GitHub API interface for dependency injection."""
    
    def get_user_profile(self, username: str) -> dict[str, Any]:
        """Fetch user profile information."""
        ...
    
    def get_user_repos(self, username: str, per_page: int, page: int) -> list[dict[str, Any]]:
        """Fetch user's repositories."""
        ...


class GHCLIClient:
    """Concrete implementation using GitHub CLI (gh)."""
    
    def _run_gh(self, args: list[str]) -> dict[str, Any] | list[dict[str, Any]]:
        """Run gh CLI command and return JSON output.
        
        Args:
            args: Additional arguments to pass to gh api
            
        Returns:
            Parsed JSON response
            
        Raises:
            RuntimeError: If gh command fails
        """
        result = subprocess.run(
            ["gh", "api", *args],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0:
            raise RuntimeError(f"gh API error: {result.stderr}")
        return json.loads(result.stdout)
    
    def get_user_profile(self, username: str) -> dict[str, Any]:
        """Fetch user profile information.
        
        Args:
            username: GitHub username
            
        Returns:
            User profile data including name, bio, avatar_url, etc.
        """
        return self._run_gh([f"/users/{username}"])
    
    def get_user_repos(
        self, 
        username: str, 
        per_page: int = 100, 
        page: int = 1
    ) -> list[dict[str, Any]]:
        """Fetch user's public repositories.
        
        Args:
            username: GitHub username
            per_page: Results per page (max 100)
            page: Page number for pagination
            
        Returns:
            List of repository metadata dicts
        """
        return self._run_gh([
            f"/users/{username}/repos",
            f"--per-page={per_page}",
            f"--page={page}",
            "--type=public"
        ])


class MockGitHubClient:
    """Mock client for testing purposes."""

    def __init__(
        self,
        profile_data: dict[str, Any] | None = None,
        repos: list[dict[str, Any]] | None = None,
    ):
        self.profile_data = profile_data or {
            "name": "Test User",
            "bio": "Test bio",
            "avatar_url": "http://example.com/avatar.png",
        }
        self.repos = repos or []

    def get_user_profile(self, username: str) -> dict[str, Any]:
        return self.profile_data

    def get_user_repos(
        self, username: str, per_page: int = 100, page: int = 1
    ) -> list[dict[str, Any]]:
        return self.repos


def get_default_client() -> GitHubAPIClient:
    """Factory function for GitHub API client.
    
    Returns:
        Default GHCLIClient instance
    """
    return GHCLIClient()