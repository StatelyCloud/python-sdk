# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: db/scan_root_paths.proto
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
    'db/scan_root_paths.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x18\x64\x62/scan_root_paths.proto\x12\nstately.db\"\x9e\x01\n\x14ScanRootPathsRequest\x12\x19\n\x08store_id\x18\x01 \x01(\x04R\x07storeId\x12\x14\n\x05limit\x18\x02 \x01(\rR\x05limit\x12)\n\x10pagination_token\x18\x03 \x01(\x0cR\x0fpaginationToken\x12*\n\x11schema_version_id\x18\x04 \x01(\rR\x0fschemaVersionId\"|\n\x15ScanRootPathsResponse\x12\x38\n\x07results\x18\x01 \x03(\x0b\x32\x1e.stately.db.ScanRootPathResultR\x07results\x12)\n\x10pagination_token\x18\x02 \x01(\x0cR\x0fpaginationToken\"/\n\x12ScanRootPathResult\x12\x19\n\x08key_path\x18\x01 \x01(\tR\x07keyPathBm\n\x0e\x63om.stately.dbB\x12ScanRootPathsProtoP\x01\xa2\x02\x03SDX\xaa\x02\nStately.Db\xca\x02\nStately\\Db\xe2\x02\x16Stately\\Db\\GPBMetadata\xea\x02\x0bStately::Dbb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'db.scan_root_paths_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'\n\016com.stately.dbB\022ScanRootPathsProtoP\001\242\002\003SDX\252\002\nStately.Db\312\002\nStately\\Db\342\002\026Stately\\Db\\GPBMetadata\352\002\013Stately::Db'
  _globals['_SCANROOTPATHSREQUEST']._serialized_start=41
  _globals['_SCANROOTPATHSREQUEST']._serialized_end=199
  _globals['_SCANROOTPATHSRESPONSE']._serialized_start=201
  _globals['_SCANROOTPATHSRESPONSE']._serialized_end=325
  _globals['_SCANROOTPATHRESULT']._serialized_start=327
  _globals['_SCANROOTPATHRESULT']._serialized_end=374
# @@protoc_insertion_point(module_scope)
