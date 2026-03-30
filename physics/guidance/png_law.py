"""Pure Proportional Navigation Guidance Law (PNG).

Industry standard for ALL modern AAMs.
a_commanded = N * Vc * lambda_dot

Where:
  N = navigation constant (4.0 optimal vs maneuvering target)
  Vc = closing velocity
  lambda_dot = LOS (line-of-sight) rate vector
"""

import numpy as np
from physics.constants import NAV_CONSTANT_N, MAX_ACCEL_MS2
from physics.utils.vector_math import magnitude, clip_vector, dot, cross


class ProportionalNavigation:
    """Pure Proportional Navigation guidance law implementation."""

    def __init__(self, N: float = NAV_CONSTANT_N):
        self.N = N

    def los_rate(self, missile_state: np.ndarray,
                 target_state: np.ndarray) -> np.ndarray:
        """Compute Line-of-Sight rate vector (lambda_dot).

        lambda_dot = (R × V_rel) / |R|²

        missile_state, target_state = [x, y, z, vx, vy, vz]
        """
        r_m = missile_state[:3]
        r_t = target_state[:3]
        v_m = missile_state[3:6]
        v_t = target_state[3:6]

        R_vec = r_t - r_m       # range vector (missile to target)
        V_rel = v_t - v_m       # relative velocity

        R_mag = magnitude(R_vec)
        if R_mag < 1.0:
            return np.zeros(3)

        lambda_dot = cross(R_vec, V_rel) / (R_mag ** 2)
        return lambda_dot

    def closing_velocity(self, missile_state: np.ndarray,
                         target_state: np.ndarray) -> float:
        """Compute closing velocity Vc.

        Vc = -(R · V_rel) / |R|
        Positive = closing (approaching target).
        """
        r_m = missile_state[:3]
        r_t = target_state[:3]
        v_m = missile_state[3:6]
        v_t = target_state[3:6]

        R_vec = r_t - r_m
        V_rel = v_t - v_m
        R_mag = magnitude(R_vec)

        if R_mag < 1.0:
            return 0.0

        return -dot(R_vec, V_rel) / R_mag

    def compute(self, missile_state: np.ndarray,
                target_state: np.ndarray,
                N: float = None) -> np.ndarray:
        """Compute 3D acceleration command [ax, ay, az] in m/s².

        a_cmd = N * Vc * cross(V_m_hat, lambda_dot)

        Clipped to ±30g per axis.
        """
        if N is None:
            N = self.N

        Vc = self.closing_velocity(missile_state, target_state)
        lambda_dot = self.los_rate(missile_state, target_state)
        v_m = missile_state[3:6]
        v_m_mag = magnitude(v_m)
        r_m = missile_state[:3]
        r_t = target_state[:3]
        R_vec = r_t - r_m
        R_mag = magnitude(R_vec)

        if v_m_mag < 1.0 or R_mag < 1.0:
            return np.zeros(3)
            
        R_hat = R_vec / R_mag

        # True Proportional Navigation vector form:
        # Acceleration must be perpendicular to LOS, in the plane of LOS rotation
        a_cmd = N * Vc * cross(lambda_dot, R_hat)
        
        # Add gravity compensation (assuming gravity pulls in +Z direction in NED)
        # We need an acceleration in -Z to counteract it
        a_bias = np.array([0.0, 0.0, -9.80665])
        
        # Only apply gravity bias if the missile has reasonable speed
        if v_m_mag > 50.0:
            a_cmd = a_cmd + a_bias

        # Clip to max acceleration
        a_cmd = clip_vector(a_cmd, MAX_ACCEL_MS2)

        return a_cmd
