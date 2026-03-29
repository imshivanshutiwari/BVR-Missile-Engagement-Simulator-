"""FastAPI Route — Telemetry SSE Stream.

GET /api/telemetry/stream — Server-Sent Events stream during active engagement.
"""

import sys
import os
import json
import asyncio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi import APIRouter, Query
from sse_starlette.sse import EventSourceResponse
from physics.engagement.engagement_engine import EngagementEngine
from physics.utils.vector_math import magnitude
import numpy as np

router = APIRouter()
engine = EngagementEngine()


@router.get("/api/telemetry/stream")
async def telemetry_stream(
    scenario: str = Query(default="head_on"),
    guidance_law: str = Query(default="png"),
    launch_range_m: float = Query(default=20000.0),
    launch_altitude_m: float = Query(default=8000.0),
    target_speed_ms: float = Query(default=250.0),
    target_altitude_m: float = Query(default=8000.0)
):
    """SSE stream of engagement telemetry at 10Hz."""

    async def event_generator():
        # Run simulation first
        result = engine.run(
            scenario=scenario,
            launch_range_m=launch_range_m,
            launch_altitude_m=launch_altitude_m,
            target_speed_ms=target_speed_ms,
            target_altitude_m=target_altitude_m,
            guidance_law=guidance_law,
            target_evasion=True
        )

        traj = result['trajectory']
        tgt_traj = result['target_trajectory']
        n = len(traj['t'])

        # Stream at 10Hz — subsample trajectory data
        step = max(1, n // (int(traj['t'][-1] * 10) if traj['t'][-1] > 0 else 1))

        for i in range(0, n, max(1, step)):
            m_pos = np.array([traj['x'][i], traj['y'][i], traj['z'][i]])

            if i < len(tgt_traj['t']):
                t_pos = np.array([tgt_traj['x'][i], tgt_traj['y'][i], tgt_traj['z'][i]])
                range_to_target = float(magnitude(m_pos - t_pos))
                m_vel = np.array([traj['vx'][i], traj['vy'][i], traj['vz'][i]])
                r_vec = t_pos - m_pos
                r_mag = magnitude(r_vec)
                closing_vel = float(-np.dot(r_vec, m_vel) / r_mag) if r_mag > 0 else 0
            else:
                range_to_target = 0
                closing_vel = 0
                t_pos = m_pos

            g_load = 0
            if traj['speed'][i] > 0:
                accel_mag = magnitude(np.array([
                    traj['guidance_ax'][i],
                    traj['guidance_ay'][i],
                    traj['guidance_az'][i]
                ]))
                g_load = accel_mag / 9.80665

            event_data = {
                't': round(traj['t'][i], 3),
                'mach': round(traj['mach'][i], 3),
                'altitude_m': round(traj['altitude'][i], 1),
                'range_to_target_m': round(range_to_target, 1),
                'closing_velocity_ms': round(closing_vel, 1),
                'g_load': round(g_load, 2),
                'phase': traj['phase'][i],
                'guidance_error_mrad': round(g_load * 10, 2),
                'los_rate_rads': round(g_load * 0.01, 4),
                'pk_current': round(result['pk'], 3),
                'missile_x': round(traj['x'][i], 1),
                'missile_y': round(traj['y'][i], 1),
                'missile_z': round(traj['z'][i], 1),
                'target_x': round(float(t_pos[0]), 1),
                'target_y': round(float(t_pos[1]), 1),
                'target_z': round(float(t_pos[2]), 1)
            }

            yield {
                "event": "telemetry",
                "data": json.dumps(event_data)
            }

            await asyncio.sleep(0.1)  # 10Hz

        # Final event
        yield {
            "event": "complete",
            "data": json.dumps({
                'intercept_achieved': result['intercept_achieved'],
                'miss_distance_m': round(result['miss_distance_m'], 2),
                'pk': round(result['pk'], 3),
                'time_of_flight_s': round(result['time_of_flight_s'], 2)
            })
        }

    return EventSourceResponse(event_generator())
