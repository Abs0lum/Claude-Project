#!/usr/bin/env python3
"""build_markers_024.py — the MANHOLE COVER lifts, then slides (his 19:06, D-C564; replaces the static 1-px raise of 18:30).
  * PW Civitas Markers RP 0.2.2 -> 0.2.3 (from _build/markers-0.2.2-rp/RP, never rebuilt): in pw_civitas.geo.json the hatch
    phases become  p1 = the plate LIFTED 1 px (y 15..17) still over the hole (x -8),  p2 / p3 / p4 = sliding at that height
    (x -4 / 0 / 4),  open = x 4 at y 15 (== p4, the settled beat). Closed (p0) is untouched: the full flush cube.
  * PW Civitas Markers BP 0.2.3 -> 0.2.4 (from _build/markers-0.2.3-bp): slide() dwells 4 ticks at phase 1 in both
    directions (lift ... then slide; slide back ... then drop), 2 ticks between the other phases as before. Block json,
    custom component and everything else unchanged.
Usage: build_markers_024.py   (both destination dirs must not exist)"""
import json
import shutil
from pathlib import Path

B = Path("/home/claude/_build")
RP_SRC, RP_DST = B / "markers-0.2.2-rp/RP", B / "markers-0.2.3-rp"
BP_SRC, BP_DST = B / "markers-0.2.3-bp", B / "markers-0.2.4-bp"
LIFT_Y = 15                                   # the plate's bottom when lifted: 1 px above the cell top (16) -> y 15..17
SLIDE_X = {"p1": -8, "p2": -4, "p3": 0, "p4": 4, "open": 4}


def main():
    for d in (RP_DST, BP_DST):
        if d.exists():
            raise SystemExit(f"never rebuild {d}")
    shutil.copytree(RP_SRC, RP_DST)
    shutil.copytree(BP_SRC, BP_DST)
    # RP: the hatch lids
    gp = RP_DST / "models/blocks/pw_civitas.geo.json"
    doc = json.loads(gp.read_text())
    touched = {}
    for g in doc["minecraft:geometry"]:
        gid = g["description"]["identifier"]
        if not gid.startswith("geometry.pw_hatch_") or gid.endswith("_closed"):
            continue
        phase = gid.split("geometry.pw_hatch_")[1]
        if phase not in SLIDE_X:
            raise SystemExit(f"unexpected hatch geometry {gid}")
        for b in g["bones"]:
            if b["name"] != "lid":
                continue
            for c in b["cubes"]:
                if c["size"] != [16, 2, 16] or c["origin"][1] != 14:
                    raise SystemExit(f"{gid}: unexpected lid cube {c['origin']} {c['size']}")
                c["origin"] = [SLIDE_X[phase], LIFT_Y, c["origin"][2]]
                touched[phase] = touched.get(phase, 0) + 1
    if sorted(touched) != sorted(SLIDE_X) or any(v != 1 for v in touched.values()):
        raise SystemExit(f"lid edit count {touched}")
    gp.write_text(json.dumps(doc, separators=(",", ":")))
    mp = RP_DST / "manifest.json"
    m = json.loads(mp.read_text())
    m["header"]["version"] = [0, 2, 3]
    for mod in m["modules"]:
        mod["version"] = [0, 2, 3]
    m["header"]["name"] = "PW Civitas Markers RP v0.2.3"
    m["header"]["description"] = ("v0.2.3 (2026-10-04) MANHOLE COVER lifts 1 px, then slides (closed stays flush; the open plate rests on "
                                  "the street instead of clipping it). Pairs with Markers BP 0.2.4. Includes all of " + m["header"]["description"])[:1000]
    mp.write_text(json.dumps(m, indent=1))
    # BP: the dwell after the lift / before the drop
    sp = BP_DST / "scripts/main.js"
    t = sp.read_text()
    old = "    if (ph !== to) system.runTimeout(tick, 2);"
    new = ("    // v0.2.4 (his 19:06): phase 1 is the LIFTED plate — dwell 4 ticks there (lift ... then slide; slide back ... then drop)\n"
           "    if (ph !== to) system.runTimeout(tick, ph === 1 ? 4 : 2);")
    if t.count(old) != 1:
        raise SystemExit("slide() timeout line not found")
    t = t.replace(old, new)
    sp.write_text(t)
    mp = BP_DST / "manifest.json"
    m = json.loads(mp.read_text())
    m["header"]["version"] = [0, 2, 4]
    for mod in m["modules"]:
        mod["version"] = [0, 2, 4]
    m["header"]["name"] = "PW Civitas Markers BP v0.2.4"
    m["header"]["description"] = ("v0.2.4 (2026-10-04) manhole cover: lift beat (4 ticks) before the slide and before the drop. Pairs "
                                  "with Markers RP 0.2.3. Includes all of " + m["header"]["description"])[:1000]
    mp.write_text(json.dumps(m, indent=1))
    print("DONE", RP_DST, BP_DST, touched)


if __name__ == "__main__":
    main()
