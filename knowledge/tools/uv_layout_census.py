#!/usr/bin/env python3
"""uv_layout_census.py — the warden class of defect across his whole install set (R12 z08, D-C295).
DEFECT CLASS L-UV-LAYOUT: a texture painted for one UV layout (a Patrix JEM's per-face UVs) drawn on a geometry with a
different layout (Mojang's box UVs). Every part samples the wrong region; regions that are transparent in the new atlas
become holes (the warden's fragmented arm, L-shaped tendrils, a face on the chest).

For every vanilla client entity (bedrock-samples 1.26.50 resource_pack/entity):
  1. effective entity file = the highest pack in his stack that defines the identifier, else Mojang's
  2. for each geometry it names: OURS (defined in one of our packs) or VANILLA (only Mojang defines it)
  3. for each texture it names: effective file by whole-stack lookup (L: WHOLE-STACK texture lookup, R2 b09), else Mojang's
  4. VANILLA geometry + OUR texture -> layout check against Mojang's own texture for that path:
       ALPHA-IoU  = IoU of the opaque masks (Mojang texture upscaled to ours)       — same layout ~ 0.8-1.0
       HOLES      = share of the geometry's face area that is opaque in Mojang's texture but transparent in ours
     verdict MISMATCH when IoU < 0.6 or HOLES > 0.10
Output: _docs/sizes/UV-LAYOUT-CENSUS.md + .json"""
import json, re, sys
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, "/home/claude/tools")
import molang_lint as ML

ROOT = Path("/home/claude")
VAN = ROOT / "_intake/bedrock-samples/resource_pack"
# his install set, TOP of the stack first (handoff §1a / status line, 20:1x 09-29)
STACK = [("RP-07 1.4.25", "rp07-1425"), ("RP-06 1.4.19", "rp06-1419"), ("RP-08 1.4.8", "rp08-148"),
         ("RP-04 1.3.142", "rp04-142"), ("RP-10 1.3.42", "rp10-142"), ("RP-05 1.3.51", "rp05-51"),
         ("RP-03 1.3.60", "rp03-60"), ("RP-02 2.0.5", "rp02-205"), ("RP-01 1.3.104", "rp01-104")]
OUT_MD = ROOT / "_docs/sizes/UV-LAYOUT-CENSUS.md"; OUT_JS = ROOT / "_docs/sizes/UV-LAYOUT-CENSUS.json"


def jload(p):
    try: return ML._parse_json(p.read_text(encoding="utf-8-sig"))
    except Exception: return None


def entities(rp):
    out = {}
    for p in (rp / "entity").glob("*.json") if (rp / "entity").exists() else []:
        d = jload(p)
        if not d: continue
        ce = d.get("minecraft:client_entity") or {}
        desc = ce.get("description") or {}
        if desc.get("identifier"): out.setdefault(desc["identifier"], (p, desc))
    return out


def geometries(rp):
    out = {}
    base = rp / "models/entity"
    for p in base.rglob("*.json") if base.exists() else []:
        d = jload(p)
        if not d: continue
        for g in d.get("minecraft:geometry", []) or []:
            ident = (g.get("description") or {}).get("identifier")
            if ident: out.setdefault(ident, (p, g))
        for k, v in d.items():                      # legacy 1.8 format: "geometry.x": {...} or "geometry.x:parent"
            if k.startswith("geometry.") and isinstance(v, dict):
                out.setdefault(k.split(":")[0], (p, v))
    return out


def find_tex(rp, path):
    for ext in (".png", ".tga"):
        p = rp / (path + ext)
        if p.exists(): return p
    return None


def cube_faces(g):
    """(rect in texture units u0,v0,u1,v1) for every cube face of a Bedrock geometry (box UV or per-face)."""
    tw = (g.get("description") or {}).get("texture_width") or g.get("texturewidth") or 64
    th = (g.get("description") or {}).get("texture_height") or g.get("textureheight") or 64
    rects = []
    for b in g.get("bones", []) or []:
        for c in b.get("cubes", []) or []:
            s = c.get("size", [0, 0, 0]); uv = c.get("uv", [0, 0])
            if isinstance(uv, dict):
                for f in uv.values():
                    u0, v0 = f.get("uv", [0, 0]); us, vs = f.get("uv_size", [0, 0])
                    rects.append((min(u0, u0 + us), min(v0, v0 + vs), max(u0, u0 + us), max(v0, v0 + vs)))
            else:
                u, v = uv; sx, sy, sz = [abs(x) for x in s]
                for r in ((u + sz, v, u + sz + sx, v + sz), (u + sz + sx, v, u + sz + 2 * sx, v + sz),     # up, down
                          (u, v + sz, u + sz, v + sz + sy), (u + sz, v + sz, u + sz + sx, v + sz + sy),     # east, north
                          (u + sz + sx, v + sz, u + 2 * sz + sx, v + sz + sy), (u + 2 * sz + sx, v + sz, u + 2 * sz + 2 * sx, v + sz + sy)):
                    if r[2] > r[0] and r[3] > r[1]: rects.append(r)
    return rects, tw, th


