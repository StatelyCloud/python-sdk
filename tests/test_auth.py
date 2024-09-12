"""Contains tests for SDK authentication."""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any

from aioresponses import CallbackResult, aioresponses
from statelydb.src.auth import init_server_auth


async def test_token_provider() -> None:
    count = 0
    delay = 1

    async def make_resp(_url: str, **_kwargs: dict[str, Any]) -> CallbackResult:
        nonlocal count, delay
        await asyncio.sleep(delay)
        count += 1
        return CallbackResult(
            status=200,
            method="POST",
            payload={"access_token": f"test_token-{count}", "expires_in": 5},
        )

    with aioresponses() as http_mock:
        http_mock.post(  # type: ignore[reportUnknownMemberType]
            "http://localhost/oauth/token",
            callback=make_resp,
            repeat=True,
        )

        get_token = init_server_auth(
            client_id="test_id",
            client_secret="test_secret",
            audience="test_audience",
            auth_domain="http://localhost",
        )

        start = datetime.now()
        tasks = [get_token() for _ in range(200)]
        tokens = await asyncio.gather(*tasks)
        for token in tokens:
            assert token == "test_token-1"  # noqa: S105
        duration = datetime.now() - start
        # we ran the operation 10 times so if the dedupe operation
        # failed the total duration would be 10x the delay
        assert duration.total_seconds() < 10 * delay
