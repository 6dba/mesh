import hashlib
import hmac
import json

import httpx

from .config import settings


async def send_webhook(url: str, payload: dict):
    payload_str = json.dumps(payload)
    signature = hmac.new(
        settings.webhook_secret.encode(), payload_str.encode(), hashlib.sha256
    ).hexdigest()

    headers = {"Content-Type": "application/json", "X-Kosatka-Signature": signature}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, data=payload_str, headers=headers, timeout=10.0)
            return response.status_code
        except Exception as e:
            # Log error
            print(f"Failed to send webhook to {url}: {e}")
            return None
