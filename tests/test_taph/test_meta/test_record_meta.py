"""Tests for the taph.meta.record_meta module (RecordType)."""

from __future__ import annotations
# lazy eval in 3.14 annotations requires from future
import pytest
from taph.record import Record
from taph.meta.record_meta import (
    RecordType,
    _compile_init,
    _namespace_guard,
    _prepare_record_fields,
    _check_mro_fields,
)
from taph.exceptions import ImmutableError

class ParentRecord(Record):
    __slots__ = ("parent_id", "parent_name", "__digest__")
    parent_id: int
    parent_name: str


class ProtectedRecord(Record):
    __slots__ = ("id",)
    id: int


def test_record_compile_init_zero_fields() -> None:
    """Verify boundary instantiation on compiling record with no custom attributes."""
    init_func = _compile_init("EmptyRecord", [], {})
    assert init_func is not None

    class DummyInstance:
        pass

    instance = DummyInstance()
    init_func(instance)
    assert hasattr(instance, '__digest__')


def test_record_compile_init_single_field() -> None:
    """Verify trailing-comma logic on compiling record with a single attribute."""
    init_func = _compile_init("SingleFieldRecord", ["id"], {"id": 1})
    assert init_func is not None

    class DummyInstance:
        pass

    instance = DummyInstance()
    init_func(instance, id=101)
    assert instance.id == 101
    assert hasattr(instance, '__digest__')


def test_record_compile_init_multiple_fields() -> None:
    """Verify constructor formatting with multiple parameters."""
    init_func = _compile_init("MultiFieldRecord", ["id", "username"], {})
    assert init_func is not None

    class DummyInstance:
        pass

    instance = DummyInstance()
    init_func(instance, id=42, username="dev")
    assert instance.id == 42
    assert instance.username == "dev"
    assert hasattr(instance, '__digest__')


def test_record_namespace_guard_mcdc() -> None:
    """Test metadata bypass rules and unannotated field boundaries."""
    annotations = {"value": int}
    namespace = {
        "__slots__": (),
        "__qualname__": "GuardTest",
        "__module__": "test_module",
        "abc_callable": lambda x: x,
    }
    _namespace_guard("GuardTest", annotations, namespace)

    bad_namespace = {
        "unannotated_var": "fails_guard"
    }
    with pytest.raises(TypeError, match="Invalid unannotated variable"):
        _namespace_guard("GuardTest", annotations, bad_namespace)


def test_prepare_record_fields_mcdc() -> None:
    """Verify attribute identifier validations, skipping, and defaults freezing."""
    with pytest.raises(TypeError, match="Invalid attribute name"):
        _prepare_record_fields("BadRecord", {"123_invalid": int}, {})

    from typing import ClassVar
    annotations = {
        "id": int,
        "name": str,
        "ClassVarAttr": ClassVar[str],
        "__slots__": tuple,
        "__digest__": bytes,
    }
    namespace = {
        "name": "default_user_name",
        "__slots__": (),
    }
    fields, defaults = _prepare_record_fields("UserRecord", annotations, namespace)
    assert fields == ["id", "name"]
    assert defaults == {"name": "default_user_name"}


def test_check_mro_fields_ordering() -> None:
    """Verify base fields accurately precede subclass fields during MRO merge."""
    bases = (ParentRecord,)
    fields = ["child_field"]
    annotations = {"child_field": str}

    merged_fields, merged_annotations = _check_mro_fields(
        RecordType, bases, fields, annotations
    )
    assert merged_fields == ["parent_id", "parent_name", "child_field"]
    assert "parent_id" in merged_annotations
    assert "child_field" in merged_annotations


def test_record_type_new_sealing() -> None:
    """Verify compiled records are deeply frozen and locked."""
    instance = ProtectedRecord(id=101)
    assert instance.id == 101

    with pytest.raises(ImmutableError):
        instance.id = 202

    with pytest.raises(ImmutableError):
        del instance.id
