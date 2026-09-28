from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import asyncio

from app.database import get_db
from app import models
from app.services.stimulation_service import generate_comparison_report

router = APIRouter(prefix="/api/v1/stimulation", tags=["Stimulation & Closed-Loop"])

# --- Request Schemas ---
class EvaluateRequest(BaseModel):
    patient_id: int
    session_id: int

class LogAfterRequest(BaseModel):
    stimulation_log_id: int
    after_session_id: int

# --- Endpoints ---
@router.post("/evaluate-and-trigger")
async def evaluate_and_trigger(request: EvaluateRequest, db: AsyncSession = Depends(get_db)):
    # 1. Fetch the 'before' session
    session = await db.get(models.MovementSession, request.session_id)
    if not session or session.movement_score is None:
        raise HTTPException(status_code=400, detail="Session not found or score not yet calculated.")

    # 2. Set the clinical threshold (mocked at 50 for the MVP)
    chorea_threshold = 50.0 
    triggered = False
    new_log = None

    if session.movement_score >= chorea_threshold:
        # 3. Simulate sending an MQTT message or HTTP request to the device architecture
        print(f"⚡ SIMULATING NEURAL TRIGGER: Outbound signal sent for Patient {request.patient_id}")
        await asyncio.sleep(0.5) # Simulate network/hardware delay
        
        # 4. Log the stimulation event in the database
        new_log = models.StimulationLog(
            patient_id=request.patient_id,
            before_session_id=request.session_id,
            stimulation_parameters={"mode": "burst", "target": "STN", "intensity": "medium", "duration_sec": 300}
        )
        db.add(new_log)
        await db.commit()
        await db.refresh(new_log)
        triggered = True

    return {
        "evaluated_session_id": request.session_id,
        "movement_score": session.movement_score,
        "stimulation_triggered": triggered,
        "stimulation_log_id": new_log.id if new_log else None,
        "message": "Device triggered successfully." if triggered else "Score below threshold. No stimulation required."
    }

@router.post("/log-after-session")
async def log_after_session(request: LogAfterRequest, db: AsyncSession = Depends(get_db)):
    # Link the secondary "after" test to the original stimulation event
    log = await db.get(models.StimulationLog, request.stimulation_log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Stimulation log not found.")

    log.after_session_id = request.after_session_id
    await db.commit()

    return {
        "message": "Post-stimulation session successfully linked.",
        "stimulation_log_id": log.id,
        "after_session_id": log.after_session_id
    }

@router.get("/report/{stimulation_log_id}")
async def get_comparison_report(stimulation_log_id: int, db: AsyncSession = Depends(get_db)):
    # Generate the closed-loop tracking report
    report = await generate_comparison_report(stimulation_log_id, db)
    if "error" in report:
        raise HTTPException(status_code=400, detail=report["error"])
    return report