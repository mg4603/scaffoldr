from __future__ import annotations

from unittest.mock import patch

from scaffoldr.config import DEFAULT_LICENSE, Config


def test_config_defaults():
    cfg = Config()
    assert cfg.author == ""
    assert cfg.github_username == ""
    assert cfg.license == DEFAULT_LICENSE
    assert cfg.python_version == "3.10"
    assert cfg.default_private is False
    assert cfg.use_ssh is True


def test_config_load_missing_file(tmp_path):
    fake_config = tmp_path / "config.toml"
    with patch("scaffoldr.config.CONFIG_FILE", fake_config):
        cfg = Config.load()
    assert cfg.author == ""


def test_config_write_and_load(tmp_path):
    fake_config = tmp_path / "config.toml"
    fake_dir = tmp_path

    with (
        patch("scaffoldr.config.CONFIG_FILE", fake_config),
        patch("scaffoldr.config.CONFIG_DIR", fake_dir),
    ):
        cfg = Config(
            author="Test User",
            github_username="testuser",
            license="Apache-2.0",
            python_version="3.11",
            default_private=True,
            use_ssh=False,
        )
        cfg.write()
        loaded = Config.load()

    assert loaded.author == "Test User"
    assert loaded.github_username == "testuser"
    assert loaded.license == "Apache-2.0"
    assert loaded.python_version == "3.11"
    assert loaded.default_private is True
    assert loaded.use_ssh is False
