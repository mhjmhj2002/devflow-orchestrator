# app/workflows/planning_workflow.py

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


async def start_planning_workflow(event: dict):

    repository = event.get("repository")
    issue_title = event.get("issue_title")
    issue_number = event.get("issue_number")

    logger.info(
        f"Starting planning workflow for repo={repository}"
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

    # if a target service was specified (via labels or issue template), prefer it
    target = event.get("service") or repository

    repo_path = get_project_path(target)

    if not repo_path:
        logger.error(
            f"Repository/Service not registered: {target}"
        )

        # if the event explicitly targeted a service and it's not mapped -> error
        if event.get("service"):
            return {
                "status": "error",
                "reason": f"repository/service not mapped: {target}"
            }

        # if no service label was provided, prefer to ignore the event instead of failing
        return {
            "status": "ignored",
            "reason": "missing service mapping"
        }

    # =========================
    # BUILD CONTEXT (service-aware)
    # =========================

    project_context = build_project_context(
        repo_path=repo_path,
        repository=repository
    )

    logger.info(f"Project context: {project_context}")

    # choose target service (from event labels) or fallback to repository
    target = event.get("service") or repository

    # find matching service context
    service_context = None
    for s in project_context.services:
        if s.name == target or s.name in target:
            service_context = s
            break

    # fallback: first service or a minimal context built from project root
    if not service_context and project_context.services:
        service_context = project_context.services[0]

    if not service_context:
        # minimal fallback
        service_context = project_context

    # =========================
    # GENERATE PLAN (per-service)
    # =========================

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

    # attempt to post GitHub comment; don't let failing comment break the workflow
    try:
        comment_result = post_github_comment(
            repository=repository,
            issue_number=issue_number,
            body=markdown
        )

        if isinstance(comment_result, dict) and comment_result.get("status") != "ok":
            logger.warning(f"Posting GitHub comment returned non-ok status: {comment_result}")

    except Exception as e:
        # should not happen because post_github_comment handles exceptions, but be extra safe
        logger.exception("Unexpected error while posting GitHub comment")

    return {
        "status": "planning_completed",
        "repository": repository,
        "issue": issue_title,
        "plan_file": saved_file
    }

