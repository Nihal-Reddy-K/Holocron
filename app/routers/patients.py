from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/patients", tags=["Patients"])

@router.post("/", response_model=schemas.PatientResponse)
async def create_patient(patient: schemas.PatientCreate, db: AsyncSession = Depends(get_db)):
    new_patient = models.Patient(**patient.model_dump())
    db.add(new_patient)
    await db.commit()
    await db.refresh(new_patient)
    return new_patient

@router.get("/", response_model=list[schemas.PatientResponse])
async def get_patients(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Patient))
    return result.scalars().all()