from __future__ import annotations

import subprocess
from pathlib import Path

import typer

from scaffoldr.config import Config
from scaffoldr.templates import (
    adr_template,
    contributing,
    github_actions_ci,
    gitignore,
    pyproject,
    readme,
)


def _git(args: list[str], cwd: Path) -> None:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        typer.echo(
            f"git error: {result.stderr.strip()}", err=True
        )
        raise typer.Exit(code=1)


def scaffold(project_name: str, path: Path) -> None:
    """
    Create a new project at path/project_name with
    opinionated folder structure and initial git commit
    """
    cfg = Config.load()
    root = path / project_name

    if root.exists():
        typer.echo(f"Error: {root} already exists.", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"Creating project at {root} ...")

    # folders
    (root / project_name).mkdir(parents=True)
    (root / "tests").mkdir()
    (root / "docs" / "adr").mkdir(parents=True)
    (root / ".github" / "workflows").mkdir(parents=True)

    # files
    (root / "README.md").write_text(
        readme(project_name, cfg.author)
    )
    (root / "CONTRIBUTING.md").write_text(
        contributing(project_name)
    )
    (root / "pyproject.toml").write_text(
        pyproject(
            project_name,
            cfg.author,
            cfg.python_version,
            cfg.license,
        )
    )
    (
        root / "docs" / "adr" / "0001-initial-decisions.md"
    ).write_text(adr_template(project_name))
    (root / ".gitignore").write_text(gitignore())
    (root / "tests" / "__init__.py").write_text("")
    (root / project_name / "__init__.py").write_text("")
    (root / ".github" / "workflows" / "ci.yml").write_text(
        github_actions_ci(project_name, cfg.python_version)
    )

    # git
    _git(["init"], cwd=root)
    _git(["add", "."], cwd=root)
    _git(["commit", "-m", "chore: initial scaffold"], cwd=root)

    typer.echo(f"Done. Project ready at {root}")
