from core.repo_scanner import _repo_id, scan_repo, scan_root
from tests.conftest import FIXTURES_DIR


def test_scan_repo_returns_record():
    record = scan_repo(FIXTURES_DIR / "sample_repo", use_cache=False)
    assert record is not None
    assert record.name == "sample_repo"
    assert record.total_commits >= 2


def test_scan_repo_has_readme_description():
    record = scan_repo(FIXTURES_DIR / "sample_repo", use_cache=False)
    assert record.has_docs is True
    assert record.description is not None
    assert len(record.description) > 10


def test_scan_repo_backend_detects_python():
    record = scan_repo(FIXTURES_DIR / "backend_repo", use_cache=False)
    assert record is not None
    assert "Python" in record.stack


def test_scan_repo_non_git_returns_none(tmp_path):
    record = scan_repo(tmp_path, use_cache=False)
    assert record is None


def test_repo_id_is_stable():
    id1 = _repo_id(FIXTURES_DIR / "sample_repo")
    id2 = _repo_id(FIXTURES_DIR / "sample_repo")
    assert id1 == id2
    assert len(id1) == 16


def test_scan_root_finds_both_fixtures():
    records = scan_root(FIXTURES_DIR, min_commits=1)
    names = [r.name for r in records]
    assert "sample_repo" in names
    assert "backend_repo" in names


def test_scan_root_respects_min_commits():
    records = scan_root(FIXTURES_DIR, min_commits=100)
    assert all(r.total_commits >= 100 for r in records)


def test_scan_root_empty_dir_returns_empty(tmp_path):
    records = scan_root(tmp_path)
    assert records == []
