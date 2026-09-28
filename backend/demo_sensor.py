"""Hardware-free client for exercising Holocron /sensor.

Run the Flask server first:
    python app.py

Then in another terminal:
    python demo_sensor.py
"""
from __future__ import annotations

import math
import time
import urllib.request
import json
import sys

URL = "http://127.0.0.1:5000/sensor"


def post(payload):
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=3) as response:
        return json.loads(response.read().decode("utf-8"))


def main():
    hz = 50
    seconds = 6
    start = time.time()

    print("Sending simulated accelerometer data...")
    for i in range(hz * seconds):
        t = i / hz
        # z≈1g + two small movement components; intentionally synthetic.
        x = 0.10 * math.sin(2 * math.pi * 4.0 * t)
        y = 0.06 * math.sin(2 * math.pi * 7.0 * t + 0.7)
        z = 1.0 + 0.04 * math.sin(2 * math.pi * 2.0 * t)
        result = post({
            "timestamp": start + t,
            "x": x,
            "y": y,
            "z": z,
            "sleep_hours": 6.5,
            "stress": "high",
        })
        if i % hz == 0:
            print(
                f"t={t:4.1f}s  "
                f"Movement Index={result['movement_index']:5.1f}  "
                f"Pattern={result['pattern']['pattern']}"
            )
    print("\nDone. Try:")
    print("  GET http://127.0.0.1:5000/features")
    print("  GET http://127.0.0.1:5000/baseline")
    print("  GET http://127.0.0.1:5000/insight")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Could not reach Flask at {URL}: {exc}", file=sys.stderr)
        sys.exit(1)
