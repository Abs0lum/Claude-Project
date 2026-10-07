#!/usr/bin/env python3
"""build_rp06_1421.py — R14 fix round (D-C306 / D-C307, his GO 00:5x CT 09-30). RP-06 Hostile Mobs RP v1.4.21 from v1.4.20.
  VEX    arms nested UNDER the body (Java VexModel tree: root > body > right_arm / left_arm; FreshLX's JEM subtracts body.r* in
         the arm formulas and adds body.t* only in its 'testing' mode = it assumes the nesting). Converter B `anim_child`:
         the arm's runtime pivot = the body's + the arm's own Java offset; the body's pose now reaches the arms (L-CEM-JAVA-TREE).
         Hand points recomputed in the geometry FILE frame (the bind pose Bedrock pivots live in; 1.4.20 took them from the
         rotated rest pose = the arm's rest rotation applied twice). enable_attachables TRUE (the allay, which drew its item
         in R14, has it; the vex did not) — the sword probe of lineup p11 tells which of the open candidates it was.
  BLAZE  self-glow restored (L-ENT-ALPHA-EMISSIVE): Mojang's blaze materials (blaze_body / blaze_head) read the texture ALPHA
         as the lit share — vanilla's sheet has alpha 90 on every drawn texel (~65 % self-lit, Java's full-bright blaze); the
         Patrix sheet we ship had 255 (0 % self-lit). Drawn texels -> 90, cut-outs stay 0, colour untouched. Vibrant Visuals:
         the first entity TEXTURE SET (L-ENT-MERS probe): blaze_mers from the Patrix LabPBR specular (lesson #156: emission =
         specular alpha where < 255) at the colour sheet's own size, in the same shape as Mojang's blaze.texture_set.json.
Everything else byte-identical to 1.4.20. manifest 1.4.21, uuid kept. verify: verify_rp06_1421.py."""
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, "/home/claude/tools")
import convb_round as R
import convb
import jem_anim_port as P
import build_rp06_1420 as B6

ROOT = Path("/home/claude")
CHANGED, ADDED, REMOVED = [], [], []

# ------------------------------------------------------------------------------------------------ the Java tree (vex)
convb.JAVA_PARENT["vex"] = {"right_arm": "body", "left_arm": "body"}
for _c in ("right_arm", "left_arm"): convb.PART_PIVOT.setdefault("vex", {})[_c] = "anim_child"


def mers_156(spec):
    """Lesson #156 (CONFIRMED v1.2.32) — LabPBR _s -> Bedrock MERS: M = 255 if G >= 230 else 0 · E = A if A < 255 else 0 ·
    R = 255 - R_lab · S = (B - 64) * 255 / 191 if B >= 65 else 0."""
    Rr, G, B, A = (spec[..., i].astype(int) for i in range(4))
    out = np.zeros(spec.shape, np.uint8)
    out[..., 0] = np.where(G >= 230, 255, 0)
    out[..., 1] = np.where(A < 255, A, 0)
    out[..., 2] = 255 - Rr
    out[..., 3] = np.where(B >= 65, np.round((B - 64) * 255 / 191), 0)
    return out


def vex_update(dst):
    """the port is independent of the nesting (arm channels are Java-local deltas); re-run it and prove the shipped animation +
    scripts are what it produces, then switch attachables on"""
    init, pre, anim, _ = B6.vx_port()
    shipped = R.jl(dst / "animations/pw_vex.animation.json")["animations"][B6.VX["anim"]]
    same_anim = json.dumps(shipped, sort_keys=True) == json.dumps(json.loads(json.dumps(anim)), sort_keys=True)
    pe = dst / "entity/vex.entity.json"; d = R.jl(pe); desc = d["minecraft:client_entity"]["description"]
    same_scripts = desc["scripts"]["pre_animation"] == pre and desc["scripts"]["initialize"] == init
    if not same_anim:
        R.wj(dst / "animations/pw_vex.animation.json", {"format_version": "1.8.0", "animations": {B6.VX["anim"]: anim}})
        CHANGED.append("animations/pw_vex.animation.json")
    if not same_scripts:
        desc["scripts"]["initialize"] = init; desc["scripts"]["pre_animation"] = pre
    assert not desc.get("enable_attachables"), desc.get("enable_attachables")
    desc["enable_attachables"] = True
    R.wj(pe, d); CHANGED.append("entity/vex.entity.json")
    return f"vex port re-run: animation {'unchanged' if same_anim else 'REWRITTEN'}, scripts {'unchanged' if same_scripts else 'REWRITTEN'}; enable_attachables true"


