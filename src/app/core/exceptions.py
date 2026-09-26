class ApplicationError(Exception):
    pass


class LLMError(ApplicationError):
    pass


class LLMProviderUnavailableError(LLMError):
    pass


class LLMRateLimitError(LLMError):
    pass


class LLMAuthenticationError(LLMError):
    pass


class LLMQuotaExceededError(LLMError):
    pass
