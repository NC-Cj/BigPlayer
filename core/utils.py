from loguru import logger


def validate_element_presence(nullable, element, selector):
    if nullable:
        return element

    if not element:
        raise ValueError(f"No element found for selector: {selector}")
    return element


def print_log(info=None):
    def wrapper(fn):
        def inner(*args, **kwargs):
            result = fn(*args, **kwargs)

            log_message = f"{info}" if info else f"{fn.__name__} done..."
            logger.debug(log_message)

            return result

        return inner

    return wrapper
