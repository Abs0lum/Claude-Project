#!/usr/bin/env python3
"""verify_rp06_1421.py — the gate for tools/build_rp06_1421.py (R14 fix round, RP-06).
convb_round.verify: diff A/J/K + per-job B/C/D/E/F/G/L + standing gates; plus this round's hooks:
  N2   the vex port == the JEM with Java VexModel arm seeds (unchanged by the nesting: arm channels are Java-local deltas)
  JT1  vex right_arm / left_arm are children of body (Java tree), pivots = body + the arm's Java offset
  JT2  arm_tree_gap: shoulder top -> body box <= 1.2 px in idle / flying / charging (1.4.20: 1.36-1.57)
  HPT  rightItem / leftItem under the arms at the arm cube's bottom centre in the FILE frame (bind pose)
  ATT  vex enable_attachables true; nothing else in the vex entity changed
  BG1  blaze.png: RGB identical to 1.4.20; every drawn texel alpha 90, every cut-out texel 0
  BG2  blaze_mers.png = lesson #156 of the Patrix 1.21.11 blaze_s, same size as the colour sheet, 0 where the sheet is empty
  BG3  blaze.texture_set.json = Mojang's shape (format 1.21.30, color + metalness_emissive_roughness_subsurface) and resolves
  BG4  textures_list.json names textures/entity/blaze_mers
  ONLY every other file byte-identical to 1.4.20
Static checks only rule OUT (P1); his in-game witness rules IN."""
import itertools, json, sys
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, "/home/claude/tools")
import convb_round as R
import build_rp06_1421 as B
import build_rp06_1420 as B6
import jem_anim_port as P
import arm_tree_gap as AG

ROOT = Path("/home/claude")
OLD, NEW = B.CFG["src"], B.CFG["dst"]


def hooks(cfg, check):
    # ---------------------------------------------------------------- N2
    init, pre, anim, _ = B6.vx_port()
    cs = [dict(c, _ch=ch, _rh=rh, _lh=lh) for c in (
        [{"age": a, "limb_swing": l, "limb_speed": s, "head_yaw": y, "head_pitch": p, "frame_counter": a}
         for a, l, s, y, p in itertools.product((0.0, 37.0, 211.0), (0.0, 1.3), (0.0, 0.3, 1.0), (0.0, 25.0), (0.0, -10.0))])
        for ch, rh, lh in ((0, 1, 0), (1, 1, 0), (1, 0, 0), (0, 0, 0))]
    w = P.numeric_check("vex", B6.VX["prefix"], init, pre, anim, cs, seed_fn=B6.vex_java, env_fn=B6.vex_env)
    check(f"N2 vex Molang == JEM with Java VexModel arm seeds ({len(cs)} cases)", w["rotation"] < 1e-3 and w["position"] < 1e-4, str(w))
    # ---------------------------------------------------------------- JT
    _, g = R.geo_file(NEW, "geometry.pw_vex"); by = {b["name"]: b for b in g["bones"]}
    ok = all(by[a].get("parent") == "body" for a in ("right_arm", "left_arm"))
    check("JT1 vex arms are children of body (Java VexModel tree)", ok, str({a: (by[a].get("parent"), by[a]["pivot"]) for a in ("right_arm", "left_arm")}))
    rows = {}
    for st, env in {"idle": {"q.is_item_equipped(0)": 1.0}, "flying": {"q.is_item_equipped(0)": 1.0, "q.modified_move_speed": 0.5},
                    "charging": {"q.is_item_equipped(0)": 1.0, "q.is_charging": 1.0}}.items():
        wst = AG.sim(NEW, "vex", "geometry.pw_vex", env, False)
        rows[st] = round(max(v[0] for v in wst.values()), 2)
    check("JT2 vex shoulder -> body <= 1.2 px in idle / flying / charging (1.4.20: 1.36-1.57)", max(rows.values()) <= 1.2, str(rows))
    # ---------------------------------------------------------------- HPT
    good = True; info = {}
    for item, arm in (("rightItem", "right_arm"), ("leftItem", "left_arm")):
        b = by.get(item, {}); c = by[arm]["cubes"][0]; o, s = c["origin"], c["size"]
        want = [o[0] + s[0] / 2, o[1], o[2] + s[2] / 2]
        good &= b.get("parent") == arm and np.allclose(b.get("pivot", [9e9] * 3), want, atol=1e-3) and not any(b.get("rotation", [0, 0, 0]))
        info[item] = b.get("pivot")
    check("HPT hand points under the arms at the cube's bottom centre (file frame)", good, str(info))
    # ---------------------------------------------------------------- ATT
    dn = R.jl(NEW / "entity/vex.entity.json")["minecraft:client_entity"]["description"]
    do = R.jl(OLD / "entity/vex.entity.json")["minecraft:client_entity"]["description"]
    rest_same = {k: v for k, v in dn.items() if k != "enable_attachables"} == do
    check("ATT vex enable_attachables true; the rest of its definition unchanged", dn.get("enable_attachables") is True and rest_same, "")
    # ---------------------------------------------------------------- BG
    a_new = np.asarray(Image.open(NEW / "textures/entity/blaze.png").convert("RGBA")); a_old = np.asarray(Image.open(OLD / "textures/entity/blaze.png").convert("RGBA"))
    drawn = a_old[..., 3] > 0
    check("BG1 blaze.png: RGB identical to 1.4.20; drawn texels alpha 90, cut-outs 0",
          (a_new[..., :3] == a_old[..., :3]).all() and (a_new[..., 3][drawn] == 90).all() and (a_new[..., 3][~drawn] == 0).all(),
          f"{int(drawn.sum())} drawn texels")
    spec = np.asarray(B6.ptex("blaze_s.png")); m = np.asarray(Image.open(NEW / "textures/entity/blaze_mers.png").convert("RGBA"))
    want = B.mers_156(spec); want[~drawn] = 0
    check("BG2 blaze_mers = lesson #156 of the Patrix blaze_s, same size as the colour sheet", m.shape == a_new.shape and (m == want).all(),
          f"{m.shape[1]}x{m.shape[0]}, emissive texels {int((m[..., 1] > 0).sum())}, max {int(m[..., 1].max())}")
    ts = R.jl(NEW / "textures/entity/blaze.texture_set.json")
    van = R.jl(R.VAN_RP / "textures/entity/blaze.texture_set.json")
    okts = (ts["format_version"] == van["format_version"] and set(ts["minecraft:texture_set"]) == set(van["minecraft:texture_set"])
            and all((NEW / f"textures/entity/{v}.png").exists() for v in ts["minecraft:texture_set"].values()))
    check("BG3 blaze.texture_set.json in Mojang's shape; both layers resolve in this pack", okts, json.dumps(ts))
    tl = R.jl(NEW / "textures/textures_list.json")
    check("BG4 textures_list names textures/entity/blaze_mers", "textures/entity/blaze_mers" in tl, f"{len(tl)} entries")


B.CFG["verify_hooks"] = [hooks]
B.CFG["joints_ok"] = {}
B.CFG["prec_order"] = [("StripMine RP 3.0.1", ROOT / "_intake/stack-rps/PW-StripMine-RP-v3_0_1.mcpack"), ("RP-08", ROOT / "_build/rp08-148"),
                       ("RP-07", ROOT / "_build/rp07-1426"), ("RP-06", NEW)]

if __name__ == "__main__":
    files = json.load(open(ROOT / "_docs/convb/build_rp06_1421_files.json"))
    B.CFG["extra_changed"], B.CFG["extra_added"], B.CFG["extra_removed"] = files["changed"], files["added"], files["removed"]
    sys.exit(R.verify(B.CFG))
