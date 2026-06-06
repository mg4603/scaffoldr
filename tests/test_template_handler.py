from pathlib import Path
from tomllib import TOMLDecodeError
from unittest.mock import patch

import pytest

from scaffoldr.exceptions import TemplateError
from scaffoldr.template_handler import (
    Template,
    load_template,
    render_template,
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


def test_template_not_found_during_load(tmp_path):
    template_dir = tmp_path / "templates"
    template_dir.mkdir()

    template_file = template_dir / "foo"

    with pytest.raises(
        TemplateError, match="Template file not found: foo"
    ):
        load_template(template_file)


def test_permission_error_during_load(tmp_path):
    template_dir = tmp_path / "templates"
    template_dir.mkdir()

    template_file = template_dir / "foo"
    template_file.write_text('description="sample template"')

    with patch.object(
        Path, "open", side_effect=PermissionError("read denied")
    ):
        with pytest.raises(
            TemplateError,
            match="Permission denied reading template: foo",
        ):
            load_template(template_file)


def test_toml_decode_error_during_load(tmp_path):
    template_dir = tmp_path / "templates"
    template_dir.mkdir()

    template_file = template_dir / "foo"
    template_file.write_text('description = "sample template"')

    with patch(
        "scaffoldr.template_handler.toml_load",
        side_effect=TOMLDecodeError("simulated decode error"),
    ):
        with pytest.raises(
            TemplateError,
            match=(
                "Invalid TOML in template file foo: "
                "simulated decode error"
            ),
        ):
            load_template(template_file)


def test_os_error_during_load(tmp_path):
    template_dir = tmp_path / "templates"
    template_dir.mkdir()

    template_file = template_dir / "foo"
    template_file.write_text(
        'description = "sample template file"'
    )

    with patch(
        "scaffoldr.template_handler.toml_load",
        side_effect=OSError("simulated OSError"),
    ):
        with pytest.raises(
            TemplateError,
            match=(
                "Failed to read template file foo: "
                "simulated OSError"
            ),
        ):
            load_template(template_file)


def test_missing_key_during_load(tmp_path):
    template_dir = tmp_path / "templates"
    template_dir.mkdir()

    template_file = template_dir / "foo"
    template_file.write_text(
        'description = "sample template file"'
    )

    with pytest.raises(
        TemplateError,
        match=(
            "Missing required key in template file foo: files"
        ),
    ):
        load_template(template_file)


def test_key_error_during_render():
    variables = {"foo": "bar"}
    template: Template = {
        "description": "Sample template",
        "files": [{"path": "{name}.toml", "content": "sample"}],
    }

    with pytest.raises(
        TemplateError,
        match="Missing variable in template: 'name'",
    ):
        render_template(template, variables)


def test_value_error_during_render():
    variables = {"foo": "bar"}
    template: Template = {
        "description": "Sample template",
        "files": [{"path": "{name.toml", "content": "sample"}],
    }

    with pytest.raises(
        TemplateError, match="Template rendering failed: "
    ):
        render_template(template, variables)
