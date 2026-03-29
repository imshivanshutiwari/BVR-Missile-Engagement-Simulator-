"""No-Escape Zone (NEZ) Computer.

Computes the NEZ and Launch Acceptability Region (LAR)
by sweeping aspect angles and ranges, running full engagement
simulations at each point.
"""

import numpy as np
import math
from physics.engagement.engagement_engine import EngagementEngine
from physics.engagement.pk_calculator import ProbabilityOfKillCalculator
from physics.constants import FUZE_RADIUS


class NoEscapeZoneComputer:
    """Computes NEZ and LAR envelopes."""

    def __init__(self):
        self.engine = EngagementEngine()
        self.pk_calc = ProbabilityOfKillCalculator()

    def compute_nez_slice(self, altitude_m: float = 8000.0,
                          target_speed: float = 250.0,
                          guidance_law: str = "png",
                          n_aspect: int = 32,
                          n_range: int = 25) -> dict:
        """Compute NEZ for a single altitude slice.

        Sweeps aspect (0-360°) and range (2-60km).
        Returns 2D boolean matrix [range × aspect].
        """
        aspects = np.linspace(0, 360, n_aspect, endpoint=False)
        ranges = np.linspace(2000, 60000, n_range)

        nez_matrix = np.zeros((n_range, n_aspect), dtype=bool)
        miss_matrix = np.zeros((n_range, n_aspect))
        pk_matrix = np.zeros((n_range, n_aspect))

        nez_points = []

        for i, r in enumerate(ranges):
            for j, aspect in enumerate(aspects):
                # Convert aspect angle to scenario geometry
                # 0° = head-on, 180° = tail-chase
                if aspect < 45 or aspect > 315:
                    scenario = "head_on"
                elif 135 < aspect < 225:
                    scenario = "tail_chase"
                else:
                    scenario = "crossing"

                try:
                    result = self.engine.run(
                        scenario=scenario,
                        launch_range_m=float(r),
                        launch_altitude_m=altitude_m,
                        target_speed_ms=target_speed,
                        target_altitude_m=altitude_m,
                        guidance_law=guidance_law,
                        target_evasion=True,
                        dt=0.05  # coarser dt for NEZ sweep speed
                    )

                    miss = result['miss_distance_m']
                    pk = result['pk']
                    is_nez = miss < FUZE_RADIUS

                    nez_matrix[i, j] = is_nez
                    miss_matrix[i, j] = miss
                    pk_matrix[i, j] = pk

                    nez_points.append({
                        'range_m': float(r),
                        'aspect_deg': float(aspect),
                        'altitude_m': altitude_m,
                        'is_nez': bool(is_nez),
                        'miss_distance_m': float(miss),
                        'pk': float(pk)
                    })

                except Exception:
                    nez_matrix[i, j] = False
                    miss_matrix[i, j] = float('inf')
                    pk_matrix[i, j] = 0.0
                    nez_points.append({
                        'range_m': float(r),
                        'aspect_deg': float(aspect),
                        'altitude_m': altitude_m,
                        'is_nez': False,
                        'miss_distance_m': float('inf'),
                        'pk': 0.0
                    })

        return {
            'nez_points': nez_points,
            'nez_matrix': nez_matrix.tolist(),
            'miss_matrix': miss_matrix.tolist(),
            'pk_matrix': pk_matrix.tolist(),
            'ranges_m': ranges.tolist(),
            'aspects_deg': aspects.tolist(),
            'altitude_m': altitude_m,
            'total_sims': n_aspect * n_range
        }

    def compute_full_nez(self, target_params: dict = None,
                         guidance_law: str = "png",
                         n_aspect: int = 16,
                         n_range: int = 12) -> list:
        """Compute full 3D NEZ across altitude bands.

        target_params: {'speed': m/s, 'alt': m}
        Returns list of NEZ points.
        """
        if target_params is None:
            target_params = {'speed': 250.0, 'alt': 8000.0}

        speed = target_params.get('speed', 250.0)
        base_alt = target_params.get('alt', 8000.0)

        altitudes = [
            max(1000.0, base_alt - 3000.0),
            base_alt,
            min(20000.0, base_alt + 3000.0)
        ]

        all_points = []
        for alt in altitudes:
            result = self.compute_nez_slice(
                altitude_m=alt,
                target_speed=speed,
                guidance_law=guidance_law,
                n_aspect=n_aspect,
                n_range=n_range
            )
            all_points.extend(result['nez_points'])

        return all_points

    def compute_lar(self, altitude_m: float = 8000.0,
                    target_speed: float = 250.0,
                    guidance_law: str = "png",
                    n_aspect: int = 24) -> dict:
        """Compute Launch Acceptability Region.

        R_min: minimum range for fuze activation
        R_max: maximum range for sufficient energy
        """
        aspects = np.linspace(0, 345, n_aspect)
        r_min_array = []
        r_max_array = []

        for aspect in aspects:
            if aspect < 45 or aspect > 315:
                scenario = "head_on"
            elif 135 < aspect < 225:
                scenario = "tail_chase"
            else:
                scenario = "crossing"

            # Find R_max: sweep from far to near, find first intercept
            r_max = 2000.0
            for r in np.linspace(60000, 2000, 15):
                try:
                    result = self.engine.run(
                        scenario=scenario, launch_range_m=float(r),
                        launch_altitude_m=altitude_m,
                        target_speed_ms=target_speed,
                        target_altitude_m=altitude_m,
                        guidance_law=guidance_law,
                        target_evasion=True, dt=0.05
                    )
                    if result['intercept_achieved']:
                        r_max = float(r)
                        break
                except Exception:
                    continue

            # R_min: minimum arming distance (~1.5 km typical)
            r_min = 1500.0

            r_min_array.append(r_min)
            r_max_array.append(r_max)

        return {
            'r_min': r_min_array,
            'r_max': r_max_array,
            'aspect': aspects.tolist()
        }

    def export_nez_mesh(self, nez_points: list) -> dict:
        """Convert NEZ points to Three.js-compatible geometry."""
        vertices = []
        colors = []

        for pt in nez_points:
            r = pt['range_m']
            theta = math.radians(pt['aspect_deg'])
            alt = pt.get('altitude_m', 8000.0)
            pk = pt.get('pk', 0.0)

            x = r * math.cos(theta)
            y = r * math.sin(theta)
            z = -alt

            vertices.extend([x, y, z])

            # Color: green (high Pk) to red (low Pk)
            colors.extend([1.0 - pk, pk, 0.3, max(0.2, pk)])

        return {
            'vertices': vertices,
            'colors': colors,
            'point_count': len(nez_points)
        }
