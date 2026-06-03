from __future__ import annotations

from collections.abc import Callable

from scaffoldr.exceptions import GitHubError


def protect_branch(
    owner: str,
    repo: str,
    client,
    branch: str = "main",
    required_reviewers: int = 1,
    progress: Callable[[str], None] = lambda _: None,
) -> None:
    """
    Apply branch protection rules to the given branch.
    Blocks direct pushes and optionally requires PR
    reviews before merging.
    """
    response = client.put(
        f"/repos/{owner}/{repo}/branches/{branch}/protection",
        json={
            "required_status_checks": {
                "strict": False,
                "contexts": [],
            },
            "enforce_admins": False,
            "required_pull_request_reviews": {
                "required_approving_review_count": (
                    required_reviewers
                ),
                "dismiss_stale_reviews": False,
                "required_code_owner_reviews": False,
            },
            "restrictions": None,
        },
    )
    if not response.is_success:
        raise GitHubError(
            f"Error: Failed to set branch protection "
            f"- {response.status_code}: {response.text}",
        )

    progress(
        f"Branch protection enabled on '{branch}' "
        f" ({required_reviewers} reviewer(s) required)."
    )
