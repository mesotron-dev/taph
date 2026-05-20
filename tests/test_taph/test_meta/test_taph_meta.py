"""Tests for the taph.meta.taph_meta module (TaphType Metaclass)."""

import pytest
from taph.meta.taph_meta import TaphType
from taph.exceptions import ImmutableError
from taph.config.meta_conf import taph_type_conf as taph


class DummyTaphClass(metaclass=TaphType):
    """Pragmatic mock class using TaphType."""

    __slots__ = ()


def test_taph_type_new_requires_slots() -> None:
    """Verify Class creation fails immediately if __slots__ is absent."""
    with pytest.raises(TypeError, match="must define '__slots__'"):
        class BadClass(metaclass=TaphType):
            pass


def test_taph_type_new_filters_non_string_keys() -> None:
    """Ensure non-string keys (py3.12+ generic leaks) are securely filtered."""
    namespace = {'__slots__': (), 42: "leaked_generic_key"}
    cls = TaphType('GenericClass', (), namespace)
    assert not hasattr(cls, '42')
    assert 42 not in cls.__dict__


def test_taph_type_block_setattr_and_delattr() -> None:
    """Verify instance block operations prevent mutation and deletion."""
    instance = DummyTaphClass()
    with pytest.raises(ImmutableError, match="instance_setattr"):
        TaphType._block_setattr(instance, "x", 1)

    with pytest.raises(ImmutableError, match="instance_delattr"):
        TaphType._block_delattr(instance, "x")


def test_taph_type_class_level_setattr_mcdc() -> None:
    """Test class-level attribute assignment overrides and guards."""
    for internal in taph.class_internals():
        TaphType.__setattr__(DummyTaphClass, internal, "allowed_val")
        assert getattr(DummyTaphClass, internal) == "allowed_val"

    TaphType.__setattr__(DummyTaphClass, "_abc_cache", "abc_allowed")
    assert getattr(DummyTaphClass, "_abc_cache") == "abc_allowed"

    TaphType.__setattr__(DummyTaphClass, "__abstractmethods__", "abstract_allowed")
    assert getattr(DummyTaphClass, "__abstractmethods__") == "abstract_allowed"

    with pytest.raises(ImmutableError, match="class_setattr"):
        DummyTaphClass.some_new_class_attr = 999


def test_taph_type_class_level_delattr_mcdc() -> None:
    """Test class-level attribute deletion overrides and guards."""
    TaphType.__setattr__(DummyTaphClass, "_abc_delete_target", "delete_me")
    assert getattr(DummyTaphClass, "_abc_delete_target") == "delete_me"

    TaphType.__delattr__(DummyTaphClass, "_abc_delete_target")
    assert not hasattr(DummyTaphClass, "_abc_delete_target")

    with pytest.raises(ImmutableError, match="class_delattr"):
        del DummyTaphClass.__slots__
