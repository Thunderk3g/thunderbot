"""Client-side order throttle.

The engine places a handful of orders a day, far below SEBI's 10 orders/second
algo-registration threshold, but a bug (e.g. a retry loop) must never be able to
breach it. Every order-mutating broker call goes through ``OrderThrottle``.
"""

from __future__ import annotations

import threading
import time
from collections import deque
from collections.abc import Callable


class OrderThrottle:
    def __init__(
        self,
        per_second: int,
        per_minute: int,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        if per_second <= 0 or per_minute <= 0:
            raise ValueError("rates must be positive")
        self.per_second = per_second
        self.per_minute = per_minute
        self._clock = clock
        self._sleep = sleep
        self._events: deque[float] = deque()
        self._lock = threading.Lock()

    def _wait_time(self, now: float) -> float:
        while self._events and now - self._events[0] >= 60.0:
            self._events.popleft()
        wait = 0.0
        if len(self._events) >= self.per_minute:
            wait = max(wait, 60.0 - (now - self._events[-self.per_minute]))
        recent = [t for t in self._events if now - t < 1.0]
        if len(recent) >= self.per_second:
            wait = max(wait, 1.0 - (now - recent[-self.per_second]))
        return wait

    def acquire(self) -> float:
        """Block until an order may be sent. Returns total seconds waited."""
        waited = 0.0
        with self._lock:
            while True:
                now = self._clock()
                wait = self._wait_time(now)
                if wait <= 0:
                    self._events.append(now)
                    return waited
                self._sleep(wait)
                waited += wait
