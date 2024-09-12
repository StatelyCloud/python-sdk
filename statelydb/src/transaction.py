"""Helpers for transactions."""

from __future__ import annotations

from typing import TYPE_CHECKING, AsyncContextManager, AsyncGenerator, Literal, TypeVar
from uuid import UUID

from google.protobuf import empty_pb2 as pb_empty
from typing_extensions import Self

from statelydb.lib.api.db import delete_pb2 as pb_delete
from statelydb.lib.api.db import get_pb2 as pb_get
from statelydb.lib.api.db import put_pb2 as pb_put
from statelydb.lib.api.db import transaction_pb2 as pb_transaction
from statelydb.lib.api.db.list_pb2 import SortDirection
from statelydb.src.list import ListResult, TokenReceiver, handle_list_response
from statelydb.src.types import StatelyItem

if TYPE_CHECKING:
    from types import TracebackType

    from grpclib.client import Stream

    from statelydb.lib.api.db.list_token_pb2 import ListToken
    from statelydb.src.types import BaseTypeMapper, StoreID

T = TypeVar("T", bound=StatelyItem)
ResponseField = Literal["get_results", "put_ack", "list_results", "finished"]
ResponseType = TypeVar(
    "ResponseType",
    pb_transaction.TransactionGetResponse,
    pb_transaction.TransactionPutAck,
    pb_transaction.TransactionListResponse,
    pb_transaction.TransactionFinished,
)


class TransactionResult:
    """
    The result of a transaction.
    This contains two fields, `puts` and `committed`.
    `puts` is a list of items that were put during the transaction.
    `committed` is a boolean indicating if the transaction was committed.
    """

    def __init__(
        self,
        puts: list[StatelyItem] | None = None,
        committed: bool = False,
    ) -> None:
        """
        Construct a new TransactionResult.

        :param puts: The list of items that were put during the transaction.
            Defaults to None.
        :type puts: list[StatelyItem], optional

        :param committed: Whether or not the transaction was committed.
            Defaults to False.
        :type committed: bool, optional
        """
        self.puts = puts or []
        self.committed = committed


