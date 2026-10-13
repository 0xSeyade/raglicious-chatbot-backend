class ApplicationError(Exception):
    """Base class for expected application errors."""


class LLMError(ApplicationError):
    """Base class for LLM-related errors."""


class LLMProviderUnavailableError(LLMError):
    """The LLM provider is temporarily unavailable."""


class LLMRateLimitError(LLMError):
    """The LLM provider rate limit was exceeded."""


class LLMAuthenticationError(LLMError):
    """The LLM provider rejected the configured credentials."""


class LLMQuotaExceededError(LLMError):
    """The LLM provider account exceeded its quota."""


class ConversationNotFoundError(ApplicationError):
    """The requested conversation does not exist."""
