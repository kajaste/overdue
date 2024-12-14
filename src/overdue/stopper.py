import ctypes
import sys
import threading
from contextlib import contextmanager
from dataclasses import dataclass
from functools import wraps
from typing import Iterator, TypeVar, Callable, ParamSpec, Optional, Final

from overdue.action import OverdueAction

if sys.version_info >= (3, 12):
    from typing import override
else:
    OverrideCallableT = TypeVar('OverrideCallableT', bound=Callable)

    def override(x: OverrideCallableT) -> OverrideCallableT:
        return x


class TaskAbortedError(TimeoutError):
    def __init__(self) -> None:
        super().__init__("Task aborted due to timeout")


def get_current_thread_id() -> int:
    if (tid := threading.current_thread().ident) is not None:
        return tid
    raise RuntimeError("Cannot resolve current thread id")


def raise_in_thread(thread_id: int, exception: type[Exception]) -> None:
    # https://docs.python.org/3/c-api/init.html#c.PyThreadState_SetAsyncExc
    states_modified = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_ulong(thread_id), ctypes.py_object(exception)
    )
    if states_modified == 0:
        raise ValueError("Thread not running: %d" % thread_id)


class Stopper(OverdueAction):
    def __init__(self, seconds: float):
        super().__init__(seconds)
        self.target_thread_id: Final = get_current_thread_id()

    @override
    def _action(self) -> None:
        raise_in_thread(self.target_thread_id, TaskAbortedError)


@dataclass
class TimeoutResult:
    triggered: bool


@contextmanager
def timeout_set_to(after_seconds: float, *, raise_exception: bool = False) -> Iterator[TimeoutResult]:
    timeout_result = TimeoutResult(triggered=False)
    try:
        with Stopper(after_seconds).armed():
            yield timeout_result
    except TaskAbortedError as e:
        timeout_result.triggered = True
        if raise_exception:
            raise e


T = TypeVar("T")
P = ParamSpec("P")


def timecapped_to(seconds: float) -> Callable[[Callable[P, T]], Callable[P, T]]:
    def timecap_decorator(f: Callable[P, T]) -> Callable[P, T]:
        @wraps(f)
        def timecap_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            with timeout_set_to(seconds, raise_exception=True):
                return f(*args, **kwargs)
        return timecap_wrapper
    return timecap_decorator


def in_time_or_none(seconds: float) -> Callable[[Callable[P, T]], Callable[P, Optional[T]]]:
    def timecap_decorator(f: Callable[P, T]) -> Callable[P, Optional[T]]:
        @wraps(f)
        def timecap_wrapper(*args: P.args, **kwargs: P.kwargs) -> Optional[T]:
            try:
                with timeout_set_to(seconds, raise_exception=True):
                    return f(*args, **kwargs)
            except TaskAbortedError:
                return None
        return timecap_wrapper
    return timecap_decorator
