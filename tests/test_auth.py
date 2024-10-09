"""Contains tests for SDK authentication."""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any

from aioresponses import CallbackResult, aioresponses
from statelydb.src.auth import init_server_auth


async def test_token_provider() -> None:
    count = 0
    delay = 0.1
    expiry = 0.1
    # the timer isn't 100% accurate so we allow a small delta on time based assertions
    allowed_delta = 0.1
    semaphore = asyncio.Semaphore(1)
    await semaphore.acquire()

    async def make_resp(_url: str, **_kwargs: dict[str, Any]) -> CallbackResult:
        nonlocal count, delay, semaphore
        await asyncio.sleep(delay)
        count += 1
        if count >= 2:
            # release the semaphore to allow us to make the second assertion
            semaphore.release()
        return CallbackResult(
            status=200,
            method="POST",
            payload={"access_token": f"test_token-{count}", "expires_in": expiry},
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
            refresh_buffer=0,
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

        # wait for the refresh request to go through
        # which will trigger the semaphore release
        started_waiting = datetime.now()
        await semaphore.acquire()
        # check that the token was refreshed
        assert await get_token() == "test_token-2"
        assert (datetime.now() - started_waiting).total_seconds() >= (
            1 - allowed_delta
        ) * expiry + delay
        assert (datetime.now() - started_waiting).total_seconds() <= (
            1 + allowed_delta
        ) * expiry + delay

        # wait for another request to go through to verify that the refresh task
        # works multiple times.
        await semaphore.acquire()
        assert await get_token() == "test_token-3"


def test_token_provider_sync_context() -> None:
    async def make_resp(_url: str, **_kwargs: dict[str, Any]) -> CallbackResult:
        return CallbackResult(
            status=200,
            method="POST",
            payload={"access_token": "test_token", "expires_in": 5},
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
            refresh_buffer=0,
        )

        token = asyncio.run(get_token())
        assert token == "test_token"  # noqa: S105
