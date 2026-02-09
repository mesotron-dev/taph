"""Custom exception types for the Taph library."""

__all__ = ('TaphError', 'ImmutableError')


class TaphError(Exception):
    """Raise the base exception for all Taph-related errors."""



class ImmutableError(TaphError, TypeError):
    """Raise when an attempt is made to modify an immutable object or class.

    Inherits from TypeError to maintain semantic compatibility with standard
    Python expectations for immutability violations (e.g., modifying a tuple).
    """

