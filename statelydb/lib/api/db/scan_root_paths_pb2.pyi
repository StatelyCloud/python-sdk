from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ScanRootPathsRequest(_message.Message):
    __slots__ = ("store_id", "limit", "pagination_token", "schema_version_id")
    STORE_ID_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    store_id: int
    limit: int
    pagination_token: bytes
    schema_version_id: int
    def __init__(self, store_id: _Optional[int] = ..., limit: _Optional[int] = ..., pagination_token: _Optional[bytes] = ..., schema_version_id: _Optional[int] = ...) -> None: ...

class ScanRootPathsResponse(_message.Message):
    __slots__ = ("results", "pagination_token")
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[ScanRootPathResult]
    pagination_token: bytes
    def __init__(self, results: _Optional[_Iterable[_Union[ScanRootPathResult, _Mapping]]] = ..., pagination_token: _Optional[bytes] = ...) -> None: ...

class ScanRootPathResult(_message.Message):
    __slots__ = ("key_path",)
    KEY_PATH_FIELD_NUMBER: _ClassVar[int]
    key_path: str
    def __init__(self, key_path: _Optional[str] = ...) -> None: ...
