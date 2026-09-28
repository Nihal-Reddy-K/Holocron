from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel

from app.database import get_db
from app import models
from app.services.signal_processing_service import calculate_movement_score

router = APIRouter(prefix="/api/v1/sessions", tags=["Sessions"])

# --- Incoming Payload Schemas ---
class BulkSensorData(BaseModel):
    accelerometer_x: float = 0.0
    accelerometer_y: float = 0.0
    accelerometer_z: float = 0.0
    gyroscope_x: float = 0.0
    gyroscope_y: float = 0.0
    gyroscope_z: float = 0.0
    touchscreen_data: Optional[Dict[str, Any]] = None

class SessionIngestionPayload(BaseModel):
    patient_id: int
    timestamp: Optional[datetime] = None
    medication_status: str
    sleep_hours: float
    stress_level: str
    stillness_phase_data: List[BulkSensorData]
    tapping_phase_data: List[BulkSensorData]

# --- POST Endpoint: Ingest Data & Trigger Background Task ---
@router.post("/")
async def submit_session_data(
    payload: SessionIngestionPayload, 
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    # 1. Create the Movement Session (Score is empty at first)
    new_session = models.MovementSession(
        patient_id=payload.patient_id,
        session_type="Chorea Meter Full Test",
        timestamp=payload.timestamp or datetime.now(timezone.utc)
    )
    db.add(new_session)
    await db.flush() 

    # 2. Save the Contextual Check-In
    new_context = models.ContextCheckIn(
        session_id=new_session.id,
        medication_status=payload.medication_status,
        sleep_hours=payload.sleep_hours,
        stress_level=payload.stress_level
    )
    db.add(new_context)

    # 3. Save the Sensor Data
    sensor_records = []
    for data in payload.stillness_phase_data:
        sensor_records.append(models.SensorData(session_id=new_session.id, phase="stillness", **data.model_dump()))
    for data in payload.tapping_phase_data:
        sensor_records.append(models.SensorData(session_id=new_session.id, phase="tapping", **data.model_dump()))

    db.add_all(sensor_records)
    await db.commit()

    # --- Trigger the Brain ---
    # This runs the heavy math AFTER the response is already sent to the phone
    background_tasks.add_task(calculate_movement_score, new_session.id)

    # Return immediately
    return {
        "message": "Data ingested successfully. Movement score is calculating in the background.",
        "session_id": new_session.id
    }

# --- GET Endpoint: Check the Calculated Score ---
@router.get("/{session_id}/score")
async def get_session_score(session_id: int, db: AsyncSession = Depends(get_db)):
    """Allows the frontend to fetch the calculated score after the background task finishes."""
    session = await db.get(models.MovementSession, session_id)
    if not session:
        return {"error": "Session not found"}
    
    return {
        "session_id": session.id,
        "movement_score": session.movement_score,
        "status": "Calculating..." if session.movement_score is None else "Complete"
    }