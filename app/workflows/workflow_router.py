# app/workflows/workflow_router.py

from app.workflows.planning_workflow import start_planning_workflow
from app.workflows.comment_workflow import start_comment_workflow
from pydantic import BaseModel


async def route_workflow(event):

    # support both legacy dict events and new Pydantic event contracts
    if isinstance(event, BaseModel):
        # contract event_type uses format resource.action (e.g. issues.opened)
        raw_event_type = getattr(event, "event_type", "")
        parts = raw_event_type.split(".")
        event_type = parts[0] if parts else None
        action = parts[1] if len(parts) > 1 else None

        # convert model to a flattened payload expected by existing workflows
        dumped = event.model_dump()

        # IssueOpenedEvent shape: { repository: {name}, issue: {number,title,...}, service }
        if event_type == "issues":
            repo = dumped.get("repository") or {}
            issue = dumped.get("issue") or {}

            event_payload = {
                "event": "issues",
                "action": "opened" if action == "opened" else action,
                "repository": repo.get("name") if isinstance(repo, dict) else repo,
                "issue_title": issue.get("title"),
                "issue_number": issue.get("number"),
                "service": dumped.get("service")
            }
        else:
            event_payload = dumped
    else:
        event_type = event.get("event")
        action = event.get("action")
        event_payload = event

    # ISSUE OPENED -> start planning workflow
    if event_type == "issues" and action == "opened":
        return await start_planning_workflow(event_payload)

    # ISSUE COMMENT CREATED -> comment workflow (approval parsing)
    if event_type == "issue_comment" and action == "created":
        return await start_comment_workflow(event_payload)

    return {
        "status": "ignored",
        "reason": "event not supported"
    }