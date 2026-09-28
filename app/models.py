from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    baseline_info = Column(JSON, nullable=True)

    sessions = relationship("MovementSession", back_populates="patient")
    stimulation_logs = relationship("StimulationLog", back_populates="patient")


class MovementSession(Base):
    __tablename__ = "movement_sessions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    session_type = Column(String) # e.g., "Chorea Meter Baseline"
    movement_score = Column(Float, nullable=True)

    patient = relationship("Patient", back_populates="sessions")
    check_in = relationship("ContextCheckIn", back_populates="session", uselist=False)
    sensor_data = relationship("SensorData", back_populates="session")


class ContextCheckIn(Base):
    __tablename__ = "context_check_ins"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("movement_sessions.id"), unique=True)
    medication_status = Column(String)
    sleep_hours = Column(Float)
    stress_level = Column(String)

    session = relationship("MovementSession", back_populates="check_in")


class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("movement_sessions.id"))
    phase = Column(String) # "stillness" or "tapping"
    
    accelerometer_x = Column(Float)
    accelerometer_y = Column(Float)
    accelerometer_z = Column(Float)
    
    gyroscope_x = Column(Float)
    gyroscope_y = Column(Float)
    gyroscope_z = Column(Float)
    
    touchscreen_data = Column(JSON, nullable=True) # Stores tapping behavior, timing, and missed taps

    session = relationship("MovementSession", back_populates="sensor_data")


class StimulationLog(Base):
    __tablename__ = "stimulation_logs"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    stimulation_parameters = Column(JSON)
    
    before_session_id = Column(Integer, ForeignKey("movement_sessions.id"), nullable=True)
    after_session_id = Column(Integer, ForeignKey("movement_sessions.id"), nullable=True)

    patient = relationship("Patient", back_populates="stimulation_logs")