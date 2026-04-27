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
{project_name} --help
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
    project_name: str,
    author: str,
    python_version: str,
    license_: str,
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

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "ruff>=0.4.0",
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


def github_actions_ci(
    project_name: str, python_version: str
) -> str:
    # ruff: noqa: E501
    return f"""\
name: CI

on:
    push:
        branches: ["main"]
    pull_request:
        branches: ["main"]

jobs:
    test:
        name: Test (Python ${{{{ matrix.python-version }}}})
        runs-on: ubuntu-latest
        strategy:
            matrix:
                python-version: ["{python_version}"]

        steps:
            - uses: actions/checkout@v4

            - name: Set up Python ${{{{ matrix.python-version }}}}
              uses: actions/setup-python@v5
              with:
                python-version: ${{{{ matrix.python-version }}}}

            - name: Configure git identity for tests
              run: |
                git config --global user.email "ci@{project_name}.com"
                git config --global user.name "CI"

            - name: Install dependencies
              run: |
                pip install -e ".[dev]"
                pip install ruff pytest

            - name: Run tests
              run: pytest tests/ -v

    lint:
         name: Lint
         runs-on: ubuntu-latest

         steps:
            - name: Set up Python
              uses: actions/setup-python@v5
              with:
                python-version: "{python_version}"

            - name: Install ruff
              run: pip install ruff>=0.4.0

            - name: Run ruff
              run: ruff check .
"""
