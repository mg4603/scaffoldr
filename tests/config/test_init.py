from typer.testing import CliRunner

from scaffoldr.main import app

runner = CliRunner()


# addressed in #61
# def test_init_config_file_overwrite_denied(
#     tmp_path, monkeypatch
# ):
#     config_dir = tmp_path / ".config" / "scaffoldr"
#     config_dir.mkdir(parents=True, exist_ok=True)
#
#     config_file = config_dir / "config.toml"
#     config_file.write_text('foo="bar"')
#
#     monkeypatch.setattr(
#         "scaffoldr.config.init.CONFIG_FILE", config_file
#     )
#
#     result = runner.invoke(app, ["config", "init"],
#               input="n\n")
#
#     assert (
#         f"{config_file} already exists. Overwrite?\nAborted."
#     ) in result.output


def test_init_happy_path(tmp_path, monkeypatch):
    config_dir = tmp_path / ".config" / "scaffoldr"
    config_file = config_dir / "config.toml"

    monkeypatch.setattr(
        "scaffoldr.user_config.CONFIG_DIR", config_dir
    )
    monkeypatch.setattr(
        "scaffoldr.user_config.CONFIG_FILE", config_file
    )
    monkeypatch.setattr(
        "scaffoldr.config.init.CONFIG_FILE", config_file
    )

    result = runner.invoke(
        app,
        ["config", "init"],
        input=(
            "user\ngithub_username\nMIT\n3.12\ny\ntoken\n2\ny\n"
        ),
    )

    assert f"Config written to {config_file}" in result.output

    with config_file.open("r") as f:
        assert (
            'author = "user"\n'
            'github_username = "github_username"\n'
            'license = "MIT"\n'
            'python_version = "3.12"\n'
            "default_private = true\n"
            'github_token = "token"\n'
            "required_reviewers = 2\n"
            "use_ssh = true\n"
        ) in f.read()
