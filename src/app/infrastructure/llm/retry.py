import asyncio
import random


class RetryPolicy:
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 0.5,
        max_delay: float = 8.0,
        jitter: float = 0.5,
    ) -> None:
        self._max_attempts = max_attempts
        self._base_delay = base_delay
        self._max_delay = max_delay
        self._jitter = jitter

    async def wait(self, attempt: int) -> None:
        exponentional_delay = self._base_delay * (2**attempt)

        delay = min(
            exponentional_delay,
            self._max_delay,
        )

        delay += random.uniform(0, self._jitter)
        await asyncio.sleep(delay)

    @property
    def max_attempts(self) -> int:
        return self._max_attempts
