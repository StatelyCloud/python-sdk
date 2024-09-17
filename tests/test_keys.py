"""Test key generation functions."""

from __future__ import annotations

from uuid import UUID

import pytest
from statelydb.src.errors import StatelyError
from statelydb.src.keys import key_id, key_path


def test_key_path__single_level_paths() -> None:
    assert key_path("/foo-{id}", id="bar") == "/foo-bar"
    assert key_path("/foo-{id}", id="1234") == "/foo-1234"
    assert key_path("/foo-{id}", id=1234) == "/foo-1234"
    assert (
        key_path("/foo-{id}", id=UUID("f4a8a24a-129d-411f-91d2-6d19d0eaa096"))
        == "/foo-9KiiShKdQR-R0m0Z0Oqglg"
    )


def test_key_path__multi_level_paths() -> None:
    assert (
        key_path("/foo-{id1}/baz-{id2}/quux-{id3}", id1="bar", id2="qux", id3="corge")
        == "/foo-bar/baz-qux/quux-corge"
    )


def test_key_path__partial_paths() -> None:
    assert key_path("/foo-{id1}/namespace", id1="bar") == "/foo-bar/namespace"


def test_key_id__uuid() -> None:
    assert (
        key_id(UUID("00000000-0000-0000-0000-000000000005"))
        == "AAAAAAAAAAAAAAAAAAAABQ"
    )


def test_key_id__string() -> None:
    assert key_id("batman") == "batman"


def test_key_id__binary() -> None:
    assert key_id(b"\x00\x01\x02\x03") == "AAECAw"


def test_key_id__int() -> None:
    assert key_id(1234) == "1234"


def test_key_id__negative_int() -> None:
    with pytest.raises(StatelyError) as e:
        key_id(-1234)
    assert e.value.stately_code == "InvalidKeyPath"


def test_key_id__invalid_type() -> None:
    with pytest.raises(StatelyError) as e:
        key_id(3.14)  # type: ignore[arg-type,reportArgumentType] # ignore for the purpose of testing.
    assert e.value.stately_code == "InvalidKeyPath"
