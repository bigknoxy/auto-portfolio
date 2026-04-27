# 🎨 Auto-Portable

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
