"""Profile importer for GitHub-based portfolio generation.

This module handles importing user profiles and selecting repositories
from GitHub for portfolio generation.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from rich.console import Console

from core.github_client import GitHubAPIClient

if TYPE_CHECKING:
    from core.models import ProjectRecord


console = Console()


@dataclass
class GitHubProfileData:
    """Parsed GitHub profile data."""
    name: str
    title: str
    bio: str
    avatar_url: str | None
    location: str | None
    company: str | None
    twitter_username: str | None
    blog_url: str | None


def parse_github_profile(raw_data: dict) -> GitHubProfileData:
    """Parse raw GitHub API response into structured profile data.
    
    Args:
        raw_data: Raw response from GitHub API /users endpoint
      
    Returns:
        Structured profile data with safe defaults
    """
    return GitHubProfileData(
        name=raw_data.get("name") or raw_data.get("login", "Unknown"),
        title=raw_data.get("blog", "") or "",
        bio=raw_data.get("bio", "") or "Building cool things",
        avatar_url=raw_data.get("avatar_url"),
        location=raw_data.get("location"),
        company=raw_data.get("company"),
        twitter_username=raw_data.get("twitter_username"),
        blog_url=raw_data.get("blog")
    )


def import_github_profile(
    github_url: str, 
    client: GitHubAPIClient | None = None
) -> "GitHubProfileData":
    """Import profile data from GitHub URL.
    
    Args:
        github_url: GitHub profile URL (e.g., https://github.com/username)
        client: GitHub API client (uses default if None)
      
    Returns:
        Parsed profile data
      
    Raises:
        ValueError: If URL is invalid
        RuntimeError: If API call fails
    """
    if not github_url or "github.com" not in github_url:
        raise ValueError("Invalid GitHub URL")
    
    username = github_url.rstrip("/").split("/")[-1]
    client = client or _get_default_client()
    
    profile_raw = client.get_user_profile(username)
    return parse_github_profile(profile_raw)


def _get_default_client() -> GitHubAPIClient:
    """Get default GitHub API client."""
    from core.github_client import get_default_client
    return get_default_client()


def select_repos_interactive(
    username: str, 
    client: GitHubAPIClient | None = None,
    all_repos: list[dict] | None = None
) -> list[dict]:
    """Interactive repository selection.
    
    Shows available repos and prompts user to select which to include.
    
    Args:
        username: GitHub username
        client: GitHub API client
        all_repos: Pre-fetched repos (for testing)
      
    Returns:
        List of selected repository metadata
    """
    client = client or _get_default_client()
    
    if all_repos is None:
        # Fetch repos (simplified - just first page)
        all_repos = client.get_user_repos(username, per_page=100, page=1)
    
    if not all_repos:
        console.print("[yellow]No public repositories found.[/yellow]")
        return []
    
    console.print(f"\n[bold]Found {len(all_repos)} repositories[/bold]\n")
    console.print("[bold]Select repositories to include:[/bold]\n")
    
    # Show numbered list
    for i, repo in enumerate(all_repos, 1):
        description = repo.get("description", "No description") or ""
        lang = repo.get("language", "Unknown")
        stars = repo.get("stargazers_count", 0)
        console.print(f"{i}. {repo['name']} - {lang} ({stars}★)")
        desc = description[:60] if len(description) > 60 else description
        console.print(f"   {desc}...\n" if len(description) > 60 else f"   {desc}\n")
    
    # Prompt for selection
    selected_input = console.input(
        "[bold blue]Enter numbers to include (comma-separated, or Enter for all): [/bold blue]"
    ).strip()
    
    if not selected_input:
        return all_repos
    
    try:
        indices = [int(x.strip()) - 1 for x in selected_input.split(",")]
        return [all_repos[i] for i in indices if 0 <= i < len(all_repos)]
    except ValueError:
        console.print("[red]Invalid selection format[/red]")
        return all_repos


def create_project_from_github(repo: dict, username: str) -> "ProjectRecord":
    """Create ProjectRecord from GitHub repository metadata.
    
    Args:
        repo: Repository metadata from GitHub API
        username: GitHub username (for remote URL)
      
    Returns:
        ProjectRecord for portfolio generation
    """
    from data.models import ProjectRecord
    
    updated_at = repo.get("updated_at")
    last_active = datetime.fromisoformat(updated_at.rstrip("Z")) if updated_at else None
    
    created_at_raw = repo.get("created_at", "")
    created_at = None
    if created_at_raw:
        created_at = datetime.fromisoformat(created_at_raw.rstrip("Z"))
  
    primary_lang = repo.get("language")
    
    return ProjectRecord(
        id=repo["name"],
        path=f"https://github.com/{username}/{repo['name']}",
        name=repo["name"],
        slug=repo["name"].lower().replace("_", "-"),
        description=repo.get("description"),
        remote_url=f"https://github.com/{username}/{repo['name']}",
        created_at=created_at,
        last_active=last_active,
        total_commits=0,
        contributors=[username],
        primary_language=primary_lang,
        languages={primary_lang: 100.0} if primary_lang else {},
        stack=[],
        has_docs=bool(repo.get("description")),
        size_bytes=repo.get("size", 0) or 0
    )