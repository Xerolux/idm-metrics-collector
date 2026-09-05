git restore tests/test_scheduler.py tests/test_technician_code_logic.py tests/verify_technician_code.py
git checkout tests/test_scheduler.py tests/test_technician_code_logic.py tests/verify_technician_code.py
sed -i 's/datetime.datetime/datetime.datetime/g' tests/test_scheduler.py
sed -i 's/mock_datetime.datetime(tzinfo=datetime.timezone.utc).now.return_value = fixed_now/mock_datetime.datetime.now.return_value = fixed_now/g' tests/test_scheduler.py
sed -i 's/fixed_now = datetime.datetime(2024, 1, 1, 12, 0, 0)/fixed_now = datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)/g' tests/test_scheduler.py
sed -i 's/datetime(2023, 10, 27, 14, 30)/datetime(2023, 10, 27, 14, 30, tzinfo=timezone.utc)/g' tests/test_technician_code_logic.py
sed -i 's/datetime(2024, 5, 5, 9, 15)/datetime(2024, 5, 5, 9, 15, tzinfo=timezone.utc)/g' tests/test_technician_code_logic.py
sed -i 's/from datetime import datetime/from datetime import datetime, timezone/g' tests/test_technician_code_logic.py
sed -i 's/datetime.datetime.now()/datetime.datetime.now(datetime.timezone.utc)/g' tests/verify_technician_code.py

ruff check tests/test_scheduler.py tests/test_technician_code_logic.py tests/verify_technician_code.py
PYTHONPATH=. python -m pytest tests/test_scheduler.py tests/test_technician_code_logic.py
