"""Tests for the core module ensuring exhaustive MC/DC coverage."""

from __future__ import annotations

import pytest
import types
from taph.core import (
    Immutable,
    ImmutableType,
    Namespace,
    freeze,
    is_immutable
)
from taph.exceptions import ImmutableError


class TestImmutableType:
    """Test metaclass logic."""

    def test_metaclass_enforces_slots(self, class_factory):
        """Verify TypeError is raised if __slots__ is missing."""
        with pytest.raises(TypeError) as check:
            Fail = class_factory('ImmutableType', (object,), {})
            assert "Class 'Fail' must define '__slots__'" in str(check.value)

    def test_immutable_base_logic(self):
        """Verify the 'Immutable' base class itself is treated specially."""
        assert Immutable.__name__ == 'Immutable'

    def test_metaclass_block_methods(self):
        """Check metaclass blocking methds for new class dict."""
        NewClass = ImmutableType('NewClass', (object,), {'__slots__': ()})

        assert '__setattr__' in NewClass.__dict__
        assert '__delattr__' in NewClass.__dict__
        assert NewClass.__setattr__.__name__ == '_block_setattr'
        assert NewClass.__delattr__.__name__ == '_block_delattr'

    def test_metaclass_skip_immutable_base(self):
        """Check the Immutable base class is not modified."""
        Base = ImmutableType('Immutable', (object,), {'__slots__': ()})

        assert '__setattr__' not in Base.__dict__
        assert '__delattr__' not in Base.__dict__

    def test_metaclass_base_logic(self, class_factory):
        """Verify the special case for the 'Immutable' base class name."""
        cls = class_factory('Immutable', (object,), {'__slots__': ()})
        assert cls.__name__ == 'Immutable'

    def test_class_blocks(self, class_factory):
        """Test block functions."""
        with pytest.raises(ImmutableError) as block_set:
            Block = class_factory(
                'ImmutableType', (object,), {'__slots__': ('fix')}
            )
            Block.fix = None

        assert (
            "Cannot modify attribute of an immutable class 'ImmutableType'"
        )in str(block_set.value)
        with pytest.raises(ImmutableError) as block_del:
            Block = class_factory(
                'Immutable', (object,), {'__slots__': ('delete')}
            )
            del Block.delete

        assert (
            "Cannot delete attribute of an immutable class 'Immutable'"
        ) in str(block_del.value)


class TestImmutable:
    """Test the usage of Immutable."""
    def test_init_works(self, point_class):
        p = point_class(1,2)
        assert p.x == 1
        assert p.y == 2

    def test_setattr_fail(self, point_class):
        p = point_class(4, 2)
        with pytest.raises(ImmutableError) as set_fail:
            p.x = 42
        assert "Cannot modify attribute 'x'" in str(set_fail.value)
        assert "'Point' is immutable" in str(set_fail.value)

    def test_delattr_fail(self, point_class):
        p = point_class(10, 20)
        with pytest.raises(ImmutableError, match="Cannot delete attribute "):
            del p.x

    def test_class_setattr_fail(self, point_class):
        with pytest.raises(ImmutableError, match="Cannot modify attribute"):
            point_class.z = 8

    def test_class_delattr_fail(self, point_class):
        with pytest.raises(ImmutableError, match="Cannot delete attribute"):
            del point_class.x

    def test_slots_enforcement_raises_error(self):
        """Verify class inheritance of Immutable declares __slots__.

        Raises a TypeError during class creation.
        """
        with pytest.raises(TypeError, match="must define '__slots__'"):
            class Invalid(Immutable):
                pass

    def test_slots_enforcement_true(self):
        """Condition: '__slots__' not in attrs -> False (Success)."""
        class Valid(Immutable):
            __slots__ = ()

        assert isinstance(Valid(), Valid)

    def test_slots_enforcement_false(self):
        """Condition: '__slots__' not in attrs -> True (Raise TypeError)."""
        with pytest.raises(TypeError, match="must define '__slots__'"):
            class Invalid(Immutable):
                pass

    def test_attribute_freezing_logic(self):
        """Verify if k.startswith('__') and k.endswith('__') logic

        Cases:
        1. False, False (Normal) -> Freeze
        2. True, False  (Starts with dunder) -> Freeze
        3. False, True  (Ends with dunder) -> Freeze
        4. True, True   (Full dunder) -> Skip
        """
        class LogicProbe(Immutable):
            __slots__ = ()
            # Case 1: Normal
            normal = [1]
            # Case 2: Starts with dunder only
            __hidden = [2]
            # Case 3: Ends with dunder only
            trailing__ = [3]
            # Case 4: Full Dunder (Mocking a system method)
            __dunder__ = [4]

        # 1. Normal -> Frozen
        assert isinstance(LogicProbe.normal, tuple)
        assert LogicProbe.normal == (1,)

        # 2. __hidden -> Frozen (mangled name check requires class prefix)
        # Note: Python mangles __hidden to _LogicProbe__hidden
        assert isinstance(LogicProbe._LogicProbe__hidden, tuple)
        assert LogicProbe._LogicProbe__hidden == (2,)

        # 3. trailing__ -> Frozen
        assert isinstance(LogicProbe.trailing__, tuple)
        assert LogicProbe.trailing__ == (3,)

        # 4. __dunder__ -> Skipped (Mutable List preserved)
        assert isinstance(LogicProbe.__dunder__, list)
        assert LogicProbe.__dunder__ == [4]

    def test_immutable_class(self):
        """True if value is an Immutable subclass (the class itself)."""
        class A(Immutable):
            __slots__ = ()
        assert is_immutable(A) is True

    def test_immutable_instance(self):
        """True if value is an instance of an Immutable subclass."""
        class A(Immutable):
            __slots__ = ()
        assert is_immutable(A()) is True

    def test_namespace_class(self):
        """True if value is a Namespace class."""
        class N(Namespace):
            __slots__ = ()
        assert is_immutable(N) is True

    def test_standard_types(self):
        """False for standard mutable/immutable types not managed by Taph."""
        assert is_immutable(1) is False
        assert is_immutable("s") is False
        assert is_immutable((1, 2)) is False
        assert is_immutable([]) is False


