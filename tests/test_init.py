from typer.testing import CliRunner

from scaffoldr.exceptions import TemplateError
from scaffoldr.main import app

runner = CliRunner()


def test_init_command_scaffold_raises_template_error(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(
        "scaffoldr.init._scaffold",
        lambda *a, **kw: (_ for _ in ()).throw(
            TemplateError("simulated")
        ),
    )
    result = runner.invoke(
        app, ["init", "foo", "--path", f"{tmp_path}"]
    )

    assert result.exit_code == 1
    assert "simulated" in result.output