class Transaction(
    AsyncContextManager["Transaction"],
):
    """
    The transaction context manager.
    This class is returned from the `transaction` method on the Stately client.
    """

    result: TransactionResult | None = None

    def __init__(
        self,
        store_id: StoreID,
        type_mapper: BaseTypeMapper,
        stream: Stream[
            pb_transaction.TransactionRequest,
            pb_transaction.TransactionResponse,
        ],
    ) -> None:
        """
        Create a new Transaction context manager.

        :param store_id: The store ID for the transaction.
        :type store_id: StoreID

        :param type_mapper: The type mapper for unmarshalling items.
        :type type_mapper: BaseTypeMapper

        :param stream: The bidirectional stream to use for the transaction.
        :type stream: Stream[pb_transaction.TransactionRequest, pb_transaction.TransactionResponse]

        """  # noqa: E501 # the line is long because the types are long. it's unavoidable.
        self._stream = stream
        self._message_id = 1
        self._store_id = store_id
        self._type_mapper = type_mapper

    def _next_message_id(self) -> int:
        self._message_id += 1
        return self._message_id

    async def __aenter__(self) -> Self:
        """Called when entering the context manager."""
        await self._stream.__aenter__()
        await self._stream.send_message(
            pb_transaction.TransactionRequest(
                message_id=self._next_message_id(),
                begin=pb_transaction.TransactionBegin(store_id=self._store_id),
            ),
        )
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        """Called when exiting the context manager."""
        if exc_type is not None:
            # if there was an exception then abort the transaction
            try:
                # wrap the abort in try/finally because if the stream
                # already errored then this will probably error too
                await self._abort()
            finally:
                self.result = TransactionResult(puts=[], committed=False)
        else:
            # if no error then commit the transaction
            self.result = await self._commit()

        # propagate exc_type etc... into the stream so that it can
        # run it's own error cleanup if there was an error
        await self._stream.__aexit__(exc_type, exc_val, exc_tb)
        # Returning False here will re-raise the exception
        # I don't think we want our context manager swallowing exceptions.
        return False

    async def get_batch(self, *key_paths: str) -> list[StatelyItem]:
        """
        get_batch retrieves a set of items by their full key paths. This will return
        the corresponding items that exist. It will fail if the caller does not
        have permission to read Items. Use begin_list if you want to retrieve
        multiple items but don't already know the full key paths of the items you
        want to get. You can get items of different types in a single get_batch -
        you will need to use `isinstance` to determine what item
        type each item is.

        :param *key_paths: The full key path of each item to load.
        :type *key_paths: str

        :return: The items that were loaded.
        :rtype: list[StatelyItem]

        Examples
        --------
        .. code-block:: python
            with await client.transaction() as txn:
                items = await txn.get_batch(
                    "/jedi-luke/equipment-lightsaber", "/jedi-luke/equipment-cloak")
                for item in items:
                    if isinstance(item, Equipment):
                        print(f"Got an equipment item: {item}")

        """
        resp = await self._request_response(
            get_items=pb_transaction.TransactionGet(
                gets=[pb_get.GetItem(key_path=k) for k in key_paths],
            ),
            expect_field="get_results",
            expect_type=pb_transaction.TransactionGetResponse,
        )
        return [self._type_mapper.unmarshal(i) for i in resp.items]

    async def get(self, item_type: type[T], key_path: str) -> T | None:
        """
        get retrieves an item by its full key path. This will return the item if it
        exists, or None if it does not. It will fail if  the caller does not
        have permission to read Items.

        :param item_type: The type of the item to load.
        :type item_type: type[T]

        :param key_path: The full key path of the item to load.
        :type key_path: str

        :return: The item that was loaded, or None if it does not exist.
        :rtype: T | None

        Examples
        --------
        .. code-block:: python
            with await client.transaction() as txn:
                item = await txn.get(Equipment, "/jedi-luke/equipment-lightsaber")
                if item is not None:
                    print(f"Got an equipment item: {item}")

        """
        resp = await self.get_batch(key_path)
        if len(resp) == 0:
            return None
        item = next(iter(resp))
        if item.item_type() != item_type.item_type():
            msg = f"Expected item type {item_type.item_type()}, got {item.item_type()}"
            raise ValueError(msg)
        if not isinstance(item, item_type):
            msg = f"Error unmarshalling {item_type}, got {type(item)}"
            raise TypeError(msg)
        return item

    async def put(self, item: StatelyItem) -> int | UUID | None:
        """
        put adds an Item to the Store, or replaces the Item if it already exists at
        that path. This will fail if the caller does not have permission to create
        Items.

        :param item: The item to put.
        :type item: StatelyItem

        :return: The generated ID for the item, if it had one.
        :rtype: int | UUID | None

        Examples
        --------
        .. code-block:: python
            txn = await client.transaction()
            with txn:
                lightsaber = Equipment(color="green", jedi="luke", type="lightsaber")
                lightsaber_id = await txn.put(lightsaber)
            assert txn.result is not None
            assert txn.result.committed
            assert len(tnx.result.puts) == 1

        """
        return next(iter(await self.put_batch(item)))

    async def put_batch(self, *items: StatelyItem) -> list[int | UUID | None]:
        """
        put_batch adds Items to the Store, or replaces Items if they already exist
        at that path. This will fail if the caller does not have permission to
        create Items. Data can be provided as either JSON, or as a proto encoded by
        a previously agreed upon schema, or by some combination of the two. You can
        put items of different types in a single put_batch. Puts will not be
        acknowledged until the transaction is committed - the TransactionResult
        will contain the updated metadata for each item.

        :param *items: A list of Items from your generated schema.
        :type *items: StatelyItem

        :return: An array of generated IDs for each item, if that
            item had an ID generated for its "initialValue" field. Otherwise the value
            is undefined. These are returned in the same order as the input items.
            This value can be used in subsequent puts to reference newly created items.
        :rtype: list[int | UUID | None]

        Examples
        --------
        .. code-block:: python
            txn = await client.transaction()
            with txn:
                lightsaber = Equipment(color="green", jedi="luke", type="lightsaber")
                cloak = Equipment(color="brown", jedi="luke", type="cloak")
                lightsaber_id, cloak_id = await txn.put_batch(lightsaber, cloak)
            assert txn.result is not None
            assert txn.result.committed
            assert len(tnx.result.puts) == 2

        """
        resp = await self._request_response(
            put_items=pb_transaction.TransactionPut(
                puts=[pb_put.PutItem(item=i.marshal()) for i in items],
            ),
            expect_field="put_ack",
            expect_type=pb_transaction.TransactionPutAck,
        )

        out: list[int | UUID | None] = []
        for i in resp.generated_ids:
            if i.WhichOneof("value") == "uint":
                out.append(i.uint)
            elif i.WhichOneof("value") == "bytes":
                out.append(UUID(bytes=i.bytes))
            else:
                out.append(None)
        return out

    async def delete(self, *key_paths: str) -> None:
        """
        del removes one or more Items from the Store by their full key paths. This
        will fail if the caller does not have permission to delete Items.

        :param *key_paths: The full key path of each item to delete.
        :type *key_paths: str

        :return: None

        Examples
        --------
        .. code-block:: python
            with await client.transaction() as txn:
                await txn.delete("/jedi-luke/equipment-lightsaber")


        """
        await self._request_only(
            delete_items=pb_transaction.TransactionDelete(
                deletes=[pb_delete.DeleteItem(key_path=k) for k in key_paths],
            ),
        )

    async def begin_list(
        self,
        key_path_prefix: str,
        limit: int = 0,
        sort_direction: SortDirection = SortDirection.SORT_ASCENDING,
    ) -> ListResult[StatelyItem]:
        """
        begin_list loads Items that start with a specified key path, subject to
        additional filtering. The prefix must minimally contain a Group Key (an
        item type and an item ID). begin_list will return an empty result set if
        there are no items matching that key prefix. A token is returned from this
        API that you can then pass to continueList to expand the result set, or to
        syncList to get updates within the result set. This can fail if the caller
        does not have permission to read Items.

        begin_list streams results via an AsyncGenerator, allowing you to handle
        results as they arrive. You can call `collect()` on it to get all the
        results as a list.

        You can list items of different types in a single begin_list, and you can
        use `isinstance` to handle different item types.

        :param key_path_prefix: The key path prefix to query for.
        :type key_path_prefix: str

        :param limit: The max number of Items to retrieve. Defaults to 0 which
            fetches all Items.
        :type limit: int, optional

        :param sort_direction: The direction to sort results. Defaults to
            SortDirection.SORT_ASCENDING.
        :type sort_direction: SortDirection, optional

        :return: The result generator.
        :rtype: ListResult[StatelyItem]

        Examples
        --------
        .. code-block:: python
            with await client.transaction() as txn:
                list_resp = await txn.begin_list("/jedi-luke/equipment")
                async for item in list_resp:
                    if isinstance(item, Equipment):
                        print(item.color)
                token = list_resp.token

        """
        msg_id = await self._request_only(
            begin_list=pb_transaction.TransactionBeginList(
                key_path_prefix=key_path_prefix,
                limit=limit,
                sort_direction=sort_direction,
            ),
        )
        token_receiver = TokenReceiver(token=None)
        return ListResult(
            token_receiver,
            handle_list_response(
                self._type_mapper,
                token_receiver,
                self._stream_list_responses(msg_id),
            ),
        )

    async def continue_list(self, token: ListToken) -> ListResult[StatelyItem]:
        """

        continue_list takes the token from a begin_list call and returns the next
        "page" of results based on the original query parameters and pagination
        options. It doesn't have options because it is a continuation of a previous
        list operation. It will return a new token which can be used for another
        continue_list call, and so on. The token is the same one used by sync_list -
        each time you call either continue_list or sync_list, you should pass the
        latest version of the token, and then use the new token from the result in
        subsequent calls. You may interleave continue_list and sync_list calls
        however you like, but it does not make sense to make both calls in
        parallel. Calls to continue_list are tied to the authorization of the
        original begin_list call, so if the original begin_list call was allowed,
        continue_list with its token should also be allowed.

        continue_list streams results via an AsyncGenerator, allowing you to handle
        results as they arrive. You can call `collect()` on it to get all the
        results as a list.

        You can list items of different types in a single continueList, and you can
        use `isinstance` to handle different item types.

        :param token: The token from the previous list operation.
        :type token: ListToken

        :return: The result generator.
        :rtype: ListResult[StatelyItem]

        Examples
        --------
        .. code-block:: python
            with await client.transaction() as txn:
                list_resp = await txn.begin_list("/jedi-luke/equipment")
                async for item in list_resp:
                    if isinstance(item, Equipment):
                        print(item.color)
                token = list_resp.token
                while token.can_continue:
                    list_resp = await txn.continue_list(token)
                    async for item in list_resp:
                        if isinstance(item, Equipment):
                            print(item)
                    token = list_resp.token

        """
        msg_id = await self._request_only(
            continue_list=pb_transaction.TransactionContinueList(
                token_data=token.token_data,
            ),
        )
        token_receiver = TokenReceiver(token=None)
        return ListResult(
            token_receiver,
            handle_list_response(
                self._type_mapper,
                token_receiver,
                self._stream_list_responses(msg_id),
            ),
        )

    async def _commit(self) -> TransactionResult:
        """
        _commit finalizes the transaction, applying all the changes made within it.
        This is called automatically if the context manager runs without
        error.
        """
        resp = await self._request_response(
            commit=pb_empty.Empty(),
            expect_field="finished",
            expect_type=pb_transaction.TransactionFinished,
        )
        return TransactionResult(
            puts=[self._type_mapper.unmarshal(i) for i in resp.put_results],
            committed=resp.committed,
        )

    async def _abort(self) -> None:
        """
        _abort cancels the transaction, discarding all changes made within it. This
        is called automatically if the context manager throws an error.
        """
        await self._request_response(
            abort=pb_empty.Empty(),
            expect_field="finished",
            expect_type=pb_transaction.TransactionFinished,
        )

    async def _request_only(  # noqa: PLR0913
        self,
        begin: pb_transaction.TransactionBegin | None = None,
        get_items: pb_transaction.TransactionGet | None = None,
        begin_list: pb_transaction.TransactionBeginList | None = None,
        continue_list: pb_transaction.TransactionContinueList | None = None,
        put_items: pb_transaction.TransactionPut | None = None,
        delete_items: pb_transaction.TransactionDelete | None = None,
        commit: pb_empty.Empty | None = None,
        abort: pb_empty.Empty | None = None,
    ) -> int:
        """
        Helper to dispatch requests to the transaction stream.

        :return: The generated message ID of the request.
        :rtype: int
        """
        msg_id = self._next_message_id()
        await self._stream.send_message(
            pb_transaction.TransactionRequest(
                message_id=msg_id,
                begin=begin,
                get_items=get_items,
                begin_list=begin_list,
                continue_list=continue_list,
                put_items=put_items,
                delete_items=delete_items,
                commit=commit,
                abort=abort,
            ),
            # grpclib stream needs to know if the stream is expected to
            # end after this message
            end=commit is not None or abort is not None,
        )
        return msg_id

    async def _expect_response(
        self,
        message_id: int,
        expect_field: ResponseField,
        expect_type: type[ResponseType],
    ) -> ResponseType:
        """
        Helper to wait for an incoming response from the transaction stream.
        This will raise an error if the response does not match the expected
        message ID, or if it cannot be unpacked as expected.
        """
        resp = await self._stream.recv_message()
        if resp is None:
            msg = "Expected a response but got None"
            raise ValueError(msg)
        if resp.message_id != message_id:
            msg = f"Expected message_id {message_id}, got {resp.message_id}"
            raise ValueError(msg)
        if resp.WhichOneof("result") != expect_field:
            msg = f"Expected {expect_field}, got {resp.WhichOneof('result')}"
            raise ValueError(msg)
        val = getattr(resp, expect_field)
        if not isinstance(val, expect_type):
            msg = f"Expected {expect_type}, got {type(val)}"
            raise TypeError(msg)
        return val

    async def _request_response(  # noqa: PLR0913
        self,
        expect_field: ResponseField,
        expect_type: type[ResponseType],
        begin: pb_transaction.TransactionBegin | None = None,
        get_items: pb_transaction.TransactionGet | None = None,
        begin_list: pb_transaction.TransactionBeginList | None = None,
        continue_list: pb_transaction.TransactionContinueList | None = None,
        put_items: pb_transaction.TransactionPut | None = None,
        delete_items: pb_transaction.TransactionDelete | None = None,
        commit: pb_empty.Empty | None = None,
        abort: pb_empty.Empty | None = None,
    ) -> ResponseType:
        """A helper that sends an input command, then waits for an output result."""
        msg_id = await self._request_only(
            begin=begin,
            get_items=get_items,
            begin_list=begin_list,
            continue_list=continue_list,
            put_items=put_items,
            delete_items=delete_items,
            commit=commit,
            abort=abort,
        )

        return await self._expect_response(msg_id, expect_field, expect_type)

    async def _stream_list_responses(
        self,
        message_id: int,
    ) -> AsyncGenerator[pb_transaction.TransactionListResponse]:
        """Convert a stream of list responses into a generator of items."""
        while True:
            yield await self._expect_response(
                message_id,
                "list_results",
                pb_transaction.TransactionListResponse,
            )
