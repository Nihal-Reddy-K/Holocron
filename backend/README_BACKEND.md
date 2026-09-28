# Holocron Backend + AI

This adds the numerical movement pipeline and optional LLM explanation layer
around the existing Flask dashboard. The original `basic_stimulator.py` and
`templates/index.html` are retained.

## Pipeline

```text
POST /sensor
      ↓
5-second timestamp-aware buffer
      ↓
gravity removal + preprocessing
      ↓
interpretable feature extraction
      ↓
prototype Movement Index (0-100)
      ↓
personal baseline from prior sessions
      ↓
synthetic-data prototype pattern classifier
      ↓
structured result
      ↓
optional LLM explanation
```

The numerical pipeline works without an AI API key.

## Run

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

pip install -r requirements.txt
python app.py
```

Open the existing dashboard at http://127.0.0.1:5000/

## Optional AI

Copy `.env.example` to `.env` and set a server-side key:

```text
AI_PROVIDER=openai
AI_MODEL=gpt-5.6-luna
AI_API_KEY=...
```

Never put the key in frontend JavaScript.

Without a key, `GET /insight` returns a deterministic local fallback.

## API

### Sensor

```http
POST /sensor
Content-Type: application/json

{
  "timestamp": 1750000000.123,
  "x": 0.12,
  "y": 0.03,
  "z": 0.98,
  "sleep_hours": 6.5,
  "stress": "high"
}
```

### Current features

`GET /features`

### Current personal baseline

`GET /baseline`

### Dashboard compatibility

`GET /movement`

Returns the current Movement Index and `stimulation: false`.
The backend never controls stimulation hardware.

### AI explanation

`GET /insight`

or:

```http
POST /insight
Content-Type: application/json

{"sleep_hours": 6.5, "stress": "high"}
```

### Save longitudinal session

`POST /session`

Optional context:

```json
{
  "duration": 5,
  "sleep_hours": 6.5,
  "meals": 3,
  "stress": "high"
}
```

### History

`GET /history?limit=30`

## Tests

```bash
python test_signal.py
```

The ML classifier is trained on synthetic demonstration distributions at
startup. No clinical accuracy or validation claim is made.

## Hardware-free backend demo

With Flask running, use `python demo_sensor.py` to stream synthetic timestamped accelerometer samples into `/sensor`. This does not control stimulation hardware.
