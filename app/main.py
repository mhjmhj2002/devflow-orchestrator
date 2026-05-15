from fastapi import FastAPI, Request
from app.api.webhook import router as webhook_router
from app.core.config import settings
from app.core.logger import logger
from app.api.context import router as context_router

app = FastAPI(
    title=settings.APP_NAME
)


@app.get("/health")
async def health():

    logger.info("Healthcheck called")

    return {
        "status": "ok"
    }


app.include_router(webhook_router)

app.include_router(context_router)


@app.post("/")
async def root(request: Request):
    """Simple root POST handler to log unexpected traffic hitting '/'.

    GitHub or external scanners sometimes POST to the root URL; having
    this handler improves observability during webhook debugging.
    """

    raw = await request.body()
    logger.info("=== ROOT RECEIVED ===")
    logger.info(f"Client: {request.client.host if request.client else 'unknown'}")
    logger.info(f"Raw Body: {raw.decode('utf-8', errors='replace')}")

    return {"status": "ok", "message": "root endpoint - use /webhook/github"}

logger.info("DevFlow Orchestrator started")
