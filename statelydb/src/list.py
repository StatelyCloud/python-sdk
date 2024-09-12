"""Helpers for list operations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, AsyncGenerator, Generic, Never, TypeVar

from grpclib.client import Stream

from statelydb.src.sync import SyncResult
from statelydb.src.types import StatelyItem

if TYPE_CHECKING:
    from types import TracebackType

    from statelydb.lib.api.db import list_pb2 as pb_list
    from statelydb.lib.api.db import transaction_pb2 as pb_transaction
    from statelydb.lib.api.db.list_token_pb2 import ListToken
    from statelydb.src.types import BaseTypeMapper

T = TypeVar("T", StatelyItem, SyncResult)


class ListResult(Generic[T], AsyncGenerator[T, Never]):
    """
    ListResult wraps an AsyncGenerator of items and a token. It can be iterated
    like a normal AsyncGenerator via `async for`. However, it also holds on to
    the token returned from the generator, which would otherwise be lost from
    within the for loop.

    Yielded items are instances of `StatelyItem` or `SyncResult` depending on
    what kind of generator is passed in.

    Examples
    --------
        ```python
        list_resp = await client.begin_list("/jedi-luke/equipment")
        async for item in list_resp:
            print(item)
        token = list_resp.token
        ```

    """

    _generator: AsyncGenerator[T]

    def __init__(
        self,
        token_receiver: TokenReceiver,
        generator: AsyncGenerator[T],
    ) -> None:
        """
        Create a new ListResult from the given generator and token receiver.

        :param token_receiver: The token receiver to use to propagate the ListToken up
            to the ListResult from the generator.
        :type token_receiver: TokenReceiver

        :param generator: The generator to wrap.
        :type generator: AsyncGenerator[T]

        """
        self._generator = generator
        self._token_receiver = token_receiver

    async def __anext__(self) -> T:
        """
        Override the default `__anext__` method to read the list token from the
        internal generator when StopAsyncIteration is thrown.
        """
        try:
            return await self._generator.__anext__()
        except StopAsyncIteration:
            self.token = self._token_receiver.token
            raise

    async def asend(self, value: Never) -> T:
        """Send the provided value into the internal generator."""
        return await self._generator.asend(value)

    async def aclose(self) -> None:
        """Close the internal generator."""
        return await self._generator.aclose()

    async def athrow(  # type: ignore[reportIncompatibleMethodOverride,override] # pretty sure this is a bug in the type library
        self,
        typ: type[BaseException],
        val: object = None,
        tb: TracebackType | None = None,
    ) -> T:
        """Throw an exception into the internal generator."""
        return await self._generator.athrow(typ, val, tb)

    async def collect(self) -> tuple[list[T], ListToken]:
        """
        Collect all of the items from the generator into an array, and return the
        list token. This is a convenience for when you don't want to handle the
        items in a streaming fashion (e.g. with `async for`).

        Returns
        -------
            tuple[list[T], ListToken]: The list of items and the list token.

        """
        items: list[T] = []
        items = [item async for item in self]
        if self._token_receiver.token is None:
            # TODO @stan-stately: return stately error here
            # https://app.clickup.com/t/86897hejr
            msg = "ListToken was not set after streaming finished"
            raise ValueError(msg)
        return items, self._token_receiver.token


@dataclass
class TokenReceiver:
    """
    Allows us to share a reference to a ListToken
    so the internal generator can propagate the ListToken
    up into ListResult after it has finished generating.
    """

    token: ListToken | None


async def handle_list_response(
    type_mapper: BaseTypeMapper,
    token_receiver: TokenReceiver,
    stream: Stream[
        Any,
        pb_list.ListResponse,
    ]
    | AsyncGenerator[pb_transaction.TransactionListResponse],
) -> AsyncGenerator[StatelyItem]:
    """Convert a ListResponse stream into an AsyncGenerator of StatelyItems."""
    try:
        async for r in stream:
            if r.WhichOneof("response") == "result":
                for item in r.result.items:
                    yield type_mapper.unmarshal(item)
            elif r.WhichOneof("response") == "finished":
                token_receiver.token = r.finished.token
                if isinstance(stream, Stream):
                    await stream.__aexit__(None, None, None)
                return
            else:
                # TODO @stan-stately: return stately error here
                # https://app.clickup.com/t/86897hejr
                msg = "Expected 'result' or 'finished' to be set but both are unset"
                raise ValueError(msg)  # noqa: TRY301
        # TODO @stan-stately: return stately error here
        # https://app.clickup.com/t/86897hejr
        msg = "Expected 'finished' to be set but it was never set"
        raise ValueError(msg)  # noqa: TRY301

    except Exception as e:
        if isinstance(stream, Stream):
            # we need to manually close the stream since
            # we can't use the async context manager as the author of grpclib intended
            await stream.__aexit__(type(e), e, e.__traceback__)
        raise
