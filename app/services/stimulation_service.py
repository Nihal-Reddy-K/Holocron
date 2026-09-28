from sqlalchemy.ext.asyncio import AsyncSession
from app import models

async def generate_comparison_report(stimulation_log_id: int, db: AsyncSession):
    """
    Calculates the percentage change in the movement score before and after stimulation.
    Lower scores indicate less chorea/tremor, meaning a negative percentage is an improvement.
    """
    # 1. Fetch the stimulation log
    log = await db.get(models.StimulationLog, stimulation_log_id)
    if not log:
        return {"error": "Stimulation log not found."}
    
    if not log.before_session_id or not log.after_session_id:
        return {"error": "Both a 'before' and 'after' session are required to generate a report."}

    # 2. Fetch the corresponding movement sessions
    before_session = await db.get(models.MovementSession, log.before_session_id)
    after_session = await db.get(models.MovementSession, log.after_session_id)

    before_score = before_session.movement_score if before_session else None
    after_score = after_session.movement_score if after_session else None

    if before_score is None or after_score is None:
        return {"error": "One or both session scores are still calculating or missing."}

    # 3. Calculate percentage change
    if before_score > 0:
        change_percent = ((after_score - before_score) / before_score) * 100
    else:
        change_percent = 0.0

    # Determine clinical effectiveness
    if change_percent <= -5.0:
        effectiveness = "Improved (Reduced Chorea/Tremor)"
    elif change_percent >= 5.0:
        effectiveness = "Worsened"
    else:
        effectiveness = "Unchanged / Stable"

    return {
        "stimulation_log_id": log.id,
        "patient_id": log.patient_id,
        "before_score": before_score,
        "after_score": after_score,
        "percentage_change": round(change_percent, 2),
        "effectiveness": effectiveness,
        "stimulation_parameters": log.stimulation_parameters
    }