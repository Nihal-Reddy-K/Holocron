from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any
from datetime import datetime

# --- Patient Schemas ---
class PatientBase(BaseModel):
    name: str
    baseline_info: Optional[dict[str, Any]] = None

class PatientCreate(PatientBase):
    pass

class PatientResponse(PatientBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# --- Context Check-In Schemas ---
class ContextCheckInBase(BaseModel):
    medication_status: str
    sleep_hours: float
    stress_level: str

class ContextCheckInCreate(ContextCheckInBase):
    session_id: int

class ContextCheckInResponse(ContextCheckInBase):
    id: int
    session_id: int
    model_config = ConfigDict(from_attributes=True)

# --- Sensor Data Schemas ---
class SensorDataBase(BaseModel):
    phase: str
    accelerometer_x: float
    accelerometer_y: float
    accelerometer_z: float
    gyroscope_x: float
    gyroscope_y: float
    gyroscope_z: float
    touchscreen_data: Optional[dict[str, Any]] = None

class SensorDataCreate(SensorDataBase):
    session_id: int

class SensorDataResponse(SensorDataBase):
    id: int
    session_id: int
    model_config = ConfigDict(from_attributes=True)

# --- Movement Session Schemas ---
class MovementSessionBase(BaseModel):
    session_type: str
    movement_score: Optional[float] = None

class MovementSessionCreate(MovementSessionBase):
    patient_id: int

class MovementSessionResponse(MovementSessionBase):
    id: int
    patient_id: int
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)

# --- Stimulation Log Schemas ---
class StimulationLogBase(BaseModel):
    stimulation_parameters: dict[str, Any]
    before_session_id: Optional[int] = None
    after_session_id: Optional[int] = None

class StimulationLogCreate(StimulationLogBase):
    patient_id: int

class StimulationLogResponse(StimulationLogBase):
    id: int
    patient_id: int
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)