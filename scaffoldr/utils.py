from pathlib import Path

from typer import Abort as typer_abort
from typer import echo as typer_echo

from scaffoldr.user_config import (
    CONFIG_DIR,
    USER_DEFINED_TEMPLATES_PATH,
)


def check_legacy_config():
    legacy_path = Path.home() / ".scaffoldr"
    if legacy_path.exists():
        typer_echo(
            f"Config directory changed from {legacy_path} to"
            f" {CONFIG_DIR}."
            "\nRun `scaffoldr config migrate` to move existing"
            " config.",
            err=True,
        )
        raise typer_abort()


def ensure_dirs():
    USER_DEFINED_TEMPLATES_PATH.mkdir(
        parents=True, exist_ok=True
    )
