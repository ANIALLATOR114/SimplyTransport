import cProfile
import pstats
import io
from functools import wraps

number_of_lines_to_print = 15

def profile(func):
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
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


class Profiler:
    def __init__(self):
        self.pr = cProfile.Profile()

    def __enter__(self):
        self.pr.enable()
        return self

    def __exit__(self, type, value, traceback):
        self.pr.disable()
        s = io.StringIO()
        sortby = "cumulative"
        ps = pstats.Stats(self.pr, stream=s).strip_dirs().sort_stats(sortby)
        ps.print_stats(number_of_lines_to_print)
        print(s.getvalue())