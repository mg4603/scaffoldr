from typer import Typer
from typer import echo as typer_echo

from scaffoldr.user_config import Config

app = Typer()


@app.command()
def show() -> None:
    """Print current config values."""
    cfg = Config.load()
    typer_echo(f"author             = {cfg.author!r}")
    typer_echo(f"github_username    = {cfg.github_username!r}")
    typer_echo(f"python_version     = {cfg.python_version!r}")
    typer_echo(f"license            = {cfg.license!r}")
    typer_echo(f"default_private    = {cfg.default_private}")
    typer_echo(f"required_reviewers = {cfg.required_reviewers}")
    typer_echo(f"use_ssh            = {cfg.use_ssh}")
    masked = (
        cfg.github_token[:4] + "****"
        if cfg.github_token
        else "(not set)"
    )
    typer_echo(f"github_token       = {masked}")
