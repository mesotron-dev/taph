"""Tests for the taph.config.tools_conf module."""
from taph.config.tools_conf import (
    code,
    default,
    freeze_error_messages,
    hash_error_messages,
    mark,
    thaw_error_messages,
)


def test_default_constants() -> None:
    """Verify hashing default values."""
    assert default.DIGEST_SIZE == 16


def test_encoding_protocol_stability() -> None:
    """Verify system binary markers and string conversion definitions are frozen."""
    assert code.BOOL == b'?'
    assert code.BIG == 'big'
    assert code.LITTLE == 'little'
    assert code.NONE == b'<NoneType>'
    assert code.UNSIGNED_BYTE == b'B'
    assert code.UNSIGNED_DBL_LONG == b'<Q'
    assert code.UTF8 == 'utf-8'


def test_reference_marks_domain_separation() -> None:
    """Verify strict token assignment numbers across every type domain."""
    assert mark.DIGEST == 1
    assert mark.INT == 2
    assert mark.FLOAT == 3
    assert mark.INF == 4
    assert mark.NEG_INF == 5
    assert mark.NAN == 6
    assert mark.COMPLEX == 7
    assert mark.DECIMAL == 8
    assert mark.FRACTION == 9
    assert mark.STRING == 10
    assert mark.BOOL == 11
    assert mark.BYTES == 12
    assert mark.NONE == 13
    assert mark.TUPLE == 14
    assert mark.SET == 15
    assert mark.MAP == 16
    assert mark.END == 17
    assert mark.UNKNOWN == 18


def test_tooling_error_message_interpolation_exact() -> None:
    """Verify exact string rendering for processing, serialization, and thawing errors."""
    # Freeze module messages
    assert (
        freeze_error_messages.freeze("<class 'set'>")
        == "Object of type <class 'set'> cannot be frozen."
    )

    # Hash module messages
    assert (
        hash_error_messages.type_error('list')
        == 'Object of type list is not hashable.'
    )

    # Thaw module messages
    assert (
        thaw_error_messages.type_error('Generator')
        == 'Object of type Generator cannot be thawed.'
    )
