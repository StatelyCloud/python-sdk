"""Options for a Put operation."""

from dataclasses import dataclass

from statelydb.src.types import StatelyItem


@dataclass
class WithPutOptions:
    """Wrap an item with additional options for a Put operation."""

    item: StatelyItem
    must_not_exist: bool
    """must_not_exist is a condition that indicates this item must not already
    exist at any of its key paths. If there is already an item at one of those
    paths, the Put operation will fail with a ConditionalCheckFailed error. Note
    that if the item has an `initialValue` field in its key, that initial value
    will automatically be chosen not to conflict with existing items, so this
    condition only applies to key paths that do not contain the `initialValue`
    field."""
