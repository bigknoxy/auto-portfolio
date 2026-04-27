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
