from __future__ import annotations

from unittest.mock import patch

import pytest

from scaffoldr.exceptions import LocalError
from scaffoldr.local import dry_run_scaffold, scaffold
from scaffoldr.user_config import Config

DUMMY_CONFIG = Config(
    author="Test User",
    github_username="testuser",
    license="MIT",
    python_version="3.11",
    default_private=False,
)


@pytest.fixture
def project(tmp_path):
    with patch(
        "scaffoldr.local.Config.load", return_value=DUMMY_CONFIG
    ):
        scaffold("myproject", "default", tmp_path)
    return tmp_path / "myproject"


def test_folders_created(project):
    assert (project / "myproject").is_dir()
    assert (project / "tests").is_dir()
    assert (project / "docs" / "adr").is_dir()


def test_files_created(project):
    assert (project / "README.md").exists()
    assert (project / "CONTRIBUTING.md").exists()
    assert (project / "pyproject.toml").exists()
    assert (project / ".gitignore").exists()
    assert (
        project / "docs" / "adr" / "0001-initial-decisions.md"
    ).exists()


def test_readme_contains_project_name(project):
    content = (project / "README.md").read_text()
    assert "myproject" in content


def test_pyproject_contains_author(project):
    content = (project / "pyproject.toml").read_text()
    assert "Test User" in content


def test_git_repo_initialized(project):
    assert (project / ".git").is_dir()


def test_already_exists_raises(tmp_path):
    with patch(
        "scaffoldr.local.Config.load", return_value=DUMMY_CONFIG
    ):
        scaffold("myproject", "default", tmp_path)
        with pytest.raises(LocalError):
            scaffold("myproject", "default", tmp_path)


def test_ci_workflow_created(project):
    assert (
        project / ".github" / "workflows" / "ci.yml"
    ).exists()


def test_ci_workflow_contains_python_version(project):
    content = (
        project / ".github" / "workflows" / "ci.yml"
    ).read_text()
    assert DUMMY_CONFIG.python_version in content


def test_ci_workflow_contains_explicit_installs(project):
    content = (
        project / ".github" / "workflows" / "ci.yml"
    ).read_text()
    assert "pip install ruff pytest" in content


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
        "scaffoldr.local.resolve_template_path",
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
