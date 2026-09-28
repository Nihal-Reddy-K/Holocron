from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta, timezone

from app.database import get_db
from app import models

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard & Clinician Views"])

# --- 1. Latest Result Endpoint ---
@router.get("/patient/{patient_id}/latest-result")
async def get_latest_result(patient_id: int, db: AsyncSession = Depends(get_db)):
    """Returns the most recent movement score alongside its contextual data."""
    # Fetch the newest session with a calculated score
    result = await db.execute(
        select(models.MovementSession)
        .where(models.MovementSession.patient_id == patient_id)
        .where(models.MovementSession.movement_score.isnot(None))
        .order_by(models.MovementSession.timestamp.desc())
        .limit(1)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="No completed sessions found for this patient.")

    # Fetch the linked context
    context_result = await db.execute(
        select(models.ContextCheckIn).where(models.ContextCheckIn.session_id == session.id)
    )
    context = context_result.scalar_one_or_none()

    return {
        "session_id": session.id,
        "date": session.timestamp,
        "movement_score": session.movement_score,
        "context": {
            "medication_status": context.medication_status if context else "Unknown",
            "sleep_hours": context.sleep_hours if context else 0,
            "stress_level": context.stress_level if context else "Unknown"
        }
    }

# --- 2. 30-Day Trend Endpoint ---
@router.get("/patient/{patient_id}/30-day-trend")
async def get_30_day_trend(patient_id: int, db: AsyncSession = Depends(get_db)):
    """Queries the last 30 days of scores, grouped by day, with trend direction."""
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    
    result = await db.execute(
        select(models.MovementSession)
        .where(models.MovementSession.patient_id == patient_id)
        .where(models.MovementSession.timestamp >= thirty_days_ago)
        .where(models.MovementSession.movement_score.isnot(None))
        .order_by(models.MovementSession.timestamp.asc())
    )
    sessions = result.scalars().all()

    # Group scores by date
    daily_scores = {}
    for s in sessions:
        date_str = s.timestamp.strftime("%Y-%m-%d")
        if date_str not in daily_scores:
            daily_scores[date_str] = []
        daily_scores[date_str].append(s.movement_score)

    # Calculate average per day and trend
    trend_data = []
    previous_score = None

    for date_str, scores in daily_scores.items():
        avg_score = sum(scores) / len(scores)
        
        # Determine trend direction
        direction = "stable"
        if previous_score is not None:
            if avg_score > previous_score + 2.0:
                direction = "up"
            elif avg_score < previous_score - 2.0:
                direction = "down"
                
        trend_data.append({
            "date": date_str,
            "score": round(avg_score, 1),
            "trend_direction": direction
        })
        previous_score = avg_score

    return trend_data

# --- 3. Clinician Overview Endpoint ---
@router.get("/clinician/patients-overview")
async def get_patients_overview(db: AsyncSession = Depends(get_db)):
    """Returns all patients with latest score, past week delta, and significant change flags."""
    patients_result = await db.execute(select(models.Patient))
    patients = patients_result.scalars().all()
    
    overview = []
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    two_weeks_ago = datetime.now(timezone.utc) - timedelta(days=14)

    for p in patients:
        # Get latest score
        latest_res = await db.execute(
            select(models.MovementSession)
            .where(models.MovementSession.patient_id == p.id)
            .where(models.MovementSession.movement_score.isnot(None))
            .order_by(models.MovementSession.timestamp.desc())
            .limit(1)
        )
        latest = latest_res.scalar_one_or_none()
        if not latest:
            continue

        # Get average score from the previous week (7-14 days ago) to serve as a baseline
        past_res = await db.execute(
            select(models.MovementSession)
            .where(models.MovementSession.patient_id == p.id)
            .where(models.MovementSession.timestamp >= two_weeks_ago)
            .where(models.MovementSession.timestamp < week_ago)
            .where(models.MovementSession.movement_score.isnot(None))
        )
        past_sessions = past_res.scalars().all()
        
        delta = 0.0
        flag = False
        
        if past_sessions:
            past_avg = sum(s.movement_score for s in past_sessions) / len(past_sessions)
            delta = latest.movement_score - past_avg
            # Flag if the movement score jumped by more than 10 points (indicating severe worsening)
            if delta >= 10.0 or delta <= -10.0:
                flag = True

        overview.append({
            "patient_id": p.id,
            "name": p.name,
            "latest_score": latest.movement_score,
            "delta_from_last_week": round(delta, 1),
            "significant_change_flag": flag
        })

    return overview