"""Pydantic Schemas — NEZ Response."""

from pydantic import BaseModel
from typing import List


class NEZPoint(BaseModel):
    """Single NEZ computation point."""
    range_m: float
    aspect_deg: float
    altitude_m: float
    is_nez: bool
    miss_distance_m: float
    pk: float


class LARData(BaseModel):
    """Launch Acceptability Region data."""
    r_min: List[float]
    r_max: List[float]
    aspect: List[float]


class NEZResponse(BaseModel):
    """Response for /api/compute-nez."""
    nez_points: List[dict]
    lar_data: dict
    computation_time_s: float
    total_sims_run: int
