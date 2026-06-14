from pathlib import Path

from typer.testing import CliRunner

from scaffoldr.main import app

runner = CliRunner()


def test_migrate_legacy_path_doesnt_exist(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    result = runner.invoke(app, ["config", "migrate"])

    assert "Legacy config does not exist." in result.output


def test_migrate_config_dir_exists_deny_overwrite(
    tmp_path, monkeypatch
):
    legacy_path = tmp_path / ".scaffoldr"
    legacy_path.mkdir(parents=True, exist_ok=True)

    config_dir = tmp_path / ".config" / "scaffoldr"
    config_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setattr(
        "scaffoldr.config.migrate.CONFIG_DIR", config_dir
    )

    result = runner.invoke(
        app, ["config", "migrate"], input="n\n"
    )

    assert (
        f"{config_dir} already exists. Overwrite?"
        in result.output
    )

    assert "Aborted." in result.output


def test_migrate_files_are_copied(tmp_path, monkeypatch):
    legacy_path = tmp_path / ".scaffoldr"
    legacy_path.mkdir(parents=True, exist_ok=True)

    legacy_config_file = legacy_path / "config.toml"
    legacy_config_file.write_text('description="sample config"')

    config_dir = tmp_path / ".config" / "scaffoldr"

    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setattr(
        "scaffoldr.config.migrate.CONFIG_DIR", config_dir
    )

    result = runner.invoke(app, ["config", "migrate"])

    assert (
        f"Successfully removed {legacy_path}\n"
        "Config files migrated successfully from "
        f"{legacy_path} to {config_dir}"
    ) in result.output

    config_file = config_dir / "config.toml"
    assert config_file.exists()


def test_migrate_dirs_are_copied(tmp_path, monkeypatch):
    legacy_path = tmp_path / ".scaffoldr"
    legacy_subdir = legacy_path / "subdir"
    legacy_subdir.mkdir(parents=True, exist_ok=True)

    config_dir = tmp_path / ".config" / "scaffoldr"

    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setattr(
        "scaffoldr.config.migrate.CONFIG_DIR", config_dir
    )

    result = runner.invoke(app, ["config", "migrate"])

    assert (
        f"Successfully removed {legacy_path}\n"
        "Config files migrated successfully from "
        f"{legacy_path} to {config_dir}"
    ) in result.output

    config_subdir = config_dir / "subdir"
    assert config_subdir.exists()


def test_migrate_permission_denied_legacy_path_removal(
    tmp_path, monkeypatch
):
    legacy_path = tmp_path / ".scaffoldr"
    legacy_path.mkdir(parents=True, exist_ok=True)

    config_dir = tmp_path / ".config" / "scaffoldr"

    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setattr(
        "scaffoldr.config.migrate.CONFIG_DIR", config_dir
    )
    monkeypatch.setattr(
        "scaffoldr.config.migrate.shutil_rmtree",
        lambda *a, **kw: (_ for _ in ()).throw(
            PermissionError("denied")
        ),
    )

    result = runner.invoke(app, ["config", "migrate"])

    assert (
        f"Permission denied when removing {legacy_path}"
    ) in result.output


def test_migrate_non_permission_error_legacy_path_removal(
    tmp_path, monkeypatch
):
    legacy_path = tmp_path / ".scaffoldr"
    legacy_path.mkdir(parents=True, exist_ok=True)

    config_dir = tmp_path / ".config" / "scaffoldr"

    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setattr(
        "scaffoldr.config.migrate.CONFIG_DIR", config_dir
    )
    monkeypatch.setattr(
        "scaffoldr.config.migrate.shutil_rmtree",
        lambda *a, **kw: (_ for _ in ()).throw(
            Exception("non-permission error")
        ),
    )

    result = runner.invoke(app, ["config", "migrate"])

    assert (
        "Error: non-permission error\nAborted."
    ) in result.output
