# Xerolux 2026
# SPDX-License-Identifier: MIT
"""
Retry utility decorator for handling transient failures with exponential backoff.

This module provides a decorator that can be used to wrap functions that may fail
transiently (e.g., network requests, database operations) and should be retried.
"""

import asyncio
import functools
import logging
import time
from collections.abc import Callable

logger = logging.getLogger(__name__)


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    exceptions: type[Exception] | tuple[type[Exception], ...] = Exception,
    on_retry: Callable[[Exception, int], None] | None = None,
):
    """
    Decorator to retry a function with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        initial_delay: Initial delay in seconds before first retry (default: 1.0)
        backoff_factor: Multiplier for delay after each retry (default: 2.0)
        max_delay: Maximum delay between retries in seconds (default: 60.0)
        exceptions: Exception(s) to catch and retry on (default: Exception)
        on_retry: Optional callback function called on each retry with (exception, attempt)

    Returns:
        Function result if successful, raises last exception if all retries fail

    Example:
        @retry_with_backoff(max_retries=3, initial_delay=1.0)
        def fetch_data(url):
            return requests.get(url)
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        # Final attempt failed, log and raise
                        logger.error(
                            f"{func.__name__} failed after {max_retries + 1} attempts: {e}"
                        )
                        raise

                    # Log retry attempt
                    logger.warning(
                        f"{func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}): {e}. "
                        f"Retrying in {delay:.1f}s..."
                    )

                    # Call custom retry callback if provided
                    if on_retry:
                        try:
                            on_retry(e, attempt + 1)
                        except Exception as callback_error:
                            logger.error(
                                f"Error in retry callback for {func.__name__}: {callback_error}"
                            )

                    # Wait before retry
                    time.sleep(min(delay, max_delay))
                    delay *= backoff_factor

            # Should never reach here, but just in case
            if last_exception:
                raise last_exception

        return wrapper

    return decorator


def retry_async_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    exceptions: type[Exception] | tuple[type[Exception], ...] = Exception,
    on_retry: Callable[[Exception, int], None] | None = None,
):
    """
    Async decorator to retry an async function with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        initial_delay: Initial delay in seconds before first retry (default: 1.0)
        backoff_factor: Multiplier for delay after each retry (default: 2.0)
        max_delay: Maximum delay between retries in seconds (default: 60.0)
        exceptions: Exception(s) to catch and retry on (default: Exception)
        on_retry: Optional callback function called on each retry with (exception, attempt)

    Returns:
        Coroutine that resolves to function result if successful,
        raises last exception if all retries fail

    Example:
        @retry_async_with_backoff(max_retries=3, initial_delay=1.0)
        async def fetch_data_async(url):
            return await aiohttp.get(url)
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        # Final attempt failed, log and raise
                        logger.error(
                            f"{func.__name__} failed after {max_retries + 1} attempts: {e}"
                        )
                        raise

                    # Log retry attempt
                    logger.warning(
                        f"{func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}): {e}. "
                        f"Retrying in {delay:.1f}s..."
                    )

                    # Call custom retry callback if provided
                    if on_retry:
                        try:
                            on_retry(e, attempt + 1)
                        except Exception as callback_error:
                            logger.error(
                                f"Error in retry callback for {func.__name__}: {callback_error}"
                            )

                    # Wait before retry
                    await asyncio.sleep(min(delay, max_delay))
                    delay *= backoff_factor

            # Should never reach here, but just in case
            if last_exception:
                raise last_exception

        return wrapper

    return decorator
