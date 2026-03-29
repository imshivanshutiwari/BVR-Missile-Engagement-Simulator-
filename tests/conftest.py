"""Pytest Fixtures — Real physics instances for all tests."""

import sys
import os
import pytest
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from physics.atmosphere import StandardAtmosphere1976
from physics.aerodynamics import MissileAerodynamics
from physics.propulsion import DualPulsePropulsion
from physics.equations_of_motion import PointMassEOM
from physics.guidance.png_law import ProportionalNavigation
from physics.guidance.apng_law import AugmentedProportionalNavigation
from physics.target.f16_model import F16KinematicModel
from physics.engagement.engagement_engine import EngagementEngine
from physics.engagement.nez_computer import NoEscapeZoneComputer
from physics.engagement.pk_calculator import ProbabilityOfKillCalculator


@pytest.fixture
def std_atm():
    return StandardAtmosphere1976()


@pytest.fixture
def aero():
    return MissileAerodynamics()


@pytest.fixture
def prop():
    return DualPulsePropulsion()


@pytest.fixture
def png_law():
    return ProportionalNavigation(N=4.0)


@pytest.fixture
def apng_law():
    return AugmentedProportionalNavigation(N=4.0)


@pytest.fixture
def f16():
    return F16KinematicModel()


@pytest.fixture
def eom():
    return PointMassEOM()


@pytest.fixture
def engine():
    return EngagementEngine()


@pytest.fixture
def nez():
    return NoEscapeZoneComputer()


@pytest.fixture
def pk_calc():
    return ProbabilityOfKillCalculator()
