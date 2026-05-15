from app.core.logger import logger
from app.workflows.issue_workflow import execute_issue_workflow


async def dispatch_github_event(event: str, payload: dict):

    logger.info(f"Dispatching event: {event}")

    logger.info(f"Normalized payload: {payload}")

    if event == "issues":

        if payload.get("action") == "opened":

            return await execute_issue_workflow(payload)

    if event == "issue_comment":

        return {
            "workflow": "comment_workflow",
            "status": "accepted"
        }

    return {
        "workflow": "ignored",
        "status": "ignored"
    }