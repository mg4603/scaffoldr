from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from scaffoldr.exceptions import GitHubError
from scaffoldr.protection import protect_branch


def _mock_client(status_code: int) -> MagicMock:
    client = MagicMock()
    response = MagicMock()
    response.status_code = status_code
    response.is_success = status_code < 400
    response.text = "error details"
    client.put.return_value = response
    return client


def test_protect_branch_success():
    client = _mock_client(200)
    protect_branch("user", "repo", client)
    client.put.assert_called_once()


def test_protect_branch_with_no_reviewers():
    client = _mock_client(200)
    protect_branch("user", "repo", client, required_reviewers=0)
    call_json = client.put.call_args.kwargs["json"]
    assert (
        call_json["required_pull_request_reviews"][
            "required_approving_review_count"
        ]
        == 0
    )


def test_protect_branch_with_reviewers():
    client = _mock_client(200)
    protect_branch("user", "repo", client, required_reviewers=2)
    call_json = client.put.call_args.kwargs["json"]
    assert (
        call_json["required_pull_request_reviews"][
            "required_approving_review_count"
        ]
        == 2
    )


def test_protect_branch_forbidden():
    client = _mock_client(403)
    with pytest.raises(GitHubError):
        protect_branch("user", "repo", client)


def test_protect_branch_not_found():
    client = _mock_client(404)
    with pytest.raises(GitHubError):
        protect_branch("user", "repo", client)
