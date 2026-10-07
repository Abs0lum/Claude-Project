#!/usr/bin/env python3
import sys
sys.path.insert(0, "/home/claude/tools")
import contact_gate as C  # noqa: E402


def rig(rot_thigh=0, rot_hip=0):
    return [{"name": "body", "pivot": [0, 10, 0], "cubes": [{"origin": [-2, 10, -2], "size": [4, 4, 4]}]},
            {"name": "hip", "parent": "body", "pivot": [0, 10, 0], "rotation": [rot_hip, 0, 0]},
            {"name": "thigh", "parent": "hip", "pivot": [0, 10, 0], "rotation": [rot_thigh, 0, 0],
             "cubes": [{"origin": [-0.5, 5, 0], "size": [1, 5, 0]}]},
            {"name": "knee", "parent": "hip", "pivot": [0, 5, 0]},
            {"name": "shin", "parent": "knee", "pivot": [0, 5, 0], "cubes": [{"origin": [-0.5, 0, 0], "size": [1, 5, 0]}]}]


def test_hip_tuck_keeps_contact():
    pairs = C.touching_pairs(rig(), ["thigh", "shin"])
    assert ("thigh", "shin") in pairs or ("shin", "thigh") in pairs, pairs
    assert C.worst(rig(rot_hip=65), pairs)[0] < 1e-6


def test_double_turn_detected():
    pairs = C.touching_pairs(rig(), ["thigh", "shin"])
    assert C.worst(rig(rot_hip=65, rot_thigh=65), pairs)[0] > 1.0


if __name__ == "__main__":
    for k, f in list(globals().items()):
        if k.startswith("test_"):
            f()
            print("ok", k)
