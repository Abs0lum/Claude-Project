#!/usr/bin/env python3
"""equine_b.py — CONVERTER B for the equine family (D-C268/D-C269): a Bedrock geometry built straight from the Patrix JEM.

  1. jem_convert.jem_tree(jem): the JEM in the Blockbench frame (CONV-1; boxes absolute, per-face UVs, sizeAdd, mirror).
  2. The FreshLX rest POSTURE: every CEM animation evaluated at rest with the vanilla per-frame seeds (cem_eval.rest_pose,
     seeds = neck ty 4 / tz -12 / rx 30°, body rx 0) and AVERAGED over 64 idle times, so the idle sway cancels out and the
     designed pose remains (neck 30-31° forward, head riding the neck, ears 8° back, donkey/mule ears splayed ±15°, tail ~12°).
     Applied to: neck2 (pivot + rx), head2 (rx), ears (rx, rz), tail2 (pivot + rx), snout2 / chests (pivot). A moved pivot
     carries its boxes and every descendant with it.
  3. Legs and body keep the static JEM placement (rotation 0) — our walk / trot / idle animations drive them. Legs pivot at
     their TOP (BB y 11 = the body's underside) and are children of `body`, so the idle bob (pw_ambient: up to 0.5 px) and sway
     (±2°) carry the legs with the body — the belly joint never opens (a hoof may rise 0.5 px instead).
  4. Bones renamed to the names our animations and render controllers use:
        body (+ the body box)             neck2 -> neck (+ neck3 box; skeleton: bone2 -> neck_bones)
        head2 -> head (posture) + head2 (the skull box; the idle wobble bone)
        snout2 -> snout · left_ear2 -> left_ear · right_ear2 -> right_ear · mane3 -> mane_top · mane2 -> mane
        tail2 -> tail · right_chest2(+_rot) -> right_chest(+right_chest_rot) · left likewise
        front_right_leg -> leg0 · front_left_leg -> leg1 · back_right_leg -> leg2 · back_left_leg -> leg3
  5. Bedrock frame (CONV-1): pivot (-x, y, z); cube origin (-(x + w), y, z); rotation (-rx, -ry, +rz) of the BB rotation.

API: build(mob) -> (bones, texture_width, texture_height, posture_report)
"""
import copy, json, math, sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
from cem_eval import rest_pose
from jem_convert import jem_tree, to_bedrock, load_json

CEM = Path("/home/claude/_intake/patrix-mobs/assets/minecraft/optifine/cem")
SEEDS = {"neck": {"ty": 4.0, "tz": -12.0, "rx": 0.5235988}, "body": {"rx": 0.0}, "tail": {"ry": 0.0}}
POSTURE = {  # bone -> attributes taken from the averaged rest pose
    "neck2": ("ty", "tz", "rx"), "head2": ("rx",), "left_ear2": ("rx", "rz"), "right_ear2": ("rx", "rz"),
    "tail2": ("ty", "rx"), "snout2": ("ty",), "right_chest2": ("ty",), "left_chest2": ("ty",),
}
RENAME = {"neck2": "neck", "snout2": "snout", "left_ear2": "left_ear", "right_ear2": "right_ear", "mane3": "mane_top", "mane2": "mane",
          "tail2": "tail", "right_chest2": "right_chest", "right_chest2_rot": "right_chest_rot", "left_chest2": "left_chest",
          "left_chest2_rot": "left_chest_rot", "bone2": "neck_bones",
          "front_right_leg": "leg0", "front_left_leg": "leg1", "back_right_leg": "leg2", "back_left_leg": "leg3"}
LEG_TOP_Y = 11.0
N_SAMPLES = 64


def averaged_rest(jem):
    """Mean of every model attribute over N_SAMPLES idle times (age spread over ~2.5 in-game hours of ticks)."""
    acc = {}; errs = {}
    for i in range(N_SAMPLES):
        ctx, err = rest_pose(jem, params={"age": i * 97.0}, seeds=SEEDS)
        errs.update(err)
        for m, d in ctx.models.items():
            for k, v in d.items():
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    acc.setdefault(m, {}).setdefault(k, []).append(float(v))
    return {m: {k: sum(v) / len(v) for k, v in d.items()} for m, d in acc.items()}, errs


def assigned_attrs(jem):
    out = {}
    for part in jem.get("models", []):
        pname = part.get("part") or part.get("id")
        for block in part.get("animations", []) or []:
            for k in block:
                m, _, a = k.rpartition("."); m = pname if m in ("this", "part") else m.split(":")[-1]
                out.setdefault(m, set()).add(a)
    return out


