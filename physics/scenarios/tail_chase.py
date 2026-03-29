"""Tail-Chase Engagement Scenario.

Both aircraft heading same direction, missile chasing from behind.
Low closing velocity, energy-critical engagement.
"""


class TailChaseScenario:
    """Tail-chase BVR engagement setup."""

    ID = "tail_chase"
    NAME = "Tail-Chase Engagement"
    DESCRIPTION = (
        "Missile pursues target from rear hemisphere. Both heading same direction. "
        "Low closing velocity (~50-150 m/s). Missile must close gap using "
        "superior speed. Longer TOF, lower Pk. Energy management critical."
    )
    GEOMETRY_DIAGRAM = "M →→→→→→ T →→→→→→"

    DEFAULT_PARAMS = {
        'launch_range_m': 15000.0,
        'launch_altitude_m': 8000.0,
        'target_speed_ms': 250.0,
        'target_altitude_m': 8000.0,
        'guidance_law': 'png',
        'target_evasion': True
    }

    EXPECTED_TOF_RANGE = (20.0, 60.0)
    TYPICAL_PK_RANGE = (0.30, 0.75)

    @classmethod
    def to_dict(cls) -> dict:
        return {
            'id': cls.ID,
            'name': cls.NAME,
            'description': cls.DESCRIPTION,
            'geometry_diagram': cls.GEOMETRY_DIAGRAM,
            'default_params': cls.DEFAULT_PARAMS,
            'expected_tof_s': list(cls.EXPECTED_TOF_RANGE),
            'typical_pk_range': list(cls.TYPICAL_PK_RANGE)
        }
