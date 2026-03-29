"""Evasion Maneuver Module — 7g Barrel Roll Implementation.

Detailed kinematic barrel roll maneuver model for target evasion.
"""

import numpy as np
import math
from physics.constants import G0, F16_EVASION_G, F16_VCRUISE


class BarrelRollManeuver:
    """7g barrel roll evasive maneuver kinematics."""

    def __init__(self, speed_ms: float = F16_VCRUISE,
                 g_load: float = F16_EVASION_G):
        self.speed = speed_ms
        self.g_load = g_load
        self.turn_radius = speed_ms ** 2 / (g_load * G0)
        self.pull_duration = 1.5      # s
        self.roll_duration = 2.0      # s
        self.recovery_duration = 1.0  # s
        self.cycle_duration = self.pull_duration + self.roll_duration + self.recovery_duration

    def compute_offset(self, t: float) -> tuple:
        """Compute position offset (dy, dz) and velocity offsets from barrel roll.

        Returns: (offset_yz: np.ndarray, vel_offset_yz: np.ndarray, g_current: float)
        """
        t_cycle = t % self.cycle_duration
        R = self.turn_radius
        V = self.speed

        if t_cycle < self.pull_duration:
            frac = t_cycle / self.pull_duration
            angle = frac * math.pi / 2
            dy = R * 0.2 * math.sin(angle * 0.5)
            dz = -R * 0.3 * (1.0 - math.cos(angle))
            vy = V * 0.2 * math.cos(angle * 0.5)
            vz = -V * 0.3 * math.sin(angle)
            g = self.g_load

        elif t_cycle < self.pull_duration + self.roll_duration:
            t_roll = t_cycle - self.pull_duration
            roll_angle = math.radians(270.0) * t_roll / self.roll_duration
            dy = R * 0.3 * math.sin(roll_angle)
            dz = -R * 0.3 * math.cos(roll_angle)
            vy = V * 0.3 * math.cos(roll_angle) * math.radians(270.0) / self.roll_duration
            vz = V * 0.3 * math.sin(roll_angle) * math.radians(270.0) / self.roll_duration
            g = self.g_load * 0.8

        else:
            t_rec = t_cycle - self.pull_duration - self.roll_duration
            frac = t_rec / self.recovery_duration
            dy = R * 0.1 * (1.0 - frac)
            dz = -R * 0.3 * (1.0 - frac)
            vy = -V * 0.1 / self.recovery_duration
            vz = V * 0.3 / self.recovery_duration
            g = 3.0

        return (np.array([dy, dz]), np.array([vy, vz]), g)

    def max_g_in_cycle(self) -> float:
        """Maximum g-load in a full barrel roll cycle."""
        return self.g_load

    def acceleration_at_time(self, t: float) -> np.ndarray:
        """Compute lateral acceleration vector at time t.

        Used by APNG to estimate target acceleration.
        """
        _, vel_offset, g = self.compute_offset(t)
        # Approximate acceleration from velocity change
        dt = 0.01
        _, vel_offset2, _ = self.compute_offset(t + dt)
        accel = (vel_offset2 - vel_offset) / dt
        return np.array([0.0, accel[0], accel[1]])
