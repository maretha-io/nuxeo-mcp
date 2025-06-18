# Type Hinting

This specification describes the type hinting standards for the Nuxeo MCP Server project.

## Overview

Type hints are annotations that specify the expected types of variables, function parameters, and return values. They help improve code readability, enable better IDE support, and allow for static type checking with tools like mypy.

## Requirements

1. All Python files in the project should include type hints
2. Type hints should follow PEP 484 and PEP 585 standards
3. Use the most specific types possible
4. Include return type annotations for all functions
5. Use type aliases for complex types
6. Use Optional for parameters that can be None
7. Use Union for parameters that can be multiple types
8. Use TypeVar for generic types

## Implementation

### Basic Types

Use Python's built-in types for simple annotations:

```python
def add(a: int, b: int) -> int:
    return a + b

def greet(name: str) -> str:
    return f"Hello, {name}!"

def is_valid(flag: bool) -> bool:
    return flag
```

### Container Types

Use the typing module for container types:

```python
from typing import List, Dict, Set, Tuple

def process_items(items: List[str]) -> None:
    for item in items:
        print(item)

def get_user_data() -> Dict[str, str]:
    return {"name": "John", "email": "john@example.com"}

def unique_numbers(numbers: List[int]) -> Set[int]:
    return set(numbers)

def get_coordinates() -> Tuple[float, float]:
    return (0.0, 0.0)
```

### Optional and Union Types

Use Optional for values that can be None, and Union for values that can be multiple types:

```python
from typing import Optional, Union

def find_user(user_id: Optional[int] = None) -> Optional[Dict[str, str]]:
    if user_id is None:
        return None
    return {"id": user_id, "name": "John"}

def process_value(value: Union[int, str]) -> str:
    return str(value)
```

### Type Aliases

Use type aliases for complex types:

```python
from typing import Dict, List, TypeAlias

UserData: TypeAlias = Dict[str, Union[str, int, bool]]
UserList: TypeAlias = List[UserData]

def get_users() -> UserList:
    return [{"name": "John", "age": 30, "active": True}]
```

### Callable Types

Use Callable for function types:

```python
from typing import Callable

def apply_function(func: Callable[[int], int], value: int) -> int:
    return func(value)
```

### Generic Types

Use TypeVar for generic types:

```python
from typing import TypeVar, List

T = TypeVar('T')

def first_element(items: List[T]) -> T:
    return items[0]
```

## File-Specific Type Hinting

### src/nuxeo_mcp/server.py

- Add type hints to the `NuxeoMCPServer` class
- Add type hints to all methods
- Use appropriate types for Nuxeo-specific objects

### src/nuxeo_mcp/__main__.py

- Add type hints to the main function
- Add type hints to any helper functions

### tests/*.py

- Add type hints to test functions
- Add type hints to fixtures
- Use appropriate types for pytest-specific objects

### seed_nuxeo.py

- Add type hints to all functions
- Use appropriate types for Nuxeo-specific objects

## Tools

The following tools can be used to check and enforce type hints:

- mypy: Static type checker
- pyright: Static type checker (used by Pylance in VS Code)
- flake8-annotations: Flake8 plugin to check for missing type annotations

## References

- [PEP 484 – Type Hints](https://peps.python.org/pep-0484/)
- [PEP 585 – Type Hinting Generics In Standard Collections](https://peps.python.org/pep-0585/)
- [Python typing module documentation](https://docs.python.org/3/library/typing.html)
