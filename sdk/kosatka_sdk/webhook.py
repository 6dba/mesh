import hmac
import hashlib
import json
from typing import Dict, Any
from .exceptions import KosatkaWebhookError
from .models import WebhookEvent

class KosatkaWebhookHandler:
    def __init__(self, webhook_secret: str):
        self.webhook_secret = webhook_secret

    def verify_signature(self, payload: str, signature: str) -> bool:
        """
        Verify the signature of a webhook request.
        payload: raw body of the request
        signature: value from X-Kosatka-Signature header
        """
        expected_signature = hmac.new(
            self.webhook_secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)

    def parse_event(self, payload: str, signature: str) -> WebhookEvent:
        if not self.verify_signature(payload, signature):
            raise KosatkaWebhookError("Invalid webhook signature")
        
        try:
            data = json.loads(payload)
            return WebhookEvent.model_validate(data)
        except Exception as e:
            raise KosatkaWebhookError(f"Failed to parse webhook payload: {str(e)}")
