"""Full Engagement Simulation Engine.

Runs complete BVR missile engagement:
  missile launch → guidance → flight → intercept/miss
"""

import numpy as np
import math
from physics.atmosphere import StandardAtmosphere1976
from physics.aerodynamics import MissileAerodynamics
from physics.propulsion import DualPulsePropulsion
from physics.equations_of_motion import PointMassEOM
from physics.guidance.png_law import ProportionalNavigation
from physics.guidance.apng_law import AugmentedProportionalNavigation
from physics.guidance.guidance_selector import select_guidance
from physics.target.f16_model import F16KinematicModel
from physics.target.target_predictor import TargetPredictor
from physics.engagement.pk_calculator import ProbabilityOfKillCalculator
from physics.engagement.fuze_model import ProximityFuze
from physics.engagement.miss_distance import MissDistanceCalculator
from physics.utils.vector_math import magnitude
from physics.constants import SIM_DT, SIM_MAX_TIME


class EngagementEngine:
    """Full engagement simulation engine."""

    def __init__(self):
        self.atm = StandardAtmosphere1976()
        self.aero = MissileAerodynamics(self.atm)
        self.prop = DualPulsePropulsion(self.atm)
        self.eom = PointMassEOM(self.atm, self.aero, self.prop)
        self.pk_calc = ProbabilityOfKillCalculator()
        self.fuze = ProximityFuze()
        self.miss_calc = MissDistanceCalculator()
        self.target_predictor = TargetPredictor()

    def setup_engagement(self, scenario: str = "head_on",
                         launch_range_m: float = 20000.0,
                         launch_altitude_m: float = 8000.0,
                         target_speed_ms: float = 250.0,
                         target_altitude_m: float = 8000.0,
                         guidance_law: str = "png",
                         target_evasion: bool = True) -> dict:
        """Set up engagement geometry.

        Returns initial conditions dict.
        """
        scenario = scenario.lower().strip()

        missile_speed = 300.0  # m/s launch speed (rail launch off fighter)

        if scenario == "head_on":
            # Missile moving east, target moving west (head-on)
            missile_pos = np.array([0.0, 0.0, -launch_altitude_m])
            missile_vel = np.array([missile_speed, 0.0, 0.0])
            target_pos = np.array([launch_range_m, 0.0, -target_altitude_m])
            target_vel = np.array([-target_speed_ms, 0.0, 0.0])
            heading_deg = 180.0

        elif scenario == "tail_chase":
            # Both moving east, missile behind target
            missile_pos = np.array([0.0, 0.0, -launch_altitude_m])
            missile_vel = np.array([missile_speed, 0.0, 0.0])
            target_pos = np.array([launch_range_m, 0.0, -target_altitude_m])
            target_vel = np.array([target_speed_ms, 0.0, 0.0])
            heading_deg = 0.0

        elif scenario == "crossing":
            # Missile east, target moving north (90° crossing)
            missile_pos = np.array([0.0, 0.0, -launch_altitude_m])
            missile_vel = np.array([missile_speed, 0.0, 0.0])
            target_pos = np.array([launch_range_m, 0.0, -target_altitude_m])
            target_vel = np.array([0.0, target_speed_ms, 0.0])
            heading_deg = 90.0

        else:
            raise ValueError(f"Unknown scenario: {scenario}")

        # Create target model
        target = F16KinematicModel(
            initial_pos=target_pos,
            initial_vel=target_vel,
            altitude_m=target_altitude_m,
            speed_ms=target_speed_ms,
            heading_deg=heading_deg
        )

        # Select guidance law
        guidance = select_guidance(guidance_law)

        return {
            'missile_pos': missile_pos,
            'missile_vel': missile_vel,
            'target': target,
            'guidance': guidance,
            'guidance_law': guidance_law,
            'target_evasion': target_evasion,
            'scenario': scenario,
            'launch_range_m': launch_range_m
        }

    def run(self, scenario: str = "head_on",
            launch_range_m: float = 20000.0,
            launch_altitude_m: float = 8000.0,
            target_speed_ms: float = 250.0,
            target_altitude_m: float = 8000.0,
            guidance_law: str = "png",
            target_evasion: bool = True,
            dt: float = SIM_DT) -> dict:
        """Run complete engagement simulation.

        Returns full results dict with trajectories, Pk, miss distance, etc.
        """
        setup = self.setup_engagement(
            scenario=scenario,
            launch_range_m=launch_range_m,
            launch_altitude_m=launch_altitude_m,
            target_speed_ms=target_speed_ms,
            target_altitude_m=target_altitude_m,
            guidance_law=guidance_law,
            target_evasion=target_evasion
        )

        missile_state0 = np.concatenate([
            setup['missile_pos'], setup['missile_vel']
        ])
        target = setup['target']
        guidance = setup['guidance']
        is_apng = guidance_law.lower() == "apng"

        # Target state function
        def target_fn(t):
            if target_evasion:
                return target.evasive_barrel_roll(t)
            return target.straight_and_level(t)

        # Guidance function
        predictor = TargetPredictor()

        def guidance_fn(t, missile_state, target_state):
            predictor.update(t, target_state)
            if is_apng:
                target_accel = predictor.get_acceleration()
                return guidance.compute(missile_state, target_state, target_accel)
            return guidance.compute(missile_state, target_state)

        # Run integration
        result = self.eom.integrate_rk4(
            state0=missile_state0,
            t_span=(0.0, SIM_MAX_TIME),
            dt=dt,
            guidance_fn=guidance_fn,
            target_fn=target_fn
        )

        # Compute Pk
        miss_dist = result['miss_distance_m']
        pk = self.pk_calc.compute_pk(miss_dist)
        pk_breakdown = self.pk_calc.pk_breakdown(miss_dist)

        # Build engagement summary
        traj = result['trajectory']
        max_mach = max(traj['mach']) if traj['mach'] else 0
        max_alt = max(traj['altitude']) if traj['altitude'] else 0
        max_speed = max(traj['speed']) if traj['speed'] else 0

        result['pk'] = pk
        result['pk_breakdown'] = pk_breakdown
        result['engagement_summary'] = {
            'scenario': scenario,
            'guidance_law': guidance_law,
            'launch_range_m': launch_range_m,
            'max_mach': max_mach,
            'max_altitude_m': max_alt,
            'max_speed_ms': max_speed,
            'target_evasion': target_evasion,
            'intercept_achieved': result['intercept_achieved'],
            'miss_distance_m': miss_dist,
            'time_of_flight_s': result['time_of_flight_s'],
            'pk': pk
        }

        return result
