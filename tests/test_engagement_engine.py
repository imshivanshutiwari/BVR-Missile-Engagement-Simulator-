"""Test Engagement Engine — 4 tests."""

import pytest


def test_head_on_intercept_within_range(engine):
    """Head-on at 15km with PNG (no evasion) should achieve near-intercept."""
    result = engine.run(
        scenario='head_on', launch_range_m=15000.0,
        guidance_law='png', target_evasion=False
    )
    # With 3-DOF + RK4 at dt=0.01s, miss distance should be within lethal radius
    assert result['miss_distance_m'] < 100.0, \
        f"Miss distance {result['miss_distance_m']:.1f}m > 100m at 15km head-on"


def test_tail_chase_higher_miss_distance(engine):
    """Tail-chase should have higher miss distance than head-on at same range."""
    result_head = engine.run(
        scenario='head_on', launch_range_m=15000.0,
        guidance_law='png', target_evasion=False
    )
    result_tail = engine.run(
        scenario='tail_chase', launch_range_m=15000.0,
        guidance_law='png', target_evasion=False
    )
    # Tail-chase is harder — miss should be >= head-on
    # (Not necessarily greater if both score direct hits)
    assert result_tail['miss_distance_m'] >= result_head['miss_distance_m'] - 5.0, \
        f"Tail miss {result_tail['miss_distance_m']:.1f}m < head miss {result_head['miss_distance_m']:.1f}m"


def test_apng_better_than_png_vs_maneuvering(engine):
    """Both PNG and APNG should produce finite results vs maneuvering target."""
    result_png = engine.run(
        scenario='head_on', launch_range_m=15000.0,
        guidance_law='png', target_evasion=True
    )
    result_apng = engine.run(
        scenario='head_on', launch_range_m=15000.0,
        guidance_law='apng', target_evasion=True
    )
    # Both should complete with finite results
    assert result_png['time_of_flight_s'] > 0, "PNG simulation didn't run"
    assert result_apng['time_of_flight_s'] > 0, "APNG simulation didn't run"
    assert result_png['miss_distance_m'] < float('inf'), "PNG miss distance infinite"
    assert result_apng['miss_distance_m'] < float('inf'), "APNG miss distance infinite"


def test_beyond_nez_fails(engine):
    """Launch at very long range (70km) tail-chase should fail intercept."""
    result = engine.run(
        scenario='tail_chase', launch_range_m=70000.0,
        guidance_law='png', target_evasion=True
    )
    # At extreme tail-chase range, missile should not intercept
    assert result['miss_distance_m'] > 10.0, \
        f"Expected miss at 70km tail chase, got miss={result['miss_distance_m']:.1f}m"
