"""Minimal automated checks for the numerical pipeline."""
import math
import numpy as np

from signal_processing import SensorSample, extract_features, movement_index, feature_vector
from movement_buffer import MovementBuffer
from baseline import calculate_baseline
from ml_model import MovementPatternModel


def make_samples(seconds=5, hz=50, amplitude=0.12):
    out = []
    for i in range(int(seconds * hz)):
        t = i / hz
        signal = amplitude * math.sin(2 * math.pi * 4 * t)
        out.append(SensorSample(t, signal, 0.0, 1.0))
    return out


def test_buffer_window():
    buf = MovementBuffer(window_seconds=5)
    for i in range(400):
        buf.append(SensorSample(i / 50, 0, 0, 1))
    window = buf.get_current_window()
    assert window
    assert window[-1].timestamp - window[0].timestamp <= 5.01


def test_feature_extraction():
    features = extract_features(make_samples())
    assert features["sample_count"] > 100
    assert features["sample_rate_hz"] > 40
    assert features["rms"] >= 0
    assert 0 <= features["spectral_entropy"] <= 1


def test_movement_index():
    features = extract_features(make_samples(amplitude=0.2))
    score = movement_index(features)
    assert 0 <= score <= 100
    assert len(feature_vector(features)) == 10


def test_baseline():
    result = calculate_baseline([20, 30, 40], 35)
    assert result["baseline"] == 30
    assert result["difference"] == 5
    assert result["baseline_ready"] is True


def test_ml_prediction():
    model = MovementPatternModel()
    result = model.predict([0.05, 0.003, 0.1, 1.5, 0.3, 0.1, 0.3, 0.5, 0.4, 0.1])
    assert result.pattern in {"near_baseline", "above_baseline", "below_baseline", "irregular_pattern"}


if __name__ == "__main__":
    for fn in [
        test_buffer_window,
        test_feature_extraction,
        test_movement_index,
        test_baseline,
        test_ml_prediction,
    ]:
        fn()
    print("All Holocron backend tests passed.")
