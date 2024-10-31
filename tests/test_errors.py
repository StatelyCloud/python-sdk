"""Contains tests for SDK error code."""

from __future__ import annotations

from grpclib import Status
from statelydb import StatelyCode, StatelyError


async def test_error_formatter() -> None:
    """Tests that the error formatter correctly formats the error message."""
    error = StatelyError(
        stately_code=StatelyCode.NON_RECOVERABLE_TRANSACTION,
        code=Status.NOT_FOUND,
        message="test_message",
        cause="test_cause",
    )

    assert error.stately_code == StatelyCode.NON_RECOVERABLE_TRANSACTION

    assert str(error) == "(NotFound/NonRecoverableTransaction) test_message"


async def test_code_as_int() -> None:
    """Tests that we can pass in the code as an int."""
    error = StatelyError(
        stately_code=StatelyCode.NON_RECOVERABLE_TRANSACTION,
        code=5,
        message="test_message",
        cause="test_cause",
    )

    assert error.code == Status.NOT_FOUND


async def test_invalid_int_code() -> None:
    """Tests that we set code: UNKNOWN if the int code is invalid."""
    error = StatelyError(
        stately_code=StatelyCode.NON_RECOVERABLE_TRANSACTION,
        code=-1,
        message="test_message",
        cause="test_cause",
    )

    assert error.code == Status.UNKNOWN
