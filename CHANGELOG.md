# Changelog

All notable changes to this project will be documented in this 
file.

This format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-04-01

## Added
- User config file support
- `scaffoldr init` - scaffold a new project locally
- `scaffoldr new` - scaffold locally and create GitHub repo, 
  issues, and branch protection via API
- SSH support for git remote by default
- CI workflow generation during `scaffoldr new`
- CI setup using GitHub Actions
- ADR for typer and httpx dependencies
- Full README with CLI demo GIF
- CONTRIBUTING.md

## Fixed
- Explicilty install pytest and ruff in generated CI
- Use optional dependencies in generated `pyproject.toml`
- Provide `required_status_checks` in branch protection API call
- Simplify branch protection error handling


## [0.2.0] - 2026-07-11

## Added
- `scaffoldr template list` command
- `scaffoldr template validate` command
- User-defined project structure templates
- `--template` flag on `new` and `init` commands
- `--dry-run` flag on `new` and `init` commands
- Config path migrated to XDG-compliant location

## Fixed
- `config init` now checks file existence before prompting
- `config init` callback replaced with explicit prompts in
  command body
- Updated installation instruction in README

## Changed
- Restructured `main.py` into per-command files
- Removed `typer.echo` progress feedback from business logic
- Changed `create_issues` return type from `list[dict]` to `None`
- Moved `_git` helper to `utils.py`
- Extracted GitHub interaction logic from `new.py` to `github.py`
