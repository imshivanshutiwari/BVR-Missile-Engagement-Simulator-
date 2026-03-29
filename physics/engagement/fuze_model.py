"""Proximity Fuze + Warhead Lethality Model.

Models fuze actuation probability and fragmentation lethality
as a function of miss distance.
"""

import math
from physics.constants import FUZE_RADIUS, LETHAL_RADIUS, FUZE_K, WARHEAD_K


class ProximityFuze:
    """Proximity fuze and warhead lethality model."""

    def __init__(self, fuze_radius: float = FUZE_RADIUS,
                 lethal_radius: float = LETHAL_RADIUS,
                 k_fuze: float = FUZE_K,
                 k_warhead: float = WARHEAD_K):
        self.fuze_radius = fuze_radius
        self.lethal_radius = lethal_radius
        self.k_fuze = k_fuze
        self.k_warhead = k_warhead

    def fuze_actuation_probability(self, miss_distance_m: float) -> float:
        """Probability that proximity fuze fires.

        P_fuze = 1 - exp(-k_f * (R_lethal / miss_dist)^2)
        """
        if miss_distance_m < 0.01:
            return 1.0
        ratio = (self.lethal_radius / miss_distance_m) ** 2
        return 1.0 - math.exp(-self.k_fuze * ratio)

    def warhead_lethality(self, miss_distance_m: float) -> float:
        """Warhead lethality given fuze fires.

        P_lethality = 1 - exp(-k_w * (R_lethal / miss_dist)^2)
        """
        if miss_distance_m < 0.01:
            return 1.0
        ratio = (self.lethal_radius / miss_distance_m) ** 2
        return 1.0 - math.exp(-self.k_warhead * ratio)

    def is_within_fuze_range(self, miss_distance_m: float) -> bool:
        """Check if target is within fuze activation range."""
        return miss_distance_m <= self.fuze_radius

    def damage_assessment(self, miss_distance_m: float) -> dict:
        """Full damage assessment for a given miss distance."""
        p_fuze = self.fuze_actuation_probability(miss_distance_m)
        p_lethality = self.warhead_lethality(miss_distance_m)
        p_kill = p_fuze * p_lethality

        return {
            'miss_distance_m': miss_distance_m,
            'p_fuze': p_fuze,
            'p_lethality': p_lethality,
            'p_kill': p_kill,
            'fuze_activated': miss_distance_m <= self.fuze_radius,
            'target_destroyed': p_kill > 0.5
        }
