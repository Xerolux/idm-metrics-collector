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
**Learning:** `fetchall()` is typically the fastest way to fetch SQLite rows and release the DB lock quickly. If callers expect mutable dict-like records (e.g. `.get()` or in-place updates), convert `sqlite3.Row` objects to `dict` after fetching.
**Action:** Prefer `rows = cursor.fetchall()` and, when mutability is required, return `[dict(row) for row in rows]`.

## 2026-03-09 - Blocking File I/O in Async APIs
**Learning:** Synchronous file I/O operations (like reading/writing JSON files) in asynchronous endpoints block the entire asyncio event loop, severely degrading concurrent request handling capabilities.
**Action:** Always offload expensive or synchronous blocking file operations to a background thread using `asyncio.to_thread` in FastAPI/asyncio contexts.

## 2026-03-10 - Redundant String Parsing in Loops
**Learning:** Checking threshold alerts evaluated static string thresholds into floats on every single tick (e.g. `_to_float("12.5")`), multiplying small parsing overheads into significant aggregate CPU time on the main event loop over time.
**Action:** When static configuration values must be compared repeatedly in a fast-running loop, pre-parse and cache their types (e.g. `float`) at load time.

## 2026-03-11 - Pre-calculating Common String Prefixes
**Learning:** String interpolation and concatenation (`f"heatpump_metrics,{tags} ..."`) inside hot loops (like formatting large batches of telemetry data) incurs unnecessary CPU overhead per record when part of the string is static.
**Action:** Always pre-calculate common string prefixes outside the loop and append to them, rather than reconstructing the entire string format for every iteration.

## 2026-04-06 - Memoizing Key Parsing in Telemetry Batches
**Learning:** Evaluating `_escape_field_key` or `str(value).capitalize()` per key inside the inner loop formatting Line Protocol strings for large data batches caused redundant CPU string allocations, since batches generally contain identical keys across all records.
**Action:** Use a local dictionary cache (`_key_cache`) outside the batch loop to memoize the string parsing operations to optimize the aggregate CPU processing time.
## 2026-04-09 - Optimize Modbus Struct Pack/Unpack Loops
**Learning:** In Python loops handling struct operations (like encoding/decoding Modbus registers), manual string concatenation and list slicing inside the loop is very slow and memory-intensive. However, using vectorized C-level `struct.pack` and `struct.unpack` with format multipliers (e.g., `f"{fmt_char}{len(registers)}H"`) to pack/unpack items concurrently significantly reduces CPU time and memory allocation overhead on hot paths, cutting execution times by over 30% for these methods.
**Action:** Always prefer vectorized `struct` operations with format multipliers over manual iterations and slicing when parsing arrays of binary registers in performance-sensitive contexts.

## 2026-08-12 - Optimize Line Protocol Batch Formatting
**Learning:** In the inner loop for formatting metrics batches into Line Protocol, duplicate type checking (using `isinstance` twice consecutively) and local list appends (e.g., `lines.append`) cause unnecessary CPU overhead per record. Hoisting list methods to local variables (e.g., `lines_append = lines.append`), using `elif` to prevent redundant type checking, and explicitly formatting bools as `1 if value else 0` instead of `int(value)` improves the aggregate CPU formatting time by ~30%.
**Action:** Keep `isinstance()` for primitive type validation to ensure robustness, stringify values only when appending, hoist list methods to local variables, and use `elif` to prevent redundant type checking to maximize inner-loop speed.
