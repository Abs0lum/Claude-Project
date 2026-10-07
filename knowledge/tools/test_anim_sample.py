#!/usr/bin/env python3
"""tests for anim_sample.py — every channel form, keyframe interpolation, pre / post sides, clip length."""
import sys

sys.path.insert(0, "/home/claude/tools")
import anim_sample as A  # noqa: E402


def close(a, b, eps=1e-9):
    return all(abs(x - y) < eps for x, y in zip(a, b))


def test_forms():
    assert close(A.sample_channel(5, 0, {}), [5, 5, 5])
    assert close(A.sample_channel("2 * 3", 0, {}), [6, 6, 6])
    assert close(A.sample_channel([1, "q.anim_time * 10", 0], 0.5, {"q.anim_time": 0.5}), [1, 5, 0])
    assert close(A.sample_channel("math.sin(90) * 30", 0, {}), [30, 30, 30])


def test_keyframes():
    ch = {"0.0": [0, 0, 0], "1.0": [10, 20, 30]}
    assert close(A.sample_channel(ch, 0.5, {}), [5, 10, 15])
    assert close(A.sample_channel(ch, -1, {}), [0, 0, 0])
    assert close(A.sample_channel(ch, 2, {}), [10, 20, 30])
    ch2 = {"0.0": {"pre": [0, 0, 0], "post": [100, 0, 0]}, "1.0": {"pre": [0, 0, 0], "post": [7, 7, 7]}}
    assert close(A.sample_channel(ch2, 0.5, {}), [50, 0, 0])          # from post(0) to pre(1)
    assert close(A.sample_channel(ch2, 1.5, {}), [7, 7, 7])           # after the last key: its post
    ch3 = {"0.5": 4}
    assert close(A.sample_channel(ch3, 0, {}), [4, 4, 4])


def test_clip():
    clip = {"animation_length": 2.0, "bones": {"leg": {"rotation": {"0": [0, 0, 0], "2": [20, 0, 0]}, "position": [0, "q.anim_time", 0]}}}
    s = A.sample_clip(clip, 1.0)
    assert close(s["leg"]["rotation"], [10, 0, 0]) and close(s["leg"]["position"], [0, 1, 0])
    assert A.clip_length(clip) == 2.0
    assert A.clip_length({"bones": {"a": {"rotation": {"0.0": 0, "1.5": 3}}}}) == 1.5
    assert A.clip_length({"bones": {"a": {"rotation": "math.sin(q.anim_time * 90)"}}}) == 1.0


if __name__ == "__main__":
    n = 0
    for name, f in list(globals().items()):
        if name.startswith("test_"):
            f()
            n += 1
    print(f"{n} test groups passed")
