# 🎨 Auto-Portfolio — Plan

> **Your code writes your portfolio.** A zero-input portfolio generator that mines your git history and builds a stunning personal site — projects, skills, commit history, and more.

---

## 🎯 Project Goal

Build a single-command portfolio generator that:
1. Scans all local git repositories (configurable paths)
2. Extracts project metadata (tech stack, description, activity, complexity)
3. Generates a **beautiful, design-forward portfolio website** with zero manual input
4. Supports deployment (static export, GitHub Pages, Vercel)
5. Updates incrementally — re-scan only changed repos

The entire process: `auto-portfolio generate → auto-Portfolio deploy`

---

## 📦 Tech Stack

| Layer | Choice | Why |
|-------|--------|-----|
| Core Engine | Python 3.12+ | Git parsing, metadata extraction |
| Web Framework | **Astro** + **Tailwind CSS** | Fast static gen, SSG, design system |
| Git Parsing | `gitpython` + raw `git log` | Commit counts, contributors, languages |
| Tech Detection | Custom manifest parser + file extension analysis | Auto-detect stack from `package.json`, `Cargo.toml`, etc. |
| Image Generation | **DALL-E / local** or auto-screenshot via Playwright | Project "preview" images |
| Markdown Processing | Language extraction from commit messages | Auto-generated project descriptions |
| Deployment | `gh-pages` or Vercel CLI | One-command publish |

---

## 🏗 Architecture

```
auto-portfolio/
├── cmd/
│   ├── auto-portfolio.py   # Main CLI (generate, deploy, scan)
│   └── auto-portfolio.sh   # Shell wrapper
├── core/
│   ├── repo_scanner.py     # Find repos, extract metadata
│   ├── tech_detector.py    # Parse manifests → stack list
│   ├── commit_analyzer.py  # Git history → activity metrics
│   ├── description_gen.py  # AI or heuristic project descriptions
│   └── asset_builder.py    # Generate screenshots, logos, icons
├── data/
│   ├── models.py           # Project, Tech, Commit models (pydantic)
│   ├── schema.json         # JSON output schema
│   └── themes/             # Color schemes, font configs
├── site/                   # Generated Astro project (output dir)
│   ├── astro.config.mjs    # Auto-generated config
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── layouts/        # Page layouts
│   │   ├── pages/          # Auto-generated pages
│   │   ├── styles/         # Tailwind config
│   │   └── data/           # JSON project data (pipelines into Astro)
│   └── public/             # Static assets, screenshots
├── templates/              # Astro component templates
├── deploy/
│   ├── github_pages.py     # gh-pages push
│   ├── vercel.py           # Vercel deploy
│   └── netlify.py          # Netlify deploy
├── config.toml             # Scan paths, profile info, theme, deployment target
└── pyproject.toml
```

---

## 🔍 What Gets Extracted Per Project

### Project Identity
| Field | Source |
|-------|--------|
| Name | Repo name or `package.json` / `pyproject.toml` name |
| Description | README.md top paragraph or AI-generated from commits |
| Stars/Forks | GitHub API (if public) |
| Created/Updated | First/last commit dates |
| Language Distribution | Linguist-style file extension analysis |

### Tech Stack
| Field | Source |
|-------|--------|
| Primary Language | Dominant file extension |
| Frameworks | Manifest files (`package.json` deps, etc.) |
| Package Manager | `package-lock.json`, `yarn.lock`, `Cargo.lock`, etc. |
| Build Tools | Webpack, Vite, Turbopack, etc. detection |
| Testing | Jest, Vitest, Pytest, etc. |

### Activity Metrics
| Field | Source |
|-------|--------|
| Total Commits | `git log --oneline | wc -l` |
| Contributors | `git shortlog -sn` |
| Files Changed | `git diff --stat` on last month |
| Commit Frequency | Commits/month average |
| Last Active | Most recent commit date |

### Quality Signals
| Field | Source |
|-------|--------|
| Has Tests | Test framework detection |
| Has CI/CD | `.github/workflows/`, `.gitlab-ci.yml` |
| Has Docs | `README.md`, `docs/` directory |
| Has Linting | ESLint, Prettier, Ruff detection |
| Commit Quality | Conventional commits detection |

---

## 🌐 Generated Website Structure

### Pages
| Page | Purpose |
|------|---------|
| **Home** | Hero section, about me, quick stats |
| **Projects** | Grid of project cards with filters |
| **Project Detail** | Auto-generated per project |
| **Skills** | Radar chart of tech proficiency |
| **Activity** | GitHub-style contribution heatmap |
| **Timeline** | Chronological project history |
| **Blog (optional)** | Auto-generated commit highlights |

### Hero Statistics
```
┌──────────────────────────────────────────┐
│   Welcome, I'm Joshua                  │
│   Full-Stack Developer · Tinkerer       │
│                                        │
│   📦  42 repos        ⭐ 128 stars     │
│   🌐  5 languages     🧪 84 exper.    │
│   📝  3,241 commits   📅 3+ years     │
│   🔥  3 month streak  🏆 Top 1%       │
└──────────────────────────────────────────┘
```

