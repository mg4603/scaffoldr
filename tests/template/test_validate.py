from unittest.mock import MagicMock, call

from typer.testing import CliRunner

from scaffoldr.exceptions import TemplateError
from scaffoldr.main import app

runner = CliRunner()


def test_validate_template_err(make_raise, tmp_path):
    make_raise(
        "scaffoldr.template.validate.validate_template",
        TemplateError("simulated"),
    )
    result = runner.invoke(
        app, ["template", "validate", f"{tmp_path}"]
    )
    assert result.exit_code == 1
    assert "simulated" in result.output


def test_validate_happy_path(tmp_path, monkeypatch):
    mock_validate = MagicMock(return_value=[("foo", True)])
    monkeypatch.setattr(
        "scaffoldr.template.validate.validate_template",
        mock_validate,
    )

    result = runner.invoke(
        app, ["template", "validate", f"{tmp_path}"]
    )
    assert "[PASS] foo" in result.output
    assert mock_validate.call_args_list[0] == call(tmp_path)


def test_validate_some_fields_fail(monkeypatch, tmp_path):
    mock_validate = MagicMock(
        return_value=[("foo", True), ("bar", False)]
    )
    monkeypatch.setattr(
        "scaffoldr.template.validate.validate_template",
        mock_validate,
    )
    result = runner.invoke(
        app, ["template", "validate", f"{tmp_path}"]
    )
    assert ("[PASS] foo\n[FAIL] bar\n") in result.output
    assert result.exit_code == 1
