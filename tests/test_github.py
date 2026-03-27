from __future__ import annotations

from unittest.mock import MagicMock, patch

import click
import pytest


def test_create_repo_success():
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.is_success = True
    mock_response.json.return_value = {
        "html_url": "https://github.com/user/myrepo",
        "clone_url": "https://github.com/user/myrepo.git",
    }

    with (
        patch("scaffoldr.github._get_token", return_value="fake-token"),
        patch("httpx.Client.post", return_value=mock_response),
    ):
        from scaffoldr.github import create_repo

        result = create_repo("myrepo")

    assert result["html_url"] == ("https://github.com/user/myrepo")


def test_create_repo_already_exists():
    mock_response = MagicMock()
    mock_response.status_code = 422
    mock_response.is_success = False

    with (
        patch("scaffoldr.github._get_token", return_value="fake-token"),
        patch("httpx.Client.post", return_value=mock_response),
    ):
        from scaffoldr.github import create_repo

        with pytest.raises(click.exceptions.Exit):
            create_repo("myrepo")


def test_create_repo_invalid_token():
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.is_succes = False

    with (
        patch("scaffoldr.github._get_token", return_vlaue="fake-token"),
        patch("httpx.Client.post", return_value=mock_response),
    ):
        from scaffoldr.github import create_repo

        with pytest.raises(click.exceptions.Exit):
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

        with pytest.raises(click.exceptions.Exit):
            _get_token()
