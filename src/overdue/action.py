import threading
from abc import ABC, abstractmethod
from contextlib import contextmanager
from datetime import timedelta

from typing import final, Iterator, Final


class OverdueAction(ABC):
    def __init__(self, seconds: float | timedelta):
        interval = seconds.total_seconds() if isinstance(seconds, timedelta) else seconds
        self.timer: Final = threading.Timer(interval, self._action)

    @abstractmethod
    def _action(self) -> None:
        """Called from the Timer thread -> must be threadsafe"""
        ...

    @final
    def arm(self) -> None:
        self.timer.start()

    @final
    def disarm(self) -> None:
        self.timer.cancel()

    @final
    @contextmanager
    def armed(self) -> Iterator[None]:
        try:
            self.arm()
            yield
        finally:
            self.disarm()
