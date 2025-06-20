from time import perf_counter
from functools import wraps
from logging import Logger
from typing import Optional
from app.core.logger import get_logger  # adjust import to your file

def log_timeit(label: Optional[str] = None, logger: Optional[Logger] = None):
    """
    Decorator to log execution time of a function using the provided logger.

    Args:
        label (str): Optional label for the log message.
        logger (Logger): Optional logger instance. Defaults to `get_logger()`.
    """
    def decorator(func):
        log = logger or get_logger()

        @wraps(func)
        def wrapper(*args, **kwargs):
            start = perf_counter()
            result = func(*args, **kwargs)
            duration = (perf_counter() - start) * 1000  # in ms
            log.info(f"[{label or func.__name__}] executed in {duration:.2f} ms")
            return result
        return wrapper
    return decorator
