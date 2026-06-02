class TemplateError(Exception):
    """Raised when a template operation fails."""


class GitHubError(Exception):
    """Raised when a GitHub operation fails."""


class LocalError(Exception):
    """Raised when a local scaffold operation fails."""


class GitError(Exception):
    """Raised when a git operation fails."""
