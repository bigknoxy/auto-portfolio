# Starting Prompt — Auto-Portfolio

> Paste this entire prompt into Claude Code (or your coding tool) to begin execution.

---

## Prompt

You are implementing the **auto-portfolio** project from scratch. This is a two-runtime project: a Python 3.12 scanner that generates JSON data, and an Astro 4 + Tailwind CSS static site that consumes that data to produce a beautiful developer portfolio.

**Your working directory is:** `~/projects/auto-portfolio`

**This project has two runtimes — keep them separate:**
- Python (uv) handles git scanning, tech detection, and JSON generation
- Node 20 (npm) handles the Astro site build

**Read these files FIRST, in this exact order, before writing any code:**
1. `AGENTS.md` — two-runtime architecture, common mistakes, workflow
2. `CLAUDE.md` — allowed commands, file structure rules, data contract
3. `PLAN.md` — architecture, phases, design philosophy
4. `IMPLEMENTATION.md` — scanner API, site generation, CI
5. `TASKS.md` — the atomic task list you will execute

**Your mission:** Work through `TASKS.md` from TASK-001 to TASK-016, completing each task fully before moving to the next.

**Task execution protocol (MANDATORY):**
1. Read the full task before writing any code
2. Execute every step in the exact order written
3. Run the `### Verification` command at the end of each task
4. If verification exits 0 → move to the next task
5. If verification fails → debug, fix, re-run, then proceed
6. NEVER skip a verification step

**Environment setup required before TASK-001:**
```bash
# Verify Node.js is available
node --version   # must be >= 18
npm --version

# Verify Rust is NOT needed (this is Python + Node only)
```

**After completing each task:**
- Append a completion note to `LEARNINGS.md`
- If you encountered a bug, write a full learning entry

**After every Python task block, run Python tests:**
```bash
cd ~/projects/auto-portfolio && source .venv/bin/activate
python -m pytest tests/ -q --tb=short
```

**After site tasks, verify Astro build:**
```bash
cd ~/projects/auto-portfolio/site && npm run build
```

**The project is complete when:**
- All 16 tasks verified ✓
- `python -m pytest tests/ -v` shows 0 failed
- `ruff check .` shows 0 issues
- `cd site && npm run build` exits 0
- `site/dist/index.html` exists and contains "Portfolio"
- `auto-portfolio generate --no-build` writes valid JSON to `site/src/data/projects.json`

Begin by reading `AGENTS.md`, then `TASKS.md`, then start TASK-001.
