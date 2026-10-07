#!/usr/bin/env python3
"""build_round_1002b.py — ROUND 1002b: 256 x 16-frame plant sway flipbooks (his 00:53 'for sure a', 16 frames).
Ownership: every one of the 17 plant keys — its terrain definition, its flipbook definition, the strip, its texture set
and its normal / MERS strips — lives in RP-05 Flora only:
  RP-05  terrain keys re-pointed to textures/blocks/sway/<key>; flipbook entries for the 17 keys replaced by the new ones;
         + 17 x (colour, _n, _mer, .texture_set.json) from _staging/sway (tools/sway_flipbooks.py)
  RP-10  the 4 seagrass_tall_* terrain keys removed (now defined in RP-05)
  RP-01  the 6 grass flipbook entries + the short_dry_grass terrain key removed (now in RP-05)
  RP-03  the kelp_top flipbook entry removed (now in RP-05)
Old strips are left where they are (no longer referenced; full cleanup is the later ownership pass).
New build dirs: rp05-55 (from rp05-54), rp10-147 (rp10-146), rp01-111 (rp01-110), rp03-64 (rp03-63)."""
import json
import re
import shutil
from pathlib import Path

ROOT = Path("/home/claude")
B = ROOT / "_build"
JOBS = {"RP-05": ("rp05-54", "rp05-55", [1, 3, 55]), "RP-10": ("rp10-146", "rp10-147", [1, 3, 47]),
        "RP-01": ("rp01-110", "rp01-111", [1, 3, 111]), "RP-03": ("rp03-63", "rp03-64", [1, 3, 64])}
DESC = {"RP-05": "Plant sway flipbooks: 16 frames at 256 for short / tall grass, short / tall dry grass, short / tall "
                 "seagrass and kelp (stem joins itself block to block), each with depth + shine strips; this pack now "
                 "owns all 17 plant texture names and their flipbooks.",
        "RP-10": "4 seagrass texture names handed to RP-05 Flora (it owns them now).",
        "RP-01": "6 grass flipbooks + 1 texture name handed to RP-05 Flora (it owns them now).",
        "RP-03": "kelp_top flipbook handed to RP-05 Flora (it owns it now)."}


def jl(p):
    return json.loads(re.sub(r"(?m)^\s*//.*$", "", p.read_text(encoding="utf-8-sig")))


def main():
    for pk, (src, dst, _) in JOBS.items():
        assert not (B / dst).exists(), f"never rebuild a build dir: {dst}"
    for pk, (src, dst, _) in JOBS.items():
        shutil.copytree(B / src, B / dst)
    defs = json.loads((ROOT / "_staging/sway/rp05/FLIPBOOKS.json").read_text())
    keys = [d["atlas_tile"] for d in defs]
    rep = {}
    # strips
    sd = ROOT / "_staging/sway/rp05/textures/blocks/sway"
    out = B / JOBS["RP-05"][1] / "textures/blocks/sway"
    out.mkdir(parents=True)
    for f in sd.iterdir():
        shutil.copy2(f, out / f.name)
    rep["RP-05 files"] = len(list(out.iterdir()))
    for pk in JOBS:
        d = B / JOBS[pk][1] / "textures"
        tp, fp = d / "terrain_texture.json", d / "flipbook_textures.json"
        if tp.exists():
            t = jl(tp)
            td = t["texture_data"]
            if pk == "RP-05":
                for k in keys:
                    td[k] = {"textures": f"textures/blocks/sway/{k}"}
            else:
                gone = [k for k in keys if td.pop(k, None) is not None]
                rep[f"{pk} terrain keys removed"] = gone
            tp.write_text(json.dumps(t, indent=1))
        if fp.exists():
            fb = jl(fp)
            kept = [e for e in fb if e.get("atlas_tile") not in keys]
            rep[f"{pk} flipbook entries removed"] = [e["atlas_tile"] for e in fb if e.get("atlas_tile") in keys]
            if pk == "RP-05":
                kept += defs
            fp.write_text(json.dumps(kept, indent=1))
    for pk, (src, dst, ver) in JOBS.items():
        mp = B / dst / "manifest.json"
        m = jl(mp)
        old = ".".join(map(str, m["header"]["version"]))
        m["header"]["version"] = ver
        for mod in m["modules"]:
            mod["version"] = ver
        vs = ".".join(map(str, ver))
        m["header"]["name"] = re.sub(r"v\d+\.\d+\.\d+", "v" + vs, m["header"]["name"])
        m["header"]["description"] = f"v{vs} (2026-10-02) {DESC[pk]} Includes all of v{old}."
        assert "pbr" in (m.get("capabilities") or [])
        mp.write_text(json.dumps(m, indent=2))
    (ROOT / "_docs/flora/BUILD-1002B.json").write_text(json.dumps(rep, indent=1))
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()
