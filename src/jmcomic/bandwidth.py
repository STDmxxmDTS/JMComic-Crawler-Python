"""Thread-safe aggregate byte-rate limiting for image downloads."""

from __future__ import annotations

import threading
import time
from collections.abc import Callable

DEFAULT_DOWNLOAD_RATE = 3 * 1024 * 1024


class BandwidthLimiter:
    def __init__(
        self,
        rate: float,
        *,
        clock: Callable[[], float] = time.monotonic,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        self.rate = max(0.0, float(rate))
        self._clock = clock
        self._sleeper = sleeper
        self._next_at = clock()
        self._lock = threading.Lock()

    def consume(self, size: int) -> None:
        amount = max(0, int(size))
        if amount == 0 or self.rate <= 0:
            return
        with self._lock:
            now = self._clock()
            start = max(now, self._next_at)
            wait = start - now
            self._next_at = start + amount / self.rate
        if wait > 0:
            self._sleeper(wait)

    async def aconsume(self, size: int) -> None:
        import asyncio

        await asyncio.to_thread(self.consume, size)


_shared: dict[int, BandwidthLimiter] = {}
_shared_lock = threading.Lock()


def shared_bandwidth_limiter(rate: float) -> BandwidthLimiter:
    normalized = max(0, int(float(rate)))
    if normalized == 0:
        return BandwidthLimiter(0)
    with _shared_lock:
        limiter = _shared.get(normalized)
        if limiter is None:
            limiter = BandwidthLimiter(normalized)
            _shared[normalized] = limiter
        return limiter
