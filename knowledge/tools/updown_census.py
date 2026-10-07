#!/usr/bin/env python3
"""updown_census.py — D-C278: which shipped geometries carry JEM-literal up/down face UVs (turned 180° in Bedrock)?
For every geometry an entity file uses, every per-face up/down rect is matched against every Patrix JEM's uvUp/uvDown:
  LITERAL  uv = [u1, v1], size = [u2-u1, v2-v1]      (jem_convert before D-C278 -> wrong in game)
  BEDROCK  uv = [u2, v2], size = [u1-u2, v1-v2]      (Blockbench-converted -> right)
The verdict per geometry is the majority; ties/none are reported. Output: _docs/convb/updown_census.json"""
import json, re, sys
from pathlib import Path
ROOT = Path("/home/claude"); CEM = ROOT / "_intake/patrix-mobs/assets/minecraft/optifine/cem"
PACKS = {"RP-07": ROOT / "_build/rp07-1419", "RP-06": ROOT / "_build/rp06-1412"}


def lj(p):
    return json.loads(re.sub(r"^\s*//.*$", "", Path(p).read_text(encoding="utf-8-sig"), flags=re.M))


def jem_rects():
    lit, bed = {}, {}
    for p in CEM.glob("*.jem"):
        try: j = lj(p)
        except Exception: continue
        def walk(m):
            for b in m.get("boxes", []) or []:
                for k in ("uvUp", "uvDown"):
                    v = b.get(k)
                    if v:
                        u1, v1, u2, v2 = [float(x) for x in v]
                        lit.setdefault((round(u1, 3), round(v1, 3), round(u2 - u1, 3), round(v2 - v1, 3)), set()).add(p.stem)
                        bed.setdefault((round(u2, 3), round(v2, 3), round(u1 - u2, 3), round(v1 - v2, 3)), set()).add(p.stem)
            for s in m.get("submodels", []) or []: walk(s)
        for m in j.get("models", []): walk(m)
    return lit, bed


def used_geometries():
    out = {}
    for tag, rp in PACKS.items():
        for f in (rp / "entity").glob("*.json"):
            try: d = lj(f)["minecraft:client_entity"]["description"]
            except Exception: continue
            for g in (d.get("geometry") or {}).values(): out.setdefault(g, set()).add(f"{tag}:{f.name}")
    return out


def main():
    lit, bed = jem_rects(); used = used_geometries(); rows = []
    for tag, rp in PACKS.items():
        for f in sorted((rp / "models").rglob("*.json")):
            try: d = lj(f)
            except Exception: continue
            for g in d.get("minecraft:geometry", []) or []:
                ident = g["description"]["identifier"]
                if ident not in used: continue
                nl = nb = nn = 0; mobs = set()
                for b in g.get("bones", []):
                    for c in b.get("cubes", []):
                        uv = c.get("uv")
                        if not isinstance(uv, dict): continue
                        for k in ("up", "down"):
                            fc = uv.get(k)
                            if not fc or "uv_size" not in fc: continue
                            key = (round(float(fc["uv"][0]), 3), round(float(fc["uv"][1]), 3), round(float(fc["uv_size"][0]), 3), round(float(fc["uv_size"][1]), 3))
                            if key in lit: nl += 1; mobs |= lit[key]
                            elif key in bed: nb += 1
                            else: nn += 1
                if nl + nb + nn == 0: continue
                verdict = "LITERAL" if nl > nb else ("BEDROCK" if nb > nl else "UNDECIDED")
                rows.append({"pack": tag, "file": str(f.relative_to(rp)), "ident": ident, "literal": nl, "bedrock": nb, "unmatched": nn,
                             "verdict": verdict, "used_by": sorted(used[ident])})
    json.dump(rows, open(ROOT / "_docs/convb/updown_census.json", "w"), indent=1)
    for r in rows: print(f"{r['pack']} {r['ident']:42s} lit {r['literal']:3d} bed {r['bedrock']:3d} none {r['unmatched']:3d} -> {r['verdict']}")
    return rows


if __name__ == "__main__":
    main()
