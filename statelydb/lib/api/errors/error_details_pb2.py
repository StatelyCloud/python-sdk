# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: errors/error_details.proto
# Protobuf Python Version: 5.29.3
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    3,
    '',
    'errors/error_details.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1a\x65rrors/error_details.proto\x12\x0estately.errors\"\x8d\x01\n\x13StatelyErrorDetails\x12!\n\x0cstately_code\x18\x01 \x01(\tR\x0bstatelyCode\x12\x18\n\x07message\x18\x02 \x01(\tR\x07message\x12%\n\x0eupstream_cause\x18\x03 \x01(\tR\rupstreamCause\x12\x12\n\x04\x63ode\x18\x04 \x01(\rR\x04\x63odeB\x80\x01\n\x12\x63om.stately.errorsB\x11\x45rrorDetailsProtoP\x01\xa2\x02\x03SEX\xaa\x02\x0eStately.Errors\xca\x02\x0eStately\\Errors\xe2\x02\x1aStately\\Errors\\GPBMetadata\xea\x02\x0fStately::Errorsb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'errors.error_details_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'\n\022com.stately.errorsB\021ErrorDetailsProtoP\001\242\002\003SEX\252\002\016Stately.Errors\312\002\016Stately\\Errors\342\002\032Stately\\Errors\\GPBMetadata\352\002\017Stately::Errors'
  _globals['_STATELYERRORDETAILS']._serialized_start=47
  _globals['_STATELYERRORDETAILS']._serialized_end=188
# @@protoc_insertion_point(module_scope)
