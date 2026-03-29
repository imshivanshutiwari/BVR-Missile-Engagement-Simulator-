"""Miss Distance Calculator.

Computes final miss distance between missile and target
at closest point of approach (CPA).
"""

import numpy as np
from physics.utils.vector_math import magnitude


class MissDistanceCalculator:
    """Computes miss distance from trajectory data."""

    @staticmethod
    def compute_from_trajectories(missile_traj: dict,
                                  target_traj: dict) -> dict:
        """Compute miss distance from missile and target trajectory dicts.

        Finds the closest point of approach (CPA).
        """
        n = min(len(missile_traj['x']), len(target_traj['x']))
        if n == 0:
            return {'miss_distance_m': float('inf'), 'cpa_time': 0, 'cpa_index': 0}

        min_dist = float('inf')
        cpa_index = 0
        cpa_time = 0.0

        for i in range(n):
            m_pos = np.array([missile_traj['x'][i],
                              missile_traj['y'][i],
                              missile_traj['z'][i]])
            t_pos = np.array([target_traj['x'][i],
                              target_traj['y'][i],
                              target_traj['z'][i]])
            dist = magnitude(m_pos - t_pos)

            if dist < min_dist:
                min_dist = dist
                cpa_index = i
                cpa_time = missile_traj['t'][i]

        return {
            'miss_distance_m': min_dist,
            'cpa_time': cpa_time,
            'cpa_index': cpa_index,
            'cpa_missile_pos': [missile_traj['x'][cpa_index],
                                missile_traj['y'][cpa_index],
                                missile_traj['z'][cpa_index]],
            'cpa_target_pos': [target_traj['x'][cpa_index],
                               target_traj['y'][cpa_index],
                               target_traj['z'][cpa_index]]
        }

    @staticmethod
    def compute_instant(missile_pos: np.ndarray,
                        target_pos: np.ndarray) -> float:
        """Instantaneous distance between missile and target."""
        return magnitude(missile_pos - target_pos)
