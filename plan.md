1. **Optimize `int(time.time())` inside loop in `publish_data`**:
   - In `idm_logger/mqtt.py`, the method `publish_data(self, data)` loops over `data.items()`.
   - In each iteration, it does `payload = {"value": value, "unit": unit, "timestamp": int(time.time())}`.
   - We will evaluate `now_ts = int(time.time())` once outside the loop and reuse it inside the loop to avoid redundant system calls and ensure semantic correctness (all items in a batch should share the exact same timestamp).
   - We will also add a note to `.jules/bolt.md` based on memory.
2. **Run tests**:
   - Ensure tests still pass (e.g. `PYTHONPATH=. python -m pytest tests/test_mqtt.py`).
3. **Complete pre-commit steps**:
   - Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.
4. **Submit PR**:
   - Create a PR with title "⚡ Bolt: [performance improvement]" and required description.
