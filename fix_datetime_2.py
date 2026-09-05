import re

def fix_file(filepath, pattern, replacement):
    with open(filepath, 'r') as f:
        content = f.read()
    new_content = re.sub(pattern, replacement, content)
    with open(filepath, 'w') as f:
        f.write(new_content)

fix_file('tests/test_scheduler.py', r'mock_datetime.datetime\(tzinfo=datetime.timezone.utc\).now.return_value = fixed_now', r'mock_datetime.datetime.now.return_value = fixed_now')
fix_file('tests/test_technician_code_logic.py', r'datetime\(2023, 10, 27, 14, 30, tzinfo=datetime\.timezone\.utc\)', r'datetime(2023, 10, 27, 14, 30, tzinfo=timezone.utc)')
fix_file('tests/test_technician_code_logic.py', r'datetime\(2024, 5, 5, 9, 15, tzinfo=datetime\.timezone\.utc\)', r'datetime(2024, 5, 5, 9, 15, tzinfo=timezone.utc)')
fix_file('tests/test_technician_code_logic.py', r'from datetime import datetime', r'from datetime import datetime, timezone')
