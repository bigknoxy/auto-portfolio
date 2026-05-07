"""Integration tests for GitHub portfolio workflow."""
import json

from core.config import ProfileConfig
from core.github_client import MockGitHubClient
from core.profile_importer import create_project_from_github, import_github_profile
from core.site_generator import write_profile_json, write_projects_json


class TestGitHubWorkflow:
    """End-to-end GitHub portfolio generation workflow."""

    def test_full_workflow_with_mock_client(self, tmp_path):
        """Complete workflow from profile import to JSON files."""
        # Setup mock client with test data
        mock_client = MockGitHubClient(
            profile_data={
                "name": "Test Developer",
                "bio": "Building cool stuff",
                "avatar_url": "https://example.com/avatar.png",
            },
            repos=[
                {
                    "name": "api-service",
                    "owner": {"login": "testuser"},
                    "description": "REST API",
                    "language": "Python",
                    "updated_at": "2024-01-01T00:00:00Z",
                    "created_at": "2023-01-01T00:00:00Z",
                    "stargazers_count": 10,
                },
                {
                    "name": "web-app",
                    "owner": {"login": "testuser"},
                    "description": "Frontend",
                    "language": "TypeScript",
                    "updated_at": "2024-01-01T00:00:00Z",
                    "created_at": "2023-06-01T00:00:00Z",
                    "stargazers_count": 5,
                },
            ],
        )

        # Import profile
        profile = import_github_profile(
            "https://github.com/testuser", client=mock_client
        )
        assert profile.name == "Test Developer"

        # Create projects
        repos = mock_client.get_user_repos("testuser")
        projects = [create_project_from_github(r, "testuser") for r in repos]
        assert len(projects) == 2

        # Write files
        data_dir = tmp_path / "src" / "data"
        data_dir.mkdir(parents=True)

        profile_cfg = ProfileConfig(
            name=profile.name,
            title="Developer",
            bio=profile.bio,
            avatar=profile.avatar_url,
            social={},
        )
        write_profile_json(profile_cfg, data_dir)
        write_projects_json([p.to_json_dict() for p in projects], data_dir)

        # Verify files exist
        profile_file = data_dir / "profile.json"
        assert profile_file.exists()

        projects_file = data_dir / "projects.json"
        assert projects_file.exists()

        # Verify content
        with open(profile_file) as f:
            profile_data = json.load(f)
        assert profile_data["name"] == "Test Developer"

        with open(projects_file) as f:
            projects_data = json.load(f)
        assert len(projects_data["projects"]) == 2
        assert projects_data["projects"][0]["name"] == "api-service"