"""Exceptions for the Taph library."""

__all__ = (
    'FrozenDictError',
    'ImmutableError',
    'ManifestError',
    'RecordError',
    'TaphError',
    'ThawError',
)


class TaphError(Exception):
    """Base exception for all errors raised by the Taph package.

    Catch this to handle any Taph-specific failure.

    """


class ImmutableError(TaphError, AttributeError, TypeError):
    """Raised when an attempt is made to mutate a frozen Taph object.

    Inherits from AttributeError and TypeError so standard library
    functions and third-party tools that expect standard Python
    mutation failures can catch it gracefully.

    """


class RecordError(TaphError):
    """Raised for structural or validation errors in Records.

    Examples: Missing required slots, type validation failures.

    """


class ManifestError(TaphError):
    """Raised for misuse of Manifests.

    Examples: Attempting to instantiate a Manifest, defining illegal attributes.

    """


class FrozenDictError(TaphError, KeyError):
    """Raised for specific mapping errors within FrozenDicts.

    Inherits from KeyError to maintain standard Mapping behavior.

    """


class ThawError(TaphError, TypeError):
    """Raised for objects that are not recognized as thawable.

    Inherits from TypeError to indicate standard type error behavior.

    """
