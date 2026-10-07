#!/usr/bin/env python3
"""verify_rp07_1426.py — the gate for tools/build_rp07_1426.py (FA-1 RP-07).
convb_round.verify (A/J/K diff, per-job B/C/D/E/F/G/L, MLS · ARS · RCV · FMT · RBW · ATT · PREC) + this round's hooks:
  N1 parrot Molang == JEM (perched / walking / flying / sitting / shoulder / dancing; visibility of the two wing sets and the
     dance legs as bone scale)   N2 allay Molang == JEM (idle / flying / holding / dancing)
  S1-S4 entities   T1-T2 textures   HPT allay rightItem   PIV animated bones sit on Mojang's pivots (vanilla-animated mobs)
  ULC allay + sniffer no longer drawn on Mojang's model
Static checks only rule OUT (P1); his in-game witness rules IN."""
import io, itertools, json, math, sys, zipfile
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, "/home/claude/tools")
import build_rp07_1426 as B            # (sets the shared CEM folder with sniffer_neutral.jem)
import convb_round as R
import jem_anim_port as P
import build_rp06_1420 as B6

ROOT = Path("/home/claude")
NEW = B.CFG["dst"]


def hooks(cfg, check):
    anims = {}
    for f in (NEW / "animations").glob("pw_*.animation.json"): anims.update(R.jl(f)["animations"])
    # N1 parrot
    init, pre, anim, _ = B.pa_port()
    cs = []
    for a, l, s, y, p, st in itertools.product((0.0, 41.0, 333.0), (0.0, 2.3), (0.0, 0.5), (0.0, 35.0), (0.0, -20.0),
                                               ("perch", "fly", "sit", "shoulder", "dance")):
        c = {"age": a, "time": a, "limb_swing": l, "limb_speed": s, "head_yaw": y, "head_pitch": p}
        if st == "fly": c["is_on_ground"] = False
        if st == "sit": c["is_sitting"] = True
        if st == "shoulder": c.update(is_on_shoulder=True, is_on_ground=False)
        if st == "dance": c["_dance"] = True
        cs.append(c)
    w = P.numeric_check("parrot", B.PA["prefix"], init, pre, anim, cs, seed_fn=B.pa_java, env_fn=B.pa_env)
    check(f"N1 parrot Molang == JEM ({len(cs)} cases: perched, flying, sitting, shoulder, dancing; wing sets + dance legs by scale)",
          w["rotation"] < 1e-3 and w["position"] < 1e-4 and w["scale"] < 1e-6, str(w))
    # N2 allay
    init, pre, anim, _ = B.al_port()
    cs = []
    for a, l, s, y, p, (h, d) in itertools.product((0.0, 41.0, 333.0), (0.0, 2.3), (0.0, 0.2, 0.6), (0.0, 35.0), (0.0, -20.0),
                                                   ((0, 0), (1, 0), (0, 1))):
        cs.append({"age": a, "limb_swing": l, "limb_speed": s, "head_yaw": y, "head_pitch": p, "_hold": h, "_dance": d})
    cs += [{"age": 40.0, "hurt_time": 6.0, "is_hurt": True}, {"age": 40.0, "death_time": 8.0, "is_alive": False}]
    w = P.numeric_check("allay", B.AL["prefix"], init, pre, anim, cs, seed_fn=B.al_java, env_fn=B.al_env)
    check(f"N2 allay Molang == JEM with Java AllayModel seeds ({len(cs)} cases: idle, flying, holding, dancing)",
          w["rotation"] < 1e-3 and w["position"] < 1e-4 and w["scale"] < 1e-6, str(w))
    # S entities
    def ent(stem): return R.jl(NEW / f"entity/{stem}.entity.json")["minecraft:client_entity"]["description"]
    def raw(stem): return json.loads((NEW / f"entity/{stem}.entity.json").read_text())
    van = lambda s: B6.ML._parse_json((B6.VRP / f"entity/{s}.entity.json").read_text())["minecraft:client_entity"]["description"]
    i2, p2, a2, _ = B.pa_port(); d = ent("parrot")
    check("S1 parrot: geometry.pw_parrot, the port animation + scripts, Mojang's textures / render controller, format >= 1.10.0",
          d["geometry"] == {"default": "geometry.pw_parrot"} and d["animations"] == {"pw_jem": B.PA["anim"]} and anims.get(B.PA["anim"]) == a2
          and d["scripts"] == {"initialize": i2, "pre_animation": p2, "animate": ["pw_jem"]} and d["textures"] == van("parrot")["textures"]
          and d["render_controllers"] == van("parrot")["render_controllers"] and raw("parrot")["format_version"] >= "1.10.0", "")
    d, v = ent("bat"), van("bat")
    check("S2 bat: geometry.pw_bat + the Patrix sheet; Mojang's definition otherwise (bat_v2 resting / flying)",
          d["geometry"] == {"default": "geometry.pw_bat"} and d["textures"] == {"default": "textures/entity/bat"}
          and {k: x for k, x in d.items() if k not in ("geometry", "textures")} == {k: x for k, x in v.items() if k not in ("geometry", "textures")}, "")
    i2, p2, a2, _ = B.al_port(); d, v = ent("allay"), van("allay")
    check("S3 allay: geometry.pw_allay, the port, attachables on, Mojang's trident variable kept",
          d["geometry"] == {"default": "geometry.pw_allay"} and d["animations"] == {"pw_jem": B.AL["anim"]} and anims.get(B.AL["anim"]) == a2
          and d["scripts"]["pre_animation"] == v["scripts"]["pre_animation"] + p2 and d["scripts"]["initialize"] == i2
          and d.get("enable_attachables") and raw("allay")["format_version"] >= "1.10.0", "")
    d, v = ent("sniffer"), van("sniffer")
    check("S4 sniffer: geometry.pw_sniffer (baby Mojang's), Mojang's definition otherwise", d["geometry"] == {"default": "geometry.pw_sniffer", "baby": "geometry.sniffer.baby"}
          and {k: x for k, x in d.items() if k != "geometry"} == {k: x for k, x in v.items() if k != "geometry"}, "")
    # T textures
    z = zipfile.ZipFile(B6.ZIP)
    def pz(rel): return np.asarray(Image.open(io.BytesIO(z.read(f"assets/minecraft/textures/entity/{rel}"))).convert("RGBA"))
    def ours(rel): return np.asarray(Image.open(NEW / f"textures/entity/{rel}").convert("RGBA"))
    rels = [f"parrot/parrot_{c}.png" for c in ("blue", "green", "grey", "red_blue", "yellow_blue")] + ["allay/allay.png", "bat.png", "sniffer/sniffer.png"]
    bad = [r for r in rels if not (ours(r).shape == pz(r).shape and (ours(r) == pz(r)).all())]
    check("T1 every converted mob's sheet is the Patrix 1.21.11 128x file, pixel-exact", not bad, str(bad))
    # HPT
    _, g = R.geo_file(NEW, "geometry.pw_allay"); by = {b["name"]: b for b in g["bones"]}
    check("HPT allay rightItem under body, Mojang's -80 deg hold", by.get("rightItem", {}).get("parent") == "body" and by["rightItem"]["rotation"] == [-80.0, 0.0, 0.0],
          f"{by.get('rightItem', {}).get('pivot')}")
    # LOC (D-C301) Mojang's lead locators carried to the same-named bones, same coordinates
    bad, n = [], 0
    for stem, (ours_id, van_id) in B.LOCATOR_MOBS.items():
        _, gg = R.geo_file(NEW, ours_id); ob = {b["name"]: b for b in gg["bones"]}
        for vb in B6.vgeo(van_id)[0]:
            for loc, xyz in (vb.get("locators") or {}).items():
                if vb["name"] not in ob: continue
                n += 1
                if (ob[vb["name"]].get("locators") or {}).get(loc) != [float(v) for v in xyz]: bad.append((stem, vb["name"], loc))
    check(f"LOC Mojang's locators on the same-named bones of parrot / allay / sniffer ({n} carried; the allay's root.lead_hold has no bone)", not bad and n >= 9, str(bad))
    # PIV
    from convb_preview import library
    anl, _ = library(NEW)
    bad = []
    for stem, ours_id, van_id in (("bat", "geometry.pw_bat", "geometry.bat_v2"), ("sniffer", "geometry.pw_sniffer", "geometry.sniffer")):
        _, gg = R.geo_file(NEW, ours_id); ob = {b["name"]: b for b in gg["bones"]}; vb = {b["name"]: b for b in B6.vgeo(van_id)[0]}
        for short, aid in ent(stem)["animations"].items():
            for bn, bv in ((anl.get(aid) or {}).get("bones") or {}).items():
                if isinstance(bv, dict) and "rotation" in bv and bn in ob and bn in vb and np.abs(np.array(ob[bn]["pivot"]) - np.array(vb[bn]["pivot"])).max() > 1.0:
                    bad.append((stem, bn, ob[bn]["pivot"], vb[bn]["pivot"]))
    check("PIV every bone Mojang's animations rotate sits within 1 px of Mojang's pivot (bat, sniffer)", not bad, str(sorted(set(map(str, bad)))[:4]))
    # ULC
    import uv_layout_census as U
    U.STACK = list(U.STACK); U.STACK[0] = ("RP-07 1.4.26", "rp07-1426"); U.STACK[1] = ("RP-06 1.4.20", "rp06-1420")
    U.OUT_MD = ROOT / "_docs/sizes/UV-LAYOUT-CENSUS-after-fa1.md"; U.OUT_JS = ROOT / "_docs/sizes/UV-LAYOUT-CENSUS-after-fa1.json"
    U.main(); rows = json.load(open(U.OUT_JS))
    left = sorted({r["entity"] for r in rows if r.get("verdict") == "MISMATCH" and r["entity"] in {"minecraft:allay", "minecraft:sniffer", "minecraft:parrot", "minecraft:bat"}})
    check("ULC allay, sniffer, parrot, bat no longer draw our texture on a Mojang model", not left, f"still {left}")


B.CFG["verify_hooks"] = [hooks]
B.CFG["prec_order"] = [("StripMine RP 3.0.1", ROOT / "_intake/stack-rps/PW-StripMine-RP-v3_0_1.mcpack"), ("RP-08", ROOT / "_build/rp08-148"),
                       ("RP-07", NEW), ("RP-06", ROOT / "_build/rp06-1420")]

if __name__ == "__main__":
    files = json.load(open(ROOT / "_docs/convb/build_rp07_1426_files.json"))
    B.CFG["extra_changed"], B.CFG["extra_added"], B.CFG["extra_removed"] = files["changed"], files["added"], files["removed"]
    sys.exit(R.verify(B.CFG))
