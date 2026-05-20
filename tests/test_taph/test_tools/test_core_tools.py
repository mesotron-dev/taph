"""Test taph.tools.core_tools module."""
import datetime
import decimal
import fractions
import pathlib
import re
import uuid
from collections import deque
from subprocess import CompletedProcess
import typing
from collections.abc import Iterator, MutableMapping, MutableSequence, MutableSet
from typing import Any, ClassVar
import pytest
from taph.tools.core_tools import (
    is_atom,
    is_classvar,
    is_immutable,
    is_mutable,
    namespace_skip,
    snapshot,
)
from taph.frozen_dict import FrozenDict
from taph.manifest import Manifest
from taph.protocols import Immutable


class DummyImmutable:
    """A minimal implementation of the Taph Immutable protocol."""
    def __init__(self, digest: bytes) -> None:
        self.__digest__ = digest

    @property
    def fingerprint(self) -> str:
        return "mock_fingerprint"

    @property
    def hexdigest(self) -> str:
        return "mock_hexdigest"


class DummyMutableMapping(MutableMapping[Any, Any]):
    """A standard mutable mapping mock for ABC registration testing."""
    def __init__(self) -> None:
        self._data: dict[Any, Any] = {}
    def __getitem__(self, key: Any) -> Any:
        return self._data[key]
    def __setitem__(self, key: Any, value: Any) -> None:
        self._data[key] = value
    def __delitem__(self, key: Any) -> None:
        del self._data[key]
    def __iter__(self) -> Iterator[Any]:
        return iter(self._data)
    def __len__(self) -> int:
        return len(self._data)

class DummyMutableSequence(MutableSequence[Any]):
    """A standard mutable sequence mock for ABC registration testing."""
    def __init__(self) -> None:
        self._data: list[Any] = []
    def __getitem__(self, index: Any) -> Any:
        return self._data[index]
    def __setitem__(self, index: Any, value: Any) -> None:
        self._data[index] = value
    def __delitem__(self, index: Any) -> None:
        del self._data[index]
    def __len__(self) -> int:
        return len(self._data)
    def insert(self, index: int, value: Any) -> None:
        self._data.insert(index, value)

class DummyMutableSet(MutableSet[Any]):
    """A standard mutable set mock for ABC registration testing."""
    def __init__(self) -> None:
        self._data: set[Any] = set()
    def __contains__(self, x: object) -> bool:
        return x in self._data
    def __iter__(self) -> Iterator[Any]:
        return iter(self._data)
    def __len__(self) -> int:
        return len(self._data)
    def add(self, value: Any) -> None:
        self._data.add(value)
    def discard(self, value: Any) -> None:
        self._data.discard(value)

def test_is_atom() -> None:
    """Verify built-in atomic immutable types are correctly classified."""
    class DummyClass:
        def method(self) -> None:
            pass

        @property
        def prop(self) -> None:
            pass

    dummy_instance = DummyClass()
    match_object = re.match(r"\d+", "123")
    assert match_object is not None

    test_instances: list[object] = [
        # --- Basic Categories ---
        "test_string",
        True,
        b"test_bytes",
        None,

        # --- Number Categories ---
        42,
        3.14159,
        1 + 2j,
        decimal.Decimal("3.14"),
        fractions.Fraction(1, 2),

        # --- Temporal Categories ---
        datetime.datetime(2026, 1, 1, 12, 0, 0),
        datetime.date(2026, 1, 1),
        datetime.time(12, 0, 0),
        datetime.timedelta(days=1),

        # --- System & Path Primitives ---
        uuid.UUID("12345678-1234-5678-1234-567812345678"),
        pathlib.PurePath("foo/bar"),
        pathlib.Path("foo/bar"),  # Validates subclass/inheritance compatibility
        re.compile(r"\d+"),
        match_object,
        CompletedProcess(args=["ls"], returncode=0),

        # --- Callables / Descriptors ---
        lambda: None,                  # FunctionType
        dummy_instance.method,         # MethodType
        staticmethod(lambda: None),
        classmethod(lambda cls: None),
        DummyClass.prop,               # property descriptor
    ]

    # 1. Assert exhaustive positive cases
    for inst in test_instances:
        assert is_atom(inst) is True, (
            f"Type failed identification in is_atom: {type(inst).__name__}"
        )

    # 2. Assert negative cases (Verify boundaries do not leak to mutable structures)
    assert is_atom([1, 2, 3]) is False
    assert is_atom({"key": "val"}) is False
    assert is_atom({1, 2}) is False
    assert is_atom(DummyClass) is False  # Type objects are not atoms

