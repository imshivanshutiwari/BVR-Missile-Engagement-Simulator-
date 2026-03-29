"""Test Dual-Pulse Propulsion — 4 tests (3 thrust + 1 mass)."""

import pytest


def test_boost_thrust_correct(prop):
    """Thrust at t=1.0s, sea level ≈ 15000 ±200 N."""
    thrust = prop.thrust(1.0, 0.0)
    assert abs(thrust - 15000.0) < 200, f"Boost thrust {thrust}N not ≈ 15000N"


def test_sustain_thrust_correct(prop):
    """Thrust at t=5.0s, sea level ≈ 3200 ±100 N."""
    thrust = prop.thrust(5.0, 0.0)
    assert abs(thrust - 3200.0) < 100, f"Sustain thrust {thrust}N not ≈ 3200N"


def test_coast_thrust_zero(prop):
    """Thrust at t=25.0s should be exactly 0."""
    thrust = prop.thrust(25.0, 0.0)
    assert thrust == 0.0, f"Coast thrust {thrust}N not == 0"


def test_mass_decreases_during_burn(prop):
    """Mass at t=3.0s < mass at t=0, and mass at t=25.0 ≈ empty mass."""
    m0 = prop.mass(0.0)
    m3 = prop.mass(3.0)
    m25 = prop.mass(25.0)
    assert m3 < m0, f"Mass not decreasing: m(3)={m3} not < m(0)={m0}"
    assert abs(m25 - 145.0) < 0.5, f"Empty mass {m25}kg not ≈ 145.0kg"
