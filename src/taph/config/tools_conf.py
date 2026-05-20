"""Taph tools configuration module."""

from typing import Literal, NamedTuple

__all__: tuple[str, ...] = (
    'code',
    'default',
    'freeze_error_messages',
    'hash_error_messages',
    'mark',
    'thaw_error_messages',
)


class Default(NamedTuple):
    """Defaults for the hash_tools module."""

    DIGEST_SIZE: int = 16


default: Default = Default()


class Encoding(NamedTuple):
    """The accepted encodings."""

    BOOL: bytes = b'?'
    BIG: Literal['big'] = 'big'
    LITTLE: Literal['little'] = 'little'
    NONE: bytes = b'<NoneType>'
    UNSIGNED_BYTE: bytes = b'B'
    UNSIGNED_DBL_LONG: bytes = b'<Q'
    UTF8: str = 'utf-8'


code: Encoding = Encoding()


class ReferenceMark(NamedTuple):
    """Reference Markers for hash_tools._feed_digest."""

    DIGEST: int = 1
    INT: int = 2
    FLOAT: int = 3
    INF: int = 4
    NEG_INF: int = 5
    NAN: int = 6
    COMPLEX: int = 7
    DECIMAL: int = 8
    FRACTION: int = 9
    STRING: int = 10
    BOOL: int = 11
    BYTES: int = 12
    NONE: int = 13
    TUPLE: int = 14
    SET: int = 15
    MAP: int = 16
    END: int = 17
    UNKNOWN: int = 18


mark: ReferenceMark = ReferenceMark()


class CoreErrorMessage(NamedTuple):
    """Core error messages."""

    OBJECT_TYPE: str = 'Object of type'


core_error_message: CoreErrorMessage = CoreErrorMessage()


class FreezeErrorMessage(NamedTuple):
    """Error messages for the freeze_tools module."""

    def freeze(self, name: object) -> str:
        """#todo."""
        return f'{core_error_message.OBJECT_TYPE} {name} cannot be frozen.'


freeze_error_messages = FreezeErrorMessage()


class HashErrorMessage(NamedTuple):
    """Error messages for the hash_tools module."""

    NOT_HASHABLE: str = 'is not hashable.'

    def type_error(self, name: str) -> str:
        """Unhashable object type error message."""
        return f'{core_error_message.OBJECT_TYPE} {name} {self.NOT_HASHABLE}'


hash_error_messages = HashErrorMessage()


class ThawErrorMessage(NamedTuple):
    """Error messages for the thaw_tools module."""

    NOT_THAWABLE: str = 'cannot be thawed.'

    def type_error(self, name: str) -> str:
        """Unthawable object type error message."""
        return f'{core_error_message.OBJECT_TYPE} {name} {self.NOT_THAWABLE}'


thaw_error_messages = ThawErrorMessage()
