"""Pydantic Schemas — Trajectory Response."""

from pydantic import BaseModel
from typing import List, Optional


class TrajectoryPoint(BaseModel):
    """Single point in trajectory."""
    t: float
    x: float
    y: float
    z: float
    vx: float
    vy: float
    vz: float
    mach: float
    altitude: float
    speed: float
    thrust: float
    drag: float
    guidance_ax: float
    guidance_ay: float
    guidance_az: float
    mass: float
    q_dynamic: float
    phase: str


class InterceptPoint(BaseModel):
    """Intercept location."""
    x: float
    y: float
    z: float


class EngagementSummary(BaseModel):
    """Summary of engagement results."""
    scenario: str
    guidance_law: str
    launch_range_m: float
    max_mach: float
    max_altitude_m: float
    max_speed_ms: float
    target_evasion: bool
    intercept_achieved: bool
    miss_distance_m: float
    time_of_flight_s: float
    pk: float


class TrajectoryResponse(BaseModel):
    """Response for /api/run-engagement."""
    trajectory: List[dict]
    target_trajectory: List[dict]
    intercept_achieved: bool
    miss_distance_m: float
    time_of_flight_s: float
    pk: float
    pk_breakdown: dict
    intercept_point: Optional[dict] = None
    engagement_summary: dict
