"""Tests for GitHub GraphQL client."""
import pytest

from core.github_graphql import GraphQLClient, LiveRepoStats


class TestGraphQLClient:
    """Tests for GraphQLClient."""
    
    def test_live_repo_stats_dataclass(self):
        """Test LiveRepoStats dataclass."""
        stats = LiveRepoStats(
            total_commits=100,
            language_percentages={"Python": 80.0, "JavaScript": 20.0},
            last_commit_date="2024-01-15T10:30:00Z",
            default_branch_protection=True,
            ci_passing=True
        )
        assert stats.total_commits == 100
        assert stats.language_percentages["Python"] == 80.0
    
    def test_client_init(self):
        """Test GraphQLClient initialization."""
        client = GraphQLClient()
        assert client.token is None
        
        client_with_token = GraphQLClient(token="test-token")
        assert client_with_token.token == "test-token"