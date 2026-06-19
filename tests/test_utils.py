from unittest.mock import MagicMock, patch

import pytest
from typer import Abort as typer_abort

from scaffoldr.exceptions import GitError
from scaffoldr.utils import (
    _git,
    check_legacy_config,
    ensure_dirs,
)


def test_git_error_in_git_command_runner(tmp_path):
    args = ["asdf"]
    result = MagicMock()
    result.returncode = 1
    result.stderr = "some error"

    with patch(
        "scaffoldr.utils.subprocess_run",
        return_value=result,
    ):
        with pytest.raises(
            GitError, match="git error: some error"
        ):
            _git(args, tmp_path)


def test_git_cmd_runner_happy_path(tmp_path, monkeypatch):
    args = ["init"]
    result = MagicMock()
    result.returncode = 0

    monkeypatch.setattr(
        "scaffoldr.utils.subprocess_run",
        lambda *a, **kw: result,
    )
    _git(args, cwd=tmp_path)


def test_ensure_dirs_success(tmp_path, monkeypatch):
    user_templates = tmp_path / "templates"

    monkeypatch.setattr(
        "scaffoldr.utils.USER_DEFINED_TEMPLATES_PATH",
        user_templates,
    )

    ensure_dirs()
    assert user_templates.exists()


def test_legacy_path_exists(tmp_path):
    config_dir = tmp_path / ".scaffoldr"
    config_dir.mkdir()

    with patch(
        "scaffoldr.utils.Path.home", return_value=tmp_path
    ):
        with pytest.raises(typer_abort):
            check_legacy_config()
