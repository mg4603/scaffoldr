from __future__ import annotations

import os
from typing import Optional

import httpx
import typer

from scaffoldr.config import Config

GITHUB_API = "https://api.github.com"


def _get_token() -> str:
    token = os.environ.get("SCAFFOLDR_GITHUB_TOKEN")
    if token:
        return token
    cfg = Config.load()
    if cfg.github_token:
        return cfg.github_token
    typer.echo(
        "Error no GitHub token found.\n"
        "Set SCAFFOLDR_GITHUB_TOKEN env var or run "
        "`scaffoldr config init` to save a token.",
        err=True,
    )
    raise typer.Exit(code=1)


def _client() -> httpx.Client:
    token = _get_token(0)
    return httpx.Client(
        base_url=GITHUB_API,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        timeout=10.0,
    )


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
            typer.echo(
                f"Error: repo '{name}' already exists on GitHub.",
                err=True,
            )
            raise typer.Exit(code=1)

        if response.status_code == 401:
            typer.echo(
                "Error: invald or expired GitHub token.", err=True
            )
            raise typer.Exit(code=1)

        if not response.is_success:
            typer.echo(
                f"Error: GitHub API returned "
                f"{response.status_code} - "
                f"{response.text}",
                err=True,
            )
            raise typer.Exit(code=1)
        return response.json()
