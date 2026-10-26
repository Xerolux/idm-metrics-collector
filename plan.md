1. **Optimize AuditLogger Synchronous File I/O with `asyncio.to_thread`**
   - The memory section explicitly mentions: `Audit log retrieval methods (get_recent_events, get_events_by_admin, get_events_by_action) and cleanup_old_logs in telemetry_server/audit_log.py are actually synchronous and block the FastAPI event loop with un-offloaded file I/O operations, representing a clear optimization opportunity to use asyncio.to_thread.`
   - These methods are currently synchronous and involve blocking file system read operations. In a FastAPI application, synchronous blocking operations halt the event loop, causing poor performance and higher latency when serving concurrent requests.
   - I will modify `telemetry_server/app.py` to offload the calls to `audit_logger` methods using `asyncio.to_thread()`. This allows the file I/O to run in a separate thread without blocking the event loop.
2. **Update `app.py` logic**
   - Update `admin_get_audit_log` to use `await asyncio.to_thread(audit_logger.get_events_by_action, action, limit=limit)` (and similarly for other branches).
   - Update `cleanup_rate_limits_and_bans` background task to offload `audit_logger.cleanup_old_logs()` and `training_queue.cleanup_old_tasks(max_age_days=30)` using `await asyncio.to_thread(...)`. Note: `cleanup_old_tasks` is mentioned in memory: `cleanup_old_tasks in TrainingQueue is a synchronous method and is called without await in the cleanup_rate_limits_and_bans background task in telemetry_server/app.py.`
3. **Verify tests**
   - Run unit tests to ensure `admin_get_audit_log` still functions correctly and no functional regressions are introduced.
   - Run format and lint on modified code.
4. **Complete pre-commit steps**
   - Run `pre_commit_instructions` to ensure proper testing, verification, review, and reflection.
5. **Submit PR**
   - Create a PR with title "⚡ Bolt: Offload synchronous AuditLog and TrainingQueue file operations to background thread" describing what, why, impact, and measurement.
