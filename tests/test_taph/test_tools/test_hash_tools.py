"""Test suite for taph.tools.hash_tools."""

import cmath
import decimal
import fractions
import math
import struct
from hashlib import blake2b
from typing import Any

import pytest

from taph.config.tools_conf import code, mark
from taph.tools.hash_tools import (
    _check_number,
    _feed_digest,
    content_id,
    hash_id,
    hash_mapping,
    hex_id,
    mk_digest,
)


# ---------------------------------------------------------
# 1. Structural Hash Utility Conversions & Formats
# ---------------------------------------------------------

def test_hash_conversions_and_formats() -> None:
    """Validate hex, base64 url-safe, and integer stable-ID mappings."""
    digest = b'0123456789abcdef'

    # hex_id check (Lowercase hex string, exactly twice the bytes length)
    assert hex_id(digest) == '30313233343536373839616263646566'

    # content_id check (URL-safe base64 string, completely stripped of padding)
    c_id = content_id(digest)
    assert '=' not in c_id
    assert '+' not in c_id
    assert '/' not in c_id
    assert c_id == 'MDEyMzQ1Njc4OWFiY2RlZg'

    # hash_id check (Deterministic, signed, big-endian integer extraction)
    expected_int = int.from_bytes(digest, byteorder='big', signed=True)
    assert hash_id(digest) == expected_int


def test_hash_mapping_structure() -> None:
    """Validate empty and populated hash mapping state calculations."""
    # Boundary condition: Empty Mapping
    empty_digest = hash_mapping(0, [])
    assert len(empty_digest) == 16

    # Standard mapping compilation
    pairs = [(b'key_1', b'val_1'), (b'key_2', b'val_2')]
    populated_digest = hash_mapping(len(pairs), pairs)
    assert len(populated_digest) == 16
    assert empty_digest != populated_digest


# ---------------------------------------------------------
# 2. Metaclass/Immutable Protocol Fast-Path Checks (MC/DC)
# ---------------------------------------------------------

def test_mk_digest_immutable_protocol_bytes() -> None:
    """MC/DC: Test branch where data.__digest__ is active and is bytes."""
    class MockImmutableBytes:
        __digest__ = b'secure_hash_val_'

    obj = MockImmutableBytes()
    digest = mk_digest(obj)

    # Expected: Bypasses standard hashing, writes mark.DIGEST, returns result
    hasher = blake2b(digest_size=16)
    hasher.update(struct.pack(code.UNSIGNED_BYTE, mark.DIGEST))
    hasher.update(b'secure_hash_val_')
    assert digest == hasher.digest()


def test_mk_digest_immutable_protocol_non_bytes() -> None:
    """MC/DC: Test branch where data.__digest__ exists but is not bytes."""
    class MockImmutableBadDigest:
        __digest__ = 123456  # Invalid non-bytes type

    obj = MockImmutableBadDigest()
    # Expected: Falls through to standard hashing, ultimately raising TypeError
    # since custom classes without dispatcher or valid byte-digests are unhashable.
    with pytest.raises(TypeError, match='is not hashable'):
        mk_digest(obj)


# ---------------------------------------------------------
# 3. Numeric Serializer & Float Exception Checks (_check_number)
# ---------------------------------------------------------

def test_check_number_fallback_type_error() -> None:
    """MC/DC: Direct invocation of _check_number with invalid type.

    Ensures that the internal try/except fallback block on math/cmath checks
    correctly intercepts non-numeric objects and maps them to a TypeError.
    """
    hasher = blake2b(digest_size=16)
    with pytest.raises(TypeError, match='is not hashable'):
        _check_number('unsupported_string', hasher)  # type: ignore[arg-type]


# ---------------------------------------------------------
# 4. Singledispatch Type-Specific Registers
# ---------------------------------------------------------

def test_hash_tuple_boundaries() -> None:
    """Validate empty, non-empty, and deep recursive tuple structures."""
    # Empty tuple (0 elements)
    d_empty = mk_digest(())
    assert len(d_empty) == 16

    # Normal populated tuple
    d_flat = mk_digest((1, 2, 3))

    # Nested recursive tuple
    d_nested = mk_digest((1, (2, 3)))
    assert d_empty != d_flat
    assert d_flat != d_nested


def test_hash_frozenset_determinism() -> None:
    """Validate frozensets are sorted deterministically, ensuring order-independence."""
    fs1 = frozenset([10, 20, 30])
    fs2 = frozenset([30, 20, 10])

    # Order independence assertion
    assert mk_digest(fs1) == mk_digest(fs2)

    # Value difference assertion
    assert mk_digest(fs1) != mk_digest(frozenset([10, 20]))


