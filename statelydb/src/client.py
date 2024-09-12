"""The Stately Python client."""

from __future__ import annotations

import copy
from typing import (
    TYPE_CHECKING,
    Self,
    TypeVar,
)
from urllib.parse import urlparse

from grpclib.client import Channel
from grpclib.const import Status
from grpclib.encoding.proto import ProtoStatusDetailsCodec
from grpclib.events import RecvTrailingMetadata, SendRequest, listen

from statelydb.lib.api.db import continue_list_pb2 as pb_continue_list
from statelydb.lib.api.db import delete_pb2 as pb_delete
from statelydb.lib.api.db import get_pb2 as pb_get
from statelydb.lib.api.db import list_pb2 as pb_list
from statelydb.lib.api.db import put_pb2 as pb_put
from statelydb.lib.api.db import service_grpc as db
from statelydb.lib.api.db import sync_list_pb2 as pb_sync_list
from statelydb.lib.api.db.list_pb2 import SortDirection
from statelydb.src.auth import AuthTokenProvider, init_server_auth
from statelydb.src.errors import StatelyError
from statelydb.src.list import ListResult, TokenReceiver, handle_list_response
from statelydb.src.sync import handle_sync_response
from statelydb.src.transaction import Transaction
from statelydb.src.types import StatelyItem

if TYPE_CHECKING:
    from statelydb.lib.api.db.list_token_pb2 import ListToken
    from statelydb.src.sync import SyncResult
    from statelydb.src.types import BaseTypeMapper, StoreID

T = TypeVar("T", bound=StatelyItem)


