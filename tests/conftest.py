"""Taph fixtures"""
import pytest
from taph.core import Immutable, Namespace, ImmutableType

@pytest.fixture
def point_class():
    """Return fresh, valid Immutable subclass with __init__ logic.

    Used for testing instance behavior (setattr/delattr on instances).

    """
    class Point(Immutable):
        __slots__ = ('x', 'y')

        def __init__(self, x: int, y: int):
            # Correct way to initialize immutable objects
            super().__setattr__('x', x)
            super().__setattr__('y', y)

    return Point


@pytest.fixture
def config_class():
    """Return fresh Namespace subclass with attributes.

    Used for testing Namespace behavior.
    """
    class Config(Namespace):
        __slots__ = ()
        HOST = "localhost"
        PORT = 8080

    return Config


@pytest.fixture
def mutable_class():
    """Return a standard mutable Python class.

    Used to verify freeze() behavior on unknown objects.
    """
    class Dummy:
        def __init__(self, value):
            self.value = value
    return Dummy


@pytest.fixture
def class_factory():
    """Return a factory function to create dynamic classes at runtime.

    Used for testing metaclass validation.
    """
    def _create_class(name, bases, attrs):
        # manually invoke the metaclass to simulate class creation
        return ImmutableType(name, bases, attrs)
    return _create_class
