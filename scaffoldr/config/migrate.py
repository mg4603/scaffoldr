from pathlib import Path
from shutil import copy2 as shutil_copy2
from shutil import rmtree as shutil_rmtree

from typer import Abort as typer_abort
from typer import Typer
from typer import confirm as typer_confirm
from typer import echo as typer_echo

from scaffoldr.user_config import CONFIG_DIR

app = Typer()


@app.command()
def migrate() -> None:
    legacy_path = Path.home() / ".scaffoldr"
    if not legacy_path.exists():
        typer_echo("Legacy config does not exist.")
        return

    if CONFIG_DIR.exists():
        overwrite = typer_confirm(
            f"{CONFIG_DIR} already exists. Overwrite?"
        )
        if not overwrite:
            raise typer_abort()

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    for item in legacy_path.rglob("*"):
        relative_path = item.relative_to(legacy_path)
        destination_item = CONFIG_DIR / relative_path

        if item.is_file():
            destination_item.parent.mkdir(
                parents=True, exist_ok=True
            )
            shutil_copy2(item, destination_item)
        else:
            destination_item.mkdir(parents=True, exist_ok=True)

    try:
        shutil_rmtree(legacy_path)
        typer_echo(f"Successfully removed {legacy_path}")
    except PermissionError:
        typer_echo(
            f"Permission denied when removing {legacy_path}",
            err=True,
        )
        raise typer_abort()
    except Exception as e:
        typer_echo(f"Error: {e}", err=True)
        raise typer_abort()

    typer_echo(
        "Config files migrated successfully from "
        f"{legacy_path} to {CONFIG_DIR}"
    )