def build(mob):
    jem = load_json(CEM / f"{mob}.jem")
    tw, th = jem.get("textureSize") or [64, 64]
    bones = jem_tree(jem)                                   # BB frame, boxes absolute
    by = {b["name"]: b for b in bones}
    rest, errs = averaged_rest(jem); asg = assigned_attrs(jem)
    report = {}

    def shift(name, d):                                     # move a bone, its boxes and every descendant
        b = by[name]; b["pivot"] = [b["pivot"][k] + d[k] for k in range(3)]
        for x in b["boxes"]: x["from"] = [x["from"][k] + d[k] for k in range(3)]
        for c in bones:
            if c["parent"] == name: shift(c["name"], d)

    # posture — parents first (depth order)
    for b in sorted(bones, key=lambda b: b["depth"]):
        n = b["name"]
        if n not in POSTURE or n not in rest: continue
        st = rest[n]; want = [a for a in POSTURE[n] if a in asg.get(n, set())]
        if any(a in want for a in ("tx", "ty", "tz")):
            par = by.get(b["parent"])
            if b["depth"] == 1: target = [-st.get("tx", 0), -st.get("ty", 0), st.get("tz", 0)]
            else: target = [par["pivot"][0] - st.get("tx", 0), par["pivot"][1] - st.get("ty", 0), par["pivot"][2] + st.get("tz", 0)]
            new = list(b["pivot"])
            for k, a in enumerate(("tx", "ty", "tz")):
                if a in want: new[k] = target[k]
            d = [new[k] - b["pivot"][k] for k in range(3)]
            if any(abs(x) > 1e-9 for x in d): shift(n, d)
        rot = list(b["rotation"])
        for k, a in enumerate(("rx", "ry", "rz")):
            if a in want: rot[k] = (-1 if k < 2 else 1) * math.degrees(st.get(a, 0.0))
        b["rotation"] = rot
        report[n] = {"pivot_BB": [round(v, 3) for v in b["pivot"]], "rotation_BB": [round(v, 2) for v in rot]}

    # legs: pivot at the top of the leg, rotation 0, children of body; body static, rotation 0
    for n in ("front_right_leg", "front_left_leg", "back_right_leg", "back_left_leg"):
        b = by[n]; b["pivot"] = [b["pivot"][0], LEG_TOP_Y, b["pivot"][2]]; b["rotation"] = [0, 0, 0]; b["parent"] = "body"
    by["body"]["rotation"] = [0, 0, 0]

    # head: split head2 into the posture bone `head` + the wobble bone `head2` (same pivot) that owns the skull box
    h = by["head2"]
    skull = {"name": "head2_skull", "parent": "head2", "depth": h["depth"] + 1, "pivot": list(h["pivot"]), "rotation": [0, 0, 0],
             "mirror": h["mirror"], "boxes": h["boxes"], "part": h["part"]}
    h["boxes"] = []
    for c in bones:
        if c["parent"] == "head2": c["parent"] = "head2_skull"
    bones.insert(bones.index(h) + 1, skull); by["head2_skull"] = skull
    # keep only what renders or is animated: drop empty vanilla placeholder parts and the FreshLX credit bone
    keep_empty = {"body", "neck2", "head2", "head2_skull", "right_chest2", "left_chest2", "tail2"}
    drop = {b["name"] for b in bones if not b["boxes"] and b["name"] not in keep_empty
            and not any(c["parent"] == b["name"] and (c["boxes"] or c["name"] in keep_empty) for c in bones)}
    bones = [b for b in bones if b["name"] not in drop]
    # rename
    names = dict(RENAME); names["head2"] = "head"; names["head2_skull"] = "head2"
    for b in bones:
        b["name"] = names.get(b["name"], b["name"])
        if b["parent"]: b["parent"] = names.get(b["parent"], b["parent"])
    # neck3 (a box-only child of neck2, no rotation) folds into `neck` unless it has children (skeleton horse: bone2)
    out = to_bedrock(bones)
    ob = {b["name"]: b for b in out}
    # D-C272: render-controller part_visibility hides only the cubes the NAMED bone owns (witnessed 09-28: 1.4.15 saddlebags
    # stayed visible) — fold each chest `_rot` child into its parent (same pivot) so left_chest / right_chest own their cube.
    for side in ("left_chest", "right_chest"):
        child = ob.get(side + "_rot")
        if child and side in ob and child.get("parent") == side and child["pivot"] == ob[side]["pivot"] and not any(ob[side]["rotation"]):
            ob[side]["rotation"] = list(child["rotation"]); ob[side]["cubes"] = ob[side]["cubes"] + child["cubes"]
            if child.get("mirror"): ob[side]["mirror"] = True
            out = [b for b in out if b["name"] != side + "_rot"]; ob = {b["name"]: b for b in out}
    if "neck3" in ob and not any(b["parent"] == "neck3" for b in out) and not any(ob["neck3"]["rotation"]):
        ob["neck"]["cubes"] = ob["neck"]["cubes"] + ob["neck3"]["cubes"]; out = [b for b in out if b["name"] != "neck3"]
    for b in out:
        if b.get("parent") is None: b.pop("parent", None)
        b["rotation"] = [round(v, 3) + 0.0 for v in b["rotation"]]
        b["pivot"] = [round(v, 4) + 0.0 for v in b["pivot"]]
    return out, tw, th, {"posture": report, "rest_errors": errs, "dropped_empty": sorted(drop)}


if __name__ == "__main__":
    for m in sys.argv[1:] or ["horse"]:
        bones, tw, th, rep = build(m)
        print(f"== {m} {tw}x{th}")
        for b in bones:
            print(f"  {b['name']:16s} parent={str(b.get('parent')):12s} pivot={b['pivot']} rot={b['rotation']} cubes={len(b['cubes'])}")
        print("  posture:", json.dumps(rep["posture"]))
        print("  dropped:", rep["dropped_empty"], "errors:", rep["rest_errors"])
