import cProfile
import io
import pstats
from collections.abc import Callable
from functools import wraps
from typing import Any

number_of_lines_to_print = 15


def profile(func: Callable) -> Callable:
    @wraps(func)
    async def async_wrapper(*args, **kwargs) -> Any:
        pr = cProfile.Profile()
        print("Profiling function:", func.__name__)
        pr.enable()
        result = await func(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        sortby = "cumulative"
        ps = pstats.Stats(pr, stream=s).strip_dirs().sort_stats(sortby)
        ps.print_stats(number_of_lines_to_print)
        print(s.getvalue())
        return result

    return async_wrapper


def profile_sync(func: Callable) -> Callable:
    @wraps(func)
    def sync_wrapper(*args, **kwargs) -> Any:
        pr = cProfile.Profile()
        print("Profiling function:", func.__name__)
        pr.enable()
        result = func(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        sortby = "cumulative"
        ps = pstats.Stats(pr, stream=s).strip_dirs().sort_stats(sortby)
        ps.print_stats(number_of_lines_to_print)
        print(s.getvalue())
        return result

    return sync_wrapper


class Profiler:
    def __init__(self) -> None:
        self.pr = cProfile.Profile()

    def __enter__(self) -> "Profiler":
        self.pr.enable()
        return self

    def __exit__(self, type: Any, value: Any, traceback: Any) -> None:
        self.pr.disable()
        s = io.StringIO()
        sortby = "cumulative"
        ps = pstats.Stats(self.pr, stream=s).strip_dirs().sort_stats(sortby)
        ps.print_stats(number_of_lines_to_print)
        print(s.getvalue())
