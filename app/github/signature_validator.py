import hmac
import hashlib
from app.core.config import settings


def validate_github_signature(
    signature_header: str,
    payload_body: bytes
) -> bool:

    if not signature_header:
        return False

    secret = settings.GITHUB_WEBHOOK_SECRET.encode()

    expected_signature = "sha256=" + hmac.new(
        secret,
        payload_body,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(
        expected_signature,
        signature_header
    )

