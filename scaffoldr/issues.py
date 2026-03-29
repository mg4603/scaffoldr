from __future__ import annotations

try:
    import tomllib
except ImportError:
    import tomli as tomllib

import typer

from scaffoldr.config import CONFIG_DIR

ISSUES_FILE = CONFIG_DIR / "issues.toml"

DEFAULT_ISSUES: list[dict] = [
    {
        "title": "chore: initial project setup",
        "body": (
            "## Summary\n"
            "Setup project structore, dependencies, and dev\n"
            "environment.\n\n"
            "## Acceptance Criteria\n"
            "- [ ] `pyproject.toml` configured\n"
            "- [ ] venv set up and documented\n"
            "- [ ] README stub in place\n"
        ),
    },
    {
        "title": "chore: setup CI with GitHub Actions",
        "body": (
            "## Summary\n"
            "Add GitHub Actions workflow that runs tests and\n"
            "linting on every push and PR.\n\n"
            "## Acceptance Criteria\n"
            "- [ ] `pytest` runs on push and PR\n"
            "- [ ] `ruff` runs on push and PR\n"
            "- [ ] CI badge added to README\n"
        ),
    },
    {
        "title": "docs: write full README",
        "body": (
            "## Summary\n"
            "Write the production README.\n\n"
            "## Acceptance Criteria\n"
            "- [ ] What the project does and why\n"
            "- [ ] Install instructions\n"
            "- [ ] Usage examples\n"
            "- [ ] Contributing section\n"
        ),
    },
]


def _load_user_issues() -> list[dict]:
    if not ISSUES_FILE.exists():
        return []
    with ISSUES_FILE.open("rb") as f:
        data = tomllib.load(f)
    return data.get("issue", [])


def resolve_templates() -> list[dict]:
    """
    Merge built-in defaults with user templates.
    User templates override defaults by title.
    """
    user_issues = _load_user_issues()
    user_titles = {i["title"] for i in user_issues}
    merged = [
        i for i in DEFAULT_ISSUES if i["title"] not in user_titles
    ]
    merged.extend(user_issues)
    return merged


def create_issues(owner: str, repo: str, client) -> list[dict]:
    """
    Create issues on a GitHub repo using resolved templates.
    Returns list of created issue dicts.
    """
    templates = resolve_templates()
    created = []

    for template in templates:
        response = client.post(
            f"/repos/{owner}/{repo}/issues",
            json={
                "title": template["title"],
                "body": template.get("body", ""),
            },
        )

        if response.status_code == 410:
            typer.echo(
                "Error: issues are disabled on this repo.",
                err=True,
            )
            raise typer.Exit(code=1)

        if response.status_code == 403:
            typer.echo("Error: rate limited by GitHub API.", err=True)
            raise typer.Exit(code=1)

        if not response.is_success:
            typer.echo(
                f"Error: failed to create issue "
                f"'{template['title']}' - "
                f"{response.status_code}",
                err=True,
            )
            raise typer.Exit(code=1)

        issue = response.json()
        created.append(issue)
        typer.echo(f"Created: #{issue['number']} {issue['title']}")

    return created
