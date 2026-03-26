from __future__ import annotations


def readme(project_name: str, author: str) -> str:
    return f"""\
# {project_name}

> Short description of what this project does.

## Installation
```bash
pip install {project_name}
```

## Usage
```bash
{project_name} -- help
````

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup and
contribution guidelines.

## License

{author} - MIT
"""


def contributing(project_name: str) -> str:
    return f"""\
# Contributing to {project_name}

## Branch Naming

- feat/<short-description>
- fix/<short-description>
- chore/<short-description>
- docs/<short-description>

## Commit Messages

Follow conventional commits:

- feat: add a new feature
- fix: fix a bug
- chore: tooling, config, dependencies
- docs: documentation only
- test: add tests

## Pull Requests

1. Branch off meain
2. Make your changes
3. Open a PR referencing the related issue
4. PR title should follow the commit message format

## Running tests
```bash
pytest
```
"""


def pyproject(
    project_name: str, author: str, python_version: str, license_: str
) -> str:
    return f"""\
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{project_name}"
version = "0.1.0"
description = ""
authors = [{{name = "{author}"}}]
license = {{text = "{license_}"}}
requires-python = ">={python_version}"
dependencies = []

[dependency-groups]
dev = [
    "pytest>=8.0.0",
]
"""


def adr_template(project_name: str) -> str:
    return f"""\
# ADR 0001: Initial decisions for {project_name}

**Status: Draft**
**Date: **

## Context

Describes the context and problem this decision 
addresses.

## Decision

Describes the decision made.

## Alternatives considered

- Alternative A: reason rejected
- Alternative B: reason rejected

## Consequences

### Positive
...

### Negative
...
"""


def gitignore() -> str:
    return """\
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.venv/
.env
.pytest-cache/
.ruff-cache/
"""
