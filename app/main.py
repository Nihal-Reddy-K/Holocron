from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
import app.models 

# Import all of your completed routers
from app.routers import patients, sessions, stimulation, dashboard

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Clean up resources on shutdown
    await engine.dispose()

app = FastAPI(
    title="NeuroTrack MVP API",
    description="Backend for neurological digital movement-monitoring platform",
    version="1.0.0",
    lifespan=lifespan
)

# --- Enable CORS for Frontend Integration ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for the hackathon demo
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# --- Register all endpoints ---
app.include_router(patients.router)
app.include_router(sessions.router)
app.include_router(stimulation.router)
app.include_router(dashboard.router)

@app.get("/")
async def root():
    return {"message": "NeuroTrack API is running."}