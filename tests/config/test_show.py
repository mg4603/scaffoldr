from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from scaffoldr.main import app

runner = CliRunner()


def test_show_success(tmp_path):
    mock_config = MagicMock()
    mock_config.author = "test_author"
    mock_config.github_username = "test_username"
    mock_config.python_version = "test_version"
    mock_config.license = "test_license"
    mock_config.default_private = False
    mock_config.required_reviewers = 1
    mock_config.use_ssh = True
    mock_config.github_token = ""

    with patch(
        "scaffoldr.config.show.Config.load",
        return_value=mock_config,
    ):
        result = runner.invoke(app, ["config", "show"])

        assert result.exit_code == 0
        assert (
            "author             = 'test_author'\n"
            "github_username    = 'test_username'\n"
            "python_version     = 'test_version'\n"
            "license            = 'test_license'\n"
            "default_private    = False\n"
            "required_reviewers = 1\n"
            "use_ssh            = True\n"
            "github_token       = (not set)"
        ) in result.output
