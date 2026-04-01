# Contributing to scaffoldr

## Development Setup

1. Clone the repo
```bash
git clone https://github.com/mg4603/scaffoldr.git
cd scaffoldr
```

2. Create and activate a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies
```bash
pip install -e ".[dev]"
```

## Running Tests
```bash
pytest
```

## Branch Conventions
- Never commit directly to `main`
- Branch naming: ``<type>/<short-description>``
  - Examples: `feat/add-docker-support`,
    `fix/config-parse-error`

## Commit Conventions
Follow [Conventional Commits](https://conventionalcommits.org):

- `feat:` - new feature
- `fix:` - new bug
- `docs:` - documentation only
- `refactor:` - code change, no feature or fix
- `test:` - adding or updating tests
- `chore:` - maintenance, deps, config

One logical unit per commit. Keep messages concise.

## Pull Requests
- Every PR must reference an issue: `Closes: #N`
- PRs go into main via rebase + merge
- All checks must pass before merging

## Reporting Issues
Open an issue on GitHub with:
- What you expected to happen
- What actually happened
- Steps to reproduce
- Your OS and Python version
