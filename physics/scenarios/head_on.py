"""Head-On Engagement Scenario.

Missile heading east, target heading west.
Maximum closing velocity, most favorable geometry.
"""


class HeadOnScenario:
    """Head-on BVR engagement setup."""

    ID = "head_on"
    NAME = "Head-On Engagement"
    DESCRIPTION = (
        "Classic BVR head-on geometry. Missile and target approach each other "
        "on reciprocal headings. Maximum closing velocity (~700 m/s combined). "
        "Most favorable for missile — smallest NEZ, highest Pk."
    )
    GEOMETRY_DIAGRAM = "M →→→→→→ ←←←←←← T"

    DEFAULT_PARAMS = {
        'launch_range_m': 20000.0,
        'launch_altitude_m': 8000.0,
        'target_speed_ms': 250.0,
        'target_altitude_m': 8000.0,
        'guidance_law': 'png',
        'target_evasion': True
    }

    EXPECTED_TOF_RANGE = (8.0, 25.0)
    TYPICAL_PK_RANGE = (0.70, 0.98)

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
