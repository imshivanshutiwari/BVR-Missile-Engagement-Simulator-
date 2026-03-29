"""Test NEZ Computer — 4 tests."""

import pytest
import numpy as np


def test_nez_head_on_larger_than_tail_chase(nez):
    """NEZ range at head-on (0°) should be larger than tail-chase (180°)."""
    result = nez.compute_nez_slice(
        altitude_m=8000, target_speed=250,
        guidance_law='png', n_aspect=8, n_range=6
    )
    # Find max range where is_nez=True for head-on (aspect~0) and tail (aspect~180)
    head_on_max = 0
    tail_max = 0
    for pt in result['nez_points']:
        if pt['is_nez']:
            if pt['aspect_deg'] < 45:
                head_on_max = max(head_on_max, pt['range_m'])
            elif 135 < pt['aspect_deg'] < 225:
                tail_max = max(tail_max, pt['range_m'])

    assert head_on_max >= tail_max, \
        f"Head-on NEZ {head_on_max/1000:.0f}km not >= tail NEZ {tail_max/1000:.0f}km"


def test_nez_boundary_is_closed_curve(nez):
    """NEZ should have computed values for all aspect angles."""
    result = nez.compute_nez_slice(
        altitude_m=8000, target_speed=250,
        guidance_law='png', n_aspect=8, n_range=6
    )
    aspects_covered = set()
    for pt in result['nez_points']:
        aspects_covered.add(round(pt['aspect_deg']))

    assert len(aspects_covered) >= 8, \
        f"Only {len(aspects_covered)} aspects covered, expected >= 8"


def test_nez_shrinks_with_target_speed(nez):
    """NEZ should shrink when target speed increases (harder to catch)."""
    result_slow = nez.compute_nez_slice(
        altitude_m=8000, target_speed=200,
        guidance_law='png', n_aspect=8, n_range=6
    )
    result_fast = nez.compute_nez_slice(
        altitude_m=8000, target_speed=400,
        guidance_law='png', n_aspect=8, n_range=6
    )
    slow_nez = sum(1 for p in result_slow['nez_points'] if p['is_nez'])
    fast_nez = sum(1 for p in result_fast['nez_points'] if p['is_nez'])
    assert slow_nez >= fast_nez, \
        f"Slow target NEZ ({slow_nez} pts) not >= fast target NEZ ({fast_nez} pts)"


def test_lar_r_max_greater_r_min_all_aspects(nez):
    """R_max should be > R_min for all computed aspects."""
    lar = nez.compute_lar(
        altitude_m=8000, target_speed=250,
        guidance_law='png', n_aspect=8
    )
    for i in range(len(lar['r_max'])):
        assert lar['r_max'][i] >= lar['r_min'][i], \
            f"R_max ({lar['r_max'][i]}) < R_min ({lar['r_min'][i]}) at aspect {lar['aspect'][i]}°"