def test_is_classvar() -> None:
    """Test is_classvar core tool."""
    assert is_classvar(ClassVar) is True
    assert is_classvar(ClassVar[int]) is True
    assert is_classvar(int) is False

def test_is_immutable() -> None:
    """Verify instance-level, class-level, and raw fallback immutability."""
    # Path A: Atomic evaluation
    assert is_immutable(42) is True
    assert is_immutable("string_constant") is True

    # Path B: Instance-level Protocol Match
    assert is_immutable(DummyImmutable(b"cryptographic_digest_bytes")) is True

    # Path C: Class-level Metaclass Protocol Match (Manifest Subclasses)
    class SystemConstants(Manifest):
        VERSION = "1.0.0"
        PORT = 8080
    assert is_immutable(SystemConstants) is True

    # Path D: Fallback class check (Uninitialized slots verification)
    uninit_fd = FrozenDict.__new__(FrozenDict)
    assert is_immutable(uninit_fd) is True

    # Path E: Fallthrough evaluation
    class StandardMutableClass:
        pass

    assert is_immutable(StandardMutableClass()) is False
    assert is_immutable([1, 2, 3]) is False


def test_is_mutable() -> None:
    """Verify full coverage for is_mutable."""
    # Built-in collections (Branch 1)
    assert is_mutable([]) is True
    assert is_mutable({}) is True
    assert is_mutable(set()) is True

    # Abstract collections & variants (Branch 2)
    assert is_mutable(DummyMutableMapping()) is True
    assert is_mutable(DummyMutableSequence()) is True
    assert is_mutable(DummyMutableSet()) is True
    assert is_mutable(deque([1, 2])) is True
    assert is_mutable(bytearray(b"mutable")) is True

    # Fallthrough (False)
    assert is_mutable(42) is False
    assert is_mutable("string") is False


def test_namespace_skip() -> None:
    """Test coveage for namespace_skip tool."""
    class CustomCallableClass:
        def __call__(self) -> None:
            pass

    # Non-string key
    with pytest.raises(AttributeError):
        namespace_skip(42, 123)  # type: ignore[arg-type]

    # Dunder checks (MC/DC)
    assert namespace_skip(42, "__init__") is True
    assert namespace_skip(42, "__private") is False
    assert namespace_skip(42, "public__") is False
    assert namespace_skip(42, "_abc_impl") is True

    # Typing constraints
    assert namespace_skip(ClassVar, "my_var") is True
    assert namespace_skip(lambda x: x, "my_func") is True
    assert namespace_skip(CustomCallableClass(), "callable_field") is True
    assert namespace_skip(42, "my_var") is False

def test_snapshot() -> None:
    """Verify snapshot processes public state and guarantees recursive freezing.

    This ensures that when mutable objects (like lists or dicts) are found
    on the target object's state, they are returned as deeply immutable
    structures inside the snapshot's FrozenDict.
    """
    class TargetClass:
        __slots__ = ("public_val", "mutable_list", "mutable_dict")
        def __init__(self) -> None:
            self.public_val = 100
            self.mutable_list = [10, 20, 30]
            self.mutable_dict = {"a": "A"}

    snap = snapshot(TargetClass())

    assert isinstance(snap, FrozenDict)
    assert snap["public_val"] == 100
    assert isinstance(snap["mutable_list"], tuple)
    assert snap["mutable_list"] == (10, 20, 30)

    assert isinstance(snap["mutable_dict"], FrozenDict)
    assert snap["mutable_dict"]["a"] == "A"
