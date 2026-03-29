"""Augmented Proportional Navigation Guidance Law (APNG).

Compensates for target acceleration to reduce miss distance
against hard-maneuvering targets by 40-60%.

a_commanded = N * Vc * lambda_dot + (N/2) * a_target
"""

import numpy as np
from physics.constants import NAV_CONSTANT_N, MAX_ACCEL_MS2
from physics.guidance.png_law import ProportionalNavigation
from physics.utils.vector_math import clip_vector


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
        a_png = N * Vc * lambda_dot

        # Augmentation term
        if target_accel is not None:
            a_aug = (N / 2.0) * target_accel
        else:
            a_aug = np.zeros(3)

        a_cmd = a_png + a_aug

        # Clip to max acceleration
        a_cmd = clip_vector(a_cmd, MAX_ACCEL_MS2)

        return a_cmd
