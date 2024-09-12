"""Shared types for the Stately Cloud SDK."""

from abc import ABC, abstractmethod
from typing import TypeVar
from uuid import UUID

from google.protobuf.message import Message

from statelydb.lib.api.db.item_pb2 import Item as PBItem

type StoreID = int

type AllKeyTypes = UUID | str | int | bytes
AnyKeyType = TypeVar("AnyKeyType", bound=AllKeyTypes)


class StatelyObject(ABC):
    """
    All generated object types must implement the StatelyObject interface
    which allows for serialization and deserialization to and from protobuf.
    """

    @abstractmethod
    def marshal(self) -> Message:
        """Marshal the StatelyObject to it's corresponding proto message."""

    @staticmethod
    @abstractmethod
    def unmarshal(proto_bytes: bytes) -> "StatelyObject":
        """Unmarshal proto bytes into their corresponding StatelyObject."""


class StatelyItem(ABC):
    """
    All generated item types must implement the StatelyItem interface
    which allows for serialization and deserialization to and from protobuf.
    """

    @abstractmethod
    def marshal(self) -> PBItem:
        """Marshal the StatelyItem to it's corresponding proto message."""

    @staticmethod
    @abstractmethod
    def unmarshal(proto_bytes: bytes) -> "StatelyItem":
        """Unmarshal proto bytes into their corresponding StatelyItem."""

    @staticmethod
    @abstractmethod
    def item_type() -> str:
        """Return the type of the item."""


class BaseTypeMapper(ABC):
    """
    TypeMapper is an interface that is implemented by Stately generated schema code
    unmarshalling concrete Stately schema from generic
    protobuf items that are received from the API.
    """

    @staticmethod
    @abstractmethod
    def unmarshal(item: PBItem) -> StatelyItem:
        """Unmarshal a generic protobuf item into a concrete schema type."""