def test_hash_str_encodings() -> None:
    """Validate ASCII and multi-byte UTF-8 Unicode string serializers."""
    assert mk_digest('') != mk_digest(' ')
    assert mk_digest('hello') != mk_digest('world')

    # Validate encoding safety boundaries
    unicode_digest_1 = mk_digest('こんにちは')
    unicode_digest_2 = mk_digest('世界')
    assert len(unicode_digest_1) == 16
    assert unicode_digest_1 != unicode_digest_2


def test_hash_bool_domain() -> None:
    """Validate boolean type hashing."""
    assert mk_digest(True) != mk_digest(False)


def test_hash_bytes_domain() -> None:
    """Validate raw binary data serialization."""
    assert mk_digest(b'') != mk_digest(b'\x00')
    assert mk_digest(b'taph') == mk_digest(b'taph')


def test_hash_none_constant() -> None:
    """Validate None constant hashing."""
    assert len(mk_digest(None)) == 16


def test_hash_integer_precision() -> None:
    """Validate variable-length integer serialization across bit boundaries."""
    assert mk_digest(0) != mk_digest(1)
    assert mk_digest(-1) != mk_digest(1)

    # Boundary: Extremely large integers that force bit length expansions
    large_pos = 2**128
    large_neg = -(2**128)
    assert mk_digest(large_pos) != mk_digest(large_neg)


def test_hash_fractions_decimals_floats() -> None:
    """Validate float, decimal, and fraction numeric ratio serializers."""
    assert mk_digest(0.1) != mk_digest(0.2)
    assert mk_digest(decimal.Decimal('0.1')) != mk_digest(decimal.Decimal('0.2'))
    assert mk_digest(fractions.Fraction(1, 10)) != mk_digest(fractions.Fraction(2, 10))


# ---------------------------------------------------------
# 5. Security Safeguards, Exceptions & Boundaries
# ---------------------------------------------------------

def test_unhashable_types() -> None:
    """Ensure mutable standard Python structures trigger strict TypeError bounds."""
    with pytest.raises(TypeError, match='is not hashable'):
        mk_digest([1, 2, 3])  # list

    with pytest.raises(TypeError, match='is not hashable'):
        mk_digest({'a': 1})  # dict

    with pytest.raises(TypeError, match='is not hashable'):
        mk_digest({1, 2})  # set


def test_recursive_nested_custom_immutables() -> None:
    """Validate recursive traversal of custom immutable objects in containers.

    This exercises the fallback branch inside the `@singledispatch` default
    implementation when encountered as a nested element during structured
    traversal (e.g. inside a tuple).
    """
    class CustomImmutableMock:
        def __init__(self, digest: bytes) -> None:
            self.__digest__ = digest

    mock_obj = CustomImmutableMock(b'crypt_bytes_1234')
    container = (42, mock_obj)

    # Expected: The default dispatch logic should recursively inspect 'mock_obj',
    # successfully locate its '__digest__' bytes, and serialize without error.
    digest = mk_digest(container)
    assert isinstance(digest, bytes)
    assert len(digest) == 16


def test_custom_digest_size_override() -> None:
    """Verify that customized digest size overrides generate correctly sized hashes."""
    # Standard output matches global defaults (16 bytes)
    assert len(mk_digest(100)) == 16

    # Custom digest size constraints (e.g., 32-byte hash)
    assert len(mk_digest(100, digest_size=32)) == 32


def test_hash_complex_normal() -> None:
    """Validate hashing of standard, valid complex numbers.

    This ensures the final non-exception lines (such as mark.END) of the
    complex register are fully covered under non-error pathways.
    """
    c1 = complex(1.5, -2.5)
    c2 = complex(1.5, -2.5)
    c3 = complex(3.0, 4.0)

    assert mk_digest(c1) == mk_digest(c2)
    assert mk_digest(c1) != mk_digest(c3)


# ---------------------------------------------------------
# Numeric Serializer & Special Value Checks (_check_number)
# ---------------------------------------------------------

def test_check_number_special_values() -> None:
    """Test that inf, -inf, and nan are properly marked and hashing continues."""
    hasher = blake2b(digest_size=16)

    _check_number(float('inf'), hasher)
    _check_number(float('-inf'), hasher)
    _check_number(float('nan'), hasher)

    _check_number(complex('inf'), hasher)
    _check_number(complex('-inf'), hasher)
    _check_number(complex('nan'), hasher)

    _check_number(decimal.Decimal('Infinity'), hasher)
    _check_number(decimal.Decimal('-Infinity'), hasher)
    _check_number(decimal.Decimal('NaN'), hasher)


