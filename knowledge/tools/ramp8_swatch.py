#!/usr/bin/env python3
"""ramp8_swatch.py — every ramp material's 8-block ramp side by side (staged blocks + textures), for his look."""
import os, shutil, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
os.environ["PW_STACK"] = "final"
sys.path.insert(0, "/home/claude/tools")
import civ_render as CR  # noqa: E402
import ramp_v8 as R  # noqa: E402
ST = Path("/home/claude/_staging/ramps228")
TMP = Path("/tmp/claude-0/-home-claude/c0a4a7ef-9c52-560d-ac77-bcf688f4b3d2/scratchpad/ramp8blocks")
if TMP.exists(): shutil.rmtree(TMP)
TMP.mkdir(parents=True)
for f in (ST / "bp/blocks").glob("*_8_e*.json"): shutil.copy2(f, TMP / f.name)
CR.BP = TMP
CR.RP_MODELS = [ST / "rp/models/blocks"]
for f in (ST / "rp/textures/blocks").glob("*.png"):
    if f.stem.endswith(("_n", "_mer")) or not (f.stem.startswith(("pw_deck7", "pw_fill7e", "pw_rampcut8", "pw_rampv4"))): continue
    CR._tex[f.stem] = np.asarray(Image.open(f).convert("RGBA")).astype(np.float32) / 255.0
for f in Path("/home/claude/_build/rp04-158/textures/blocks").glob("pw_rampv4_*.png"):
    if not f.stem.endswith(("_n", "_mer")): CR._tex.setdefault(f.stem, np.asarray(Image.open(f).convert("RGBA")).astype(np.float32) / 255.0)
mats = R.MATS + list(R.NEW_MATS)
tiles = []
for mat in mats:
    B = [[x, 0, z, "minecraft:stone", {}] for x in range(0, 4) for z in range(0, 11)]
    for i in range(1, 9):
        B.append([1, 1, i, f"pw:ramp_{mat}_8_e{i}", {"minecraft:cardinal_direction": "south", "pw:var": (i * 3) % 4, "pw:snow": 0}])
    B.append([1, 1, 9, "minecraft:smooth_stone", {}])
    items = CR.scene({"datum_y": 0, "blocks": B}, min_feet=0)
    im = Image.fromarray(CR.render(items, (5.2 * 16, 3.4 * 16, 1.0 * 16), (1.5 * 16, 1.1 * 16, 5.5 * 16), W=300, H=200, fov=55))
    ImageDraw.Draw(im).text((6, 4), mat, fill=(0, 0, 0))
    tiles.append(im)
cols = 5
rows = (len(tiles) + cols - 1) // cols
sheet = Image.new("RGB", (cols * 305, rows * 205), (20, 20, 24))
for i, t in enumerate(tiles):
    sheet.paste(t, ((i % cols) * 305, (i // cols) * 205))
out = "/home/claude/_docs/program228/RAMP8-MATERIALS-v1.png"
sheet.save(out); print(out, sheet.size, len(tiles))
