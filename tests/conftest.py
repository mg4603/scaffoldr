from re import compile as re_compile
from unittest.mock import MagicMock

import pytest

ANSI_ESCAPE = re_compile(r"\x1b\[[0-9;]*m")


def strip_ansi(text: str) -> str:
    return ANSI_ESCAPE.sub("", text)


@pytest.fixture
def make_mock_config(monkeypatch):
    def _make(patch_target: str):
        mock_config = MagicMock()

        mock_config.author = "test_author"
        mock_config.github_username = "user"
        mock_config.python_version = "test_version"
        mock_config.license = "test_license"
        mock_config.default_private = True
        mock_config.required_reviewers = 1
        mock_config.use_ssh = True
        mock_config.github_token = "token"

        monkeypatch.setattr(patch_target, lambda: mock_config)
        return mock_config

    return _make
