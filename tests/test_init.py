from unittest.mock import MagicMock, call

from typer import echo as typer_echo
from typer.testing import CliRunner

from scaffoldr.exceptions import TemplateError
from scaffoldr.main import app

runner = CliRunner()


def test_init_command_dry_run(tmp_path, monkeypatch):
    mock_dry_run_scaffold = MagicMock()
    monkeypatch.setattr(
        "scaffoldr.init.dry_run_scaffold",
        mock_dry_run_scaffold,
    )

    result = runner.invoke(
        app,
        ["init", "foo", "--path", f"{tmp_path}", "--dry-run"],
    )

    assert result.exit_code == 0
    assert mock_dry_run_scaffold.call_args_list[0] == call(
        "foo", "default", tmp_path, typer_echo
    )


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
