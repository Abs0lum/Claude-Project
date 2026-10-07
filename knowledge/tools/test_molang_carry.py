#!/usr/bin/env python3
"""tests for molang_carry — the p21 shared_ case (anim_speed_* set by the source's pre_animation), closure, renaming,
missing variables, idempotent apply."""
import sys

sys.path.insert(0, "/home/claude/tools")
import molang_carry as C  # noqa: E402


def test_split():
    assert C.split_statements("v.a = 1; v.b = (v.a > 0 ? {v.c = 2; v.c} : 0); v.d = 3") == \
        ["v.a = 1", "v.b = (v.a > 0 ? {v.c = 2; v.c} : 0)", "v.d = 3"]


def test_carry_closure_and_rename():
    src = {"scripts": {"initialize": ["v.base = 2;"],
                       "pre_animation": ["v.anim_speed_multiplier = q.modified_move_speed * v.base; v.other = 9;",
                                         "v.anim_speed_movement_max = v.anim_speed_multiplier * 3;"]}}
    tgt = {"scripts": {"pre_animation": ["v.anim_speed_multiplier = 77;"]}}      # the target means something else by it
    clip = {"bones": {"leg": {"rotation": ["math.cos(q.anim_time * 90) * v.anim_speed_movement_max", 0, "v.gliding_speed_value"]}}}
    clip2, init, pre, missing = C.carry(clip, src, tgt, "pwc_")
    rot = clip2["bones"]["leg"]["rotation"][0]
    assert "v.pwc_anim_speed_movement_max" in rot and "v.anim_speed_movement_max" not in rot
    assert any("v.pwc_anim_speed_multiplier = q.modified_move_speed * v.pwc_base" in s for s in pre), pre
    assert any("v.pwc_anim_speed_movement_max = v.pwc_anim_speed_multiplier * 3" in s for s in pre), pre
    assert init == ["v.pwc_base = 2;"], init
    assert not any("v.other" in s for s in pre)               # an unrelated statement is not carried
    assert missing == []
    assert clip2["bones"]["leg"]["rotation"][2] == "v.gliding_speed_value"     # engine variable untouched


def test_missing_and_guard():
    clip = {"bones": {"a": {"rotation": ["v.nowhere * 2", "(v.safe ?? 0)", 0]}}}
    _, _, _, missing = C.carry(clip, {"scripts": {}}, {"scripts": {}}, "pwc_")
    assert missing == ["nowhere"], missing
    _, _, _, missing2 = C.carry(clip, {"scripts": {}}, {"scripts": {"pre_animation": ["v.nowhere = 1;"]}}, "pwc_")
    assert missing2 == []


def test_apply_idempotent():
    d = {"scripts": {"pre_animation": ["v.x = 1;"]}}
    C.apply_to_entity(d, ["v.pwc_a = 1;"], ["v.pwc_b = 2;"])
    C.apply_to_entity(d, ["v.pwc_a = 1;"], ["v.pwc_b = 2;"])
    assert d["scripts"]["pre_animation"] == ["v.x = 1;", "v.pwc_b = 2;"] and d["scripts"]["initialize"] == ["v.pwc_a = 1;"]


def test_old_format_entity():
    d = {"scripts": {"pre_animation": ["v.y = 1;"]}}
    C.apply_to_entity(d, ["v.pwc_a = math.random(0, 1);"], ["v.pwc_b = v.pwc_a * 2;"], "1.8.0")
    assert "initialize" not in d["scripts"], d
    assert d["scripts"]["pre_animation"][0] == "v.pwc_a = v.pwc_a ?? (math.random(0, 1));", d
    assert d["scripts"]["pre_animation"][-1] == "v.pwc_b = v.pwc_a * 2;", d


if __name__ == "__main__":
    n = 0
    for k, f in list(globals().items()):
        if k.startswith("test_"):
            f()
            n += 1
    print(f"{n} carry test groups passed")
