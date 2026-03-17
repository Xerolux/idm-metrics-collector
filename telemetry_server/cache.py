import asyncio
import hashlib
import os
import time
from typing import Dict, Optional, Tuple, Any

from .config import cache_config


class FileHashCache:
    def __init__(self, ttl: int = cache_config.hash_ttl):
        self.ttl = ttl
        self._cache: Dict[str, Tuple[Optional[str], float]] = {}

    async def get(self, filepath: str) -> Optional[str]:
        now = time.time()

        if filepath in self._cache:
            cached_hash, timestamp = self._cache[filepath]
            if now - timestamp < self.ttl:
                return cached_hash

        hash_val = await asyncio.get_event_loop().run_in_executor(
            None, self._compute_hash, filepath
        )

        if hash_val:
            self._cache[filepath] = (hash_val, now)

        return hash_val

    def _compute_hash(self, filepath: str) -> Optional[str]:
        if not os.path.exists(filepath):
            return None
        try:
            with open(filepath, "rb") as f:
                return hashlib.file_digest(f, "sha256").hexdigest()
        except Exception:
            return None

    def invalidate(self, filepath: str) -> None:
        self._cache.pop(filepath, None)

    def clear(self) -> None:
        self._cache.clear()


class PoolStatsCache:
    def __init__(self, ttl: int = cache_config.pool_stats_ttl):
        self.ttl = ttl
        self._cache: Tuple[Optional[Dict[str, Any]], float] = (None, 0)

    async def get(self) -> Optional[Dict[str, Any]]:
        cached_stats, timestamp = self._cache
        if cached_stats and time.time() - timestamp < self.ttl:
            return cached_stats
        return None

    async def set(self, stats: Dict[str, Any]) -> None:
        self._cache = (stats, time.time())

    def clear(self) -> None:
        self._cache = (None, 0)


class CommunityAverageCache:
    def __init__(self, ttl: int = cache_config.community_avg_ttl):
        self.ttl = ttl
        self._cache: Dict[str, Tuple[Dict[str, Any], float]] = {}

    def get(self, cache_key: str) -> Optional[Tuple[Dict[str, Any], float]]:
        if cache_key in self._cache:
            cached_result, cached_time = self._cache[cache_key]
            if time.time() - cached_time < self.ttl:
                return (cached_result, cached_time)
        return None

    async def set(self, cache_key: str, result: Dict[str, Any]) -> None:
        self._cache[cache_key] = (result, time.time())

    def clear(self) -> None:
        self._cache.clear()

    def cleanup_expired(self) -> int:
        now = time.time()
        expired = [k for k, (_, t) in self._cache.items() if now - t >= self.ttl]
        for k in expired:
            del self._cache[k]
        return len(expired)


file_hash_cache = FileHashCache()
pool_stats_cache = PoolStatsCache()
community_avg_cache = CommunityAverageCache()


async def cleanup_all_caches() -> int:
    total_expired = community_avg_cache.cleanup_expired()
    return total_expired