class Client:
    """Client is a Stately client that interacts with the given store."""

    db_service: db.DatabaseServiceStub
    _token_provider: AuthTokenProvider

    def __init__(
        self,
        store_id: StoreID,
        type_mapper: BaseTypeMapper,
        token_provider: AuthTokenProvider | None = None,
        endpoint: str = "https://api.stately.cloud",
    ) -> None:
        """
        Construct a new Stately Client.

        :param store_id: The ID of the store to connect to. All client operations will
            be performed on this store.
        :type store_id: StoreID

        :param type_mapper: The Stately generated schema mapper for converting generic
            Stately Items into concrete schema types.
        :type type_mapper: BaseTypeMapper

        :param token_provider: An optional token provider function.
            Defaults to reading `STATELY_CLIENT_ID` and `STATELY_CLIENT_SECRET` from
            the environment.
        :type token_provider: AuthTokenProvider, optional

        :param endpoint: The Stately endpoint to connect to.
            Defaults to "https://api.stately.cloud".
        :type endpoint: str, optional

        :return: A Client for interacting with a Stately store
        :rtype: Client
        """
        self._token_provider = token_provider or init_server_auth()
        self._db_service = db.DatabaseServiceStub(
            self._new_channel(endpoint),
        )
        self._store_id = store_id
        self._type_mapper = type_mapper
        self._allow_stale = False

    def _new_channel(
        self,
        endpoint: str = "https://api.stately.cloud",
    ) -> Channel:
        """Create a new grpc channel and setup interceptors."""
        url = urlparse(endpoint)
        channel = Channel(
            host=url.hostname,
            port=443 if url.scheme == "https" else 3000,
            ssl=url.scheme == "https",
            status_details_codec=ProtoStatusDetailsCodec(),
        )
        # add any listeners.
        # These are basically grpclib's version of interceptors
        listen(channel, SendRequest, self._send_request)
        listen(channel, RecvTrailingMetadata, self._recv_trailing_metadata)
        return channel

    async def _send_request(self, event: SendRequest) -> None:
        """Hook that is called before a request is sent."""
        # grpclib doesn't allow uppercase characters in headers:
        # https://github.com/vmagamedov/grpclib/blob/62f968a4c84e3f64e6966097574ff0a59969ea9b/grpclib/metadata.py#L113
        event.metadata["authorization"] = f"Bearer {await self._token_provider()}"

    async def _recv_trailing_metadata(self, event: RecvTrailingMetadata) -> None:
        """Hook that is called after a response is received."""
        if event.status != Status.OK:
            raise StatelyError.from_trailing_metadata(event)

    def with_allow_stale(self, allow_stale: bool = True) -> Self:
        """
        Returns a new client that is either OK with or not OK with stale reads.
        This affects get and list operations from the returned client. Use this
        only if you know you can tolerate stale reads. This can result in improved
        performance, availability, and cost.

        :param allow_stale: Whether staleness is allowed or not. Defaults to True.
        :type allow_stale: bool, optional

        :return: A clone of the existing client with allow_stale set to the new value.
        :rtype: Self
        """
        # create a shallow copy since we don't mind if the grpc client,
        # type mapper or token provider are shared.
        # These are all safe for concurrent use.
        new_client = copy.copy(self)
        new_client._allow_stale = allow_stale  # noqa: SLF001
        return new_client

    async def get(self, item_type: type[T], key_path: str) -> T | None:
        """
        get retrieves an item by its full key path. This will return the item if it
        exists, or undefined if it does not. It will fail if  the caller does not
        have permission to read Items.

        :param item_type: One of the itemType names from your schema.
                This is used to determine the type of the resulting item.
        :type item_type: type[T]

        :param key_path: The full key path of the item.
        :type key_path: str

        :return: The Stately Item retrieved from the store or None if no
            item was found.
        :rtype: T | None

        Examples
        --------
        .. code-block:: python
            item = await client.get(Equipment, "/jedi-luke/equipment-lightsaber")

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

    async def get_batch(self, *key_paths: str) -> list[StatelyItem]:
        """
        get_batch retrieves a set of items by their full key paths. This will return
        the corresponding items that exist. It will fail if the caller does not
        have permission to read Items. Use BeginList if you want to retrieve
        multiple items but don't already know the full key paths of the items you
        want to get. You can get items of different types in a single getBatch -
        you will need to use `DatabaseClient.isType` to determine what item type
        each item is.

        :param *key_paths: The full key path of each item to load.
        :type *key_paths: str

        :return: The list of Items retrieved from the store.
            These are returned as generic StatelyItems and should be cast or
            narrowed to the correct type if you are using typed python.
        :rtype: list[StatelyItem]

        Examples
        --------
        .. code-block:: python
            first_item, second_item = await client.get_batch(
                "/jedi-luke/equipment-lightsaber", "/jedi-luke/equipment-cloak")
            print(cast(Equipment, first_item).color)
            if isinstance(second_item, Equipment):
                print(second_item.color)

        """
        resp = await self._db_service.Get(
            pb_get.GetRequest(
                store_id=self._store_id,
                gets=[pb_get.GetItem(key_path=key_path) for key_path in key_paths],
                allow_stale=self._allow_stale,
            ),
        )
        return [self._type_mapper.unmarshal(i) for i in resp.items]

    async def put(self, item: T) -> T:
        """
        put adds an Item to the Store, or replaces the Item if it already exists at
        that path. This will fail if the caller does not have permission to create
        Items.

        :param item: An Item from your generated schema.
        :type item: T

        :return: The item that was put, with any server-generated fields filled in.

        Examples
        --------
        .. code-block:: python
            lightsaber = Equipment(color="green", jedi="luke", type="lightsaber")
            lightsaber = await client.put(lightsaber)

        """
        put_item = next(iter(await self.put_batch(item)))
        if put_item.item_type() != item.item_type():
            msg = f"Expected item type {item.item_type()}, got {put_item.item_type()}"
            raise ValueError(msg)
        if isinstance(put_item, type(item)):
            return put_item
        msg = f"Error unmarshalling {put_item}, got {type(item)}"
        raise TypeError(msg)

    async def put_batch(self, *items: StatelyItem) -> list[StatelyItem]:
        """
        put_batch adds Items to the Store, or replaces Items if they already exist
        at that path. This will fail if the caller does not have permission to
        create Items. Data must be provided as a schema type generated from your defined
        schema. You can put items of different types in a single putBatch.

        :param *items: Items from your generated schema.
        :type *items: StatelyItem

        :return: The items that were put, with any server-generated fields filled in.
            They are returned in the same order they were provided.
        :rtype: list[StatelyItem]

        Examples
        --------
        .. code-block:: python
            items = await client.put_batch(
                Equipment(color="green", jedi="luke", type="lightsaber"),
                Equipment(color="brown", jedi="luke", type="cloak"),
            )

        """
        resp = await self._db_service.Put(
            pb_put.PutRequest(
                store_id=self._store_id,
                puts=[pb_put.PutItem(item=i.marshal()) for i in items],
            ),
        )

        return [self._type_mapper.unmarshal(i) for i in resp.items]

    async def delete(self, *key_paths: str) -> None:
        """
        delete removes one or more Items from the Store by their full key paths.
        This will fail if the caller does not have permission to delete Items.

        :param *key_paths: The full key paths of the items.
        :type *key_paths: str

        :return: None

        Examples
        --------
        .. code-block:: python
            await client.delete("/jedi-luke/equipment-lightsaber")

        """
        await self._db_service.Delete(
            pb_delete.DeleteRequest(
                store_id=self._store_id,
                deletes=[
                    pb_delete.DeleteItem(key_path=key_path) for key_path in key_paths
                ],
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
        API that you can then pass to continue_list to expand the result set, or to
        sync_list to get updates within the result set. This can fail if the caller
        does not have permission to read Items.

        begin_list streams results via an AsyncGenerator, allowing you to handle
        results as they arrive. You can call `collect()` on it to get all the
        results as a list.

        You can list items of different types in a single begin_list, and you can
        use `isinstance` to handle different item types.

        :param key_path_prefix: The key path prefix to query for.
        :type key_path_prefix: str

        :param limit: The max number of items to retrieve.
            If set to 0 then the full set will be returned. Defaults to 0.
        :type limit: int, optional

        :param sort_direction: The direction to sort the results.
            Defaults to SortDirection.SORT_ASCENDING.
        :type sort_direction: SortDirection, optional

        :return: The result generator.
        :rtype: ListResult[StatelyItem]

        Examples
        --------
        .. code-block:: python
            list_resp = await client.begin_list("/jedi-luke")
            async for item in list_resp:
                if isinstance(item, Equipment):
                    print(item.color)
                else:
                    print(item)
            token = list_resp.token

        """
        # grpclib only supports streaming with a context manager but that doesn't work
        # here because we want to wrap the stream and return it to the customer for them
        # to read at their leisure.
        # To get around that we have to manually call __aenter__ and __aexit__ hooks on
        # the stream.
        # We call __aenter__ here to open the thing and call __aexit__ at the end of the
        # response handler to ensure the stream is closed correctly.
        stream = self._db_service.BeginList.open()
        await stream.__aenter__()
        await stream.send_message(
            pb_list.BeginListRequest(
                store_id=self._store_id,
                key_path_prefix=key_path_prefix,
                limit=limit,
                sort_direction=sort_direction,
            ),
        )
        token_receiver = TokenReceiver(token=None)
        return ListResult(
            token_receiver,
            handle_list_response(self._type_mapper, token_receiver, stream),
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

        You can list items of different types in a single continue_list, and you can
        use `isinstance` to handle different item types.

        :param token: The token from the previous list operation.
        :type token: ListToken

        :return: The result generator.
        :rtype: ListResult[StatelyItem]

        Examples
        --------
        .. code-block:: python
            list_resp = await client.continue_list(token)
            async for item in list_resp:
                if isinstance(item, Equipment):
                    print(item.color)
                else:
                    print(item)
            token = list_resp.token

        """
        stream = self._db_service.ContinueList.open()
        await stream.__aenter__()
        await stream.send_message(
            pb_continue_list.ContinueListRequest(
                token_data=token.token_data,
                direction=pb_continue_list.CONTINUE_LIST_FORWARD,
            ),
        )
        token_receiver = TokenReceiver(token=None)
        return ListResult(
            token_receiver,
            handle_list_response(self._type_mapper, token_receiver, stream),
        )

    async def sync_list(self, token: ListToken) -> ListResult[SyncResult]:
        """
        sync_list returns all changes to Items within the result set of a previous
        List operation. For all Items within the result set that were modified, it
        returns the full Item at in its current state. It also returns a list of
        Item key paths that were deleted since the last sync_list, which you should
        reconcile with your view of items returned from previous
        begin_list/continue_list calls. Using this API, you can start with an initial
        set of items from begin_list, and then stay up to date on any changes via
        repeated sync_list requests over time. The token is the same one used by
        continue_list - each time you call either continue_list or sync_list, you
        should pass the latest version of the token, and then use the new token
        from the result in subsequent calls. Note that if the result set has
        already been expanded to the end (in the direction of the original
        begin_list request), sync_list will return newly created Items. You may
        interleave continue_list and sync_list calls however you like, but it does
        not make sense to make both calls in parallel. Calls to sync_list are tied
        to the authorization of the original begin_list call, so if the original
        begin_list call was allowed, sync_list with its token should also be allowed.

        sync_list streams results via an AsyncGenerator, allowing you to handle
        results as they arrive. You can call `collect()` on it to get all the
        results as a list.

        You can sync items of different types in a single syncList, and you can use
        `isinstance` to handle different item types.

        :param token: The token from the previous list operation.
        :type token: ListToken

        :return: The result generator.
        :rtype: ListResult[SyncResult]

        Examples
        --------
        .. code-block:: python
            sync_resp = await client.sync_list(token)
            async for item in sync_resp:
                if isinstance(item, SyncChangedItem):
                    print(item.item)
                elif isinstance(item, SyncDeletedItem):
                    print(item.key_path)
                elif isinstance(item, SyncUpdatedItemKeyOutsideListWindow):
                    print(item.key_path)
            token = sync_resp.token

        """
        stream = self._db_service.SyncList.open()
        await stream.__aenter__()
        await stream.send_message(
            pb_sync_list.SyncListRequest(
                token_data=token.token_data,
            ),
        )
        token_receiver = TokenReceiver(token=None)
        return ListResult(
            token_receiver,
            handle_sync_response(self._type_mapper, token_receiver, stream),
        )

    async def transaction(self) -> Transaction:
        """
        Transaction creates a Transaction context manager, within which you can
        issue writes and reads in any order, and all writes will either succeed
        or all will fail.

        Reads are guaranteed to reflect the state as of when the transaction
        started. This method may fail if another transaction commits before this
        one finishes
        - in that case, you should retry your transaction.

        If any error is thrown from the handler, the transaction is aborted and
        none of the changes made in it will be applied. If the handler returns
        without error, the transaction is automatically committed.

        If any of the operations in the handler fails (e.g. a request is invalid)
        you may not find out until the *next* operation, or once the handler
        returns, due to some technicalities about how requests are handled.

        :return: A new Transaction context manager.
        :rtype: Transaction

        Examples
        --------
        .. code-block:: python
            txn = await client.transaction()
            async with txn:
                item = await txn.get(Equipment, "/jedi-luke/equipment-lightsaber")
                if item is not None and item.color == "red":
                    item.color = "green"
                    await txn.put(item)
            assert txn.result is not None
            assert txn.result.committed
            assert len(txn.puts) == 1

        """
        stream = self._db_service.Transaction.open()
        return Transaction(self._store_id, self._type_mapper, stream)
