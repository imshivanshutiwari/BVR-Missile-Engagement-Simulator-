"""STRIKE-VECTOR FastAPI Server — Main Entry Point.

Runs on port 8000 with CORS enabled for React frontend.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.routes.simulation import router as sim_router
from server.routes.nez import router as nez_router
from server.routes.scenarios import router as scenarios_router
from server.routes.telemetry import router as telemetry_router

app = FastAPI(
    title="STRIKE-VECTOR API",
    description="BVR Missile Engagement Simulator — Physics Engine API",
    version="1.0.0"
)

# CORS for React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routes
app.include_router(sim_router)
app.include_router(nez_router)
app.include_router(scenarios_router)
app.include_router(telemetry_router)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "name": "STRIKE-VECTOR",
        "version": "1.0.0",
        "systems": {
            "physics": "ONLINE",
            "guidance": "PNG-N4",
            "atmosphere": "ISA-1976",
            "target": "F-16 CLASS",
            "server": "CONNECTED"
        }
    }


@app.get("/api/health")
async def health():
    """System health check."""
    return {"status": "ok", "systems_online": True}
