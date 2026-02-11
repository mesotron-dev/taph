# Taph: Zero-Overhead Immutability for Python

[![PyPI - Version](https://img.shields.io/pypi/v/taph.svg?style=flat-square)](https://pypi.org/project/taph/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg?style=flat-square)](LICENSE)
[![Tests](https://img.shields.io/github/actions/workflow/status/mesotron-dev/taph/full-coverage.yml?style=flat-square)](https://github.com/mesotron-dev/taph/actions)
[![Coverage](https://img.shields.io/badge/Coverage-100%25-brightgreen.svg?style=flat-square)](https://github.com/mesotron-dev/taph/actions)

Taph is a minimalist Python package for enforcing deep, zero-overhead immutability. Taph creates objects that are guaranteed to be unchangeable, enabling predictable, pure functional programming patterns in Python.

Taph's core value proposition: **Fast & Reliable Immutability.**

---

## Key Features

*   **Zero-Overhead:** Achieves immutability using Python's Method Resolution Order (MRO) and metaclass injection.
*   **Memory Efficiency:** Enforces `__slots__` usage, eliminating the memory footprint of `__dict__` for every instance.
*   **Deep Immutability:** Recursively transforms nested mutable structures (like `list`, `dict`) into immutable counterparts (`tuple`, `MappingProxyType`) during class creation.
*   **Zero Dependencies:** A single-file core module built using the Python Standard Library.

## Installation

```bash
pip install taph
```

## Usage

Taph provides two classes of immutable objects: 

- `Immutable` for instantiable data objects
- `Namespace` for static constants.

### 1. The `Immutable` Base Class

Use `Immutable` for creating value objects (data structures) whose state must never change after initialization.

**Contract:** Subclasses **must** define `__slots__`.

```python
from taph import Immutable, ImmutableError

class Point(Immutable):
    __slots__ = ('x', 'y')

    def __init__(self, x: int, y: int):
        # IMPORTANT: Use super().__setattr__ for initialization!
        super().__setattr__('x', x)
        super().__setattr__('y', y)

p = Point(10, 20)

# Fails (ImmutableError)
try:
    p.x = 30
except ImmutableError as e:
    print(f"Success: {e}")

# Fails (ImmutableError)
try:
    del p.y
except ImmutableError as e:
    print(f"Success: {e}")
```

### 2. The `Namespace` Static Container

Use `Namespace` for static configuration, constants, or utility groups. `Namespace` classes are **non-instantiable** and their class attributes are ** frozen** at creation time.

```python
from taph import Namespace, ImmutableError

class AppConfig(Namespace):
    __slots__ = () # Required, must be empty
    VERSION = "1.0.0"
    HOSTS = ["server-a", "server-b"] # Deeply frozen into a tuple

# Access attributes directly
print(f"Version: {AppConfig.VERSION}")
print(f"Hosts Type: {type(AppConfig.HOSTS)}") # <class 'tuple'>

# Fails (ImmutableError) - Cannot modify class attributes
try:
    AppConfig.TIMEOUT = 60
except ImmutableError as e:
    print(f"Success: {e}")

# Fails (ImmutableError) - Cannot instantiate
try:
    _ = AppConfig()
except ImmutableError as e:
    print(f"Success: {e}")
```

## Deep Freezing

Taph's `freeze` utility ensures deep immutability by recursively converting mutable collections during class construction:

| Mutable Type | Taph Equivalent |
| :--- | :--- |
| `list` | `tuple` |
| `set` | `frozenset` |
| `dict` | `types.MappingProxyType` |

Custom objects must inherit from `Immutable` or `Namespace`, or `freeze` will raise an `ImmutableError` at class definition time.

## Functional Style

Taph provides a solid foundation for functional programming in Python:

### 1.  **Pure Functions:** 

Pass Taph `Immutable` objects into functions with confidence that no side effects can occur.

```python
from taph import Immutable

class User(Immutable):
    __slots__ = ('user_id', 'name', 'is_active')

    def __init__(self, user_id: int, name: str, is_active: bool = True):
        super().__setattr__('user_id', user_id)
        super().__setattr__('name', name)
        super().__setattr__('is_active', is_active)

# PURE FUNCTION: No side effects. Takes a User, returns a NEW User.
def deactivate_user(user: User) -> User:
    # This is the "copy-on-write" pattern.
    return User(
        user_id=user.user_id,
        name=user.name,
        is_active=False
    )

# --- Caller ---
user1 = User(101, 'Alice')
user2 = deactivate_user(user1)

# The original object is completely untouched. The system is predictable.
print(user1.is_active)  # -> True
print(user2.is_active)  # -> False
assert user1 is not user2
```

### 2.  **Stateless Systems:** 

Use `Namespace` to provide verifiably safe, global constants that cannot be accidentally mutated by any function.

```python
from taph import Namespace

class Config(Namespace):
    __slots__ = ()
    TIMEOUT_SECONDS = 30
    SUPPORTED_METHODS = ('GET', 'POST')

def is_request_valid(request_duration: int, method: str) -> bool:
    # This function is predictable. Its behavior depends on its inputs and
    # constants that are guaranteed to be immutable.
    if method not in Config.SUPPORTED_METHODS:
        return False
    return request_duration < Config.TIMEOUT_SECONDS

# Config.TIMEOUT_SECONDS = 1 # Raises ImmutableError, protecting the function.
```

---

## License

Taph is licensed under the **Apache License 2.0**. See the [LICENSE](LICENSE) file for details.
