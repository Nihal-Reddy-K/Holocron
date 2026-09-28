# Frontend integration contract

The existing dashboard does not need to be rebuilt. A separate frontend can
call these Flask endpoints.

## Send one sensor sample

`POST http://127.0.0.1:5000/sensor`

```json
{
  "timestamp": 1750000000.123,
  "x": 0.12,
  "y": 0.03,
  "z": 0.98,
  "sleep_hours": 6.5,
  "meals": 3,
  "stress": "high"
}
```

The response contains:

```json
{
  "ok": true,
  "buffer_samples": 250,
  "window_seconds": 5.0,
  "movement_index": 37.2,
  "features": {},
  "baseline": {
    "baseline": 29.5,
    "baseline_std": 3.4,
    "current": 37.2,
    "difference": 7.7,
    "relative_change": 26.1,
    "baseline_ready": true,
    "sessions_used": 4
  },
  "pattern": {
    "pattern": "above_baseline",
    "confidence": 0.78,
    "model": "synthetic_decision_tree",
    "synthetic_demo_model": true
  }
}
```

## Dashboard polling

- `GET /movement` → lightweight live Movement Index
- `GET /features` → latest feature vector
- `GET /baseline` → baseline comparison
- `GET /insight` → concise AI/local interpretation
- `GET /history` → longitudinal session records

The backend has CORS enabled for the hackathon frontend.

## Important UI wording

Use:
- "Movement Index"
- "Personal Baseline"
- "Change from Baseline"
- "Detected Pattern"
- "AI Insight"

Do not label the Movement Index as a clinical chorea score, and do not present
the synthetic model confidence as clinical certainty.
