from openai import (
    AsyncOpenAI,
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    RateLimitError,
)

from app.application.chat.ports import LLMRequest, LLMResponse
from app.core.config import Settings
from app.core.exceptions import (
    LLMAuthenticationError,
    LLMProviderUnavailableError,
    LLMQuotaExceededError,
    LLMRateLimitError,
)
from app.infrastructure.llm.retry import RetryPolicy


class OpenAIProvider:
    def __init__(
        self,
        settings: Settings,
        retry_policy: RetryPolicy | None = None,
    ):
        self._client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            timeout=settings.openai_timeout_seconds,
        )
        self._model = settings.openai_model
        self._retry_policy = retry_policy or RetryPolicy()

    async def generate(self, request: LLMRequest) -> LLMResponse:
        attempt = 0

        while True:
            try:
                response = await self._client.responses.create(
                    model=self._model,
                    input=request.prompt,
                )
                return LLMResponse(content=response.output_text)

            except AuthenticationError as exc:
                raise LLMAuthenticationError(
                    "The LLM provider rejected the configured credentials."
                ) from exc

            except RateLimitError as exc:
                if attempt >= self._retry_policy.max_attempts - 1:
                    raise LLMRateLimitError(
                        "The LLM provider rate limit was exceeded."
                    ) from exc
                await self._retry_policy.wait(attempt)
                attempt += 1

            except APITimeoutError as exc:
                if attempt >= self._retry_policy.max_attempts - 1:
                    raise LLMProviderUnavailableError(
                        "The LLM provider request timed out."
                    ) from exc
                await self._retry_policy.wait(attempt)
                attempt += 1

            except APIConnectionError as exc:
                if attempt >= self._retry_policy.max_attempts - 1:
                    raise LLMProviderUnavailableError(
                        "Unable to connect to the LLM provider."
                    ) from exc

                await self._retry_policy.wait(attempt)
                attempt += 1

            except APIStatusError as exc:
                if exc.status_code == 429:
                    if attempt >= self._retry_policy.max_attempts - 1:
                        raise LLMRateLimitError(
                            "The LLM provider rate limit was exceeded."
                        ) from exc
                    await self._retry_policy.wait(attempt)
                    attempt += 1
                    continue

                if exc.status_code >= 500:
                    if attempt >= self._retry_policy.max_attempts - 1:
                        raise LLMProviderUnavailableError(
                            "The LLM provider is temporarily unavailable."
                        ) from exc
                    await self._retry_policy.wait(attempt)
                    attempt += 1
                    continue

                raise
