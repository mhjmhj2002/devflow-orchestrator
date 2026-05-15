"""app/workflows/comment_workflow.py

Handle issue comment events (approval parsing) and trigger code generation workflow.
"""

from typing import Any, Dict

from app.core.logger import logger
from app.github.github_commenter import post_github_comment
from app.codegen.codegen_orchestrator import start_codegen_workflow
import os


APPROVAL_COMMANDS = ["/approve", "/devflow approve", "approve"]


async def start_comment_workflow(event: Dict[str, Any]):

    # event may be either dict (from workflow_router) or already flattened
    repository = event.get("repository")

    # when router hands a Pydantic dumped model it will have 'repository' as dict
    if isinstance(repository, dict):
        repo_name = repository.get("name")
    else:
        repo_name = repository

    issue_number = event.get("issue_number")

    # comment body may be nested under 'comment' or 'comment_body'
    comment = event.get("comment") or {}
    comment_body = comment.get("body") if isinstance(comment, dict) else event.get("comment_body")

    logger.info(f"Processing comment on {repo_name}#{issue_number}: {str(comment_body)[:120]}")

    comment_text = (comment_body or "").strip().lower()

    approved = any(cmd in comment_text for cmd in APPROVAL_COMMANDS)

    if not approved:
        logger.info("Comment not an approval; ignoring")
        return {"status": "ignored", "reason": "no approval command"}

    logger.info("Approval detected; starting code generation workflow")

    try:
        result = start_codegen_workflow({
            "repository": repo_name,
            "issue_number": issue_number,
            "comment": comment,
        })

        # try to notify the issue that generation started (skip in dry-run)
        try:
            if os.getenv("DEVFLOW_DRY_RUN", "false").lower() not in ("1", "true", "yes"):
                post_github_comment(
                    repository=repo_name,
                    issue_number=issue_number,
                    body=f"DevFlow: code generation started (workflow result: {result})"
                )
            else:
                logger.info("DRY RUN: skipping post_github_comment for generation start")
        except Exception:
            logger.exception("Failed to post start comment")

        return {"status": "codegen_started", "result": result}

    except Exception as e:
        logger.exception("Error starting codegen workflow")
        return {"status": "error", "reason": str(e)}

