import os
import requests
from requests import RequestException

from app.core.logger import logger


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_OWNER = os.getenv("GITHUB_OWNER")


def _headers():
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }


def get_default_branch(repository: str):
    if not GITHUB_TOKEN or not GITHUB_OWNER:
        logger.warning("GitHub credentials not configured: cannot get default branch")
        return None

    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{repository}"
    try:
        resp = requests.get(url, headers=_headers(), timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("default_branch")
    except RequestException as e:
        logger.error(f"Failed to fetch repo info for {repository}: {e}")
        return None


def create_pull_request(repository: str, head: str, base: str = None, title: str = None, body: str = None, requested_reviewers: list | None = None):
    """Create a pull request on GitHub. Returns dict with status and result/error."""

    if not GITHUB_TOKEN or not GITHUB_OWNER:
        logger.warning("GitHub credentials not configured: skipping PR creation")
        return {"status": "skipped", "reason": "missing credentials"}

    if base is None:
        base = get_default_branch(repository) or "main"

    if title is None:
        title = f"AI generated changes: {head}"

    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{repository}/pulls"

    payload = {
        "title": title,
        "head": head,
        "base": base,
        "body": body or "AI generated changes by DevFlow"
    }

    # include requested reviewers when provided
    if requested_reviewers:
        # GitHub API expects a list under 'requested_reviewers'
        payload["requested_reviewers"] = requested_reviewers

    try:
        resp = requests.post(url, headers=_headers(), json=payload, timeout=10)
        resp.raise_for_status()
        return {"status": "ok", "result": resp.json()}
    except RequestException as e:
        status_code = None
        try:
            status_code = e.response.status_code if hasattr(e, "response") and e.response is not None else None
        except Exception:
            status_code = None

        logger.error(f"Failed to create PR for {repository}: {e} (status={status_code})")
        return {"status": "error", "reason": str(e), "status_code": status_code}


def update_pull_request(repository: str, pr_number: int, body: str = None, title: str = None):
    """Patch an existing PR to update title/body."""
    if not GITHUB_TOKEN or not GITHUB_OWNER:
        logger.warning("GitHub credentials not configured: skipping PR update")
        return {"status": "skipped", "reason": "missing credentials"}

    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{repository}/pulls/{pr_number}"
    payload = {}
    if body is not None:
        payload["body"] = body
    if title is not None:
        payload["title"] = title

    try:
        resp = requests.patch(url, headers=_headers(), json=payload, timeout=10)
        resp.raise_for_status()
        return {"status": "ok", "result": resp.json()}
    except RequestException as e:
        status_code = None
        try:
            status_code = e.response.status_code if hasattr(e, "response") and e.response is not None else None
        except Exception:
            status_code = None

        logger.error(f"Failed to update PR #{pr_number} for {repository}: {e} (status={status_code})")
        return {"status": "error", "reason": str(e), "status_code": status_code}


