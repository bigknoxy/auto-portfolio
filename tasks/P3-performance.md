# TASK-P3: Performance Optimization

## Objective
Reduce portfolio generation time to <5 seconds and enable incremental builds.

## User Story
As a developer, I want fast builds so I can iterate quickly on my portfolio without waiting.

## Technical Requirements

### Caching Layer
- [ ] LRU cache for GitHub API responses
- [ ] Cache TTL: 1 hour for live stats
- [ ] Cache key: `github/<owner>/<repo>/<sha>`
- [ ] Redis-compatible serialization

### Parallel Processing
- [ ] Async git operations using `asyncio.create_subprocess_exec`
- [ ] Concurrent repository processing
- [ ] Batch GitHub API requests
- [ ] Semaphore for connection limits

### Incremental Builds
- [ ] Only generate changed project pages
- [ ] Astro partial build support
- [ ] Detect file changes via mtime
- [ ] Skip unchanged repositories

### Memory Efficiency
- [ ] Streaming JSON parsing
- [ ] Generator-based data processing
- [ ] Memory profiling after each operation
- [ ] Target: <100MB peak usage

## Success Criteria

| Metric | Current | Target |
|--------|---------|--------|
| Cold generate time | ~15 seconds | <10 seconds |
| Incremental build | ~8 seconds | <3 seconds |
| API requests per build | 20+ | ≤ 3 |
| Memory usage | N/A | <100MB |

## Dependencies
- `aiocache` for caching
- `asyncio` for parallel processing
- Astro's partial build support

## Estimated Effort
**1-2 days**
- Day 1: Caching implementation
- Day 2: Parallel processing + benchmarking

## Risk Assessment

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|--      -------|
| Cache coherency | High | Medium | Write-through |
| Async complexity | Medium | Medium | Error handling |
| Memory leaks | High | Low | Profiling |

## Acceptance Criteria
- [ ] Cold generate: <10 seconds
- [ ] Incremental: <3 seconds  
- [ ] Memory usage documented
- [ ] Benchmark test suite
- [ ] Cache hit monitoring