#!/usr/bin/env python3
"""test_std_cube.py — the exact any-axis hinge: Python euler and the Molang strings both reproduce Rodrigues."""
import sys
import numpy as np
sys.path.insert(0, "/home/claude/tools")
import std_cube as CU  # noqa: E402
import molang_eval as ME  # noqa: E402
from equine_compare import rot_matrix  # noqa: E402

rng = np.random.default_rng(7)


def test_euler_roundtrip():
    for _ in range(200):
        u = rng.normal(size=3)
        th = rng.uniform(-80, 80)
        M = CU.rodrigues(u, th)
        assert np.allclose(rot_matrix(CU.euler_of(M)), M, atol=1e-9)


def test_molang_matches():
    for _ in range(60):
        u = rng.normal(size=3)
        u /= np.linalg.norm(u)
        th = float(rng.uniform(-60, 60))
        ch = CU.hinge_molang(u, f"{th} * q.life_time")
        e = [ME.run(x, {"q.life_time": 1.0}) for x in ch]
        assert np.allclose(rot_matrix(e), CU.rodrigues(u, th), atol=1e-6), (u, th, e)


def test_axis_aligned():
    assert CU.axis_aligned({"rotation": [0, 90, 0]}) and CU.axis_aligned({}) and not CU.axis_aligned({"rotation": [-119, 0, 0]})


def test_corners_rotate():
    c = {"origin": [0, 0, 0], "size": [2, 1, 1], "rotation": [0, 0, 90], "pivot": [0, 0, 0]}
    R = rot_matrix([0, 0, 90])
    assert np.allclose(CU.centre(c), R @ np.array([1, 0.5, 0.5]))


if __name__ == "__main__":
    for k, f in list(globals().items()):
        if k.startswith("test_"):
            f()
            print("ok", k)
