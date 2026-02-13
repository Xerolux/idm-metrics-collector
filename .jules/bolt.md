## 2024-05-22 - MetricsWriter Connection Overhead
**Learning:** `requests.post` inside the main loop created a new TCP connection for every metric write, causing unnecessary overhead.
**Action:** Always use `requests.Session()` for repeated requests to the same host to enable connection pooling.

## 2025-05-23 - Synchronous Metrics Blocking Main Loop
**Learning:** `requests.Session.post` is still a synchronous blocking call. Even with connection pooling, network latency or timeouts (5s) block the main application loop, affecting sensor reading frequency and "realtime mode" stability.
**Action:** Offload metric writing to a background thread using a `queue.Queue` (Producer-Consumer pattern) to decouple the main loop from network IO latency.

## 2025-05-24 - Unused WebSocket Logic
**Learning:** The `broadcast_metric_update` method existed but was never called, and client subscriptions lacked `join_room` logic, rendering real-time updates non-functional. The frontend relied on frequent polling (5s) as a result.
**Action:** Implemented `join_room` in subscription handler and hooked `broadcast_metrics` into the main data update loop. Converted `SensorValues` to use WebSocket push updates, reducing polling to 60s fallback.

## 2026-02-13 - Python Boolean Type Inheritance
**Learning:** In Python, `isinstance(True, int)` returns `True` because `bool` inherits from `int`. Checking `isinstance(value, (int, float))` BEFORE `isinstance(value, bool)` makes the boolean check unreachable, causing booleans to be formatted as integers/strings (e.g., `True` vs `true`) if logic differs.
**Action:** Always check `isinstance(value, bool)` *before* checking `isinstance(value, int)` when handling mixed types, or use strict type checking (`type(value) is bool`) if appropriate.
