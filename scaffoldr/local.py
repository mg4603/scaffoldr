from __future__ import annotations

import subprocess
from pathlib import Path

import typer

from scaffoldr.template_handler import (
    Template,
    load_template,
    render_template,
    resolve_template_path,
)
from scaffoldr.user_config import Config


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


def scaffold(
    project_name: str, template_name: str, path: Path
) -> None:
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

    scaffold_variables = {
        "project_name": project_name,
        "author": cfg.author,
        "python_version": cfg.python_version,
        "license_": cfg.license,
    }

    template_path = resolve_template_path(template_name)
    template: Template = load_template(template_path)
    rendered_template = render_template(
        template, scaffold_variables
    )

    for path_str, content in rendered_template.items():
        path = Path(path_str)
        (root / path.parent).mkdir(parents=True, exist_ok=True)
        (root / path).write_text(content)

    # git
    _git(["init"], cwd=root)
    _git(["add", "."], cwd=root)
    _git(["commit", "-m", "chore: initial scaffold"], cwd=root)

    typer.echo(f"Done. Project ready at {root}")
