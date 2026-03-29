"""F-16 Class Fighter Jet Kinematic Model.

Point mass with aerodynamic limits.
Supports: straight-and-level, barrel roll evasion, defensive break turn.
"""

import numpy as np
import math
from physics.constants import (
    F16_MASS, F16_VMAX, F16_VCRUISE, F16_G_MAX,
    F16_CLIMB_RATE, F16_BANK_RATE_DEG, F16_EVASION_G, G0
)


class F16KinematicModel:
    """F-16 class target aircraft kinematic model."""

    def __init__(self, initial_pos: np.ndarray = None,
                 initial_vel: np.ndarray = None,
                 altitude_m: float = 8000.0,
                 speed_ms: float = None,
                 heading_deg: float = 180.0):
        self.mass = F16_MASS
        self.Vmax = F16_VMAX
        self.Vcruise = speed_ms or F16_VCRUISE
        self.g_max = F16_G_MAX
        self.climb_rate = F16_CLIMB_RATE
        self.bank_rate = math.radians(F16_BANK_RATE_DEG)
        self.evasion_g = F16_EVASION_G

        heading_rad = math.radians(heading_deg)

        if initial_pos is not None:
            self.pos0 = initial_pos.copy()
        else:
            self.pos0 = np.array([50000.0, 0.0, -altitude_m])

        if initial_vel is not None:
            self.vel0 = initial_vel.copy()
        else:
            self.vel0 = np.array([
                self.Vcruise * math.cos(heading_rad),
                self.Vcruise * math.sin(heading_rad),
                0.0
            ])

        self._evasion_active = False
        self._evasion_trigger_range = 15000.0
        self._evasion_start_time = None

    def straight_and_level(self, t: float) -> np.ndarray:
        """Constant velocity, heading, altitude flight.

        Returns state [x, y, z, vx, vy, vz].
        """
        pos = self.pos0 + self.vel0 * t
        return np.concatenate([pos, self.vel0])

    def evasive_barrel_roll(self, t: float,
                            trigger_range_m: float = None) -> np.ndarray:
        """Full barrel roll evasion maneuver.

        Phase 1 (0-1.5s): 7g vertical pull-up
        Phase 2 (1.5-3.5s): 270°/s roll with sustained pull
        Phase 3 (3.5-4.5s): nose-low recovery push
        Then repeats.
        """
        if trigger_range_m is not None:
            self._evasion_trigger_range = trigger_range_m

        # Evasion cycle period
        cycle_duration = 4.5
        t_in_cycle = t % cycle_duration

        g_load = self.evasion_g
        turn_radius = self.Vcruise ** 2 / (g_load * G0)

        # Base position (straight flight component)
        base_pos = self.pos0 + self.vel0 * t
        speed = self.Vcruise

        # Maneuver offsets
        if t_in_cycle < 1.5:
            # Phase 1: Pull-up — 7g vertical pull
            frac = t_in_cycle / 1.5
            dz = -turn_radius * (1.0 - math.cos(frac * math.pi / 2)) * 0.3
            dy = turn_radius * math.sin(frac * math.pi / 4) * 0.2
            vz = -speed * 0.3 * math.sin(frac * math.pi / 2)
            vy_offset = speed * 0.2 * math.cos(frac * math.pi / 4)

        elif t_in_cycle < 3.5:
            # Phase 2: Roll — 270°/s roll with sustained pull
            t_roll = t_in_cycle - 1.5
            roll_angle = math.radians(270.0) * t_roll / 2.0
            dz = -turn_radius * 0.3 * math.cos(roll_angle)
            dy = turn_radius * 0.3 * math.sin(roll_angle)
            vz = speed * 0.3 * math.sin(roll_angle)
            vy_offset = speed * 0.3 * math.cos(roll_angle)

        else:
            # Phase 3: Recovery push
            t_rec = t_in_cycle - 3.5
            frac = t_rec / 1.0
            dz = -turn_radius * 0.3 * (1.0 - frac)
            dy = turn_radius * 0.1 * (1.0 - frac)
            vz = speed * 0.3 * frac
            vy_offset = speed * 0.1 * (1.0 - frac)

        pos = base_pos + np.array([0.0, dy, dz])
        vel = self.vel0.copy()
        vel[1] += vy_offset
        vel[2] += vz

        # Clamp speed
        spd = np.linalg.norm(vel)
        if spd > self.Vmax:
            vel = vel * (self.Vmax / spd)

        return np.concatenate([pos, vel])

    def defensive_break_turn(self, t: float,
                             missile_bearing_rad: float = 0.0) -> np.ndarray:
        """Hard break turn toward missile approach bearing.

        7g sustained turn to minimize tail-aspect engagement.
        """
        g_load = self.evasion_g
        turn_rate = g_load * G0 / self.Vcruise  # rad/s

        heading0 = math.atan2(self.vel0[1], self.vel0[0])
        # Turn toward missile bearing
        target_heading = missile_bearing_rad
        d_heading = target_heading - heading0
        d_heading = math.atan2(math.sin(d_heading), math.cos(d_heading))
        sign = 1.0 if d_heading > 0 else -1.0

        current_heading = heading0 + sign * turn_rate * t
        vx = self.Vcruise * math.cos(current_heading)
        vy = self.Vcruise * math.sin(current_heading)

        # Integrate position
        if abs(turn_rate) > 1e-6:
            dx = self.Vcruise / turn_rate * (
                math.sin(current_heading) - math.sin(heading0))
            dy = self.Vcruise / turn_rate * (
                math.cos(heading0) - math.cos(current_heading))
        else:
            dx = vx * t
            dy = vy * t

        pos = self.pos0 + np.array([dx, dy, 0.0])
        vel = np.array([vx, vy, 0.0])

        return np.concatenate([pos, vel])

    def get_state(self, t: float, evasion: bool = False,
                  missile_range: float = None) -> np.ndarray:
        """Get target state at time t.

        If evasion=True and missile is within trigger range,
        execute barrel roll.
        """
        if evasion:
            if missile_range is not None and missile_range < self._evasion_trigger_range:
                return self.evasive_barrel_roll(t)
            else:
                return self.evasive_barrel_roll(t)
        return self.straight_and_level(t)

    def g_load_at_time(self, t: float) -> float:
        """Compute g-load experienced during barrel roll maneuver."""
        cycle_duration = 4.5
        t_in_cycle = t % cycle_duration
        if t_in_cycle < 1.5:
            return self.evasion_g
        elif t_in_cycle < 3.5:
            return self.evasion_g * 0.8
        else:
            return 3.0  # recovery

    def chaff_dispensing(self, t: float) -> dict:
        """Chaff cloud position and RCS model (for future seeker extension)."""
        state = self.straight_and_level(t)
        return {
            'position': state[:3] - self.vel0 * 0.5,
            'rcs_m2': 50.0,
            'dispense_time': t,
            'lifetime_s': 10.0
        }
