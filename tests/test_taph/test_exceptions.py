"""Tests for the exceptions module."""

from taph.exceptions import ImmutableError, TaphError


def test_exception_hierarchy():
    """Verify inheritance structure for clean error handling."""
    err = ImmutableError("test")

    assert isinstance(err, TaphError)
    assert isinstance(err, TypeError)
    assert isinstance(err, Exception)
