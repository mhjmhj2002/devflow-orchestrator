# app/events/dispatcher.py

from app.events.validator import EventValidator
from app.workflows.workflow_router import route_workflow
from app.core.logger import logger


async def dispatch(event_name: str, payload: dict):

    event, error = EventValidator.validate(event_name, payload)

    if error:
        logger.warning(f"Event rejected: {error}")
        return {
            "status": "ignored",
            "reason": error
        }

    logger.info(f"Event accepted: {event.event_type}")

    # route_workflow understands either raw dicts or Pydantic models
    return await route_workflow(event)

