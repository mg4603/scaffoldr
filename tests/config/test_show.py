from typer.testing import CliRunner

from scaffoldr.main import app

runner = CliRunner()


def test_show_success(tmp_path, make_mock_config):
    _ = make_mock_config("scaffoldr.config.show.Config.load")

    result = runner.invoke(app, ["config", "show"])

    assert result.exit_code == 0
    assert (
        "author             = 'test_author'\n"
        "github_username    = 'user'\n"
        "python_version     = 'test_version'\n"
        "license            = 'test_license'\n"
        "default_private    = True\n"
        "required_reviewers = 1\n"
        "use_ssh            = True\n"
        "github_token       = toke****\n"
    ) in result.output
