import inspect
import sys

from loguru import logger

format_ = '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> ' \
          '| <magenta>{process}</magenta>:<yellow>{thread}</yellow> ' \
          '| <cyan>{extra[func_module]}</cyan>:<cyan>{extra[func_name]}</cyan>:<yellow>{extra[func_lineno]}</yellow> - <level>{message}</level>'
logger.remove(0)
logger.add(
    sys.stderr,
    format=format_
)


def validate_element_presence(nullable, element, selector):
    if nullable:
        return element

    if element is None:
        raise ValueError(f"No element found for selector: {selector}")
    return element


def print_log(info=None):
    def wrapper(fn):
        def inner(*args, **kwargs):
            result = fn(*args, **kwargs)

            # 获取被装饰函数的信息
            func_name = fn.__name__
            func_module = inspect.getmodule(fn).__name__
            try:
                func_lineno = inspect.currentframe().f_back.f_lineno  # 获取调用位置（执行位置）的行号
            except Exception:  # 防止异常情况，如在闭包或生成器中使用时可能获取不到行号
                func_lineno = None

            context = {"func_name": func_name, "func_module": func_module, "func_lineno": func_lineno}

            log_message = f"{info}" if info else f"{func_name} done..."
            logger.bind(**context).debug(log_message)

            return result

        return inner

    return wrapper
