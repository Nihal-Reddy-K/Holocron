"""Personal baseline and lightweight longitudinal session storage."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from statistics import median, pstdev
from threading import Lock
import json
import time
import uuid


@dataclass
class Session:
    session_id: str
    timestamp: float
    duration: float
    features: dict
    movement_index: float
    context: dict


class SessionStore:
    def __init__(self, path: str = "data/sessions.json", max_sessions: int = 200):
        self.path = Path(path)
        self.max_sessions = max_sessions
        self._lock = Lock()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def _load(self) -> list[dict]:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except (OSError, json.JSONDecodeError):
            return []

    def all(self) -> list[dict]:
        with self._lock:
            return self._load()

    def add(
        self,
        features: dict,
        movement_index: float,
        duration: float,
        context: dict | None = None,
        session_id: str | None = None,
        timestamp: float | None = None,
    ) -> dict:
        record = asdict(Session(
            session_id=session_id or f"demo_{uuid.uuid4().hex[:8]}",
            timestamp=float(timestamp if timestamp is not None else time.time()),
            duration=float(duration),
            features=features,
            movement_index=float(movement_index),
            context=context or {},
        ))
        with self._lock:
            data = self._load()
            data.append(record)
            data = data[-self.max_sessions:]
            tmp = self.path.with_suffix(".tmp")
            tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
            tmp.replace(self.path)
        return record

    def recent_indices(self, limit: int = 10) -> list[float]:
        records = self.all()
        return [float(r["movement_index"]) for r in records[-limit:]]


def calculate_baseline(previous_indices: list[float], current: float) -> dict:
    """
    Baseline is based only on prior sessions. With no prior history, the
    current session is reported as the provisional baseline and baseline_ready
    is false.
    """
    previous = [float(v) for v in previous_indices]
    if not previous:
        return {
            "baseline": round(float(current), 2),
            "baseline_std": 0.0,
            "current": round(float(current), 2),
            "difference": 0.0,
            "relative_change": 0.0,
            "baseline_ready": False,
            "sessions_used": 0,
        }

    baseline = float(median(previous))
    std = float(pstdev(previous)) if len(previous) > 1 else 0.0
    difference = float(current - baseline)
    relative = (difference / baseline * 100.0) if abs(baseline) > 1e-9 else 0.0

    return {
        "baseline": round(baseline, 2),
        "baseline_std": round(std, 2),
        "current": round(float(current), 2),
        "difference": round(difference, 2),
        "relative_change": round(relative, 2),
        "baseline_ready": len(previous) >= 2,
        "sessions_used": len(previous),
    }
