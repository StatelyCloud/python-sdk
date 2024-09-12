"""Contains tests for SDK error code."""

from __future__ import annotations

from grpclib import Status
from statelydb import StatelyCode, StatelyError


async def test_error_formatter() -> None:
    """Tests that the error formatter correctly formats the error message."""
    error = StatelyError(
        stately_code=StatelyCode.NON_RECOVERABLE_TRANSACTION,
        grpc_code=Status.NOT_FOUND,
        message="test_message",
        cause="test_cause",
    )

    assert error.stately_code == StatelyCode.NON_RECOVERABLE_TRANSACTION

    assert str(error) == "(NotFound/NonRecoverableTransaction) test_message"
