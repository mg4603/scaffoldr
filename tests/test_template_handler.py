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


def test_resolution_find_user_template(mock_template_paths):
    user_file, _ = mock_template_paths
    result = resolve_template_path("foo")
    assert result == user_file


def test_resolution_builtin_fallback(mock_template_paths):
    _, builtin_file = mock_template_paths
    result = resolve_template_path("foo1")
    assert result == builtin_file


def test_resolution_template_not_found(
    tmp_path, mock_template_paths
):
    with pytest.raises(
        TemplateError, match="Template 'foo2' not found"
    ):
        resolve_template_path("foo2")


def test_load_template_not_found(tmp_path):
    template = tmp_path / "foo"
    with pytest.raises(
        TemplateError, match="Template file not found: foo"
    ):
        load_template(template)


def test_load_permission_err(tmp_path, raise_on_open):
    template = make_template_file(tmp_path, "f", 'f="b"')
    _ = raise_on_open(PermissionError("read denied"))

    with pytest.raises(
        TemplateError,
        match="Permission denied reading template: f",
    ):
        load_template(template)


def test_load_toml_decode_err(tmp_path, raise_on_toml_load):
    template = make_template_file(tmp_path, "f", 'f="b"')
    _ = raise_on_toml_load(TOMLDecodeError("simulated"))

    with pytest.raises(
        TemplateError,
        match="Invalid TOML in template file f: simulated",
    ):
        load_template(template)


def test_load_os_err(tmp_path, raise_on_toml_load):
    template = make_template_file(tmp_path, "f", 'f="b"')
    _ = raise_on_toml_load(OSError("simulated"))

    with pytest.raises(
        TemplateError,
        match="Failed to read template file f: simulated",
    ):
        load_template(template)


def test_load_missing_key(tmp_path):
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


def test_render_key_err():
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


def test_render_value_err():
    variables = {"foo": "bar"}
    template: Template = {
        "description": "Sample template",
        "files": [{"path": "{name.toml", "content": "sample"}],
    }

    with pytest.raises(
        TemplateError, match="Template rendering failed: "
    ):
        render_template(template, variables)


def test_get_description_success(tmp_path):
    template = make_template_file(
        tmp_path, "foo.toml", 'description="sample template"'
    )
    result = get_description(template)
    assert result == "sample template"


def test_get_description_file_not_found(tmp_path):
    template = tmp_path / "foo.toml"
    with pytest.raises(
        TemplateError, match="Template file not found: foo"
    ):
        get_description(template)


def test_get_description_permission_err(
    tmp_path, raise_on_open
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


def test_get_description_toml_decode_err(
    tmp_path, raise_on_toml_load
):
    template = make_template_file(tmp_path, "f.toml", "sample")
    _ = raise_on_toml_load(
        TOMLDecodeError("simulated"),
    )

    with pytest.raises(
        TemplateError,
        match="Invalid TOML in template file f: simulated",
    ):
        get_description(template)


def test_get_description_os_err(tmp_path, raise_on_toml_load):
    template = make_template_file(tmp_path, "f.toml", "sample")
    _ = raise_on_toml_load(OSError("simulated"))

    with pytest.raises(
        TemplateError,
        match="Failed to read template file f: simulated",
    ):
        get_description(template)


def test_get_description_description_missing(tmp_path):
    template = make_template_file(tmp_path, "f.toml", 'f="b"')

    with pytest.raises(
        TemplateError,
        match="Missing 'description' in template file f",
    ):
        get_description(template)


def build_template_content(options: dict[str, bool]) -> str:
    template_string = ""

    if options.get("no_desc", False):
        pass
    elif options.get("empty_desc", False):
        template_string += 'description=""\n'
    elif options.get("non_str_desc", False):
        template_string += "description=1234\n"
    else:
        template_string += (
            'description="template description"\n'
        )

    if options.get("unexpected_field", False):
        template_string += 'foo="bar"\n'

    if options.get("no_files", False):
        return template_string

    template_string += "[[files]]\n"
    if options.get("no_path", False):
        pass
    elif options.get("empty_path", False):
        template_string += 'path=""\n'
    else:
        template_string += 'path="some-path"\n'

    if not options.get("no_content", False):
        template_string += 'content="some-content"\n'

    if options.get("unexpected_key", False):
        template_string += 'foo="bar"\n'

    return template_string


def assert_validation_result(
    field: str, expected: bool, results: list[tuple[str, bool]]
):
    for field_name, passed in results:
        if field_name == field:
            assert passed == expected
            return
    pytest.fail(f"Field '{field}' not found in results")
