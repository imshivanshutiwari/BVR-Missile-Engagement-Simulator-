"""90° Crossing Engagement Scenario.

Target moving perpendicular to missile heading.
High angular rate, demanding on guidance law.
"""


class CrossingScenario:
    """90-degree crossing BVR engagement setup."""

    ID = "crossing"
    NAME = "90° Crossing Engagement"
    DESCRIPTION = (
        "Target crossing at 90° to missile heading. High line-of-sight rate "
        "demands aggressive guidance corrections. Moderate closing velocity. "
        "Tests PNG lateral acceleration authority. Moderate Pk."
    )
    GEOMETRY_DIAGRAM = "M →→→→→→  T ↑↑↑↑↑↑"

    DEFAULT_PARAMS = {
        'launch_range_m': 18000.0,
        'launch_altitude_m': 8000.0,
        'target_speed_ms': 250.0,
        'target_altitude_m': 8000.0,
        'guidance_law': 'png',
        'target_evasion': True
    }

    EXPECTED_TOF_RANGE = (12.0, 40.0)
    TYPICAL_PK_RANGE = (0.45, 0.85)

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
