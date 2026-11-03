1. **Optimize `idm_logger/mqtt.py`**
   - The method `publish_data` loops over items in the payload and constructs individual messages. Inside this loop, `int(time.time())` is called redundantly for each item. Evaluating `time.time()` once before the loop and using it for all items avoids redundant system calls and guarantees all items in the batch are assigned the same timestamp. This directly matches the learning from memory and is a classic micro-optimization.
   - Use `sed` or Python to apply the optimization.

2. **Run format and lint checks**
   - Run `ruff check idm_logger/mqtt.py`.

3. **Run the test suite**
   - Run `PYTHONPATH=. pytest tests/test_mqtt.py`.

4. **Complete pre-commit steps**
   - Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.

5. **Submit the Pull Request**
   - Create a PR with a `⚡ Bolt: [performance improvement]` title.
   - PR Description will include What, Why, Impact, and Measurement.
