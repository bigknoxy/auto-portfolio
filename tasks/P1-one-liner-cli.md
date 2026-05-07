# TASK-P1: One-Liner CLI

## Objective
Enable generating a complete portfolio with a single command: `npx auto-portfolio --github username`

## User Story
As a developer, I want to create my portfolio by running one command so I don't need documentation or configuration.

## Technical Requirements

### CLI Interface
- [ ] `auto-portfolio generate --github <username>`
- [ ] Interactive mode: `auto-portfolio setup`
- [ ] Auto-detect GitHub username
- [ ] Optional: GitHub token prompt

### GitHub Integration
- [ ] Auto-create GitHub App (or use existing)
- [ ] Fetch public profile data
- [ ] Detect repository languages
- [ ] Clone template repository
- [ ] Commit portfolio to `gh-pages` branch

### Deployment Automation
- [ ] GitHub Actions workflow generation
- [ ] Auto-enable Pages on repository
- [ ] Commit portfolio to `docs/` or root
- [ ] Trigger deployment

### Zero-Config Defaults
- [ ] Pre-filled profile config
- [ ] Default styling theme
- [ ] Standard project card template
- [ ] Working without any input files

## Success Criteria

| Metric | Target |
|--------|--------|
| Time to portfolio | ≤ 60 seconds |
| Manual steps required | 0 |
| Works without config | Yes |
| Deploys to GitHub Pages | Yes |

## Dependencies
- GitHub CLI (`gh`) installed or bundled
- Template repository
- GitHub App for OAuth (optional)

## Estimated Effort
**2-3 days**
- Day 1: CLI interface and GitHub integration
- Day 2: Template system and deployment
- Day 3: Testing with real accounts

## Risk Assessment

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| GitHub API changes | Medium | Low | Use stable APIs |
| CLI bundling size | Medium | Medium | Tree-shaking |
| User auth complexity | High | Medium | Optional, progressive |

## Acceptance Criteria
- [ ] `npx auto-portfolio --github bigknoxy` creates portfolio
- [ ] Portfolio auto-deploys to GitHub Pages
- [ ] No configuration files needed
- [ ] Works for any public GitHub profile