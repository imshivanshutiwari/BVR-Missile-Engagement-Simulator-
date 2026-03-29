"""Coordinate Transformations: NED ↔ ECEF ↔ Body frame."""

import numpy as np
import math
from physics.constants import R_EARTH


def ned_to_ecef(pos_ned: np.ndarray, origin_lla: tuple = (0.0, 0.0, 0.0)) -> np.ndarray:
    """Convert NED (North-East-Down) position to ECEF.

    For simulation purposes uses flat-Earth approximation
    with optional geodetic origin.
    """
    lat0, lon0, alt0 = origin_lla
    lat0_rad = math.radians(lat0)
    lon0_rad = math.radians(lon0)

    N, E, D = pos_ned
    x = (R_EARTH + alt0 - D) * math.cos(lat0_rad) * math.cos(lon0_rad) + N
    y = (R_EARTH + alt0 - D) * math.cos(lat0_rad) * math.sin(lon0_rad) + E
    z = (R_EARTH + alt0 - D) * math.sin(lat0_rad) - D

    return np.array([x, y, z])


def body_to_ned(v_body: np.ndarray, heading_rad: float,
                pitch_rad: float, roll_rad: float) -> np.ndarray:
    """Transform vector from body frame to NED frame using Euler angles."""
    ch, sh = math.cos(heading_rad), math.sin(heading_rad)
    cp, sp = math.cos(pitch_rad), math.sin(pitch_rad)
    cr, sr = math.cos(roll_rad), math.sin(roll_rad)

    # DCM: Body to NED (3-2-1 sequence: yaw, pitch, roll)
    R = np.array([
        [ch * cp, ch * sp * sr - sh * cr, ch * sp * cr + sh * sr],
        [sh * cp, sh * sp * sr + ch * cr, sh * sp * cr - ch * sr],
        [-sp,     cp * sr,                cp * cr               ]
    ])

    return R @ v_body


def ned_to_body(v_ned: np.ndarray, heading_rad: float,
                pitch_rad: float, roll_rad: float) -> np.ndarray:
    """Transform vector from NED frame to body frame (inverse of body_to_ned)."""
    ch, sh = math.cos(heading_rad), math.sin(heading_rad)
    cp, sp = math.cos(pitch_rad), math.sin(pitch_rad)
    cr, sr = math.cos(roll_rad), math.sin(roll_rad)

    R = np.array([
        [ch * cp, ch * sp * sr - sh * cr, ch * sp * cr + sh * sr],
        [sh * cp, sh * sp * sr + ch * cr, sh * sp * cr - ch * sr],
        [-sp,     cp * sr,                cp * cr               ]
    ])

    return R.T @ v_ned


def altitude_from_ned(pos_ned: np.ndarray) -> float:
    """Extract altitude from NED position (z-down, so altitude = -z)."""
    return -pos_ned[2]


def gravity_at_altitude(h_m: float) -> float:
    """Gravitational acceleration at altitude h (m above sea level).

    g(h) = g0 * (R_earth / (R_earth + h))^2
    """
    from physics.constants import G0
    return G0 * (R_EARTH / (R_EARTH + h_m)) ** 2
