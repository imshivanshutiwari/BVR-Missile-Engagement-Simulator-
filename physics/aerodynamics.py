"""Missile Aerodynamics — Drag Polar Cd(Mach) with Transonic Bump.

Complete aerodynamic model for a generic BVR AAM (ASTRA/AIM-120 class).
Includes: zero-lift drag Cd0(Mach), wave drag, induced drag, lift coefficient.
"""

import math
import numpy as np
from scipy.interpolate import interp1d
from physics.constants import (
    MISSILE_REF_AREA, ASPECT_RATIO, OSWALD_EFFICIENCY,
    CD0_MACH_TABLE, CD0_VALUES
)
from physics.atmosphere import StandardAtmosphere1976


class MissileAerodynamics:
    """Complete aerodynamic model for BVR air-to-air missile."""

    def __init__(self, atmosphere: StandardAtmosphere1976 = None):
        self.S_ref = MISSILE_REF_AREA
        self.AR = ASPECT_RATIO
        self.e = OSWALD_EFFICIENCY
        self.atm = atmosphere or StandardAtmosphere1976()

        # Build cubic spline for Cd0 vs Mach
        self._cd0_interp = interp1d(
            CD0_MACH_TABLE, CD0_VALUES,
            kind='cubic', fill_value='extrapolate'
        )

    def cd_zero(self, mach: float) -> float:
        """Zero-lift drag coefficient Cd0 from Mach table (cubic interpolation)."""
        mach = max(0.3, min(mach, 5.0))
        return float(self._cd0_interp(mach))

    def cd_wave(self, mach: float) -> float:
        """Wave drag correction in the transonic regime (0.8 < M < 1.2)."""
        if 0.8 < mach < 1.2:
            cd0 = self.cd_zero(mach)
            return cd0 * 0.4 * (mach - 0.8) ** 2
        return 0.0

    def cd_induced(self, cl: float) -> float:
        """Induced drag from lift: Cd_i = CL^2 / (pi * AR * e)."""
        return cl ** 2 / (math.pi * self.AR * self.e)

    def cl(self, alpha_rad: float, mach: float) -> float:
        """Lift coefficient CL(alpha, Mach).

        Subsonic: CL = 2*pi*alpha (thin-airfoil theory)
        Supersonic: CL = 4*alpha / sqrt(M^2 - 1) (Ackeret / linearized)
        Smooth blend through transonic using tanh.
        """
        cl_sub = 2.0 * math.pi * alpha_rad
        # Prevent sqrt of negative / zero
        m2 = max(mach * mach, 1.01)
        cl_super = 4.0 * alpha_rad / math.sqrt(m2 - 1.0)

        # Smooth blend: sigma goes 0→1 as Mach crosses 1.0
        sigma = 0.5 * (1.0 + math.tanh(10.0 * (mach - 1.0)))
        return (1.0 - sigma) * cl_sub + sigma * cl_super

    def cd_total(self, mach: float, alpha_rad: float, h_m: float = 0.0) -> float:
        """Total drag coefficient: Cd0 + Cd_wave + Cd_induced."""
        cd0 = self.cd_zero(mach)
        cdw = self.cd_wave(mach)
        cl_val = self.cl(alpha_rad, mach)
        cdi = self.cd_induced(cl_val)
        return cd0 + cdw + cdi

    def drag_force(self, velocity_ms: float, alpha_rad: float, h_m: float) -> float:
        """Drag force D = Cd_total * q * S_ref in Newtons."""
        mach = self.atm.mach_number(velocity_ms, h_m)
        cd = self.cd_total(mach, alpha_rad, h_m)
        q = self.atm.dynamic_pressure(velocity_ms, h_m)
        return cd * q * self.S_ref

    def lift_force(self, velocity_ms: float, alpha_rad: float, h_m: float) -> float:
        """Lift force L = CL * q * S_ref in Newtons."""
        mach = self.atm.mach_number(velocity_ms, h_m)
        cl_val = self.cl(alpha_rad, mach)
        q = self.atm.dynamic_pressure(velocity_ms, h_m)
        return cl_val * q * self.S_ref
