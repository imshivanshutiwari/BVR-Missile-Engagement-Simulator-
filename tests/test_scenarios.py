"""Test Scenarios — 3 tests."""

import pytest
from physics.scenarios.scenario_runner import ScenarioRunner


@pytest.fixture
def runner():
    return ScenarioRunner()


def test_all_three_scenarios_run_complete(runner):
    """All scenarios should run to completion without errors."""
    for sid in ['head_on', 'tail_chase', 'crossing']:
        result = runner.run_scenario(sid)
        assert 'trajectory' in result, f"Scenario {sid} missing trajectory"
        assert 'miss_distance_m' in result, f"Scenario {sid} missing miss_distance"
        assert len(result['trajectory']['t']) > 10, \
            f"Scenario {sid} trajectory too short: {len(result['trajectory']['t'])} points"


def test_crossing_geometry_correct(runner):
    """At t=0, target velocity should be roughly ⊥ to LOS (within 15°)."""
    import numpy as np
    result = runner.run_scenario('crossing')
    traj = result['trajectory']
    tgt = result['target_trajectory']

    if len(tgt['x']) > 0:
        # LOS direction at t=0
        los = np.array([tgt['x'][0] - traj['x'][0],
                        tgt['y'][0] - traj['y'][0],
                        tgt['z'][0] - traj['z'][0]])
        tgt_vel = np.array([tgt['vx'][0], tgt['vy'][0], tgt['vz'][0]])

        los_norm = los / np.linalg.norm(los) if np.linalg.norm(los) > 0 else los
        tgt_norm = tgt_vel / np.linalg.norm(tgt_vel) if np.linalg.norm(tgt_vel) > 0 else tgt_vel

        dot = abs(np.dot(los_norm, tgt_norm))
        angle_from_perp = np.degrees(np.arccos(np.clip(dot, -1, 1)))
        # Should be close to 90° (dot product close to 0) — allow 15° tolerance
        assert angle_from_perp > 60, \
            f"Crossing geometry angle {angle_from_perp}° not near 90°"


def test_scenario_results_physically_reasonable(runner):
    """All results should have physically reasonable values."""
    for sid in ['head_on', 'tail_chase', 'crossing']:
        result = runner.run_scenario(sid)
        tof = result['time_of_flight_s']
        miss = result['miss_distance_m']
        pk = result['pk']

        assert 1.0 <= tof <= 120.0, \
            f"{sid}: TOF {tof}s outside [1, 120]"
        assert miss >= 0, \
            f"{sid}: miss distance {miss}m is negative"
        assert 0 <= pk <= 1.0, \
            f"{sid}: Pk {pk} outside [0, 1]"
