# Auto-Portfolio — Atomic Task List

> Every task is self-contained. Read it fully, execute each step exactly,
> run the verification command, and only proceed when it passes.
> Small models: do NOT skip verifications.

Reference docs:
- `PLAN.md` — architecture, phases, design philosophy
- `IMPLEMENTATION.md` — data schema, scanner API, site generation, CI

---

## TASK-001: Initialize Python project

**Depends on:** nothing
**Files created:** `pyproject.toml`, `.python-version`, `.gitignore`

### Steps

```bash
cd ~/projects/auto-portfolio
uv init --name auto-portfolio --python 3.12
```

Replace generated `pyproject.toml`:
```toml
[project]
name = "auto-portfolio"
version = "0.1.0"
description = "Zero-input portfolio generator from git history"
requires-python = ">=3.12"
dependencies = [
    "gitpython>=3.1.40",
    "pydantic>=2.6.0",
    "rich>=13.7.0",
    "typer>=0.12.0",
    "tomli>=2.0.1",
    "jinja2>=3.1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.1.0",
    "pytest-cov>=5.0.0",
    "ruff>=0.4.0",
]
playwright = [
    "playwright>=1.43.0",
]

[project.scripts]
auto-portfolio = "cmd.auto_portfolio:app"

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP"]
```

Create `.python-version`:
```
3.12
```

Create `.gitignore`:
```
.venv/
__pycache__/
*.pyc
site/dist/
site/node_modules/
~/.cache/auto-portfolio/
.coverage
dist/
*.egg-info/
.ruff_cache/
```

### Verification
```bash
cd ~/projects/auto-portfolio
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
python -c "import gitpython, pydantic, rich, typer, jinja2; print('OK')" 2>/dev/null || \
python -c "import git, pydantic, rich, typer, jinja2; print('OK')"
```
**Done when:** prints `OK`.

---

## TASK-002: Create directory skeleton

**Depends on:** TASK-001
**Files created:** all package directories + `__init__.py`

### Steps

```bash
cd ~/projects/auto-portfolio
mkdir -p cmd core data/themes deploy templates tests/unit tests/integration
mkdir -p tests/fixtures/sample_repo tests/fixtures/backend_repo
mkdir -p site/src/components site/src/layouts site/src/pages site/src/styles site/src/data
mkdir -p site/public/previews
mkdir -p .github/workflows

touch cmd/__init__.py
touch core/__init__.py
touch data/__init__.py
touch deploy/__init__.py
touch tests/__init__.py tests/unit/__init__.py tests/integration/__init__.py
```

Create `tests/conftest.py`:
```python
import pytest
from pathlib import Path
import subprocess

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def pytest_configure(config):
    """Create test git fixtures if they don't exist."""
    sample = FIXTURES_DIR / "sample_repo"
    if not (sample / ".git").exists():
        subprocess.run(["git", "init"], cwd=sample, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=sample, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=sample, capture_output=True)
        (sample / "package.json").write_text('{"name":"sample-app","version":"1.0.0","dependencies":{"react":"^18.0.0","typescript":"^5.0.0"}}')
        (sample / "README.md").write_text("# Sample App\n\nA sample web application for testing.\n")
        (sample / "index.html").write_text("<html><body>Hello</body></html>")
        subprocess.run(["git", "add", "."], cwd=sample, capture_output=True)
        subprocess.run(["git", "commit", "-m", "feat: initial app setup"], cwd=sample, capture_output=True)
        (sample / "index.html").write_text("<html><body>Hello World</body></html>")
        subprocess.run(["git", "add", "."], cwd=sample, capture_output=True)
        subprocess.run(["git", "commit", "-m", "fix: update greeting"], cwd=sample, capture_output=True)

    backend = FIXTURES_DIR / "backend_repo"
    if not (backend / ".git").exists():
        subprocess.run(["git", "init"], cwd=backend, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=backend, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=backend, capture_output=True)
        (backend / "pyproject.toml").write_text('[project]\nname = "backend-api"\ndependencies = ["fastapi", "uvicorn"]')
        (backend / "main.py").write_text("from fastapi import FastAPI\napp = FastAPI()\n")
        subprocess.run(["git", "add", "."], cwd=backend, capture_output=True)
        subprocess.run(["git", "commit", "-m", "feat: fastapi backend"], cwd=backend, capture_output=True)
```

### Verification
```bash
cd ~/projects/auto-portfolio
python -c "
from pathlib import Path
dirs = ['cmd', 'core', 'data', 'deploy', 'templates', 'tests/unit', 'tests/integration',
        'site/src/components', 'site/src/data', 'site/public/previews']
for d in dirs:
    assert Path(d).exists(), f'Missing: {d}'
print('OK')
"
```
**Done when:** prints `OK`.

---

## TASK-003: Create config.toml and config parser

**Depends on:** TASK-002
**Files created:** `config.toml`, `core/config.py`

### Steps

Create `config.toml`:
```toml
[profile]
name = "Your Name"
title = "Software Engineer"
bio = "I build things."
# avatar = "~/Pictures/avatar.jpg"
# social.github = "https://github.com/yourusername"
# social.linkedin = "https://linkedin.com/in/yourusername"

[scan]
paths = ["~/projects"]
exclude = ["**/.git", "**/node_modules", "**/dist", "**/.venv", "**/target"]
min_commits = 1
max_age_days = 730

[site]
theme = "dark"
accent_color = "#6366f1"
language = "en"

[deploy]
target = "github-pages"
# domain = "yourdomain.com"

[cache]
enabled = true
dir = "~/.cache/auto-portfolio"
```

