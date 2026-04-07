import functools
import inspect
from typing import Callable

from loguru import logger


def log_function(func: Callable) -> Callable:
    # Kiểm tra xem function có phải async không
    if inspect.iscoroutinefunction(func):

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            signature = inspect.signature(func)
            bound_args = signature.bind(*args, **kwargs)
            bound_args.apply_defaults()

            logger.debug(
                f"Start calling: {func.__name__} with arguments: {dict(bound_args.arguments)}"
            )

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                logger.exception(f"Exception in {func.__name__}:")
                raise

        return async_wrapper
    else:

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            signature = inspect.signature(func)
            bound_args = signature.bind(*args, **kwargs)
            bound_args.apply_defaults()

            logger.debug(
                f"Start calling: {func.__name__} with arguments: {dict(bound_args.arguments)}"
            )

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                logger.exception(f"Exception in {func.__name__}:")
                raise

        return sync_wrapper
