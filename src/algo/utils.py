from functools import wraps
from time import time
from typing import ParamSpec, TypeVar
from collections.abc import Callable

P = ParamSpec("P")
R = TypeVar("R")


def timing(f: Callable[P, R]) -> Callable[P, R]:
    """Decorator that prints how long a function takes.

    Args:
        f: The function to time.

    Returns:
        The wrapped function.
    """
    @wraps(f)
    def wrap(*args: P.args, **kwargs: P.kwargs) -> R:
        """Call `f` and print its run time."""
        ts = time()
        result = f(*args, **kwargs)
        te = time()
        print("func:%r  took: %2.4f sec" % (f.__name__, te - ts))
        return result

    return wrap
