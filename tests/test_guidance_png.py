"""Test Proportional Navigation Guidance — 4 tests."""

import pytest
import numpy as np
from physics.utils.vector_math import magnitude


def test_closing_velocity_head_on(png_law):
    """Head-on: missile east at 500, target west at 200 → Vc ≈ 700 m/s."""
    missile = np.array([0, 0, 0, 500, 0, 0], dtype=float)
    target = np.array([50000, 0, 0, -200, 0, 0], dtype=float)
    vc = png_law.closing_velocity(missile, target)
    assert abs(vc - 700.0) < 5.0, f"Closing velocity {vc} not ≈ 700 m/s"


def test_los_rate_zero_for_collision_course(png_law):
    """Perfect collision course → LOS rate ≈ 0."""
    missile = np.array([0, 0, 0, 500, 0, 0], dtype=float)
    target = np.array([50000, 0, 0, -200, 0, 0], dtype=float)
    los = png_law.los_rate(missile, target)
    assert magnitude(los) < 1e-6, f"|lambda_dot| = {magnitude(los)} not < 1e-6"


def test_png_commands_toward_target(png_law):
    """Off-axis missile → PNG command should have non-zero lateral correction."""
    missile = np.array([0, 1000, 0, 500, 0, 0], dtype=float)
    target = np.array([50000, 0, 0, -200, 0, 0], dtype=float)
    a_cmd = png_law.compute(missile, target)
    # PNG must produce lateral/vertical acceleration to correct the offset
    lateral_mag = np.sqrt(a_cmd[1]**2 + a_cmd[2]**2)
    assert lateral_mag > 0.1, f"PNG lateral command {lateral_mag} m/s² too small for 1km offset"


def test_acceleration_limit_enforced(png_law):
    """Large LOS rate → acceleration should be clipped to 30g."""
    missile = np.array([0, 5000, 0, 500, 0, 0], dtype=float)
    target = np.array([5000, 0, 0, -200, 500, 0], dtype=float)
    a_cmd = png_law.compute(missile, target)
    a_mag = magnitude(a_cmd)
    max_accel = 30.0 * 9.80665
    assert a_mag <= max_accel + 1.0, \
        f"|a_cmd| = {a_mag} m/s² exceeds 30g = {max_accel} m/s²"
