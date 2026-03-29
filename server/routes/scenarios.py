"""FastAPI Route — Scenarios Endpoint.

GET /api/scenarios — returns all scenario definitions.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi import APIRouter
from physics.scenarios.scenario_runner import ScenarioRunner

router = APIRouter()
runner = ScenarioRunner()


@router.get("/api/scenarios")
async def get_scenarios():
    """Return all scenario definitions."""
    return runner.get_all_scenarios()
