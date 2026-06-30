from unittest.mock import MagicMock, call

from pytest import fixture as pytest_fixture
from typer import echo as typer_echo
from typer.testing import CliRunner

from scaffoldr.exceptions import TemplateError
from scaffoldr.main import app

runner = CliRunner()


@pytest_fixture
def mock_github_ops(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr("scaffoldr.new.github_ops", mock)
    return mock


@pytest_fixture
def mock_scaffold(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr("scaffoldr.new._scaffold", mock)
    return mock


@pytest_fixture
def mock_git_cmd_runner(monkeypatch):
    git_cmd_runner = MagicMock()

    monkeypatch.setattr("scaffoldr.new._git", git_cmd_runner)
    return git_cmd_runner


@pytest_fixture
def mock_github_deps(monkeypatch):
    mock_repo = {
        "ssh_url": "ssh-url",
        "clone_url": "https://github.com/user/repo.git",
        "html_url": "html-url",
    }

    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    monkeypatch.setattr(
        "scaffoldr.new.get_client", lambda: mock_client
    )

    monkeypatch.setattr(
        "scaffoldr.new._create_repo", lambda *a, **kw: mock_repo
    )
    monkeypatch.setattr(
        "scaffoldr.new._scaffold", lambda *a: None
    )
    monkeypatch.setattr(
        "scaffoldr.new._create_issues", lambda *a: None
    )

    monkeypatch.setattr(
        "scaffoldr.new.get_authenticated_user",
        lambda *a: "user",
    )

    monkeypatch.setattr(
        "scaffoldr.new._protect_branch", lambda *a, **kw: None
    )

    return mock_repo


def test_new_raises_exception(
    tmp_path,
    monkeypatch,
    make_mock_config,
    mock_scaffold,
    mock_github_ops,
):
    _ = make_mock_config("scaffoldr.new.Config.load")
    monkeypatch.setattr(
        "scaffoldr.new._scaffold",
        lambda *a: (_ for _ in ()).throw(
            TemplateError("simulated.")
        ),
    )

    result = runner.invoke(
        app,
        [
            "new",
            "foo",
            "--description",
            "bar",
            "--path",
            f"{tmp_path}",
        ],
    )

    assert result.exit_code == 1
    assert result.output == "simulated.\n"


def test_new_dry_run(tmp_path, monkeypatch, make_mock_config):
    _ = make_mock_config("scaffoldr.new.Config.load")

    mock_dry_run_scaffold = MagicMock()
    monkeypatch.setattr(
        "scaffoldr.new.dry_run_scaffold", mock_dry_run_scaffold
    )

    mock_dry_run_github_ops = MagicMock()
    monkeypatch.setattr(
        "scaffoldr.new.dry_run_github_ops",
        mock_dry_run_github_ops,
    )

    result = runner.invoke(
        app,
        [
            "new",
            "foo",
            "--description",
            "bar",
            "--path",
            f"{tmp_path}",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    assert mock_dry_run_scaffold.call_args_list[0] == call(
        "foo", "default", tmp_path, typer_echo
    )

    assert mock_dry_run_github_ops.call_args_list[0] == call(
        "foo", True, True, typer_echo
    )
