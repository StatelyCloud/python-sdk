from . import item_pb2 as _item_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PutRequest(_message.Message):
    __slots__ = ("store_id", "puts")
    STORE_ID_FIELD_NUMBER: _ClassVar[int]
    PUTS_FIELD_NUMBER: _ClassVar[int]
    store_id: int
    puts: _containers.RepeatedCompositeFieldContainer[PutItem]
    def __init__(self, store_id: _Optional[int] = ..., puts: _Optional[_Iterable[_Union[PutItem, _Mapping]]] = ...) -> None: ...

class PutItem(_message.Message):
    __slots__ = ("item",)
    ITEM_FIELD_NUMBER: _ClassVar[int]
    item: _item_pb2.Item
    def __init__(self, item: _Optional[_Union[_item_pb2.Item, _Mapping]] = ...) -> None: ...

class PutResponse(_message.Message):
    __slots__ = ("items",)
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[_item_pb2.Item]
    def __init__(self, items: _Optional[_Iterable[_Union[_item_pb2.Item, _Mapping]]] = ...) -> None: ...
