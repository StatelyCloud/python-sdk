from . import item_pb2 as _item_pb2
from . import item_property_pb2 as _item_property_pb2
from . import list_token_pb2 as _list_token_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SortDirection(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SORT_ASCENDING: _ClassVar[SortDirection]
    SORT_DESCENDING: _ClassVar[SortDirection]
SORT_ASCENDING: SortDirection
SORT_DESCENDING: SortDirection

class BeginListRequest(_message.Message):
    __slots__ = ("store_id", "key_path_prefix", "limit", "allow_stale", "sort_property", "sort_direction")
    STORE_ID_FIELD_NUMBER: _ClassVar[int]
    KEY_PATH_PREFIX_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    ALLOW_STALE_FIELD_NUMBER: _ClassVar[int]
    SORT_PROPERTY_FIELD_NUMBER: _ClassVar[int]
    SORT_DIRECTION_FIELD_NUMBER: _ClassVar[int]
    store_id: int
    key_path_prefix: str
    limit: int
    allow_stale: bool
    sort_property: _item_property_pb2.SortableProperty
    sort_direction: SortDirection
    def __init__(self, store_id: _Optional[int] = ..., key_path_prefix: _Optional[str] = ..., limit: _Optional[int] = ..., allow_stale: bool = ..., sort_property: _Optional[_Union[_item_property_pb2.SortableProperty, str]] = ..., sort_direction: _Optional[_Union[SortDirection, str]] = ...) -> None: ...

class ListResponse(_message.Message):
    __slots__ = ("result", "finished")
    RESULT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_FIELD_NUMBER: _ClassVar[int]
    result: ListPartialResult
    finished: ListFinished
    def __init__(self, result: _Optional[_Union[ListPartialResult, _Mapping]] = ..., finished: _Optional[_Union[ListFinished, _Mapping]] = ...) -> None: ...

class ListPartialResult(_message.Message):
    __slots__ = ("items",)
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[_item_pb2.Item]
    def __init__(self, items: _Optional[_Iterable[_Union[_item_pb2.Item, _Mapping]]] = ...) -> None: ...

class ListFinished(_message.Message):
    __slots__ = ("token",)
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    token: _list_token_pb2.ListToken
    def __init__(self, token: _Optional[_Union[_list_token_pb2.ListToken, _Mapping]] = ...) -> None: ...
