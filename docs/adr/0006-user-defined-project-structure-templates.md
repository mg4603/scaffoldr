# ADR 0006: User-Defined Project Structure Template

**Status: Accepted**  
**Date: 18-05-2026**  

## Context
v0.1.0 ships a single hardcoded project structure. Different teams
need different structures (FastAPI, Django, CLI tools, data 
pipelines). Requiring a code change to add a template is bad UX.


## Decision
Support user-defined templates as TOML files in 
`~/.config/scaffoldr/templates`. Each file declares a name, 
description, and file paths with content. Variable substitution via
{key} syntax is supported.

Built-in templates ship with the package. User templates take
precedence on name collision.

## Alternatives Considered
- Jinja2 templating: more powerful but heavy dependency and steeper
  learning curve for users writing templates. Deferred to v0.3.0
  if demand exists
- Git-based templates (like cookiecutter): too complex for use case;
  `scaffoldr` is opinionated
- Single shared templates dir only: loses the built-in/user 
  separation; harder to document

## Consequences
## Positives
- Flexibility in project structure
- Code base need not be changed for different project structure

## Negatives
- `{key}` substitution syntax conflicts with literal `{` characters
  in template file contents, such as JSON or Python code
