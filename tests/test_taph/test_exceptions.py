"""Tests for the exceptions module."""

import pytest
from taph.exceptions import (
    TaphError, ImmutableError, RecordError,
    ManifestError, FrozenDictError
)

def test_exception_hierarchy():
    """Verify that ImmutableError satisfies multiple standard interfaces."""
    exc = ImmutableError("Mutation failed")

    assert isinstance(exc, TaphError)
    assert isinstance(exc, AttributeError)
    assert isinstance(exc, TypeError)

def test_frozen_dict_error_inheritance():
    """Verify FrozenDictError maps to KeyError for Mapping compatibility."""
    exc = FrozenDictError("Key missing or immutable")

    assert isinstance(exc, TaphError)
    assert isinstance(exc, KeyError)

@pytest.mark.parametrize("exc_class", [RecordError, ManifestError])
def test_generic_taph_errors(exc_class):
    """Ensure structural errors inherit from the base TaphError."""
    assert issubclass(exc_class, TaphError)
