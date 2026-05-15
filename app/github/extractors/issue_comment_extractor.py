"""Extractor for GitHub issue_comment payloads.

Normalizes the GitHub webhook payload into a small dict consumed by the
internal validator and workflows.
"""

from typing import Dict, Any


def extract_issue_comment(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Extracts normalized fields from a GitHub issue_comment payload.

    Returns a dict with keys: repository (str), issue_number (int|None),
    comment_body (str|None), comment_user (str|None), comment_id (int|None), action
    """

    repo = payload.get("repository")
    if isinstance(repo, dict):
        repository = repo.get("name")
    else:
        repository = repo

    issue = payload.get("issue")
    issue_number = None
    if isinstance(issue, dict):
        issue_number = issue.get("number")
    else:
        issue_number = payload.get("issue_number")

    comment = payload.get("comment")
    if isinstance(comment, dict):
        comment_body = comment.get("body")
        comment_user = (comment.get("user") or {}).get("login")
        comment_id = comment.get("id")
    else:
        comment_body = payload.get("comment_body")
        comment_user = payload.get("comment_user")
        comment_id = payload.get("comment_id")

    action = payload.get("action")

    return {
        "repository": repository,
        "issue_number": issue_number,
        "comment_body": comment_body,
        "comment_user": comment_user,
        "comment_id": comment_id,
        "action": action,
    }