def vex_hands_file_frame(dst):
    """rightItem / leftItem at the bottom centre of the arm's cube in the FILE frame (Bedrock pivots are bind-pose model
    coordinates; the arm's own and its parents' rotations are applied at run time), child of the arm, rotation 0"""
    p, g = R.geo_file(dst, "geometry.pw_vex"); bones = g["bones"]; by = {b["name"]: b for b in bones}
    out = {}
    for item, arm in (("rightItem", "right_arm"), ("leftItem", "left_arm")):
        assert item not in by and arm in by and by[arm].get("parent") == "body", (item, arm, by.get(arm, {}).get("parent"))
        cs = by[arm]["cubes"]; assert len(cs) == 1 and not any(cs[0].get("rotation", [0, 0, 0]) or []), cs
        o, s = cs[0]["origin"], cs[0]["size"]
        piv = [round(o[0] + s[0] / 2, 3), round(o[1], 3), round(o[2] + s[2] / 2, 3)]
        bones.append({"name": item, "parent": arm, "pivot": piv, "rotation": [0.0, 0.0, 0.0], "cubes": []}); out[item] = piv
    d = R.jl(p); d["minecraft:geometry"] = [g]; R.wj(p, d)
    return f"vex hand points (file frame) {out}"


BLAZE_ALPHA = 90          # Mojang's blaze sheet: every drawn texel alpha 90 (1,584 texels 0 + 464 texels 90)


def blaze_glow(dst):
    rel = "textures/entity/blaze.png"; p = dst / rel
    a = np.asarray(Image.open(p).convert("RGBA")).copy()
    vals = set(np.unique(a[..., 3]).tolist()); assert vals <= {0, 255}, vals
    drawn = a[..., 3] > 0; n = int(drawn.sum())
    a[..., 3][drawn] = BLAZE_ALPHA
    Image.fromarray(a, "RGBA").save(p, optimize=True); CHANGED.append(rel)
    spec = np.asarray(B6.ptex("blaze_s.png"))
    assert spec.shape == a.shape, (spec.shape, a.shape)
    mers = mers_156(spec); mers[~drawn] = 0
    Image.fromarray(mers, "RGBA").save(dst / "textures/entity/blaze_mers.png", optimize=True); ADDED.append("textures/entity/blaze_mers.png")
    ts = {"format_version": "1.21.30", "minecraft:texture_set": {"color": "blaze", "metalness_emissive_roughness_subsurface": "blaze_mers"}}
    R.wj(dst / "textures/entity/blaze.texture_set.json", ts); ADDED.append("textures/entity/blaze.texture_set.json")
    tl = dst / "textures/textures_list.json"; lst = R.jl(tl)
    if "textures/entity/blaze_mers" not in lst:
        lst.insert(lst.index("textures/entity/blaze") + 1, "textures/entity/blaze_mers"); R.wj(tl, lst); CHANGED.append("textures/textures_list.json")
    em = int((mers[..., 1] > 0).sum())
    return f"blaze: {n} drawn texels alpha 255 -> {BLAZE_ALPHA}; blaze_mers {mers.shape[1]}x{mers.shape[0]} ({em} emissive texels, max {int(mers[..., 1].max())}); texture set + textures_list"


JOBS = [("vex", "vex", "default", "vex", "default")]
PRE = [vex_update]
POST = [vex_hands_file_frame, blaze_glow]

CFG = {
    "src": ROOT / "_build/rp06-1420", "dst": ROOT / "_build/rp06-1421", "version": "1.4.21",
    "name": "AbsolutRealism Hostile Mobs RP v1.4.21",
    "desc": ("v1.4.21 (2026-09-30) R14 fixes: the vex's arms hang from its body (they floated), its hand points sit in the "
             "model's own frame and attachments are on (sword test); the blaze glows again (Mojang's self-light through the "
             "texture alpha, plus Patrix's fire glow in Vibrant Visuals). Includes all of 1.4.20."),
    "pre": PRE, "jobs": JOBS, "look": {}, "frame_exempt": {"vex": B6.FRAME_EXEMPT["vex"]}, "unbound_ok": {},
    "placement": {"vex": B6.PLACEMENT["vex"]}, "post": POST, "png_checked_elsewhere": ["textures/entity/blaze.png"],
    "extra_changed": CHANGED, "extra_added": ADDED, "extra_removed": REMOVED,
    "ars_tag": "RP-06", "ars_stack": [ROOT / "_build/rp07-1426"], "verify_hooks": [],
    "report": ROOT / "_docs/convb/build_rp06_1421_report.json",
}

if __name__ == "__main__":
    R.build(CFG)
    json.dump({"changed": sorted(set(CHANGED)), "added": sorted(set(ADDED)), "removed": REMOVED},
              open(ROOT / "_docs/convb/build_rp06_1421_files.json", "w"), indent=1)
