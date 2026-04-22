import pytest
import json
import hmac
import hashlib
from unittest.mock import patch, MagicMock, AsyncMock
from kosatka_master.webhooks import send_webhook
from kosatka_master.config import settings

@pytest.mark.asyncio
async def test_send_webhook_success():
    url = "http://test-webhook.com"
    payload = {"event": "test", "data": "hello"}
    
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        status_code = await send_webhook(url, payload)
        
        assert status_code == 200
        
        # Verify signature
        payload_str = json.dumps(payload)
        expected_signature = hmac.new(
            settings.webhook_secret.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        args, kwargs = mock_post.call_args
        assert kwargs["headers"]["X-Kosatka-Signature"] == expected_signature
        assert kwargs["data"] == payload_str

@pytest.mark.asyncio
async def test_send_webhook_failure():
    url = "http://test-webhook.com"
    payload = {"event": "test"}
    
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.side_effect = Exception("Connection error")
        
        status_code = await send_webhook(url, payload)
        
        assert status_code is None
