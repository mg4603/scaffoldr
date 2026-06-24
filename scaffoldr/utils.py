from collections.abc import Callable
from pathlib import Path
from subprocess import run as subprocess_run

from typer import Abort as typer_abort
from typer import echo as typer_echo

from scaffoldr.exceptions import GitError, LocalError
from scaffoldr.template_handler import (
    Template,
    load_template,
    render_template,
    resolve_template_path,
)
from scaffoldr.user_config import (
    CONFIG_DIR,
    USER_DEFINED_TEMPLATES_PATH,
    Config,
)


def _git(args: list[str], cwd: Path) -> None:
    result = subprocess_run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise GitError(f"git error: {result.stderr.strip()}")


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


def build_scaffold_variables(
    project_name: str, cfg: Config
) -> dict[str, str]:
    return {
        "project_name": project_name,
        "author": cfg.author,
        "python_version": cfg.python_version,
        "license_": cfg.license,
    }


def dry_run_scaffold(
    project_name: str,
    template_name: str,
    path: Path,
    progress: Callable[[str], None] = lambda _: None,
) -> None:
    cfg = Config.load()

    root = path / project_name

    if root.exists():
        raise LocalError(f"Error: {root} already exists.")

    scaffold_variables = build_scaffold_variables(
        project_name, cfg
    )

    template_path = resolve_template_path(template_name)
    template: Template = load_template(template_path)
    rendered_template = render_template(
        template, scaffold_variables
    )

    for path_str, _ in rendered_template.items():
        progress(f"[dry-run] Would create: {(root / path_str)}")

    # git
    progress(f"[dry-run] @{root}: git init")
    progress(f"[dry-run] @{root}: git add .")
    progress(
        f'[dry-run] @{root}: git commit -m "chore: '
        'initial scaffold"'
    )
