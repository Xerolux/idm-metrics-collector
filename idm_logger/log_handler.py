import logging
from collections import deque
import datetime
import threading

class MemoryLogHandler(logging.Handler):
    def __init__(self, capacity=1000):
        super().__init__()
        self.log_records = deque(maxlen=capacity)
        self.formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.lock = threading.Lock()

    def emit(self, record):
        try:
            msg = self.format(record)
            record_entry = {
                'timestamp': datetime.datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S'),
                'level': record.levelname,
                'message': record.getMessage(), # Get the raw message or formatted? format() gets the full string.
                'full_message': msg
            }
            with self.lock:
                self.log_records.append(record_entry)
        except Exception:
            self.handleError(record)

    def get_logs(self):
        """Thread-safe method to retrieve logs."""
        with self.lock:
            return list(self.log_records)

# Global instance
memory_handler = MemoryLogHandler()
