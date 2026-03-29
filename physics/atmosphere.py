"""US Standard Atmosphere 1976 — Full 7-Layer ISA Model.

Valid from 0 to 86 km geopotential altitude.
Computes: temperature, pressure, density, speed of sound,
dynamic viscosity, Mach number, dynamic pressure.
"""

import math
from physics.constants import (
    R_AIR, GAMMA_AIR, G0, T0_SEA, P0_SEA, RHO0_SEA,
    MU0_SEA, SUTHERLAND_C, ISA_LAYER_ALTITUDES_KM, ISA_LAPSE_RATES_K_PER_KM
)


class StandardAtmosphere1976:
    """Full US Standard Atmosphere 1976 implementation."""

    def __init__(self):
        # Precompute base T and P for each layer boundary
        self._layer_alt_m = [h * 1000.0 for h in ISA_LAYER_ALTITUDES_KM]
        self._lapse_rates = [L / 1000.0 for L in ISA_LAPSE_RATES_K_PER_KM]  # K/m
        self._base_T = [0.0] * len(self._layer_alt_m)
        self._base_P = [0.0] * len(self._layer_alt_m)
        self._base_T[0] = T0_SEA
        self._base_P[0] = P0_SEA

        for i in range(1, len(self._layer_alt_m)):
            h_b = self._layer_alt_m[i - 1]
            h_t = self._layer_alt_m[i]
            L = self._lapse_rates[i - 1]
            T_b = self._base_T[i - 1]
            P_b = self._base_P[i - 1]
            dh = h_t - h_b

            if abs(L) < 1e-10:
                # Isothermal layer
                self._base_T[i] = T_b
                self._base_P[i] = P_b * math.exp(-G0 * dh / (R_AIR * T_b))
            else:
                # Gradient layer
                T_t = T_b + L * dh
                self._base_T[i] = T_t
                self._base_P[i] = P_b * (T_t / T_b) ** (-G0 / (L * R_AIR))

    def _find_layer(self, h_m: float) -> int:
        """Find the ISA layer index for a given altitude."""
        h_m = max(0.0, min(h_m, 86000.0))
        for i in range(len(self._layer_alt_m) - 1, 0, -1):
            if h_m >= self._layer_alt_m[i]:
                return i
        return 0

    def temperature(self, h_m: float) -> float:
        """Temperature in K at geopotential altitude h_m (meters)."""
        h_m = max(0.0, min(h_m, 86000.0))
        i = self._find_layer(h_m)
        T_b = self._base_T[i]
        L = self._lapse_rates[i]
        dh = h_m - self._layer_alt_m[i]
        return T_b + L * dh

    def pressure(self, h_m: float) -> float:
        """Pressure in Pa at geopotential altitude h_m (meters)."""
        h_m = max(0.0, min(h_m, 86000.0))
        i = self._find_layer(h_m)
        T_b = self._base_T[i]
        P_b = self._base_P[i]
        L = self._lapse_rates[i]
        dh = h_m - self._layer_alt_m[i]

        if abs(L) < 1e-10:
            return P_b * math.exp(-G0 * dh / (R_AIR * T_b))
        else:
            T = T_b + L * dh
            return P_b * (T / T_b) ** (-G0 / (L * R_AIR))

    def density(self, h_m: float) -> float:
        """Air density in kg/m³ at altitude h_m."""
        T = self.temperature(h_m)
        P = self.pressure(h_m)
        return P / (R_AIR * T)

    def speed_of_sound(self, h_m: float) -> float:
        """Speed of sound in m/s at altitude h_m."""
        T = self.temperature(h_m)
        return math.sqrt(GAMMA_AIR * R_AIR * T)

    def dynamic_viscosity(self, h_m: float) -> float:
        """Dynamic viscosity in Pa·s via Sutherland's law."""
        T = self.temperature(h_m)
        return MU0_SEA * (T / T0_SEA) ** 1.5 * (T0_SEA + SUTHERLAND_C) / (T + SUTHERLAND_C)

    def mach_number(self, velocity_ms: float, h_m: float) -> float:
        """Mach number for given true airspeed and altitude."""
        a = self.speed_of_sound(h_m)
        return velocity_ms / a

    def dynamic_pressure(self, velocity_ms: float, h_m: float) -> float:
        """Dynamic pressure q = 0.5 * rho * V^2 in Pa."""
        rho = self.density(h_m)
        return 0.5 * rho * velocity_ms ** 2
