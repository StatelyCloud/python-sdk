"""
Authentication code for the Stately Cloud SDK.

The authenticator function is a callable
that returns a JWT token string containing the auth token.
"""

from __future__ import annotations

import asyncio
import os
from typing import Any, Awaitable, Callable

import aiohttp

type AuthTokenProvider = Callable[[], Awaitable[str]]

DEFAULT_GRANT_TYPE = "client_credentials"


def init_server_auth(
    client_id: str | None = None,
    client_secret: str | None = None,
    auth_domain: str = "https://oauth.stately.cloud",
    audience: str = "api.stately.cloud",
) -> AuthTokenProvider:
    """
    Create a new authenticator with the provided arguments.

    init_server_auth creates an authenticator function that asynchronously
    returns a JWT token string using the provided arguments.


    :param client_id: The customer client ID to use for authentication.
        This will be provided to you by a Stately admin.
        Defaults to os.getenv("STATELY_CLIENT_ID").
    :type client_id: str, optional

    :param client_secret: The customer client secret to use for authentication.
        This will be provided to you by a Stately admin.
        Defaults to os.getenv("STATELY_CLIENT_SECRET").
    :type client_secret: str, optional

    :param auth_domain: The domain to use for authentication.
        Defaults to "https://oauth.stately.cloud".
    :type auth_domain: str, optional

    :param audience: The audience to authenticate for.
        Defaults to "api.stately.cloud".
    :type audience: str, optional

    :return: A callable that asynchronously returns a JWT token string
    :rtype: AuthTokenProvider

    """
    # args are evaluated at definition time
    # so we can't put these in the definition
    client_id = client_id or os.getenv("STATELY_CLIENT_ID")
    client_secret = client_secret or os.getenv("STATELY_CLIENT_SECRET")

    # init nonlocal vars containing the initial state
    # these are overridden by the refresh function
    access_token: str | None = None
    refresh_timeout: int = 60

    async def _refresh_token_impl() -> str:
        async with aiohttp.ClientSession() as session, session.post(
            f"{auth_domain}/oauth/token",
            headers={
                "Content-Type": "application/json",
            },
            json={
                "client_id": client_id,
                "client_secret": client_secret,
                "audience": audience,
                "grant_type": DEFAULT_GRANT_TYPE,
            },
        ) as response:
            auth_data = await response.json()

            nonlocal access_token, refresh_timeout
            access_token = auth_data["access_token"]
            refresh_timeout = auth_data["expires_in"]

            # set the refresh task
            # this will cause you to see `Task was destroyed but it is pending!`
            # after the tests run
            # TODO @stan-stately: implement an abort signal like JS
            # https://app.clickup.com/t/86899vgje
            asyncio.get_event_loop().create_task(
                _schedule(refresh_token, refresh_timeout),
            )

            return auth_data["access_token"]

    refresh_token = _dedupe(asyncio.create_task(_refresh_token_impl()))

    async def get_token() -> str:
        nonlocal access_token
        return access_token or await refresh_token()

    return get_token


async def _schedule(fn: Callable[[], Awaitable[Any]], delay: int) -> None:
    await asyncio.sleep(delay)
    fn()


# Dedupe multiple tasks
# If this this is called multiple times while the first task is running
# then the result of the first task will be returned to all callers
# and the other tasks will never be awaited
def _dedupe(
    task: asyncio.Task[Any],
) -> Callable[..., Awaitable[Any]]:
    cached: asyncio.Task[Any] | None = None

    async def _run() -> Awaitable[Any]:
        nonlocal cached
        cached = cached or task
        try:
            return await cached
        finally:
            cached = None

    return _run
