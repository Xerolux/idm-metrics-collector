import re

def fix_file(filepath, pattern, replacement):
    with open(filepath, 'r') as f:
        content = f.read()
    new_content = re.sub(pattern, replacement, content)
    with open(filepath, 'w') as f:
        f.write(new_content)

fix_file('tests/verify_technician_code.py', r'datetime\.datetime\.now\(tz=datetime\.timezone\.utc\)', r'datetime.datetime.now(datetime.timezone.utc)')
