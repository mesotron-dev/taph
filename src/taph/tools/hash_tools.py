"""Cryptographic stability and content addressing.

This module implements deterministic, content-addressed hashing (BLAKE2b)
shared by FrozenDict, Immutable, and Namespace.

The hashing is order-sensitive for sequences & deterministic (sorted) for sets.

"""

import base64
import cmath
import decimal
import fractions
import math
import struct
from functools import singledispatch
from hashlib import blake2b
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

from taph.config.meta_conf import taph_type_conf as taph
from taph.config.tools_conf import code, default, mark
from taph.config.tools_conf import hash_error_messages as error_msg

__all__ = ('content_id', 'hash_id', 'hash_mapping', 'hex_id', 'mk_digest')


def mk_digest(data: object, digest_size: int = default.DIGEST_SIZE) -> bytes:
    """Compute a deterministic BLAKE2b digest of arbitrary (im)mutable data.

    Uses a custom serialization format with type markers and recursive feeding.
    Designed for content-addressing immutable structures.

    Args:
        data: Python object to hash (primitives, containers, __digest__).
        digest_size: Output size in bytes (default 16; max 64 for BLAKE2b).

    Returns:
        bytes: Fixed-length BLAKE2b digest.

    Raises:
        TypeError: If data type cannot be serialized.

    """
    hasher = blake2b(digest_size=digest_size)

    digest = getattr(data, taph.digest, None)
    if isinstance(digest, bytes):
        hasher.update(struct.pack(code.UNSIGNED_BYTE, mark.DIGEST))
        hasher.update(digest)
        return hasher.digest()

    _feed_digest(data, hasher)
    return hasher.digest()


def content_id(digest: bytes) -> str:
    """Convert a digest to a URL-safe base64 string (no padding).

    Suitable for filenames, cache keys, URLs, etc.

    Args:
        digest: Raw bytes from mk_digest().

    Returns:
        str: URL-safe base64 without '=' padding.

    """
    return base64.urlsafe_b64encode(digest).rstrip(b'=').decode(code.UTF8)


def hex_id(digest: bytes) -> str:
    """Convert a digest to a lowercase hexadecimal string.

    Args:
        digest: Raw bytes from mk_digest().

    Returns:
        str: Hex string (twice the digest length).

    """
    return digest.hex()


def hash_id(digest: bytes) -> int:
    """Generate a stable Python integer hash from a digest."""
    return int.from_bytes(digest, byteorder=code.BIG, signed=True)


def hash_mapping(size: int, items: Iterable[tuple[bytes, bytes]]) -> bytes:
    """Build up a digest from provided key/value digests.

    The hash_mapping is for creating the digest of Mapping.
    This is an internal tool for building a FrozenDict digest.

    Args:
        size (int): The size in bytes of the items being hashed.
        items (Iterable): The items being hashed.

    Returns:
        bytes: A hash digest for the provided mapping iterable.

    """
    hasher = blake2b(digest_size=default.DIGEST_SIZE)

    hasher.update(struct.pack(code.UNSIGNED_BYTE, mark.MAP))
    hasher.update(struct.pack(code.UNSIGNED_DBL_LONG, size))

    for key_digest, val_digest in items:
        hasher.update(key_digest)
        hasher.update(val_digest)

    hasher.update(struct.pack(code.UNSIGNED_BYTE, mark.END))
    return hasher.digest()


def _check_number(
    data: complex | decimal.Decimal | fractions.Fraction | float,
    hasher: blake2b
) -> None:
    """Mark special floating-point values (inf, -inf, nan) and continue.

    These values cannot use .as_integer_ratio(). so we mark them
    So each value is explicitly in the digest for deterministic hashing.

    Args:
        data (complex, Decimal, Fraction, float):
            The value to check for inf or nan.
        hasher (blake2b hash):
            The hasher used to create the digest.

    Raises:
        TypeError: Unhashable type of data.

    """
    try:
        is_inf = (
            math.isinf(data)
            if not isinstance(data, complex)
            else cmath.isinf(data)
        )
        is_nan = (
            math.isnan(data)
            if not isinstance(data, complex)
            else cmath.isnan(data)
        )
    except TypeError as e:
        raise TypeError(error_msg.type_error(type(data).__name__)) from e

    if is_inf:
        if hasattr(data, 'real') and data.real > 0:
            hasher.update(struct.pack(code.UNSIGNED_BYTE, mark.INF))
        else:
            hasher.update(struct.pack(code.UNSIGNED_BYTE, mark.NEG_INF))
        return

    if is_nan:
        hasher.update(struct.pack(code.UNSIGNED_BYTE, mark.NAN))
        return

    # Some unhashable value
    raise TypeError(error_msg.type_error(type(data).__name__))


