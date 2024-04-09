from functools import wraps
from time import sleep
from typing import Callable, Any

from loguru import logger


def validate_element_presence(nullable, element, selector):
    if nullable:
        return element

    if not element:
        raise ValueError(f"No element found for selector: {selector}")
    return element


def validate_action(fn):
    def decorator(*args, **kwargs):
        target = args[1]
        result = fn(*args, **kwargs)
        if result is None:
            logger.error(f"Action: {fn.__name__}, Message: {target} invalid ")
        return result

    return decorator


def print_log(info=None):
    def decorator(fn):
        def inner(*args, **kwargs):
            result = fn(*args, **kwargs)

            log_message = f"{info}" if info else f"{fn.__name__} done..."
            logger.debug(log_message)

            return result

        return inner

    return decorator


def retry(retries: int = 3, delay: float = 1) -> Callable:
    if retries < 1 or delay <= 0:
        raise ValueError('Are you high, mate?')

    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kwargs) -> Any:
            for i in range(1, retries + 1):  # 1 to retries + 1 since upper bound is exclusive
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    if i == retries:
                        logger.error(f'Error: {repr(e)}.')
                        logger.error(f'"{fn.__name__}()" failed after {retries} retries.')
                        break
                    else:
                        logger.warning(f'Error: {repr(e)} -> Retrying...')
                        sleep(delay)

        return wrapper

    return decorator
