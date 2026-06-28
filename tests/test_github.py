from __future__ import annotations

from unittest.mock import MagicMock, patch, sentinel

import pytest

from scaffoldr.exceptions import GitHubError
from scaffoldr.github import (
    _get_token,
    create_repo,
    dry_run_github_ops,
    get_authenticated_user,
    get_client,
)
from scaffoldr.user_config import Config


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
        with pytest.raises(GitHubError):
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
        with pytest.raises(GitHubError):
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
        with pytest.raises(
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

        with pytest.raises(GitHubError):
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

    with pytest.raises(
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