class TestNamespace:
    """Tests for the Namespace class."""
    def test_instantiation_fails(self, config_class):
        with pytest.raises(ImmutableError, match="cannot be instantiated"):
            _ = config_class()

    def test_strict_slots_on_namespace_subclass(self):
        """Even Namespace subclasses must define slots for deep immutability."""
        with pytest.raises(TypeError, match="must define '__slots__'"):
            class BadConfig(Namespace):
                HOST = "1.1.1.1"

    def test_class_attrs_frozen(self, config_class):
        assert config_class.HOST == "localhost"
        with pytest.raises(ImmutableError, match="Cannot modify attribute"):
            config_class.HOST = "127.0.0.1"


class TestFreeze:
    """Tests for the recursive freeze function with full MC/DC coverage."""
    def test_primitives_pass_through(self):
        """Condition: Not Immutable, but is Primitive Safe Type."""
        assert freeze(1) == 1
        assert freeze("a") == "a"
        assert freeze(1.1) == 1.1
        assert freeze(True) is True
        assert freeze(None) is None
        assert freeze(b"b") == b"b"
        assert freeze(1j) == 1j

    def test_tuples_and_frozensets_pass_through(self):
        """Condition: Not Immutable, but is Container Safe Type."""
        t = (1, 2)
        fs = frozenset([1, 2])
        assert freeze(t) is t
        assert freeze(fs) is fs

    def test_behavior_types_pass_through(self):
        """Condition: Not Immutable, but is Behavior Safe Type (NEW)."""
        def my_func(): pass
        assert freeze(my_func) is my_func
        sm = staticmethod(my_func)
        assert freeze(sm) is sm
        cm = classmethod(my_func)
        assert freeze(cm) is cm
        prop = property(lambda self: None)
        assert freeze(prop) is prop

    def test_immutable_object_pass_through(self, point_class):
        """Condition: Is Immutable (Condition A1: True)."""
        i = point_class(1, 2)
        assert freeze(i) is i

    def test_list_to_tuple(self):
        """Decision B: isinstance(list) -> True."""
        assert freeze([1, 2]) == (1, 2)
        assert freeze([[1], 2]) == ((1,), 2)

    def test_set_to_frozenset(self):
        """Decision C: isinstance(set) -> True."""
        res = freeze({1, 2})
        assert isinstance(res, frozenset)
        assert res == frozenset({1, 2})

    def test_dict_to_mappingproxy(self):
        """Decision D: isinstance(dict) -> True."""
        d = {'a': 1, 'b': [2]}
        res = freeze(d)
        assert isinstance(res, types.MappingProxyType)
        assert res['a'] == 1
        assert res['b'] == (2,)  # Recursive verify

    def test_unknown_mutable_raises(self, mutable_class):
        """Decision E: Else -> Raise (Standard Object)."""
        with pytest.raises(ImmutableError, match="Object of type 'Dummy' may be mutable"):
            freeze(mutable_class(1))

    def test_custom_callable_fails(self):
        """Decision E: Else -> Raise (Custom Callable).

        Crucial Negative Test: Ensures that while we allow 'functions',
        we do NOT blindly allow any object just because it has __call__.
        A mutable class with __call__ is still unsafe.
        """
        class UnsafeCallable:
            def __call__(self):
                pass

        c = UnsafeCallable()

        with pytest.raises(ImmutableError, match="Object of type 'UnsafeCallable' may be mutable"):
            freeze(c)

    def test_unknown_mutable_in_container_raises(self, mutable_class):
        """Recursion Failure Check."""
        with pytest.raises(ImmutableError):
            freeze([mutable_class(1)])
