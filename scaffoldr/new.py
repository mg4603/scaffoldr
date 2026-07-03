from pathlib import Path
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
    dry_run_github_ops,
    github_ops,
)
from scaffoldr.local import (
    dry_run_scaffold,
)
from scaffoldr.local import (
    scaffold as _scaffold,
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
    dry_run: bool = typer_option(
        False,
        help=(
            "Print what would happen without filesystem "
            "changes or calling GitHub."
        ),
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
        if dry_run:
            dry_run_scaffold(
                project_name, template, path, typer_echo
            )

            dry_run_github_ops(
                project_name, protect, cfg.use_ssh, typer_echo
            )

        else:
            _scaffold(project_name, template, path, typer_echo)

            github_ops(
                project_name,
                description,
                is_private,
                protect,
                cfg,
                path,
                typer_echo,
            )
    except (
        TemplateError,
        GitHubError,
        LocalError,
        GitError,
    ) as e:
        typer_echo(e, err=True)
        raise typer_exit(code=1)
