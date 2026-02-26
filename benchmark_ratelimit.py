import time
import collections
from typing import List, Dict

# Mock constants
RATE_LIMIT_WINDOW = 60
RATE_LIMIT = 100


# Current Implementation
def check_rate_limit_list(store: Dict[str, List[float]], key: str, now: float):
    if key not in store:
        store[key] = []

    # Filter old
    store[key] = [t for t in store[key] if now - t < RATE_LIMIT_WINDOW]

    if len(store[key]) >= RATE_LIMIT:
        return False

    store[key].append(now)
    return True


# Optimized Implementation
def check_rate_limit_deque(store: Dict[str, collections.deque], key: str, now: float):
    if key not in store:
        store[key] = collections.deque()

    dq = store[key]
    # Remove old from left (oldest)
    while dq and now - dq[0] >= RATE_LIMIT_WINDOW:
        dq.popleft()

    if len(dq) >= RATE_LIMIT:
        return False

    dq.append(now)
    return True


def run_benchmark():
    iterations = 100_000
    store_list = {}
    store_deque = {}
    key = "127.0.0.1"

    # Pre-fill to simulate load
    start_time = time.time()
    for i in range(50):
        check_rate_limit_list(store_list, key, start_time + (i * 0.1))
        check_rate_limit_deque(store_deque, key, start_time + (i * 0.1))

    print(f"Benchmark: {iterations} requests against active rate limit bucket")

    # Benchmark List
    t0 = time.time()
    current_time = start_time + 60  # Start shifting window
    for i in range(iterations):
        # Advance time slightly to trigger sliding window effects
        current_time += 0.01
        check_rate_limit_list(store_list, key, current_time)
    t1 = time.time()
    print(f"List Implementation: {t1 - t0:.4f} seconds")

    # Benchmark Deque
    t0 = time.time()
    current_time = start_time + 60
    for i in range(iterations):
        current_time += 0.01
        check_rate_limit_deque(store_deque, key, current_time)
    t1 = time.time()
    print(f"Deque Implementation: {t1 - t0:.4f} seconds")


if __name__ == "__main__":
    run_benchmark()