Create `core/config.py`:
```python
from pathlib import Path
from dataclasses import dataclass, field
import tomllib


@dataclass
class ProfileConfig:
    name: str = "Developer"
    title: str = "Software Engineer"
    bio: str = ""
    avatar: str | None = None
    social: dict = field(default_factory=dict)


@dataclass
class ScanConfig:
    paths: list[str] = field(default_factory=lambda: ["~/projects"])
    exclude: list[str] = field(default_factory=lambda: [
        "**/.git", "**/node_modules", "**/dist", "**/.venv"
    ])
    min_commits: int = 1
    max_age_days: int = 730


@dataclass
class SiteConfig:
    theme: str = "dark"
    accent_color: str = "#6366f1"
    language: str = "en"


@dataclass
class CacheConfig:
    enabled: bool = True
    dir: str = "~/.cache/auto-portfolio"


@dataclass
class AppConfig:
    profile: ProfileConfig = field(default_factory=ProfileConfig)
    scan: ScanConfig = field(default_factory=ScanConfig)
    site: SiteConfig = field(default_factory=SiteConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)

    @classmethod
    def from_toml(cls, path: Path = Path("config.toml")) -> "AppConfig":
        if not path.exists():
            return cls()
        with open(path, "rb") as f:
            data = tomllib.load(f)
        cfg = cls()
        if "profile" in data:
            for k, v in data["profile"].items():
                if hasattr(cfg.profile, k):
                    setattr(cfg.profile, k, v)
        if "scan" in data:
            for k, v in data["scan"].items():
                if hasattr(cfg.scan, k):
                    setattr(cfg.scan, k, v)
        if "site" in data:
            for k, v in data["site"].items():
                if hasattr(cfg.site, k):
                    setattr(cfg.site, k, v)
        return cfg
```

### Verification
```bash
cd ~/projects/auto-portfolio
source .venv/bin/activate
python -c "
from core.config import AppConfig
cfg = AppConfig.from_toml()
assert cfg.scan.min_commits == 1
assert cfg.site.theme == 'dark'
print('OK')
"
```
**Done when:** prints `OK`.

---

## TASK-004: Implement the Pydantic data models

**Depends on:** TASK-002
**Files created:** `data/models.py`

### Steps

Create `data/models.py`:
```python
from pydantic import BaseModel, Field, computed_field
from datetime import datetime
from pathlib import Path
import re


def slugify(name: str) -> str:
    """Convert a name to a URL-safe slug."""
    slug = name.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


class ProjectRecord(BaseModel):
    id: str
    path: str
    name: str
    slug: str
    description: str | None = None
    long_description: str | None = None
    remote_url: str | None = None
    created_at: datetime | None = None
    last_active: datetime | None = None
    total_commits: int = 0
    contributors: list[str] = Field(default_factory=list)
    primary_language: str | None = None
    languages: dict[str, float] = Field(default_factory=dict)
    stack: list[str] = Field(default_factory=list)
    has_tests: bool = False
    has_ci: bool = False
    has_docs: bool = False
    quality_score: float = 0.0
    tags: list[str] = Field(default_factory=list)
    screenshot_path: str | None = None
    size_bytes: int = 0
    preview_text: str | None = None

    @computed_field
    @property
    def last_active_display(self) -> str:
        if not self.last_active:
            return "Unknown"
        delta = datetime.utcnow() - self.last_active.replace(tzinfo=None)
        if delta.days == 0:
            return "Today"
        if delta.days == 1:
            return "Yesterday"
        if delta.days < 30:
            return f"{delta.days} days ago"
        if delta.days < 365:
            return f"{delta.days // 30} months ago"
        return f"{delta.days // 365} years ago"

    def to_json_dict(self) -> dict:
        """Serialize for site/src/data/projects.json"""
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "long_description": self.long_description,
            "path": self.path,
            "remote_url": self.remote_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_active": self.last_active.isoformat() if self.last_active else None,
            "last_active_display": self.last_active_display,
            "total_commits": self.total_commits,
            "contributors": self.contributors,
            "primary_language": self.primary_language,
            "languages": self.languages,
            "stack": self.stack,
            "has_tests": self.has_tests,
            "has_ci": self.has_ci,
            "has_docs": self.has_docs,
            "quality_score": round(self.quality_score, 2),
            "tags": self.tags,
            "screenshot": self.screenshot_path,
            "preview_text": self.preview_text,
            "size_bytes": self.size_bytes,
        }
```

### Verification
```bash
cd ~/projects/auto-portfolio
source .venv/bin/activate
python -c "
from data.models import ProjectRecord, slugify
from datetime import datetime

assert slugify('My Cool Project!') == 'my-cool-project'
assert slugify('React + TypeScript App') == 'react-typescript-app'

p = ProjectRecord(
    id='abc123', path='/tmp/test', name='Test App',
    slug='test-app', last_active=datetime(2025, 1, 1),
    total_commits=42, primary_language='TypeScript',
)
d = p.to_json_dict()
assert d['slug'] == 'test-app'
assert d['total_commits'] == 42
print('OK')
"
```
**Done when:** prints `OK`.

---

## TASK-005: Implement tech_detector.py (manifest parser)

**Depends on:** TASK-004
**Files created:** `core/tech_detector.py`

### Steps

