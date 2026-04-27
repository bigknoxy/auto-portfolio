import subprocess
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def pytest_configure(config):
    """Create test git fixtures if they don't exist."""
    sample = FIXTURES_DIR / "sample_repo"
    if not (sample / ".git").exists():
        subprocess.run(
            ["git", "init"],
            cwd=sample,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=sample,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=sample,
            capture_output=True,
        )
        pkg = (
            '{"name":"sample-app","version":"1.0.0",'
            '"dependencies":{"react":"^18.0.0",'
            '"typescript":"^5.0.0"}}'
        )
        (sample / "package.json").write_text(pkg)
        (sample / "README.md").write_text("# Sample App\n\nA sample web application for testing.\n")
        (sample / "index.html").write_text("<html><body>Hello</body></html>")
        subprocess.run(
            ["git", "add", "."],
            cwd=sample,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "feat: initial app setup"],
            cwd=sample,
            capture_output=True,
        )
        (sample / "index.html").write_text("<html><body>Hello World</body></html>")
        subprocess.run(
            ["git", "add", "."],
            cwd=sample,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "fix: update greeting"],
            cwd=sample,
            capture_output=True,
        )

    backend = FIXTURES_DIR / "backend_repo"
    if not (backend / ".git").exists():
        subprocess.run(
            ["git", "init"],
            cwd=backend,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=backend,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=backend,
            capture_output=True,
        )
        pyproj = '[project]\nname = "backend-api"\ndependencies = ["fastapi", "uvicorn"]'
        (backend / "pyproject.toml").write_text(pyproj)
        (backend / "main.py").write_text("from fastapi import FastAPI\napp = FastAPI()\n")
        subprocess.run(
            ["git", "add", "."],
            cwd=backend,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "feat: fastapi backend"],
            cwd=backend,
            capture_output=True,
        )
