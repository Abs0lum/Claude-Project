#!/usr/bin/env python3
"""convb_preview3.py — D-C277 batch previews (RP-07 1.4.19 / RP-06 1.4.12 candidates).

NEW = exactly what the round build writes (convb_round.build_one: bake + binds + Java parents + legs + frames), OLD = what the
pack ships now, same cameras, checker floor at y 0 in every tile, camera distance fitted to the model's HEIGHT as well as its
span (the 23:5x dry run cut the heads off the tall mobs). Optional REFERENCE tiles (a vanilla rig posed from Mojang's own
numbers, flat colours) sit first in the row — the guardian spike layout his 00:10 message asked me to research.

Usage: convb_preview3.py <label> [...]   -> _docs/convb/p3_<stem>.png"""
import json, math, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/claude/tools")
from equine_compare import bone_affines, posed_faces
from entity_tex_render import render_entity
from face_alpha_census import resolve_texture
from convb_preview import library, bind_info, holes, floating
from convb_preview2 import entity, geo
from convb_round import build_one, moving_bones

ROOT = Path("/home/claude"); OUT = ROOT / "_docs/convb"
W, H = 330, 270
try:
    FB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13); FR = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
except Exception:
    FB = FR = ImageFont.load_default()
DIRS = {"front": (0, 0.30, 1), "back": (0, 0.30, -1), "east": (1, 0.30, 0), "west": (-1, 0.30, 0), "top": (0.15, 1.0, 0.35),
        "front-east": (0.7, 0.35, 0.7), "front-west": (-0.7, 0.35, 0.7), "back-east": (0.7, 0.35, -0.7), "below": (0.3, -0.6, 0.7)}
FOV = 50.0


def camera(faces, view, pad=1.25):
    P = np.array([p for f in faces for p in f.pts]); P = P * np.array([1, 1, -1])      # world frame (render_entity world=True)
    lo, hi = P.min(0), P.max(0); c = (lo + hi) / 2; r = float(np.linalg.norm(hi - lo)) / 2
    d = np.array(DIRS[view], float); d /= np.linalg.norm(d)
    dist = max(24.0, r / math.sin(math.radians(FOV / 2)) * pad * 0.92)
    return list(c + d * dist), list(c)


def tile(img, title, sub, color):
    img = img.convert("RGB"); d = ImageDraw.Draw(img); d.rectangle([0, 0, W, 32], fill=color)
    d.text((5, 2), title, fill=(255, 255, 255), font=FB); d.text((5, 17), sub, fill=(225, 230, 240), font=FR)
    return img


def new_old(stem, gkey, jname, look=None):
    tag, rp, desc = entity(stem); anims, rcs = library(rp)
    ident = desc["geometry"][gkey]; old, otw, oth = geo(rp, ident)
    names, rel, _ = bind_info(desc, anims, rcs)
    look = (["head"] if rel else []) if look is None else look
    new, ntw, nth, info = build_one(jname, stem, names, moving_bones(desc, anims) | set(look), old, look)
    return tag, desc, (new, ntw, nth), (old, otw, oth), info, rel


def render_row(label, faces_sets, cams, out_name, sub_new, sub_old):
    """faces_sets: {"NEW": (faces, tex), "OLD": (...), "REF": (...)}; cams: [(key, view, title)]"""
    allf = [f for k, (fs, _) in faces_sets.items() if k != "REF" for f in fs]
    cells = []
    for key, view, title in cams:
        fs, tex = faces_sets[key]
        e, t = camera(fs if key == "REF" else allf, view)
        col = {"NEW": (30, 70, 140), "OLD": (130, 30, 30), "REF": (40, 110, 60)}[key]
        sub = {"NEW": sub_new, "OLD": sub_old, "REF": "reference: vanilla rig, Mojang's spike numbers"}[key]
        cells.append(tile(render_entity(fs, tex, e, t, W, H, fov=FOV, floor_y=0.0), f"{label.upper()} — {title}", sub, col))
    row = Image.new("RGB", (len(cells) * (W + 4) - 4, H), (255, 255, 255))
    for i, c in enumerate(cells): row.paste(c, (i * (W + 4), 0))
    row.save(OUT / out_name); return row


