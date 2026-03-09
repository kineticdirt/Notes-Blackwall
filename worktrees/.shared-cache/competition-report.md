# Competition report (tool-name sanitization)

- Generated: 2026-01-30T22:26:46.064Z
- Spec version: 2.0.0
- Target regex: `^[a-zA-Z0-9_-]{1,128}$`

## Leaderboard
- 1. **pragmatist** — total=80.31 tests=PASS perf(ns/iter)=5651
- 2. **user-experience** — total=79.81 tests=PASS perf(ns/iter)=6652
- 3. **security-focused** — total=78.09 tests=PASS perf(ns/iter)=10102
- 4. **conservative** — total=77.91 tests=PASS perf(ns/iter)=10461
- 5. **performance-focused** — total=77.72 tests=PASS perf(ns/iter)=10824
- 6. **radical** — total=71.16 tests=PASS perf(ns/iter)=23937

## Winner
**pragmatist**

## Notes
This is a pragmatic harness applying the worktree-orchestration spec to the current R&D blocker: Goose MCP tool-name validation.
Peer review / code quality / innovation are currently neutral placeholders; we can wire those to real cross-review and complexity metrics next.
