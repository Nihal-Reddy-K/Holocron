"""
Holocron signal processing and feature extraction.

This module is deliberately independent of Flask and the LLM. It accepts
timestamped accelerometer samples and returns interpretable numerical
features plus the prototype Movement Index.

Prototype/research code only; not a clinical chorea score or diagnostic tool.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Iterable, Sequence
import math
import numpy as np


@dataclass
class SensorSample:
    timestamp: float
    x: float
    y: float
    z: float

    @classmethod
    def from_dict(cls, data: dict) -> "SensorSample":
        return cls(
            timestamp=float(data["timestamp"]),
            x=float(data["x"]),
            y=float(data["y"]),
            z=float(data["z"]),
        )

    def to_dict(self) -> dict:
        return asdict(self)


def _clean_samples(samples: Iterable[SensorSample | dict]) -> list[SensorSample]:
    cleaned = []
    for item in samples:
        sample = item if isinstance(item, SensorSample) else SensorSample.from_dict(item)
        values = (sample.timestamp, sample.x, sample.y, sample.z)
        if all(math.isfinite(v) for v in values):
            cleaned.append(sample)
    cleaned.sort(key=lambda s: s.timestamp)
    return cleaned


def sample_rate(samples: Sequence[SensorSample | dict]) -> float:
    cleaned = _clean_samples(samples)
    if len(cleaned) < 2:
        return 0.0
    dt = np.diff([s.timestamp for s in cleaned])
    dt = dt[dt > 1e-6]
    if len(dt) == 0:
        return 0.0
    return float(1.0 / np.median(dt))


def movement_magnitude(x, y, z):
    """Euclidean acceleration magnitude."""
    return np.sqrt(np.asarray(x) ** 2 + np.asarray(y) ** 2 + np.asarray(z) ** 2)


def remove_gravity(samples: Sequence[SensorSample | dict], gravity_tau: float = 0.50):
    """
    Estimate gravity with an EMA and return the magnitude of dynamic
    acceleration. The time constant is timestamp-aware, so irregular sampling
    is tolerated.
    """
    cleaned = _clean_samples(samples)
    if not cleaned:
        return np.array([]), np.array([])

    dynamic_vectors = []
    gravity = np.array([0.0, 0.0, 1.0], dtype=float)

    previous_t = cleaned[0].timestamp
    for sample in cleaned:
        dt = max(0.0, sample.timestamp - previous_t)
        alpha = 1.0 - math.exp(-dt / max(gravity_tau, 1e-3)) if dt > 0 else 0.02
        vector = np.array([sample.x, sample.y, sample.z], dtype=float)
        gravity = (1.0 - alpha) * gravity + alpha * vector
        dynamic_vectors.append(vector - gravity)
        previous_t = sample.timestamp

    dynamic = np.asarray(dynamic_vectors)
    magnitude = np.linalg.norm(dynamic, axis=1)
    timestamps = np.asarray([s.timestamp for s in cleaned])
    return timestamps, magnitude


def _uniform_signal(timestamps: np.ndarray, values: np.ndarray):
    if len(values) < 3:
        return timestamps, values
    duration = timestamps[-1] - timestamps[0]
    if duration <= 0:
        return timestamps, values
    rate = sample_rate([
        SensorSample(float(timestamps[i]), 0, 0, 0)
        for i in range(len(timestamps))
    ])
    rate = float(np.clip(rate if rate else 50.0, 20.0, 200.0))
    n = max(8, int(round(duration * rate)) + 1)
    uniform_t = np.linspace(timestamps[0], timestamps[-1], n)
    uniform_v = np.interp(uniform_t, timestamps, values)
    return uniform_t, uniform_v


def _spectral_features(timestamps: np.ndarray, signal: np.ndarray):
    if len(signal) < 8:
        return 0.0, 0.0, 0.0, 0.0

    t, y = _uniform_signal(timestamps, signal)
    if len(y) < 8:
        return 0.0, 0.0, 0.0, 0.0

    y = y - np.mean(y)
    duration = t[-1] - t[0]
    if duration <= 0:
        return 0.0, 0.0, 0.0, 0.0

    dt = np.median(np.diff(t))
    freqs = np.fft.rfftfreq(len(y), d=dt)
    power = np.abs(np.fft.rfft(y)) ** 2
    if len(power) > 0:
        power[0] = 0.0

    total = float(power.sum())
    if total <= 1e-12:
        return 0.0, 0.0, 0.0, 0.0

    dominant_frequency = float(freqs[int(np.argmax(power))])
    spectral_power = float(total / len(y))

    # Normalized Shannon entropy of the power spectrum.
    p = power / total
    p = p[p > 0]
    entropy = float(-(p * np.log(p)).sum() / max(np.log(len(power)), 1e-9))

    band = (freqs >= 3.0) & (freqs <= 8.0)
    band_energy = float(power[band].sum() / total)

    return dominant_frequency, spectral_power, entropy, band_energy


def _zero_crossing_rate(signal: np.ndarray) -> float:
    if len(signal) < 2:
        return 0.0
    centered = signal - np.mean(signal)
    return float(np.mean((centered[:-1] * centered[1:]) < 0))


def _autocorrelation(signal: np.ndarray) -> float:
    if len(signal) < 4:
        return 0.0
    x = signal - np.mean(signal)
    denom = float(np.dot(x, x))
    if denom <= 1e-12:
        return 0.0
    max_lag = min(len(x) // 2, 100)
    ac = [float(np.dot(x[:-lag], x[lag:]) / denom) for lag in range(1, max_lag)]
    return max(ac) if ac else 0.0


def extract_features(samples: Sequence[SensorSample | dict]) -> dict:
    """Return one interpretable, JSON-safe feature dictionary."""
    cleaned = _clean_samples(samples)
    if len(cleaned) < 3:
        return {
            "sample_count": len(cleaned),
            "duration_seconds": 0.0,
            "sample_rate_hz": 0.0,
            "mean": 0.0,
            "variance": 0.0,
            "std": 0.0,
            "rms": 0.0,
            "peak": 0.0,
            "peak_to_peak": 0.0,
            "zero_crossing_rate": 0.0,
            "dominant_frequency": 0.0,
            "spectral_power": 0.0,
            "spectral_entropy": 0.0,
            "band_energy_3_8hz": 0.0,
            "autocorrelation": 0.0,
            "jerk_rms": 0.0,
            "movement_event_rate": 0.0,
        }

    timestamps, movement = remove_gravity(cleaned)
    if len(movement) < 3:
        return extract_features([])

    centered = movement - np.mean(movement)
    duration = max(float(timestamps[-1] - timestamps[0]), 0.0)
    dt = np.diff(timestamps)
    dt = dt[dt > 1e-6]
    median_dt = float(np.median(dt)) if len(dt) else 0.0

    jerk = np.diff(movement) / median_dt if median_dt > 0 else np.zeros(1)
    jerk_rms = float(np.sqrt(np.mean(jerk ** 2))) if len(jerk) else 0.0

    # Adaptive event threshold keeps this a prototype movement-event detector,
    # rather than a fixed clinical threshold.
    threshold = max(float(np.mean(movement) + 1.5 * np.std(movement)), 0.03)
    events = np.sum((movement[1:] >= threshold) & (movement[:-1] < threshold))
    event_rate = float(events / duration) if duration > 0 else 0.0

    dominant_frequency, spectral_power, entropy, band_energy = _spectral_features(
        timestamps, centered
    )

    return {
        "sample_count": int(len(cleaned)),
        "duration_seconds": round(duration, 4),
        "sample_rate_hz": round(sample_rate(cleaned), 3),
        "mean": round(float(np.mean(movement)), 6),
        "variance": round(float(np.var(movement)), 6),
        "std": round(float(np.std(movement)), 6),
        "rms": round(float(np.sqrt(np.mean(movement ** 2))), 6),
        "peak": round(float(np.max(movement)), 6),
        "peak_to_peak": round(float(np.ptp(movement)), 6),
        "zero_crossing_rate": round(_zero_crossing_rate(centered), 6),
        "dominant_frequency": round(dominant_frequency, 4),
        "spectral_power": round(spectral_power, 8),
        "spectral_entropy": round(entropy, 6),
        "band_energy_3_8hz": round(band_energy, 6),
        "autocorrelation": round(_autocorrelation(centered), 6),
        "jerk_rms": round(jerk_rms, 6),
        "movement_event_rate": round(event_rate, 6),
    }


def movement_index(features: dict) -> float:
    """
    Deterministic prototype Movement Index (0-100).

    40% amplitude, 25% jerk, 20% movement-event rate, 15% irregularity.
    Thresholds are engineering/demo normalization constants, not clinical
    cutoffs.
    """
    amplitude = np.clip(float(features.get("rms", 0.0)) / 0.25, 0.0, 1.0)
    jerk = np.clip(float(features.get("jerk_rms", 0.0)) / 2.0, 0.0, 1.0)
    event_rate = np.clip(float(features.get("movement_event_rate", 0.0)) / 3.0, 0.0, 1.0)
    irregularity = np.clip(float(features.get("spectral_entropy", 0.0)), 0.0, 1.0)

    score = 100.0 * (
        0.40 * amplitude
        + 0.25 * jerk
        + 0.20 * event_rate
        + 0.15 * irregularity
    )
    return round(float(np.clip(score, 0.0, 100.0)), 2)


def feature_vector(features: dict) -> list[float]:
    """Stable ordered vector for ML; never pass arbitrary raw JSON to a model."""
    names = [
        "rms",
        "variance",
        "peak",
        "dominant_frequency",
        "spectral_entropy",
        "band_energy_3_8hz",
        "jerk_rms",
        "movement_event_rate",
        "autocorrelation",
        "zero_crossing_rate",
    ]
    return [float(features.get(name, 0.0)) for name in names]
