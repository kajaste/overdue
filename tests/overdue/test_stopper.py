import random
from datetime import timedelta
from typing import Final

import pytest
from _pytest.fixtures import FixtureRequest

from overdue import timeout_set_to, TaskAbortedError, timecapped_to, in_time_or_none

_very_large_number: Final = 999_999_999_999_999

def _slow_function() -> None:
    for _ in range(_very_large_number):
        random.random() * _very_large_number / random.random() * _very_large_number


_fast_function_result: Final = 14

def _fast_function() -> int:
    return _fast_function_result

@pytest.fixture(params=[0.01, timedelta(milliseconds=10)], ids=["float", "timedelta"])
def timeout_value(request: FixtureRequest) -> float | timedelta:
    value: float | timedelta = request.param
    return value


def test_timeout_set_to(timeout_value: float | timedelta) -> None:
    with timeout_set_to(timeout_value) as timeout:
        assert _fast_function() == _fast_function_result
    assert not timeout.triggered

    with timeout_set_to(timeout_value) as timeout:
        _slow_function()
        assert False, "Timeout did not trigger"
    assert timeout.triggered  # type:ignore[unreachable]  # Types and exceptions :')


def test_timeout_set_to_raises(timeout_value: float | timedelta) -> None:
    with timeout_set_to(timeout_value, raise_exception=True):
        assert _fast_function() == _fast_function_result

    with pytest.raises(TaskAbortedError):
        with timeout_set_to(timeout_value, raise_exception=True):
            _slow_function()
            assert False, "Timeout did not trigger"


def test_timecapped_to(timeout_value: float | timedelta) -> None:
    @timecapped_to(timeout_value)
    def fast_enough_function() -> int:
        return _fast_function()

    assert fast_enough_function() == _fast_function_result

    @timecapped_to(timeout_value)
    def too_slow_function() -> None:
        _slow_function()

    with pytest.raises(TaskAbortedError):
        too_slow_function()
        assert False, "Timeout did not trigger"


def test_in_time_or_none(timeout_value: float | timedelta) -> None:
    @in_time_or_none(timeout_value)
    def fast_enough_function() -> int:
        return _fast_function()

    assert fast_enough_function() == _fast_function_result

    @in_time_or_none(timeout_value)
    def function() -> int:
        _slow_function()
        return 7

    assert function() is None
