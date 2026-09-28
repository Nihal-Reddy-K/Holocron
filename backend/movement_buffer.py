"""Small timestamp-aware in-memory sensor buffer for Holocron."""
from __future__ import annotations

from collections import deque
from threading import Lock
from typing import Iterable
from signal_processing import SensorSample


class MovementBuffer:
    def __init__(self, window_seconds: float = 5.0, max_samples: int = 2000):
        self.window_seconds = float(window_seconds)
        self.samples = deque(maxlen=max_samples)
        self._lock = Lock()

    def append(self, sample: SensorSample | dict) -> int:
        item = sample if isinstance(sample, SensorSample) else SensorSample.from_dict(sample)
        with self._lock:
            self.samples.append(item)
            cutoff = item.timestamp - self.window_seconds
            while self.samples and self.samples[0].timestamp < cutoff:
                self.samples.popleft()
            return len(self.samples)

    def get_current_window(self) -> list[SensorSample]:
        with self._lock:
            return list(self.samples)

    def clear(self) -> None:
        with self._lock:
            self.samples.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self.samples)
