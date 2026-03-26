from __future__ import annotations

import typer
from typing import Optional
from pathlib import Path

from scaffoldr.config import (
    Config,
    CONFIG_FILE,
    DEFAULT_LICENSE,
    DEFAULT_PYTHON_VERSION,
)
from scaffoldr.local import scaffold as _scaffold

app = typer.Typer(
    name="scaffoldr",
    help="Scaffold new projects with opinionated structure.",
    no_args_is_help=True,
)

config_app = typer.Typer(name="config", help="Manage scaffoldr config.")
app.add_typer(config_app)


@config_app.command("init")
def config_init(
    author: Optional[str] = typer.Option(None, prompt="Author name"),
    github_username: Optional[str] = typer.Option(
        None, prompt="GitHub username"
    ),
    license: str = typer.Option(DEFAULT_LICENSE, prompt="License"),
    python_version: str = typer.Option(
        DEFAULT_PYTHON_VERSION, prompt="Python version"
    ),
    default_private: bool = typer.Option(
        False, prompt="Private repos by default?"
    ),
) -> None:
    """Create ~/.scaffoldr/config.toml interactively."""
    if CONFIG_FILE.exists():
        overwrite = typer.confirm(
            f"{CONFIG_FILE} already exists. Overwrite?"
        )
        if not overwrite:
            raise typer.Abort()

    cfg = Config(
        author=author or "",
        github_username=github_username or "",
        python_version=python_version,
        license=license,
        default_private=default_private,
    )
    cfg.write()
    typer.echo(f"Config written to {CONFIG_FILE}.")


@config_app.command("show")
def config_show() -> None:
    """Print current config values."""
    cfg = Config.load()
    typer.echo(f"author          = {cfg.author!r}")
    typer.echo(f"github_username = {cfg.github_username!r}")
    typer.echo(f"python_version  = {cfg.python_version!r}")
    typer.echo(f"license         = {cfg.license!r}")
    typer.echo(f"default_private = {cfg.default_private}")


@app.command("init")
def init(
    project_name: str = typer.Argument(
        ..., help="Name of the new project"
    ),
    path: Path = typer.Option(
        Path("."), help="Where to create the project"
    ),
) -> None:
    """Scaffold a new project locally."""
    _scaffold(project_name, path)
