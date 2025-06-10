from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class FilterCondition(_message.Message):
    __slots__ = ("item_type",)
    ITEM_TYPE_FIELD_NUMBER: _ClassVar[int]
    item_type: str
    def __init__(self, item_type: _Optional[str] = ...) -> None: ...
