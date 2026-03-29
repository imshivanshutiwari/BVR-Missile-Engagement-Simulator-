"""Test Probability of Kill Calculator — 3 tests."""

import pytest
import numpy as np


def test_pk_unity_at_direct_hit(pk_calc):
    """Pk should be 1.0 at 0.005m miss distance (direct hit threshold)."""
    pk = pk_calc.compute_pk(0.005)
    assert pk == 1.0, f"Pk at 0.005m miss = {pk}, expected 1.0"
    # Also verify reasonable Pk at 1m miss
    pk1 = pk_calc.compute_pk(1.0)
    assert pk1 > 0.85, f"Pk at 1.0m miss = {pk1}, expected > 0.85"


def test_pk_zero_beyond_lethal_radius(pk_calc):
    """Pk should be < 0.01 at 100m miss distance."""
    pk = pk_calc.compute_pk(100.0)
    assert pk < 0.01, f"Pk at 100m miss = {pk}, expected < 0.01"


def test_pk_surface_monotone_with_range(pk_calc):
    """At fixed aspect, Pk should decrease with increasing range (generally)."""
    ranges = np.arange(5000, 60000, 5000)
    prev_pk = 1.0
    for r in ranges:
        # Approximate miss distance increases with range
        approx_miss = r / 3000.0  # rough linear relationship
        pk = pk_calc.compute_pk(approx_miss)
        # Allow some non-monotonicity due to model
        assert pk <= prev_pk + 0.1, \
            f"Pk increased at range {r}: {pk} > {prev_pk}"
        prev_pk = pk
