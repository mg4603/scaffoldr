from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from scaffoldr.exceptions import LocalError
from scaffoldr.template_handler import (
    Template,
    load_template,
    render_template,
    resolve_template_path,
)
from scaffoldr.user_config import Config
from scaffoldr.utils import _git, build_scaffold_variables


def scaffold(
    project_name: str,
    template_name: str,
    path: Path,
    progress: Callable[[str], None] = lambda _: None,
) -> None:
    """
    Create a new project at path/project_name with
    opinionated folder structure and initial git commit
    """
    cfg = Config.load()
    root = path / project_name

    if root.exists():
        raise LocalError(f"Error: {root} already exists.")

    progress(f"Creating project at {root} ...")

    scaffold_variables = build_scaffold_variables(
        project_name, cfg
    )

    template_path = resolve_template_path(template_name)
    template: Template = load_template(template_path)
    rendered_template = render_template(
        template, scaffold_variables
    )

    for path_str, content in rendered_template.items():
        path = Path(path_str)
        (root / path.parent).mkdir(parents=True, exist_ok=True)
        (root / path).write_text(content)

    # git
    _git(["init"], cwd=root)
    _git(["add", "."], cwd=root)
    _git(["commit", "-m", "chore: initial scaffold"], cwd=root)

    progress(f"Done. Project ready at {root}")