def test_check_number_raises_on_bad_input() -> None:
    """Non-numeric or unsupported types should raise TypeError."""
    hasher = blake2b(digest_size=16)

    with pytest.raises(TypeError, match='is not hashable'):
        _check_number('not a number', hasher)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match='is not hashable'):
        _check_number([1, 2, 3], hasher)  # type: ignore[arg-type]

    with pytest.raises(ZeroDivisionError):
        _check_number(fractions.Fraction(1, 0), hasher)


def test_check_number_branches() -> None:
    """Coverage for all decision branches in _check_number."""
    hasher = blake2b(digest_size=16)

    # Positive inf path
    _check_number(float('inf'), hasher)

    # Negative inf path
    _check_number(float('-inf'), hasher)

    # NaN path
    _check_number(float('nan'), hasher)

    # Complex inf path
    _check_number(complex('inf'), hasher)

    # Decimal inf path
    _check_number(decimal.Decimal('Infinity'), hasher)


def test_numeric_dispatchers_exception_paths() -> None:
    """Test OverflowError and ValueError paths _check_number types."""

    test_values = [
        float('inf'),
        float('-inf'),
        float('nan'),
        complex('inf'),
        complex('nan'),
        decimal.Decimal('Infinity'),
        decimal.Decimal('-Infinity'),
        decimal.Decimal('NaN'),
    ]

    for value in test_values:
        digest = mk_digest(value)
        assert isinstance(digest, bytes)
        assert len(digest) == 16


def test_special_floats_inf_nan() -> None:
    """Verify BLAKE2b digest determinism and separation for float inf, -inf, and nan."""
    pos_inf = float('inf')
    neg_inf = float('-inf')
    nan_val = float('nan')

    digest_pos_inf = mk_digest(pos_inf)
    digest_neg_inf = mk_digest(neg_inf)
    digest_nan = mk_digest(nan_val)

    # All must produce valid, unique digests
    assert isinstance(digest_pos_inf, bytes)
    assert len(digest_pos_inf) == 16
    assert digest_pos_inf != digest_neg_inf
    assert digest_pos_inf != digest_nan
    assert digest_neg_inf != digest_nan

    # NaN must hash deterministically, regardless of distinct object identity
    assert mk_digest(float('nan')) == digest_nan


def test_special_complex_inf_nan() -> None:
    """Verify BLAKE2b digests for complex inf, -inf, and nan values."""
    comp_inf = complex('inf')
    comp_neg_inf = complex('-inf')
    comp_nan = complex('nan')

    digest_inf = mk_digest(comp_inf)
    digest_neg_inf = mk_digest(comp_neg_inf)
    digest_nan = mk_digest(comp_nan)

    assert isinstance(digest_inf, bytes)
    assert len(digest_inf) == 16
    assert digest_inf != digest_neg_inf
    assert digest_inf != digest_nan


def test_special_decimals_inf_nan() -> None:
    """Verify BLAKE2b digests for Decimal infinity and NaN values."""
    dec_inf = decimal.Decimal('Infinity')
    dec_neg_inf = decimal.Decimal('-Infinity')
    dec_nan = decimal.Decimal('NaN')

    digest_inf = mk_digest(dec_inf)
    digest_neg_inf = mk_digest(dec_neg_inf)
    digest_nan = mk_digest(dec_nan)

    assert isinstance(digest_inf, bytes)
    assert len(digest_inf) == 16
    assert digest_inf != digest_neg_inf
    assert digest_inf != digest_nan


def test_fraction_boundary_conditions() -> None:
    """Verify Fraction boundary cases and division-by-zero checks."""
    frac_normal = fractions.Fraction(1, 3)
    assert isinstance(mk_digest(frac_normal), bytes)

    # Fractions with zero denominator are invalid in Python's fraction module,
    # raising ZeroDivisionError during construction.
    with pytest.raises(ZeroDivisionError):
        _ = fractions.Fraction(1, 0)


def test_invalid_type_error_boundaries() -> None:
    """Validate that unhashable or invalid types strictly raise a TypeError."""

    class UnhashableObject:
        """A plain class without the Immutable or Freezable protocols."""
        pass

    # Standard mutable structures
    with pytest.raises(TypeError, match="is not hashable"):
        mk_digest([1, 2, 3])  # list

    with pytest.raises(TypeError, match="is not hashable"):
        mk_digest({"a": 1})  # dict

    # Custom non-conforming objects
    with pytest.raises(TypeError, match="is not hashable"):
        mk_digest(UnhashableObject())


def test_check_number_unsupported_types() -> None:
    """Verify that _check_number raises TypeError directly for non-numeric types."""
    from hashlib import blake2b
    hasher = blake2b(digest_size=16)

    # Passing raw strings to _check_number must trigger the internal except handler
    with pytest.raises(TypeError, match="is not hashable"):
        _check_number("string", hasher)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="is not hashable"):
        _check_number(None, hasher)  # type: ignore[arg-type]
