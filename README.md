# scaffoldr
CLI tool that scaffolds new projects with opinionated structure -
GitHub repo, issues, ADR templates, branch protection rules, all 
in one command.

![CI](https://github.com/mg4603/scaffoldr/actions/workflows/ci.yml/badge.svg)

## Why

Most projects start with `git init` and a blank README. 
`scaffoldr` sets up everything you actually need from day one:
- Opinionated folder structure
- ADR template for documenting decisions
- GitHub repo created via API
- Default issues so that you have a backlog immediately
- Branch protection on main so nothing gets pushed directly

## Demo
![demo](demo.gif)

## Installation
```bash
pipx install scaffoldr
```

Or with pip:
```bash
pip install scaffoldr
```

## Quickstart

Setup your config once:
```bash
scaffoldr config init
```

Then scaffold a new project:
```bash
scaffoldr new myproject --description "What it does"
```

This will:
1. Create `myproject` locally with opinionated structure
2. Create a GitHub repo via the API
3. Push the initial commit
4. Open default issues on the repo
5. Enable branch protection on main

To scaffold locally only (no GitHub):
```bash
scaffoldr init myproject
```

## Project structure

Every scaffolded project gets:
```
myproject/
├── myproject/
│   └── __init__.py
├── tests/
│   └── __init__.py
├── docs/
│   └── adr/
│       └── 0001-initial-decisions.md
├── .github/
│   └── workflows/
│       └── ci.yml
├── .gitignore
├── pyproject.toml
├── README.md
└── CONTRIBUTING.md
```

## Configuration

Run `scaffoldr config init` to create:
`~/.scaffoldr/config.toml`:
```toml
author = "Your Name"
github_username = "yourusername"
license = "MIT"
python_version = "3.11"
default_private = false
github_token = "ghp_..."
required_reviewers = 1
use_ssh = true
```

| Field              | Default | Description                     |
|--------------------|---------|---------------------------------|
| author             | ""      | Used in generated files         |
| github_username    | ""      | GitHub username for API calls   |
| license            | MIT     | License in pyproject.toml       |
| python_version     | 3.10    | Python version in CI, pyproject |
| default_private    | false   | Private repos by default        |
| github_token       | ""      | GitHub personal access token    |
| required_reviewers | 1       | PR reviewers required on main   |
| use_ssh            | true    | SSH remote, false for HTTPS     |

## GitHub token

Generate a classic token at 
```GitHub -> Settings -> Developer settings ->  
Personal access token -> Tokens (classic)```.

Check the top-level `repo` scope.

Set it via env var or config:
```bash
export SCAFFOLDR_GITHUB_TOKEN=ghp_...
# or
scaffoldr config init
```

## Commands
```
scaffoldr new <name>        Scaffold locally + GitHub
scaffoldr init <name>       Scaffold locally only
scaffoldr config init       Create config interactively
scaffoldr config show       Print current config
scaffoldr issues create     Create issues on existing repo
```

## Issue templates  

scaffoldr ships with default issues every project needs.
Override or extend them in `~/.scaffoldr/issues.toml`:
```toml
[[issue]]
title = "feat: my custom issue"
body = """
## Summary
Description here.

## Acceptance criteria
- [ ] Item one
"""
```

User templates override built-in defaults by title.
New titles are added alongside the defaults.

## Development
```bash
git clone https://github.com/mg4603/scaffoldr.git
cd scaffoldr
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/ -v
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for branch naming,
commit format, and PR process.

## Architecture decisions

All architectural decisions are documented in 
[docs/adr](docs/adr).

## License

MIT - mg4603
