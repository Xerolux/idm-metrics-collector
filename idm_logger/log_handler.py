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

    def get_logs(self, limit=None):
        """Thread-safe method to retrieve logs."""
        with self.lock:
            if limit:
                # Optimized slicing without full list copy
                if limit >= len(self.log_records):
                    return list(self.log_records)

                # Deque rotation/slicing is not direct, but we can iterate from the end
                # Or just use the fact that list(deque) is relatively fast, but let's be smarter if possible.
                # Actually, for a deque, casting to list is O(N). Slicing a list is O(K).
                # To avoid O(N) copy, we can use itertools.islice.
                # However, islice on deque iterates from start. We want end.
                # Simplest optimized way for 'last N':
                start_index = len(self.log_records) - limit
                if start_index < 0: start_index = 0

                import itertools
                return list(itertools.islice(self.log_records, start_index, None))

            return list(self.log_records)

# Global instance
memory_handler = MemoryLogHandler()
