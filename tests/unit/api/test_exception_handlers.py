import pytest

from fastapi import Request

from app.api.exception_handlers import handle_llm_rate_limit
from app.core.exceptions import LLMRateLimitError


@pytest.mark.asyncio
async def test_llm_rate_limit_returns_429() -> None:
    request = Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/api/v1/chat",
            "headers": [],
            "query_string": b"",
            "server": ("testserver", 80),
            "scheme": "http",
            "client": ("testclient", 50000),
        }
    )

    response = await handle_llm_rate_limit(
        request,
        LLMRateLimitError(),
    )

    assert response.status_code == 429
