"""Contains tests for SDK authentication."""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any

from aioresponses import CallbackResult, aioresponses
from grpclib.server import Server, Stream
from grpclib.utils import graceful_exit
from statelydb.lib.api.auth import get_auth_token_pb2
from statelydb.lib.api.auth.service_grpc import AuthServiceBase
from statelydb.src.auth import init_server_auth


async def test_auth0_token_provider() -> None:
    count = 0
    delay = 0.1
    expiry = 0.1
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
            origin="http://localhost",
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
        await semaphore.acquire()
        # check that the token was refreshed
        assert await get_token() == "test_token-2"

        # wait for another request to go through to verify that the refresh task
        # works multiple times.
        await semaphore.acquire()
        assert await get_token() == "test_token-3"


def test_auth0_token_provider_sync_context() -> None:
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
            origin="http://localhost",
        )

        token = asyncio.run(get_token())
        assert token == "test_token"  # noqa: S105


async def test_auth0_token_provider_refresh_error() -> None:
    """Tests that the token provider retries the request when it receives an error."""
    count = 0
    success = CallbackResult(
        status=200,
        method="POST",
        payload={"access_token": "test_token", "expires_in": 5},
    )
    error = CallbackResult(
        status=500,
        method="POST",
    )

    async def make_resp(_url: str, **_kwargs: dict[str, Any]) -> CallbackResult:
        nonlocal count
        count += 1
        # return one error then return success after that
        if count > 1:
            return success
        return error

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
            origin="http://localhost",
        )

        token = await get_token()
        assert token == "test_token"  # noqa: S105
        assert count == 2


class MockAuthService(AuthServiceBase):
    def __init__(self, *, token: str, expires_in_sec: int, expected_key: str) -> None:
        self.token = token
        self.expires_in_sec = expires_in_sec
        self.expected_key = expected_key

    async def GetAuthToken(  # noqa: N802
        self,
        stream: Stream[
            get_auth_token_pb2.GetAuthTokenRequest,
            get_auth_token_pb2.GetAuthTokenResponse,
        ],
    ) -> None:
        req = await stream.recv_message()
        assert req is not None
        if self.expected_key != req.access_key:
            msg = "Invalid access key"
            raise ValueError(msg)
        await stream.send_message(
            get_auth_token_pb2.GetAuthTokenResponse(
                auth_token=self.token, expires_in_s=self.expires_in_sec
            )
        )


async def test_stately_token_provider() -> None:
    server = Server(
        [MockAuthService(token="test_token", expires_in_sec=5, expected_key="test_key")]
    )
    with graceful_exit([server]):
        await server.start("127.0.0.1")
        port = server._server.sockets[0].getsockname()[1]  # type: ignore[reportUnknownMemberType,union-attr] # noqa: SLF001

        get_token = init_server_auth(
            access_key="test_key",
            origin=f"http://127.0.0.1:{port}",
        )

        token = await get_token()
        assert token == "test_token"  # noqa: S105
