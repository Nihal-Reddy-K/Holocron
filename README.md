# NeuroTrack API Backend (Role 3)

This is the FastAPI backend for the NeuroTrack MVP. It handles data ingestion from the mobile sensors, calculates the movement score via background tasks, and provides the dashboard endpoints for the frontend.

## How to Run the Server locally
1. Activate the virtual environment: `.\venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
2. Install requirements (if not already installed): `pip install fastapi uvicorn sqlalchemy aiosqlite pydantic greenlet`
3. Start the server: `uvicorn app.main:app --reload`
4. View the interactive API Docs (Swagger): http://127.0.0.1:8000/docs

---

## 📱 Integration Guide for Role 1 (Movement & Sensors)
Your mobile app/wearable needs to collect the ~30s stillness data and ~20s tapping data. 
* **Where to send it:** `POST /api/v1/sessions/`
* **Format:** Send a single JSON payload containing the `patient_id`, contextual check-in data, and the arrays of accelerometer/gyroscope readings. Check the Swagger UI (`/docs`) for the exact JSON schema.
* **Note:** The API will return a `session_id` immediately so the UI doesn't freeze while the background task calculates the score.

## 🖥️ Integration Guide for Role 4 (Frontend & Clinical UX)
CORS is fully enabled for all origins (`*`). You can make Axios/Fetch requests directly to `http://127.0.0.1:8000`.
* **Create a Patient:** `POST /patients/`
* **Get Latest Test Score:** `GET /api/v1/dashboard/patient/{patient_id}/latest-result`
* **Get Graph Data:** `GET /api/v1/dashboard/patient/{patient_id}/30-day-trend` (Returns pre-formatted `{date, score, trend}` arrays for Recharts/Chart.js).
* **Poll for Score:** If you just submitted a new test, wait 2 seconds and poll `GET /api/v1/sessions/{session_id}/score` to get the background-calculated result.

## 🧠 Integration Guide for Role 2 (Neuro & Stimulation)
The stimulation logic evaluates the baseline movement score and triggers the hardware response.
* **Trigger Endpoint:** `POST /api/v1/stimulation/evaluate-and-trigger`
* **Log Secondary Test:** `POST /api/v1/stimulation/log-after-session`
* **Get Clinical Report:** `GET /api/v1/stimulation/report/{stimulation_log_id}` (Calculates the % change in the movement score before and after stimulation).