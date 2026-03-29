from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional

import typer

from scaffoldr.config import (
    CONFIG_FILE,
    DEFAULT_LICENSE,
    DEFAULT_PYTHON_VERSION,
    Config,
)
from scaffoldr.github import (
    create_repo as _create_repo,
)
from scaffoldr.github import (
    get_authenticated_user,
    get_client,
)
from scaffoldr.issues import create_issues as _create_issues
from scaffoldr.local import scaffold as _scaffold
from scaffoldr.protection import protect_branch as _protect_branch

app = typer.Typer(
    name="scaffoldr",
    help="Scaffold new projects with opinionated structure.",
    no_args_is_help=True,
)

config_app = typer.Typer(name="config", help="Manage scaffoldr config.")
app.add_typer(config_app)

issues_app = typer.Typer(name="issues", help="Manage GitHub issues.")
app.add_typer(issues_app)


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
    github_token: str = typer.Option(
        "", prompt="GitHub token (leave blank to skip)"
    ),
    required_reviewers: int = typer.Option(
        1, prompt="Required PR reviewers"
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
        github_token=github_token or "",
        required_reviewers=required_reviewers,
    )
    cfg.write()
    typer.echo(f"Config written to {CONFIG_FILE}.")


@config_app.command("show")
def config_show() -> None:
    """Print current config values."""
    cfg = Config.load()
    typer.echo(f"author             = {cfg.author!r}")
    typer.echo(f"github_username    = {cfg.github_username!r}")
    typer.echo(f"python_version     = {cfg.python_version!r}")
    typer.echo(f"license            = {cfg.license!r}")
    typer.echo(f"default_private    = {cfg.default_private}")
    typer.echo(f"required_reviewers = {cfg.required_reviewers}")
    masked = (
        cfg.github_token[:4] + "****"
        if cfg.github_token
        else "(not set)"
    )
    typer.echo(f"github_token       = {masked}")


@issues_app.command("create")
def issues_create(
    repo: str = typer.Argument(
        ..., help="Repo name (owner/repo or just repo)"
    ),
) -> None:
    """Create default issues on an existing GitHub repo."""
    with get_client() as client:
        if "/" in repo:
            owner, repo_name = repo.split("/", 1)
        else:
            owner = get_authenticated_user(client)
            repo_name = repo

        typer.echo(f"Creating issues on {owner}/{repo_name}...")
        created = _create_issues(owner, repo_name, client)
        typer.echo(f"Done. {len(created)} issues created.")


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


@app.command("new")
def new(
    project_name: str = typer.Argument(
        ..., help="Name of the new project"
    ),
    description: str = typer.Option("", help="GitHub repo description"),
    private: Optional[bool] = typer.Option(
        None, help="Override default_private from config"
    ),
    path: Path = typer.Option(
        Path("."), help="Where to create the project locally"
    ),
    protect: bool = typer.Option(
        True, help="Enable branch protection on main."
    ),
) -> None:
    """
    Scaffold a new project locally and create a
    GitHub repo for it.
    """
    cfg = Config.load()
    is_private = private if private is not None else cfg.default_private

    _scaffold(project_name, path)

    typer.echo("Creating GitHub repo...")
    repo = _create_repo(
        name=project_name, description=description, private=is_private
    )

    root = path / project_name
    remote_url = repo["clone_url"]
    subprocess.run(
        ["git", "remote", "add", "origin", remote_url],
        cwd=root,
        check=True,
    )
    subprocess.run(
        ["git", "push", "-u", "origin", "main"], cwd=root, check=True
    )

    with get_client() as client:
        owner = get_authenticated_user(client)

        typer.echo("Creating issues...")
        _create_issues(owner, project_name, client)

        if protect:
            typer.echo("Setting branch protection...")
            _protect_branch(
                owner,
                project_name,
                client,
                required_reviewers=cfg.required_reviewers,
            )

    typer.echo(f"Repo ready: {repo['html_url']}")
