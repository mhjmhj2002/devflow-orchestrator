import os
import requests
from requests import RequestException

from app.core.logger import logger


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_OWNER = os.getenv("GITHUB_OWNER")


def post_github_comment(
        repository: str,
        issue_number: int,
        body: str
):
    """
    Post a comment to a GitHub issue. This function is resilient and will
    catch network/HTTP errors and return a structured result instead of
    raising, allowing callers to decide how to handle failures.
    """

    if not GITHUB_TOKEN or not GITHUB_OWNER:
        logger.warning("GitHub credentials not configured: skipping comment post")
        return {"status": "skipped", "reason": "missing credentials"}

    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{repository}/issues/{issue_number}/comments"

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json={
                "body": body
            },
            timeout=10
        )

        response.raise_for_status()

        return {"status": "ok", "result": response.json()}

    except RequestException as e:
        # capture response status code/message when available
        status_code = None
        try:
            status_code = e.response.status_code if hasattr(e, "response") and e.response is not None else None
        except Exception:
            status_code = None

        logger.error(f"Failed to post GitHub comment: {e} (status={status_code})")

        return {"status": "error", "reason": str(e), "status_code": status_code}