Create `core/tech_detector.py`:
```python
import json
from pathlib import Path

# Map from package name substring → framework label
NPM_FRAMEWORK_MAP = {
    "react": "React",
    "vue": "Vue.js",
    "svelte": "Svelte",
    "next": "Next.js",
    "nuxt": "Nuxt",
    "angular": "Angular",
    "astro": "Astro",
    "solid-js": "SolidJS",
    "remix": "Remix",
    "express": "Express",
    "fastify": "Fastify",
    "hono": "Hono",
    "vite": "Vite",
    "webpack": "Webpack",
    "tailwindcss": "Tailwind CSS",
    "prisma": "Prisma",
    "drizzle-orm": "Drizzle",
    "trpc": "tRPC",
    "graphql": "GraphQL",
    "typescript": "TypeScript",
    "jest": "Jest",
    "vitest": "Vitest",
    "playwright": "Playwright",
}

PYTHON_FRAMEWORK_MAP = {
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "starlette": "Starlette",
    "sqlalchemy": "SQLAlchemy",
    "pydantic": "Pydantic",
    "typer": "Typer",
    "click": "Click",
    "textual": "Textual",
    "pytest": "Pytest",
}

LANG_EXT_MAP = {
    ".py": "Python", ".rs": "Rust", ".go": "Go",
    ".ts": "TypeScript", ".tsx": "TypeScript",
    ".js": "JavaScript", ".jsx": "JavaScript",
    ".rb": "Ruby", ".java": "Java",
    ".kt": "Kotlin", ".swift": "Swift",
    ".c": "C", ".cpp": "C++",
    ".cs": "C#", ".ex": "Elixir",
}

TEST_INDICATORS = {
    "pytest", "jest", "vitest", "mocha", "jasmine", "rspec",
    "go test", "cargo test", "minitest"
}

CI_FILES = {
    ".github/workflows", ".gitlab-ci.yml", ".travis.yml",
    "Jenkinsfile", "circle.ci", ".circleci",
}


def detect_stack(repo_path: Path) -> list[str]:
    """Detect tech stack from manifest files."""
    stack: list[str] = []

    def _add(item: str) -> None:
        if item not in stack:
            stack.append(item)

    # package.json
    pkg = repo_path / "package.json"
    if pkg.exists():
        try:
            data = json.loads(pkg.read_text(errors="replace"))
            all_deps = list(data.get("dependencies", {}).keys()) + \
                       list(data.get("devDependencies", {}).keys())
            _add("JavaScript")
            if any("typescript" in d for d in all_deps):
                _add("TypeScript")
            for dep in all_deps:
                for key, label in NPM_FRAMEWORK_MAP.items():
                    if key in dep.lower():
                        _add(label)
        except (json.JSONDecodeError, OSError):
            pass

    # pyproject.toml
    pyproject = repo_path / "pyproject.toml"
    if pyproject.exists():
        content = pyproject.read_text(errors="replace").lower()
        _add("Python")
        for key, label in PYTHON_FRAMEWORK_MAP.items():
            if key in content:
                _add(label)

    # Cargo.toml
    if (repo_path / "Cargo.toml").exists():
        _add("Rust")

    # go.mod
    if (repo_path / "go.mod").exists():
        _add("Go")

    # Gemfile
    if (repo_path / "Gemfile").exists():
        _add("Ruby")

    return stack


def detect_languages(repo_path: Path) -> dict[str, float]:
    """Count source files by extension and return percentage distribution."""
    counts: dict[str, int] = {}
    total = 0
    for f in repo_path.rglob("*"):
        if f.is_file() and ".git" not in f.parts:
            # Skip binary-ish and irrelevant files
            if f.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".svg",
                                      ".ico", ".woff", ".ttf", ".lock", ".sum"}:
                continue
            lang = LANG_EXT_MAP.get(f.suffix.lower())
            if lang:
                counts[lang] = counts.get(lang, 0) + 1
                total += 1
    if total == 0:
        return {}
    return {
        lang: round(count / total * 100, 1)
        for lang, count in sorted(counts.items(), key=lambda x: -x[1])
    }


def detect_quality_signals(repo_path: Path) -> tuple[bool, bool, bool, float]:
    """
    Returns (has_tests, has_ci, has_docs, quality_score).
    quality_score is 0.0-1.0 heuristic.
    """
    has_tests = any((repo_path / d).exists() for d in ["tests", "test", "spec", "__tests__"])
    if not has_tests:
        # Check package.json for test scripts
        pkg = repo_path / "package.json"
        if pkg.exists():
            try:
                data = json.loads(pkg.read_text(errors="replace"))
                has_tests = "test" in data.get("scripts", {})
            except (json.JSONDecodeError, OSError):
                pass

    has_ci = any((repo_path / ci).exists() for ci in CI_FILES)

    has_docs = (repo_path / "README.md").exists() or (repo_path / "docs").exists()

    score = 0.0
    if has_tests:
        score += 0.35
    if has_ci:
        score += 0.25
    if has_docs:
        score += 0.25
    if (repo_path / "package.json").exists() or (repo_path / "pyproject.toml").exists():
        score += 0.15

    return has_tests, has_ci, has_docs, round(score, 2)
```

### Verification
```bash
cd ~/projects/auto-portfolio
source .venv/bin/activate
python -c "
from core.tech_detector import detect_stack, detect_languages, detect_quality_signals
from pathlib import Path

# Test on sample_repo (has package.json with react)
sample = Path('tests/fixtures/sample_repo')
stack = detect_stack(sample)
print(f'Stack: {stack}')
assert 'JavaScript' in stack or 'TypeScript' in stack or 'React' in stack
assert 'Python' not in stack

langs = detect_languages(sample)
print(f'Languages: {langs}')

# Test on backend_repo (has pyproject.toml with fastapi)
backend = Path('tests/fixtures/backend_repo')
stack_b = detect_stack(backend)
assert 'Python' in stack_b
assert 'FastAPI' in stack_b

has_tests, has_ci, has_docs, score = detect_quality_signals(sample)
assert 0.0 <= score <= 1.0
print('OK')
"
```
**Done when:** prints `Stack: [...]`, `Languages: {...}`, and `OK`.

---

## TASK-006: Implement repo_scanner.py

**Depends on:** TASK-004, TASK-005
**Files created:** `core/repo_scanner.py`

### Steps

Create `core/repo_scanner.py`:
```python
import hashlib
import json
import subprocess
from pathlib import Path
from datetime import datetime

from data.models import ProjectRecord, slugify
from core.tech_detector import detect_stack, detect_languages, detect_quality_signals


CACHE_DIR = Path.home() / ".cache" / "auto-portfolio"


def _repo_id(path: Path) -> str:
    return hashlib.sha256(str(path.resolve()).encode()).hexdigest()[:16]


def _run_git(args: list[str], cwd: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(cwd)] + args,
            capture_output=True, text=True, timeout=20
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
                    p for p in paragraphs
                    if not p.startswith("#") and not p.startswith("!") and len(p) > 20
                ]
                if text_paras:
                    long_desc = text_paras[0][:500]
                    short_desc = long_desc[:280]
                    # Cut to sentence boundary
                    for punct in [". ", "! ", "? "]:
                        idx = short_desc.find(punct)
                        if 30 < idx < 200:
                            short_desc = short_desc[:idx + 1]
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
            line.split("\t", 1)[1].strip()
            for line in contributors_raw.splitlines()
            if "\t" in line
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
            f.stat().st_size for f in path.rglob("*")
            if f.is_file() and ".git" not in f.parts
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


def scan_root(root: Path, min_commits: int = 1, max_depth: int = 5,
              exclude: list[str] | None = None) -> list[ProjectRecord]:
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
```

