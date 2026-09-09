# Xerolux 2026
# SPDX-License-Identifier: MIT
import logging
from collections import deque
import datetime
import threading


class MemoryLogHandler(logging.Handler):
    def __init__(self, capacity=1000):
        super().__init__()
        # Use appendleft so logs are stored [newest, ..., oldest]
        self.log_records = deque(maxlen=capacity)
        self.formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        # Use a separate lock for the deque (don't conflict with Handler's lock)
        self._records_lock = threading.RLock()
        self.sequence_id = 0

    def emit(self, record):
        try:
            # Format the message manually to avoid potential blocking issues
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            msg = record.getMessage()
            full_msg = f"{timestamp} - {record.levelname} - {msg}"

            with self._records_lock:
                self.sequence_id += 1
                record_entry = {
                    "id": self.sequence_id,
                    "timestamp": timestamp,
                    "level": record.levelname,
                    "message": msg,
                    "full_message": full_msg,
                    "asctime": timestamp,  # For frontend compatibility
                }
                self.log_records.appendleft(record_entry)
        except Exception as e:
            # Failsafe: don't let logging errors crash the app
            import sys

            print(f"ERROR in MemoryLogHandler.emit: {e}", file=sys.stderr, flush=True)
            try:
                self.handleError(record)
            except Exception:
                # Last resort failsafe: silently ignore to prevent logger crashes
                pass

    def get_logs(self, limit=None, since_id=None):
        """Thread-safe method to retrieve logs."""
        with self._records_lock:
            # log_records is [newest, ..., oldest]

            if since_id is not None:
                # Filter logs newer than since_id
                # Since list is ordered newest first, we iterate and stop when we hit an old one
                result = []
                for record in self.log_records:
                    if record["id"] > since_id:
                        result.append(record)
                    else:
                        break
                # Result is [newest, ..., boundary] which is correct order for frontend to prepend
                return result

            if limit:
                # Optimized slicing without full list copy
                if limit >= len(self.log_records):
                    return list(self.log_records)

                # Return the newest 'limit' records
                # Since they are at the start of the deque:
                import itertools

                return list(itertools.islice(self.log_records, 0, limit))

            return list(self.log_records)


# Global instance
memory_handler = MemoryLogHandler()
