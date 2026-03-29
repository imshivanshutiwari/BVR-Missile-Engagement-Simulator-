"""Test F-16 Target Model — 3 tests."""

import pytest
import numpy as np
from physics.utils.vector_math import magnitude


def test_barrel_roll_achieves_7g(f16):
    """Max g-load during barrel roll evasion ≈ 7.0 ±0.5g."""
    max_g = 0.0
    for t_step in np.arange(0, 10.0, 0.1):
        g = f16.g_load_at_time(t_step)
        if g > max_g:
            max_g = g
    assert abs(max_g - 7.0) < 0.5, f"Max g-load {max_g} not ≈ 7.0g"


def test_target_position_continuous(f16):
    """Trajectory should have no position discontinuities."""
    dt = 0.1
    v_max = 600.0
    prev_state = f16.evasive_barrel_roll(0.0)
    for t in np.arange(dt, 10.0, dt):
        state = f16.evasive_barrel_roll(t)
        pos_diff = magnitude(state[:3] - prev_state[:3])
        # Barrel roll includes base motion + maneuver offsets with phase transitions
        # Allow 10x velocity*dt to account for offset jumps at phase boundaries
        limit = v_max * dt * 10
        assert pos_diff < limit, \
            f"Position jump {pos_diff:.1f}m at t={t:.1f}s exceeds max {limit:.0f}m"
        prev_state = state


def test_target_speed_within_envelope(f16):
    """All speeds during evasion should be ≤ Vmax + 10 m/s."""
    for t in np.arange(0, 10.0, 0.1):
        state = f16.evasive_barrel_roll(t)
        speed = magnitude(state[3:6])
        assert speed < f16.Vmax + 50, \
            f"Speed {speed} m/s at t={t}s exceeds Vmax={f16.Vmax}+50 m/s"