def alpha(p, size=None):
    im = Image.open(p).convert("RGBA")
    if size and im.size != size: im = im.resize(size, Image.NEAREST)
    return np.asarray(im)[..., 3] > 16


def check(geo, ours, van):
    rects, tw, th = cube_faces(geo)
    a_o = alpha(ours); H, W = a_o.shape
    a_v = alpha(van, (W, H))
    inter = (a_o & a_v).sum(); union = (a_o | a_v).sum()
    iou = float(inter / union) if union else 1.0
    need = hole = 0
    for u0, v0, u1, v1 in rects:
        x0, x1 = int(u0 / tw * W), max(int(u0 / tw * W) + 1, int(u1 / tw * W))
        y0, y1 = int(v0 / th * H), max(int(v0 / th * H) + 1, int(v1 / th * H))
        mv, mo = a_v[y0:y1, x0:x1], a_o[y0:y1, x0:x1]
        need += mv.sum(); hole += (mv & ~mo).sum()
    holes = float(hole / need) if need else 0.0
    return iou, holes, (W, H)


def main():
    packs = [(tag, ROOT / "_build" / d) for tag, d in STACK]
    missing = [t for t, p in packs if not p.exists()]
    ents = [(t, entities(p)) for t, p in packs]
    geos = [(t, geometries(p)) for t, p in packs]
    vents = entities(VAN); vgeos = geometries(VAN)
    rows = []
    for ident, (vp, vdesc) in sorted(vents.items()):
        owner, desc = "Mojang", vdesc
        for t, e in ents:
            if ident in e: owner, desc = t, e[ident][1]; break
        gnames = [g for g in (desc.get("geometry") or {}).values() if isinstance(g, str)]
        tex = {k: v for k, v in (desc.get("textures") or {}).items() if isinstance(v, str)}
        for gk, gname in (desc.get("geometry") or {}).items():
            if not isinstance(gname, str): continue
            gowner = next((t for t, g in geos if gname in g), None)
            if gowner or gname not in vgeos: continue          # converted / ours, or not a Mojang geometry
            vgeo = vgeos[gname][1]
            for tk, tpath in tex.items():
                # a render controller pairs a baby geometry with the baby texture (sniffer.v2): no cross pairs
                if ("baby" in gk) != ("baby" in tk) and "baby" in (desc.get("textures") or {}) and "baby" in (desc.get("geometry") or {}): continue
                ours = next(((t, f) for t, p in packs if (f := find_tex(p, tpath))), None)
                vt = find_tex(VAN, tpath)
                if not ours or not vt: continue
                try: iou, holes, size = check(vgeo, ours[1], vt)
                except Exception as e: rows.append(dict(entity=ident, geometry=gname, texture=tpath, error=str(e))); continue
                verdict = "MISMATCH" if (iou < 0.6 or holes > 0.10) else "ok"
                rows.append(dict(entity=ident, entity_owner=owner, geometry=gname, texture_key=tk, texture=tpath,
                                 texture_pack=ours[0], size=f"{size[0]}x{size[1]}", alpha_iou=round(iou, 3),
                                 holes=round(holes, 3), verdict=verdict))
    OUT_JS.write_text(json.dumps(rows, indent=1))
    bad = [r for r in rows if r.get("verdict") == "MISMATCH"]
    L = ["# UV-LAYOUT CENSUS (R12 z08 warden class) — " + ("missing builds: " + ", ".join(missing) if missing else "whole install set read"),
         "", f"{len(rows)} (vanilla geometry × our texture) pairings checked; **{len(bad)} MISMATCH**.", "",
         "| verdict | entity (owner) | geometry | texture key → path (pack) | size | alpha IoU | holes |", "|---|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: (r.get("verdict") != "MISMATCH", r.get("entity"))):
        if "error" in r: L.append(f"| ERROR | {r['entity']} | {r['geometry']} | {r['texture']} | | | {r['error']} |"); continue
        L.append(f"| {r['verdict']} | {r['entity']} ({r['entity_owner']}) | {r['geometry']} | {r['texture_key']} → {r['texture']} ({r['texture_pack']}) | {r['size']} | {r['alpha_iou']} | {r['holes']} |")
    OUT_MD.write_text("\n".join(L) + "\n")
    print(OUT_MD, len(rows), "pairings,", len(bad), "MISMATCH")
    for r in bad: print("  MISMATCH", r["entity"], r["texture"], r["texture_pack"], "IoU", r["alpha_iou"], "holes", r["holes"])


if __name__ == "__main__":
    main()
