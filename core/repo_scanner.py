import hashlib
import json
import subprocess
from datetime import datetime
from pathlib import Path

from core.tech_detector import detect_languages, detect_quality_signals, detect_stack
from data.models import ProjectRecord, slugify

CACHE_DIR = Path.home() / ".cache" / "auto-portfolio"


def _repo_id(path: Path) -> str:
    return hashlib.sha256(str(path.resolve()).encode()).hexdigest()[:16]


def _run_git(args: list[str], cwd: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(cwd)] + args, capture_output=True, text=True, timeout=20
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""


def _get_cache_path(repo_id: str, head_sha: str) -> Path:
    return CACHE_DIR / repo_id / f"{head_sha}.json"


def _load_from_cache(repo_id: str, head_sha: str) -> dict | None:
    cache_path = _get_cache_path(repo_id, head_sha)
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return None


def _save_to_cache(repo_id: str, head_sha: str, data: dict) -> None:
    cache_path = _get_cache_path(repo_id, head_sha)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        cache_path.write_text(json.dumps(data, default=str))
    except OSError:
        pass


def _read_readme(repo_path: Path) -> tuple[str | None, str | None]:
    """Return (short_description, long_description) from README."""
    for name in ["README.md", "README.txt", "readme.md"]:
        readme = repo_path / name
        if readme.exists():
            try:
                content = readme.read_text(errors="replace")
                paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
                # Skip title line and badge lines
                text_paras = [
                    p
                    for p in paragraphs
                    if not p.startswith("#") and not p.startswith("!") and len(p) > 20
                ]
                if text_paras:
                    long_desc = text_paras[0][:500]
                    short_desc = long_desc[:280]
                    # Cut to sentence boundary
                    for punct in [". ", "! ", "? "]:
                        idx = short_desc.find(punct)
                        if 30 < idx < 200:
                            short_desc = short_desc[: idx + 1]
                            break
                    return short_desc, long_desc
            except OSError:
                pass
    return None, None


def scan_repo(path: Path, use_cache: bool = True) -> ProjectRecord | None:
    """Scan a single git repository and return a ProjectRecord."""
    if not (path / ".git").exists():
        return None

    path = path.resolve()
    repo_id = _repo_id(path)

    # Get HEAD SHA for cache key
    head_sha = _run_git(["rev-parse", "HEAD"], path)
    if not head_sha:
        return None  # Empty repo or no commits

    # Try cache first
    if use_cache:
        cached = _load_from_cache(repo_id, head_sha)
        if cached:
            try:
                return ProjectRecord(**cached)
            except Exception:
                pass

    # Scan the repo
    try:
        name = path.name
        slug = slugify(name)

        # Git metadata
        first_commit_str = _run_git(["log", "--reverse", "--format=%cI", "--max-count=1"], path)
        last_commit_str = _run_git(["log", "--format=%cI", "--max-count=1"], path)
        total_str = _run_git(["rev-list", "--count", "HEAD"], path)
        remote = _run_git(["remote", "get-url", "origin"], path) or None
        contributors_raw = _run_git(["shortlog", "-sn", "--no-merges", "HEAD"], path)

        first_commit = _parse_dt(first_commit_str)
        last_commit = _parse_dt(last_commit_str)
        total_commits = int(total_str) if total_str.isdigit() else 0
        contributors = [
            line.split("\t", 1)[1].strip() for line in contributors_raw.splitlines() if "\t" in line
        ]

        # Tech stack
        stack = detect_stack(path)
        langs = detect_languages(path)
        primary_lang = list(langs.keys())[0] if langs else (stack[0] if stack else None)
        has_tests, has_ci, has_docs, quality_score = detect_quality_signals(path)

        # README
        description, long_description = _read_readme(path)

        # Directory size (rough)
        size_bytes = sum(
            f.stat().st_size for f in path.rglob("*") if f.is_file() and ".git" not in f.parts
        )

        record = ProjectRecord(
            id=repo_id,
            path=str(path),
            name=name,
            slug=slug,
            description=description,
            long_description=long_description,
            remote_url=remote,
            created_at=first_commit,
            last_active=last_commit,
            total_commits=total_commits,
            contributors=contributors[:10],
            primary_language=primary_lang,
            languages=langs,
            stack=stack,
            has_tests=has_tests,
            has_ci=has_ci,
            has_docs=has_docs,
            quality_score=quality_score,
            tags=[],
            size_bytes=size_bytes,
        )

        # Cache for next run
        if use_cache:
            _save_to_cache(repo_id, head_sha, record.model_dump())

        return record

    except Exception:
        return None


def _parse_dt(s: str) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def scan_root(
    root: Path, min_commits: int = 1, max_depth: int = 5, exclude: list[str] | None = None
) -> list[ProjectRecord]:
    """Walk root directory and return all ProjectRecords found."""
    records: list[ProjectRecord] = []
    root = root.expanduser().resolve()
    if not root.exists():
        return records

    def _walk(current: Path, depth: int) -> None:
        if depth > max_depth:
            return
        if (current / ".git").exists():
            record = scan_repo(current)
            if record and record.total_commits >= min_commits:
                records.append(record)
            return  # Don't recurse into git repos
        try:
            for child in sorted(current.iterdir()):
                if child.is_dir() and not child.name.startswith("."):
                    _walk(child, depth + 1)
        except PermissionError:
            pass

    _walk(root, 0)
    return records
