"""Extractor for GitHub issues payloads.

Normalizes the GitHub webhook payload into a small dict consumed by
the internal validator and workflows.
"""

from typing import Dict, Any


def extract_issues_event(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Extracts normalized fields from a GitHub issues payload.

    Returns a dict with keys: repository (str), issue_number (int|None),
    issue_title (str|None), labels (list), action (str|None), issue_body (str|None)
    """

    repo = payload.get("repository")
    if isinstance(repo, dict):
        repository = repo.get("name")
    else:
        repository = repo

    # support raw payload shape where issue is a dict
    issue = payload.get("issue")
    if isinstance(issue, dict):
        issue_number = issue.get("number")
        issue_title = issue.get("title")
        issue_body = issue.get("body")
        labels_raw = issue.get("labels") or []
    else:
        # normalized / flattened shape
        issue_number = payload.get("issue_number")
        issue_title = payload.get("issue_title")
        issue_body = payload.get("issue_body")
        labels_raw = payload.get("labels") or []

    # normalize labels to list of dicts with 'name'
    labels = []
    for l in labels_raw:
        if isinstance(l, dict):
            name = l.get("name")
        else:
            name = str(l)
        if name:
            labels.append({"name": name})

    action = payload.get("action")

    return {
        "repository": repository,
        "issue_number": issue_number,
        "issue_title": issue_title,
        "issue_body": issue_body,
        "labels": labels,
        "action": action,
    }

