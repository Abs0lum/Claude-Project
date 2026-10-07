#!/usr/bin/env python3
"""build_rp07_1418.py — D-C275 / D-C276. RP-07 Neutral Mobs RP v1.4.18 from v1.4.17:
  1. RAVAGER — geometry.ravager (lives in RP-07; the entity is in RP-06) rebuilt from the Patrix JEM: body + neck/head/jaw/horns in
     the FreshLX rest pose; the vanilla leg part moved onto the ground (leg4 t* = 0 -> +24 px, the D-C274 attach rule); the four Patrix
     legs (one part) bound to leg0..leg3 by quadrant, each with a hip hinge so the vanilla walk swings them diagonally; `neck` = Patrix
     neck2 (stunned moves neck + head). Holes 31 % -> 1 %.
  2. TRADER LLAMA — his 23:10 GO "build it that way" (a separate blanket layer):
     a. geometry.trader_llama.patrix from the Patrix JEM with the LLAMA template pose (the template has no trader llama: without the
        vanilla body's 90 deg the body stood upright) — 5 fur shells properly spaced (the old ones were coplanar = "south face clipping").
     b. the BLANKET LAYER = the Patrix trader_llama_decor.jem (every box inflated 0.5 px, i.e. 0.1 px OUTSIDE the outermost fur shell)
        -> new geometry.trader_llama_decor.patrix (models/entity/trader_llama_decor.geo.json), fully transparent boxes dropped (the four
        leg bands carry no decor); its animated bones share the main geometry's names / pivots / rotations so every animation moves both.
     c. texture = textures/entity/llama/trader_llama.png (already in RP-07, unused until now: the Patrix decor texture, 1024x512,
        blanket + tassels + halter only — identical, pixel for pixel, to the decor baked into trader_llama_<variant>.png).
     d. controller.render.pw_trader_llama_decor (render_controllers/pw_trader_llama_decor.render.json): Geometry.decor /
        Material.decor (entity_alphatest) / Texture.decor, drawn after controller.render.pw_trader_llama.
     e. the base coat = the plain llama coats (textures/entity/llama/creamy|white|brown|gray — what the llama already uses), so the
        blanket is not ALSO painted underneath the fur (it showed through as blue speckles).
     f. look -> animation.pw_convb.look.
  3. AXOLOTL + FROG re-baked with rest-pose part scales (D-C276): the axolotl's land legs (scale 0 in water) and the frog's croak sac
     (vanilla hides it unless croaking) are no longer drawn.
  manifest 1.4.18, uuid kept. verify: verify_rp07_1418.py."""
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, "/home/claude/tools")
import convb_round as R
from convb_preview import library, bind_info
from face_alpha_census import face_rects, opaque_fraction

ROOT = Path("/home/claude")
LL = "textures/entity/llama"
DECOR_GEO = "geometry.trader_llama_decor.patrix"
DECOR_RC = "controller.render.pw_trader_llama_decor"
DECOR_TEX = f"{LL}/trader_llama"
BASE_TEX = {"default": f"{LL}/creamy", "variant_0": f"{LL}/creamy", "variant_1": f"{LL}/white", "variant_2": f"{LL}/brown", "variant_3": f"{LL}/gray"}
TL_TEXTURES = {**BASE_TEX, "decor": DECOR_TEX}


def decor_bones(dst):
    """Build the blanket-layer bones: Patrix trader_llama_decor.jem through the same Converter B path as the main model, bound to the
    trader llama entity's bone names; transparent boxes dropped; shared bones synced to the main geometry."""
    import convb_build as cb
    ent = R.jl(dst / "entity/trader_llama.entity.json")["minecraft:client_entity"]["description"]
    anims, rcs = library(dst)
    names, _, _ = bind_info(ent, anims, rcs)
    _, main_g = R.geo_file(dst, "geometry.trader_llama.patrix")
    main = {b["name"]: b for b in main_g["bones"]}
    old_src = R.jl(ROOT / "_build/rp07-1417/models/entity/trader_llama.geo.json")["minecraft:geometry"][0]["bones"]   # quadrant reference
    moving = R.moving_bones(ent, anims) | {"head"}
    bones, tw, th, info = R.build_one("trader_llama_decor", "trader_llama", names, moving, old_src, ["head"])
    alpha = np.asarray(Image.open(dst / f"{DECOR_TEX}.png").convert("RGBA"))[..., 3]
    dropped = []
    for b in bones:
        keep = []
        for c in b.get("cubes", []):
            if any(opaque_fraction(alpha, rect, tw, th)[0] > 0 for rect in face_rects(c, b.get("mirror", False)).values()): keep.append(c)
            else: dropped.append(b["name"])
        b["cubes"] = keep
    # keep only bones that carry boxes or lead to one
    need = set()
    by = {b["name"]: b for b in bones}
    for b in bones:
        if b.get("cubes"):
            n = b["name"]
            while n: need.add(n); n = by[n].get("parent")
    bones = [b for b in bones if b["name"] in need]
    # shared animated bones must move exactly like the main geometry's
    synced, mismatch = [], []
    for b in bones:
        m = main.get(b["name"])
        if not m: continue
        same_rot = np.allclose(b.get("rotation", [0, 0, 0]), m.get("rotation", [0, 0, 0]), atol=1e-3)
        same_par = b.get("parent") == m.get("parent")
        if not (same_rot and same_par): mismatch.append(b["name"]); continue
        if not np.allclose(b["pivot"], m["pivot"], atol=1e-3):
            if np.allclose(b.get("rotation", [0, 0, 0]), 0, atol=1e-6): b["pivot"] = list(m["pivot"]); synced.append(b["name"])
            else: mismatch.append(b["name"])
    assert not mismatch, ("decor bones differ from the main geometry", mismatch)
    return bones, tw, th, {"dropped_transparent": sorted(set(dropped)), "synced_pivots": synced, "bones": [b["name"] for b in bones]}


