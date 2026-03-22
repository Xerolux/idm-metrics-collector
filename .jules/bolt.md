## 2024-05-22 - MetricsWriter Connection Overhead
**Learning:** `requests.post` inside the main loop created a new TCP connection for every metric write, causing unnecessary overhead.
**Action:** Always use `requests.Session()` for repeated requests to the same host to enable connection pooling.

## 2025-05-23 - Synchronous Metrics Blocking Main Loop
**Learning:** `requests.Session.post` is still a synchronous blocking call. Even with connection pooling, network latency or timeouts (5s) block the main application loop, affecting sensor reading frequency and "realtime mode" stability.
**Action:** Offload metric writing to a background thread using a `queue.Queue` (Producer-Consumer pattern) to decouple the main loop from network IO latency.

## 2025-05-24 - Unused WebSocket Logic
**Learning:** The `broadcast_metric_update` method existed but was never called, and client subscriptions lacked `join_room` logic, rendering real-time updates non-functional. The frontend relied on frequent polling (5s) as a result.
**Action:** Implemented `join_room` in subscription handler and hooked `broadcast_metrics` into the main data update loop. Converted `SensorValues` to use WebSocket push updates, reducing polling to 60s fallback.

## 2026-03-08 - SQLite Cursor Iteration
**Learning:** Iterating directly over SQLite cursors (e.g. `for row in cursor:`) prevents O(N) memory consumption from loading entire result sets via `fetchall()`, which is especially important for jobs and alerts.
**Action:** Use cursor iteration or `list(cursor)` to unpack rows rather than `fetchall()` to optimize memory usage.

## 2026-03-09 - Blocking File I/O in Async APIs
**Learning:** Synchronous file I/O operations (like reading/writing JSON files) in asynchronous endpoints block the entire asyncio event loop, severely degrading concurrent request handling capabilities.
**Action:** Always offload expensive or synchronous blocking file operations to a background thread using `asyncio.to_thread` in FastAPI/asyncio contexts.

## 2026-03-10 - O(N) Database Load on Admin Endpoint
**Learning:** The `admin_installation_details` endpoint was executing an expensive `group by(installation_id) (count by (installation_id))` query on every request to compute a simple contribution rank. This caused an O(N) database load, severely impacting backend performance.
**Action:** Implement a global cache (e.g. `_contribution_rank_cache`) with a TTL. Avoid executing the expensive cross-installation analytical queries unless the cache is stale or missing. And when valid, remove the query from the batch `asyncio.gather` list.