def _feed_int_ratio(data: tuple[int, int], hasher: blake2b) -> None:
    numerator, denominator = data
    n_bytes = (numerator.bit_length() + 8) // 8
    d_bytes = (denominator.bit_length() + 8) // 8

    hasher.update(struct.pack(code.UNSIGNED_DBL_LONG, n_bytes))
    hasher.update(
        numerator.to_bytes(n_bytes, byteorder=code.LITTLE, signed=True)
    )

    hasher.update(struct.pack(code.UNSIGNED_DBL_LONG, d_bytes))
    hasher.update(
        denominator.to_bytes(d_bytes, byteorder=code.LITTLE, signed=True)
    )


@singledispatch
def _feed_digest(data: object, hasher: blake2b) -> None:
    """Default dispatcher."""
    digest = getattr(data, taph.digest, None)
    if isinstance(digest, bytes):
        hasher.update(struct.pack(code.UNSIGNED_BYTE, mark.DIGEST))
        hasher.update(digest)
        return
    raise TypeError(error_msg.type_error(type(data).__name__))


@_feed_digest.register(tuple)
def _(data: tuple[object], hasher: blake2b) -> None:
    hasher.update(struct.pack(code.UNSIGNED_BYTE, mark.TUPLE))
    hasher.update(struct.pack(code.UNSIGNED_DBL_LONG, len(data)))
    for item in data:
        _feed_digest(item, hasher)
    hasher.update(struct.pack(code.UNSIGNED_BYTE, mark.END))


@_feed_digest.register(frozenset)
def _(data: frozenset[object], hasher: blake2b) -> None:
    hasher.update(struct.pack(code.UNSIGNED_BYTE, mark.SET))
    hasher.update(struct.pack(code.UNSIGNED_DBL_LONG, len(data)))
    sorted_digests = sorted(mk_digest(item) for item in data)
    for digest in sorted_digests:
        hasher.update(digest)
    hasher.update(struct.pack(code.UNSIGNED_BYTE, mark.END))


@_feed_digest.register(str)
def _(data: str, hasher: blake2b) -> None:
    hasher.update(struct.pack(code.UNSIGNED_BYTE, mark.STRING))
    encoded_data = data.encode(code.UTF8)
    hasher.update(struct.pack(code.UNSIGNED_DBL_LONG, len(encoded_data)))
    hasher.update(encoded_data)


@_feed_digest.register(bool)
def _(data: bool, hasher: blake2b) -> None:
    hasher.update(struct.pack(code.UNSIGNED_BYTE, mark.BOOL))
    hasher.update(struct.pack(code.BOOL, data))


@_feed_digest.register(bytes)
def _(data: bytes, hasher: blake2b) -> None:
    hasher.update(struct.pack(code.UNSIGNED_BYTE, mark.BYTES))
    hasher.update(struct.pack(code.UNSIGNED_DBL_LONG, len(data)))
    hasher.update(data)


@_feed_digest.register(type(None))
def _(data: None, hasher: blake2b) -> None:  # noqa #ARG003
    hasher.update(struct.pack(code.UNSIGNED_BYTE, mark.NONE))
    hasher.update(struct.pack(code.UNSIGNED_DBL_LONG, len(code.NONE)))
    hasher.update(code.NONE)


@_feed_digest.register(int)
def _(data: int, hasher: blake2b) -> None:
    data_bytes: int = (data.bit_length() + 8) // 8
    hasher.update(struct.pack(code.UNSIGNED_BYTE, mark.INT))
    hasher.update(struct.pack(code.UNSIGNED_DBL_LONG, data_bytes))
    hasher.update(data.to_bytes(data_bytes, byteorder=code.LITTLE, signed=True))


@_feed_digest.register(float)
def _(data: float, hasher: blake2b) -> None:
    hasher.update(struct.pack(code.UNSIGNED_BYTE, mark.FLOAT))
    try:
        _feed_int_ratio(data.as_integer_ratio(), hasher)
    except (OverflowError, ValueError):
        _check_number(data, hasher)


@_feed_digest.register(complex)
def _(data: complex, hasher: blake2b) -> None:
    hasher.update(struct.pack(code.UNSIGNED_BYTE, mark.COMPLEX))
    try:
        _feed_int_ratio(data.real.as_integer_ratio(), hasher)
        _feed_int_ratio(data.imag.as_integer_ratio(), hasher)
    except (OverflowError, ValueError):
        _check_number(data, hasher)
    hasher.update(struct.pack(code.UNSIGNED_BYTE, mark.END))


@_feed_digest.register(decimal.Decimal)
def _(data: decimal.Decimal, hasher: blake2b) -> None:
    hasher.update(struct.pack(code.UNSIGNED_BYTE, mark.DECIMAL))
    try:
        _feed_int_ratio(data.as_integer_ratio(), hasher)
    except (OverflowError, ValueError):
        _check_number(data, hasher)
    hasher.update(struct.pack(code.UNSIGNED_BYTE, mark.END))


@_feed_digest.register(fractions.Fraction)
def _(data: fractions.Fraction, hasher: blake2b) -> None:
    hasher.update(struct.pack(code.UNSIGNED_BYTE, mark.FRACTION))
    _feed_int_ratio(data.as_integer_ratio(), hasher)
    hasher.update(struct.pack(code.UNSIGNED_BYTE, mark.END))
