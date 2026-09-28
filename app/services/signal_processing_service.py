from sqlalchemy.future import select
from app import models
from app.database import AsyncSessionLocal

async def calculate_movement_score(session_id: int):
    """
    Background task: Retrieves raw data, extracts features, and updates the score.
    """
    # Open a fresh background database connection
    async with AsyncSessionLocal() as db:
        # 1. Retrieve the session
        session = await db.get(models.MovementSession, session_id)
        if not session:
            return

        # 2. Retrieve all raw sensor data for this session
        result = await db.execute(
            select(models.SensorData).where(models.SensorData.session_id == session_id)
        )
        sensor_data = result.scalars().all()

        # Separate the phases
        stillness_data = [d for d in sensor_data if d.phase == "stillness"]
        tapping_data = [d for d in sensor_data if d.phase == "tapping"]

        # --- MOCK SIGNAL PROCESSING PIPELINE ---
        
        # Step A: Filtering & Preprocessing
        # (In a real app, you'd apply a low-pass filter here to remove device noise)
        
        # Step B: Feature Extraction
        amplitude = 0.0
        if stillness_data:
            # Calculate mock movement variability/amplitude
            total_movement = sum(
                abs(d.accelerometer_x) + abs(d.accelerometer_y) + abs(d.accelerometer_z)
                for d in stillness_data
            )
            amplitude = total_movement / len(stillness_data)
        
        tapping_speed = 0.0
        if tapping_data:
            # Mock tapping speed based on the density of the sensor data
            tapping_speed = len(tapping_data) * 0.5 

        # Step C: Rule-Based Scoring Algorithm
        # Higher amplitude = higher score (more chorea/tremor)
        # Lower tapping speed = higher score (more impairment)
        raw_score = (amplitude * 40.0) + (max(0, 20.0 - tapping_speed) * 2.0)
        
        # Normalize to an integer between 0 and 100
        final_score = int(min(100, max(0, raw_score)))

        # 3. Save the calculated score back to the database
        session.movement_score = final_score
        await db.commit()