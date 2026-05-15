# app/events/mapper.py

from app.core.logger import logger


def map_event(event_name: str, payload: dict):

    logger.info(f"Mapping event: {event_name}")

    # Simple, strict mapping wrapper. In the future it can transform
    # fields, normalize names and add metadata (version, received_at, etc.)
    return {
        "event_type": event_name,
        "payload": payload
    }

