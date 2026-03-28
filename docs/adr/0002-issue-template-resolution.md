# ADR 0002: Issue template resolution strategy

**Status: Accepted**
**Date: 28-03-2026**

## Context
`scaffoldr` needs to create GitHub issues when scaffolding a new
project. We need to decide where issue templates come from and how
conflicts between built-in and user-defined templates are resolved.

## Decision
Use a two-layer resolution strategy:
1. Load built-in default templates shipped with `scaffoldr`
2. Load user templates from `~/.scaffoldr/issues.toml`
3. User templates override built-in defaults by title

Built-in defaults cover the most common issue types that any new
project needs (e.g. chore: initial setup, chore: CI setup, 
docs: write README).

User templates allow customization without forking `scaffoldr` or
losing built-in defaults entirely.

## Alternatives Considered
- Built-in defaults only: simple but not flexible, users can't 
  customize without modifying source
- User templates only: flexible but requires users to define 
  everything from scratch, poor out-of-box experience

## Consequences
- `scaffoldr` ships with a sensible default issue set
- Users can override any default by matching title
- Users can add new templates that built-ins don't cover
- Template resolution logic lives in a single module
- `issues.toml` format must be documented clearly
