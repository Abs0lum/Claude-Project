#!/usr/bin/env python3
"""build_fix_229.py — BP-02 1.3.229 + RP-13 1.0.1: the spiral-stair geometry fix only (his first-load content log,
22:46 CT 2026-10-06: "cannot find geometry.pw_spiral_..." for every spiral piece).

Derived from the shipped builds (bp02-228, rp13-100) so nothing else changes:
  RP-13: models/blocks/pw_spiral_stairs.geo.json -> every identifier lowercased, format_version 1.16.0 (the format and
         casing of all 4,618 working geometries in our packs); manifest 1.0.1.
  BP-02: the 8 blocks/pw_spiral_stairs_*.json -> geometry identifiers lowercased; manifest 1.3.229; PW_BUILD "1.3.229".
The generator (tools/spiral_pack.py) carries the same change for every later build.
"""
import json
import re
import shutil
from pathlib import Path

B = Path("/home/claude/_build")
BP_SRC, BP_DST = B / "bp02-228", B / "bp02-229"
RP_SRC, RP_DST = B / "rp13-100", B / "rp13-101"
BP_NOTE = ("v1.3.229 (2026-10-06) the spiral stairs' geometry ids lowercased — his first-load log showed 'cannot find geometry' "
           "for every spiral piece; needs RP-13 1.0.1. Includes all of 1.3.228. ")
RP_NOTE = ("v1.0.1 (2026-10-06) spiral stair geometry ids lowercased + geometry format 1.16.0 (the client did not register "
           "the 1.0.0 ones); pairs with BP-02 1.3.229. Includes all of 1.0.0. ")


def fresh_copy(src, dst):
    """Copy a build dir to a new version dir (refusing to overwrite an existing one: versions are never reused)."""
    if dst.exists():
        raise SystemExit(f"{dst} exists — versions are never reused")
    shutil.copytree(src, dst)


def bump_manifest(path, version, name_from, name_to, note):
    """Set header + module versions, rename, prepend the note to the description."""
    m = json.loads(path.read_text(encoding="utf-8-sig"))
    m["header"]["version"] = version
    m["header"]["name"] = m["header"]["name"].replace(name_from, name_to)
    m["header"]["description"] = note + m["header"].get("description", "")
    for mod in m.get("modules", []):
        mod["version"] = version
    path.write_text(json.dumps(m, indent=1))


def lower_geo_ids(text):
    """Lowercase every geometry.* identifier string in a JSON text; returns (text, count)."""
    n = 0

    def repl(mo):
        nonlocal n
        n += 1
        return mo.group(0).lower()
    return re.sub(r'"geometry\.pw_spiral_[^"]+"', repl, text), n


def main():
    fresh_copy(RP_SRC, RP_DST)
    geo = RP_DST / "models/blocks/pw_spiral_stairs.geo.json"
    g = json.loads(geo.read_text())
    for x in g["minecraft:geometry"]:
        x["description"]["identifier"] = x["description"]["identifier"].lower()
    g["format_version"] = "1.16.0"
    geo.write_text(json.dumps(g))
    bump_manifest(RP_DST / "manifest.json", [1, 0, 1], "v1.0.0", "v1.0.1", RP_NOTE)
    print(f"RP-13 1.0.1: {len(g['minecraft:geometry'])} geometries lowercased, format 1.16.0")

    fresh_copy(BP_SRC, BP_DST)
    total = 0
    for f in sorted((BP_DST / "blocks").glob("pw_spiral_stairs_*.json")):
        text, n = lower_geo_ids(f.read_text())
        f.write_text(text)
        total += n
    main_js = BP_DST / "scripts/main.js"
    s = main_js.read_text()
    if s.count('const PW_BUILD = "1.3.228";') != 1:
        raise SystemExit("PW_BUILD line not found")
    main_js.write_text(s.replace('const PW_BUILD = "1.3.228";', 'const PW_BUILD = "1.3.229";'))
    bump_manifest(BP_DST / "manifest.json", [1, 3, 229], "v1.3.228", "v1.3.229", BP_NOTE)
    print(f"BP-02 1.3.229: {total} geometry references lowercased in the spiral blocks; PW_BUILD 1.3.229")


if __name__ == "__main__":
    main()
