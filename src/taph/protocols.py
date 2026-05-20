"""The Taph library's immutability protocols.

This module defines abstract protocols that enable decoupled,
standards-compliant freezing and immutability behaviors in Taph. The key
protocols are:

- `Freezable`: for custom objects to control their own immutable conversion
- `Freeze`: type for the freezing function itself (for dependency injection)
- `Immutable`: marker for objects that cache a cryptographic content digest

These protocols support deep immutability in Records, Manifests, and frozen
mappings without tight coupling or inheritance requirements.

"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class Freezable(Protocol):
    """Protocol for objects that to provide an immutable ("frozen") version.

    The Freezable protocol allows custom classes to define their own logic for
    creating an immutable "frozen" version of themselves. When an object
    implementing this protocol is passed to `taph.freeze`, the `__freeze__()`
    method is called, and its return value is used as the immutable
    representation.

    This protocol is useful for complex objects that may contain transient, or
    mutable, state (e.g., database connections, open files) that should be
    excluded from the snapshots or hashing.

    When designing the immutable representation, use this quick checklist to
    identify transient or mutable internals that typically need to be skipped:

    - Exclude open file streams, sockets, connections, locks, or threads
    - Drop lazy, or cached, properties that can be recomputed
    - Remove in-memory buffers, queues, or transaction state
    - Ensure the returned object is deeply immutable & hashable

    Considering these elements helps prevent subtle bugs and ensures that only
    essential, truly immutable data is preserved.

    The `@runtime_checkable` decorator enables the use of `isinstance()`
    checks, allowing `taph.freeze` to efficiently detect if an object supports
    this protocol without relying on inheritance.

    The `@runtime_checkable` decorator allows `isinstance(obj, Freezable)`.

    Example:
        Custom config object, minus live connections.

        A class implementing the Freezable protocol to control its immutable
        representation:

        >>> class DatabaseConfig:
        ...     def __init__(self, host: str, port: int):
        ...         self.host = host
        ...         self.port = port
        ...         self._connection = None  # transient
        ...
        ...     def __freeze__(self) -> 'DatabaseConfig':
        ...         return DatabaseConfig(self.host, self.port)
        ...
        >>> config = DatabaseConfig("localhost", 5432)
        >>> frozen = taph.freeze(config)  # calls __freeze__ internally

    """

    def __freeze__(self) -> object:
        """Return a new deeply immutable representation of this object.

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


@runtime_checkable
class Immutable(Protocol):
    """Protocol for immutable objects with their own cryptographic digest.

    Objects conforming to this protocol guarantee:
    - Deep immutability (no attribute mutation after creation)
    - A constant, content-based BLAKE2b digest stored in `__digest__` (bytes)
    - String representations via `fingerprint` (base64url) and `hexdigest`

    The digest MUST:
    1. Be computed only from the object's semantically meaningful content
    2. Remain identical for equal objects (hash stability)
    3. Be constant for the object's lifetime

    This protocol is used by `Record` instances, `Manifest` classes, and
    `FrozenDict` instances in Taph to enable fast content-based hashing and
    equality.

    The `@runtime_checkable` decorator supports `isinstance(obj, Immutable)`.

    Example:
        >>> class Point(Immutable):
        ...     __digest__: bytes
        ...     x: float
        ...     y: float
        ...
        ...     @property
        ...     def fingerprint(self) -> str: ...
        ...
        >>> p = Point(x=1.0, y=2.0)  # __digest__ computed at init
        >>> isinstance(p, Immutable)  # True

    """

    __digest__: bytes

    @property
    def fingerprint(self) -> str:
        """Return the Base64 URL-safe string without padding.

        This is suitable for filenames, URLs, cache keys, etc.

        Returns:
            str: Compact, safe string representation of the content digest

        """
        ...

    @property
    def hexdigest(self) -> str:
        """Return the hexadecimal (lowercase) representation of the digest.

        Returns:
            str: 32 character hex string for BLAKE2b 16-byte digest.

        """
        ...


@runtime_checkable
class Thawable(Protocol):
    """Protocol for frozen objects that can return a mutable copy.

    The Thawable protocol allows custom immutable classes to define their own
    logic for creating a mutable ("thawed") version of themselves. When passed
    to `taph.thaw`, the `__thaw__()` method is called.

    Example:
        >>> class FrozenConfig(Thawable):
        ...     def __thaw__(self) -> dict[str, object]:
        ...         return {"host": self.host, "port": self.port}

    """

    def __thaw__(self) -> object:
        """Return a mutable representation of this object.

        Returns:
            A mutable version of the object.

        """
        ...


class Thaw(Protocol):
    """A protocol representing a generic thawing function.

    Defines the abstract type signature for a callable that conforms to the
    behavior of `taph.tools.thaw`. Useful for dependency injection.
    """

    def __call__(self, obj: object) -> object:
        """Thaw an immutable object, returning a mutable version.

        Args:
            obj: The object to thaw.

        Returns:
            The mutable representation of the object.

        """
        ...
