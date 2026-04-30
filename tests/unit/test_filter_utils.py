"""Unit tests for filter utilities module."""
import pytest

from core.filter_utils import (
    filter_projects,
    get_project_summary,
    matches_pattern,
    should_include_project,
)
from data.models import ProjectRecord


@pytest.fixture
def sample_projects() -> list[ProjectRecord]:
    """Create sample projects for testing."""
    return [
        ProjectRecord(
            id="p1",
            path="/projects/backend-api",
            name="backend-api",
            slug="backend-api",
            description="API service",
            primary_language="Python",
            languages={"Python": 100.0}
        ),
        ProjectRecord(
            id="p2",
            path="/projects/frontend-app",
            name="frontend-app",
            slug="frontend-app",
            description="Web app", 
            primary_language="TypeScript",
            languages={"TypeScript": 100.0}
        ),
        ProjectRecord(
            id="p3",
            path="/projects/backend-worker",
            name="backend-worker",
            slug="backend-worker",
            description="Worker",
            primary_language="Python",
            languages={"Python": 100.0}
        ),
        ProjectRecord(
            id="p4",
            path="/test/test-utils",
            name="test-utils",
            slug="test-utils",
            description="Utils",
            primary_language="Python",
            languages={"Python": 100.0}
        )
    ]


class TestMatchesPattern:
    """Tests for pattern matching function."""
  
    def test_match_suffix_pattern(self):
        assert matches_pattern("backend-api", "backend-*")
  
    def test_match_prefix_pattern(self):
        assert matches_pattern("my-backend", "*-backend")
  
    def test_match_no_pattern_fails(self):
        assert not matches_pattern("frontend", "backend-*")
  
    def test_match_case_insensitive(self):
        assert matches_pattern("BACKEND-API", "backend-*")


class TestShouldIncludeProject:
    """Tests for project inclusion logic."""
  
    def test_include_with_pattern_matches(self, sample_projects):
        project = sample_projects[0]
        assert should_include_project(project, include_patterns=["backend-*"])
  
    def test_include_without_match_excludes(self, sample_projects):
        project = sample_projects[1]
        assert not should_include_project(project, include_patterns=["backend-*"])
  
    def test_exclude_pattern_takes_precedence(self, sample_projects):
        project = sample_projects[0]
        assert not should_include_project(
            project, 
            include_patterns=["backend-*"], 
            exclude_patterns=["backend-*"]
        )
  
    def test_no_patterns_includes_all(self, sample_projects):
        project = sample_projects[0]
        assert should_include_project(project)


class TestFilterProjects:
    """Tests for project filtering function."""
  
    def test_filter_with_include_patterns(self, sample_projects):
        result = filter_projects(sample_projects, include_patterns=["backend-*"])
        assert len(result) == 2
        assert all("backend" in p.name for p in result)
  
    def test_filter_with_exclude_patterns(self, sample_projects):
        result = filter_projects(sample_projects, exclude_patterns=["*-utils"])
        assert all("utils" not in p.name for p in result)
    def test_filter_combined(self, sample_projects):
        result = filter_projects(
            sample_projects,
            include_patterns=["backend-*"],
            exclude_patterns=["*-worker"]
        )
        assert len(result) == 1
        assert result[0].name == "backend-api"


class TestGetProjectSummary:
    """Tests for project summary function."""
  
    def test_summary_counts_projects(self, sample_projects):
        result = get_project_summary(sample_projects)
        assert result["total"] == 4
  
    def test_summary_groups_by_language(self, sample_projects):
        result = get_project_summary(sample_projects)
        assert "Python" in result["by_language"]
        assert "TypeScript" in result["by_language"]