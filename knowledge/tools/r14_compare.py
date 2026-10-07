#!/usr/bin/env python3
"""r14_compare.py — R14 witness follow-up sheets (D-C306), for his eyes next to his own shots:
  POLAR:  our shipped RP-07 polar bear (April geometry) vs the Patrix JEM baked by Converter B (same texture), side + front
  ALLAY:  the allay at the dance tick where the shoulder gap peaks: shipped (arms = root bones) vs Java tree (arms under body)
Static renders rule nothing IN (P1); they show the mechanism the numbers describe."""
import sys, copy
sys.path.insert(0, "/home/claude/tools")
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import convb_round as R
import molang_eval as ME
import posed_preview as PP
import fa_preview as FP
from equine_compare import bone_affines
from bb_truth import truth_posed_faces
from entity_tex_render import render_entity
from convb_preview3 import camera, FOV

OUT = Path("/home/claude/_docs/r14"); OUT.mkdir(parents=True, exist_ok=True)
F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
W, H = 420, 330


def shot(bones, tw, th, tex, view, label, cam=None):
    f = truth_posed_faces(bones, tw, th, bone_affines(bones))
    e, t = cam if cam else camera(f, view)
    fl = min(0.0, min(q[1] for x in f for q in x.pts))
    im = render_entity(f, tex, e, t, W, H, fov=FOV, floor_y=fl).convert("RGB")
    d = ImageDraw.Draw(im); d.rectangle([0, 0, W, 20], fill=(30, 40, 60)); d.text((5, 3), label, fill=(255, 255, 255), font=F)
    return im, (e, t)


def polar():
    D = Path("/home/claude/_build/rp07-1426")
    _, g = R.geo_file(D, "geometry.pw_polar_bear"); ours = g["bones"]
    tex = D / "textures/entity/bear/polarbear.png"
    bake = FP.bake_any("polar_bear", "26.2"); pbones = bake[0]
    rows = []
    for view in ("east", "front"):
        # one camera for both so the sizes compare 1:1
        f_all = truth_posed_faces(ours, 128, 64, bone_affines(ours)) + truth_posed_faces(pbones, 128, 64, bone_affines(pbones))
        cam = camera(f_all, view)
        a, _ = shot(ours, 128, 64, tex, view, f"SHIPPED RP-07 polar bear - {view}", cam)
        b, _ = shot(pbones, 128, 64, tex, view, f"PATRIX JEM (Converter B bake) - {view}", cam)
        rows.append((a, b))
    sheet = Image.new("RGB", (2 * W + 6, len(rows) * (H + 6)), (255, 255, 255))
    for i, (a, b) in enumerate(rows):
        sheet.paste(a, (0, i * (H + 6))); sheet.paste(b, (W + 6, i * (H + 6)))
    sheet.save(OUT / "R14-POLAR-BEAR-SHIPPED-vs-PATRIX.png"); print(OUT / "R14-POLAR-BEAR-SHIPPED-vs-PATRIX.png")


def allay(tick=138):
    D = Path("/home/claude/_build/rp07-1426")
    ent = R.jl(D / "entity/allay.entity.json")["minecraft:client_entity"]["description"]
    env = {"q.delta_time": 0.05, "q.is_on_ground": 0.0, "q.is_alive": 1.0, "q.modified_move_speed": 0.0, "q.target_x_rotation": 0.0,
           "q.target_y_rotation": 0.0, "q.hurt_time": 0.0, "q.death_ticks": 0.0, "q.modified_distance_moved": 0.0,
           "q.position(1)": 173.0, "q.is_riding": 0.0, "q.is_dancing": 1.0, "q.life_time": 0.0}
    for s in ent["scripts"].get("initialize", []): ME.run(s, env)
    for n in range(tick + 1):
        env["q.life_time"] = n * 0.05
        for s in ent["scripts"]["pre_animation"]:
            if "'" not in s: ME.run(s, env)
    lib = {}
    for f in (D / "animations").glob("*.json"): lib.update(R.jl(f).get("animations", {}))
    a = lib[ent["animations"]["pw_jem"]]
    _, g = R.geo_file(D, "geometry.pw_allay")
    tex = D / "textures/entity/allay/allay.png"
    if not tex.exists(): tex = next((D / "textures/entity").rglob("allay*.png"))
    variants = []
    for nest in (False, True):
        bones = copy.deepcopy(g["bones"])
        if nest:
            for b in bones:
                if b["name"] in ("right_arm", "left_arm"): b["parent"] = "body"
        variants.append(PP.posed_bones(bones, a["bones"], dict(env)))
    tw, th = g["description"]["texture_width"], g["description"]["texture_height"]
    rows = []
    for view in ("front", "east"):
        f_all = truth_posed_faces(variants[0], tw, th, bone_affines(variants[0])) + truth_posed_faces(variants[1], tw, th, bone_affines(variants[1]))
        cam = camera(f_all, view)
        x, _ = shot(variants[0], tw, th, tex, view, f"SHIPPED allay, dancing t{tick} - {view}", cam)
        y, _ = shot(variants[1], tw, th, tex, view, f"JAVA TREE (arms under body) t{tick} - {view}", cam)
        rows.append((x, y))
    sheet = Image.new("RGB", (2 * W + 6, len(rows) * (H + 6)), (255, 255, 255))
    for i, (x, y) in enumerate(rows):
        sheet.paste(x, (0, i * (H + 6))); sheet.paste(y, (W + 6, i * (H + 6)))
    sheet.save(OUT / "R14-ALLAY-DANCE-SHIPPED-vs-JAVA-TREE.png"); print(OUT / "R14-ALLAY-DANCE-SHIPPED-vs-JAVA-TREE.png", "tex", tex)


if __name__ == "__main__":
    polar(); allay()
