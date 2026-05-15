"""Extractor for GitHub pull_request payloads.

Normalizes the GitHub webhook payload into a small dict consumed by
the internal validator and workflows.
"""

from typing import Dict, Any


def extract_pull_request(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Extracts normalized fields from a GitHub pull_request payload.

    Returns a dict with keys: repository (str), pr_number (int|None),
    pr_title (str|None), pr_body (str|None), action (str|None), labels (list)
    """

    repo = payload.get("repository")
    if isinstance(repo, dict):
        repository = repo.get("name")
    else:
        repository = repo

    pr = payload.get("pull_request")
    if isinstance(pr, dict):
        pr_number = pr.get("number")
        pr_title = pr.get("title")
        pr_body = pr.get("body")
        labels_raw = pr.get("labels") or []
    else:
        pr_number = payload.get("pr_number") or payload.get("pull_request_number")
        pr_title = payload.get("pr_title") or payload.get("pull_request_title")
        pr_body = payload.get("pr_body")
        labels_raw = payload.get("labels") or []

    # normalize labels
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
        "pr_number": pr_number,
        "pr_title": pr_title,
        "pr_body": pr_body,
        "labels": labels,
        "action": action,
    }

