# app/api/webhook.py

from fastapi import APIRouter, Request, Header, Response

from app.core.logger import logger
from app.core.config import settings
from app.github.normalizer import normalize_github_event
from app.github.signature_validator import validate_github_signature
from app.github.delivery_store import is_processed, mark_processed
from app.events.dispatcher import dispatch as dispatch_github_event

router = APIRouter()


@router.post("/webhook/github")
async def github_webhook(
    request: Request,
    response: Response,
    x_github_event: str = Header(default="unknown"),
    x_hub_signature_256: str = Header(default=None),
    x_github_delivery: str = Header(default=None)
):

    # log raw request for better observability
    raw_body = await request.body()

    logger.info("=== GITHUB WEBHOOK RECEIVED ===")
    logger.info(f"Event Header: {x_github_event}")
    logger.info(f"Client: {request.client.host if request.client else 'unknown'}")
    logger.info(f"Raw Body: {raw_body.decode('utf-8', errors='replace')}")

    # If a webhook secret is configured, validate signature
    if settings.GITHUB_WEBHOOK_SECRET:

        is_valid = validate_github_signature(
            x_hub_signature_256,
            raw_body
        )

        if not is_valid:
            logger.warning("Invalid GitHub signature")
            response.status_code = 401
            return {
                "status": "unauthorized",
                "reason": "invalid signature"
            }

    # Log and enforce delivery idempotency when header is present
    logger.info(f"Delivery ID: {x_github_delivery}")

    if x_github_delivery and is_processed(x_github_delivery):
        logger.warning(f"Duplicate delivery ignored: {x_github_delivery}")
        return {"status": "ignored", "reason": "duplicate delivery"}

    # mark as processed immediately to avoid duplicate concurrent processing
    if x_github_delivery:
        mark_processed(x_github_delivery)

    try:
        payload = await request.json()
    except Exception as e:
        logger.error(f"Invalid JSON payload: {e}")
        return {
            "status": "error",
            "reason": "invalid json"
        }

    # normalize then dispatch
    normalized_event = normalize_github_event(
        x_github_event,
        payload
    )

    result = await dispatch_github_event(
        x_github_event,
        normalized_event
    )

    # mark delivery processed only after successful handling to allow retries on failure
    try:
        if x_github_delivery and isinstance(result, dict):
            status = result.get("status")
            # consider these statuses as non-success; do not mark so retries can occur
            non_success_statuses = {"error", "unauthorized", "ignored"}
            if status not in non_success_statuses:
                mark_processed(x_github_delivery)
        elif x_github_delivery and not isinstance(result, dict):
            # unknown result type but handler completed — mark as processed
            mark_processed(x_github_delivery)
    except Exception:
        # on any unexpected issue while marking, do not interrupt response
        logger.exception("Failed while marking delivery processed")

    return result