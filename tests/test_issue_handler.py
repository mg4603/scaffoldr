from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from scaffoldr.exceptions import GitHubError
from scaffoldr.issue_handler import (
    DEFAULT_ISSUES,
    create_issues,
    resolve_templates,
)


def test_resolve_templates_returns_defaults():
    with patch(
        "scaffoldr.issue_handler._load_user_issues",
        return_value=[],
    ):
        templates = resolve_templates()
    assert templates == DEFAULT_ISSUES


def test_user_templates_override_defaults():
    user_issue = {
        "title": "chore: initial project setup",
        "body": "custom body",
    }
    with patch(
        "scaffoldr.issue_handler._load_user_issues",
        return_value=[user_issue],
    ):
        templates = resolve_templates()

    titles = [t["title"] for t in templates]
    assert titles.count("chore: initial project setup") == 1
    match = next(
        t
        for t in templates
        if t["title"] == "chore: initial project setup"
    )
    assert match["body"] == "custom body"


def test_user_templates_extend_defaults():
    user_issue = {
        "title": "feat: custom feature",
        "body": "custom body",
    }
    with patch(
        "scaffoldr.issue_handler._load_user_issues",
        return_value=[user_issue],
    ):
        templates = resolve_templates()

    titles = [t["title"] for t in templates]
    assert "feat: custom feature" in titles
    assert "chore: initial project setup" in titles
    assert "chore: setup CI with GitHub Actions" in titles


def test_create_issues_success():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.is_success = True
    mock_response.json.return_value = {
        "number": 1,
        "title": "chore: initial project setup",
        "html_url": "https://github.com/u/r/issues/1",
    }
    mock_client.post.return_value = mock_response

    with patch(
        "scaffoldr.issue_handler._load_user_issues",
        return_value=[],
    ):
        created = create_issues("user", "repo", mock_client)

    assert len(created) == len(DEFAULT_ISSUES)


def test_create_issues_rate_limited():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.is_success = False
    mock_client.post.return_value = mock_response

    with patch(
        "scaffoldr.issue_handler._load_user_issues",
        return_value=[],
    ):
        with pytest.raises(GitHubError):
            create_issues("user", "repo", mock_client)
