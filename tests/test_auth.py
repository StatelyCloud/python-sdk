"""Contains tests for SDK authentication."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable
from datetime import datetime
from typing import Callable

import pytest
from grpclib.const import Status
from grpclib.exceptions import GRPCError
from grpclib.server import Server, Stream
from grpclib.utils import graceful_exit
from statelydb.lib.api.auth import get_auth_token_pb2
from statelydb.lib.api.auth.service_grpc import AuthServiceBase
from statelydb.src.auth import NON_RETRYABLE_ERRORS, RETRY_ATTEMPTS, init_server_auth
from statelydb.src.errors import StatelyError

GetAuthTokenHandler = Callable[
    [
        Stream[
            get_auth_token_pb2.GetAuthTokenRequest,
            get_auth_token_pb2.GetAuthTokenResponse,
        ]
    ],
    Awaitable[None],
]


class MockAuthService(AuthServiceBase):
    def __init__(self, *, handler: GetAuthTokenHandler) -> None:
        self._handler = handler

    async def GetAuthToken(  # noqa: N802
        self,
        stream: Stream[
            get_auth_token_pb2.GetAuthTokenRequest,
            get_auth_token_pb2.GetAuthTokenResponse,
        ],
    ) -> None:
        await self._handler(stream)


async def test_stately_token_provider_basic_functionalality() -> None:
    """A simple test to ensure that the token provider invokes the grpc backend as expected."""

    async def handler(
        stream: Stream[
            get_auth_token_pb2.GetAuthTokenRequest,
            get_auth_token_pb2.GetAuthTokenResponse,
        ],
    ) -> None:
        req = await stream.recv_message()
        assert req is not None
        assert req.access_key == "test_key"
        await stream.send_message(
            get_auth_token_pb2.GetAuthTokenResponse(
                auth_token="test_token", expires_in_s=1
            )
        )

    server = Server([MockAuthService(handler=handler)])
    with graceful_exit([server]):
        await server.start("127.0.0.1")
        port = server._server.sockets[0].getsockname()[1]  # type: ignore[reportUnknownMemberType,union-attr] # noqa: SLF001

        init, stop = init_server_auth(access_key="test_key")
        get_token = init(f"http://127.0.0.1:{port}")

        token = await get_token()
        assert token == "test_token"  # noqa: S105
        stop()
    server.close()
    await server.wait_closed()


async def test_token_provider_refresh() -> None:
    count = 0
    delay = 0.1
    expiry = 1
    semaphore = asyncio.Semaphore(1)
    await semaphore.acquire()

    async def handler(
        stream: Stream[
            get_auth_token_pb2.GetAuthTokenRequest,
            get_auth_token_pb2.GetAuthTokenResponse,
        ],
    ) -> None:
        nonlocal count, delay, semaphore
        _req = await stream.recv_message()
        await asyncio.sleep(delay)
        count += 1
        if count >= 2:
            # release the semaphore to allow us to make the second assertion
            semaphore.release()
        await stream.send_message(
            get_auth_token_pb2.GetAuthTokenResponse(
                auth_token=f"test_token-{count}", expires_in_s=expiry
            )
        )

    server = Server([MockAuthService(handler=handler)])
    with graceful_exit([server]):
        await server.start("127.0.0.1")
        port = server._server.sockets[0].getsockname()[1]  # type: ignore[reportUnknownMemberType,union-attr] # noqa: SLF001

        init, stop = init_server_auth(access_key="test_key")
        get_token = init(f"http://127.0.0.1:{port}")

        start = datetime.now()
        tasks = [get_token() for _ in range(200)]
        tokens = await asyncio.gather(*tasks)
        for token in tokens:
            assert token == "test_token-1"  # noqa: S105
        duration = datetime.now() - start
        # we ran the operation RETRY_ATTEMPTS times so if the dedupe operation
        # failed the total duration would be RETRY_ATTEMPTS times the delay
        assert duration.total_seconds() < RETRY_ATTEMPTS * delay

        # wait for the refresh request to go through
        # which will trigger the semaphore release
        await semaphore.acquire()
        # check that the token was refreshed
        assert await get_token() == "test_token-2"

        # wait for another request to go through to verify that the refresh task
        # works multiple times.
        await semaphore.acquire()
        assert await get_token() == "test_token-3"
        stop()
    server.close()
    await server.wait_closed()


def test_token_provider_sync_context() -> None:
    async def handler(
        stream: Stream[
            get_auth_token_pb2.GetAuthTokenRequest,
            get_auth_token_pb2.GetAuthTokenResponse,
        ],
    ) -> None:
        _req = await stream.recv_message()
        await stream.send_message(
            get_auth_token_pb2.GetAuthTokenResponse(
                auth_token="test_token", expires_in_s=5
            )
        )

    server = Server([MockAuthService(handler=handler)])
    with graceful_exit([server]):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(server.start("127.0.0.1"))
        port = server._server.sockets[0].getsockname()[1]  # type: ignore[reportUnknownMemberType,union-attr] # noqa: SLF001

        init, stop = init_server_auth(access_key="test_key")
        get_token = init(f"http://127.0.0.1:{port}")
        token = loop.run_until_complete(get_token())
        assert token == "test_token"  # noqa: S105
        stop()
    server.close()


async def test_token_provider_transient_network_error() -> None:
    """Tests that the token provider retries the request when it receives an error."""
    count = 0

    async def handler(
        stream: Stream[
            get_auth_token_pb2.GetAuthTokenRequest,
            get_auth_token_pb2.GetAuthTokenResponse,
        ],
    ) -> None:
        nonlocal count
        count += 1
        _req = await stream.recv_message()
        if count > 1:
            await stream.send_message(
                get_auth_token_pb2.GetAuthTokenResponse(
                    auth_token="test_token", expires_in_s=5
                )
            )
        else:
            msg = "test error"
            raise ValueError(msg)

    server = Server([MockAuthService(handler=handler)])
    with graceful_exit([server]):
        await server.start("127.0.0.1")
        port = server._server.sockets[0].getsockname()[1]  # type: ignore[reportUnknownMemberType,union-attr] # noqa: SLF001
        init, stop = init_server_auth(access_key="test_key")
        get_token = init(f"http://127.0.0.1:{port}")
        token = await get_token()
        assert token == "test_token"  # noqa: S105
        assert count == 2
        stop()
    server.close()
    await server.wait_closed()


async def test_token_provider_permanent_network_error() -> None:
    """Tests that the token provider eventually propagates the error if it doesn't resolve."""
    count = 0

    async def handler(
        _stream: Stream[
            get_auth_token_pb2.GetAuthTokenRequest,
            get_auth_token_pb2.GetAuthTokenResponse,
        ],
    ) -> None:
        nonlocal count
        count += 1
        msg = "test error"
        raise ValueError(msg)

    server = Server([MockAuthService(handler=handler)])
    with graceful_exit([server]):
        await server.start("127.0.0.1")
        port = server._server.sockets[0].getsockname()[1]  # type: ignore[reportUnknownMemberType,union-attr] # noqa: SLF001
        init, stop = init_server_auth(
            access_key="test_key",
            base_retry_backoff_secs=0.01,
        )
        get_token = init(f"http://127.0.0.1:{port}")

        with pytest.raises(StatelyError):
            await get_token()
        assert count == RETRY_ATTEMPTS
        stop()
    server.close()
    await server.wait_closed()


