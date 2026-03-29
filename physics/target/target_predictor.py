"""Target State Predictor — Seeker Target State Estimation.

Estimates target future state for guidance law feed-forward.
"""

import numpy as np
from physics.utils.vector_math import magnitude


class TargetPredictor:
    """Simple target state estimator for seeker."""

    def __init__(self):
        self._prev_state = None
        self._prev_time = None
        self._accel_estimate = np.zeros(3)

    def update(self, t: float, target_state: np.ndarray) -> dict:
        """Update estimator with new measurement.

        Returns estimated target state including acceleration.
        """
        pos = target_state[:3]
        vel = target_state[3:6]

        if self._prev_state is not None and self._prev_time is not None:
            dt = t - self._prev_time
            if dt > 1e-6:
                prev_vel = self._prev_state[3:6]
                self._accel_estimate = (vel - prev_vel) / dt
        else:
            self._accel_estimate = np.zeros(3)

        self._prev_state = target_state.copy()
        self._prev_time = t

        return {
            'position': pos,
            'velocity': vel,
            'acceleration': self._accel_estimate.copy(),
            'speed': magnitude(vel),
            'time': t
        }

    def predict(self, dt_ahead: float) -> np.ndarray:
        """Predict target state dt_ahead seconds into the future.

        Uses constant-acceleration model.
        """
        if self._prev_state is None:
            return np.zeros(6)

        pos = self._prev_state[:3]
        vel = self._prev_state[3:6]
        acc = self._accel_estimate

        pred_pos = pos + vel * dt_ahead + 0.5 * acc * dt_ahead ** 2
        pred_vel = vel + acc * dt_ahead

        return np.concatenate([pred_pos, pred_vel])

    def get_acceleration(self) -> np.ndarray:
        """Get current estimated target acceleration."""
        return self._accel_estimate.copy()
