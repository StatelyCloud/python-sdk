# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: db/transaction.proto
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
    'db/transaction.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import continue_list_pb2 as db_dot_continue__list__pb2
from . import delete_pb2 as db_dot_delete__pb2
from . import get_pb2 as db_dot_get__pb2
from . import item_pb2 as db_dot_item__pb2
from . import item_property_pb2 as db_dot_item__property__pb2
from . import list_pb2 as db_dot_list__pb2
from . import list_filters_pb2 as db_dot_list__filters__pb2
from . import put_pb2 as db_dot_put__pb2
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x14\x64\x62/transaction.proto\x12\nstately.db\x1a\x16\x64\x62/continue_list.proto\x1a\x0f\x64\x62/delete.proto\x1a\x0c\x64\x62/get.proto\x1a\rdb/item.proto\x1a\x16\x64\x62/item_property.proto\x1a\rdb/list.proto\x1a\x15\x64\x62/list_filters.proto\x1a\x0c\x64\x62/put.proto\x1a\x1bgoogle/protobuf/empty.proto\"\x9f\x04\n\x12TransactionRequest\x12\x1d\n\nmessage_id\x18\x01 \x01(\rR\tmessageId\x12\x34\n\x05\x62\x65gin\x18\x02 \x01(\x0b\x32\x1c.stately.db.TransactionBeginH\x00R\x05\x62\x65gin\x12\x39\n\tget_items\x18\x03 \x01(\x0b\x32\x1a.stately.db.TransactionGetH\x00R\x08getItems\x12\x41\n\nbegin_list\x18\x04 \x01(\x0b\x32 .stately.db.TransactionBeginListH\x00R\tbeginList\x12J\n\rcontinue_list\x18\x05 \x01(\x0b\x32#.stately.db.TransactionContinueListH\x00R\x0c\x63ontinueList\x12\x39\n\tput_items\x18\x06 \x01(\x0b\x32\x1a.stately.db.TransactionPutH\x00R\x08putItems\x12\x42\n\x0c\x64\x65lete_items\x18\x07 \x01(\x0b\x32\x1d.stately.db.TransactionDeleteH\x00R\x0b\x64\x65leteItems\x12\x30\n\x06\x63ommit\x18\x08 \x01(\x0b\x32\x16.google.protobuf.EmptyH\x00R\x06\x63ommit\x12.\n\x05\x61\x62ort\x18\t \x01(\x0b\x32\x16.google.protobuf.EmptyH\x00R\x05\x61\x62ortB\t\n\x07\x63ommand\"\xc8\x02\n\x13TransactionResponse\x12\x1d\n\nmessage_id\x18\x01 \x01(\rR\tmessageId\x12\x45\n\x0bget_results\x18\x02 \x01(\x0b\x32\".stately.db.TransactionGetResponseH\x00R\ngetResults\x12\x38\n\x07put_ack\x18\x03 \x01(\x0b\x32\x1d.stately.db.TransactionPutAckH\x00R\x06putAck\x12H\n\x0clist_results\x18\x04 \x01(\x0b\x32#.stately.db.TransactionListResponseH\x00R\x0blistResults\x12=\n\x08\x66inished\x18\x05 \x01(\x0b\x32\x1f.stately.db.TransactionFinishedH\x00R\x08\x66inishedB\x08\n\x06result\"v\n\x10TransactionBegin\x12\x19\n\x08store_id\x18\x01 \x01(\x04R\x07storeId\x12*\n\x11schema_version_id\x18\x02 \x01(\rR\x0fschemaVersionId\x12\x1b\n\tschema_id\x18\x03 \x01(\x04R\x08schemaId\"9\n\x0eTransactionGet\x12\'\n\x04gets\x18\x01 \x03(\x0b\x32\x13.stately.db.GetItemR\x04gets\"\xe4\x02\n\x14TransactionBeginList\x12&\n\x0fkey_path_prefix\x18\x01 \x01(\tR\rkeyPathPrefix\x12\x14\n\x05limit\x18\x02 \x01(\rR\x05limit\x12\x41\n\rsort_property\x18\x03 \x01(\x0e\x32\x1c.stately.db.SortablePropertyR\x0csortProperty\x12@\n\x0esort_direction\x18\x04 \x01(\x0e\x32\x19.stately.db.SortDirectionR\rsortDirection\x12H\n\x11\x66ilter_conditions\x18\t \x03(\x0b\x32\x1b.stately.db.FilterConditionR\x10\x66ilterConditions\x12?\n\x0ekey_conditions\x18\n \x03(\x0b\x32\x18.stately.db.KeyConditionR\rkeyConditions\"y\n\x17TransactionContinueList\x12\x1d\n\ntoken_data\x18\x01 \x01(\x0cR\ttokenData\x12?\n\tdirection\x18\x04 \x01(\x0e\x32!.stately.db.ContinueListDirectionR\tdirection\"9\n\x0eTransactionPut\x12\'\n\x04puts\x18\x01 \x03(\x0b\x32\x13.stately.db.PutItemR\x04puts\"E\n\x11TransactionDelete\x12\x30\n\x07\x64\x65letes\x18\x01 \x03(\x0b\x32\x16.stately.db.DeleteItemR\x07\x64\x65letes\"@\n\x16TransactionGetResponse\x12&\n\x05items\x18\x01 \x03(\x0b\x32\x10.stately.db.ItemR\x05items\"D\n\x0bGeneratedID\x12\x14\n\x04uint\x18\x01 \x01(\x04H\x00R\x04uint\x12\x16\n\x05\x62ytes\x18\x02 \x01(\x0cH\x00R\x05\x62ytesB\x07\n\x05value\"Q\n\x11TransactionPutAck\x12<\n\rgenerated_ids\x18\x01 \x03(\x0b\x32\x17.stately.db.GeneratedIDR\x0cgeneratedIds\"\x96\x01\n\x17TransactionListResponse\x12\x37\n\x06result\x18\x01 \x01(\x0b\x32\x1d.stately.db.ListPartialResultH\x00R\x06result\x12\x36\n\x08\x66inished\x18\x02 \x01(\x0b\x32\x18.stately.db.ListFinishedH\x00R\x08\x66inishedB\n\n\x08response\"\xa7\x01\n\x13TransactionFinished\x12\x1c\n\tcommitted\x18\x01 \x01(\x08R\tcommitted\x12\x31\n\x0bput_results\x18\x02 \x03(\x0b\x32\x10.stately.db.ItemR\nputResults\x12?\n\x0e\x64\x65lete_results\x18\x03 \x03(\x0b\x32\x18.stately.db.DeleteResultR\rdeleteResultsBk\n\x0e\x63om.stately.dbB\x10TransactionProtoP\x01\xa2\x02\x03SDX\xaa\x02\nStately.Db\xca\x02\nStately\\Db\xe2\x02\x16Stately\\Db\\GPBMetadata\xea\x02\x0bStately::Dbb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'db.transaction_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'\n\016com.stately.dbB\020TransactionProtoP\001\242\002\003SDX\252\002\nStately.Db\312\002\nStately\\Db\342\002\026Stately\\Db\\GPBMetadata\352\002\013Stately::Db'
  _globals['_TRANSACTIONREQUEST']._serialized_start=212
  _globals['_TRANSACTIONREQUEST']._serialized_end=755
  _globals['_TRANSACTIONRESPONSE']._serialized_start=758
  _globals['_TRANSACTIONRESPONSE']._serialized_end=1086
  _globals['_TRANSACTIONBEGIN']._serialized_start=1088
  _globals['_TRANSACTIONBEGIN']._serialized_end=1206
  _globals['_TRANSACTIONGET']._serialized_start=1208
  _globals['_TRANSACTIONGET']._serialized_end=1265
  _globals['_TRANSACTIONBEGINLIST']._serialized_start=1268
  _globals['_TRANSACTIONBEGINLIST']._serialized_end=1624
  _globals['_TRANSACTIONCONTINUELIST']._serialized_start=1626
  _globals['_TRANSACTIONCONTINUELIST']._serialized_end=1747
  _globals['_TRANSACTIONPUT']._serialized_start=1749
  _globals['_TRANSACTIONPUT']._serialized_end=1806
  _globals['_TRANSACTIONDELETE']._serialized_start=1808
  _globals['_TRANSACTIONDELETE']._serialized_end=1877
  _globals['_TRANSACTIONGETRESPONSE']._serialized_start=1879
  _globals['_TRANSACTIONGETRESPONSE']._serialized_end=1943
  _globals['_GENERATEDID']._serialized_start=1945
  _globals['_GENERATEDID']._serialized_end=2013
  _globals['_TRANSACTIONPUTACK']._serialized_start=2015
  _globals['_TRANSACTIONPUTACK']._serialized_end=2096
  _globals['_TRANSACTIONLISTRESPONSE']._serialized_start=2099
  _globals['_TRANSACTIONLISTRESPONSE']._serialized_end=2249
  _globals['_TRANSACTIONFINISHED']._serialized_start=2252
  _globals['_TRANSACTIONFINISHED']._serialized_end=2419
# @@protoc_insertion_point(module_scope)
