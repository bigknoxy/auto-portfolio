# LEARNINGS.md — Auto-Portfolio

> Append here after every task, bug fix, or discovery.

## Format
```
## Learning NNN — YYYY-MM-DD: TASK-NNN — <title>
**Problem:** ...
**Root cause:** ...
**Fix:** ...
**Prevention:** ...
```

---

## Pre-populated Gotchas

### G-001: Empty repos fail git rev-parse
`git -C path rev-parse HEAD` returns non-zero on repos with 0 commits.
Always check `if not head_sha: return None` before any further git operations.

### G-002: Astro dynamic imports need try/catch
`await import('../data/projects.json')` throws at build time if the file doesn't exist.
Always wrap in `try { ... } catch (e) { projects = []; }`.

### G-003: Slug collisions
Two repos named `my-app` and `My App` produce the same slug: `my-app`.
The second one would overwrite the first in Astro's `getStaticPaths`.
After slugifying, deduplicate: `my-app`, `my-app-2`, etc.
(Not yet implemented — add if you encounter this.)

### G-004: Cache is not invalidated on config changes
The cache key is `<repo-id>/<head-sha>.json`. If you add new fields to `ProjectRecord`,
old cache entries won't have them. Add a `schema_version` field and invalidate on mismatch.

### G-005: conftest.py git init in CI
The `pytest_configure` hook runs `git init` and commits in fixture dirs.
In CI, git may not have a global `user.email` set, causing commit to fail.
The conftest explicitly sets `user.email` and `user.name` per-repo to avoid this.

### G-006: Astro static paths require `getStaticPaths`
`site/src/pages/projects/[slug].astro` MUST export `getStaticPaths()`.
Without it, Astro throws: "Astro.params is not available in static mode without `getStaticPaths`".

### G-007: Language percentages don't sum to 100
`detect_languages()` counts files per extension. If a repo has 10 Python files and 5 JS files,
it returns `{"Python": 66.7, "JavaScript": 33.3}` — which sums correctly.
But if you add rounding errors (e.g., many small languages), the sum may be 99.9 or 100.1.
This is acceptable; don't assert `sum == 100.0` in tests.

## Completed: TASK-001

### Learning 001 — 2026-04-26: TASK-001 — uv package discovery
**Problem:** `uv pip install -e ".[dev]"` failed with "no packages found to install" (setuptools package discovery error).
**Root cause:** setuptools couldn't discover packages without explicit `pyproject.toml` configuration.
**Fix:** Added `[tool.setuptools.packages.find]` with `include = ["core*", "cmd*"]` to pyproject.toml.
**Prevention:** Always add setuptools package discovery config when using uv editable installs.

## Completed: TASK-002

## Completed: TASK-003

## Completed: TASK-004

## Completed: TASK-005

## Completed: TASK-006

## Completed: TASK-007

## Completed: TASK-008

### Learning 002 — 2026-04-26: TASK-008 — stdlib shadowing
**Problem:** `cmd/` directory shadowed Python's stdlib `cmd` module, breaking pdb import in pytest
**Root cause:** Python path resolution prefers local packages over stdlib
**Fix:** Renamed `cmd/` → `cli/` and updated pyproject.toml entry points
**Prevention:** Never name packages after stdlib modules

## Completed: TASK-009

## Completed: TASK-010

## Completed: TASK-011

## Completed: TASK-012

## Completed: TASK-013

## Completed: TASK-014

## Completed: TASK-015

## Learning 003 — 2026-04-29: GitHub Pages — Astro GitHub Pages base path and CSS bundling
**Problem:** Site deployed to `https://bigknoxy.github.io/auto-portfolio/` with broken CSS and internal links
**Root cause:**
  - `astro.config.mjs` was missing the `base` config, so Astro output without `/auto-portfolio` prefix
  - `global.css` had raw `@tailwind` directives served as static file instead of being processed by Astro/Tailwind pipeline
  - All internal links were hardcoded as `href="/"` and `href="/projects"` which resolved to root, not `/auto-portfolio/`
**Fix:**
  - Added `base = '/auto-portfolio'` to `astro.config.mjs` so asset paths get prefixed
  - Imported `global.css` in `BaseLayout.astro` instead of static link
  - Used relative paths (`../`, `../projects/`) calculated from page depth for nav and project card links
**Prevention:** Always configure `base` for GitHub Pages subdirectory deploys; Astro does NOT auto-rewrite manual hrefs

## Completed: TASK-016

---

All 16 tasks complete! ✅
---

*No task learnings yet — add them as you work.*