### Project Card Design
```
┌────────────────────────────────────────────┐
│  [screenshot/preview image]                │
│                                            │
│  📦 ProjectName                           │
│  Auto-generated description from README.. │
│                                            │
│  🐍 Python · ⚛️ React · 🐳 Docker       │
│                                            │
│  ⭐ 12   🍴 3   📝 89 commits          │
│  Last active: 2 days ago                  │
└────────────────────────────────────────────┘
```

---

## 🎨 Design Philosophy

The portfolio should feel **hand-crafted, not AI-generated**. Key principles:

1. **Distinctive visual identity** — not generic bootstrap/React aesthetics
2. **Motion with purpose** — subtle animations that guide attention, not distract
3. **Data-driven storytelling** — charts and metrics that tell a real story
4. **Responsive first** — mobile-native design, scales up gracefully
5. **Fast** — sub-2s LCP, minimal JS payload
6. **Accessible** — WCAG AA minimum

### Color Palette Examples (Theme Support)
- **Dark**: Deep space backgrounds (`#0a0a0f`), neon accents, gradient highlights
- **Light**: Warm whites, muted pastels, sharp typography
- **Custom**: Generated from user's most-used language colors

---

## 📊 Phases

### Phase 1: Scanner + Data Model (Week 1)
- [ ] Repo scanner with git metadata extraction
- [ ] Tech stack detection from manifests
- [ ] Commit history analysis (frequency, quality signals)
- [ ] Pydantic models + JSON serialization
- [ ] CLI scaffold: `auto-portfolio scan > projects.json`

### Phase 2: Site Generation (Week 2-3)
- [ ] Astro project scaffold with Tailwind
- [ ] Project card component with rich metadata display
- [ ] Skills radar chart from tech distribution
- [ ] Activity heatmap (GitHub-style contribution grid)
- [ ] Auto-generated project detail pages
- [ ] Theme system (dark/light/custom)

### Phase 3: Intelligence (Week 4)
- [ ] AI-powered description generation (LLM fallback, README-first heuristic)
- [ ] Project screenshot capture (Playwright headless browser)
- [ ] Timeline/era detection ("2024: Performance focus")
- [ ] Quality scoring per project (documentation, tests, activity)
- [ ] Filter system: by tech, date, activity, quality

### Phase 4: Deploy & Polish (Week 5)
- [ ] GitHub Pages deployment
- [ ] Vercel deployment
- [ ] Incremental build (only re-scan changed repos)
- [ ] Config-driven profile (name, title, bio, social links)
- [ ] SEO meta tags auto-generation
- [ ] Sitemap, RSS feed

---

## 🧪 Success Metrics

| Metric | Target |
|--------|--------|
| Scan 50 repos | < 10s |
| Site generation | < 5s (incremental), < 30s (full) |
| Lighthouse score | > 90 all categories |
| LCP (First Contentful) | < 1.5s |
| Bundle size (total JS) | < 50KB gzipped |
| Deploy time | < 60s end-to-end |

---

## 🚀 Quick Start

```bash
# Install
cd ~/projects/auto-portfolio
uv venv && source .venv/bin/activate
uv pip install gitpython pydantic rich click playwright

# Setup (generates config + profile questions)
python cmd/auto-portfolio.py setup

# Generate
python cmd/auto-portfolio.py generate

# Preview
python cmd/auto-portfolio.py preview

# Deploy
python cmd/auto-portfolio.py deploy --target vercel
```

---

## 💡 Unique Features

1. **"My Code Personality"** — AI analysis of your commit messages and code style generates a personality profile ("You write verbose, well-documented code with a testing-first mindset")
2. **"Project Family Tree"** — Graph visualization showing which projects inspired/share code with others
3. **"Streak Tracker"** — Git commit streaks visualized (like GitHub but with personal milestones)
4. **"Tech Journey Map"** — Animated timeline showing when you first used each technology
5. **"Hidden Gems"** — Projects with interesting complexity that you didn't showcase but deserve attention
6. **"Auto-Blog"** — Weekly digest of your own commits, auto-formatted as a dev blog post
7. **"Resume Export"** — Generate a PDF resume from the same data

---

## 📋 Config Example (`config.toml`)

```toml
[profile]
name = "Joshua"
title = "Full-Stack Developer · Performance Obsessive"
bio = "I build fast things and make slow things fast."
avatar = "~/Pictures/avatar.jpg"
social.github = "https://github.com/yourusername"
social.linkedin = "..."

[scan]
paths = ["~/projects", "~/work"]
exclude = ["**/.git", "**/node_modules", "**/dist"]
min_commits = 10        # Ignore repos with < 10 commits
max_age_days = 730      # Only show projects from last 2 years

[site]
theme = "dark"
accent_color = "#6366f1"
language = "en"
favicon = "auto"        # Generate from avatar or initials

[deploy]
target = "vercel"       # vercel, github-pages, netlify
domain = "joshua.dev"   # Optional custom domain
```
