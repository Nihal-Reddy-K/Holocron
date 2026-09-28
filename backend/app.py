from __future__ import annotations

import time
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from dotenv import load_dotenv

from baseline import SessionStore, calculate_baseline
from ai_service import generate_insight
from ml_model import MovementPatternModel
from movement_buffer import MovementBuffer
from signal_processing import (
    SensorSample,
    extract_features,
    feature_vector,
    movement_index,
)

load_dotenv()

app = Flask(__name__)
# Needed when the separately hosted hackathon frontend calls Flask directly.
CORS(app, resources={r"/*": {"origins": "*"}})

buffer = MovementBuffer(window_seconds=5.0)
sessions = SessionStore(path="data/sessions.json")
pattern_model = MovementPatternModel()
latest_analysis: dict | None = None


def _context_from(payload: dict) -> dict:
    context = payload.get("context") or {}
    # Also accept the current dashboard's simple field names.
    for source, target in [
        ("sleep", "sleep_hours"),
        ("sleep_hours", "sleep_hours"),
        ("stress", "stress"),
        ("meals", "meals"),
    ]:
        if source in payload and target not in context:
            context[target] = payload[source]
    return context


def analyze_current_window(context: dict | None = None) -> dict:
    global latest_analysis

    window = buffer.get_current_window()
    features = extract_features(window)
    index = movement_index(features)
    baseline = calculate_baseline(sessions.recent_indices(10), index)
    pattern = pattern_model.predict(feature_vector(features)).to_dict()

    result = {
        "timestamp": time.time(),
        "window_seconds": 5.0,
        "sample_count": len(window),
        "features": features,
        "feature_vector": feature_vector(features),
        "movement_index": index,
        "baseline": baseline,
        "pattern": pattern,
        "context": context or {},
    }
    latest_analysis = result
    return result


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/sensor", methods=["POST"])
def sensor():
    """
    Ingest one timestamped accelerometer sample.

    Accepted payload:
      {"timestamp": 1234.5, "x": 0.12, "y": 0.03, "z": 0.98}

    timestamp is optional for local demo clients; server time is used if absent.
    """
    payload = request.get_json(silent=True) or {}
    try:
        sample = SensorSample(
            timestamp=float(payload.get("timestamp", time.time())),
            x=float(payload["x"]),
            y=float(payload["y"]),
            z=float(payload["z"]),
        )
        if not all(
            __import__("math").isfinite(v)
            for v in (sample.timestamp, sample.x, sample.y, sample.z)
        ):
            raise ValueError("sensor values must be finite")

        count = buffer.append(sample)
        analysis = analyze_current_window(_context_from(payload))

        return jsonify({
            "ok": True,
            "buffer_samples": count,
            "window_seconds": 5.0,
            "movement_index": analysis["movement_index"],
            "features": analysis["features"],
            "baseline": analysis["baseline"],
            "pattern": analysis["pattern"],
        })
    except (KeyError, TypeError, ValueError) as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.route("/features", methods=["GET"])
def features():
    analysis = latest_analysis or analyze_current_window()
    return jsonify({
        "features": analysis["features"],
        "feature_vector": analysis["feature_vector"],
        "movement_index": analysis["movement_index"],
        "sample_count": analysis["sample_count"],
        "window_seconds": analysis["window_seconds"],
    })


@app.route("/baseline", methods=["GET"])
def baseline():
    analysis = latest_analysis or analyze_current_window()
    return jsonify(analysis["baseline"])


@app.route("/movement", methods=["GET"])
def movement():
    """
    Compatibility endpoint for dashboards that poll once per second.

    'stimulation' remains false here because this numerical pipeline never
    controls stimulation hardware. The existing visual simulation remains
    isolated in the browser/basic_stimulator.py.
    """
    analysis = latest_analysis or analyze_current_window()
    return jsonify({
        "movement_index": analysis["movement_index"],
        "stimulation": False,
        "timestamp": time.time(),
        "pattern": analysis["pattern"]["pattern"],
    })


@app.route("/insight", methods=["GET", "POST"])
def insight():
    analysis = latest_analysis or analyze_current_window()
    if request.method == "POST":
        payload = request.get_json(silent=True) or {}
        if payload.get("context"):
            analysis = dict(analysis)
            analysis["context"] = _context_from(payload)
    return jsonify(generate_insight(analysis))


@app.route("/session", methods=["POST"])
def create_session():
    """
    Save the latest analyzed 5-second window as one longitudinal demo session.
    A real 30-second session can call this after aggregating its windows.
    """
    analysis = latest_analysis or analyze_current_window()
    payload = request.get_json(silent=True) or {}
    context = _context_from(payload) or analysis.get("context", {})

    record = sessions.add(
        features=analysis["features"],
        movement_index=analysis["movement_index"],
        duration=float(payload.get("duration", analysis["features"].get("duration_seconds", 0))),
        context=context,
    )
    # Recompute baseline after persistence so subsequent requests see the new history.
    analyze_current_window(context)
    return jsonify(record), 201


@app.route("/history", methods=["GET"])
def history():
    limit = request.args.get("limit", default=30, type=int)
    limit = max(1, min(limit, 200))
    return jsonify(sessions.all()[-limit:])


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "pipeline": ["sensor", "buffer", "preprocessing", "features", "movement_index", "baseline", "ml", "ai"],
        "ai_optional": True,
        "buffer_samples": len(buffer),
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
