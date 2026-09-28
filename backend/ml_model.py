"""Prototype movement-pattern model.

The model is trained from synthetic demonstration data only. It is not a
clinical model and no performance claim is made.
"""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np

FEATURE_NAMES = [
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


@dataclass
class PatternResult:
    pattern: str
    confidence: float | None
    model: str
    synthetic_demo_model: bool

    def to_dict(self):
        return {
            "pattern": self.pattern,
            "confidence": self.confidence,
            "model": self.model,
            "synthetic_demo_model": self.synthetic_demo_model,
        }


class MovementPatternModel:
    """
    Small Decision Tree trained on generated feature vectors.

    We deliberately train it at runtime from synthetic distributions so the
    project has no hidden binary/model artifact and remains easy to inspect.
    """
    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.model = None
        self._fit()

    def _fit(self):
        try:
            from sklearn.tree import DecisionTreeClassifier
        except ImportError:
            self.model = None
            return

        rng = np.random.default_rng(self.random_state)
        rows, labels = [], []

        def add(label, n, rms, variance, peak, freq, entropy, band, jerk, events, ac, zcr):
            for _ in range(n):
                vals = [
                    max(0, rng.normal(rms[0], rms[1])),
                    max(0, rng.normal(variance[0], variance[1])),
                    max(0, rng.normal(peak[0], peak[1])),
                    max(0, rng.normal(freq[0], freq[1])),
                    np.clip(rng.normal(entropy[0], entropy[1]), 0, 1),
                    np.clip(rng.normal(band[0], band[1]), 0, 1),
                    max(0, rng.normal(jerk[0], jerk[1])),
                    max(0, rng.normal(events[0], events[1])),
                    np.clip(rng.normal(ac[0], ac[1]), -1, 1),
                    np.clip(rng.normal(zcr[0], zcr[1]), 0, 1),
                ]
                rows.append(vals)
                labels.append(label)

        add("near_baseline", 250, (0.05,.015),(.003,.002),(.10,.03),(1.5,.8),(.35,.12),(.12,.08),(.35,.15),(.7,.3),(.35,.2),(.12,.05))
        add("above_baseline", 250, (0.18,.04),(.03,.015),(.35,.08),(2.5,1.2),(.45,.12),(.28,.12),(.9,.3),(1.8,.5),(.25,.2),(.22,.07))
        add("below_baseline", 250, (0.025,.01),(.001,.001),(.06,.02),(1.2,.7),(.30,.12),(.08,.05),(.18,.08),(.3,.2),(.45,.2),(.08,.04))
        add("irregular_pattern", 250, (0.14,.05),(.025,.018),(.30,.10),(3.5,1.8),(.82,.08),(.45,.15),(1.4,.5),(2.4,.8),(.05,.18),(.40,.10))

        self.model = DecisionTreeClassifier(max_depth=5, random_state=self.random_state)
        self.model.fit(np.asarray(rows), np.asarray(labels))

    def predict(self, vector: list[float]) -> PatternResult:
        if self.model is None:
            # Dependency-free fallback. This is explicitly a heuristic.
            rms = float(vector[0])
            entropy = float(vector[4])
            if entropy > 0.72:
                pattern = "irregular_pattern"
            elif rms > 0.15:
                pattern = "above_baseline"
            elif rms < 0.04:
                pattern = "below_baseline"
            else:
                pattern = "near_baseline"
            return PatternResult(pattern, None, "heuristic_fallback", True)

        x = np.asarray(vector, dtype=float).reshape(1, -1)
        pattern = str(self.model.predict(x)[0])
        probabilities = self.model.predict_proba(x)[0]
        confidence = float(np.max(probabilities))
        return PatternResult(pattern, round(confidence, 3), "synthetic_decision_tree", True)
