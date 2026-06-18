from typer.testing import CliRunner

from scaffoldr.main import app
from scaffoldr.template.list import list_templates

runner = CliRunner()


def test_template_list_no_builtin_no_user(
    tmp_path, monkeypatch
):
    builtin_templates_dir = tmp_path / "builtin"
    builtin_templates_dir.mkdir(parents=True, exist_ok=True)

    user_defined_templates_dir = tmp_path / "user"
    user_defined_templates_dir.mkdir(
        parents=True, exist_ok=True
    )

    monkeypatch.setattr(
        "scaffoldr.template.list.BUILTIN_TEMPLATES_PATH",
        builtin_templates_dir,
    )
    monkeypatch.setattr(
        "scaffoldr.template.list.USER_DEFINED_TEMPLATES_PATH",
        user_defined_templates_dir,
    )

    result = runner.invoke(app, ["template", "list"])

    assert (
        "Built-in\n(none)\n\n"
        f"User ({user_defined_templates_dir})\n(none)\n"
        in result.output
    )


def test_template_list_builtin_no_user(tmp_path, monkeypatch):
    builtin_templates_dir = tmp_path / "builtin"
    builtin_templates_dir.mkdir(parents=True, exist_ok=True)

    builtin_template = builtin_templates_dir / "foo.toml"
    builtin_template.write_text('description="bar"')

    user_defined_templates_dir = tmp_path / "user"
    user_defined_templates_dir.mkdir(
        parents=True, exist_ok=True
    )

    monkeypatch.setattr(
        "scaffoldr.template.list.BUILTIN_TEMPLATES_PATH",
        builtin_templates_dir,
    )

    monkeypatch.setattr(
        "scaffoldr.template.list.USER_DEFINED_TEMPLATES_PATH",
        user_defined_templates_dir,
    )

    result = runner.invoke(app, ["template", "list"])

    assert (
        "Built-in\nfoo   bar\n\n"
        f"User ({user_defined_templates_dir})\n(none)\n"
    ) in result.output


def test_template_list_builtin_and_user(tmp_path, monkeypatch):
    builtin_templates_dir = tmp_path / "builtin"
    builtin_templates_dir.mkdir(parents=True, exist_ok=True)

    builtin_template = builtin_templates_dir / "foo.toml"
    builtin_template.write_text('description="bar"')

    user_defined_templates_dir = tmp_path / "user"
    user_defined_templates_dir.mkdir(
        parents=True, exist_ok=True
    )
    user_defined_template = (
        user_defined_templates_dir / "user-foo.toml"
    )
    user_defined_template.write_text('description="user-bar"')

    monkeypatch.setattr(
        "scaffoldr.template.list.BUILTIN_TEMPLATES_PATH",
        builtin_templates_dir,
    )
    monkeypatch.setattr(
        "scaffoldr.template.list.USER_DEFINED_TEMPLATES_PATH",
        user_defined_templates_dir,
    )
    result = runner.invoke(app, ["template", "list"])

    assert (
        "Built-in\nfoo   bar\n\n"
        f"User ({user_defined_templates_dir})\n"
        "user-foo   user-bar\n"
    ) in result.output


def test_list_templates_returns_name_description(tmp_path):
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir(parents=True, exist_ok=True)

    template1 = templates_dir / "foo.toml"
    template1.write_text('description="bar"')

    template2 = templates_dir / "hello.toml"
    template2.write_text('description="world"')

    result = list_templates(templates_dir)

    assert sorted(["foo   bar", "hello   world"]) == sorted(
        result
    )
