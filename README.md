# Holocron

Holocron is a research and hackathon prototype for smartphone-based movement monitoring and analysis.

The project combines a React/Vite frontend with a Python/Flask backend for movement signal processing, feature extraction, personal baseline analysis, machine-learning movement-pattern classification, and optional AI interpretation.

> Important: Holocron is a research/demo prototype. It is not a medical diagnostic, treatment, or clinical decision-making device.

## Architecture

Sensor / Demo Sensor
        |
        v
5-Second Buffer
        |
        v
Signal Preprocessing
        |
        v
Feature Extraction
        |
        v
Movement Index
        |
        v
Personal Baseline
        |
        v
ML Pattern Detection
        |
        v
AI Interpretation
        |
        v
React Dashboard

## Project Structure

Holocron/
├── backend/
│   ├── app.py
│   ├── signal_processing.py
│   ├── movement_buffer.py
│   ├── baseline.py
│   ├── ml_model.py
│   ├── ai_service.py
│   ├── basic_stimulator.py
│   ├── demo_sensor.py
│   ├── test_signal.py
│   ├── requirements.txt
│   ├── .env.example
│   └── data/
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.js
│   └── ...
│
└── README.md

## Backend

The Flask backend handles:

- Sensor ingestion
- Timestamp-aware movement buffering
- Signal preprocessing
- Feature extraction
- Movement Index calculation
- Personal baseline calculation
- ML movement-pattern classification
- Session/history data
- Optional AI interpretation

### Main API Endpoints

POST /sensor
GET  /movement
GET  /features
GET  /baseline
GET  /insight
GET  /history

## Frontend

The React/Vite frontend provides:

- Live movement visualization
- Movement Index
- Personal baseline
- Change from baseline
- ML movement pattern
- AI insight
- Session/history views
- Reports
- Simulated stimulation visualization

The frontend communicates with the Flask backend through the development API proxy.

## Setup

### 1. Start the Backend

Open a terminal in the project root:

cd backend

Create a Python virtual environment:

python -m venv .venv

Windows:

.venv\Scripts\activate

macOS/Linux:

source .venv/bin/activate

Install dependencies:

pip install -r requirements.txt

### 2. Configure the AI

Inside the backend directory, copy:

.env.example

to:

.env

Configure the file:

AI_PROVIDER=openai
AI_MODEL=gpt-5-mini
AI_API_KEY=YOUR_API_KEY

Replace YOUR_API_KEY with your OpenAI API key.

Never commit or share .env.

The API key must remain on the backend and must never be placed in frontend code.

If no API key is available, the numerical movement pipeline still works and the backend can use its local fallback insight.

### 3. Test the Backend

Run:

python test_signal.py

The backend tests should pass before continuing.

### 4. Start the Backend

Run:

python app.py

The Flask backend runs locally at:

http://127.0.0.1:5000

Keep this terminal running.

## Frontend Setup

Open a second terminal.

From the project root:

cd frontend

Install dependencies:

npm install

Start the development server:

npm run dev

Vite will display a local URL, normally:

http://localhost:5173

Open that URL in a browser.

The Vite development proxy forwards API requests to the Flask backend.

## Demo Without Hardware

The project includes a simulated movement sensor for development and demonstration.

Open Movement in the UI and select Start Demo.

The simulated sensor sends timestamped accelerometer samples to the Flask backend.

The complete pipeline is:

Simulated Sensor
       |
       v
5-Second Buffer
       |
       v
Signal Processing
       |
       v
Feature Extraction
       |
       v
Movement Index
       |
       v
Personal Baseline
       |
       v
ML Pattern
       |
       v
Optional AI Insight
       |
       v
Dashboard

This allows the complete system to be demonstrated without a physical smartphone or wearable sensor.

## Movement Index

The Movement Index is a prototype movement metric designed to provide a consistent numerical representation of movement characteristics.

It is not a clinical score and should not be interpreted as a measurement of disease severity.

The system compares the current movement measurement with the individual's personal baseline rather than relying only on universal thresholds.

## Machine Learning

The ML layer operates on structured movement features rather than raw natural-language input.

Example movement-pattern outputs include:

- NEAR BASELINE
- ABOVE BASELINE
- BELOW BASELINE
- IRREGULAR PATTERN

These represent movement patterns and are not medical diagnoses.

Synthetic data may be used for demonstration and development. No clinical accuracy or validation claims are made.

## AI Interpretation

The AI layer receives structured movement results such as:

- Current Movement Index
- Personal baseline
- Relative change
- Movement features
- User-provided contextual information

The AI is an interpretation layer and does not directly analyze raw accelerometer streams.

It is designed to:

- Explain supplied measurements
- Use cautious language
- Distinguish measured data from self-reported context
- Avoid unsupported conclusions

The AI must not:

- Diagnose medical conditions
- Claim disease progression from a single session
- Infer causality
- Recommend medication changes
- Claim treatment efficacy
- Control real stimulation hardware

## Testing

Before running the full application:

cd backend
python test_signal.py

The numerical pipeline should continue to function even if the AI service is unavailable.

The system should therefore still support:

Sensor
  |
  v
Processing
  |
  v
Features
  |
  v
Movement Index
  |
  v
Baseline
  |
  v
ML Pattern

without requiring an LLM.

## Simulated Stimulation

Holocron includes a software-only stimulation simulation for demonstration purposes.

It does not:

- Control real stimulation hardware
- Send electrical signals
- Claim therapeutic efficacy
- Provide treatment recommendations

The stimulation component is isolated from the real sensor and analysis pipeline.

## Security

Never commit sensitive credentials to the repository.

Do not commit:

- .env
- API keys
- Passwords
- Private credentials

The repository should contain .env.example, but not the real .env.

Development environments such as:

- backend/.venv/
- frontend/node_modules/

should also not be committed.

## Quick Start

### Terminal 1 — Backend

cd backend

python -m venv .venv

Windows:

.venv\Scripts\activate

macOS/Linux:

source .venv/bin/activate

Then:

pip install -r requirements.txt
python test_signal.py
python app.py

### Terminal 2 — Frontend

cd frontend
npm install
npm run dev

Open the Vite URL shown in the terminal.

Then open Movement and select Start Demo to test the complete pipeline.

## Technology Stack

### Frontend

- React
- Vite
- JavaScript
- CSS

### Backend

- Python
- Flask
- NumPy
- Signal processing
- Machine learning

### AI

- Server-side LLM integration
- Structured movement-result interpretation

### Development

- Git/GitHub
- Simulated sensor data
- Local development environment

## Project Goal

Holocron demonstrates how a short, repeatable movement session can be transformed into structured information that can be compared against an individual's own historical baseline.

The goal is to provide additional quantitative movement information between clinical visits while keeping the prototype transparent, modular, and extensible.

## Disclaimer

Holocron is a research and hackathon prototype. It is not a medical device, diagnostic system, treatment system, or substitute for professional medical evaluation.

Movement metrics, ML classifications, AI interpretations, and simulated intervention responses are experimental and should not be interpreted as clinical conclusions.
