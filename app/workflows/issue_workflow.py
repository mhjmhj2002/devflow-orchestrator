# app/workflows/issue_workflow.py

from app.core.logger import logger

from app.agents.planning_agent import generate_plan

from app.project_context.context_builder import (
    build_project_context
)

from app.project_context.context_registry import (
    get_project_path
)

from app.skills.plan_markdown_generator import generate_markdown_plan
from app.skills.plan_file_writer import save_plan
import json
from app.github.github_commenter import post_github_comment


async def handle_issue_opened(event: dict):

    repository = event.get("repository")
    issue_title = event.get("issue_title")
    issue_number = event.get("issue_number")

    logger.info(
        f"Starting workflow for repo={repository}"
    )

    # =========================
    # VALIDATE REPOSITORY
    # =========================

    if not repository:
        logger.error("Repository missing in event payload")

        return {
            "status": "error",
            "reason": "repository missing"
        }

    # =========================
    # LOAD PROJECT PATH
    # =========================

    repo_path = get_project_path(repository)

    if not repo_path:
        logger.error(
            f"Repository not registered: {repository}"
        )

        # if no specific mapping found for repository, return ignored
        return {
            "status": "ignored",
            "reason": f"repository not mapped: {repository}"
        }

    # =========================
    # BUILD CONTEXT
    # =========================

    project_context = build_project_context(
        repo_path=repo_path,
        repository=repository
    )

    logger.info(f"Project context: {project_context}")

    # choose target service (if provided) or fallback
    target = event.get("service") or repository

    service_context = None
    for s in project_context.services:
        if s.name == target or s.name in target:
            service_context = s
            break

    if not service_context and project_context.services:
        service_context = project_context.services[0]

    if not service_context:
        service_context = project_context

    plan = await generate_plan(
        issue_title=issue_title,
        context=service_context
    )

    logger.info(f"Generated plan:\n{plan}")

    clean_plan = plan.replace("```json", "").replace("```", "")

    plan_json = json.loads(clean_plan)

    markdown = generate_markdown_plan(
        issue_title=issue_title,
        issue_number=issue_number,
        project_context=project_context,
        service_context=service_context,
        plan=plan_json
    )

    saved_file = save_plan(
        issue_number,
        markdown
    )

    try:
        comment_result = post_github_comment(
            repository=repository,
            issue_number=issue_number,
            body=markdown
        )

        if isinstance(comment_result, dict) and comment_result.get("status") != "ok":
            logger.warning(f"Posting GitHub comment returned non-ok status: {comment_result}")

    except Exception:
        logger.exception("Unexpected error while posting GitHub comment")

    return {
        "status": "planning_completed",
        "repository": repository,
        "issue": issue_title,
        "plan_file": saved_file
    }