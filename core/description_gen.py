import subprocess
from pathlib import Path


def generate_description(
    repo_path: Path,
    existing_description: str | None,
    stack: list[str],
    total_commits: int,
    name: str,
) -> str:
    """
    Generate a short project description.
    Priority: existing README description > heuristic from commits > fallback.
    """
    if existing_description and len(existing_description.strip()) > 20:
        return existing_description.strip()

    # Heuristic: build description from detected stack and activity
    lang_str = " + ".join(stack[:3]) if stack else "code"
    if total_commits > 100:
        activity = "actively developed"
    elif total_commits > 20:
        activity = "growing"
    else:
        activity = "experimental"

    return f"An {activity} {lang_str} project."


def extract_commit_highlights(repo_path: Path, n: int = 10) -> list[str]:
    """Return the last N non-merge commit messages."""
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_path), "log", "--no-merges", f"--max-count={n}", "--format=%s"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return []
