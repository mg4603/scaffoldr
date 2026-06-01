from importlib.resources import files
from pathlib import Path
from tomllib import TOMLDecodeError
from tomllib import load as toml_load
from typing import Any, TypedDict

from scaffoldr.exceptions import TemplateError
from scaffoldr.user_config import USER_DEFINED_TEMPLATES_PATH

BUILTIN_TEMPLATES_PATH = Path(
    files("scaffoldr").joinpath("templates")
)


class TemplateFile(TypedDict):
    path: str
    content: str


class Template(TypedDict):
    description: str
    files: list[TemplateFile]


def resolve_template_path(name: str) -> Path:
    if USER_DEFINED_TEMPLATES_PATH.exists():
        for f in USER_DEFINED_TEMPLATES_PATH.iterdir():
            if f.is_file() and f.stem == name:
                return f

    for f in BUILTIN_TEMPLATES_PATH.iterdir():
        if f.is_file() and f.stem == name:
            return f

    raise TemplateError(f"Template '{name}' not found.")


def load_template(path: Path) -> Template:
    try:
        with path.open("rb") as f:
            data: dict[str, Any] = toml_load(f)
    except FileNotFoundError:
        raise TemplateError(
            f"Template file not found: {path.stem}"
        )
    except PermissionError:
        raise TemplateError(
            f"Permission denied reading template: {path.stem}",
        )
    except TOMLDecodeError as e:
        raise TemplateError(
            f"Invalid TOML in template file {path.stem}: {e}",
        ) from e
    except OSError as e:
        raise TemplateError(
            f"Failed to read template file {path.stem}: {e}",
        ) from e

    try:
        description: str = data["description"]
        files: list[TemplateFile] = data["files"]
    except KeyError as e:
        raise TemplateError(
            "Missing required key in template file "
            f"{path.stem}: {e.args[0]}"
        ) from e

    return {"description": description, "files": files}


def render_template(
    template: Template, variables: dict[str, str]
) -> dict[str, str]:
    result = {}

    try:
        for file in template["files"]:
            path = file["path"].format_map(variables)
            content = file["content"].format_map(variables)
            result[path] = content
    except KeyError as e:
        raise TemplateError(
            f"Missing variable in template: {e}"
        ) from e
    except ValueError as e:
        raise TemplateError(
            f"Template rendering failed: {e}"
        ) from e

    return result


def get_description(path: Path) -> str:
    try:
        with path.open("rb") as f:
            data: dict[str, Any] = toml_load(f)
            return data["description"]
    except FileNotFoundError:
        raise TemplateError(
            f"Template file not found: {path.stem}"
        )
    except PermissionError:
        raise TemplateError(
            f"Permission denied reading template: {path.stem}"
        )
    except TOMLDecodeError as e:
        raise TemplateError(
            f"Invalid TOML in template file {path.stem}: {e}"
        ) from e
    except OSError as e:
        raise TemplateError(
            f"Failed to read template file {path.stem}: {e}"
        ) from e
    except KeyError:
        raise TemplateError(
            "Missing 'description' in template file "
            f"{path.stem}"
        )
