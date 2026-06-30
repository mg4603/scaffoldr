from __future__ import annotations

import os
from collections.abc import Callable

import httpx

from scaffoldr.exceptions import GitHubError
from scaffoldr.user_config import Config

GITHUB_API = "https://api.github.com"


def _get_token() -> str:
    token = os.environ.get("SCAFFOLDR_GITHUB_TOKEN")
    if token:
        return token
    cfg = Config.load()
    if cfg.github_token:
        return cfg.github_token

    raise GitHubError(
        "Error no GitHub token found.\n"
        "Set SCAFFOLDR_GITHUB_TOKEN env var or run "
        "`scaffoldr config init` to save a token.",
    )


def _client() -> httpx.Client:
    token = _get_token()
    return httpx.Client(
        base_url=GITHUB_API,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        timeout=10.0,
    )


def get_client() -> httpx.Client:
    """Return an authenticated httpx client."""
    return _client()


def create_repo(
    name: str,
    description: str = "",
    private: bool = False,
) -> dict:
    """
    Create a new GitHub repo and return the API response.
    Exits with a clear error message on failure.
    """
    with _client() as client:
        response = client.post(
            "/user/repos",
            json={
                "name": name,
                "description": description,
                "private": private,
                "auto_init": False,
            },
        )

        if response.status_code == 422:
            raise GitHubError(
                f"Error: repo '{name}' already exists"
                " on GitHub.",
            )

        if response.status_code == 401:
            raise GitHubError(
                "Error: invald or expired GitHub token.",
            )

        if not response.is_success:
            raise GitHubError(
                "Error: GitHub API returned "
                f"{response.status_code} - "
                f"{response.text}",
            )

        return response.json()


def get_authenticated_user(client: httpx.Client) -> str:
    """Return the authenticated GitHub username."""
    response = client.get("/user")
    if not response.is_success:
        raise GitHubError(
            "Error: could not fetch GitHub user - check"
            " your token.",
        )
    return response.json()["login"]


def dry_run_github_ops(
    project_name: str,
    protect: bool,
    use_ssh: bool,
    progress: Callable[[str], None] = lambda _: None,
) -> None:
    progress(
        f"[dry-run] Would create GitHub repo: {project_name}"
    )

    progress(
        "[dry-run] Would run: git remote add "
        "origin <remote-url>"
    )

    progress("[dry-run] Would run: git push -u origin main")

    if not use_ssh:
        progress(
            "[dry-run] Would run: git remote set-url "
            "origin <clone-url>"
        )

    progress(
        "[dry-run] Would create default issues for: "
        f"{project_name}"
    )

    if protect:
        progress(
            "[dry-run] Would enable branch protection on: main"
        )
