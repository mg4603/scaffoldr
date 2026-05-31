from typer import Argument as typer_argument
from typer import Typer
from typer import echo as typer_echo

from scaffoldr.github import get_authenticated_user, get_client
from scaffoldr.issue_handler import (
    create_issues as _create_issues,
)

app = Typer()


@app.command("create")
def create(
    repo: str = typer_argument(
        ..., help="Repo name (owner/repo or just repo)"
    ),
) -> None:
    """Create default issues on an existing GitHub repo."""
    with get_client() as client:
        if "/" in repo:
            owner, repo_name = repo.split("/", 1)
        else:
            owner = get_authenticated_user(client)
            repo_name = repo

        typer_echo(f"Creating issues on {owner}/{repo_name}...")
        created = _create_issues(owner, repo_name, client)
        typer_echo(f"Done. {len(created)} issues created.")
