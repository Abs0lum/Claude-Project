#!/usr/bin/env python3
"""ramp8_preview.py — program 228: true-geometry views of the new 8-block ramp (staging) beside the shipped 4-block ramp,
for his look before anything enters a pack. Renders through tools/civ_render.py (our block geometry + textures)."""
import json, os, shutil, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
os.environ["PW_STACK"] = "final"
sys.path.insert(0, "/home/claude/tools")
import civ_render as CR  # noqa: E402

ST = Path("/home/claude/_staging/ramps228")
TMP = Path("/tmp/claude-0/-home-claude/c0a4a7ef-9c52-560d-ac77-bcf688f4b3d2/scratchpad/ramp8blocks")
if TMP.exists(): shutil.rmtree(TMP)
TMP.mkdir(parents=True)
for f in Path("/home/claude/_build/bp02-227/blocks").glob("pw_ramp_*.json"): shutil.copy2(f, TMP / f.name)
for f in (ST / "bp/blocks").glob("*.json"): shutil.copy2(f, TMP / f.name)
CR.BP = TMP
CR.RP_MODELS = [ST / "rp/models/blocks", Path("/home/claude/_build/rp04-158/models/blocks")]
for f in (ST / "rp/textures/blocks").glob("*.png"):
    if f.stem.endswith(("_n", "_mer")): continue
    CR._tex[f.stem] = np.asarray(Image.open(f).convert("RGBA")).astype(np.float32) / 255.0
for f in Path("/home/claude/_build/rp04-158/textures/blocks").glob("pw_*.png"):
    if f.stem.startswith(("pw_rampv4", "pw_deck14", "pw_fill14", "pw_rampcut", "pw_snowcap")) and not f.stem.endswith(("_n", "_mer")):
        CR._tex.setdefault(f.stem, np.asarray(Image.open(f).convert("RGBA")).astype(np.float32) / 255.0)

def scene(mat, snow=0):
    B = []
    for x in range(0, 14):                      # a stone floor
        for z in range(0, 7):
            B.append([x, 0, z, "minecraft:stone", {}])
    # row z=1: 8-ramp rising east (state 'east' = ascending toward +x? the ramp ascends toward +z for 'south'); use south-ascending rows
    for i in range(1, 9):
        B.append([2, 1, 1 + i - 1, f"pw:ramp_{mat}_8_e{i}", {"minecraft:cardinal_direction": "south", "pw:var": i % 8, "pw:snow": snow}])
    B.append([2, 1, 9, "minecraft:smooth_stone", {}])
    for i in range(1, 5):
        B.append([6, 1, 5 + i - 1, f"pw:ramp_{mat}_4_q{i}", {"minecraft:cardinal_direction": "south", "pw:var": i % 8, "pw:snow": snow}])
    B.append([6, 1, 9, "minecraft:smooth_stone", {}])
    return {"datum_y": 0, "blocks": B}

tiles = []
for mat in ("smooth_stone", "cobble", "stonebrick"):
    items = CR.scene(scene(mat), min_feet=0)
    eye = (12.5 * 16, 4.2 * 16, 2.0 * 16); tgt = (4 * 16, 1.2 * 16, 6 * 16)
    a = Image.fromarray(CR.render(items, eye, tgt, W=620, H=360, fov=48))
    ImageDraw.Draw(a).text((8, 6), f"{mat}: LEFT 8-block ramp (new, ~7 deg) | RIGHT 4-block ramp (shipped, 14 deg)", fill=(0, 0, 0))
    eye2 = (-3.5 * 16, 1.6 * 16, 5.5 * 16); tgt2 = (3 * 16, 1.3 * 16, 5.5 * 16)
    b = Image.fromarray(CR.render(items, eye2, tgt2, W=620, H=360, fov=55))
    ImageDraw.Draw(b).text((8, 6), f"{mat}: side view from the west (low end left)", fill=(0, 0, 0))
    tiles.append((a, b))
sheet = Image.new("RGB", (1250, 3 * 370), (20, 20, 24))
for r, (a, b) in enumerate(tiles):
    sheet.paste(a, (0, r * 370)); sheet.paste(b, (630, r * 370))
out = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/_docs/program228/RAMP8-PREVIEW-v1.png"
sheet.save(out); print(out, sheet.size)
