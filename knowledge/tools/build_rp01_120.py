#!/usr/bin/env python3
"""build_rp01_120.py — RP-01 1.3.120 from the frozen 1.3.119 (never rebuilt): TREES RE-PROPORTIONED (D-C525).
  * trunk models a little thicker (his TS1 c, "mostly a"): pw_oak_mature_log 12 -> 14 cubes across (0.75 -> 0.875 m),
    pw_oak_old_log 13 -> 15 (0.81 -> 0.94 m), every box scaled in x / z about the cell axis (oak + jungle use them)
  * spruce keeps its trunk: pw_spruce_mature_log / pw_spruce_old_log = copies of the OLD oak models (BP-02 1.3.218 points
    the spruce blocks at them)
  * the 544 falling-copy geometries regenerated from BP-02 1.3.218's re-sampled templates (tools/ft_tpl_gen.py)
Usage: build_rp01_120.py [--planes=N]"""
import copy
import json
import shutil
import subprocess
import sys
from pathlib import Path

B = Path("/home/claude/_build")
SRC, DST, BP = B / "rp01-119", B / "rp01-120", B / "bp02-218"
THICKEN = {"pw_oak_mature_log": 15 / 14, "pw_oak_old_log": 16 / 15}   # measured WITH the bark panels (D-C525 correction)


def scale_xz(geo, k):
    for b in geo["bones"]:
        if "pivot" in b:
            b["pivot"] = [round(b["pivot"][0] * k, 4), b["pivot"][1], round(b["pivot"][2] * k, 4)]
        for c in b.get("cubes", []):
            c["origin"] = [round(c["origin"][0] * k, 4), c["origin"][1], round(c["origin"][2] * k, 4)]
            c["size"] = [round(c["size"][0] * k, 4), c["size"][1], round(c["size"][2] * k, 4)]
            if "pivot" in c:
                c["pivot"] = [round(c["pivot"][0] * k, 4), c["pivot"][1], round(c["pivot"][2] * k, 4)]


def main():
    if DST.exists():
        raise SystemExit(f"never rebuild {DST}")
    planes = next((a for a in sys.argv if a.startswith("--planes=")), "--planes=1")
    shutil.copytree(SRC, DST)
    for stem, k in THICKEN.items():
        p = DST / f"models/blocks/{stem}.geo.json"
        doc = json.loads(p.read_text())
        g = next(g for g in doc["minecraft:geometry"] if g["description"]["identifier"] == f"geometry.{stem}")
        fork = copy.deepcopy(doc)
        sp = stem.replace("pw_oak_", "pw_spruce_")
        for fg in fork["minecraft:geometry"]:
            fg["description"]["identifier"] = fg["description"]["identifier"].replace(stem, sp)
        (DST / f"models/blocks/{sp}.geo.json").write_text(json.dumps(fork, indent=1))
        scale_xz(g, k)
        ext = max(max(abs(c["origin"][0]), abs(c["origin"][0] + c["size"][0]), abs(c["origin"][2]), abs(c["origin"][2] + c["size"][2]))
                  for b in g["bones"] for c in b.get("cubes", []))
        if ext > 8 + 1e-6:
            raise SystemExit(f"{stem}: thickened model leaves the cell ({ext})")
        p.write_text(json.dumps(doc, indent=1))
        print(f"{stem}: x/z x{k:.3f} (fork {sp} keeps the old width)")
    r = subprocess.run([sys.executable, "/home/claude/tools/ft_tpl_gen.py", str(DST), str(BP), planes], capture_output=True, text=True)
    print(r.stdout[-2500:], r.stderr[-1500:])
    if r.returncode != 0:
        raise SystemExit("generator failed")
    idx_names = [e["name"] for e in json.loads(Path("/home/claude/_docs/fell/ft_tpl_index.json").read_text())]
    ent = json.loads((DST / "entity/falling_tree.json").read_text())["minecraft:client_entity"]["description"]["geometry"]
    for i, n in enumerate(idx_names):
        if ent.get(f"tpl_{i}") != f"geometry.ft_tpl.{n}":
            raise SystemExit(f"index drift at {i}: {n}")
    mp = DST / "manifest.json"
    m = json.loads(mp.read_text())
    m["header"]["version"] = [1, 3, 120]
    for mod in m["modules"]:
        mod["version"] = [1, 3, 120]
    m["header"]["name"] = "AbsolutRealism Tectonic RP v1.3.120"
    desc = m["header"]["description"]
    if not desc.startswith("v1.3.119 (2026-10-03) "):
        raise SystemExit("description prefix")
    m["header"]["description"] = ("v1.3.120 (2026-10-03) TREES re-proportioned: oak / jungle trunks a little thicker (spruce keeps its "
                                  "trunk), falling copies rebuilt from the new templates with the standing trunk's width (needs BP-02 1.3.218). Includes all of " + desc)[:1000]
    mp.write_text(json.dumps(m, indent=1))
    print(f"DONE {DST}")


if __name__ == "__main__":
    main()
