from datetime import datetime

from data.models import ProjectRecord, slugify


def test_slugify_basic():
    assert slugify("My Cool Project") == "my-cool-project"
    assert slugify("React + TypeScript App!") == "react-typescript-app"
    assert slugify("project--name") == "project-name"


def test_project_record_to_json_dict():
    p = ProjectRecord(
        id="abc",
        path="/tmp",
        name="test",
        slug="test",
        last_active=datetime(2024, 6, 1),
        total_commits=50,
    )
    d = p.to_json_dict()
    assert d["id"] == "abc"
    assert d["total_commits"] == 50
    assert d["quality_score"] == 0.0


def test_last_active_display_recent():
    p = ProjectRecord(id="x", path="/t", name="t", slug="t", last_active=datetime.utcnow())
    assert p.last_active_display == "Today"


def test_last_active_display_old():
    from datetime import timedelta

    p = ProjectRecord(
        id="x", path="/t", name="t", slug="t", last_active=datetime.utcnow() - timedelta(days=400)
    )
    assert "year" in p.last_active_display
