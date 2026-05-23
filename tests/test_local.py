from __future__ import annotations

from unittest.mock import patch

import pytest

from scaffoldr.config import Config
from scaffoldr.local import scaffold

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
    import click

    with patch(
        "scaffoldr.local.Config.load", return_value=DUMMY_CONFIG
    ):
        scaffold("myproject", "default", tmp_path)
        with pytest.raises(click.exceptions.Exit):
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
