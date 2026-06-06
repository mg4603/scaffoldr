from pathlib import Path
from tomllib import TOMLDecodeError
from unittest.mock import patch

import pytest

from scaffoldr.exceptions import TemplateError
from scaffoldr.template_handler import (
    load_template,
    resolve_template_path,
)


def test_find_user_template_first_during_resolution(
    tmp_path, monkeypatch
):
    user_templates = tmp_path / "user"
    builtin_templates = tmp_path / "builtin"

    user_templates.mkdir()
    builtin_templates.mkdir()

    user_file = user_templates / "foo.toml"
    user_file.write_text("user")

    monkeypatch.setattr(
        "scaffoldr.template_handler.USER_DEFINED_TEMPLATES_PATH",
        user_templates,
    )
    monkeypatch.setattr(
        "scaffoldr.template_handler.BUILTIN_TEMPLATES_PATH",
        builtin_templates,
    )

    result = resolve_template_path("foo")

    assert result == user_file


def test_falls_back_to_builtin_during_resolution(
    tmp_path, monkeypatch
):
    user_templates = tmp_path / "user"
    builtin_templates = tmp_path / "builtin"

    user_templates.mkdir()
    builtin_templates.mkdir()

    user_file = user_templates / "foo.toml"
    user_file.write_text("user")

    builtin_file = builtin_templates / "foo1.toml"
    builtin_file.write_text("builtin")

    monkeypatch.setattr(
        "scaffoldr.template_handler.USER_DEFINED_TEMPLATES_PATH",
        user_templates,
    )
    monkeypatch.setattr(
        "scaffoldr.template_handler.BUILTIN_TEMPLATES_PATH",
        builtin_templates,
    )
    result = resolve_template_path("foo1")

    assert result == builtin_file


def test_template_not_found_during_resolution(
    tmp_path, monkeypatch
):
    user_templates = tmp_path / "user"
    builtin_templates = tmp_path / "builtin"

    user_templates.mkdir()
    builtin_templates.mkdir()

    monkeypatch.setattr(
        "scaffoldr.template_handler.USER_DEFINED_TEMPLATES_PATH",
        user_templates,
    )
    monkeypatch.setattr(
        "scaffoldr.template_handler.BUILTIN_TEMPLATES_PATH",
        builtin_templates,
    )

    with pytest.raises(
        TemplateError, match="Template 'foo' not found"
    ):
        resolve_template_path("foo")
