"""FastAPI Route — NEZ Computation Endpoint.

GET /api/compute-nez — computes No-Escape Zone envelope.
"""

import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi import APIRouter, Query
from physics.engagement.nez_computer import NoEscapeZoneComputer

router = APIRouter()
nez_computer = NoEscapeZoneComputer()


@router.get("/api/compute-nez")
async def compute_nez(
    target_speed_ms: float = Query(default=250.0, ge=100, le=600),
    target_altitude_m: float = Query(default=8000.0, ge=100, le=20000),
    guidance_law: str = Query(default="png", pattern="^(png|apng|ai_model)$"),
    resolution: int = Query(default=16, ge=8, le=64)
):
    """Compute No-Escape Zone envelope."""
    start_time = time.time()

    n_aspect = resolution
    n_range = max(8, resolution // 2)

    result = nez_computer.compute_nez_slice(
        altitude_m=target_altitude_m,
        target_speed=target_speed_ms,
        guidance_law=guidance_law,
        n_aspect=n_aspect,
        n_range=n_range
    )

    lar = nez_computer.compute_lar(
        altitude_m=target_altitude_m,
        target_speed=target_speed_ms,
        guidance_law=guidance_law,
        n_aspect=min(24, n_aspect)
    )

    comp_time = time.time() - start_time

    return {
        'nez_points': result['nez_points'],
        'lar_data': lar,
        'computation_time_s': comp_time,
        'total_sims_run': result['total_sims']
    }
