#!/usr/bin/env python3
# scripts/test_webhook.py

import asyncio
import json
import hmac
import hashlib
import uuid
from app.core.config import settings
from app.api.webhook import github_webhook


async def run():

    payload = {
        "action": "opened",
        "repository": {"name": "devflow-ai"},
        "issue": {
            "number": 1,
            "title": "Create POST /users endpoint",
            "labels": [{"name": "service:identity-service"}]
        }
    }

    class DummyClient:
        def __init__(self, host="127.0.0.1"):
            self.host = host

    class DummyRequest:
        def __init__(self, payload):
            self._payload = payload
            self.client = DummyClient()
            self._raw = json.dumps(payload).encode("utf-8")

        async def body(self):
            return self._raw

        async def json(self):
            return self._payload

    request = DummyRequest(payload)

    # compute signature header using configured secret (if any)
    sig_header = None
    if settings.GITHUB_WEBHOOK_SECRET:
        sig = hmac.new(
            settings.GITHUB_WEBHOOK_SECRET.encode(),
            request._raw,
            hashlib.sha256
        ).hexdigest()
        sig_header = f"sha256={sig}"

    # generate a delivery id to simulate GitHub's X-GitHub-Delivery
    delivery_id = str(uuid.uuid4())

    result = await github_webhook(
        request,
        None,
        x_github_event="issues",
        x_hub_signature_256=sig_header,
        x_github_delivery=delivery_id
    )

    print("\n=== WEBHOOK RESULT ===\n")
    print(result)


if __name__ == "__main__":
    asyncio.run(run())

