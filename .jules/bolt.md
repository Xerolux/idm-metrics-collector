## 2024-05-22 - MetricsWriter Connection Overhead
**Learning:** `requests.post` inside the main loop created a new TCP connection for every metric write, causing unnecessary overhead.
**Action:** Always use `requests.Session()` for repeated requests to the same host to enable connection pooling.

## 2025-05-23 - Synchronous Metrics Blocking Main Loop
**Learning:** `requests.Session.post` is still a synchronous blocking call. Even with connection pooling, network latency or timeouts (5s) block the main application loop, affecting sensor reading frequency and "realtime mode" stability.
**Action:** Offload metric writing to a background thread using a `queue.Queue` (Producer-Consumer pattern) to decouple the main loop from network IO latency.

## 2025-05-24 - Unused WebSocket Logic
**Learning:** The `broadcast_metric_update` method existed but was never called, and client subscriptions lacked `join_room` logic, rendering real-time updates non-functional. The frontend relied on frequent polling (5s) as a result.
**Action:** Implemented `join_room` in subscription handler and hooked `broadcast_metrics` into the main data update loop. Converted `SensorValues` to use WebSocket push updates, reducing polling to 60s fallback.

## 2026-03-08 - SQLite Cursor Iteration Anti-Pattern
**Learning:** Replacing `cursor.fetchall()` with list comprehensions (e.g., `[dict(row) for row in cursor]`) inside database methods creates an O(N) list with significant Python overhead. This makes it slower and worse for memory than the highly-optimized C-code of `fetchall()`. Furthermore, yielding rows directly from a cursor while inside a context manager keeps the database lock open during iteration and risks application-wide lock contention.
**Action:** Use `cursor.fetchall()` for fetching query results. Avoid Python-level loops over cursor results when the entire dataset needs to be returned.

## 2026-03-09 - Blocking File I/O in Async APIs
**Learning:** Synchronous file I/O operations (like reading/writing JSON files) in asynchronous endpoints block the entire asyncio event loop, severely degrading concurrent request handling capabilities.
**Action:** Always offload expensive or synchronous blocking file operations to a background thread using `asyncio.to_thread` in FastAPI/asyncio contexts.

## 2026-03-10 - Redundant String Parsing in Loops
**Learning:** Checking threshold alerts evaluated static string thresholds into floats on every single tick (e.g. `_to_float("12.5")`), multiplying small parsing overheads into significant aggregate CPU time on the main event loop over time.
**Action:** When static configuration values must be compared repeatedly in a fast-running loop, pre-parse and cache their types (e.g. `float`) at load time.

## 2026-03-11 - Pre-calculating Common String Prefixes
**Learning:** String interpolation and concatenation (`f"heatpump_metrics,{tags} ..."`) inside hot loops (like formatting large batches of telemetry data) incurs unnecessary CPU overhead per record when part of the string is static.
**Action:** Always pre-calculate common string prefixes outside the loop and append to them, rather than reconstructing the entire string format for every iteration.
