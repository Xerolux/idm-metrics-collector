import threading
import time
from collections import OrderedDict
from typing import Dict, List, Tuple

import structlog

try:
    from .config import rate_limit_config, security_config
except ImportError:
    from config import rate_limit_config, security_config

logger = structlog.get_logger("telemetry-ratelimit")


class RateLimiter:
    def __init__(self):
        self._store: Dict[str, List[float]] = OrderedDict()
        self._lock = threading.Lock()
        self._redis = (
            security_config.redis_client if security_config.use_redis else None
        )

    def check(
        self, client_ip: str, endpoint_type: str = "default"
    ) -> Tuple[bool, Dict[str, str]]:
        rate_limit = rate_limit_config.get_limit(endpoint_type)
        now = time.time()

        if self._redis:
            return self._check_redis(client_ip, endpoint_type, rate_limit, now)
        return self._check_memory(client_ip, endpoint_type, rate_limit, now)

    def _check_redis(
        self, client_ip: str, endpoint_type: str, rate_limit: int, now: float
    ) -> Tuple[bool, Dict[str, str]]:
        compound_key = f"ratelimit:{client_ip}:{endpoint_type}"
        try:
            pipe = self._redis.pipeline()

            min_score = now - rate_limit_config.window
            pipe.zremrangebyscore(compound_key, 0, min_score)
            pipe.zcard(compound_key)
            pipe.zadd(compound_key, {str(now): now})
            pipe.expire(compound_key, rate_limit_config.window)

            results = pipe.execute()
            current_count = results[1]

            remaining = max(0, rate_limit - current_count)
            oldest = self._redis.zrange(compound_key, 0, 0, withscores=True)
            reset_time = (
                int(oldest[0][1] + rate_limit_config.window)
                if oldest
                else int(now + rate_limit_config.window)
            )

            if current_count >= rate_limit:
                return False, {
                    "X-RateLimit-Limit": str(rate_limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(
                        int(oldest[0][1] + rate_limit_config.window)
                        if oldest
                        else int(now + rate_limit_config.window)
                    ),
                    "Retry-After": str(rate_limit_config.window),
                }

            return True, {
                "X-RateLimit-Limit": str(rate_limit),
                "X-RateLimit-Remaining": str(remaining - 1),
                "X-RateLimit-Reset": str(reset_time),
            }
        except Exception as e:
            logger.warning(
                "redis_rate_limit_failed", error=str(e), fallback="in_memory"
            )
            return self._check_memory(client_ip, endpoint_type, rate_limit, now)

    def _check_memory(
        self, client_ip: str, endpoint_type: str, rate_limit: int, now: float
    ) -> Tuple[bool, Dict[str, str]]:
        compound_key = f"ratelimit:{client_ip}:{endpoint_type}"

        with self._lock:
            if len(self._store) >= rate_limit_config.max_entries:
                evicted_count = 0
                for _ in range(100):
                    if self._store:
                        self._store.popitem(last=False)
                        evicted_count += 1
                logger.debug("rate_limit_eviction", evicted=evicted_count)

            if compound_key not in self._store:
                self._store[compound_key] = []

            valid_timestamps = [
                t
                for t in self._store[compound_key]
                if now - t < rate_limit_config.window
            ]
            self._store[compound_key] = valid_timestamps

            if len(valid_timestamps) >= rate_limit:
                max_ts = max(valid_timestamps) if valid_timestamps else now
                return False, {
                    "X-RateLimit-Limit": str(rate_limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(max_ts + rate_limit_config.window)),
                    "Retry-After": str(rate_limit_config.window),
                }

            self._store[compound_key].append(now)
            self._store.move_to_end(compound_key)

            remaining = max(0, rate_limit - len(self._store[compound_key]))
            reset_time = int(max(self._store[compound_key]) + rate_limit_config.window)

            return True, {
                "X-RateLimit-Limit": str(rate_limit),
                "X-RateLimit-Remaining": str(remaining - 1),
                "X-RateLimit-Reset": str(reset_time),
            }


rate_limiter = RateLimiter()
