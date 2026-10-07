#!/usr/bin/env python3
"""roof_kit_render.py — true-geometry views of pw:roof_kit (tools/roof_kit.py) for his keep / fix / delete ruling:
one wide view from the south + a close view of each assembly from the south-east, above. Uses tools/civ_render.py
(shipped block geometry + our textures) pointed at the current builds (BP-02 1.3.206, RP-04 1.3.156, RP-01 1.3.117)."""
import json
import os
import sys
from pathlib import Path

os.environ["PW_STACK"] = "final"
sys.path.insert(0, "/home/claude/tools")
import civ_render as CR  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

CR.BP = Path("/home/claude/_build/bp02-206/blocks")
CR.RP_MODELS = [Path("/home/claude/_build/rp04-156/models/blocks"), Path("/home/claude/_build/rp01-117/models/blocks")]
NAMES = ["1 gusset fold (gusset pair + its 4 neighbours)", "2 hipped roof (hips, ridge ends, ridge)", "3 pyramid (hips + pyramidion)",
         "4 plain gable run", "5 crown ring", "6 steep gable 63°"]


def main():
    man = json.loads(Path("/home/claude/_staging/roof_kit_manifest.json").read_text())
    W, H, D = man["size"]
    items = CR.scene(man, min_feet=-1)
    xs = [a["x"] for a in man["assemblies"]]
    ws = [a["width"] for a in man["assemblies"]]
    tiles = []
    wide = Image.fromarray(CR.render(items, ((W / 2) * 16, 9 * 16, (D + 26) * 16), ((W / 2) * 16, 2 * 16, (D / 2) * 16), W=1290, H=420, fov=50))
    ImageDraw.Draw(wide).text((8, 6), "the whole kit from the south, numbered left to right", fill=(0, 0, 0))
    for i, (x, w) in enumerate(zip(xs, ws)):
        cx, cz = (x + w / 2) * 16, (D / 2) * 16
        eye = (cx + (w / 2 + 4) * 16, 6.5 * 16, cz + (w / 2 + 6) * 16)
        im = Image.fromarray(CR.render(items, eye, (cx, 2 * 16, cz), W=420, H=330, fov=55))
        ImageDraw.Draw(im).text((8, 6), NAMES[i], fill=(0, 0, 0))
        tiles.append(im)
    sheet = Image.new("RGB", (1290, 420 + 2 * 340 + 10), (20, 20, 24))
    sheet.paste(wide, (0, 0))
    for i, t in enumerate(tiles):
        sheet.paste(t, ((i % 3) * 435, 430 + (i // 3) * 340))
    sheet.save(os.environ.get("ROOF_OUT", "/mnt/user-data/outputs/ROOF-KIT.png"))
    print(sheet.size)


if __name__ == "__main__":
    main()
