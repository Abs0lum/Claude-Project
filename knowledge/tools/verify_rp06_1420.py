#!/usr/bin/env python3
"""verify_rp06_1420.py — the gate for tools/build_rp06_1420.py (FA-1 RP-06).
convb_round.verify: diff A/J/K, per-job B (cubes == bake) / C placement / D joints / E binds / F part_visibility / G frames /
L texture; the standing gates MLS · ARS · RCV · FMT · RBW · ATT · PREC; plus this round's hooks:
  N1-N4  every JEM port == the JEM (molang_eval vs cem_eval; seeded Java vanilla values for vex arms + blaze sticks)
  S1-S7  each entity: Patrix geometry id, the port animation + its scripts, Mojang's definition otherwise
  T1-T6  textures: Patrix 1.21.11 sheets pixel-exact; phantom eye merge; warden tendrils + emission; breeze eyes emission
  HPT    the vex has rightItem / leftItem under its arms (held sword)
  ULC    no vanilla-geometry x our-texture MISMATCH left for the converted mobs (uv_layout_census on the new stack)
  BZW    the breeze's four layer geometries: whole skeleton, cubes only where they belong, heights as Java stacks them
Static checks only rule OUT (P1); his in-game witness rules IN."""
import io, itertools, json, math, sys, zipfile
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, "/home/claude/tools")
import convb_round as R
import build_rp06_1420 as B
import jem_anim_port as P
import convb_build as CB

ROOT = Path("/home/claude")
NEW = B.CFG["dst"]
JOINT_OK = {"blaze": "the 12 rods orbit free of the body by design (Java BlazeModel)",
            "breeze": "the rods hang free under the head by design (Java BreezeModel)"}


def cases_base():
    cs = [{"age": a, "limb_swing": l, "limb_speed": s, "head_yaw": y, "head_pitch": p, "frame_counter": a}
          for a, l, s, y, p in itertools.product((0.0, 37.0, 211.0), (0.0, 1.3, 4.9), (0.0, 0.3, 1.0), (0.0, 25.0), (0.0, -10.0))]
    return cs + [{"age": 50.0, "is_alive": False, "is_hurt": True, "hurt_time": 5.0, "death_time": 7.0}, {"age": 80.0, "swing_progress": 0.4}]


