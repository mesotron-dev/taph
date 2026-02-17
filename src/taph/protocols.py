"""The Taph library’s immutability protocols.

The taph.protocols module defines the abstract protocols that allow Taph's
freezing mechanism to interact with custom objects in a decoupled,
standards-compliant way. It provides the `Freezable` protocol for objects to
advertise their own immutable conversion logic.

"""
from typing import Protocol, runtime_checkable

@runtime_checkable
class Freezable(Protocol):
    """A protocol for objects that can be explicitly frozen.

    The Freezable protocol allows custom classes to define their own logic for
    creating an immutable "frozen" version of themselves. When an object
    implementing this protocol is passed to `taph.freeze`, the `__freeze__`
    method is called, and its return value is used as the immutable
    representation.

    This protocol is particularly useful for complex objects that may contain
    transient state (e.g., database connections, open files) that should be
    excluded from the frozen snapshot. When designing the immutable
    representation, use this quick checklist to identify transient or mutable
    internals that typically need to be skipped:

        - Open file streams or sockets

        - Cached properties or lazily evaluated attributes

        - In-memory buffers, queues, or ongoing transactions

    Considering these elements helps prevent subtle bugs and ensures that only
    essential, truly immutable data is preserved.

    The `@runtime_checkable` decorator enables the use of `isinstance()`
    checks, allowing `taph.freeze` to efficiently detect if an object supports
    this protocol without relying on inheritance.

    Example:
        Custom config object, minus live connections.

        A class implementing the Freezable protocol to control its immutable
        representation::

            class DatabaseConfig:
                def __init__(self, host: str, port: int):
                    self.host = host
                    self.port = port
                    self._connection = None  # Internal, mutable state

                def __freeze__(self) -> 'DatabaseConfig':
                    # Returns a new, clean instance without the connection.
                    return DatabaseConfig(self.host, self.port)

            config = DatabaseConfig("localhost", 5432)
            frozen_config = taph.freeze(config)

    """
    def __freeze__(self) -> object:
        """Return an immutable representation of the object.

        This method should return a new object that is guaranteed to be
        immutable. It is responsible for handling all internal state to produce
        a hashable, deeply immutable snapshot.

        Returns:
            An immutable version of the object.

        """
        ...


class Freeze(Protocol):
    """A protocol representing a generic freezing function.

    The Freeze protocol defines the abstract type signature for a callable that
    conforms to the behavior of `taph.tools.freeze`. It is primarily intended
    for use in type hints to specify that a function or method accepts
    `taph.tools.freeze` or a compatible function as an argument.

    Freeze allows for dependency injection and enables functions to be tested
    with mock freezing implementations.

    Example:
        Using `Freeze` to type-hint a function that processes and freezes data:

            from taph.tools import freeze

            def process_and_store(data: dict, freezer: Freeze) -> None:
                immutable_data = freezer(data)
                # ... store immutable_data in a cache or database ...

            # Call the function with the concrete implementation
            process_and_store({"key": [1, 2]}, freezer=freeze)
    """

    def __call__(self, obj: object) -> object:
        """Freeze a mutable object, returning an immutable version.

        Args:
            obj: The object to freeze.

        Returns:
            The immutable representation of the object.
        """
        ...
