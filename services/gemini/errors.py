"""أخطاء Gemini المعروضة بصورة مفهومة."""


class GeminiServiceError(Exception):
    def __init__(self, message: str, code: int | None = None, original: Exception | None = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.original = original


class GeminiConfigurationError(GeminiServiceError):
    pass


class GeminiQuotaError(GeminiServiceError):
    pass


class GeminiModelError(GeminiServiceError):
    pass
