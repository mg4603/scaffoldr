from __future__ import annotations

from unittest.mock import MagicMock, call, patch, sentinel

from pytest import fixture as pytest_fixture
from pytest import raises as pytest_raises

from scaffoldr.exceptions import GitHubError
from scaffoldr.github import (
    _get_token,
    create_repo,
    dry_run_github_ops,
    get_authenticated_user,
    get_client,
    github_ops,
)
from scaffoldr.user_config import Config


@pytest_fixture
def mock_git_cmd_runner(monkeypatch):
    git_cmd_runner = MagicMock()

    monkeypatch.setattr("scaffoldr.github._git", git_cmd_runner)
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

    mock_get_client = MagicMock(return_value=mock_client)
    monkeypatch.setattr(
        "scaffoldr.github.get_client", mock_get_client
    )

    mock_create_repo = MagicMock(return_value=mock_repo)
    monkeypatch.setattr(
        "scaffoldr.github.create_repo", mock_create_repo
    )

    mock_create_issues = MagicMock()
    monkeypatch.setattr(
        "scaffoldr.github.create_issues", mock_create_issues
    )

    mock_get_authenticated_user = MagicMock(return_value="user")
    monkeypatch.setattr(
        "scaffoldr.github.get_authenticated_user",
        mock_get_authenticated_user,
    )

    mock_protect_branch = MagicMock()
    monkeypatch.setattr(
        "scaffoldr.github.protect_branch", mock_protect_branch
    )

    mocks = {
        "create_repo": mock_create_repo,
        "protect_branch": mock_protect_branch,
        "get_authenticated_user": mock_get_authenticated_user,
        "create_issues": mock_create_issues,
        "get_client": mock_get_client,
        "repo": mock_repo,
        "client": mock_client,
    }
    return mocks


def test_get_token_from_env(monkeypatch):
    monkeypatch.setenv("SCAFFOLDR_GITHUB_TOKEN", "env-token")

    token = _get_token()
    assert token == "env-token"


def test_get_token_from_config():
    mock_cfg = MagicMock()
    mock_cfg.github_token = "config-token"

    with patch.object(Config, "load", return_value=mock_cfg):
        token = _get_token()
        assert token == "config-token"


def test_get_client_returns_client():
    with patch(
        "scaffoldr.github._client", return_value=sentinel.client
    ) as mock_client:
        result = get_client()

    mock_client.assert_called_once_with()
    assert result == sentinel.client


def test_create_repo_success():
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.is_success = True
    mock_response.json.return_value = {
        "html_url": "https://github.com/user/myrepo",
        "clone_url": "https://github.com/user/myrepo.git",
    }

    with (
        patch(
            "scaffoldr.github._get_token",
            return_value="fake-token",
        ),
        patch("httpx.Client.post", return_value=mock_response),
    ):
        result = create_repo("myrepo")

    assert result["html_url"] == (
        "https://github.com/user/myrepo"
    )


def test_create_repo_already_exists():
    mock_response = MagicMock()
    mock_response.status_code = 422
    mock_response.is_success = False

    with (
        patch(
            "scaffoldr.github._get_token",
            return_value="fake-token",
        ),
        patch("httpx.Client.post", return_value=mock_response),
    ):
        with pytest_raises(GitHubError):
            create_repo("myrepo")


def test_create_repo_invalid_token():
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.is_success = False

    with (
        patch(
            "scaffoldr.github._get_token",
            return_value="fake-token",
        ),
        patch("httpx.Client.post", return_value=mock_response),
    ):
        with pytest_raises(GitHubError):
            create_repo("myrepo")


def test_create_repo_non_422_401_error():
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.is_success = False
    mock_response.text = "simulated error"

    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client.post.return_value = mock_response

    with patch(
        "scaffoldr.github._client",
        return_value=mock_client,
    ):
        with pytest_raises(
            GitHubError,
            match=(
                "Error: GitHub API returned "
                "500 - simulated error"
            ),
        ):
            create_repo("myrepo")


def test_no_token_raises():
    import os

    with (
        patch.dict(os.environ, {}, clear=True),
        patch(
            "scaffoldr.github.Config.load",
            return_value=MagicMock(github_token=""),
        ),
    ):
        from scaffoldr.github import _get_token

        with pytest_raises(GitHubError):
            _get_token()


def test_get_authenticated_user_returns_login():
    mock_client = MagicMock()

    mock_response = MagicMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"login": "foo"}

    mock_client.get.return_value = mock_response

    assert get_authenticated_user(mock_client) == "foo"
    mock_client.get.assert_called_once_with("/user")


