#!/usr/bin/env python3
"""test_wing_gap.py — the contact metric: a rigid slide of the whole wing + hinges = 0; a real opening is still caught."""
import copy
import sys
sys.path.insert(0, "/home/claude/tools")
import wing_gap as G  # noqa: E402


def rig():
    return [{"name": "body", "pivot": [0, 0, 0], "rotation": [45, 0, 0], "cubes": [{"origin": [-3, 0, -3], "size": [6, 6, 6]}]},
            {"name": "slide", "parent": "body", "pivot": [3, 5, 0]},
            {"name": "inner", "parent": "slide", "pivot": [3, 5, 0], "cubes": [{"origin": [3, 0, 0], "size": [7, 10, 0]}]},
            {"name": "hinge", "parent": "inner", "pivot": [10, 5, 0]},
            {"name": "outer", "parent": "hinge", "pivot": [10, 5, 0], "cubes": [{"origin": [10, 0, 0], "size": [7, 10, 0]}]}]


ENVS = [{"q.life_time": t} for t in (0.0, 0.25, 0.5, 0.75)]
PAIR = [("inner", "outer")]


def test_slide_plus_hinge_is_closed():
    an = {"slide": {"position": ["1.5", "0.5", "0"]}, "hinge": {"rotation": ["0", "30 * math.sin(q.life_time * 360)", "0"]}}
    assert G.gap(rig(), an, ENVS, PAIR) < 1e-6


def test_slid_piece_alone_opens():
    an = {"outer": {"position": ["1.5", "0", "0"]}}
    assert G.gap(rig(), an, ENVS, PAIR) > 1.4


def test_off_edge_hinge_opens():
    b = rig()
    for x in b:
        if x["name"] in ("hinge", "outer"):
            x["pivot"] = [12, 5, 0]   # hinge 2 px past the shared edge
    an = {"hinge": {"rotation": ["0", "30", "0"]}}
    assert G.gap(b, an, ENVS, PAIR) > 0.5


def rot_rig():
    R = {"rotation": [-119, 20, 0], "pivot": [3, 5, 0]}
    return [{"name": "body", "pivot": [0, 0, 0], "cubes": [{"origin": [-3, 0, -3], "size": [6, 6, 6]}]},
            {"name": "inner", "parent": "body", "pivot": [3, 5, 0], "cubes": [{"origin": [3, 0, 0], "size": [7, 10, 0], **R}]},
            {"name": "hinge", "parent": "inner", "pivot": [0, 0, 0]},
            {"name": "outer", "parent": "hinge", "pivot": [0, 0, 0], "cubes": [{"origin": [10, 0, 0], "size": [7, 10, 0], **R}]}]


def test_rotated_plates_exact_hinge_closed():
    import numpy as np
    import std_cube as CU
    b = rot_rig()
    p0 = CU.corners(b[1]["cubes"][0])
    shared = [p for p in p0 if any(np.linalg.norm(p - q) < 1e-3 for q in CU.corners(b[3]["cubes"][0]))]
    assert len(shared) >= 2
    u = shared[-1] - shared[0]
    b[2]["pivot"] = [float(x) for x in shared[0]]
    an = {"hinge": {"rotation": CU.hinge_molang(u, "30 * math.sin(q.life_time * 360)")}}
    assert G.gap(b, an, ENVS, PAIR) < 1e-4
    an_wrong = {"hinge": {"rotation": ["0", "30 * math.sin(q.life_time * 360)", "0"]}}   # one local channel
    assert G.gap(b, an_wrong, ENVS, PAIR) > 0.5


if __name__ == "__main__":
    for k, f in list(globals().items()):
        if k.startswith("test_"):
            f()
            print("ok", k)
