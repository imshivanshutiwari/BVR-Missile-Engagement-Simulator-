"""Test Missile Aerodynamics — 4 tests."""

import pytest
import numpy as np


def test_cd0_transonic_bump_exists(aero):
    """Cd0 at Mach 0.9 > Cd0 at Mach 0.7, and Cd0 at Mach 1.5 < Cd0 at Mach 1.0."""
    cd09 = aero.cd_zero(0.9)
    cd07 = aero.cd_zero(0.7)
    cd15 = aero.cd_zero(1.5)
    cd10 = aero.cd_zero(1.0)
    assert cd09 > cd07, f"Transonic bump missing: Cd0(0.9)={cd09} not > Cd0(0.7)={cd07}"
    assert cd15 < cd10, f"Supersonic decay missing: Cd0(1.5)={cd15} not < Cd0(1.0)={cd10}"


def test_cd_total_increases_with_alpha(aero):
    """Cd_total at alpha=10° > Cd_total at alpha=0° (induced drag)."""
    cd_0 = aero.cd_total(2.0, 0.0)
    cd_10 = aero.cd_total(2.0, np.deg2rad(10.0))
    assert cd_10 > cd_0, f"Induced drag not working: Cd(α=10°)={cd_10} not > Cd(α=0)={cd_0}"


def test_drag_force_correct_magnitude(aero):
    """Drag force at 800 m/s, 0° alpha, 10000m should be 20-300 N for 178mm body."""
    drag = aero.drag_force(800.0, 0.0, 10000.0)
    assert 20 < drag < 300, f"Drag force {drag}N outside physical range [20, 300]N for S_ref=0.025m²"


def test_lift_positive_for_positive_alpha(aero):
    """Lift force should be positive for positive angle of attack."""
    lift = aero.lift_force(500.0, np.deg2rad(5.0), 8000.0)
    assert lift > 0, f"Lift force {lift}N should be positive for α=5°"
