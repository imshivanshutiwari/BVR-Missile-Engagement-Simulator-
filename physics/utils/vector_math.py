"""3D Vector Math Utilities."""

import numpy as np


def magnitude(v: np.ndarray) -> float:
    """Euclidean norm of a vector."""
    return float(np.linalg.norm(v))


def unit_vector(v: np.ndarray) -> np.ndarray:
    """Unit vector in direction of v. Returns zero vector if |v| ~ 0."""
    mag = magnitude(v)
    if mag < 1e-12:
        return np.zeros_like(v)
    return v / mag


def dot(a: np.ndarray, b: np.ndarray) -> float:
    """Dot product of two vectors."""
    return float(np.dot(a, b))


def cross(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Cross product of two 3D vectors."""
    return np.cross(a, b)


def angle_between(a: np.ndarray, b: np.ndarray) -> float:
    """Angle between two vectors in radians."""
    cos_theta = dot(unit_vector(a), unit_vector(b))
    cos_theta = np.clip(cos_theta, -1.0, 1.0)
    return float(np.arccos(cos_theta))


def clip_vector(v: np.ndarray, max_mag: float) -> np.ndarray:
    """Clip vector magnitude to max_mag while preserving direction."""
    mag = magnitude(v)
    if mag > max_mag:
        return v * (max_mag / mag)
    return v.copy()


def rotation_matrix_z(angle_rad: float) -> np.ndarray:
    """Rotation matrix about the z-axis (yaw)."""
    c, s = np.cos(angle_rad), np.sin(angle_rad)
    return np.array([
        [c, -s, 0],
        [s,  c, 0],
        [0,  0, 1]
    ])


def rotation_matrix_y(angle_rad: float) -> np.ndarray:
    """Rotation matrix about the y-axis (pitch)."""
    c, s = np.cos(angle_rad), np.sin(angle_rad)
    return np.array([
        [ c, 0, s],
        [ 0, 1, 0],
        [-s, 0, c]
    ])


def rotation_matrix_x(angle_rad: float) -> np.ndarray:
    """Rotation matrix about the x-axis (roll)."""
    c, s = np.cos(angle_rad), np.sin(angle_rad)
    return np.array([
        [1,  0,  0],
        [0,  c, -s],
        [0,  s,  c]
    ])