# ---------------------------------------------------------------------------------------------------------- guardian ref
def guardian_reference():
    """Vanilla guardian body + the 12 spikes where Java puts them at rest in water (fully extended, k = 1): centre =
    (SPIKE_X, 24 - (16 + SPIKE_Y), SPIKE_Z) in Bedrock file coords, rotation = animation.guardian.setup (Mojang)."""
    import convb
    tex = OUT / "_ref_guardian_tex.png"
    im = Image.new("RGBA", (64, 64), (60, 120, 115, 255)); dr = ImageDraw.Draw(im)
    dr.rectangle([0, 32, 8, 43], fill=(235, 140, 40, 255)); dr.rectangle([0, 48, 40, 63], fill=(90, 150, 140, 255))
    im.save(tex)
    setup = {0: [-45, 0, 0], 1: [45, 0, 0], 2: [0, 0, 45], 3: [0, 0, -45], 4: [90, 45, 0], 5: [90, -45, 0], 6: [90, -135, 0],
             7: [90, 135, 0], 8: [-135, 0, 0], 9: [135, 0, 0], 10: [0, 0, 135], 11: [0, 0, -135]}
    bones = [{"name": "head", "pivot": [0, 24, 0], "rotation": [0, 0, 0],
              "cubes": [{"origin": [-6, 2, -8], "size": [12, 12, 16], "uv": [0, 0]}]},
             {"name": "tail0", "parent": "head", "pivot": [0, 24, 0], "rotation": [0, 0, 0], "cubes": [{"origin": [-2, 6, 7], "size": [4, 4, 8], "uv": [0, 48]}]},
             {"name": "tail1", "parent": "tail0", "pivot": [0, 24, 0], "rotation": [0, 0, 0], "cubes": [{"origin": [-1.5, 6.5, 14], "size": [3, 3, 7], "uv": [0, 48]}]},
             {"name": "tail2", "parent": "tail1", "pivot": [0, 24, 0], "rotation": [0, 0, 0], "cubes": [{"origin": [-1, 7, 20], "size": [2, 2, 6], "uv": [0, 48]}]}]
    for i in range(12):
        c = [convb._SPK_X[i], 24 - (16 + convb._SPK_Y[i]), convb._SPK_Z[i]]
        bones.append({"name": f"spike{i}", "parent": "head", "pivot": c, "rotation": setup[i],
                      "cubes": [{"origin": [c[0] - 1, c[1] - 4.5, c[2] - 1], "size": [2, 9, 2], "uv": [0, 32]}]})
    return bones, 64, 64, tex


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = {"guardian": ("guardian", "default", "guardian", "default"), "elder guardian": ("elder_guardian", "default", "elder_guardian", "default"),
            "spider": ("spider", "default", "spider", "default"), "tadpole": ("tadpole", "default", "tadpole", "default"),
            "bee": ("bee", "default", "bee", "default"), "piglin": ("piglin", "default", "piglin", "default"),
            "piglin brute": ("piglin_brute", "default", "piglin_brute", "default"), "bogged": ("bogged", "default", "bogged", "default"),
            "zombified piglin": ("zombie_pigman", "default", "zombified_piglin", "default")}
    rep = {}
    for label in sys.argv[1:] or list(jobs):
        stem, gkey, jname, tkey = jobs[label]
        tag, desc, (new, ntw, nth), (old, otw, oth), info, rel = new_old(stem, gkey, jname)
        tp = resolve_texture(desc["textures"][tkey])
        oldn = {b["name"] for b in old}
        nf = posed_faces(new, ntw, nth, bone_affines(new))
        of = posed_faces(old, otw, oth, bone_affines(old, abs_rot={n: [0, 0, 0] for n in rel if n in oldn}))
        P = np.array([p for f in nf for p in f.pts]); lo, hi = P.min(0), P.max(0)
        sub_new = f"holes {holes(new, ntw, nth, tp):.0f}% · floating {len(floating(new))} · y {lo[1]:.1f}..{hi[1]:.1f}"
        sub_old = f"holes {holes(old, otw, oth, tp):.0f}% · floating {len(floating(old))} (ships now)"
        sets = {"NEW": (nf, tp), "OLD": (of, tp)}
        if stem in ("guardian", "elder_guardian"):
            rb, rtw, rth, rtex = guardian_reference()
            sets["REF"] = (posed_faces(rb, rtw, rth, bone_affines(rb)), rtex)
            cams = [("REF", "front-east", "REFERENCE 3/4 front"), ("NEW", "front-east", "NEW 3/4 front"), ("NEW", "front", "NEW front"),
                    ("NEW", "top", "NEW top"), ("NEW", "east", "NEW side (E)"), ("OLD", "front-east", "OLD 3/4 front")]
        else:
            cams = [("NEW", "east", "NEW side (E)"), ("NEW", "front-east", "NEW 3/4 front"), ("NEW", "front-west", "NEW 3/4 front-W"),
                    ("NEW", "back-east", "NEW 3/4 back"), ("OLD", "east", "OLD side (E)"), ("OLD", "front-east", "OLD 3/4 front")]
        render_row(label, sets, cams, f"p3_{stem}.png", sub_new, sub_old)
        rep[label] = {"pack": tag, "mapping": {k: v for k, v in info["mapping"].items() if k != v}, "unbound": info["missing"],
                      "frames": sorted(info["frames"]), "pivot_shift": info["pivot_shift"], "extent": [lo.round(2).tolist(), hi.round(2).tolist()]}
        print(label, json.dumps(rep[label]))
    old_rep = json.load(open(OUT / "p3_report.json")) if (OUT / "p3_report.json").exists() else {}
    old_rep.update(rep); json.dump(old_rep, open(OUT / "p3_report.json", "w"), indent=1)


if __name__ == "__main__":
    main()
