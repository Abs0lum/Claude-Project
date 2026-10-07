#!/usr/bin/env python3
"""civ_roster_sheet.py — true-geometry review sheet of the minimum-village roster (civ_render, D-C487 law):
each building from the street side (south-west, above) and from the back (north-east, above), plus a cut at the
ground floor seen from above (furniture + station layout). Output outputs/CIVITAS-ROSTER-v1.png."""
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
MAN = Path("/home/claude/_staging/civ/manifests")
ORDER = ["mvv_cottage_s_a_r1", "mvv_cottage_m_a_r1", "mvv_cottage_l_a_r1", "mvv_bakery_a_r1", "mvv_butcher_a_r1",
         "mvv_smithy_a_r1", "mvv_inn_a_r1", "mvv_town_hall_a_r1", "mvv_farm_wheat_a_r1", "mvv_farm_cattle_a_r1",
         "mvv_lumberyard_a_r1", "mvv_quarry_a_r1", "mvv_well_a_r1"]
TW, TH = 420, 330


def views(stem):
    man = json.loads((MAN / f"{stem}.json").read_text())
    X, H, Z = man["size"]
    d = man["datum_y"]
    items = CR.scene(man, min_feet=-1)
    cx, cz = X / 2 * 16, Z / 2 * 16
    span = max(X, Z)
    top = (H - d) * 16
    front = Image.fromarray(CR.render(items, (cx - span * 16 * 1.1, top * 0.9 + 6 * 16, cz + span * 16 * 1.0 + 6 * 16),
                                      (cx, d * 16 + 3 * 16, cz), W=TW, H=TH, fov=50))
    back = Image.fromarray(CR.render(items, (cx + span * 16 * 1.1 + 4 * 16, top * 0.9 + 6 * 16, cz - span * 16 * 1.0 - 4 * 16),
                                     (cx, d * 16 + 3 * 16, cz), W=TW, H=TH, fov=50))
    cut = CR.scene(man, min_feet=-1, cut_feet=1)
    plan = Image.fromarray(CR.render(cut, (cx + 0.01, d * 16 + span * 16 * 1.6 + 40, cz + 0.6 * 16), (cx, d * 16, cz), W=TW, H=TH, fov=45))
    return front, back, plan, man


def main():
    rows = []
    for stem in ORDER:
        try:
            rows.append((stem, views(stem)))
        except Exception as e:  # noqa: BLE001
            print("FAIL", stem, e)
    sheet = Image.new("RGB", (3 * (TW + 8) + 10, 20 + len(rows) * (TH + 30)), (22, 22, 26))
    dr = ImageDraw.Draw(sheet)
    for i, (stem, (f, b, p, man)) in enumerate(rows):
        y = 20 + i * (TH + 30)
        st = [e for e in man["entities"] if e.get("fam") == "station"]
        zn = sorted({e["kind"] for e in man["entities"] if e.get("fam") == "zone"})
        dr.text((10, y + 4), f"{stem}  {man['size'][0]}x{man['size'][2]}  stations {len(st)}  zones {', '.join(zn)}   (street view · back view · ground-floor cut from above, street at the left)", fill=(255, 210, 120))
        for k, im in enumerate((f, b, p)):
            sheet.paste(im, (10 + k * (TW + 8), y + 22))
    sheet.save("/mnt/user-data/outputs/CIVITAS-ROSTER-v1.png")
    print(sheet.size)


if __name__ == "__main__":
    main()
