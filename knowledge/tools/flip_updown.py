#!/usr/bin/env python3
"""flip_updown.py — preview helper (D-C278): rewrite a geometry's per-face up/down UVs from the JEM-copied form
(uv = [u1, v1], size = [u2-u1, v2-v1]) to the Bedrock form (uv = [u2, v2], size = [u1-u2, v1-v2]) — Blockbench's
bedrock codec rule. Used only to render "after" previews of shipped geometries; the real fix is jem_convert.face_uv.
usage: flip_updown.py <in.geo.json> <out.geo.json> [identifier ...]"""
import json, sys, re
from pathlib import Path


def flip_geo(doc, idents=None):
    n = 0
    for g in doc.get("minecraft:geometry", []):
        if idents and g["description"]["identifier"] not in idents: continue
        for b in g.get("bones", []):
            for c in b.get("cubes", []):
                uv = c.get("uv")
                if not isinstance(uv, dict): continue
                for k in ("up", "down"):
                    f = uv.get(k)
                    if not f or "uv_size" not in f: continue
                    (a, bb), (w, h) = f["uv"], f["uv_size"]
                    f["uv"] = [a + w, bb + h]; f["uv_size"] = [-w, -h]; n += 1
    return n


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    doc = json.loads(re.sub(r"^\s*//.*$", "", Path(src).read_text(encoding="utf-8-sig"), flags=re.M))
    n = flip_geo(doc, set(sys.argv[3:]) or None)
    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    Path(dst).write_text(json.dumps(doc), encoding="utf-8"); print(f"flipped {n} up/down faces -> {dst}")