@pytest.mark.parametrize(
    ("code", "retryable"),
    [(err, False) for err in NON_RETRYABLE_ERRORS]
    + [(Status.UNKNOWN, True), (Status.UNAVAILABLE, True)],
)
async def test_token_provider_non_retryable_codes(
    code: Status, retryable: bool
) -> None:
    """Tests that the token provider doesn't retry on non-retryable errors."""
    count = 0

    async def handler(
        _stream: Stream[
            get_auth_token_pb2.GetAuthTokenRequest,
            get_auth_token_pb2.GetAuthTokenResponse,
        ],
    ) -> None:
        nonlocal count
        count += 1
        raise GRPCError(
            status=code,
        )

    server = Server([MockAuthService(handler=handler)])
    with graceful_exit([server]):
        await server.start("127.0.0.1")
        port = server._server.sockets[0].getsockname()[1]  # type: ignore[reportUnknownMemberType,union-attr] # noqa: SLF001
        init, stop = init_server_auth(
            access_key="test_key",
            base_retry_backoff_secs=0.01,
        )
        get_token = init(f"http://127.0.0.1:{port}")

        with pytest.raises(StatelyError):
            await get_token()
        assert count == (RETRY_ATTEMPTS if retryable else 1)
        stop()
    server.close()
    await server.wait_closed()


@pytest.mark.parametrize("code", [Status.UNAVAILABLE, Status.UNKNOWN])
async def test_token_provider_retryable_codes(code: Status) -> None:
    """Tests that the token provider does retry on retryable errors."""
    count = 0

    async def handler(
        _stream: Stream[
            get_auth_token_pb2.GetAuthTokenRequest,
            get_auth_token_pb2.GetAuthTokenResponse,
        ],
    ) -> None:
        nonlocal count
        count += 1
        raise GRPCError(
            status=code,
        )

    server = Server([MockAuthService(handler=handler)])
    with graceful_exit([server]):
        await server.start("127.0.0.1")
        port = server._server.sockets[0].getsockname()[1]  # type: ignore[reportUnknownMemberType,union-attr] # noqa: SLF001
        init, stop = init_server_auth(
            access_key="test_key",
            base_retry_backoff_secs=0.01,
        )
        get_token = init(f"http://127.0.0.1:{port}")
        with pytest.raises(StatelyError):
            await get_token()
        assert count == RETRY_ATTEMPTS
        stop()
    server.close()
    await server.wait_closed()
