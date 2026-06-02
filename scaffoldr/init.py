from pathlib import Path

from typer import Argument as typer_argument
from typer import Exit as typer_exit
from typer import Option as typer_option
from typer import Typer
from typer import echo as typer_echo

from scaffoldr.exceptions import (
    GitError,
    LocalError,
    TemplateError,
)
from scaffoldr.local import scaffold as _scaffold

app = Typer(help="Scaffold a new project locally.")


@app.command("init")
def init(
    project_name: str = typer_argument(
        ..., help="Name of the new project"
    ),
    template: str = typer_option(
        "default", help="default template"
    ),
    path: Path = typer_option(
        Path("."), help="Where to create the project"
    ),
) -> None:
    """Scaffold a new project locally."""
    try:
        _scaffold(project_name, template, path)
    except (TemplateError, LocalError, GitError) as e:
        typer_echo(e, err=True)
        raise typer_exit(code=1)
