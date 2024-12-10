"""
Authentication code for the Stately Cloud SDK.

The authenticator function is a callable
that returns an access token string containing the auth token.
"""

from __future__ import annotations

import asyncio
import os
from collections.abc import Awaitable, Coroutine
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from random import random
from typing import Any, Callable

import aiohttp

from statelydb.lib.api.auth import get_auth_token_pb2
from statelydb.lib.api.auth import service_grpc as auth
from statelydb.src.channel import StatelyChannel
from statelydb.src.errors import StatelyError, Status

type AuthTokenProvider = Callable[[], Coroutine[Any, Any, str]]


@dataclass
class TokenResult:
    """Result from a token fetch operation."""

    token: str
    expires_in_secs: int


@dataclass
class TokenState:
    """Persistent state for the token provider."""

    token: str
    expires_at: datetime


# TokenFetcher is a callable that returns a TokenResult
# this is basically the abstraction that we swap out for different providers ie.
# auth0 or stately
type TokenFetcher = Callable[[], Coroutine[Any, Any, TokenResult]]

DEFAULT_GRANT_TYPE = "client_credentials"


def init_server_auth(
    access_key: str | None = None,
    client_id: str | None = None,
    client_secret: str | None = None,
    origin: str | None = None,
    audience: str = "api.stately.cloud",
) -> AuthTokenProvider:
    """
    Create a new authenticator with the provided arguments.

    init_server_auth creates an authenticator function that asynchronously
    returns an access token string using the provided arguments.

    :param access_key: Your Stately Access Key.
        Defaults to os.getenv("STATELY_ACCESS_KEY").
    :type access_key: str, optional

    :param client_id: The customer client ID to use for authentication.
        This will be provided to you by a Stately admin.
        Defaults to os.getenv("STATELY_CLIENT_ID").
        DEPRECATED: use access_key instead.
    :type client_id: str, optional

    :param client_secret: The customer client secret to use for authentication.
        This will be provided to you by a Stately admin.
        Defaults to os.getenv("STATELY_CLIENT_SECRET").
        DEPRECATED: use access_key instead.
    :type client_secret: str, optional

    :param origin: The origin to use for authentication.
        Defaults to "https://oauth.stately.cloud" if client_id and client_secret are passed,
        or "https://api.stately.cloud" if access_key is passed.
    :type origin: str, optional

    :param audience: The audience to authenticate for.
        Defaults to "api.stately.cloud".
    :type audience: str, optional

    :return: A callable that asynchronously returns an access token string
    :rtype: AuthTokenProvider

    """
    # args are evaluated at definition time
    # so we can't put these in the definition
    access_key = access_key or os.getenv("STATELY_ACCESS_KEY")
    client_id = client_id or os.getenv("STATELY_CLIENT_ID")
    client_secret = client_secret or os.getenv("STATELY_CLIENT_SECRET")

    token_fetcher: TokenFetcher | None = None
    if access_key is not None:
        origin = origin or "https://api.stately.cloud"
        token_fetcher = make_fetch_stately_access_token(access_key, origin)
    elif client_id is not None and client_secret is not None:
        origin = origin or "https://oauth.stately.cloud"
        token_fetcher = make_fetch_auth0(client_id, client_secret, origin, audience)
    else:
        raise StatelyError(
            stately_code="Unauthenticated",
            code=Status.UNAUTHENTICATED,
            message=(
                "unable to find client credentials in STATELY_ACCESS_KEY or STATELY_CLIENT_ID and"
                " STATELY_CLIENT_SECRET environment variables. Either pass your credentials in "
                "explicitly or set these environment variables"
            ),
        )

    # init nonlocal containing the initial state
    # this is overridden by the refresh function
    token_state: TokenState | None = None

    async def _refresh_token_impl() -> str:
        nonlocal token_state

        refreshed = False
        # TODO @stan-stately: Swap this loop out for error handling with
        # retries inside the token_fetcher
        # https://app.clickup.com/t/868b8rwjk
        while token_state is None or not refreshed:
            try:
                token_result = await token_fetcher()  # type: ignore[misc] # mypy can't work out that this can't be None
                expires_at = datetime.now(timezone.utc) + timedelta(
                    seconds=token_result.expires_in_secs
                )
                token_state = TokenState(token_result.token, expires_at)
                # Calculate a random multiplier to apply to the expiry so that we refresh
                # in the background ahead of expiration, but avoid multiple processes
                # hammering the service at the same time.
                # This random generator is fine, it doesn't need to
                # be cryptographically secure.
                # ruff: noqa: S311
                jitter = (random() * 0.05) + 0.9

                # set the refresh task
                # this will cause you to see `Task was destroyed but it is pending!`
                # after the tests run
                # TODO @stan-stately: implement an abort signal like JS
                # https://app.clickup.com/t/86899vgje
                asyncio.get_event_loop().create_task(
                    _schedule(_refresh_token, token_result.expires_in_secs * jitter),
                )

                refreshed = True
            except Exception:  # noqa: BLE001, PERF203
                # wait half a second and retry
                # TODO @stan-stately: Swap this to exponential backoff
                # https://app.clickup.com/t/868b8rwjk
                await asyncio.sleep(0.5)
        return token_state.token

    # _refresh_token will fetch the most current auth token for usage in Stately APIs.
    # This method is automatically invoked when calling get_token()
    # if there is no token available.
    # It is also periodically invoked to refresh the token before it expires.
    _refresh_token = _dedupe(lambda: asyncio.create_task(_refresh_token_impl()))

    def valid_access_token() -> str | None:
        nonlocal token_state
        if (
            token_state is not None
            and datetime.now(
                timezone.utc,
            )
            < token_state.expires_at
        ):
            return token_state.token
        return None

    async def get_token() -> str:
        return valid_access_token() or await _refresh_token()

    return get_token


