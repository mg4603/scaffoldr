from unittest.mock import MagicMock, patch

import pytest
from typer import Abort as typer_abort

from scaffoldr.exceptions import GitError, LocalError
from scaffoldr.utils import (
    _git,
    check_legacy_config,
    dry_run_scaffold,
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


def test_dry_run_scaffold_already_exists(
    tmp_path, monkeypatch, make_mock_config
):
    _ = make_mock_config("scaffoldr.utils.Config.load")

    path = tmp_path / "project"
    path.mkdir(parents=True, exist_ok=True)

    progress = []

    with pytest.raises(
        LocalError, match=f"Error: {path} already exists."
    ):
        dry_run_scaffold(
            "project", "template", tmp_path, progress.append
        )

    assert len(progress) == 0


def test_dry_run_scaffold_happy_path(
    tmp_path, monkeypatch, make_mock_config
):
    _ = make_mock_config("scaffoldr.utils.Config.load")

    template_path = tmp_path / "template.toml"
    template_path.write_text("""
description = "default scaffolding for python project"

[[files]]
path = "README.md"
content = ""

[[files]]
path = "CONTRIBUTING.md"
content = ""
""")

    monkeypatch.setattr(
        "scaffoldr.utils.resolve_template_path",
        lambda *a: template_path,
    )

    progress = []

    dry_run_scaffold(
        "project", "template", tmp_path, progress.append
    )

    assert [
        "[dry-run] Would create: "
        f"{(tmp_path / 'project' / 'README.md')}",
        "[dry-run] Would create: "
        f"{(tmp_path / 'project' / 'CONTRIBUTING.md')}",
        f"[dry-run] @{(tmp_path / 'project')}: git init",
        f"[dry-run] @{(tmp_path / 'project')}: git add .",
        f"[dry-run] @{(tmp_path / 'project')}: "
        'git commit -m "chore: initial scaffold"',
    ] == progress
