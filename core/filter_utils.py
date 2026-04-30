"""Project filtering utilities for enhanced local scanner.

Provides reusable filtering logic for both local and GitHub workflows.
"""
import fnmatch
from collections.abc import Iterable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from data.models import ProjectRecord


def matches_pattern(text: str, pattern: str) -> bool:
    """Check if text matches a glob pattern.

    Args:
        text: Text to check (name or path)
        pattern: Glob pattern (e.g., "backend-*", "*/test")

    Returns:
        True if text matches pattern
    """
    text_lower = text.lower()
    pattern_lower = pattern.lower()
    fn1 = fnmatch.fnmatch(text_lower, pattern_lower)
    fn2 = fnmatch.fnmatch(text_lower, f"*{pattern_lower}*")
    return fn1 or fn2


def should_include_project(
    project: "ProjectRecord",
    include_patterns: Iterable[str] = (),
    exclude_patterns: Iterable[str] = ()
) -> bool:
    """Determine if project should be included based on patterns.
    
    Args:
        project: Project to evaluate
        include_patterns: Glob patterns for inclusion
        exclude_patterns: Glob patterns for exclusion
      
    Returns:
        True if project should be included
    """
    name = project.name
    path = str(project.path)
    
    # Check exclusions first
    for pattern in exclude_patterns:
        if matches_pattern(name, pattern) or matches_pattern(path, pattern):
            return False
    
    # If include patterns specified, must match at least one
    if include_patterns:
        for pattern in include_patterns:
            if matches_pattern(name, pattern) or matches_pattern(path, pattern):
                return True
        return False
    
    return True


def filter_projects(
    projects: list["ProjectRecord"],
    include_patterns: Iterable[str] = (),
    exclude_patterns: Iterable[str] = ()
) -> list["ProjectRecord"]:
    """Filter projects based on include/exclude patterns.
    
    Args:
        projects: Projects to filter
        include_patterns: Glob patterns for inclusion
        exclude_patterns: Glob patterns for exclusion
      
    Returns:
        Filtered list of projects
    """
    return [
        p for p in projects
        if should_include_project(p, include_patterns, exclude_patterns)
    ]


def filter_by_stars(
    projects: list["ProjectRecord"],
    min_stars: int = 0
) -> list["ProjectRecord"]:
    """Filter projects by minimum star count.
    
    Args:
        projects: Projects to filter
        min_stars: Minimum required stars
      
    Returns:
        Filtered project list
    """
    return [p for p in projects if p.quality_score >= min_stars / 100.0]


def get_project_summary(projects: list["ProjectRecord"]) -> dict:
    """Get summary statistics for project list.
    
    Args:
        projects: List of projects
      
    Returns:
        Summary with counts and languages
    """
    languages: dict[str, int] = {}
    for p in projects:
        for lang, pct in p.languages.items():
            languages[lang] = languages.get(lang, 0) + int(pct)
  
    return {
        "total": len(projects),
        "by_language": languages,
        "total_commits": sum(p.total_commits for p in projects)
    }