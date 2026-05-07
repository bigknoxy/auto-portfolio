# AGENTS.md — Auto-Portfolio

> Instructions for all AI coding agents working on this project.
> Read this file **before** reading any other file.

---

## Project at a Glance

| Item | Value |
|------|-------|
| Python | 3.12+ (backend scanner) |
| Package manager | `uv` |
| Site framework | Astro 4.x + Tailwind CSS 3.x |
| Node version | 20 LTS |
| Test runner | `pytest` |
| Linter | `ruff` (Python), TypeScript via Astro |

---

## Golden Rule

**Never mark a task complete unless its verification command exits 0.**
Fix, re-run, then proceed. No skipping.

---

## Workflow Protocol

1. Read `TASKS.md` — single source of truth for task order (TASK-001 → TASK-016).
2. For each task:
   a. Read the full task before writing any code.
   b. Execute every step in order.
   c. Run the `### Verification` command.
   d. Pass → move on. Fail → fix and re-run.
3. After Python tasks (001-008), run:
   ```bash
   cd ~/projects/auto-portfolio && source .venv/bin/activate
   python -m pytest tests/ -q --tb=short
   ```
4. After site tasks (009-011), verify the Astro build:
   ```bash
   cd ~/projects/auto-portfolio/site && npm run build
   ```
5. Record learnings in `LEARNINGS.md`.

---

## Two Separate Environments

This project has **two runtimes**:

### Python (scanner/generator)
```bash
cd ~/projects/auto-portfolio
source .venv/bin/activate
uv pip install -e ".[dev]"
python cmd/auto_portfolio.py --help
```

### Node/Astro (site)
```bash
cd ~/projects/auto-portfolio/site
npm install
npm run dev   # dev server
npm run build # production build
```

**These environments are independent.** Python writes JSON to `site/src/data/`.
Astro reads that JSON at build time. Never import Python from Astro or vice versa.

---

## Task Tracking Rules

- Before starting: add `## In Progress: TASK-NNN` to `LEARNINGS.md`.
- After completing: update to `## Completed: TASK-NNN`.
- After any bug: write full learning entry.

---

## Code Standards

### Python Scanner
- Type annotations on every public function
- Cache results in `~/.cache/auto-portfolio/<repo-id>/<head-sha>.json`
- Always invalidate cache by HEAD SHA — if HEAD changed, re-scan
- Use `pathlib.Path` everywhere
- `ruff check .` must pass with zero warnings

### Astro/TypeScript
- Components in `site/src/components/*.astro`
- Pages in `site/src/pages/`
- Data consumed only from `site/src/data/` JSON files
- No external API calls from Astro pages (static site)
- Tailwind utility classes only — no custom CSS files except `global.css`

### Data Stability Rules
- `id` field in `ProjectRecord` must be stable across runs (sha256 of path)
- `slug` must be URL-safe and consistent with `slugify()` function
- Never change the JSON schema without updating both scanner output AND Astro consumers

---

## Common Mistakes — Read Before Coding

1. **gitpython vs subprocess**: The codebase uses `subprocess` + `git` CLI directly (faster than gitpython's object model). Import `gitpython` as `git` but use `subprocess` for performance-critical operations.

2. **Empty git repos**: `git rev-parse HEAD` fails on repos with 0 commits. Always check `head_sha` is non-empty before continuing `scan_repo()`.

3. **Astro dynamic imports**: `import('../data/projects.json')` can fail if the file doesn't exist yet. Always wrap in `try/catch` and provide empty fallback.

4. **`slugify()` must be consistent**: The same project name must always produce the same slug across runs. Test with special characters: `React + TypeScript!` → `react-typescript`.

5. **Node vs npm versions**: Astro 4.x requires Node 18+. If `npm run build` fails with syntax errors, check `node --version`.

6. **Cache invalidation**: The cache key is `<repo-id>/<head-sha>.json`. If a repo is scanned with old HEAD, the cached result is served. Always pass `use_cache=False` in tests.

7. **Git submodules**: `scan_repo()` can accidentally find git repos inside `.git/modules/`. Check that the path doesn't contain `.git` components.

8. **Playwright not in default deps**: Screenshot capture is in the `playwright` optional extra. Don't require it for core tests — use fallback image generation instead.

9. **`primary_language` vs `stack[0]`**: Language distribution counts files; stack comes from manifests. They may disagree. Use `primary_lang` from language distribution for display, `stack` for tags.

---

## Learnings System

```markdown
## Learning NNN — YYYY-MM-DD: TASK-NNN — <title>
**Problem:** ...
**Root cause:** ...
**Fix:** ...
**Prevention:** ...
```

**Before fixing any issue, check `LEARNINGS.md` for known patterns and their solutions.**
If you find a matching pattern, apply the known solution first, then adapt for the current context.
This prevents recurring issues and accelerates debugging.

---

## Definition of Done

- [ ] All 16 tasks verified (exit 0)
- [ ] `python -m pytest tests/ -v` shows 0 failed
- [ ] `ruff check .` shows 0 issues
- [ ] `cd site && npm run build` exits 0
- [ ] `site/dist/index.html` exists and contains "Portfolio"
- [ ] `site/dist/projects/` contains at least one project page
- [ ] `auto-portfolio generate --no-build` writes valid `site/src/data/projects.json`
- [ ] `LEARNINGS.md` populated
