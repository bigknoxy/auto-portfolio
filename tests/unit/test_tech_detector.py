from core.tech_detector import detect_languages, detect_quality_signals, detect_stack
from tests.conftest import FIXTURES_DIR


def test_detect_stack_sample_repo():
    stack = detect_stack(FIXTURES_DIR / "sample_repo")
    assert "JavaScript" in stack or "TypeScript" in stack or "React" in stack


def test_detect_stack_backend_repo():
    stack = detect_stack(FIXTURES_DIR / "backend_repo")
    assert "Python" in stack
    assert "FastAPI" in stack


def test_detect_stack_returns_list():
    stack = detect_stack(FIXTURES_DIR / "sample_repo")
    assert isinstance(stack, list)


def test_detect_languages_returns_percentages():
    langs = detect_languages(FIXTURES_DIR / "sample_repo")
    if langs:
        assert all(0 < v <= 100 for v in langs.values())
        assert abs(sum(langs.values()) - 100) < 5  # roughly sums to 100


def test_detect_quality_signals_has_docs():
    has_tests, has_ci, has_docs, score = detect_quality_signals(FIXTURES_DIR / "sample_repo")
    assert has_docs is True  # README.md exists
    assert 0.0 <= score <= 1.0


def test_detect_quality_signals_no_ci():
    has_tests, has_ci, has_docs, score = detect_quality_signals(FIXTURES_DIR / "sample_repo")
    assert has_ci is False  # No .github/workflows in fixture
