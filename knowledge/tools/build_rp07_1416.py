#!/usr/bin/env python3
"""build_rp07_1416.py — his 09-28 21:43 GO ("keep going ... continue making fixes"), D-C272 / D-C273.

RP-07 Neutral Mobs RP v1.4.16 (from v1.4.15):
  1. CONVERTER B for the READY set — geometry rebuilt from the Patrix JEM in its FreshLX rest posture (tools/convb.py) and
     bound to the bone names our animations / render controllers use (tools/convb_build.py):
        turtle · salmon · dolphin · axolotl · frog · tropical fish A + B · panda · mooshroom · wolf
     D-C273 on top of the preview: (a) vanilla-part pivot where FreshLX moves the vanilla part (turtle / axolotl / salmon) or
     the vanilla pivot differs from the declared one (dolphin) — the preview had the turtle 12 px and the axolotl 22 px under
     the ground; (b) the turtle rests in its neutral LAND pose (egg belly hidden, walk cycle averaged: flippers flat, 20°/20°);
     (c) frame bones so every rotated/positioned animated bone keeps an entity-aligned parent frame (turtle head; wolf head,
     head2, mane, tail — they sit inside a body rotated 90°). Identifiers kept; texture files unchanged.
  2. LOOK — `look_at_target` (relative_to-entity: animation.common.look_at_target / animation.wolf.pw.headtrack) ->
     animation.pw_convb.look (additive on `head`; its parent frame is entity-aligned after step 1c) for turtle, dolphin,
     axolotl, frog, panda, mooshroom, wolf. The witnessed equine approach (L-LOOK-REL).
  3. SADDLEBAGS (my 1.4.15 regression, D-C272) — donkey + mule rebuilt by the fixed tools/equine_b.py: left_chest /
     right_chest OWN their cubes again, so controller.render.pw_donkey / pw_mule hide them when no chest is equipped.
  4. manifest 1.4.16, uuid kept.
Everything else byte-identical (verify_rp07_1416.py asserts the diff)."""
import json, math, re, shutil, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, "/home/claude/tools")
from convb_build import build_mob
from convb_preview import JOBS, library, bind_info
from equine_b import build as build_equine
from verify_rp07_1415_rp06_1410 import world_boxes

ROOT = Path("/home/claude")
SRC, DST, VER = ROOT / "_build/rp07-1415", ROOT / "_build/rp07-1416", "1.4.16"
READY = ["turtle", "salmon", "dolphin", "axolotl", "frog", "tropical fish A", "tropical fish B", "panda", "mooshroom", "wolf"]
LOOK_ID = "animation.pw_convb.look"
LOOK_ENTITIES = {"turtle": "animation.common.look_at_target", "dolphin": "animation.common.look_at_target",
                 "axolotl": "animation.common.look_at_target", "frog": "animation.common.look_at_target",
                 "panda": "animation.common.look_at_target", "mooshroom": "animation.common.look_at_target",
                 "wolf": "animation.wolf.pw.headtrack"}
EQUINE_FIX = [("donkey", "pw_donkey.geo.json", "geometry.pw_donkey"), ("mule", "pw_mule.geo.json", "geometry.pw_mule")]


def jl(p):
    t = re.sub(r"^\s*//.*$", "", Path(p).read_text(encoding="utf-8-sig"), flags=re.M)
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        return json.loads(re.sub(r",(\s*[}\]])", r"\1", t))


def wj(p, d):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(json.dumps(d, indent=1), encoding="utf-8")


def log(m):
    print(m)
    with open(ROOT / "_logs/phase_log.md", "a") as f: f.write(f"[{time.strftime('%H:%M')} CT 09-28] BUILD {m}\n")


def geo_file(ident):
    for p in sorted((DST / "models/entity").glob("*.json")):
        d = jl(p)
        ids = [g["description"]["identifier"] for g in d.get("minecraft:geometry", [])]
        if ident in ids:
            assert ids == [ident], (p.name, ids)            # single-geometry files only: replaced whole
            return p, d["minecraft:geometry"][0]["description"]
    raise FileNotFoundError(ident)


def moving_bones(desc, anims):
    """bones our animations ROTATE or MOVE (scale-only channels do not care about the parent frame)."""
    out = set()
    for short, aid in (desc.get("animations") or {}).items():
        a = anims.get(aid)
        if not isinstance(a, dict): continue
        for bn, bv in (a.get("bones") or {}).items():
            if isinstance(bv, dict) and ({"rotation", "position"} & set(bv)): out.add(bn)
    return out - {"placeholder_bone"}


def bounds(desc, bones):
    P = np.array([p for x in world_boxes(bones) for p in x[2]])
    need_w = 2.0 * max(np.abs(P[:, 0]).max(), np.abs(P[:, 2]).max()) / 16.0 + 0.5
    need_h = P[:, 1].max() / 16.0 + 0.5
    d = {k: v for k, v in desc.items() if k != "identifier"}
    d["visible_bounds_width"] = round(max(float(d.get("visible_bounds_width", 0)), need_w), 2)
    d["visible_bounds_height"] = round(max(float(d.get("visible_bounds_height", 0)), need_h), 2)
    return d


