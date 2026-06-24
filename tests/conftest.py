from re import compile as re_compile
from unittest.mock import MagicMock

import pytest

ANSI_ESCAPE = re_compile(r"\x1b\[[0-9;]*m")


def strip_ansi(text: str) -> str:
    return ANSI_ESCAPE.sub("", text)


@pytest.fixture
def make_mock_config(monkeypatch):
    def _make(patch_target: str):
        config = MagicMock()
        config.default_private = True
        config.use_ssh = True
        config.github_username = "user"
        config.required_reviewers = 1
        config.github_token = "token"

        monkeypatch.setattr(patch_target, lambda: config)
        return config

    return _make
