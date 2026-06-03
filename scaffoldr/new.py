from pathlib import Path
from subprocess import run as subprocess_run
from typing import Optional

from typer import Argument as typer_argument
from typer import Exit as typer_exit
from typer import Option as typer_option
from typer import Typer
from typer import echo as typer_echo

from scaffoldr.exceptions import (
    GitError,
    GitHubError,
    LocalError,
    TemplateError,
)
from scaffoldr.github import (
    _get_token,
    get_authenticated_user,
    get_client,
)
from scaffoldr.github import (
    create_repo as _create_repo,
)
from scaffoldr.issue_handler import (
    create_issues as _create_issues,
)
from scaffoldr.local import scaffold as _scaffold
from scaffoldr.protection import (
    protect_branch as _protect_branch,
)
from scaffoldr.user_config import Config

app = Typer(
    help=(
        "Scaffold a new project locally and create a "
        "GitHub repo for it."
    )
)


@app.command("new")
def new(
    project_name: str = typer_argument(
        ..., help="Name of the new project"
    ),
    description: str = typer_option(
        "", help="GitHub repo description"
    ),
    private: Optional[bool] = typer_option(
        None, help="Override default_private from config"
    ),
    template: str = typer_option(
        "default", help="default template"
    ),
    path: Path = typer_option(
        Path("."), help="Where to create the project locally"
    ),
    protect: bool = typer_option(
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
        _scaffold(project_name, template, path, typer_echo)

        typer_echo("Creating GitHub repo...")
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

        subprocess_run(
            ["git", "remote", "add", "origin", remote_url],
            cwd=root,
            check=True,
        )
        subprocess_run(
            ["git", "push", "-u", "origin", "main"],
            cwd=root,
            check=True,
        )

        if not cfg.use_ssh:
            subprocess_run(
                [
                    "git",
                    "remote",
                    "set-url",
                    "origin",
                    clone_url,
                ],
                cwd=root,
                check=True,
            )

        with get_client() as client:
            owner = get_authenticated_user(client)

            typer_echo("Creating issues...")
            _create_issues(
                owner, project_name, client, typer_echo
            )

            if protect:
                typer_echo("Setting branch protection...")
                _protect_branch(
                    owner,
                    project_name,
                    client,
                    required_reviewers=cfg.required_reviewers,
                )
        typer_echo(f"Repo ready: {repo['html_url']}")
    except (
        TemplateError,
        GitHubError,
        LocalError,
        GitError,
    ) as e:
        typer_echo(e, err=True)
        raise typer_exit(code=1)
