"""Reviewer Agent

Performs an automated review of a pull request using a simple LLM prompt and
posts a summary back. This is an MVP: it fetches PR files via the GitHub API,
builds a compact prompt including patches, asks the LLM for a review and
returns the textual review.
"""

import os
import requests
from requests import RequestException
from typing import Optional

from app.llm.openai_client import generate_text
from app.core.logger import logger


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_OWNER = os.getenv("GITHUB_OWNER")


def _headers():
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }


def fetch_pr_files(repository: str, pr_number: int) -> Optional[list]:
    if not GITHUB_TOKEN or not GITHUB_OWNER:
        logger.warning("GitHub credentials not configured: cannot fetch PR files")
        return None

    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{repository}/pulls/{pr_number}/files"
    try:
        resp = requests.get(url, headers=_headers(), timeout=20)
        resp.raise_for_status()
        return resp.json()
    except RequestException as e:
        logger.error(f"Failed to fetch PR files: {e}")
        return None


def review_pull_request(repository: str, pr_number: int) -> Optional[str]:
    """Fetch PR files and create an automated review using the LLM.

    Returns textual review or None if not available.
    """
    files = fetch_pr_files(repository, pr_number)
    if not files:
        return None

    # build a compact prompt using file names and patches (limit size)
    prompt_parts = [
        "You are a senior code reviewer. Provide a concise technical review focusing on: architecture, security, naming, test coverage, and potential regressions.",
        f"Repository: {repository}",
        f"Pull Request: #{pr_number}",
        "Files changed:"
    ]

    total_chars = 0
    for f in files:
        name = f.get("filename")
        patch = f.get("patch") or ""
        snippet = patch[:2000]
        part = f"--- {name} ---\n{snippet}\n"
        prompt_parts.append(part)
        total_chars += len(part)
        if total_chars > 6000:
            prompt_parts.append("...truncated...")
            break

    prompt_parts.append("Write a short review (max 600 words) with actionable items and severity levels (info/warning/error).")

    prompt = "\n\n".join(prompt_parts)

    # if OpenAI key missing, skip
    try:
        review = None
        # generate_text is async; run it in a background thread to avoid
        # "asyncio.run() cannot be called from a running event loop" when
        # this function is invoked from an existing event loop (e.g. uvicorn).
        import asyncio
        import concurrent.futures

        def _run():
            return asyncio.run(generate_text(prompt))

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
            fut = ex.submit(_run)
            review = fut.result()

        return review
    except Exception as e:
        logger.exception(f"LLM review failed: {e}")
        return None

