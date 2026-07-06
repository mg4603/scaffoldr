from pathlib import Path
from tomllib import TOMLDecodeError

import pytest

from scaffoldr.exceptions import TemplateError
from scaffoldr.template_handler import (
    Template,
    get_description,
    load_template,
    render_template,
    resolve_template_path,
    validate_template,
)


@pytest.fixture
def make_raise(monkeypatch):
    def _make(target, exception):
        monkeypatch.setattr(
            target,
            lambda *a, **kw: (_ for _ in ()).throw(exception),
        )

    return _make


@pytest.fixture
def raise_on_open(make_raise):
    def _raise(exception):
        make_raise(
            "scaffoldr.template_handler.Path.open", exception
        )

    return _raise


@pytest.fixture
def raise_on_toml_load(make_raise):
    def _raise(exception):
        make_raise(
            "scaffoldr.template_handler.toml_load", exception
        )

    return _raise


@pytest.fixture
def mock_template_paths(tmp_path, monkeypatch):
    user_templates = tmp_path / "user"
    builtin_templates = tmp_path / "builtin"

    user_file = make_template_file(
        user_templates, "foo.toml", "user"
    )
    builtin_file = make_template_file(
        builtin_templates, "foo1.toml", "builtin"
    )

    monkeypatch.setattr(
        "scaffoldr.template_handler.USER_DEFINED_TEMPLATES_PATH",
        user_templates,
    )
    monkeypatch.setattr(
        "scaffoldr.template_handler.BUILTIN_TEMPLATES_PATH",
        builtin_templates,
    )
    return (user_file, builtin_file)


def make_template_file(path: Path, file: str, content: str):
    path.mkdir(parents=True, exist_ok=True)
    file_path = path / file
    file_path.write_text(content)
    return file_path


def test_find_user_template_first_during_resolution(
    tmp_path, monkeypatch, mock_template_paths
):
    user_file, _ = mock_template_paths
    result = resolve_template_path("foo")
    assert result == user_file


def test_falls_back_to_builtin_during_resolution(
    tmp_path, monkeypatch, mock_template_paths
):
    _, builtin_file = mock_template_paths
    result = resolve_template_path("foo1")
    assert result == builtin_file


def test_template_not_found_during_resolution(
    tmp_path, monkeypatch, mock_template_paths
):
    with pytest.raises(
        TemplateError, match="Template 'foo2' not found"
    ):
        resolve_template_path("foo2")


def test_template_not_found_during_load(tmp_path):
    template = tmp_path / "foo"

    with pytest.raises(
        TemplateError, match="Template file not found: foo"
    ):
        load_template(template)


def test_permission_error_during_load(tmp_path, raise_on_open):
    template = make_template_file(
        tmp_path, "foo", 'description="sample template"'
    )
    _ = raise_on_open(PermissionError("read denied"))

    with pytest.raises(
        TemplateError,
        match="Permission denied reading template: foo",
    ):
        load_template(template)


def test_toml_decode_error_during_load(
    tmp_path, raise_on_toml_load
):
    template = make_template_file(
        tmp_path, "foo", 'description = "sample template"'
    )
    _ = raise_on_toml_load(
        TOMLDecodeError("simulated decode error")
    )

    with pytest.raises(
        TemplateError,
        match=(
            "Invalid TOML in template file foo: "
            "simulated decode error"
        ),
    ):
        load_template(template)


def test_os_error_during_load(tmp_path, raise_on_toml_load):
    template = make_template_file(
        tmp_path, "foo", 'description = "sample template file"'
    )
    _ = raise_on_toml_load(OSError("simulated OSError"))

    with pytest.raises(
        TemplateError,
        match=(
            "Failed to read template file foo: "
            "simulated OSError"
        ),
    ):
        load_template(template)


def test_missing_key_during_load(tmp_path):
    template = make_template_file(
        tmp_path, "foo", 'description = "sample template file"'
    )

    with pytest.raises(
        TemplateError,
        match=(
            "Missing required key in template file foo: files"
        ),
    ):
        load_template(template)


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


def test_success_during_get_description(tmp_path, monkeypatch):
    template = make_template_file(
        tmp_path, "foo.toml", 'description="sample template"'
    )
    result = get_description(template)
    assert result == "sample template"


def test_file_not_found_during_get_description(
    tmp_path, monkeypatch
):
    template = tmp_path / "foo.toml"

    with pytest.raises(
        TemplateError, match="Template file not found: foo"
    ):
        get_description(template)


def test_permission_error_during_get_description(
    tmp_path, monkeypatch, raise_on_open
):
    template = make_template_file(
        tmp_path, "foo.toml", 'description="sample template"'
    )
    _ = raise_on_open(PermissionError("simulated read denial"))

    with pytest.raises(
        TemplateError,
        match="Permission denied reading template: foo",
    ):
        get_description(template)


def test_toml_decode_error_during_get_description(
    tmp_path, monkeypatch, raise_on_toml_load
):
    template = make_template_file(
        tmp_path, "foo.toml", "sample template"
    )
    _ = raise_on_toml_load(
        TOMLDecodeError("simulated toml decode error"),
    )

    with pytest.raises(
        TemplateError,
        match=(
            "Invalid TOML in template file foo: "
            "simulated toml decode error"
        ),
    ):
        get_description(template)


def test_os_error_during_get_description(
    tmp_path, monkeypatch, raise_on_toml_load
):
    template = make_template_file(
        tmp_path, "foo.toml", "sample template"
    )
    _ = raise_on_toml_load(OSError("simulated os error"))

    with pytest.raises(
        TemplateError,
        match=(
            "Failed to read template file foo: "
            "simulated os error"
        ),
    ):
        get_description(template)


def test_description_missing_in_get_description(
    tmp_path, monkeypatch
):
    template = make_template_file(
        tmp_path, "foo.toml", 'foo="bar"'
    )

    with pytest.raises(
        TemplateError,
        match="Missing 'description' in template file foo",
    ):
        get_description(template)
