from unittest.mock import MagicMock, call

from pytest import fixture as pytest_fixture
from typer.testing import CliRunner

from scaffoldr.exceptions import TemplateError
from scaffoldr.main import app

runner = CliRunner()


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


def test_new_use_ssh(
    tmp_path,
    monkeypatch,
    make_mock_config,
    mock_git_cmd_runner,
    mock_github_deps,
):
    mock_repo = mock_github_deps
    _ = make_mock_config("scaffoldr.new.Config.load")
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

    assert (
        "Creating GitHub repo...\n"
        "Creating issues...\nSetting branch protection...\n"
        f"Repo ready: {mock_repo['html_url']}"
    ) in result.output


def test_new_do_not_use_ssh(
    tmp_path,
    monkeypatch,
    make_mock_config,
    mock_git_cmd_runner,
    mock_github_deps,
):
    mock_repo = mock_github_deps
    mock_config = make_mock_config("scaffoldr.new.Config.load")
    mock_config.use_ssh = False

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

    assert (
        "Creating GitHub repo...\nCreating issues...\n"
        "Setting branch protection...\n"
        f"Repo ready: {mock_repo['html_url']}\n"
    ) in result.output

    assert len(mock_git_cmd_runner.call_args_list) == 3
    assert mock_git_cmd_runner.call_args_list[0] == call(
        [
            "remote",
            "add",
            "origin",
            "https://user:token@github.com/user/repo.git",
        ],
        cwd=tmp_path / "foo",
    )
    assert mock_git_cmd_runner.call_args_list[2] == call(
        [
            "remote",
            "set-url",
            "origin",
            "https://github.com/user/repo.git",
        ],
        cwd=tmp_path / "foo",
    )


def test_new_do_not_protect_branch(
    tmp_path,
    monkeypatch,
    make_mock_config,
    mock_git_cmd_runner,
    mock_github_deps,
):
    mock_repo = mock_github_deps
    _ = make_mock_config("scaffoldr.new.Config.load")
    result = runner.invoke(
        app,
        [
            "new",
            "foo",
            "--description",
            "bar",
            "--path",
            f"{tmp_path}",
            "--no-protect",
        ],
    )
    assert (
        "Creating GitHub repo...\n"
        "Creating issues...\n"
        f"Repo ready: {mock_repo['html_url']}"
    ) in result.output

    assert ("Setting branch protection...") not in result.output


def test_new_raises_exception(
    tmp_path,
    monkeypatch,
    make_mock_config,
    mock_git_cmd_runner,
    mock_github_deps,
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
