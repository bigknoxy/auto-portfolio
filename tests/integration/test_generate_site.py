import json

from core.config import ProfileConfig
from core.repo_scanner import scan_root
from core.site_generator import write_profile_json, write_projects_json
from tests.conftest import FIXTURES_DIR


def test_scan_and_write_json(tmp_path):
    records = scan_root(FIXTURES_DIR, min_commits=1)
    assert len(records) >= 2

    data_dir = tmp_path / "data"
    out = write_projects_json(records, data_dir)
    assert out.exists()

    data = json.loads(out.read_text())
    assert "projects" in data
    assert len(data["projects"]) == len(records)
    assert "generated_at" in data


def test_project_json_has_required_fields(tmp_path):
    records = scan_root(FIXTURES_DIR, min_commits=1)
    data_dir = tmp_path / "data"
    out = write_projects_json(records, data_dir)
    data = json.loads(out.read_text())

    for project in data["projects"]:
        required = ["id", "name", "slug", "total_commits", "stack", "quality_score"]
        for field in required:
            assert field in project, f"Missing field '{field}' in project {project.get('name')}"


def test_write_profile_json(tmp_path):
    profile = ProfileConfig(name="Joshua", title="Dev", bio="I code.")
    out = write_profile_json(profile, tmp_path)
    assert out.exists()
    data = json.loads(out.read_text())
    assert data["name"] == "Joshua"


def test_generate_produces_valid_slugs(tmp_path):
    records = scan_root(FIXTURES_DIR, min_commits=1)
    data_dir = tmp_path / "data"
    out = write_projects_json(records, data_dir)
    data = json.loads(out.read_text())
    for p in data["projects"]:
        assert p["slug"] == p["slug"].lower()
        assert " " not in p["slug"]
