1. **Optimize Timestamp Generation in MQTT Loop:**
   - Modify `publish_data` in `idm_logger/mqtt.py` to evaluate `int(time.time())` once outside the loop instead of on every iteration.
   - This avoids redundant system calls in hot paths and ensures semantic correctness (exact same timestamp for the whole batch), which aligns with the memory: "When generating timestamps for batches of data in Python (e.g., generating sensor readings payloads in idm_logger/mqtt.py), evaluate invariant system calls like time.time() once outside the loop rather than on every iteration. This avoids redundant system calls in hot paths and ensures semantic correctness by assigning the exact same timestamp to all items in the batch."
2. **Remove Unnecessary Files:**
   - Delete benchmark script (`bench_metrics.py`, `bench_time.py`, `test_perf.py`, `test_perf_2.py`, `test_perf_3.py`, `test_perf_4.py`, `fix_metrics.py`, `fix_mqtt.py`).
3. **Pre-commit step:**
   - Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.
4. **Submit PR:**
   - Create PR with title "⚡ Bolt: [performance improvement]" and description adhering to instructions.
