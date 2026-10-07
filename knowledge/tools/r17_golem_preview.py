#!/usr/bin/env python3
"""r17_golem_preview.py — R17 (his p13 i01 / i02: "legs are pivoting from the ground instead of from hips"). Side view of the
iron golem's walk at 6 moments of one stride: TOP = what the game ran (pre_animation stopped at statement 69, the first line that
reads v.pw_ig_body_top_rz, a variable nothing ever sets; every channel that reads a variable from line 69 on is skipped),
BOTTOM = the whole script (what the fix restores; == FreshLX's JEM by the N3 gate). Preview only."""
import re, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/claude/tools")
import convb_round as R, molang_lint as ML, r16b
import wing_contact as WC
from bb_truth import truth_posed_faces
from entity_tex_render import render_entity
from convb_preview3 import camera, FOV

ROOT = Path("/home/claude"); PK = ROOT / "_build/rp07-1429"; OUT = ROOT / "_docs/r17"
W, H = 300, 330
FB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
FR = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)


def main():
    e = ML._parse_json((PK / "entity/iron_golem.entity.json").read_text())["minecraft:client_entity"]["description"]
    init, pre = e["scripts"]["initialize"], e["scripts"]["pre_animation"]
    anim = R.jl(PK / "animations/pw_iron_golem_jem.animation.json")["animations"]["animation.pw_iron_golem.jem"]
    _, g = R.geo_file(PK, "geometry.pw_iron_golem"); bones = g["bones"]
    tw, th = g["description"]["texture_width"], g["description"]["texture_height"]
    tex = PK / (e["textures"]["default"] + ".png")
    stop = next(i for i, s in enumerate(pre) if "v.pw_ig_body_top_rz" in s)
    early = {v for s in init + pre[:stop] for v in re.findall(r"\bv\.(pw_ig_[a-z0-9_]+)\s*=(?!=)", s)}
    dead = {v for s in pre[stop:] for v in re.findall(r"\bv\.(pw_ig_[a-z0-9_]+)\s*=(?!=)", s)} - early | {"pw_ig_body_top_rz"}
    log = (ROOT / "_intake/r17/p13_report.txt").read_text()
    logged = set(re.findall(r"unknown variable 'variable\.(pw_ig_[a-z0-9_]+)'", log))
    read = {v for d in anim["bones"].values() for arr in d.values() for x in arr if isinstance(x, str) for v in re.findall(r"\bv\.(pw_ig_[a-z0-9_]+)", x)}
    print("dead + read by the animation:", len(dead & read), "| his log:", len(logged), "| identical (incl. the statement-69 read):", (dead & (read | {"pw_ig_body_top_rz"})) == logged)
    def chans(pre_list, c, drop_dead):
        ch = r16b.eval_channels("iron_golem", init, pre_list, anim, c)
        if drop_dead:                                   # a channel that reads a never-set variable is skipped by the game
            for b, d in anim["bones"].items():
                for k, arr in d.items():
                    for i, x in enumerate(arr):
                        if isinstance(x, str) and any(f"v.{v}" in x for v in dead):
                            ch[b][k][i] = 1.0 if k == "scale" else 0.0
        return ch
    phases = np.linspace(0.0, 7.43, 6, endpoint=False)          # one stride of var.ls = limb_swing * 0.845
    rows = []
    for lab, pl, dd in ((f"WHAT THE GAME RAN (script stopped after line {stop} of {len(pre)}: line {stop + 1} reads a variable nothing sets)", pre[:stop], True), (f"THE FIX (all {len(pre)} lines run = FreshLX's JEM)", pre, False)):
        rows.append((lab, [truth_posed_faces(bones, tw, th, WC.affines(bones, chans(pl, {"age": 100.0 + 3 * k, "limb_swing": float(p), "limb_speed": 0.6, "head_yaw": 0.0,
                     "head_pitch": 0.0, "is_on_ground": True, "health": 100.0, "max_health": 100.0}, dd))) for k, p in enumerate(phases)]))
    allf = [f for _, fl in rows for fs in fl for f in fs]
    ev, tv = camera(allf, "east", pad=1.05)
    sheet = Image.new("RGB", (6 * (W + 4) - 4, 2 * (H + 26) + 30), (245, 245, 245)); d = ImageDraw.Draw(sheet)
    d.text((6, 6), "IRON GOLEM WALK — side view from the east (golem faces screen-left), 6 moments of one stride", fill=(20, 20, 20), font=FB)
    for r, (lab, fl) in enumerate(rows):
        y0 = 30 + r * (H + 26)
        d.text((6, y0 + 4), lab, fill=(150, 20, 20) if r == 0 else (20, 90, 30), font=FB)
        for k, fs in enumerate(fl):
            img = render_entity(fs, tex, ev, tv, W, H, fov=FOV, floor_y=0.0).convert("RGB")
            sheet.paste(img, (k * (W + 4), y0 + 22))
    OUT.mkdir(parents=True, exist_ok=True); p = OUT / "R17-GOLEM-WALK.png"; sheet.save(p); print(p, "stop index", stop, "dead vars", len(dead))


if __name__ == "__main__":
    main()
