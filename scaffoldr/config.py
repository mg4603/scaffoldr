from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib

CONFIG_DIR = Path.home() / ".scaffoldr"
CONFIG_FILE = CONFIG_DIR / "config.toml"

DEFAULT_PYTHON_VERSION = "3.10"
DEFAULT_LICENSE = "MIT"


@dataclass
class Config:
    author: str = ""
    github_username: str = ""
    license: str = DEFAULT_LICENSE
    python_version: str = DEFAULT_PYTHON_VERSION
    default_private: bool = False
    github_token: str = ""
    required_reviewers: int = 1
    extra: dict = field(default_factory=dict)

    @classmethod
    def load(cls) -> "Config":
        if not CONFIG_FILE.exists():
            return cls()
        with CONFIG_FILE.open("rb") as f:
            data = tomllib.load(f)
        return cls(
            author=data.get("author", ""),
            github_username=data.get("github_username", ""),
            license=data.get("license", DEFAULT_LICENSE),
            python_version=data.get(
                "python_version", DEFAULT_PYTHON_VERSION
            ),
            default_private=data.get("default_private", False),
            github_token=data.get("github_token", ""),
            required_reviewers=data.get("required_reviewers", 1),
            extra={
                k: v
                for k, v in data.items()
                if k
                not in {
                    "author",
                    "github_username",
                    "license",
                    "python_version",
                    "default_private",
                    "github_token",
                    "required_reviewers",
                }
            },
        )

    def write(self) -> None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        lines = [
            f'author = "{self.author}"\n',
            f'github_username = "{self.github_username}"\n',
            f'license = "{self.license}"\n',
            f'python_version = "{self.python_version}"\n',
            f"default_private = {str(self.default_private).lower()}\n",
            f'github_token = "{self.github_token}"\n',
            f"required_reviewers = {self.required_reviewers}\n",
        ]
        CONFIG_FILE.write_text("".join(lines))