def write_geo(p, ident, desc_extra, bones, tw, th):
    desc = {"identifier": ident, **desc_extra, "texture_width": tw, "texture_height": th}
    wj(p, {"format_version": "1.16.0", "minecraft:geometry": [{"description": desc, "bones": bones}]})


def main():
    if DST.exists(): shutil.rmtree(DST)
    shutil.copytree(SRC, DST)
    report = {}
    anims_all, rcs_all = library(DST)
    # 1 — Converter B for the READY set
    for label, stem, gkey, jname, tkey in JOBS:
        if label not in READY: continue
        ent = jl(DST / f"entity/{stem}.entity.json")["minecraft:client_entity"]["description"]
        ident = ent["geometry"][gkey]
        p, desc = geo_file(ident)
        old_bones = jl(p)["minecraft:geometry"][0]["bones"]
        names, rel, _ = bind_info(ent, anims_all, rcs_all)
        moving = moving_bones(ent, anims_all)
        look = ["head"] if stem in LOOK_ENTITIES else []
        # frame alignment only for the bones our animations rotate / move (+ the look bone); scale-only bones keep their frame
        bones, tw, th, info = build_mob_moving(jname, stem, names, moving | set(look), old_bones)
        write_geo(p, ident, bounds(desc, bones), bones, tw, th)
        report[label] = {"identifier": ident, "file": p.name, "bones": len(bones), "cubes": sum(len(b.get("cubes", [])) for b in bones),
                         "mapping": {k: v for k, v in info["mapping"].items() if k != v}, "unbound": info["missing"],
                         "frames": info["frames"], "frame_err": info["frame_err"], "pivot_shift": info["pivot_shift"],
                         "texture": [tw, th]}
        log(f"{DST.name}: {ident} <- Patrix {jname}.jem (Converter B; {len(bones)} bones, {report[label]['cubes']} cubes; "
            f"pivot shift {info['pivot_shift']}; frames {sorted(info['frames'])}; unbound {info['missing']})")
    # 2 — look
    wj(DST / "animations/pw_convb_look.animation.json", {"format_version": "1.8.0", "animations": {LOOK_ID: {"loop": True, "bones": {
        "head": {"rotation": ["query.target_x_rotation", "query.target_y_rotation", 0.0]}}}}})
    for stem, old_id in LOOK_ENTITIES.items():
        pe = DST / f"entity/{stem}.entity.json"; d = jl(pe); desc = d["minecraft:client_entity"]["description"]
        assert desc["animations"].get("look_at_target") == old_id, (stem, desc["animations"].get("look_at_target"))
        desc["animations"]["look_at_target"] = LOOK_ID
        wj(pe, d)
    log(f"{DST.name}: look_at_target -> {LOOK_ID} on {sorted(LOOK_ENTITIES)}")
    # 3 — saddlebags (donkey, mule)
    for mob, fname, ident in EQUINE_FIX:
        p = DST / "models/entity" / fname
        old = jl(p); desc = old["minecraft:geometry"][0]["description"]
        assert [g["description"]["identifier"] for g in old["minecraft:geometry"]] == [ident]
        bones, tw, th, rep = build_equine(mob)
        assert not rep["rest_errors"], rep["rest_errors"]
        write_geo(p, ident, {k: v for k, v in desc.items() if k not in ("identifier", "texture_width", "texture_height")}, bones, tw, th)
        log(f"{DST.name}: {ident} <- Patrix {mob}.jem (equine Converter B, chest _rot folded: left_chest/right_chest own their cubes)")
    # 4 — manifest
    mp = DST / "manifest.json"; m = jl(mp)
    v = [int(x) for x in VER.split(".")]
    m["header"]["version"] = v
    for mod in m.get("modules", []): mod["version"] = v
    m["header"]["name"] = f"AbsolutRealism Neutral Mobs RP v{VER}"
    m["header"]["description"] = (f"v{VER} (2026-09-28) CONVERTER B ROUND 2 (D-C273): turtle, salmon, dolphin, axolotl, frog, tropical fish, "
                                  "panda, mooshroom and wolf rebuilt from the Patrix models in their rest pose; they look at you with a "
                                  "plain head turn. Donkey and mule saddlebags show only when a chest is equipped again. "
                                  "Everything else byte-identical to v1.4.15.")
    wj(mp, m)
    json.dump(report, open(ROOT / "_docs/convb/build_1416_report.json", "w"), indent=1)
    log(f"{DST.name}: manifest {VER}; report _docs/convb/build_1416_report.json")


def build_mob_moving(jname, stem, bind_names, moving, old_bones):
    """build_mob with frame alignment limited to the bones our animations rotate / move (+ the look bone)."""
    import convb_build as cb
    orig = cb.align_frames
    cb.align_frames = lambda bones, animated, look=(): orig(bones, set(moving), look=look)
    try:
        return cb.build_mob(jname, stem, bind_names, old_bones)
    finally:
        cb.align_frames = orig


if __name__ == "__main__":
    main()
