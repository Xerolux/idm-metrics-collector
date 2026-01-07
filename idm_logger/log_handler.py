import logging
from collections import deque
import datetime

class MemoryLogHandler(logging.Handler):
    def __init__(self, capacity=1000):
        super().__init__()
        self.log_records = deque(maxlen=capacity)
        self.formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    def emit(self, record):
        try:
            msg = self.format(record)
            self.log_records.append({
                'timestamp': datetime.datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S'),
                'level': record.levelname,
                'message': record.getMessage(), # Get the raw message or formatted? format() gets the full string.
                'full_message': msg
            })
        except Exception:
            self.handleError(record)

# Global instance
memory_handler = MemoryLogHandler()
