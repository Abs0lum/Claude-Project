#!/usr/bin/env python3
"""std_cube.py — cube-level rotation helpers for the standard flight tools.
A Bedrock cube may carry its own `rotation` about its own `pivot` (file frame): file point = Rc @ (p - q) + q.
Seven flying birds (WWA bird of paradise / roadrunner / shoebill / swan, WS desert owl / hornbill, YSav black eagle) have
wing plates turned this way; every measurement that reads cube corners, centres or axes must apply it (D-C38x)."""
import numpy as np

from equine_compare import rot_matrix


def cube_R(c):
    r = c.get("rotation") or [0, 0, 0]
    return rot_matrix(list(r)) if any(r) else np.eye(3)


def cube_affine(c):
    """(R, t): rotated file point = R @ p + t for a point p of the cube's unrotated box."""
    R = cube_R(c)
    q = np.array(c.get("pivot", [0, 0, 0]), float)
    return R, q - R @ q


def box(c):
    o, s = np.array(c["origin"], float), np.array(c["size"], float)
    return np.minimum(o, o + s), np.maximum(o, o + s)


def corners(c):
    """the 8 corners of the cube in the bone's file frame, cube rotation applied."""
    o, s = np.array(c["origin"], float), np.array(c["size"], float)
    R, t = cube_affine(c)
    return [R @ (o + s * np.array([i, j, k])) + t for i in (0, 1) for j in (0, 1) for k in (0, 1)]


def centre(c):
    o, s = np.array(c["origin"], float), np.array(c["size"], float)
    R, t = cube_affine(c)
    return R @ (o + s / 2) + t


def axis(c, k):
    """the cube's local axis k as a file-frame unit vector."""
    e = np.zeros(3)
    e[k] = 1.0
    return cube_R(c) @ e


def rotated(c):
    return any(c.get("rotation") or [0, 0, 0])


def axis_aligned(c):
    """True when the cube rotation maps every axis onto an axis (multiples of 90 degrees) — or there is none."""
    R = cube_R(c)
    return bool(np.all(np.isclose(np.abs(R), np.round(np.abs(R)), atol=1e-6)))


# ---------------------------------------------------------------- an exact hinge about any axis, in Bedrock euler
def rodrigues(u, deg):
    u = np.array(u, float) / np.linalg.norm(u)
    a = np.radians(deg)
    K = np.array([[0, -u[2], u[1]], [u[2], 0, -u[0]], [-u[1], u[0], 0]])
    return np.eye(3) + np.sin(a) * K + (1 - np.cos(a)) * (K @ K)


def euler_of(M):
    """Bedrock euler [a, b, c] (degrees) with rot_matrix([a, b, c]) == M.
    rot_matrix(e) = Rz(-c) @ Ry(b) @ Rx(-a) (measured on equine_compare.rot_matrix)."""
    beta = np.degrees(np.arcsin(np.clip(-M[2, 0], -1, 1)))
    alpha = np.degrees(np.arctan2(M[2, 1], M[2, 2]))
    gamma = np.degrees(np.arctan2(M[1, 0], M[0, 0]))
    return [-alpha, beta, -gamma]


def hinge_molang(u, theta):
    """three Molang channel strings: the Bedrock euler of a rotation by `theta` (Molang, degrees) about the unit file-frame
    axis u — exact for every theta (Rodrigues + the Z·Y·X extraction above)."""
    x, y, z = [float(v) for v in np.array(u, float) / np.linalg.norm(u)]
    th = f"({theta})"
    C, S = f"math.cos{th}", f"math.sin{th}"
    T = f"(1 - {C})"
    m00 = f"({C} + {x * x:.6f} * {T})"
    m10 = f"({x * y:.6f} * {T} + {z:.6f} * {S})"
    m20 = f"({x * z:.6f} * {T} - {y:.6f} * {S})"
    m21 = f"({y * z:.6f} * {T} + {x:.6f} * {S})"
    m22 = f"({C} + {z * z:.6f} * {T})"
    a = f"(-math.atan2({m21}, {m22}))"
    b = f"math.asin(math.clamp(-{m20}, -1, 1))"
    c = f"(-math.atan2({m10}, {m00}))"
    return [a, b, c]
