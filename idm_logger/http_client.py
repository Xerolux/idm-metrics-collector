# Xerolux 2026
# SPDX-License-Identifier: MIT
import logging
import time
from typing import Callable, Optional, TypeVar, Dict, Any
from functools import wraps

import requests
from requests.exceptions import RequestException

from .telemetry_config import retry_config

logger = logging.getLogger(__name__)

T = TypeVar("T")


def with_retry(
    max_retries: Optional[int] = None,
    base_delay: Optional[float] = None,
    retryable_status_codes: Optional[tuple] = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator that adds retry logic with exponential backoff to a function.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds for exponential backoff
        retryable_status_codes: HTTP status codes that should trigger a retry
    """
    _max_retries = max_retries or retry_config.max_retries
    _base_delay = base_delay or retry_config.base_delay
    _retryable_codes = retryable_status_codes or retry_config.retryable_status_codes

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_error: Optional[Exception] = None

            for attempt in range(_max_retries):
                try:
                    return func(*args, **kwargs)
                except RequestException as e:
                    last_error = e

                    response = getattr(e, "response", None)
                    status_code = (
                        getattr(response, "status_code", None) if response else None
                    )

                    should_retry = (
                        status_code in _retryable_codes or status_code is None
                    )

                    if not should_retry or attempt >= _max_retries - 1:
                        raise

                    delay = min(_base_delay * (2**attempt), retry_config.max_delay)
                    logger.debug(
                        f"Retryable error on attempt {attempt + 1}/{_max_retries}, "
                        f"retrying in {delay:.1f}s: {e}"
                    )
                    time.sleep(delay)

            raise last_error or Exception("Max retries exceeded")

        return wrapper

    return decorator


class HttpClient:
    """HTTP client with built-in retry logic and connection pooling."""

    def __init__(
        self,
        default_timeout: float = 30.0,
        max_retries: Optional[int] = None,
    ):
        self.default_timeout = default_timeout
        self._max_retries = max_retries or retry_config.max_retries
        self.session = requests.Session()

    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay with exponential backoff and jitter."""
        delay = retry_config.base_delay * (2**attempt)
        return min(delay, retry_config.max_delay)

    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        stream: bool = False,
    ) -> requests.Response:
        """GET request with retry logic."""
        last_error: Optional[Exception] = None

        for attempt in range(self._max_retries):
            try:
                response = self.session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=timeout or self.default_timeout,
                    stream=stream,
                )

                if response.status_code in retry_config.retryable_status_codes:
                    if attempt < self._max_retries - 1:
                        delay = self._calculate_delay(attempt)
                        logger.debug(
                            f"Server error {response.status_code}, "
                            f"retrying in {delay:.1f}s (attempt {attempt + 1}/{self._max_retries})"
                        )
                        time.sleep(delay)
                        continue

                return response

            except RequestException as e:
                last_error = e
                if attempt < self._max_retries - 1:
                    delay = self._calculate_delay(attempt)
                    logger.debug(f"Network error, retrying in {delay:.1f}s: {e}")
                    time.sleep(delay)
                    continue
                raise

        raise last_error or Exception("Max retries exceeded")

    def post(
        self,
        url: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        """POST request with retry logic."""
        last_error: Optional[Exception] = None

        for attempt in range(self._max_retries):
            try:
                response = self.session.post(
                    url,
                    json=json,
                    data=data,
                    headers=headers,
                    timeout=timeout or self.default_timeout,
                    files=files,
                )

                if response.status_code in retry_config.retryable_status_codes:
                    if attempt < self._max_retries - 1:
                        delay = self._calculate_delay(attempt)
                        logger.debug(
                            f"Server error {response.status_code}, "
                            f"retrying in {delay:.1f}s (attempt {attempt + 1}/{self._max_retries})"
                        )
                        time.sleep(delay)
                        continue

                return response

            except RequestException as e:
                last_error = e
                if attempt < self._max_retries - 1:
                    delay = self._calculate_delay(attempt)
                    logger.debug(f"Network error, retrying in {delay:.1f}s: {e}")
                    time.sleep(delay)
                    continue
                raise

        raise last_error or Exception("Max retries exceeded")

    def close(self):
        """Close the session."""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


http_client = HttpClient()
