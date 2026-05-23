# Taph: Zero-Overhead Immutability for Python

[![PyPI - Version](https://img.shields.io/pypi/v/taph.svg?style=flat-square)](https://pypi.org/project/taph/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg?style=flat-square)](LICENSE)
[![Tests](https://img.shields.io/github/actions/workflow/status/mesotron-dev/taph/full-coverage.yml?style=flat-square)](https://github.com/mesotron-dev/taph/actions)
[![Coverage](https://img.shields.io/badge/Coverage-100%25-brightgreen.svg?style=flat-square)](https://github.com/mesotron-dev/taph/actions)

**Taph** makes it easy to create **deeply immutable** objects in Python with zero runtime overhead and strong content-based hashing. Taph creates objects that are guaranteed to be unchangeable, enabling predictable, pure functional programming patterns in Python.

Taph's core value proposition: **Fast & Reliable Immutability.**

---

## Core Features

-   **Zero-Overhead:** Achieves immutability using Python's Method Resolution Order (MRO) and metaclass injection.
-   **Memory Efficiency:** Enforces `__slots__` usage, eliminating the memory footprint of `__dict__` for every instance.
-   **Deep Immutability:** Recursively transforms nested mutable structures (like `list`, `dict`) into immutable counterparts (`tuple`, `MappingProxyType`) during class creation.
-   **Zero Dependencies:** A single-file core module built using the Python Standard Library.
- **Cryptographic Stability**: Every object gets a deterministic BLAKE2b content digest.
- **Simple & Fast**: Clean APIs with excellent ergonomics.    

## Usage

Taph provides 3 classes of immutable objects: 

- `Record` for instantiable data objects
- `Manifest` for static constants.
- `FrozenDict` for immutable mappings.

### `FrozenDict` — Deeply Immutable Mapping

```python
from taph import FrozenDict, freeze

# Create a deeply frozen, sorted dictionary
data = FrozenDict({"beta": 2, "alpha": 1, "gamma": 3})

# Lookup is executed via O(log N) bisection on raw byte digests
assert data["alpha"] == 1

# Underlying arrays are perfectly aligned and sorted
assert list(data) == ["alpha", "beta", "gamma"]

# Safe merging operations return new frozen instances
updated_data = data | {"delta": 4}
assert isinstance(updated_data, FrozenDict)
```

### `Record` — Immutable Data Objects

```python
from taph import Record

class User(Record):
    __slots__ = ('user_id', 'username', 'email')
    
    user_id: int
    username: str
    email: str

user = User(user_id=101, username="arch", email="arch@taph.io")

print(user.username)
print(user.hexdigest)      # stable content hash
```

Supports `keys()`, `items()`, `values()`, `get()`, and `__replace__()` for safe updates.

### `Manifest` — Static Constants

```python
from taph import Manifest

class Config(Manifest):
    __slots__ = ()
    VERSION = "2.1.0"
    DEBUG = False
    TIMEOUT = 30
```

Non-instantiable. Perfect for configuration and constants.

### `FrozenDict` — Immutable Mapping

```python
from taph import FrozenDict, freeze

data = freeze({"a": [1, 2], "b": {"nested": True}})
assert isinstance(data["b"], FrozenDict)
```

---

## Tools

```python
from taph import freeze, thaw

# Deep freeze any structure
immutable = freeze({"items": [1, 2, 3]})

# Mutable copy
mutable = thaw(immutable)
```

---

## Functional Style

Taph makes functional programming in Python safer and more predictable.

### 1. Pure Functions with `Record`

```python
from taph import Record

class User(Record):
    __slots__ = ('user_id', 'name', 'is_active')
    
    user_id: int
    name: str
    is_active: bool = True

# Pure function - no side effects
def deactivate_user(user: User) -> User:
    # Returns a new Record with updated value (copy-on-write)
    return user.__replace__(is_active=False)

# Usage
user1 = User(user_id=101, name='Alice', is_active=True)
user2 = deactivate_user(user1)

print(user1.is_active)   # → True
print(user2.is_active)   # → False
assert user1 is not user2
```

### 2. Stateless Systems with `Manifest`

```python
from taph import Manifest

class Config(Manifest):
    __slots__ = ()
    TIMEOUT_SECONDS = 30
    SUPPORTED_METHODS = ('GET', 'POST')
    API_VERSION = 'v2.1'

def is_request_valid(request_duration: int, method: str) -> bool:
    # Totally predictable - depends only on inputs + immutable constants
    if method not in Config.SUPPORTED_METHODS:
        return False
    return request_duration < Config.TIMEOUT_SECONDS

# Attempting to mutate constants will raise an error
# Config.TIMEOUT_SECONDS = 1   # Raises ImmutableError
```

---

## Installation

```bash
pip install taph
```

## License

Taph is licensed under the **Apache License 2.0**. See the [LICENSE](LICENSE) file for details.
