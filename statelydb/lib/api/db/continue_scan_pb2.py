# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: db/continue_scan.proto
# Protobuf Python Version: 6.31.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    6,
    31,
    1,
    '',
    'db/continue_scan.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x16\x64\x62/continue_scan.proto\x12\nstately.db\"}\n\x13\x43ontinueScanRequest\x12\x1d\n\ntoken_data\x18\x01 \x01(\x0cR\ttokenData\x12*\n\x11schema_version_id\x18\x02 \x01(\rR\x0fschemaVersionId\x12\x1b\n\tschema_id\x18\x03 \x01(\x04R\x08schemaIdBl\n\x0e\x63om.stately.dbB\x11\x43ontinueScanProtoP\x01\xa2\x02\x03SDX\xaa\x02\nStately.Db\xca\x02\nStately\\Db\xe2\x02\x16Stately\\Db\\GPBMetadata\xea\x02\x0bStately::Dbb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'db.continue_scan_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'\n\016com.stately.dbB\021ContinueScanProtoP\001\242\002\003SDX\252\002\nStately.Db\312\002\nStately\\Db\342\002\026Stately\\Db\\GPBMetadata\352\002\013Stately::Db'
  _globals['_CONTINUESCANREQUEST']._serialized_start=38
  _globals['_CONTINUESCANREQUEST']._serialized_end=163
# @@protoc_insertion_point(module_scope)
