# TASK-P0: Live Portfolio Feature

## Objective
Enable portfolio to display real-time GitHub statistics instead of static data.

## User Story
As a portfolio visitor, I want to see live commit counts, language percentages, and CI status so I can verify the developer's activity level.

## Technical Requirements

### GitHub GraphQL API Integration
- [ ] Query repository details in single request
- [ ] Fetch live commit counts per repository
- [ ] Get language distribution percentages
- [ ] Retrieve default branch protection status
- [ ] Get latest commit date per repo

### Data Model Updates
- [ ] Add `live_stats` field to `ProjectRecord`
- [ ] Include `total_commits`, `language_percentages`, `last_commit_date`
- [ ] Add CI status fields (optional)

### Astro Integration
- [ ] Fetch live data at build time
- [ ] Display live badges in project cards
- [ ] Show global stats on homepage
- [ ] Graceful degradation when API unavailable

### Rate Limit Handling
- [ ] Implement exponential backoff
- [ ] User-configurable GitHub token
- [ ] Cache for 1 hour minimum
- [ ] Fallback to cached data on rate limit

## Success Criteria

| Metric | Target |
|--------|--------|
| API calls per generate | ≤ 3 total |
| Cache hit rate | ≥ 95% |
| Build time increase | ≤ 2 seconds |
| Graceful fallback | Works without API |

## Dependencies
- GitHub Personal Access Token (user-provided)
- GraphQL client library

## Estimated Effort
**3-4 days**
- Day 1: API integration and data model
- Day 2: Caching and error handling
- Day 3: Astro components and display
- Day 4: Testing and optimization

## Risk Assessment

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| GitHub API limits | High | Medium | Cache + token |
| GraphQL schema changes | Medium | Low | Version pinning |
| Build time blowup | Medium | Medium | Parallel requests |

## Acceptance Criteria
- [ ] Portfolio shows live commit counts
- [ ] Language percentages sum to 100%
- [ .ENV configuration for GitHub token
- [ ] Documentation for API setup
- [ ] Tests for API failure scenarios