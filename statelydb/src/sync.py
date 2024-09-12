"""Helpers for sync operations."""

from __future__ import annotations

from typing import TYPE_CHECKING, AsyncGenerator

if TYPE_CHECKING:
    from grpclib.client import Stream

    from statelydb.lib.api.db import sync_list_pb2 as pb_sync_list
    from statelydb.src.list import TokenReceiver
    from statelydb.src.types import BaseTypeMapper, StatelyItem


class SyncResult:
    """
    SyncResult is a base class for the different
    types of sync results that can be returned.
    """


class SyncReset(SyncResult):
    """
    If the result is a SyncReset, it means that any previously fetched items from
    this list (from previous calls to Begin/Continue/SyncList) should be
    discarded, and the results from this SyncList call should form the new result
    list. This can happen when the sync token is too old, or otherwise at the
    server's discretion.
    """


class SyncChangedItem(SyncResult):
    """
    If the result is a SyncChangedItem, it means that the item has been changed
    or newly created. The item should be "upserted" into the local result set.
    """

    def __init__(self, item: StatelyItem) -> None:
        """Create a new SyncChangedItem with the provided items."""
        self.item = item


class SyncDeletedItem(SyncResult):
    """
    If the result is a SyncDeletedItem, it means that the item has been deleted.
    The item at this key path should be removed from the local result set.
    """

    def __init__(self, key_path: str) -> None:
        """Create a new SyncDeletedItem with the provided key paths."""
        self.key_path = key_path


class SyncUpdatedItemKeyOutsideListWindow(SyncResult):
    """
    If the result is a SyncUpdatedItemKeyOutsideListWindow, it means that this
    item was updated, but now falls outside of the list window. This could be
    irrelevant, but *if* you already have this key path in the local result set,
    you should remove it. This can generally be handled the same as
    SyncDeletedItem, except the item has not actually been deleted so you
    shouldn't necessarily do cleanup you might do for a deleted item.
    """

    def __init__(self, key_path: str) -> None:
        """
        Create a new SyncUpdatedItemKeyOutsideListWindow
        with the provided key paths.
        """
        self.key_path = key_path


async def handle_sync_response(
    type_mapper: BaseTypeMapper,
    token_receiver: TokenReceiver,
    stream: Stream[pb_sync_list.SyncListRequest, pb_sync_list.SyncListResponse],
) -> AsyncGenerator[SyncResult]:
    """Convert a SyncListResponse stream into an AsyncGenerator of StatelyItems."""
    try:
        async for r in stream:
            if r.WhichOneof("response") == "reset":
                yield SyncReset()
            elif r.WhichOneof("response") == "result":
                for item in r.result.changed_items:
                    yield SyncChangedItem(type_mapper.unmarshal(item))
                for deleted_item in r.result.deleted_items:
                    yield SyncDeletedItem(deleted_item.key_path)
                for key_path in r.result.updated_item_keys_outside_list_window:
                    yield SyncUpdatedItemKeyOutsideListWindow(key_path)
            elif r.WhichOneof("response") == "finished":
                token_receiver.token = r.finished.token
                await stream.__aexit__(None, None, None)
                return
            else:
                # TODO @stan-stately: return stately error here
                # https://app.clickup.com/t/86897hejr
                msg = (
                    "Expected 'reset', 'result' or 'finished'"
                    " to be set but both are unset"
                )
                raise ValueError(msg)  # noqa: TRY301
        # TODO @stan-stately: return stately error here
        # https://app.clickup.com/t/86897hejr
        msg = "Expected 'finished' to be set but it was never set"
        raise ValueError(msg)  # noqa: TRY301

    # we need to manually close the stream since
    # we can't use the async context manager as the author of grpclib intended
    except Exception as e:
        await stream.__aexit__(type(e), e, e.__traceback__)
        raise