def trader_decor_layer(dst):
    bones, tw, th, info = decor_bones(dst)
    desc = {"identifier": DECOR_GEO, "texture_width": tw, "texture_height": th,
            "visible_bounds_width": 3.0, "visible_bounds_height": 3.0, "visible_bounds_offset": [0.0, 1.5, 0.0]}
    R.wj(dst / "models/entity/trader_llama_decor.geo.json", {"format_version": "1.16.0", "minecraft:geometry": [{"description": desc, "bones": bones}]})
    R.wj(dst / "render_controllers/pw_trader_llama_decor.render.json", {"format_version": "1.10.0", "render_controllers": {
        DECOR_RC: {"geometry": "Geometry.decor", "materials": [{"*": "Material.decor"}], "textures": ["Texture.decor"]}}})
    pe = dst / "entity/trader_llama.entity.json"; d = R.jl(pe); e = d["minecraft:client_entity"]["description"]
    e["textures"] = dict(TL_TEXTURES)
    e["geometry"]["decor"] = DECOR_GEO
    e["materials"]["decor"] = "entity_alphatest"
    if DECOR_RC not in e["render_controllers"]: e["render_controllers"].append(DECOR_RC)
    R.wj(pe, d)
    return info


def verify_decor(cfg, check):
    """D — blanket layer: geometry == the bake of trader_llama_decor.jem (0.5 px shell, llama pose); every shared bone moves like the
    main geometry; the entity wires geometry / material / texture / render controller; texture files exist; the blanket boxes sit
    OUTSIDE the outermost fur shell; the base coats are the plain llama coats (no blanket painted under the fur)."""
    from convb import bake
    from verify_rp07_1415_rp06_1410 import world_boxes
    NEW = cfg["dst"]
    g = R.jl(NEW / "models/entity/trader_llama_decor.geo.json")["minecraft:geometry"][0]
    _, main_g = R.geo_file(NEW, "geometry.trader_llama.patrix")
    bones = g["bones"]; main = {b["name"]: b for b in main_g["bones"]}
    bk, tw, th, _ = bake("trader_llama_decor")
    B = {}
    for x in world_boxes(bk): B.setdefault((tuple(x[3]), x[5]), []).append(np.array(x[2]))
    errs, miss = [], []
    for x in world_boxes(bones):
        k = (tuple(x[3]), x[5])
        if k not in B: miss.append(k); continue
        errs.append(min(float(np.abs(np.array(x[2]) - q).max()) for q in B[k]))
    check("DL1 blanket layer == bake", not miss and errs and max(errs) < 0.02,
          f"{len(errs)} boxes; max corner error {max(errs) if errs else 0:.4f} px; unmatched {len(miss)}; inflate {sorted({c.get('inflate') for b in bones for c in b.get('cubes', [])})}")
    diff = [b["name"] for b in bones if b["name"] in main and (b.get("parent") != main[b["name"]].get("parent")
            or not np.allclose(b["pivot"], main[b["name"]]["pivot"], atol=1e-3) or not np.allclose(b.get("rotation", [0, 0, 0]), main[b["name"]].get("rotation", [0, 0, 0]), atol=1e-3))]
    shared = [b["name"] for b in bones if b["name"] in main]
    check("DL2 blanket bones move with the llama", not diff and {"head", "body"} <= set(shared), f"shared {shared}; differing {diff}")
    e = R.jl(NEW / "entity/trader_llama.entity.json")["minecraft:client_entity"]["description"]
    rcf = R.jl(NEW / "render_controllers/pw_trader_llama_decor.render.json")["render_controllers"][DECOR_RC]
    wired = (e["geometry"].get("decor") == DECOR_GEO and e["materials"].get("decor") == "entity_alphatest" and e["textures"].get("decor") == DECOR_TEX
             and e["render_controllers"] == ["controller.render.pw_trader_llama", DECOR_RC]
             and rcf == {"geometry": "Geometry.decor", "materials": [{"*": "Material.decor"}], "textures": ["Texture.decor"]})
    check("DL3 entity wiring", wired, f"RCs {e['render_controllers']}; geometry.decor {e['geometry'].get('decor')}; material.decor {e['materials'].get('decor')}")
    files_ok = all((NEW / f"{t}.png").exists() for t in e["textures"].values())
    dt = Image.open(NEW / f"{DECOR_TEX}.png"); a = np.asarray(dt.convert("RGBA"))[..., 3]
    check("DL4 textures exist", files_ok and dt.size == (tw * 8, th * 8), f"{len(e['textures'])} textures present {files_ok}; decor {dt.size} opaque {int((a > 0).sum())} px")
    # outside the outermost fur shell, on every face that carries blanket pixels: compare face planes in the shared bone's frame
    def planes(c):
        o, z, i = c["origin"], c["size"], c.get("inflate", 0) or 0
        return {"west": o[0] - i, "east": o[0] + z[0] + i, "down": o[1] - i, "up": o[1] + z[1] + i, "north": o[2] - i, "south": o[2] + z[2] + i}
    sign = {"west": -1, "down": -1, "north": -1, "east": 1, "up": 1, "south": 1}
    gaps = []
    for b in bones:
        for c in b.get("cubes", []):
            dp = planes(c)
            for f, rect in face_rects(c, b.get("mirror", False)).items():
                if opaque_fraction(a, rect, tw, th)[0] <= 0: continue          # no blanket pixels on this face
                for mc in main.get(b["name"], {}).get("cubes", []):
                    gaps.append((sign[f] * (dp[f] - planes(mc)[f]), b["name"], f))
    worst = min(gaps) if gaps else (99.0, "-", "-")
    check("DL5 blanket outside the fur", gaps and worst[0] >= 0.05,
          f"{len(gaps)} blanket-face/fur-shell pairs; smallest outward gap {worst[0]:.3f} px ({worst[1]} {worst[2]}); faces with no blanket pixels are not drawn visibly")
    base = [e["textures"][k] for k in ("variant_0", "variant_1", "variant_2", "variant_3")]
    check("DL6 plain coats underneath", base == [BASE_TEX[k] for k in ("variant_0", "variant_1", "variant_2", "variant_3")], f"base coats {base}")


