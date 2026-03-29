# ADR 0003: Branch protection defaults

**Status: Accepted**
**Date: 28-03-2026**

## Context
`scaffoldr` configures branch protection on main after
creating a GitHub repo. We need to decide if protection
is mandatory, and how many PR reviewers are required.

## Decision
- Branch protection is enabled by default but can be
  skipped via `--no-protect` flag on `scaffoldr new`
- Required revier count is configurable via the 
  `~/.scaffoldr/config.toml` (`required_reviewers` field)
- Default reviewer count is 1
- Direct pushes to main are always disabled when
  protection is enabled

## Alternatives Considered
- Always protect, no override: too rigid for solo
  projects where PR reviews aren't required
- Always 1 reviewer: reasonable default, but solo devs
  may want 0 to block direct pushes without requiring 
  a reviewer

## Consequences
- Solo devs can set `required_reviewers=0` to block 
  direct pushes without needing a reviewer
- Teams can set `required_reviewers` to 2 or more
- `--no-protect` flag allows skipping entirely for
  quick throwaway repos
