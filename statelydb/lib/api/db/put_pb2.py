# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: db/put.proto
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
    'db/put.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import item_pb2 as db_dot_item__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0c\x64\x62/put.proto\x12\nstately.db\x1a\rdb/item.proto\"P\n\nPutRequest\x12\x19\n\x08store_id\x18\x01 \x01(\x04R\x07storeId\x12\'\n\x04puts\x18\x02 \x03(\x0b\x32\x13.stately.db.PutItemR\x04puts\"/\n\x07PutItem\x12$\n\x04item\x18\x01 \x01(\x0b\x32\x10.stately.db.ItemR\x04item\"5\n\x0bPutResponse\x12&\n\x05items\x18\x01 \x03(\x0b\x32\x10.stately.db.ItemR\x05itemsBc\n\x0e\x63om.stately.dbB\x08PutProtoP\x01\xa2\x02\x03SDX\xaa\x02\nStately.Db\xca\x02\nStately\\Db\xe2\x02\x16Stately\\Db\\GPBMetadata\xea\x02\x0bStately::Dbb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'db.put_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'\n\016com.stately.dbB\010PutProtoP\001\242\002\003SDX\252\002\nStately.Db\312\002\nStately\\Db\342\002\026Stately\\Db\\GPBMetadata\352\002\013Stately::Db'
  _globals['_PUTREQUEST']._serialized_start=43
  _globals['_PUTREQUEST']._serialized_end=123
  _globals['_PUTITEM']._serialized_start=125
  _globals['_PUTITEM']._serialized_end=172
  _globals['_PUTRESPONSE']._serialized_start=174
  _globals['_PUTRESPONSE']._serialized_end=227
# @@protoc_insertion_point(module_scope)