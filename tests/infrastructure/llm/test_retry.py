import pytest
from unittest.mock import AsyncMock, patch

from app.infrastructure.llm.retry import RetryPolicy


@pytest.mark.asyncio
async def test_retry_policy_uses_exponential_backoff() -> None:
    policy = RetryPolicy(
        base_delay=1.0,
        jitter=0.0,
    )

    with patch(
        "app.infrastructure.llm.retry.asyncio.sleep",
        new_callable=AsyncMock,
    ) as mock_sleep:
        await policy.wait(0)
        await policy.wait(1)
        await policy.wait(2)

    assert mock_sleep.await_args_list[0].args == (1.0,)
    assert mock_sleep.await_args_list[1].args == (2.0,)
    assert mock_sleep.await_args_list[2].args == (4.0,)
