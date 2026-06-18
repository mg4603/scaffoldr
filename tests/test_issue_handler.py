from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from tomli_w import dump as toml_dump

from scaffoldr.exceptions import GitHubError
from scaffoldr.issue_handler import (
    DEFAULT_ISSUES,
    _load_user_issues,
    create_issues,
    resolve_templates,
)


def test_load_user_issues_issues_file_does_not_exist(
    tmp_path, monkeypatch
):
    issues_file = tmp_path / "issues.toml"

    monkeypatch.setattr(
        "scaffoldr.issue_handler.ISSUES_FILE", issues_file
    )
    assert _load_user_issues() == []


def test_load_user_issues_file_exists(tmp_path, monkeypatch):
    issues = [
        {
            "title": "sample_issue_title",
            "body": "sample issue body",
        },
    ]

    issue_file = tmp_path / "issues.toml"
    monkeypatch.setattr(
        "scaffoldr.issue_handler.ISSUES_FILE", issue_file
    )

    with issue_file.open("wb") as f:
        toml_dump({"issue": issues}, f)

    assert _load_user_issues() == issues


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

    progress = []
    with patch(
        "scaffoldr.issue_handler._load_user_issues",
        return_value=[],
    ):
        create_issues(
            "user", "repo", mock_client, progress.append
        )

    assert len(progress) == len(DEFAULT_ISSUES)


def test_create_issues_rate_limited():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.is_success = False
    mock_client.post.return_value = mock_response

    progress = []
    with patch(
        "scaffoldr.issue_handler._load_user_issues",
        return_value=[],
    ):
        with pytest.raises(GitHubError):
            create_issues(
                "user", "repo", mock_client, progress.append
            )
    assert len(progress) == 0


def test_create_issues_410_error():

    mock_response = MagicMock()
    mock_response.is_success = False
    mock_response.status_code = 410

    mock_client = MagicMock()
    mock_client.post.return_value = mock_response

    progress = []
    with pytest.raises(
        GitHubError,
        match="Error: issues are disabled on this repo",
    ):
        create_issues(
            "user", "this_repo", mock_client, progress.append
        )

    assert len(progress) == 0


def test_creat_issues_non_410_403_errors(tmp_path, monkeypatch):
    issues = [
        {
            "title": "sample_template_title",
            "body": "sample template body",
        }
    ]

    mock_response = MagicMock()
    mock_response.is_success = False
    mock_response.status_code = 404

    mock_client = MagicMock()
    mock_client.post.return_value = mock_response

    progress = []

    with patch(
        "scaffoldr.issue_handler.resolve_templates",
        return_value=issues,
    ):
        with pytest.raises(
            GitHubError,
            match=(
                "Error: failed to create issue "
                "'sample_template_title' - 404"
            ),
        ):
            create_issues(
                "user",
                "this_repo",
                mock_client,
                progress.append,
            )

    assert len(progress) == 0
