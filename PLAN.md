# Auto-Portfolio Enhancement Plan

## Vision
Transform auto-portfolio from a static generator to a dynamic, live-updating portfolio system with viral adoption potential.

## Priority Roadmap

| Priority | Initiative | Estimated Effort | ROI Impact |
|----------|-----------|------------------|------------|
| 🔴 P0 | Live Portfolio Feature | 3-4 days | Highest - proves system works |
| 🟡 P1 | One-Liner CLI | 2-3 days | High - viral adoption |
| 🟢 P2 | Component Library | 2-3 days | Medium - developer experience |
| 🟢 P3 | Performance Optimization | 1-2 days | Medium - speed to market |

---

## P0: Live Portfolio Feature

### Goal
Portfolio shows real-time GitHub stats: commits, languages, CI status, stars.

### Key Metrics to Display
- 🔹 Total commits across all repos
- 🔹 Languages distribution (real %)
- 🔹 GitHub Actions CI pass rate
- 🔹 Repository star counts
- 🔹 Last commit dates

### Implementation Approach
1. **GitHub GraphQL API** - Single request for all repo data
2. **Caching Strategy** - Cache per-repo, invalidate on HEAD change
3. **Astro Integration** - Fetch at build time, cache results

### Success Criteria
- Portfolio updates automatically on `auto-portfolio generate`
- Shows accurate, real-time stats from GitHub
- Gracefully handles rate limits and API failures

### Deliverables
- [ ] GitHub client supports GraphQL queries
- [ ] Live stats integrated into ProjectRecord
- [ ] Astro components display live badges
- [ ] Rate limit handling with exponential backoff

---

## P1: One-Liner CLI

### Goal
Generate entire portfolio with `npx auto-portfolio --github username`

### Features
- No config file needed
- Auto-creates GitHub app token
- Generates, commits, and deploys in one command

### Implementation Approach
1. **GitHub OAuth App** - For seamless auth
2. **Template Repository** - Forkable starter
3. **GitHub Actions Integration** - Auto-deploy workflow

### Success Criteria
- Single command generates working portfolio
- User never leaves terminal

- Works for any public GitHub profile

### Deliverables
- [ ] GitHub App registration flow
- [ ] npx package published
- [ ] One-command deployment script

---

## P2: Component Library

### Goal
Reusable Astro components for rapid portfolio customization

### Components Planned
- 🔹 `ProjectCard.astro` - Enhanced with live stats
- 🔹 `LanguageBar.astro` - Interactive language breakdown
- 🔹 `StatsGrid..astro` - Key metrics display
- 🔹 `DeployBadge.astro` - Live CI/CD status

### Implementation Approach
1. **Slot-based composition** - Allow customization
2. **Tailwind variants** - Light/dark themes
3. **Package distribution** - Publish to npm

### Success Criteria
- Users can swap components in 5 minutes
- Consistent design language across templates
- Easy to theme and brand

### Deliverables
- [ ] Component library documentation
- [ ] npm package: `@auto-portfolio/components`
- [ ] 3+ template variations

---

## P3: Performance Optimization

### Goal
Generate portfolio in <5 seconds, incremental builds

### Optimizations Planned
- 🔹 LRU cache for GitHub API responses
- 🔹 Parallel git operations with asyncio
- 🔹 Incremental Astro builds (only changed pages)
- 🔹 Pre-built language detection cache

### Implementation Approach
1. **Async git operations** - `asyncio.create_subprocess_exec`
2. **Structured caching** - Redis-compatible format
3. **Astro partial builds** - Leverage Astro's built-in incremental

### Success Criteria
- Cold generate: <10 seconds
- Incremental: <3 seconds
- Memory usage: <100MB

### Deliverables
- [ ] Performance benchmark suite
- [ ] Caching layer with TTL
- [ ] Build time reduction metrics

---

## Execution Order

```
Week 1: P0 Live Portfolio (Days 1-4)
Week 2: P1 One-Liner CLI (Days 5-7)
Week 3: P2 Component Library (Days 8-10)
Week 4: P3 Performance Optimization (Days 11-14)
```

## Resource Requirements

- **Engineering**: 1 FTE
- **Design**: 0.2 FTE (component styling)
- **Marketing**: 0.1 FTE (documentation, examples)

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| GitHub API rate limits | Implement caching + user tokens |
| OAuth complexity | Progressive disclosure, auto-setup |
| Component library bloat | Strict size budgets |
| Memory leaks | Memory profiling after each feature |