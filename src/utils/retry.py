import time

from functools import wraps
from src.utils.logger import get_logger

logger = get_logger(__name__)


def retry(max_retries=3, initial_delay=1, backoff=2):
    """
    Декоратор для повторных попыток при ошибках
    max_retries: максимальное количество попыток
    initial_delay: начальная задержка в секундах
    backoff: множитель увеличения задержки
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt == max_retries:
                        logger.error(
                            f"Function {func.__name__} failed after {max_retries} retries: {e}"
                        )
                        raise

                    logger.warning(
                        f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {delay}s..."
                    )
                    time.sleep(delay)
                    delay *= backoff

            raise last_exception
        return wrapper
    return decorator
