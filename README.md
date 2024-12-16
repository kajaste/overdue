# Overdue
Conveniently stop Python code from running when it is taking too long on Python 3.10+.
Ships with type annotations and depends at runtime on nothing but Python itself.

For older Pythons, consider [stopit](https://github.com/glenfant/stopit).

## Installation
`$ pip install overdue` or whatever is the equivalent in your favorite package manager.

## Using a context manager
Without exceptions:
```python
from overdue import timeout_set_to

with timeout_set_to(0.25) as timeout:
    # Slow code
if timeout.triggered:
    # Handle timeout
```
With an exception:
```python
from overdue import timeout_set_to, TaskAbortedError

try:
    with timeout_set_to(0.25, raise_exception=True):
        # Slow code
except TaskAbortedError:
    # Handle timeout
```

## Using a decorator
With an exception:
```python
from overdue import timecapped_to, TaskAbortedError

@timecapped_to(0.25)
def my_slow_function() -> None:
    # Slow code

try:
    my_slow_function()
except TaskAbortedError:
    # Handle timeout
```

Without exceptions:
```python
from overdue import in_time_or_none

@in_time_or_none(0.25)
def my_slow_function() -> int:
    # Slow code
    return 7

if (result := my_slow_function()) is None:
    # Handle timeout
```