def test_get_authenticated_user_raises_on_error():
    mock_client = MagicMock()

    mock_response = MagicMock()
    mock_response.is_success = False

    mock_client.get.return_value = mock_response

    with pytest_raises(
        GitHubError,
        match=(
            "Error: could not fetch GitHub user - check "
            "your token."
        ),
    ):
        get_authenticated_user(mock_client)
    mock_client.get.assert_called_once_with("/user")


def test_dry_run_github_ops():
    progress = []
    dry_run_github_ops(
        project_name="project",
        protect=True,
        use_ssh=False,
        progress=progress.append,
    )

    assert progress == [
        "[dry-run] Would create GitHub repo: project",
        "[dry-run] Would run: git remote add "
        "origin <remote-url>",
        "[dry-run] Would run: git push -u origin main",
        "[dry-run] Would run: git remote set-url origin "
        "<clone-url>",
        "[dry-run] Would create default issues for: project",
        "[dry-run] Would enable branch protection on: main",
    ]


def assert_common_github_ops(
    mocks, mock_config, tmp_path, protect=True
):
    progress = []

    github_ops(
        "foo",
        "bar",
        True,
        protect,
        mock_config,
        tmp_path,
        progress.append,
    )

    if protect:
        assert [
            "Creating GitHub repo...",
            "Creating issues...",
            "Setting branch protection...",
            f"Repo ready: {mocks['repo']['html_url']}",
        ] == progress
        mocks["protect_branch"].assert_called_once_with(
            "user",
            "foo",
            mocks["client"],
            required_reviewers=mock_config.required_reviewers,
            progress=progress.append,
        )

    else:
        assert [
            "Creating GitHub repo...",
            "Creating issues...",
            f"Repo ready: {mocks['repo']['html_url']}",
        ] == progress

    mocks["create_repo"].assert_called_once_with(
        name="foo", description="bar", private=True
    )
    mocks["get_client"].assert_called_once_with()
    mocks["get_authenticated_user"].assert_called_once_with(
        mocks["client"]
    )
    mocks["create_issues"].assert_called_once_with(
        "user", "foo", mocks["client"], progress.append
    )


def test_github_ops_use_ssh(
    tmp_path,
    monkeypatch,
    make_mock_config,
    mock_git_cmd_runner,
    mock_github_deps,
):
    mocks = mock_github_deps

    mock_config = make_mock_config(
        "scaffoldr.github.Config.load"
    )
    mock_config.use_ssh = True

    assert_common_github_ops(
        mocks, mock_config, tmp_path, protect=True
    )

    assert mock_git_cmd_runner.call_args_list[0] == call(
        ["remote", "add", "origin", "ssh-url"],
        cwd=(tmp_path / "foo"),
    )
    assert mock_git_cmd_runner.call_args_list[1] == call(
        ["push", "-u", "origin", "main"], cwd=(tmp_path / "foo")
    )


########################################################


def test_github_ops_do_not_use_ssh(
    tmp_path,
    monkeypatch,
    make_mock_config,
    mock_git_cmd_runner,
    mock_github_deps,
):
    mocks = mock_github_deps

    mock_config = make_mock_config(
        "scaffoldr.github.Config.load"
    )
    mock_config.use_ssh = False

    assert_common_github_ops(
        mocks, mock_config, tmp_path, protect=True
    )

    assert mock_git_cmd_runner.call_args_list[0] == call(
        [
            "remote",
            "add",
            "origin",
            "https://user:token@github.com/user/repo.git",
        ],
        cwd=tmp_path / "foo",
    )

    assert mock_git_cmd_runner.call_args_list[1] == call(
        ["push", "-u", "origin", "main"], cwd=(tmp_path / "foo")
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


def test_github_ops_do_not_protect_branch(
    tmp_path,
    monkeypatch,
    make_mock_config,
    mock_git_cmd_runner,
    mock_github_deps,
):
    mocks = mock_github_deps
    mock_config = make_mock_config(
        "scaffoldr.github.Config.load"
    )

    assert_common_github_ops(
        mocks, mock_config, tmp_path, protect=False
    )

    assert mock_git_cmd_runner.call_args_list[0] == call(
        ["remote", "add", "origin", "ssh-url"],
        cwd=(tmp_path / "foo"),
    )

    assert mock_git_cmd_runner.call_args_list[1] == call(
        ["push", "-u", "origin", "main"], cwd=(tmp_path / "foo")
    )
