"""Retry helpers for flaky network-backed TTS providers."""

import logging
import random
import time
from collections.abc import Callable
from typing import TypeVar

logger = logging.getLogger(__name__)

T = TypeVar('T')


def retry_with_backoff(
    fn: Callable[[], T],
    *,
    max_attempts: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    retryable_exceptions: tuple[type[Exception], ...] = (Exception,),
) -> T:
    """Call ``fn`` until it succeeds or ``max_attempts`` is exhausted.

    Delay between attempts grows exponentially with jitter:
    ``min(base_delay * 2**attempt, max_delay) * (0.5 + random())``.
    """
    last_exc: Exception | None = None

    for attempt in range(max_attempts):
        try:
            return fn()
        except retryable_exceptions as exc:
            last_exc = exc
            if attempt >= max_attempts - 1:
                break

            delay = min(base_delay * (2 ** attempt), max_delay)
            delay *= 0.5 + random.random()
            logger.warning(
                'Attempt %d/%d failed (%s: %s); retrying in %.1fs',
                attempt + 1,
                max_attempts,
                type(exc).__name__,
                exc,
                delay,
            )
            time.sleep(delay)

    assert last_exc is not None
    raise last_exc
