"""Pydantic Schemas — Engagement Request."""

from pydantic import BaseModel, Field
from typing import Optional


class MissileParams(BaseModel):
    """Missile configuration parameters."""
    total_mass_kg: float = Field(default=185.0, ge=50, le=500)
    boost_thrust_n: float = Field(default=15000.0, ge=5000, le=30000)
    sustain_thrust_n: float = Field(default=3200.0, ge=1000, le=10000)
    boost_duration_s: float = Field(default=3.2, ge=1.0, le=10.0)
    sustain_end_s: float = Field(default=20.0, ge=5.0, le=60.0)
    nav_constant: float = Field(default=4.0, ge=2.0, le=6.0)


class TargetParams(BaseModel):
    """Target configuration parameters."""
    mass_kg: float = Field(default=9200.0)
    max_speed_ms: float = Field(default=600.0)
    max_g: float = Field(default=9.0)
    evasion_g: float = Field(default=7.0)


class EngagementRequest(BaseModel):
    """Request body for /api/run-engagement."""
    scenario: str = Field(default="head_on",
                          pattern="^(head_on|tail_chase|crossing)$")
    guidance_law: str = Field(default="png", pattern="^(png|apng)$")
    launch_range_m: float = Field(default=20000.0, ge=2000, le=80000)
    launch_altitude_m: float = Field(default=8000.0, ge=100, le=20000)
    target_speed_ms: float = Field(default=250.0, ge=100, le=600)
    target_altitude_m: float = Field(default=8000.0, ge=100, le=20000)
    target_evasion: bool = Field(default=True)
    missile_params: Optional[MissileParams] = None
    target_params: Optional[TargetParams] = None
