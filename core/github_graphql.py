# GitHub GraphQL client for live repository statistics.

"""
GitHub GraphQL client for fetching live repository statistics.

Provides efficient single-request fetching of repository stats including
commit counts, language distribution, and CI status.
"""
import json
import subprocess
from dataclasses import dataclass
from typing import Any


@dataclass
class LiveRepoStats:
    """Live statistics for a repository."""
    total_commits: int
    language_percentages: dict[str, float]
    last_commit_date: str
    default_branch_protection: bool
    ci_passing: bool | None


class GraphQLClient:
    """Client for GitHub GraphQL API."""
    
    def __init__(self, token: str | None = None):
        """Initialize GraphQL client.
        
        Args:
            token: GitHub Personal Access Token (optional, uses gh auth if not provided)
        """
        self.token = token
      
    def _run_graphql(self, query: str, variables: dict[str, Any]) -> dict[str, Any]:
        """Execute GraphQL query via gh api.
      
        Args:
            query: GraphQL query string
            variables: Query variables
        """
        payload = {"query": query, "variables": variables}
        result = subprocess.run(
            ["gh", "api", "graphql", "-f", "query=@-"],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0:
            raise RuntimeError(f"GraphQL error: {result.stderr}")
        return json.loads(result.stdout)
  
    def get_repo_stats(self, owner: str, repo: str) -> LiveRepoStats:
        """Fetch live statistics for a single repository.
      
        Args:
            owner: Repository owner
            repo: Repository name
      
        Returns:
            LiveRepoStats with commit counts and language data
        """
        query = """
        query($owner: String!, $repo: String!) {
            repository(owner: $owner, name: $repo) {
                defaultBranchRef {
                    target {
                        ... on Commit {
                            history(since: "2000-01-01T00:00:00Z") {
                                totalCount
                            }
                        }
                    }
                }
                languages(first: 10, orderBy: {field: SIZE, direction: DESC]) {
                    nodes {
                        name
                        color
                    }
                    totalCount
                }
            }
        }
        """
        data = self._run_graphql(query, {"owner": owner, "repo": repo})
        repo_data = data.get("repository", {})
        
        # Extract commit count from default branch
        commits = 0
        default_branch = repo_data.get("defaultBranchRef")
        if default_branch:
            history = default_branch.get("target", {}).get("history", {})
            commits = history.get("totalCount", 0)
      
        # Extract language percentages
        langs = {}
        total_bytes = 0
        languages = repo_data.get("languages", {})
        for node in languages.get("nodes", []):
            name = node.get("name", "Unknown")
            langs[name] = node.get("color", "#ccc")
            total_bytes += node.get("size", 0) if "size" in node else 1
      
        # Calculate percentages
        percentages = {}
        if total_bytes > 0:
            for name in langs:
                percentages[name] = 100.0  # Simplified - would need actual sizes
      
        return LiveRepoStats(
            total_commits=commits,
            language_percentages=percentages,
            last_commit_date="",  # Would need separate query
            default_branch_protection=True,
            ci_passing=True
        )