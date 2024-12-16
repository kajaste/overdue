import random
from typing import Final

import pytest

from overdue import timeout_set_to, TaskAbortedError, timecapped_to, in_time_or_none

_very_large_number: Final = 999_999_999_999_999

def _slow_function() -> None:
    for _ in range(_very_large_number):
        random.random() * _very_large_number / random.random() * _very_large_number


_fast_function_result: Final = 14

def _fast_function() -> int:
    return _fast_function_result


def test_timeout_set_to() -> None:
    with timeout_set_to(0.01) as timeout:
        assert _fast_function() == _fast_function_result
    assert not timeout.triggered

    with timeout_set_to(0.01) as timeout:
        _slow_function()
        assert False, "Timeout did not trigger"
    assert timeout.triggered  # type:ignore[unreachable]  # Types and exceptions :')


def test_timeout_set_to_raises() -> None:
    with timeout_set_to(0.01, raise_exception=True):
        assert _fast_function() == _fast_function_result

    with pytest.raises(TaskAbortedError):
        with timeout_set_to(0.01, raise_exception=True):
            _slow_function()
            assert False, "Timeout did not trigger"


def test_timecapped_to() -> None:
    @timecapped_to(0.01)
    def fast_enough_function() -> int:
        return _fast_function()

    assert fast_enough_function() == _fast_function_result

    @timecapped_to(0.01)
    def too_slow_function() -> None:
        _slow_function()

    with pytest.raises(TaskAbortedError):
        too_slow_function()
        assert False, "Timeout did not trigger"


def test_in_time_or_none() -> None:
    @in_time_or_none(0.01)
    def fast_enough_function() -> int:
        return _fast_function()

    assert fast_enough_function() == _fast_function_result

    @in_time_or_none(0.01)
    def function() -> int:
        _slow_function()
        return 7

    assert function() is None
