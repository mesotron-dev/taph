"""Taph Metaclass module.

#TODO

"""

import abc

from taph.config.meta_conf import taph_error_conf as msg
from taph.config.meta_conf import taph_type_conf as taph
from taph.exceptions import ImmutableError

__all__ = ('TaphType',)


class TaphType(abc.ABCMeta):
    """Abstract base metaclass for all Taph types.

    #TODO

    """

    __slots__ = ()

    def __new__(
        cls, name: str, bases: tuple[type, ...], namespace: dict[str, object]
    ) -> type:
        """Create a new immutable class.

        Args:
            name: The name of the class being created.
            bases: The base classes of the class being created.
            namespace: The dictionary of class attributes.

        Returns:
            The newly created class.

        Raises:
            TypeError: If the class does not define `__slots__`.
            ImmutableError: If an attribute cannot be frozen.

        """
        # py3.12+ generic syntax leaks non-string keys
        namespace = {k: v for k, v in namespace.items() if isinstance(k, str)}

        if taph.slots not in namespace:
            raise TypeError(msg.no_slots_message(name))

        return super().__new__(cls, name, bases, namespace)

    @staticmethod
    def _block_setattr(instance: object, name: str, value: object) -> None:  # noqa: ARG004
        """Block modification of instance namespace.

        Injected as `__setattr__` on immutable classes.

        Args:
            instance: The instance being modified.
            name: The name of the attribute.
            value: The value being assigned.

        Raises:
            ImmutableError: Always, to prevent modification.

        """
        raise ImmutableError(msg.instance_setattr)

    @staticmethod
    def _block_delattr(instance: object, name: str) -> None:  # noqa: ARG004
        """Block deletion of instance namespace.

        Injected as `__setattr__` on immutable classes.

        Args:
            instance: The instance being modified.
            name: The name of the attribute.
            value: The value being assigned.

        Raises:
            ImmutableError: Always, to prevent modification.

        """
        raise ImmutableError(msg.instance_delattr)

    def __setattr__(cls, name: str, value: object) -> None:
        """Prevent modification of class namespace.

        Args:
            name: The name of the class attribute.
            value: The value being assigned.

        Raises:
            ImmutableError: Always, to prevent modification of the class.

        """
        if (
            name in taph.class_internals()
            or name.startswith((taph.abc, taph.abc_methods))
        ):
            type.__setattr__(cls, name, value)
            return
        raise ImmutableError(msg.class_setattr)

    def __delattr__(cls, name: str) -> None:
        """Prevent deletion of class namespace.

        Args:
            name: The name of the class attribute.

        Raises:
            ImmutableError: Always, to prevent deletion from the class.

        #f"Cannot delete attribute of an immutable class '{cls.__name__}'."

        """
        if (
            name in taph.class_internals()
            or name.startswith((taph.abc, taph.abc_methods))
        ):
            type.__delattr__(cls, name)
            return
        raise ImmutableError(msg.class_delattr)
