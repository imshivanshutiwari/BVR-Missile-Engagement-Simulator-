"""STRIKE-VECTOR Physics Engine — Physical Constants"""

import math

# ── Universal Constants ──
G0 = 9.80665           # m/s² standard gravity
R_EARTH = 6371000.0    # m mean Earth radius
R_AIR = 287.058        # J/(kg·K) specific gas constant for dry air
GAMMA_AIR = 1.4        # ratio of specific heats for air

# ── Sea-Level Reference (ISA) ──
T0_SEA = 288.15        # K sea-level temperature
P0_SEA = 101325.0      # Pa sea-level pressure
RHO0_SEA = 1.225       # kg/m³ sea-level density
A0_SEA = 340.294       # m/s speed of sound at sea level
MU0_SEA = 1.716e-5     # Pa·s dynamic viscosity at sea level (Sutherland ref)
SUTHERLAND_C = 110.4   # K Sutherland's constant for air

# ── ISA Layer Definitions ──
ISA_LAYER_ALTITUDES_KM = [0, 11, 20, 32, 47, 51, 71, 86]
ISA_LAPSE_RATES_K_PER_KM = [-6.5, 0.0, 1.0, 2.8, 0.0, -2.8, -2.0]

# ── Missile Reference (ASTRA/AIM-120 Class) ──
MISSILE_BODY_DIAMETER = 0.178      # m
MISSILE_REF_AREA = math.pi * (MISSILE_BODY_DIAMETER / 2) ** 2  # m² ≈ 0.02488
MISSILE_BODY_LENGTH = 3.65         # m
MISSILE_CG_FROM_NOSE = 1.80        # m (varies with propellant burn)

MISSILE_TOTAL_MASS = 185.0         # kg
MISSILE_PROPELLANT_BOOST = 22.0    # kg boost grain
MISSILE_PROPELLANT_SUSTAIN = 18.0  # kg sustain grain
MISSILE_EMPTY_MASS = 145.0         # kg (warhead + avionics + structure)

# ── Propulsion ──
BOOST_DURATION = 3.2               # s
BOOST_THRUST_SL = 15000.0          # N sea-level thrust
BOOST_ISP = 265.0                  # s specific impulse
SUSTAIN_END_TIME = 20.0            # s from ignition
SUSTAIN_THRUST_SL = 3200.0         # N sea-level thrust
SUSTAIN_ISP = 270.0                # s specific impulse
ALTITUDE_THRUST_COEFF = 0.08       # k_alt for altitude compensation

# ── Aerodynamics ──
ASPECT_RATIO = 2.5                 # fin aspect ratio
OSWALD_EFFICIENCY = 0.8            # Oswald span efficiency
CD0_MACH_TABLE = [0.5, 0.8, 0.9, 0.95, 1.0, 1.05, 1.1, 1.2,
                  1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
CD0_VALUES = [0.016, 0.018, 0.021, 0.026, 0.038, 0.042,
              0.040, 0.036, 0.028, 0.022, 0.019, 0.018,
              0.017, 0.017]

# ── Guidance ──
NAV_CONSTANT_N = 4.0               # proportional navigation constant
MAX_ACCEL_G = 30.0                 # max g-load for missile
MAX_ACCEL_MS2 = MAX_ACCEL_G * G0   # m/s² ≈ 294.3

# ── Seeker ──
SEEKER_FOV_HALF_DEG = 30.0         # ±30° gimbal limit
SEEKER_FOV_HALF_RAD = math.radians(SEEKER_FOV_HALF_DEG)

# ── Warhead / Fuze ──
FUZE_RADIUS = 15.0                 # m proximity fuze activation
LETHAL_RADIUS = 25.0               # m effective fragmentation radius
FUZE_K = 2.0                       # fuze probability constant
WARHEAD_K = 1.8                    # lethality constant

# ── F-16 Target ──
F16_MASS = 9200.0                  # kg combat weight
F16_VMAX = 600.0                   # m/s (~Mach 2)
F16_VCRUISE = 250.0                # m/s
F16_G_MAX = 9.0                    # structural g limit
F16_CLIMB_RATE = 250.0             # m/s max
F16_BANK_RATE_DEG = 180.0          # deg/s max bank rate
F16_EVASION_G = 7.0                # barrel roll g-load

# ── Simulation ──
SIM_DT = 0.01                      # s integration time step
SIM_MAX_TIME = 120.0               # s maximum simulation time
INTERCEPT_DISTANCE = FUZE_RADIUS   # m distance for intercept detection