### Verification
```bash
cd ~/projects/auto-portfolio
source .venv/bin/activate
python -m pytest tests/conftest.py -v --collect-only 2>/dev/null || true  # init fixtures

python -c "
from core.repo_scanner import scan_repo, scan_root
from pathlib import Path

sample = scan_repo(Path('tests/fixtures/sample_repo'), use_cache=False)
assert sample is not None, 'scan_repo returned None'
assert sample.name == 'sample_repo'
assert sample.total_commits >= 2
assert sample.has_docs == True  # has README.md
print(f'Repo: {sample.name}, commits: {sample.total_commits}, stack: {sample.stack}')

backend = scan_repo(Path('tests/fixtures/backend_repo'), use_cache=False)
assert backend is not None
assert 'Python' in backend.stack

repos = scan_root(Path('tests/fixtures'))
assert len(repos) >= 2
print(f'Found {len(repos)} repos. OK')
"
```
**Done when:** prints repo info and `Found N repos. OK`.

---

## TASK-007: Implement description_gen.py

**Depends on:** TASK-004
**Files created:** `core/description_gen.py`

### Steps

Create `core/description_gen.py`:
```python
from pathlib import Path
import subprocess


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
            ["git", "-C", str(repo_path), "log", "--no-merges",
             f"--max-count={n}", "--format=%s"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return []
```

### Verification
```bash
cd ~/projects/auto-portfolio
source .venv/bin/activate
python -c "
from core.description_gen import generate_description, extract_commit_highlights
from pathlib import Path

desc = generate_description(
    Path('tests/fixtures/sample_repo'),
    existing_description='A sample web application for testing.',
    stack=['React', 'TypeScript'],
    total_commits=10,
    name='sample-app',
)
assert desc == 'A sample web application for testing.'

desc2 = generate_description(
    Path('tests/fixtures/sample_repo'),
    existing_description=None,
    stack=['Python', 'FastAPI'],
    total_commits=50,
    name='api',
)
assert 'Python' in desc2 or 'FastAPI' in desc2

commits = extract_commit_highlights(Path('tests/fixtures/sample_repo'))
assert len(commits) >= 1
print('OK')
"
```
**Done when:** prints `OK`.

---

## TASK-008: Write unit tests for core modules

**Depends on:** TASK-005, TASK-006, TASK-007
**Files created:** `tests/unit/test_scanner.py`, `tests/unit/test_tech_detector.py`, `tests/unit/test_models.py`

### Steps

Create `tests/unit/test_models.py`:
```python
import pytest
from datetime import datetime
from data.models import ProjectRecord, slugify


def test_slugify_basic():
    assert slugify("My Cool Project") == "my-cool-project"
    assert slugify("React + TypeScript App!") == "react-typescript-app"
    assert slugify("project--name") == "project-name"


def test_project_record_to_json_dict():
    p = ProjectRecord(
        id="abc", path="/tmp", name="test", slug="test",
        last_active=datetime(2024, 6, 1), total_commits=50,
    )
    d = p.to_json_dict()
    assert d["id"] == "abc"
    assert d["total_commits"] == 50
    assert d["quality_score"] == 0.0


def test_last_active_display_recent():
    p = ProjectRecord(id="x", path="/t", name="t", slug="t",
                      last_active=datetime.utcnow())
    assert p.last_active_display == "Today"


def test_last_active_display_old():
    from datetime import timedelta
    p = ProjectRecord(id="x", path="/t", name="t", slug="t",
                      last_active=datetime.utcnow() - timedelta(days=400))
    assert "year" in p.last_active_display
```

Create `tests/unit/test_tech_detector.py`:
```python
import pytest
from pathlib import Path
from tests.conftest import FIXTURES_DIR
from core.tech_detector import detect_stack, detect_languages, detect_quality_signals


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
```

Create `tests/unit/test_scanner.py`:
```python
import pytest
from pathlib import Path
from tests.conftest import FIXTURES_DIR
from core.repo_scanner import scan_repo, scan_root, _repo_id


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
```

### Verification
```bash
cd ~/projects/auto-portfolio
source .venv/bin/activate
python -m pytest tests/unit/ -v
```
**Done when:** all unit tests pass.

---

## TASK-009: Initialize the Astro site scaffold

**Depends on:** TASK-002
**Files created:** `site/package.json`, `site/astro.config.mjs`, `site/tailwind.config.mjs`, `site/tsconfig.json`

### Steps

```bash
cd ~/projects/auto-portfolio/site
# Check if node is available
node --version || (echo "ERROR: Node.js is required. Install from https://nodejs.org" && exit 1)
npm --version
```

Create `site/package.json`:
```json
{
  "name": "auto-portfolio-site",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "astro dev",
    "build": "astro build",
    "preview": "astro preview"
  },
  "dependencies": {
    "astro": "^4.6.0",
    "@astrojs/tailwind": "^5.1.0",
    "tailwindcss": "^3.4.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0"
  }
}
```

```bash
cd ~/projects/auto-portfolio/site
npm install
```

Create `site/astro.config.mjs`:
```javascript
import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

export default defineConfig({
  integrations: [tailwind()],
  output: 'static',
  build: {
    assets: 'assets',
  },
});
```

