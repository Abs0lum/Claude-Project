#!/usr/bin/env python3
"""r16b_preview.py — R16b posed previews for his eye: per mob the SHIPPED model (1.4.28 / 1.4.22, rest pose) next to the PORTED
model in its states, posed by the SHIPPED animation file + entity scripts (the Bedrock transform: parent . T(pos) . T(pivot) . R . S
. T(-pivot)), textured with the pack's own texture. Output _docs/r16b/R16B-PREVIEW-<mob>.png"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/claude/tools")
import convb_round as R
import molang_lint as ML
import r16b
import wing_contact as WC
from bb_truth import truth_posed_faces
from entity_tex_render import render_entity
from convb_preview3 import camera, FOV
from equine_compare import bone_affines

ROOT = Path("/home/claude"); OUT = ROOT / "_docs/r16b"
W, H = 420, 340
try:
    FB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
    FR = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
except Exception:
    FB = FR = ImageFont.load_default()

WALK = {"age": 37.0, "limb_swing": 5.1, "limb_speed": 0.35}
RUN = {"age": 211.0, "limb_swing": 13.7, "limb_speed": 0.9}
IDLE = {"age": 505.0, "limb_swing": 0.0, "limb_speed": 0.0}
STATES = {
    "hoglin": [("idle", IDLE), ("walk", WALK), ("run", RUN), ("attack (mid-swing)", {**IDLE, "_attack": 0.5})],
    "zoglin": [("idle", IDLE), ("walk", WALK), ("run", RUN), ("attack (mid-swing)", {**IDLE, "_attack": 0.5})],
    "cod": [("swimming", {**IDLE, "is_in_water": True, "is_on_ground": False}), ("swimming fast", {**WALK, "is_in_water": True, "is_on_ground": False}),
            ("flopping on land", {**IDLE, "age": 40.0, "is_in_water": False, "is_on_ground": True})],
    "fox": [("idle", IDLE), ("walk", WALK), ("run", RUN), ("sitting", {**IDLE, "_si": 1, "is_sitting": True}), ("sleeping", {**IDLE, "_sl": 1}),
            ("stalking (crouch)", {**IDLE, "_st": 1})],
    "cat": [("idle", IDLE), ("walk", WALK), ("sprint", {**RUN, "is_sprinting": True}), ("sitting", {**IDLE, "is_sitting": True}),
            ("lying down", {**IDLE, "_lie": 1}), ("sneaking", {**WALK, "is_sneaking": True})],
    "ocelot": [("idle", IDLE), ("walk", WALK), ("sprint", {**RUN, "is_sprinting": True}), ("sitting", {**IDLE, "is_sitting": True}),
               ("sneaking", {**WALK, "is_sneaking": True})],
    "goat": [("idle", IDLE), ("walk", WALK), ("run", RUN), ("ram (head down)", {**IDLE, "_bow": 1.0}), ("in the air (jump)", {**IDLE, "is_on_ground": False}),
             ("left horn lost", {**IDLE, "_lh": 0})],
    "iron_golem": [("idle", {**IDLE, "health": 100.0, "max_health": 100.0}), ("walk", {**WALK, "health": 100.0, "max_health": 100.0}),
                   ("run", {**RUN, "health": 100.0, "max_health": 100.0}), ("attack (mid-swing)", {**IDLE, "_atk": 5.0, "health": 100.0, "max_health": 100.0}),
                   ("offering a flower", {**IDLE, "_flw": 35.0, "health": 100.0, "max_health": 100.0}),
                   ("badly hurt, walking", {**WALK, "health": 20.0, "max_health": 100.0})],
}
PACK = {"hoglin": ("rp06-1422", "rp06-1423"), "zoglin": ("rp06-1422", "rp06-1423")}
TEX_KEY = {"fox": "red", "cat": "white", "ocelot": None, "goat": "default", "cod": "default", "iron_golem": "default", "hoglin": "default", "zoglin": "default"}


def entity(pack, stem):
    return ML._parse_json((ROOT / "_build" / pack / f"entity/{stem}.entity.json").read_text(encoding="utf-8"))["minecraft:client_entity"]["description"]


def tex_path(pack, desc, key):
    t = desc["textures"]; rel = t.get(key) if key else list(t.values())[0]
    rel = rel or list(t.values())[0]
    return ROOT / "_build" / pack / f"{rel}.png"


def tile(img, title, sub, colour):
    img = img.convert("RGB"); d = ImageDraw.Draw(img); d.rectangle([0, 0, W, 34], fill=colour)
    d.text((6, 2), title, fill=(255, 255, 255), font=FB); d.text((6, 19), sub, fill=(230, 235, 245), font=FR)
    return img


def sheet(m, view="front-east"):
    stem = m; old_pack, new_pack = PACK.get(m, ("rp07-1428", "rp07-1429"))
    eo, en = entity(old_pack, stem), entity(new_pack, stem)
    _, go = R.geo_file(ROOT / "_build" / old_pack, eo["geometry"]["default"]); _, gn = R.geo_file(ROOT / "_build" / new_pack, en["geometry"]["default"])
    anim = R.jl(ROOT / "_build" / new_pack / f"animations/pw_{m}_jem.animation.json")["animations"][f"animation.pw_{m}.jem"]
    init, pre = en["scripts"]["initialize"], en["scripts"]["pre_animation"]
    r16b.bake(m)
    tw_o, th_o = go["description"]["texture_width"], go["description"]["texture_height"]
    tw_n, th_n = gn["description"]["texture_width"], gn["description"]["texture_height"]
    faces_old = truth_posed_faces(go["bones"], tw_o, th_o, bone_affines(go["bones"]))
    posed = []
    for name, c in STATES[m]:
        c = {**r16b.rest_case(m), **c}
        chans = r16b.eval_channels(m, init, pre, anim, c)
        posed.append((name, truth_posed_faces(gn["bones"], tw_n, th_n, WC.affines(gn["bones"], chans))))
    allf = faces_old + [f for _, fs in posed for f in fs]
    e, t = camera(allf, view)
    floor = min(0.0, min(q[1] for f in allf for q in f.pts))
    key = TEX_KEY.get(m)
    cells = [tile(render_entity(faces_old, tex_path(old_pack, eo, key), e, t, W, H, fov=FOV, floor_y=floor),
                  f"SHIPPED ({old_pack.replace('rp0', 'RP-0').replace('-14', ' 1.4.')}) - rest", "the model you have now (its own animations not shown)", (110, 110, 110))]
    for name, fs in posed:
        tx = tex_path(new_pack, en, "red_sleep" if (m == "fox" and "sleep" in name) else key)
        cells.append(tile(render_entity(fs, tx, e, t, W, H, fov=FOV, floor_y=floor), f"NEW - {name}", "Patrix model, FreshLX's own motion", (30, 90, 160)))
    cols = 4 if len(cells) > 4 else len(cells); rows = (len(cells) + cols - 1) // cols
    out = Image.new("RGB", (cols * (W + 4) - 4, rows * (H + 4) - 4 + 30), (255, 255, 255))
    d = ImageDraw.Draw(out); d.text((6, 6), f"{m.upper().replace('_', ' ')} — camera: front-east, same distance in every tile", fill=(20, 20, 20), font=FB)
    for i, cimg in enumerate(cells): out.paste(cimg, ((i % cols) * (W + 4), 30 + (i // cols) * (H + 4)))
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / f"R16B-PREVIEW-{m}.png"; out.save(p)
    return p


if __name__ == "__main__":
    for m in sys.argv[1:] or list(STATES):
        print(sheet(m))
