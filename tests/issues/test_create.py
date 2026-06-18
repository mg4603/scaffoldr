from unittest.mock import MagicMock

from typer.testing import CliRunner

from scaffoldr.main import app

runner = CliRunner()


def test_create_issue_with_owner_and_repo(monkeypatch):
    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)

    monkeypatch.setattr(
        "scaffoldr.issues.create.get_client",
        lambda: mock_client,
    )

    monkeypatch.setattr(
        "scaffoldr.issues.create._create_issues",
        lambda *a: None,
    )

    result = runner.invoke(
        app, ["issues", "create", "user/foo"]
    )

    assert (
        "Creating issues on user/foo...\nDone. Issues created."
    ) in result.output


def test_create_issue_with_repo(monkeypatch):
    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)

    monkeypatch.setattr(
        "scaffoldr.issues.create.get_client",
        lambda: mock_client,
    )

    monkeypatch.setattr(
        "scaffoldr.issues.create.get_authenticated_user",
        lambda *a: "foo",
    )

    monkeypatch.setattr(
        "scaffoldr.issues.create._create_issues",
        lambda *a: None,
    )

    result = runner.invoke(app, ["issues", "create", "bar"])
    assert (
        "Creating issues on foo/bar...\nDone. Issues created."
    ) in result.output
