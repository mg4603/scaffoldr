from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional

import typer

from scaffoldr.config import app as config_app
from scaffoldr.exceptions import TemplateError
from scaffoldr.github import (
    _get_token,
    get_authenticated_user,
    get_client,
)
from scaffoldr.github import (
    create_repo as _create_repo,
)
from scaffoldr.issues import create_issues as _create_issues
from scaffoldr.local import scaffold as _scaffold
from scaffoldr.protection import (
    protect_branch as _protect_branch,
)
from scaffoldr.user_config import (
    Config,
)
from scaffoldr.utils import check_legacy_config, ensure_dirs

app = typer.Typer(
    name="scaffoldr",
    help="Scaffold new projects with opinionated structure.",
    no_args_is_help=True,
)


app.add_typer(config_app, name="config")


issues_app = typer.Typer(
    name="issues", help="Manage GitHub issues."
)
app.add_typer(issues_app)


@app.callback()
def app_callback(ctx: typer.Context):
    ensure_dirs()
    if ctx.invoked_subcommand == "config":
        return
    check_legacy_config()


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
    template: str = typer.Option(
        "default", help="default template"
    ),
    path: Path = typer.Option(
        Path("."), help="Where to create the project"
    ),
) -> None:
    """Scaffold a new project locally."""
    try:
        _scaffold(project_name, template, path)
    except TemplateError as e:
        typer.echo(e, err=True)
        raise typer.Exit(code=1)


@app.command("new")
def new(
    project_name: str = typer.Argument(
        ..., help="Name of the new project"
    ),
    description: str = typer.Option(
        "", help="GitHub repo description"
    ),
    private: Optional[bool] = typer.Option(
        None, help="Override default_private from config"
    ),
    template: str = typer.Option(
        "default", help="default template"
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
    is_private = (
        private if private is not None else cfg.default_private
    )
    try:
        _scaffold(project_name, template, path)
    except TemplateError as e:
        typer.echo(e, err=True)
        raise typer.Exit(code=1)

    typer.echo("Creating GitHub repo...")
    repo = _create_repo(
        name=project_name,
        description=description,
        private=is_private,
    )

    root = path / project_name
    ssh_url = repo["ssh_url"]
    clone_url = repo["clone_url"]

    if cfg.use_ssh:
        remote_url = ssh_url
    else:
        token = _get_token()
        remote_url = clone_url.replace(
            "https://",
            f"https://{cfg.github_username}:{token}@",
        )

    subprocess.run(
        ["git", "remote", "add", "origin", remote_url],
        cwd=root,
        check=True,
    )
    subprocess.run(
        ["git", "push", "-u", "origin", "main"],
        cwd=root,
        check=True,
    )

    if not cfg.use_ssh:
        subprocess.run(
            ["git", "remote", "set-url", "origin", clone_url],
            cwd=root,
            check=True,
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
