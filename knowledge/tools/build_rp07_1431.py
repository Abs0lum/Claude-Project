#!/usr/bin/env python3
"""build_rp07_1431.py — RP-07 Neutral Mobs RP v1.4.31 from v1.4.30 (R17, his 11:05 "GO all"; journal D-C317 / D-C318).

  GOLEM   his p13 i01 / i02 "legs are pivoting from the ground instead of from hips": FreshLX's `head2.rz = -body_top.rz/2` read a
          part channel his file never sets; the port read a variable nothing wrote, the game stopped the WHOLE pre_animation at
          that line (his log: 30 unknown variables) and the legs lost their slide. Re-ported with the fixed jem_anim_port
          (never-assigned reads seeded with the rest value: body_top.rz = 0).
  FOX     (1) the pounce pitch from 1.4.30 (unchanged); (2) his f02 "egg floats over head": the engine finds the fox's mouth
          item bone by NAME (`held_item`, Mojang's geometry.fox); ours had none. Added under the Patrix snout at Mojang's offset
          from the snout (0, -0.7, -1 px from the snout's lower front corner), rotation undoing the snout chain so the item sits
          level at rest; (3) his answer 3 "add short settle": the sit pose blends in / out over 0.25 s (r16b.blend_if).
Everything else byte-identical to 1.4.30 (the two animation files too: the fixes live in the entity scripts). verify: verify_rp07_1431.py"""
import json, shutil, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, "/home/claude/tools")
import convb_round as R
import molang_lint as ML
import r16b
import build_r16b as BR
import wing_contact as WC

ROOT = Path("/home/claude")
SRC, DST, VER = ROOT / "_build/rp07-1430", ROOT / "_build/rp07-1431", "1.4.31"
HELD_OFFSET = np.array([0.0, -0.7, -1.0])       # Mojang geometry.fox: held_item (-2, 3.3, -13) vs the snout box min corner (-2, 4, -12)


def log(m):
    print(m)
    with open(ROOT / "_logs/phase_log.md", "a") as f: f.write(f"[{time.strftime('%H:%M')} CT {time.strftime('%m-%d')}] BUILD rp07-1431: {m}\n")


def entity_path(stem): return DST / f"entity/{stem}.entity.json"


def swap_port(m, stem, anim_file):
    b, tw, th, init, pre, anim, rep = r16b.port(m)
    R.wj(DST / anim_file, {"format_version": "1.8.0", "animations": {BR.anim_id(m): anim}})
    pe = entity_path(stem); v = ML._parse_json(pe.read_text(encoding="utf-8")); desc = v["minecraft:client_entity"]["description"]
    desc["scripts"]["initialize"], desc["scripts"]["pre_animation"] = init, pre
    R.wj(pe, v)
    return rep, len(pre)


def held_item_bone(bones):
    """the fox mouth-item bone: world pivot = the snout's lower front corner + Mojang's offset; world orientation level at rest"""
    aff = WC.affines(bones, {})
    pts = np.array([p for _, _, P in WC.boxes(bones, aff, {"snout"}) for p in P])
    W = pts.min(0) + HELD_OFFSET
    A, t = aff["snout"]
    P = np.linalg.solve(A, W - t)
    # rotation undoing the snout chain (the chain is a pure x rotation at rest: body 90, head2 -90, snout -0.939)
    snout_rot = next(b for b in bones if b["name"] == "snout")["rotation"]
    rot = [-float(snout_rot[0]), 0.0, 0.0]
    bone = {"name": "held_item", "parent": "snout", "pivot": [round(float(x), 4) for x in P], "rotation": rot}
    Ah = WC.affines(bones + [bone], {})["held_item"][0]
    assert float(np.abs(Ah - np.eye(3)).max()) < 1e-4, "held_item not level at rest"
    return bone, W


def main():
    if DST.exists(): shutil.rmtree(DST)
    shutil.copytree(SRC, DST)
    rep, n = swap_port("iron_golem", "iron_golem", "animations/pw_iron_golem_jem.animation.json")
    log(f"golem re-ported: {n} statements; seeded rest reads {rep['seeded_rest_reads']}")
    rep, n = swap_port("fox", "fox", "animations/pw_fox_jem.animation.json")
    log(f"fox re-ported: {n} statements; {len(rep['blended'])} sit branches blended (0.25 s settle)")
    p, g = R.geo_file(DST, "geometry.pw_fox")
    assert "held_item" not in {b["name"] for b in g["bones"]}
    bone, W = held_item_bone(g["bones"])
    g["bones"].append(bone)
    d = R.jl(p); d["minecraft:geometry"] = [g]; R.wj(p, d)
    log(f"fox held_item under snout: pivot {bone['pivot']} rot {bone['rotation']} (world mouth point {np.round(W, 3).tolist()})")
    mp = DST / "manifest.json"; m = R.jl(mp); vv = [int(x) for x in VER.split(".")]
    m["header"]["version"] = vv
    for mod in m["modules"]: mod["version"] = vv
    m["header"]["name"] = f"AbsolutRealism Neutral Mobs RP v{VER}"
    m["header"]["description"] = (f"v{VER} (2026-09-30) iron golem walks from the hips again (its whole motion script runs); the fox carries "
                                  "items in its mouth, tilts into a pounce and settles into a sit. Includes all of 1.4.29 / 1.4.30.")
    R.wj(mp, m)
    log(f"manifest {VER}")


if __name__ == "__main__":
    main()
