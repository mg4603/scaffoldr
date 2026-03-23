# ADR 0001: Use typer and httpx as core dependencies

**Status: Accepted**  
**Date: 23-03-2026**

## Context
scaffoldr is a CLI tool that needs to:
1. Provide a clean, self-documenting CLI interface
2. Interact with the Github API to create repos, open issues, 
   and configure branch protection

## Decision
Use `typer` for the CLI layer and `httpx` for Github API calls

### typer
- Built on `click`, uses python type hints for argument
  definitions
- Generates `--help` output automatically
- Makes the CLI self-documenting with zero extra work
- Actively maintained, good ecosystem

### httpx
- Modern HTTP client with a clean API
- Supports both sync and async - we use sync for now
- No Github-specific abstraction layer means we only import
  what we actually use
- Lightweight: no hidden complexity for 4-5 endpoints

## Alternatives Considered
- `click` directly: more verbose, no type hint ergonomics
- `argparse`: stdlib but too low level for good UX
- `PyGithub`: full Github SDK, too much overhead for the 4
  endpoints we actually need
- `requests`: older, no async path if we need it later

## Consequences
- Adds 2 runtime dependencies
- typer requires `Python 3.7+`
- Github API calls require a personal access token,
  stored in the env variable `SCAFFOLDR_GITHUB_TOKEN`
- We own the Github API call logic - means we write a
  small client in `github.py` ourselves
