# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: db/delete.proto
# Protobuf Python Version: 5.27.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    27,
    1,
    '',
    'db/delete.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0f\x64\x62/delete.proto\x12\nstately.db\"b\n\rDeleteRequest\x12\x19\n\x08store_id\x18\x01 \x01(\x04R\x07storeId\x12\x30\n\x07\x64\x65letes\x18\x03 \x03(\x0b\x32\x16.stately.db.DeleteItemR\x07\x64\x65letesJ\x04\x08\x04\x10\x05\"\'\n\nDeleteItem\x12\x19\n\x08key_path\x18\x01 \x01(\tR\x07keyPath\"/\n\x0c\x44\x65leteResult\x12\x19\n\x08key_path\x18\x01 \x01(\tR\x07keyPathJ\x04\x08\x02\x10\x03\"D\n\x0e\x44\x65leteResponse\x12\x32\n\x07results\x18\x01 \x03(\x0b\x32\x18.stately.db.DeleteResultR\x07resultsBf\n\x0e\x63om.stately.dbB\x0b\x44\x65leteProtoP\x01\xa2\x02\x03SDX\xaa\x02\nStately.Db\xca\x02\nStately\\Db\xe2\x02\x16Stately\\Db\\GPBMetadata\xea\x02\x0bStately::Dbb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'db.delete_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'\n\016com.stately.dbB\013DeleteProtoP\001\242\002\003SDX\252\002\nStately.Db\312\002\nStately\\Db\342\002\026Stately\\Db\\GPBMetadata\352\002\013Stately::Db'
  _globals['_DELETEREQUEST']._serialized_start=31
  _globals['_DELETEREQUEST']._serialized_end=129
  _globals['_DELETEITEM']._serialized_start=131
  _globals['_DELETEITEM']._serialized_end=170
  _globals['_DELETERESULT']._serialized_start=172
  _globals['_DELETERESULT']._serialized_end=219
  _globals['_DELETERESPONSE']._serialized_start=221
  _globals['_DELETERESPONSE']._serialized_end=289
# @@protoc_insertion_point(module_scope)