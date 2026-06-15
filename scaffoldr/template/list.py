from pathlib import Path

from typer import Typer
from typer import echo as typer_echo

from scaffoldr.template_handler import (
    BUILTIN_TEMPLATES_PATH,
    get_description,
)
from scaffoldr.user_config import USER_DEFINED_TEMPLATES_PATH

app = Typer()


@app.command("list")
def list_cmd():
    typer_echo("Built-in")
    found = False
    for t in list_templates(BUILTIN_TEMPLATES_PATH):
        found = True
        typer_echo(t)

    if found:
        typer_echo("")
    else:
        typer_echo("(none)\n")

    typer_echo(f"User ({USER_DEFINED_TEMPLATES_PATH})")
    found = False
    for t in list_templates(USER_DEFINED_TEMPLATES_PATH):
        found = True
        typer_echo(t)

    if not found:
        typer_echo("(none)")


def list_templates(dir_path: Path) -> list[str]:
    template_list = []
    for path in dir_path.iterdir():
        if path.is_file():
            template_list.append(
                f"{path.stem}   {get_description(path)}"
            )

    return template_list
