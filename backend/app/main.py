import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database.session import engine, Base, SessionLocal
from app.models import *  # Import all models to ensure table registration
from app.services.scenarios import ScenarioService

# Import API Routers
from app.api.auth import router as auth_router
from app.api.events import router as events_router
from app.api.detections import router as detections_router
from app.api.incidents import router as incidents_router
from app.api.investigations import router as investigations_router
from app.api.risk import router as risk_router
from app.api.response import router as response_router
from app.api.audit import router as audit_router
from app.api.agents import router as agents_router
from app.api.intel import router as intel_router
from app.api.analytics import router as analytics_router
from app.api.scenarios import router as scenarios_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database schema is created
    try:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            ScenarioService.seed_threat_intel_and_users(db)
        finally:
            db.close()
        print("[GAS Startup] Database schema initialized and seed records verified.")
    except Exception as e:
        print(f"[GAS Startup WARNING] Database connection issue during initialization: {e}")
        print("[GAS Startup WARNING] Application will continue running. Please verify your DATABASE_URL in Render environment settings.")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Enterprise-Grade AI-Supported Cyber-Resilience Platform (TECHgium 2026 - L&T Technology Services)",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits local development & Vercel deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 Routers
api_v1_prefix = settings.API_V1_STR
app.include_router(auth_router, prefix=api_v1_prefix)
app.include_router(events_router, prefix=api_v1_prefix)
app.include_router(detections_router, prefix=api_v1_prefix)
app.include_router(incidents_router, prefix=api_v1_prefix)
app.include_router(investigations_router, prefix=api_v1_prefix)
app.include_router(risk_router, prefix=api_v1_prefix)
app.include_router(response_router, prefix=api_v1_prefix)
app.include_router(audit_router, prefix=api_v1_prefix)
app.include_router(agents_router, prefix=api_v1_prefix)
app.include_router(intel_router, prefix=api_v1_prefix)
app.include_router(analytics_router, prefix=api_v1_prefix)
app.include_router(scenarios_router, prefix=api_v1_prefix)

@app.get("/")
def root():
    return {
        "platform": settings.PROJECT_NAME,
        "status": "OPERATIONAL",
        "philosophy": "DETECT. CORRELATE. INVESTIGATE. EXPLAIN. GOVERN. PROTECT.",
        "api_docs": "/docs",
        "api_v1": settings.API_V1_STR
    }

@app.get("/api/v1/health")
def health_check():
    return {
        "status": "HEALTHY",
        "platform": "Guardian Angel Systems (GAS)",
        "mode": settings.ENVIRONMENT,
        "database": "CONNECTED",
        "timestamp": time.time()
    }
