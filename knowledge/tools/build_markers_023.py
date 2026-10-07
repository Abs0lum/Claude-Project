#!/usr/bin/env python3
"""build_markers_023.py — PW Civitas Markers BP 0.2.3 from the frozen 0.2.1 BP (never rebuilt): MARKERS HIDDEN BY DEFAULT
(D-C527, his 17:00 + screenshots S162751 / S163820 / S164831: zone, station, port and datum markers stood visible all
over the village). A world that never ran `/scriptevent civ:markers show` now keeps them hidden (and without a hit box);
`show` / `hide` work as before. 0.2.2 is the RP's number, so the BP skips to 0.2.3."""
import json
import shutil
from pathlib import Path

B = Path("/home/claude/_build")
SRC, DST = B / "markers-0.2.1/BP", B / "markers-0.2.3-bp"


def main():
    if DST.exists():
        raise SystemExit(f"never rebuild {DST}")
    shutil.copytree(SRC, DST)
    p = DST / "scripts/pw_markers.js"
    t = p.read_text()
    old = 'export function markersVisible() { try { return world.getDynamicProperty("civ:markers_vis") !== false; } catch (e) { return true; } }'
    new = ('// v0.2.3 (D-C527): hidden unless the world was told `show` (before: shown unless told `hide`)\n'
           'export function markersVisible() { try { return world.getDynamicProperty("civ:markers_vis") === true; } catch (e) { return false; } }')
    if t.count(old) != 1:
        raise SystemExit("markersVisible line not found")
    t = t.replace(old, new).replace("[CIVITAS-MARKERS] v0.2.1 markers", "[CIVITAS-MARKERS] v0.2.3 markers")
    p.write_text(t)
    m = json.loads((DST / "manifest.json").read_text())
    m["header"]["version"] = [0, 2, 3]
    for mod in m["modules"]:
        mod["version"] = [0, 2, 3]
    m["header"]["name"] = "PW Civitas Markers BP v0.2.3"
    m["header"]["description"] = ("v0.2.3 (2026-10-03) markers HIDDEN by default (/scriptevent civ:markers show to edit). Includes all of "
                                  + m["header"]["description"])[:1000]
    (DST / "manifest.json").write_text(json.dumps(m, indent=1))
    print("DONE", DST)


if __name__ == "__main__":
    main()
