from typing import Optional

from typer import Abort as typer_abort
from typer import Option as typer_option
from typer import Typer
from typer import confirm as typer_confirm
from typer import echo as typer_echo
from typer import prompt as typer_prompt

from scaffoldr.user_config import (
    CONFIG_FILE,
    DEFAULT_LICENSE,
    DEFAULT_PYTHON_VERSION,
    Config,
)

app = Typer()


@app.command()
def init(
    author: Optional[str] = typer_option(
        None, help="Author name"
    ),
    github_username: Optional[str] = typer_option(
        None, help="GitHub username"
    ),
    license: Optional[str] = typer_option(None, help="License"),
    python_version: Optional[str] = typer_option(
        None, help="Python version"
    ),
    default_private: Optional[bool] = typer_option(
        None, help="Private repos by default?"
    ),
    github_token: Optional[str] = typer_option(
        None, help="GitHub token (leave blank to skip)"
    ),
    required_reviewers: Optional[int] = typer_option(
        None, help="Required PR reviewers"
    ),
    use_ssh: Optional[bool] = typer_option(
        None, help="Use SSH for git remote?"
    ),
) -> None:
    """Create ~/.config/scaffoldr/config.toml interactively."""
    if CONFIG_FILE.exists():
        overwrite = typer_confirm(
            f"{CONFIG_FILE} already exists. Overwrite?"
        )
        if not overwrite:
            raise typer_abort()

    if author is None:
        author = typer_prompt("Author name")

    if github_username is None:
        github_username = typer_prompt("GitHub username")

    if license is None:
        license = typer_prompt(
            "License", default=DEFAULT_LICENSE
        )

    if python_version is None:
        python_version = typer_prompt(
            "Python version",
            default=DEFAULT_PYTHON_VERSION,
        )

    if default_private is None:
        default_private = typer_prompt(
            "Private repos by default?", default=False
        )

    if github_token is None:
        github_token = typer_prompt(
            "GitHub token (leave blank to skip)", default=""
        )

    if required_reviewers is None:
        required_reviewers = typer_prompt(
            "Required PR reviewers", default=1
        )

    if use_ssh is None:
        use_ssh = typer_prompt(
            "Use SSH for git remote?", default=True
        )

    cfg = Config(
        author=author or "",
        github_username=github_username or "",
        python_version=python_version,
        license=license,
        default_private=default_private,
        github_token=github_token or "",
        required_reviewers=required_reviewers,
        use_ssh=use_ssh,
    )
    cfg.write()
    typer_echo(f"Config written to {CONFIG_FILE}.")
