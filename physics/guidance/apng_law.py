"""Augmented Proportional Navigation Guidance Law (APNG).

Compensates for target acceleration to reduce miss distance
against hard-maneuvering targets by 40-60%.

a_commanded = N * Vc * lambda_dot + (N/2) * a_target
"""

import numpy as np
from physics.constants import NAV_CONSTANT_N, MAX_ACCEL_MS2
from physics.guidance.png_law import ProportionalNavigation
from physics.utils.vector_math import clip_vector, magnitude


class AugmentedProportionalNavigation(ProportionalNavigation):
    """Augmented PNG — adds target acceleration compensation."""

    def __init__(self, N: float = NAV_CONSTANT_N):
        super().__init__(N)

    def compute(self, missile_state: np.ndarray,
                target_state: np.ndarray,
                target_accel: np.ndarray = None,
                N: float = None) -> np.ndarray:
        """Compute APNG acceleration command.

        a_cmd = N * Vc * lambda_dot + (N/2) * a_target

        target_accel: estimated target acceleration [ax, ay, az] m/s²
        """
        if N is None:
            N = self.N

        # Standard PNG term
        Vc = self.closing_velocity(missile_state, target_state)
        lambda_dot = self.los_rate(missile_state, target_state)
        
        v_m = missile_state[3:6]
        v_m_mag = magnitude(v_m)
        r_m = missile_state[:3]
        r_t = target_state[:3]
        R_vec = r_t - r_m
        R_mag = magnitude(R_vec)
        
        if v_m_mag < 1.0 or R_mag < 1.0:
            a_png = np.zeros(3)
        else:
            R_hat = R_vec / R_mag
            a_png = N * Vc * np.cross(lambda_dot, R_hat)

        # Augmentation term (requires projected target acceleration perpendicular to LOS)
        if target_accel is not None:
            r_m = missile_state[:3]
            r_t = target_state[:3]
            R_vec = r_t - r_m
            R_mag = magnitude(R_vec)
            
            if R_mag > 1.0:
                R_hat = R_vec / R_mag
                # Target acceleration perpendicular to LOS
                a_t_normal = target_accel - np.dot(target_accel, R_hat) * R_hat
                a_aug = (N / 2.0) * a_t_normal
            else:
                a_aug = np.zeros(3)
        else:
            a_aug = np.zeros(3)

        a_cmd = a_png + a_aug
        
        # Add gravity compensation
        if v_m_mag > 50.0:
            a_cmd = a_cmd + np.array([0.0, 0.0, -9.80665])

        # Clip to max acceleration
        a_cmd = clip_vector(a_cmd, MAX_ACCEL_MS2)

        return a_cmd
