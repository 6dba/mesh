class KosatkaError(Exception):
    """Base exception for Kosatka SDK"""
    pass

class KosatkaAPIError(KosatkaError):
    """Raised when the API returns an error"""
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"API Error {status_code}: {detail}")

class KosatkaAuthError(KosatkaAPIError):
    """Raised when authentication fails"""
    pass

class KosatkaValidationError(KosatkaError):
    """Raised when local validation fails"""
    pass

class KosatkaWebhookError(KosatkaError):
    """Raised when webhook verification fails"""
    pass
