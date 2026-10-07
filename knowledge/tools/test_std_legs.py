#!/usr/bin/env python3
import sys
sys.path.insert(0, "/home/claude/tools")
import std_legs as L  # noqa: E402
from bb_truth import face_uvs  # noqa: E402


def test_round_trip_box_and_mirror():
    for m in (False, True):
        for s in ([1, 7, 0], [2, 4, 2], [3, 5, 1]):
            assert L.round_trip_ok({"origin": [0, 0, 0], "size": s, "uv": [10, 20], "mirror": m})


def test_thicken_z_sheet():
    c = {"origin": [1, 0.1, 1], "size": [1, 7, 0], "uv": [40, 12]}
    n, r = L.thicken(c)
    assert n["size"] == [1, 7, 1] and n["origin"][2] == 0.5 and r["faces_kept"]
    rects = face_uvs(n["uv"], n["size"], False)
    assert rects["east"] == rects["north"] == rects["west"]


def test_mirrored_sheet_faces_kept():
    n, r = L.thicken({"origin": [0, 0, 0], "size": [1, 5, 0], "uv": [8, 8], "mirror": True})
    assert r["faces_kept"]


def test_not_a_sheet():
    assert L.thicken({"origin": [0, 0, 0], "size": [2, 0, 5], "uv": [0, 0]}) == (None, None)   # a flat foot sole
    assert L.thicken({"origin": [0, 0, 0], "size": [1, 2, 1], "uv": [0, 0]}) == (None, None)


if __name__ == "__main__":
    for k, f in list(globals().items()):
        if k.startswith("test_"):
            f()
            print("ok", k)
