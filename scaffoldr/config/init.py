from typing import Optional

from typer import Abort as typer_abort
from typer import Option as typer_option
from typer import Typer
from typer import confirm as typer_confirm
from typer import echo as typer_echo

from scaffoldr.user_config import (
    CONFIG_FILE,
    DEFAULT_LICENSE,
    DEFAULT_PYTHON_VERSION,
    Config,
)

app = Typer()


@app.callback()
def check_config_existence():
    if CONFIG_FILE.exists():
        overwrite = typer_confirm(
            f"{CONFIG_FILE} already exists. Overwrite?"
        )
        if not overwrite:
            raise typer_abort()


@app.command()
def init(
    author: Optional[str] = typer_option(
        None, prompt="Author name"
    ),
    github_username: Optional[str] = typer_option(
        None, prompt="GitHub username"
    ),
    license: str = typer_option(
        DEFAULT_LICENSE, prompt="License"
    ),
    python_version: str = typer_option(
        DEFAULT_PYTHON_VERSION, prompt="Python version"
    ),
    default_private: bool = typer_option(
        False, prompt="Private repos by default?"
    ),
    github_token: str = typer_option(
        "", prompt="GitHub token (leave blank to skip)"
    ),
    required_reviewers: int = typer_option(
        1, prompt="Required PR reviewers"
    ),
    use_ssh: bool = typer_option(
        True, prompt="Use SSH for git remote?"
    ),
) -> None:
    """Create ~/.config/scaffoldr/config.toml interactively."""
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
