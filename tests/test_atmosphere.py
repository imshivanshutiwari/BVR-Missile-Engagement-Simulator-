"""Test US Standard Atmosphere 1976 — 4 tests."""

import pytest
import math


def test_sea_level_values_correct(std_atm):
    """T(0)=288.15K, P(0)=101325Pa, rho(0)=1.225, a(0)=340.29."""
    assert abs(std_atm.temperature(0) - 288.15) < 0.01
    assert abs(std_atm.pressure(0) - 101325.0) < 1.0
    assert abs(std_atm.density(0) - 1.225) < 0.001
    assert abs(std_atm.speed_of_sound(0) - 340.29) < 0.5


def test_tropopause_correct(std_atm):
    """T(11000)=216.65K, T(12000)=216.65K (isothermal layer)."""
    assert abs(std_atm.temperature(11000) - 216.65) < 0.1
    assert abs(std_atm.temperature(12000) - 216.65) < 0.1


def test_density_decreases_monotonically(std_atm):
    """Density should decrease with altitude from 0 to 20km."""
    densities = [std_atm.density(h) for h in range(0, 20001, 500)]
    for i in range(len(densities) - 1):
        assert densities[i] > densities[i + 1], \
            f"Density not monotonically decreasing at h={i*500}m"


def test_mach_number_at_cruise(std_atm):
    """Mach(250 m/s, 10000m) ≈ 0.84."""
    mach = std_atm.mach_number(250.0, 10000.0)
    assert abs(mach - 0.84) < 0.05, f"Expected Mach ≈ 0.84, got {mach}"
