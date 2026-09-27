from functools import wraps
from time import time
from typing import ParamSpec, TypeVar
from collections.abc import Callable

P = ParamSpec("P")
R = TypeVar("R")


def timing(f: Callable[P, R]) -> Callable[P, R]:
    @wraps(f)
    def wrap(*args: P.args, **kwargs: P.kwargs) -> R:
        ts = time()
        result = f(*args, **kwargs)
        te = time()
        print("func:%r  took: %2.4f sec" % (f.__name__, te - ts))
        return result
    return wrap