CFG = {
    "src": ROOT / "_build/rp07-1417", "dst": ROOT / "_build/rp07-1418", "version": "1.4.18",
    "name": "AbsolutRealism Neutral Mobs RP v1.4.18",
    "desc": ("v1.4.18 (2026-09-28) RAVAGER + TRADER LLAMA (D-C275/D-C276): the ravager rebuilt from the Patrix model (one solid body, head low "
             "between the front legs, horns, four legs on the ground that walk); the trader llama rebuilt like the llama, its blanket, tassels "
             "and halter drawn as their own layer over the fur; axolotl without the extra set of legs; frog without the always-on throat sac. "
             "Everything else byte-identical to v1.4.17."),
    "jobs": [("ravager", "ravager", "default", "ravager", "default"), ("trader llama", "trader_llama", "default", "trader_llama", "default"),
             # D-C276 re-bakes (my 1.4.16 regressions): FreshLX part SCALES — the axolotl's land-leg set is scaled to 0 in water (Java hides
             # it; 1.4.16 drew all 8 legs) and the frog's croak sac is shown by vanilla only while croaking (1.4.16 drew it always)
             ("axolotl", "axolotl", "default", "axolotl", "default"), ("frog", "frog", "default", "frog", "default")],
    "entity_src": {"ravager": ROOT / "_build/rp06-1411"},
    "look": {"trader_llama": "animation.common.look_at_target"},
    "post": [trader_decor_layer],
    "extra_added": ["models/entity/trader_llama_decor.geo.json", "render_controllers/pw_trader_llama_decor.render.json"],
    "textures_changed": {"trader_llama": TL_TEXTURES},
    "verify_hooks": [verify_decor],
    "unbound_ok": {},
    "placement": {"ravager": ("ground",), "trader llama": ("ground",), "axolotl": ("centre", 2.0, 3.0), "frog": ("ground",)},
    "report": ROOT / "_docs/convb/build_1418_report.json",
}

if __name__ == "__main__":
    R.build(CFG)
