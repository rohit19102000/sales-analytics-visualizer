
from functools import wraps
from time import perf_counter


def log_operation(func):
    """Log when an analytics operation starts and finishes."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"\n[START] {func.__name__}")
        start_time = perf_counter()

        try:
            result = func(*args, **kwargs)
            elapsed = perf_counter() - start_time
            print(
                f"[DONE] {func.__name__} "
                f"completed in {elapsed:.4f} seconds"
            )
            return result

        except Exception as error:
            print(f"[ERROR] {func.__name__}: {error}")
            raise

    return wrapper