def hooks(cfg, check):
    anims = {}
    for f in (NEW / "animations").glob("pw_*.animation.json"): anims.update(R.jl(f)["animations"])
    # ------------------------------------------------------------------ N: numeric
    init, pre, anim, _ = B.em_port()
    w = P.numeric_check("endermite", B.EM["prefix"], init, pre, anim, cases_base(), scale_div=B.EM["scale_div"])
    check("N1 endermite Molang == JEM (110 cases)", w["rotation"] < 1e-3 and w["position"] < 1e-4 and w["scale"] < 1e-6, str(w))
    init, pre, anim, _ = B.vx_port()
    cs = []
    for a, l, s, y, p, (ch, rh, lh) in itertools.product((0.0, 37.0, 211.0), (0.0, 2.1), (0.0, 0.6), (0.0, 30.0), (0.0, -12.0),
                                                         ((0, 1, 0), (1, 1, 0), (1, 0, 0), (1, 1, 1), (1, 0, 1))):
        cs.append({"age": a, "limb_swing": l, "limb_speed": s, "head_yaw": y, "head_pitch": p, "frame_counter": a, "_ch": ch, "_rh": rh, "_lh": lh})
    cs += [{"age": 40.0, "hurt_time": 6.0, "is_hurt": True}, {"age": 40.0, "death_time": 8.0, "is_alive": False}, {"age": 30.0, "is_riding": True}]
    w = P.numeric_check("vex", B.VX["prefix"], init, pre, anim, cs, seed_fn=B.vex_java, env_fn=B.vex_env)
    check(f"N2 vex Molang == JEM with Java VexModel arm seeds ({len(cs)} cases: calm / charging with sword / empty / both hands / off-hand)",
          w["rotation"] < 1e-3 and w["position"] < 1e-4 and w["scale"] < 1e-6, str(w))
    init, pre, anim, _ = B.ph_port()
    cs = [dict(c, rot_y=r) for c in cases_base() for r in (0.0, 1.1, -2.7)]
    w = P.numeric_check("phantom", B.PH["prefix"], init, pre, anim, cs, env_fn=lambda c: {"q.body_y_rotation": math.degrees(c.get("rot_y", 0.0))})
    check(f"N3 phantom Molang == JEM (unwrapped body yaw; {len(cs)} cases)", w["rotation"] < 1e-3 and w["position"] < 1e-4, str(w))
    init, pre, anim, _ = B.bz_port()
    cs = [dict(c, is_burning=b) for c in cases_base() for b in (False, True)]
    w = P.numeric_check("blaze", B.BZ["prefix"], init, pre, anim, cs, seed_fn=B.blaze_java,
                        env_fn=lambda c: {"q.is_on_fire": 1.0 if c.get("is_burning") else 0.0})
    check(f"N4 blaze Molang == JEM with Java BlazeModel stick seeds ({len(cs)} cases)", w["rotation"] < 1e-3 and w["position"] < 1e-4, str(w))
    # the blaze seeds reproduce Java's rings: radii 9 / 7 / 5 at every age
    env = {}
    import molang_eval as ME
    ok = True
    for age in (0.0, 13.0, 77.0, 400.0):
        env = {"q.life_time": age / 20.0}
        for s in pre[: 1 + 36]: ME.run(s, env)
        jv = B.blaze_java({"age": age})
        for k in range(1, 13):
            for ch in ("tx", "ty", "tz"):
                if abs(env.get(f"v.pw_bz_stick{k}_{ch}", 1e9) - jv[f"stick{k}"][ch]) > 1e-4: ok = False
    check("N5 blaze stick seeds == Java BlazeModel (rings r 9/7/5, bob) at 4 ages", ok, "")
    # ------------------------------------------------------------------ S: entities
    def ent(stem): return R.jl(NEW / f"entity/{stem}.entity.json")["minecraft:client_entity"]["description"]
    van = lambda s: B.ML._parse_json((B.VRP / f"entity/{s}.entity.json").read_text())["minecraft:client_entity"]["description"]
    EXTRA = {"phantom": ({"pw_pitch": B.PH["pitch"], "pw_dust": B.PH["dust"]}, ["pw_pitch", "pw_dust"]), "blaze": ({"flame": "controller.animation.blaze.flame"}, ["flame"])}
    for tag, stem, port, a_id in (("S1", "endermite", B.em_port, B.EM["anim"]), ("S2", "vex", B.vx_port, B.VX["anim"]),
                                  ("S3", "phantom", B.ph_port, B.PH["anim"]), ("S4", "blaze", B.bz_port, B.BZ["anim"])):
        i2, p2, a2, _ = port(); d = ent(stem); ex_a, ex_n = EXTRA.get(stem, ({}, []))
        raw = json.loads((NEW / f"entity/{stem}.entity.json").read_text())
        check(f"{tag} {stem}: geometry.pw_{stem}, the port animation shipped == the port, scripts == the port, format >= 1.10.0, no legacy controllers",
              d["geometry"] == {"default": f"geometry.pw_{stem}"} and d["animations"] == {"pw_jem": a_id, **ex_a} and anims.get(a_id) == a2
              and d["scripts"]["pre_animation"] == p2 and d["scripts"]["initialize"] == i2 and d["scripts"]["animate"] == ["pw_jem"] + ex_n
              and tuple(int(x) for x in raw["format_version"].split(".")) >= (1, 10, 0) and "animation_controllers" not in d, f"format {raw['format_version']}")
    pa = anims.get(B.PH["pitch"]); _, gp = R.geo_file(NEW, "geometry.pw_phantom"); byp = {b["name"]: b for b in gp["bones"]}
    check("S3b phantom pitch: Java's whole-model pitch on pw_pitch at the origin, every former top bone under it",
          pa == B.PH_PITCH and byp.get("pw_pitch", {}).get("pivot") == [0.0, 0.0, 0.0]
          and all(b.get("parent") for b in gp["bones"] if b["name"] != "pw_pitch"), "")
    # S3c (D-C301) the wing dust Mojang's base_pose controller played: our particles-only controller + locators at the Patrix wing tips
    vph = van("phantom"); dph = ent("phantom"); ctrl = R.jl(NEW / B.PH["dust_file"])
    tips = {}
    for bone, loc, side in (("left_wing_tip2", "left_wing", 1), ("right_wing_tip2", "right_wing", -1)):
        sub = [bone] + [b["name"] for b in gp["bones"] if b.get("parent") == bone]
        xs = [v for n in sub for c in byp[n].get("cubes", []) for v in (c["origin"][0], c["origin"][0] + c["size"][0])]
        tips[loc] = ((byp[bone].get("locators") or {}).get(loc), max(xs) if side > 0 else min(xs), side)
    check("S3c phantom wing dust: particles-only controller on left_wing / right_wing, Mojang's wing_dust effect, locators at the outer tip ends",
          ctrl == B.PH_DUST_DOC and dph.get("particle_effects") == vph.get("particle_effects") == {"wing_dust": "minecraft:phantom_trail_particle"}
          and all(t[0] is not None and abs(t[0][0] - t[1]) < 1e-3 and t[0][0] * t[2] > 20 for t in tips.values())
          and {e["locator"] for e in ctrl["animation_controllers"][B.PH["dust"]]["states"]["default"]["particle_effects"]} == set(tips)
          and "animations" not in ctrl["animation_controllers"][B.PH["dust"]]["states"]["default"], str({k: v[0] for k, v in tips.items()}))
    d = ent("warden")
    check("S5 warden: geometry.pw_warden; Mojang's warden definition otherwise (scale 1.2 kept)", d["geometry"] == {"default": "geometry.pw_warden"}
          and d["scripts"]["scale"] == "1.2" and d["render_controllers"] == R.jl(B.CFG["src"] / "entity/warden.entity.json")["minecraft:client_entity"]["description"]["render_controllers"], "")
    d, v = ent("creaking"), van("creaking")
    check("S6 creaking: geometry.pw_creaking, everything else Mojang's", d["geometry"] == {"default": "geometry.pw_creaking"}
          and {k: x for k, x in d.items() if k != "geometry"} == {k: x for k, x in v.items() if k != "geometry"}, "")
    d, v = ent("breeze"), van("breeze")
    check("S7 breeze: 5 pw geometries, everything else Mojang's", set(d["geometry"].values()) == {"geometry.pw_breeze", "geometry.pw_breeze_eyes",
          "geometry.pw_breeze_wind_top", "geometry.pw_breeze_wind_mid", "geometry.pw_breeze_wind_bottom"}
          and {k: x for k, x in d.items() if k != "geometry"} == {k: x for k, x in v.items() if k != "geometry"}, "")
    # ------------------------------------------------------------------ T: textures
    z = zipfile.ZipFile(B.ZIP)
    def pz(rel): return np.asarray(Image.open(io.BytesIO(z.read(f"assets/minecraft/textures/entity/{rel}"))).convert("RGBA"))
    def ours(rel): return np.asarray(Image.open(NEW / f"textures/entity/{rel}").convert("RGBA"))
    same = {r: (ours(r).shape == pz(r).shape and (ours(r) == pz(r)).all()) for r in
            ("illager/vex.png", "illager/vex_charging.png", "breeze/breeze.png", "breeze/breeze_wind.png", "blaze.png", "endermite.png",
             "creaking/creaking.png", "creaking/creaking_eyes.png", "warden/warden.png", "warden/warden_heart.png",
             "warden/warden_pulsating_spots_1.png", "warden/warden_pulsating_spots_2.png")}
    check("T1 every converted mob's sheet is the Patrix 1.21.11 128x file, pixel-exact", all(same.values()), str({k: v for k, v in same.items() if not v}))
    ph, base, eyes = ours("phantom.png"), pz("phantom.png"), pz("phantom_eyes.png")
    m = eyes[..., 3] > 16
    check("T2 phantom = Patrix body + eye overlay merged (eye texels alpha 18, everything else untouched)",
          (ph[m, :3] == eyes[m, :3]).all() and (ph[m, 3] == 18).all() and (ph[~m] == base[~m]).all(), f"{int(m.sum())} eye texels")
    t = ours("warden/warden_tendrils.png"); w_ = ours("warden/warden.png"); s = w_.shape[0] // 128
    mask = np.zeros(t.shape[:2], bool)
    for u0, v0, u1, v1 in B.WARDEN_TENDRIL_RECTS: mask[v0 * s:v1 * s, u0 * s:u1 * s] = True
    check("T3 warden tendrils sheet = the Patrix tendril faces only", (t[mask] == w_[mask]).all() and (t[~mask, 3] == 0).all(), "")
    bio = ours("warden/warden_bioluminescent_layer.png"); sp = pz("warden/warden_s.png")
    em = (sp[..., 3] > 0) & (sp[..., 3] < 255) & (w_[..., 3] > 16)
    check("T4 warden bioluminescent sheet = Patrix LabPBR emission (colour where emissive, alpha ~ strength, 0 elsewhere)",
          (bio[~em, 3] == 0).all() and (bio[em, :3] == w_[em, :3]).all() and bio[em, 3].max() == 255, f"{int(em.sum())} emissive texels")
    # VBR (D-C303) the retro culling-box fix: pw_evoker + pw_silverfish bones byte-identical to 1.4.19, box offset + covering
    from verify_rp07_1415_rp06_1410 import world_boxes as _wb
    vbr = []
    for label, (stem, gkey, gid) in B.RETRO_VB.items():
        _, gn = R.geo_file(NEW, gid); _, go = R.geo_file(B.CFG["src"], gid)
        P_ = np.array([q for x in _wb(gn["bones"]) for q in x[2]]) / 16.0; d_ = gn["description"]; vb_ = R.van_box(stem, gkey)
        o_ = d_.get("visible_bounds_offset"); h_ = float(d_["visible_bounds_height"]); w_ = float(d_["visible_bounds_width"])
        ok_ = (gn["bones"] == go["bones"] and o_ is not None and o_[1] - h_ / 2 <= P_[:, 1].min() - 0.49 and o_[1] + h_ / 2 >= P_[:, 1].max() + 0.49
               and w_ / 2 >= max(np.abs(P_[:, 0]).max(), np.abs(P_[:, 2]).max()) + 0.49 and (not vb_ or (o_[1] - h_ / 2 <= vb_[0] + 1e-6 and o_[1] + h_ / 2 >= vb_[1] - 1e-6)))
        if not ok_: vbr.append((label, d_, vb_))
    check("VBR evoker + silverfish: bones byte-identical to 1.4.19, culling box now offset + holding the model and Mojang's box (D-C303)", not vbr, str(vbr)[:200])
    tl = R.jl(NEW / "textures/textures_list.json")
    check("T6 textures_list.json names the new warden tendrils sheet (D-C301)", "textures/entity/warden/warden_tendrils" in tl, f"{len(tl)} entries")
    be = ours("breeze/breeze_eyes.png"); bb = pz("breeze/breeze.png")
    check("T5 breeze eyes sheet = Patrix LabPBR emission on the 256 px body sheet", be.shape == bb.shape and (be[be[..., 3] > 0, :3] == bb[be[..., 3] > 0, :3]).all(),
          f"{int((be[..., 3] > 0).sum())} glowing texels")
    # ------------------------------------------------------------------ HPT
    _, g = R.geo_file(NEW, "geometry.pw_vex"); by = {b["name"]: b for b in g["bones"]}
    check("HPT vex hand points: rightItem under right_arm, leftItem under left_arm", by.get("rightItem", {}).get("parent") == "right_arm"
          and by.get("leftItem", {}).get("parent") == "left_arm", f"{by.get('rightItem', {}).get('pivot')} / {by.get('leftItem', {}).get('pivot')}")
    # ------------------------------------------------------------------ BZW
    from verify_rp07_1415_rp06_1410 import world_boxes
    ys = {}
    for gid in ("geometry.pw_breeze_wind_top", "geometry.pw_breeze_wind_mid", "geometry.pw_breeze_wind_bottom"):
        _, gg = R.geo_file(NEW, gid); names = {b["name"] for b in gg["bones"]}
        P_ = np.array([q for x in world_boxes(gg["bones"]) for q in x[2]]); ys[gid.split("_")[-1]] = (round(float(P_[:, 1].min()), 1), round(float(P_[:, 1].max()), 1))
        assert {"tornado_body", "tornado_top", "tornado_mid", "tornado_bottom"} <= names, (gid, names)
    check("BZW breeze wind layers: tornado skeleton in each, stacked bottom < mid < top under the head (y 20)",
          ys["bottom"][0] <= 0.5 and ys["bottom"][1] < ys["top"][1] and ys["mid"][0] < ys["top"][0] and ys["top"][1] <= 24, str(ys))
    # ------------------------------------------------------------------ ULC
    import uv_layout_census as U
    U.STACK = [(t_, d_) for t_, d_ in U.STACK]; U.STACK[1] = ("RP-06 1.4.20", "rp06-1420")
    rows_path = U.OUT_JS; U.OUT_MD = ROOT / "_docs/sizes/UV-LAYOUT-CENSUS-after-rp06-1420.md"; U.OUT_JS = ROOT / "_docs/sizes/UV-LAYOUT-CENSUS-after-rp06-1420.json"
    U.main(); rows = json.load(open(U.OUT_JS))
    left = sorted({r["entity"] for r in rows if r.get("verdict") == "MISMATCH" and r["entity"] in
                   {"minecraft:warden", "minecraft:creaking", "minecraft:endermite", "minecraft:vex", "minecraft:phantom", "minecraft:blaze", "minecraft:breeze"}})
    check("ULC the 7 converted mobs no longer draw our texture on a Mojang model", not left, f"still mismatched {left}")


B.CFG["verify_hooks"] = [hooks]
B.CFG["joints_ok"] = JOINT_OK
B.CFG["prec_order"] = [("StripMine RP 3.0.1", ROOT / "_intake/stack-rps/PW-StripMine-RP-v3_0_1.mcpack"), ("RP-08", ROOT / "_build/rp08-148"),
                       ("RP-07", ROOT / "_build/rp07-1425"), ("RP-06", NEW)]

if __name__ == "__main__":
    files = json.load(open(ROOT / "_docs/convb/build_rp06_1420_files.json"))
    B.CFG["extra_changed"], B.CFG["extra_added"], B.CFG["extra_removed"] = files["changed"], files["added"], files["removed"]
    sys.exit(R.verify(B.CFG))
