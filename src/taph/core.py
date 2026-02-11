"""Core immutable class constructs for the Taph library.

This module provides the foundational metaclasses and mixins required to create
deeply immutable objects and namespaces. It enforces strict memory optimization
via `__slots__` and ensures recursive immutability for attributes

"""
import types
from typing import Any, NoReturn

from taph.exceptions import ImmutableError

__all__ = ('Immutable', 'Namespace', 'freeze', 'is_immutable')


class ImmutableType(type):
    """Metaclass that enforces immutability on classes and their instances.

    This metaclass intercepts class creation to:
    1. Enforce the presence of `__slots__`.
    2. Recursively freeze all class-level attributes.
    3. Inject blocking `__setattr__` and `__delattr__` methods into the
       generated class to prevent instance modification.
    4. Block modification of the class object itself.

    """

    __slots__ = ()

    def __new__(
        mcs, name: str, bases: tuple[type, ...], attrs: dict[str, Any]
    ) -> type:
        """Create a new immutable class.

        Args:
            name: The name of the class being created.
            bases: The base classes of the class being created.
            attrs: The dictionary of class attributes.

        Returns:
            The newly created class.

        Raises:
            TypeError: If the class does not define `__slots__`.
            ImmutableError: If an attribute cannot be frozen.

        """
        if '__slots__' not in attrs:
            msg = (
                f"Class '{name}' must define '{'__slots__'}'"
                 " to inherit from an Immutable type."
            )
            raise TypeError(msg)

        frozen_attrs = {}
        for k, v in attrs.items():
            if k.startswith('__') and k.endswith('__'):
                frozen_attrs[k] = v
            else:
                frozen_attrs[k] = freeze(v)

        if name == 'Immutable':
            return super().__new__(mcs, name, bases, attrs)

        frozen_attrs['__setattr__'] = mcs._block_setattr
        frozen_attrs['__delattr__'] = mcs._block_delattr

        return super().__new__(mcs, name, bases, frozen_attrs)

    @staticmethod
    def _block_setattr(instance: object, name: str, value: object) -> NoReturn:
        """Block modification of instance attributes.

        Injected as `__setattr__` on immutable classes.

        Args:
            instance: The instance being modified.
            name: The name of the attribute.
            value: The value being assigned.

        Raises:
            ImmutableError: Always, to prevent modification.

        """
        msg = (
            f"Cannot modify attribute '{name}'. "
            f"'{type(instance).__name__}' is immutable."
        )
        raise ImmutableError(msg)

    @staticmethod
    def _block_delattr(instance: object, name: str) -> NoReturn:
        """Block deletion of instance attributes.

        Injected as `__setattr__` on immutable classes.

        Args:
            instance: The instance being modified.
            name: The name of the attribute.
            value: The value being assigned.

        Raises:
            ImmutableError: Always, to prevent modification.

        """
        msg = (
            f"Cannot delete attribute '{name}'. "
            f"'{type(instance).__name__}' is immutable."
        )
        raise ImmutableError(msg)

    def __setattr__(cls, name: str, value: object) -> None:
        """Prevent modification of class attributes.

        Args:
            name: The name of the class attribute.
            value: The value being assigned.

        Raises:
            ImmutableError: Always, to prevent modification of the class.

        """
        msg = (
            f"Cannot modify attribute of an immutable class '{cls.__name__}'."
        )
        raise ImmutableError(msg)

    def __delattr__(cls, name: str) -> None:
        """Prevent deletion of class attributes.

        Args:
            name: The name of the class attribute.

        Raises:
            ImmutableError: Always, to prevent deletion from the class.

        """
        msg = (
            f"Cannot delete attribute of an immutable class '{cls.__name__}'."
        )
        raise ImmutableError(msg)


def is_immutable(value: object) -> bool:
    """Check if an object is a Taph immutable type or instance.

    This verifies if the object is either an instance of a class created by
    `ImmutableType`, or the class itself.

    Args:
        value: The object to check.

    Returns:
        True if the object is managed by Taph, False otherwise.

    """
    if isinstance(value, ImmutableType):
        return True

    if hasattr(value, '__class__') and isinstance(
        value.__class__, ImmutableType
    ):
        return True

    return False


def freeze(value: object) -> object:
    """Recursively transform mutable structures into immutable counterparts.

    Traverses the object graph and converts standard mutable containers into
    hashable, immutable equivalents:
    * `list` -> `tuple`
    * `set` -> `frozenset`
    * `dict` -> `types.MappingProxyType` (recursively frozen values)

    Args:
        value: The object to freeze.

    Returns:
        The immutable version of the input object.

    Raises:
        ImmutableError: If `value` is a custom object that does not inherit
            from `Immutable` or `Namespace`.

    """
    if is_immutable(value) or isinstance(
        value,
        (str, int, float, bool, type(None), bytes, complex, tuple, frozenset),
    ):
        return value

    if isinstance(value, list):
        return tuple(freeze(item) for item in value)
    if isinstance(value, set):
        return frozenset(freeze(item) for item in value)
    if isinstance(value, dict):
        return types.MappingProxyType({k: freeze(v) for k, v in value.items()})

    msg = (
        f"Object of type '{type(value).__name__}' may be mutable. "
        "All custom objects are required to inherit from an Immutable "
        "or Namespace type."
    )
    raise ImmutableError(msg)


class Immutable(metaclass=ImmutableType):
    """Base class for creating immutable value objects.

    Subclasses define `__slots__` to ensure memory efficiency and prevent the
    creation of `__dict__`.

    Example:
        ```python
        class Point(Immutable):
            __slots__ = ('x', 'y')

            def __init__(self, x, y):
                super().__setattr__('x', x)
                super().__setattr__('y', y)
        ```

    """

    __slots__ = ()

    def __setattr__(self, name: str, value: object) -> None:
        object.__setattr__(self, name, value)


class Namespace(metaclass=ImmutableType):
    """Base class for static, non-instantiable constant containers.

    Attributes defined on a Namespace are frozen at class creation time.
    Attempting to instantiate a Namespace will raise an error.

    Example:
        ```python
        class Config(Namespace):
            __slots__ = ()
            TIMEOUT = 30
            HOSTS = ["localhost", "127.0.0.1"]  # Becomes a tuple
        ```

    """

    __slots__ = ()

    def __new__(cls, *args: object, **kwargs: object) -> NoReturn:
        """Prevent instantiation of the Namespace."""
        msg = f"Namespace '{cls.__name__}' cannot be instantiated."
        raise ImmutableError(msg)
