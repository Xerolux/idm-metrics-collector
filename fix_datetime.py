import re

def fix_file(filepath, pattern, replacement):
    with open(filepath, 'r') as f:
        content = f.read()
    new_content = re.sub(pattern, replacement, content)
    with open(filepath, 'w') as f:
        f.write(new_content)

fix_file('tests/test_scheduler.py', r'datetime\.datetime\(tzinfo=datetime\.timezone\.utc, tzinfo=datetime\.timezone\.utc\)\(2024, 1, 1, 12, 0, 0\)', r'datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)')