async def _schedule(fn: Callable[[], Awaitable[Any]], delay_secs: float) -> None:
    await asyncio.sleep(delay_secs)
    await fn()


# Dedupe multiple tasks
# If this this is called multiple times while the first task is running
# then the result of the first task will be returned to all callers
# and the other tasks will never be awaited
def _dedupe(
    task: Callable[..., asyncio.Task[Any]],
) -> Callable[..., Awaitable[Any]]:
    cached: asyncio.Task[Any] | None = None

    async def _run() -> Awaitable[Any]:
        nonlocal cached
        cached = cached or task()
        try:
            return await cached
        finally:
            cached = None

    return _run


def make_fetch_auth0(
    client_id: str, client_secret: str, origin: str, audience: str
) -> TokenFetcher:
    """make_fetch_auth0 creates a fetcher function that fetches an auth0 token using client_id and client_secret."""

    async def fetch_auth0() -> TokenResult:
        async with (
            aiohttp.ClientSession() as session,
            session.post(
                f"{origin}/oauth/token",
                headers={
                    "Content-Type": "application/json",
                },
                json={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "audience": audience,
                    "granttype": DEFAULT_GRANT_TYPE,
                },
            ) as response,
        ):
            if response.status != HTTPStatus.OK:
                raise StatelyError(
                    stately_code="Unauthenticated",
                    code=Status.UNAUTHENTICATED,
                    message=(
                        f"Failed to fetch auth token from {origin}. "
                        f"Status: {response.status}."
                    ),
                )
            auth_data = await response.json()
            return TokenResult(
                token=auth_data["access_token"],
                expires_in_secs=auth_data["expires_in"],
            )

    return fetch_auth0


def make_fetch_stately_access_token(access_key: str, origin: str) -> TokenFetcher:
    """make_fetch_stately_access_token creates a fetcher function that fetches a Stately token using access_key."""
    auth_service: auth.AuthServiceStub | None = None

    async def fetch_stately_access_token() -> TokenResult:
        nonlocal auth_service

        # lazy init the auth service. It needs to be done in
        # an async context.
        if auth_service is None:
            auth_service = auth.AuthServiceStub(
                StatelyChannel(endpoint=origin),
            )
        resp = await auth_service.GetAuthToken(
            get_auth_token_pb2.GetAuthTokenRequest(access_key=access_key)
        )
        return TokenResult(
            token=resp.auth_token,
            expires_in_secs=resp.expires_in_s,
        )

    return fetch_stately_access_token