Create `site/tailwind.config.mjs`:
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eef2ff',
          500: '#6366f1',
          900: '#1e1b4b',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
};
```

Create `site/tsconfig.json`:
```json
{
  "extends": "astro/tsconfigs/strict",
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@data/*": ["src/data/*"],
      "@components/*": ["src/components/*"]
    }
  }
}
```

Create `site/src/styles/global.css`:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-gray-950 text-gray-100;
  }
}
```

### Verification
```bash
cd ~/projects/auto-portfolio/site
node_modules/.bin/astro --version
echo "Astro installed. OK"
```
**Done when:** prints Astro version and `OK`.

---

## TASK-010: Create Astro layout and base pages

**Depends on:** TASK-009
**Files created:** `site/src/layouts/BaseLayout.astro`, `site/src/pages/index.astro`, `site/src/pages/projects/[slug].astro`

### Steps

Create `site/src/layouts/BaseLayout.astro`:
```astro
---
interface Props {
  title: string;
  description?: string;
}

const { title, description = "Auto-generated developer portfolio" } = Astro.props;
---
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="description" content={description} />
  <title>{title}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" />
  <link rel="stylesheet" href="/styles/global.css" />
</head>
<body class="min-h-screen bg-gray-950 text-gray-100 font-sans">
  <nav class="border-b border-gray-800 bg-gray-950/80 backdrop-blur sticky top-0 z-50">
    <div class="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
      <a href="/" class="font-bold text-lg text-indigo-400 hover:text-indigo-300 transition-colors">Portfolio</a>
      <div class="flex gap-6 text-sm text-gray-400">
        <a href="/" class="hover:text-white transition-colors">Home</a>
        <a href="/projects" class="hover:text-white transition-colors">Projects</a>
      </div>
    </div>
  </nav>
  <main class="max-w-6xl mx-auto px-4 py-8">
    <slot />
  </main>
  <footer class="border-t border-gray-800 mt-16 py-8 text-center text-gray-500 text-sm">
    Generated by auto-portfolio
  </footer>
</body>
</html>
```

Create `site/src/pages/index.astro`:
```astro
---
import BaseLayout from '../layouts/BaseLayout.astro';
import ProjectCard from '../components/ProjectCard.astro';

// Import project data (generated by auto-portfolio generate)
let projects = [];
let profile = { name: "Developer", title: "Software Engineer", bio: "" };

try {
  const data = await import('../data/projects.json');
  projects = data.default.projects || [];
} catch (e) {
  // No data yet — show placeholder
}

try {
  const data = await import('../data/profile.json');
  profile = data.default;
} catch (e) {}

const topProjects = [...projects]
  .sort((a, b) => (b.quality_score || 0) - (a.quality_score || 0))
  .slice(0, 6);

const totalCommits = projects.reduce((s, p) => s + (p.total_commits || 0), 0);
const uniqueLangs = new Set(projects.flatMap(p => Object.keys(p.languages || {}))).size;
---
<BaseLayout title={`${profile.name} — Portfolio`}>
  <!-- Hero -->
  <section class="py-16 text-center">
    <h1 class="text-4xl font-bold mb-3 text-white">
      Hi, I'm <span class="text-indigo-400">{profile.name}</span>
    </h1>
    <p class="text-xl text-gray-400 mb-2">{profile.title}</p>
    {profile.bio && <p class="text-gray-500 max-w-xl mx-auto">{profile.bio}</p>}
  </section>

  <!-- Stats bar -->
  <section class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
    {[
      { label: 'Projects', value: projects.length },
      { label: 'Total Commits', value: totalCommits.toLocaleString() },
      { label: 'Languages', value: uniqueLangs },
    ].map(stat => (
      <div class="bg-gray-900 border border-gray-800 rounded-xl p-4 text-center">
        <div class="text-2xl font-bold text-indigo-400">{stat.value}</div>
        <div class="text-xs text-gray-500 mt-1">{stat.label}</div>
      </div>
    ))}
  </section>

  <!-- Featured Projects -->
  {topProjects.length > 0 ? (
    <section>
      <h2 class="text-2xl font-semibold mb-6 text-white">Featured Projects</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {topProjects.map(project => (
          <ProjectCard project={project} />
        ))}
      </div>
      {projects.length > 6 && (
        <div class="text-center mt-8">
          <a href="/projects" class="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors inline-block">
            View all {projects.length} projects →
          </a>
        </div>
      )}
    </section>
  ) : (
    <div class="text-center py-20 text-gray-500">
      <p class="text-lg">No projects yet.</p>
      <p class="text-sm mt-2">Run <code class="bg-gray-800 px-2 py-1 rounded">auto-portfolio generate</code> to populate your portfolio.</p>
    </div>
  )}
</BaseLayout>
```

Create `site/src/components/ProjectCard.astro`:
```astro
---
interface Project {
  slug: string;
  name: string;
  description?: string;
  primary_language?: string;
  stack?: string[];
  total_commits?: number;
  last_active_display?: string;
  quality_score?: number;
  has_tests?: boolean;
  has_ci?: boolean;
}

interface Props {
  project: Project;
}

const { project } = Astro.props;

const LANG_COLORS: Record<string, string> = {
  TypeScript: 'bg-blue-500', JavaScript: 'bg-yellow-400', Python: 'bg-green-500',
  Rust: 'bg-orange-500', Go: 'bg-cyan-400', Ruby: 'bg-red-500', Java: 'bg-red-600',
};
const langColor = LANG_COLORS[project.primary_language || ''] || 'bg-gray-500';
---
<a href={`/projects/${project.slug}`}
   class="block bg-gray-900 border border-gray-800 rounded-xl p-5 hover:border-indigo-500/50 transition-all hover:bg-gray-900/80 group">
  <div class="flex items-start justify-between mb-3">
    <h3 class="font-semibold text-white group-hover:text-indigo-300 transition-colors truncate mr-2">
      {project.name}
    </h3>
    {project.primary_language && (
      <span class={`text-xs px-2 py-0.5 rounded-full text-gray-900 font-medium shrink-0 ${langColor}`}>
        {project.primary_language}
      </span>
    )}
  </div>

  {project.description && (
    <p class="text-sm text-gray-400 mb-4 line-clamp-2">{project.description}</p>
  )}

  {project.stack && project.stack.length > 0 && (
    <div class="flex flex-wrap gap-1.5 mb-4">
      {project.stack.slice(0, 4).map(tech => (
        <span class="text-xs bg-gray-800 text-gray-300 px-2 py-0.5 rounded">
          {tech}
        </span>
      ))}
    </div>
  )}

  <div class="flex items-center justify-between text-xs text-gray-500">
    <span>{project.total_commits || 0} commits</span>
    <span>{project.last_active_display || ''}</span>
  </div>
</a>
```

Create `site/src/pages/projects/index.astro`:
```astro
---
import BaseLayout from '../../layouts/BaseLayout.astro';
import ProjectCard from '../../components/ProjectCard.astro';

let projects = [];
try {
  const data = await import('../../data/projects.json');
  projects = data.default.projects || [];
} catch (e) {}

const sorted = [...projects].sort((a, b) =>
  new Date(b.last_active || 0).getTime() - new Date(a.last_active || 0).getTime()
);
---
<BaseLayout title="All Projects">
  <h1 class="text-3xl font-bold mb-8">All Projects ({projects.length})</h1>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    {sorted.map(project => <ProjectCard project={project} />)}
  </div>
</BaseLayout>
```

Create `site/src/pages/projects/[slug].astro`:
```astro
---
import BaseLayout from '../../layouts/BaseLayout.astro';

export async function getStaticPaths() {
  let projects = [];
  try {
    const data = await import('../../data/projects.json');
    projects = data.default.projects || [];
  } catch (e) {}
  return projects.map(p => ({ params: { slug: p.slug }, props: { project: p } }));
}

const { project } = Astro.props;
---
<BaseLayout title={project.name} description={project.description}>
  <a href="/projects" class="text-indigo-400 hover:text-indigo-300 text-sm mb-6 inline-block">← All Projects</a>

  <div class="mb-8">
    <h1 class="text-3xl font-bold text-white mb-2">{project.name}</h1>
    {project.description && <p class="text-lg text-gray-400">{project.description}</p>}
  </div>

  <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
    {[
      { label: 'Commits', value: project.total_commits },
      { label: 'Language', value: project.primary_language || '—' },
      { label: 'Last Active', value: project.last_active_display },
      { label: 'Quality', value: `${Math.round((project.quality_score || 0) * 100)}%` },
    ].map(s => (
      <div class="bg-gray-900 rounded-lg p-4 text-center border border-gray-800">
        <div class="text-xl font-bold text-indigo-400">{s.value}</div>
        <div class="text-xs text-gray-500">{s.label}</div>
      </div>
    ))}
  </div>

  {project.stack && project.stack.length > 0 && (
    <div class="mb-6">
      <h2 class="text-lg font-semibold mb-3">Tech Stack</h2>
      <div class="flex flex-wrap gap-2">
        {project.stack.map(tech => (
          <span class="bg-gray-800 text-gray-200 px-3 py-1 rounded-lg text-sm">{tech}</span>
        ))}
      </div>
    </div>
  )}

  {project.long_description && (
    <div class="prose prose-invert max-w-none">
      <h2>About</h2>
      <p>{project.long_description}</p>
    </div>
  )}

  {project.remote_url && (
    <div class="mt-8">
      <a href={project.remote_url} target="_blank" rel="noopener"
         class="inline-flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm transition-colors">
        View Repository →
      </a>
    </div>
  )}
</BaseLayout>
```

### Verification
```bash
cd ~/projects/auto-portfolio/site
ls src/layouts/ src/pages/ src/components/
echo "Astro files created. OK"
```
**Done when:** prints `OK` after listing layout, pages, components directories.

---

## TASK-011: Create data seeding script and seed test data

**Depends on:** TASK-010
**Files created:** `site/src/data/projects.json`, `site/src/data/profile.json`

### Steps

Create a seed projects.json so Astro can build without running the full scanner:

```bash
mkdir -p ~/projects/auto-portfolio/site/src/data
```

Create `site/src/data/projects.json`:
```json
{
  "generated_at": "2024-01-01T00:00:00Z",
  "projects": [
    {
      "id": "sample001",
      "name": "sample-app",
      "slug": "sample-app",
      "description": "A sample web application for testing the portfolio generator.",
      "long_description": "This is a sample web application that demonstrates the auto-portfolio data format. It includes React, TypeScript, and Tailwind CSS.",
      "path": "/tmp/sample-app",
      "remote_url": null,
      "created_at": "2024-01-01T00:00:00Z",
      "last_active": "2024-06-15T12:00:00Z",
      "last_active_display": "10 months ago",
      "total_commits": 47,
      "contributors": ["Developer"],
      "primary_language": "TypeScript",
      "languages": {"TypeScript": 65.3, "HTML": 20.1, "CSS": 14.6},
      "stack": ["TypeScript", "React", "Vite", "Tailwind CSS"],
      "has_tests": true,
      "has_ci": true,
      "has_docs": true,
      "quality_score": 0.85,
      "tags": ["web", "frontend"],
      "screenshot": null,
      "preview_text": "A React + TypeScript web application",
      "size_bytes": 2456789
    }
  ]
}
```

Create `site/src/data/profile.json`:
```json
{
  "name": "Joshua",
  "title": "Full-Stack Developer",
  "bio": "I build fast things and make slow things fast.",
  "social": {}
}
```

### Verification
```bash
cd ~/projects/auto-portfolio/site
node_modules/.bin/astro build 2>&1 | tail -10
echo "Exit code: $?"
```
**Done when:** `astro build` succeeds (exit code 0) and creates `site/dist/`.

---

## TASK-012: Implement the site generator (core/site_generator.py)

**Depends on:** TASK-006, TASK-011
**Files created:** `core/site_generator.py`

### Steps

Create `core/site_generator.py`:
```python
import json
from pathlib import Path
from datetime import datetime

from data.models import ProjectRecord
from core.config import ProfileConfig


def write_projects_json(records: list[ProjectRecord], site_data_dir: Path) -> Path:
    """Write site/src/data/projects.json from scanner output."""
    site_data_dir.mkdir(parents=True, exist_ok=True)
    output = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "projects": [r.to_json_dict() for r in records],
    }
    out_path = site_data_dir / "projects.json"
    out_path.write_text(json.dumps(output, indent=2, default=str))
    return out_path


def write_profile_json(profile: ProfileConfig, site_data_dir: Path) -> Path:
    """Write site/src/data/profile.json from config."""
    site_data_dir.mkdir(parents=True, exist_ok=True)
    out = {
        "name": profile.name,
        "title": profile.title,
        "bio": profile.bio,
        "avatar": profile.avatar,
        "social": profile.social,
    }
    out_path = site_data_dir / "profile.json"
    out_path.write_text(json.dumps(out, indent=2))
    return out_path


def build_astro_site(site_dir: Path) -> bool:
    """Run `npm run build` in the Astro site directory."""
    import subprocess
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=site_dir,
        timeout=120,
    )
    return result.returncode == 0
```

### Verification
```bash
cd ~/projects/auto-portfolio
source .venv/bin/activate
python -c "
from core.site_generator import write_projects_json, write_profile_json
from data.models import ProjectRecord
from core.config import ProfileConfig
from datetime import datetime
from pathlib import Path
import tempfile, json

with tempfile.TemporaryDirectory() as tmp:
    data_dir = Path(tmp)
    records = [ProjectRecord(
        id='t1', path='/tmp', name='test', slug='test',
        last_active=datetime.utcnow(), total_commits=5,
    )]
    out = write_projects_json(records, data_dir)
    assert out.exists()
    data = json.loads(out.read_text())
    assert len(data['projects']) == 1

    profile = ProfileConfig(name='Josh', title='Dev', bio='Hi')
    pout = write_profile_json(profile, data_dir)
    assert pout.exists()
    pdata = json.loads(pout.read_text())
    assert pdata['name'] == 'Josh'
print('OK')
"
```
**Done when:** prints `OK`.

---

## TASK-013: Implement the CLI entrypoint (cmd/auto_portfolio.py)

**Depends on:** TASK-006, TASK-012
**Files created:** `cmd/auto_portfolio.py`

### Steps

Create `cmd/auto_portfolio.py`:
```python
import typer
from pathlib import Path
from typing import Optional

app = typer.Typer(name="auto-portfolio", help="Zero-input portfolio generator from git history.")


@app.command()
def setup():
    """Interactive setup: generate config.toml and prepare the site."""
    from rich.console import Console
    from rich.prompt import Prompt
    console = Console()
    console.print("[bold]Auto-Portfolio Setup[/bold]\n")

    dest = Path("config.toml")
    if dest.exists():
        console.print("[yellow]config.toml already exists. Editing it directly instead.[/yellow]")
    else:
        name = Prompt.ask("Your name", default="Developer")
        title = Prompt.ask("Your title", default="Software Engineer")
        bio = Prompt.ask("Short bio", default="I build things.")
        
        config_content = f'''[profile]
name = "{name}"
title = "{title}"
bio = "{bio}"

[scan]
paths = ["~/projects"]
exclude = ["**/.git", "**/node_modules", "**/dist", "**/.venv"]
min_commits = 1
max_age_days = 730

[site]
theme = "dark"
accent_color = "#6366f1"

[deploy]
target = "github-pages"
'''
        dest.write_text(config_content)
        console.print(f"[green]Created config.toml[/green]")
    
    console.print("\nNext steps:")
    console.print("  auto-portfolio generate   — scan repos and build site")
    console.print("  auto-portfolio preview    — preview site locally")


@app.command()
def generate(
    config: str = typer.Option("config.toml", "--config", "-c"),
    site_dir: str = typer.Option("site", "--site-dir"),
    no_build: bool = typer.Option(False, "--no-build", help="Skip Astro build"),
):
    """Scan all repos and generate the portfolio site."""
    from core.config import AppConfig
    from core.repo_scanner import scan_root
    from core.site_generator import write_projects_json, write_profile_json, build_astro_site
    from rich.console import Console
    from rich.progress import track

    console = Console()
    cfg = AppConfig.from_toml(Path(config))

    console.print(f"[bold]Scanning {len(cfg.scan.paths)} path(s)...[/bold]")
    all_records = []
    for raw_path in cfg.scan.paths:
        root = Path(raw_path).expanduser()
        console.print(f"  Scanning {root}...")
        records = scan_root(
            root,
            min_commits=cfg.scan.min_commits,
        )
        all_records.extend(records)
        console.print(f"  Found {len(records)} projects")

    console.print(f"\n[green]Total: {len(all_records)} projects[/green]")

    # Write data files
    site_data_dir = Path(site_dir) / "src" / "data"
    write_projects_json(all_records, site_data_dir)
    write_profile_json(cfg.profile, site_data_dir)
    console.print(f"[green]Data written to {site_data_dir}[/green]")

    # Build site
    if not no_build:
        site_path = Path(site_dir)
        if (site_path / "package.json").exists():
            console.print("\n[bold]Building Astro site...[/bold]")
            ok = build_astro_site(site_path)
            if ok:
                console.print(f"[green]Site built to {site_path / 'dist'}[/green]")
            else:
                console.print("[red]Astro build failed. Check site/package.json.[/red]")
        else:
            console.print("[yellow]No site/package.json found. Run npm install in site/ directory.[/yellow]")
    else:
        console.print("[dim]Skipping build (--no-build)[/dim]")

    console.print("\n[bold green]Done![/bold green]")
    console.print("  Preview: auto-portfolio preview")


@app.command()
def preview(
    site_dir: str = typer.Option("site", "--site-dir"),
    port: int = typer.Option(4321, "--port"),
):
    """Preview the generated site locally."""
    import subprocess
    from rich.console import Console
    console = Console()
    site_path = Path(site_dir)
    if not (site_path / "dist").exists():
        console.print("[red]No dist/ found. Run: auto-portfolio generate[/red]")
        raise typer.Exit(1)
    console.print(f"[bold]Previewing at http://localhost:{port}[/bold]")
    subprocess.run(["npm", "run", "preview", "--", f"--port={port}"], cwd=site_path)


@app.command()
def health(
    config: str = typer.Option("config.toml", "--config"),
    site_dir: str = typer.Option("site", "--site-dir"),
):
    """Show portfolio status and stats."""
    import json
    from rich.console import Console
    console = Console()

    data_file = Path(site_dir) / "src" / "data" / "projects.json"
    if not data_file.exists():
        console.print("[yellow]No data generated yet. Run: auto-portfolio generate[/yellow]")
        return

    data = json.loads(data_file.read_text())
    projects = data.get("projects", [])
    console.print(f"\n[bold]Auto-Portfolio Health[/bold]")
    console.print(f"  Projects: {len(projects)}")
    if projects:
        langs = {}
        for p in projects:
            for lang, pct in (p.get("languages") or {}).items():
                langs[lang] = langs.get(lang, 0) + pct
        top_langs = sorted(langs.items(), key=lambda x: -x[1])[:5]
        console.print(f"  Top languages: {', '.join(l[0] for l in top_langs)}")
    console.print(f"  Generated: {data.get('generated_at', 'unknown')[:10]}")
    console.print(f"  Site built: {(Path(site_dir) / 'dist').exists()}")


if __name__ == "__main__":
    app()
```

### Verification
```bash
cd ~/projects/auto-portfolio
source .venv/bin/activate
python cmd/auto_portfolio.py --help
python cmd/auto_portfolio.py health
```
**Done when:** `--help` prints usage. `health` runs without error.

---

## TASK-014: Write integration test for generate command

**Depends on:** TASK-013
**Files created:** `tests/integration/test_generate_site.py`

### Steps

Create `tests/integration/test_generate_site.py`:
```python
import pytest
import json
from pathlib import Path
from tests.conftest import FIXTURES_DIR
from core.repo_scanner import scan_root
from core.site_generator import write_projects_json, write_profile_json
from core.config import ProfileConfig


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
```

### Verification
```bash
cd ~/projects/auto-portfolio
source .venv/bin/activate
python -m pytest tests/integration/ -v
```
**Done when:** all integration tests pass.

---

## TASK-015: Run full pipeline, linter, CI, and README

**Depends on:** TASK-014
**Files created:** `.github/workflows/ci.yml`, `README.md`

### Steps

Create `.github/workflows/ci.yml`:
```yaml
name: Auto-Portfolio CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install uv
      - run: uv pip install -e ".[dev]" --system
      - run: python -m pytest tests/ -v --tb=short

  build_site:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: cd site && npm ci && npm run build

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install ruff
      - run: ruff check .
```

Create `README.md`:
```markdown
# 🎨 Auto-Portfolio

> Your code writes your portfolio. A zero-input portfolio generator that mines your git history and builds a stunning personal site.

## Quick Start

```bash
cd ~/projects/auto-portfolio
uv venv && source .venv/bin/activate
uv pip install -e .
cd site && npm install && cd ..

# Interactive setup
auto-portfolio setup

# Scan all repos and build site
auto-portfolio generate

# Preview locally
auto-portfolio preview
```

## What It Does

1. Scans all git repos in configured paths
2. Extracts tech stack, commit history, quality signals
3. Writes `site/src/data/projects.json`
4. Builds a static Astro site with project cards, stats, and detail pages

## Configuration

Edit `config.toml` to set your name, scan paths, and theme.

## Development

```bash
uv pip install -e ".[dev]"
python -m pytest tests/ -v
ruff check .
cd site && npm run dev  # Astro dev server
```
```

Run linter and fix:
```bash
cd ~/projects/auto-portfolio
source .venv/bin/activate
ruff check --fix .
ruff check .
python -m pytest tests/ -v --tb=short
```

### Verification
```bash
cd ~/projects/auto-portfolio
source .venv/bin/activate
python -m pytest tests/ --tb=short -q
ruff check .
python cmd/auto_portfolio.py --help
```
**Done when:** tests pass, ruff clean, help prints.

---

## TASK-016: End-to-end pipeline test

**Depends on:** TASK-015

### Steps

```bash
cd ~/projects/auto-portfolio
source .venv/bin/activate

# Generate portfolio from fixture repos
python cmd/auto_portfolio.py generate \
  --config config.toml \
  --site-dir site \
  --no-build  # skip Astro build in this step

# Verify JSON was written
python -c "
import json
from pathlib import Path
data = json.loads(Path('site/src/data/projects.json').read_text())
print(f'Projects in JSON: {len(data[\"projects\"])}')
assert len(data['projects']) >= 0
print('Data file OK')
"

# Build the Astro site
cd site && npm run build && cd ..

# Verify dist was created
python -c "
from pathlib import Path
dist = Path('site/dist')
assert dist.exists(), 'dist/ not created'
assert (dist / 'index.html').exists(), 'index.html missing'
print('Site built OK')
"
```

### Verification
```bash
cd ~/projects/auto-portfolio
python -c "
from pathlib import Path
assert (Path('site/dist/index.html')).exists()
content = Path('site/dist/index.html').read_text()
assert 'Portfolio' in content
print('End-to-end OK')
"
```
**Done when:** prints `End-to-end OK`.

---

## Summary

| Phase | Tasks | Goal |
|-------|-------|------|
| Setup | 001-003 | Python project, directories, config |
| Models | 004-005 | Pydantic models, tech detector |
| Scanner | 006-007 | Repo scanner with caching, description gen |
| Tests | 008 | Unit tests for all core modules |
| Site | 009-011 | Astro + Tailwind scaffold, pages, seed data |
| Generator | 012-013 | Site generator + CLI |
| Integration | 014-016 | Integration tests, CI, E2E pipeline |
