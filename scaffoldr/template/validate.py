from pathlib import Path

from typer import Argument as typer_argument
from typer import Exit as typer_exit
from typer import Typer
from typer import echo as typer_echo

from scaffoldr.exceptions import TemplateError
from scaffoldr.template_handler import validate_template

app = Typer()


@app.command("validate")
def validate_cmd(
    path: Path = typer_argument(
        ..., help="Path to template to validate"
    ),
):
    try:
        result = validate_template(path)
    except TemplateError as e:
        typer_echo(e)
        raise typer_exit(code=1)

    all_fields_pass = True
    for field, passed in result:
        if passed:
            status = "[PASS] "
        else:
            all_fields_pass = False
            status = "[FAIL] "
        typer_echo(status + field)

    if not all_fields_pass:
        raise typer_exit(code=1)
