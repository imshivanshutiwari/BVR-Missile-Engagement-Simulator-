"""FastAPI Route — Simulation Endpoint.

POST /api/run-engagement — runs a full engagement simulation.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi import APIRouter
from server.schemas.engagement_request import EngagementRequest
from physics.engagement.engagement_engine import EngagementEngine

router = APIRouter()
engine = EngagementEngine()


def _traj_to_points(traj: dict) -> list:
    """Convert trajectory dict to list of point dicts."""
    keys = list(traj.keys())
    if not keys or not traj[keys[0]]:
        return []
    n = len(traj[keys[0]])
    points = []
    for i in range(n):
        pt = {}
        for k in keys:
            pt[k] = traj[k][i] if i < len(traj[k]) else None
        points.append(pt)
    return points


@router.post("/api/run-engagement")
async def run_engagement(req: EngagementRequest):
    """Run a full BVR engagement simulation."""
    result = engine.run(
        scenario=req.scenario,
        launch_range_m=req.launch_range_m,
        launch_altitude_m=req.launch_altitude_m,
        target_speed_ms=req.target_speed_ms,
        target_altitude_m=req.target_altitude_m,
        guidance_law=req.guidance_law,
        target_evasion=req.target_evasion
    )

    # Convert trajectories to list-of-dicts for JSON
    missile_points = _traj_to_points(result['trajectory'])
    target_points = _traj_to_points(result['target_trajectory'])

    return {
        'trajectory': missile_points,
        'target_trajectory': target_points,
        'intercept_achieved': result['intercept_achieved'],
        'miss_distance_m': result['miss_distance_m'],
        'time_of_flight_s': result['time_of_flight_s'],
        'pk': result['pk'],
        'pk_breakdown': result['pk_breakdown'],
        'intercept_point': result['intercept_point'],
        'engagement_summary': result['engagement_summary']
    }
