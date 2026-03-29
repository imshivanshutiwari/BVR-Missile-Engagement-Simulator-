"""Probability of Kill (Pk) Calculator.

Pk = P_fuze × P_lethality × P_guidance

Based on NATO STANAG 4458 methodology.
"""

import math
import numpy as np
from physics.constants import FUZE_RADIUS, LETHAL_RADIUS, FUZE_K, WARHEAD_K


class ProbabilityOfKillCalculator:
    """Computes kill probability from miss distance."""

    def __init__(self, fuze_radius: float = FUZE_RADIUS,
                 lethal_radius: float = LETHAL_RADIUS):
        self.fuze_radius = fuze_radius
        self.lethal_radius = lethal_radius

    def compute_pk(self, miss_distance_m: float) -> float:
        """Compute total Pk for a given miss distance.

        Pk = P_fuze × P_lethality × P_guidance
        """
        if miss_distance_m < 0.01:
            return 1.0

        # Fuze actuation probability
        ratio = (self.lethal_radius / miss_distance_m) ** 2
        p_fuze = 1.0 - math.exp(-FUZE_K * ratio)

        # Warhead lethality given fuze fires
        p_lethality = 1.0 - math.exp(-WARHEAD_K * ratio)

        # Guidance accuracy factor
        p_guidance = max(0.0, min(1.0,
                                  1.0 - (miss_distance_m / self.lethal_radius) ** 0.7))

        pk_total = p_fuze * p_lethality * p_guidance
        return max(0.0, min(1.0, pk_total))

    def pk_breakdown(self, miss_distance_m: float) -> dict:
        """Return Pk breakdown components."""
        if miss_distance_m < 0.01:
            return {'p_fuze': 1.0, 'p_lethality': 1.0,
                    'p_guidance': 1.0, 'pk_total': 1.0}

        ratio = (self.lethal_radius / miss_distance_m) ** 2
        p_fuze = 1.0 - math.exp(-FUZE_K * ratio)
        p_lethality = 1.0 - math.exp(-WARHEAD_K * ratio)
        p_guidance = max(0.0, min(1.0,
                                  1.0 - (miss_distance_m / self.lethal_radius) ** 0.7))

        return {
            'p_fuze': p_fuze,
            'p_lethality': p_lethality,
            'p_guidance': p_guidance,
            'pk_total': p_fuze * p_lethality * p_guidance,
            'miss_distance_m': miss_distance_m
        }

    def compute_pk_surface(self, ranges_m: np.ndarray,
                           aspects_deg: np.ndarray,
                           engagement_fn=None) -> dict:
        """Compute Pk surface over range × aspect grid.

        engagement_fn: callable(range_m, aspect_deg) -> miss_distance_m
        Returns dict with grid data.
        """
        pk_grid = np.zeros((len(ranges_m), len(aspects_deg)))
        miss_grid = np.zeros_like(pk_grid)

        for i, r in enumerate(ranges_m):
            for j, a in enumerate(aspects_deg):
                if engagement_fn is not None:
                    miss = engagement_fn(r, a)
                else:
                    # Default: miss increases with range, worse at tail
                    aspect_factor = 1.0 + 2.0 * abs(math.sin(math.radians(a / 2)))
                    miss = (r / 5000.0) * aspect_factor
                miss_grid[i, j] = miss
                pk_grid[i, j] = self.compute_pk(miss)

        return {
            'ranges_m': ranges_m.tolist(),
            'aspects_deg': aspects_deg.tolist(),
            'pk_grid': pk_grid.tolist(),
            'miss_grid': miss_grid.tolist()
        }

    def pk_vs_range(self, aspect_deg: float, altitude_m: float = 8000.0,
                    engagement_fn=None, n_points: int = 50) -> dict:
        """Compute Pk vs range curve for a fixed aspect angle."""
        ranges = np.linspace(2000, 80000, n_points)
        pks = []
        for r in ranges:
            if engagement_fn is not None:
                miss = engagement_fn(r, aspect_deg)
            else:
                aspect_factor = 1.0 + 2.0 * abs(
                    math.sin(math.radians(aspect_deg / 2)))
                miss = (r / 5000.0) * aspect_factor
            pks.append(self.compute_pk(miss))

        return {
            'range_m': ranges.tolist(),
            'pk': pks,
            'aspect_deg': aspect_deg,
            'altitude_m': altitude_m
        }
