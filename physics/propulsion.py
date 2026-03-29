"""Dual-Pulse Solid Rocket Motor Model.

Based on ASTRA Mk-2 / MICA class performance.
Boost phase → Sustain phase → Coast phase.
Altitude compensation for thrust.
"""

from physics.constants import (
    G0, P0_SEA,
    MISSILE_TOTAL_MASS, MISSILE_PROPELLANT_BOOST, MISSILE_PROPELLANT_SUSTAIN,
    MISSILE_EMPTY_MASS, BOOST_DURATION, BOOST_THRUST_SL, BOOST_ISP,
    SUSTAIN_END_TIME, SUSTAIN_THRUST_SL, SUSTAIN_ISP, ALTITUDE_THRUST_COEFF
)
from physics.atmosphere import StandardAtmosphere1976


class DualPulsePropulsion:
    """Dual-pulse boost-sustain solid rocket motor model."""

    def __init__(self, atmosphere: StandardAtmosphere1976 = None):
        self.atm = atmosphere or StandardAtmosphere1976()
        self.m_total = MISSILE_TOTAL_MASS
        self.m_prop_boost = MISSILE_PROPELLANT_BOOST
        self.m_prop_sustain = MISSILE_PROPELLANT_SUSTAIN
        self.m_empty = MISSILE_EMPTY_MASS
        self.t_boost = BOOST_DURATION
        self.t_sustain_end = SUSTAIN_END_TIME
        self.T_boost_sl = BOOST_THRUST_SL
        self.T_sustain_sl = SUSTAIN_THRUST_SL
        self.Isp_boost = BOOST_ISP
        self.Isp_sustain = SUSTAIN_ISP
        self.k_alt = ALTITUDE_THRUST_COEFF

        # Mass flow rates (constant within each phase)
        self._mdot_boost = self.m_prop_boost / self.t_boost
        self._mdot_sustain = self.m_prop_sustain / (self.t_sustain_end - self.t_boost)

    def _altitude_factor(self, h_m: float) -> float:
        """Thrust altitude compensation factor: T(h) = T_sl * (1 + k*(P0-P(h))/P0)."""
        P = self.atm.pressure(h_m)
        return 1.0 + self.k_alt * (P0_SEA - P) / P0_SEA

    def phase(self, t_sec: float) -> str:
        """Return current motor phase: BOOST, SUSTAIN, or COAST."""
        if t_sec < 0:
            return "PRE-LAUNCH"
        if t_sec <= self.t_boost:
            return "BOOST"
        if t_sec <= self.t_sustain_end:
            return "SUSTAIN"
        return "COAST"

    def is_burning(self, t_sec: float) -> bool:
        """True if motor is producing thrust."""
        return t_sec <= self.t_sustain_end and t_sec >= 0

    def thrust(self, t_sec: float, h_m: float = 0.0) -> float:
        """Thrust in Newtons at time t and altitude h.

        Includes altitude compensation.
        """
        ph = self.phase(t_sec)
        alt_factor = self._altitude_factor(h_m)

        if ph == "BOOST":
            return self.T_boost_sl * alt_factor
        elif ph == "SUSTAIN":
            return self.T_sustain_sl * alt_factor
        else:
            return 0.0

    def mass_flow_rate(self, t_sec: float, h_m: float = 0.0) -> float:
        """Mass flow rate m_dot = -T / (Isp * g0) in kg/s (negative = losing mass)."""
        ph = self.phase(t_sec)
        if ph == "BOOST":
            T = self.thrust(t_sec, h_m)
            return -T / (self.Isp_boost * G0)
        elif ph == "SUSTAIN":
            T = self.thrust(t_sec, h_m)
            return -T / (self.Isp_sustain * G0)
        return 0.0

    def mass(self, t_sec: float) -> float:
        """Remaining missile mass at time t (simplified linear depletion)."""
        if t_sec <= 0:
            return self.m_total

        if t_sec <= self.t_boost:
            consumed = self._mdot_boost * t_sec
            return self.m_total - consumed

        mass_after_boost = self.m_total - self.m_prop_boost

        if t_sec <= self.t_sustain_end:
            dt_sustain = t_sec - self.t_boost
            consumed = self._mdot_sustain * dt_sustain
            return mass_after_boost - consumed

        return self.m_empty
