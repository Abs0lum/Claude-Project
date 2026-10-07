#!/usr/bin/env python3
"""civ_height_render.py — a PLAN of the ground a civtest run exported ([CIVHEIGHT] rows): hypsometric tint + hillshade,
water blue, the settlement's plots (white boxes) and kit streets (grey corridors), the clock's roads (pw:clock_road parts
in the [CIVTEST] records, orange) and, when given, the offline harness's roads (test_road_site.mjs out.json: green = found,
red crosses = benches without a road). Usage: civ_height_render.py LOG OUT.png [roads.json] [scale]"""
import json
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw


def parse_height(text):
    head = None
    for m in re.finditer(r'\[CIVTEST\] (\{"step":"heighthead".*\})\s*$', text, re.M):
        head = json.loads(m.group(1))
    if not head:
        raise SystemExit("no heightmap in the log")
    W = head["x1"] - head["x0"] + 1
    H = head["z1"] - head["z0"] + 1
    G = [[None] * W for _ in range(H)]
    for m in re.finditer(r"\[CIVHEIGHT\] (-?\d+) (\S+)", text):
        z = int(m.group(1)) - head["z0"]
        x = 0
        for run in m.group(2).split(","):
            v, _, n = run.partition("*")
            n = int(n) if n else 1
            val = "w" if v == "w" else (None if v == "?" else int(v))
            for _ in range(n):
                if 0 <= z < H and x < W:
                    G[z][x] = val
                x += 1
    return head, G


def records(text):
    out = []
    for m in re.finditer(r"\[CIVTEST\] (\{.*\})\s*$", text, re.M):
        try:
            out.append(json.loads(m.group(1)))
        except json.JSONDecodeError:
            pass
    return out


def tint(y, lo, hi):
    t = 0.0 if hi == lo else (y - lo) / (hi - lo)
    stops = [(0.0, (60, 110, 50)), (0.35, (140, 170, 80)), (0.6, (200, 180, 110)), (0.8, (160, 120, 90)), (1.0, (240, 240, 240))]
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        if a <= t <= b:
            f = (t - a) / (b - a)
            return tuple(int(ca[i] + (cb[i] - ca[i]) * f) for i in range(3))
    return stops[-1][1]


def main():
    log, out = sys.argv[1], sys.argv[2]
    roads_json = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3].endswith(".json") else None
    scale = int(sys.argv[-1]) if sys.argv[-1].isdigit() else 2
    text = Path(log).read_text(errors="ignore")
    head, G = parse_height(text)
    W, H = len(G[0]), len(G)
    ys = [v for row in G for v in row if isinstance(v, int)]
    lo, hi = min(ys), max(ys)
    im = Image.new("RGB", (W * scale, H * scale), (0, 0, 0))
    px = im.load()
    for z in range(H):
        for x in range(W):
            v = G[z][x]
            if v is None:
                c = (20, 20, 24)
            elif v == "w":
                c = (40, 90, 220)
            else:
                c = tint(v, lo, hi)
                # a soft hillshade over a 3-cell baseline (light from the north-west) + explicit contour lines every 5 blocks:
                # the first renderer shaded every 1-block step and gentle slopes came out as "stripes" (0.0.14 misread)
                n = G[z - 3][x] if z > 2 and isinstance(G[z - 3][x], int) else v
                w = G[z][x - 3] if x > 2 and isinstance(G[z][x - 3], int) else v
                sh = ((v - n) + (v - w)) / 3.0
                k = max(0.7, min(1.25, 1 + 0.06 * sh))
                c = tuple(min(255, int(ch * k)) for ch in c)
                e = G[z][x + 1] if x + 1 < W and isinstance(G[z][x + 1], int) else v
                s = G[z + 1][x] if z + 1 < H and isinstance(G[z + 1][x], int) else v
                if (v // 5) != (e // 5) or (v // 5) != (s // 5):
                    c = (max(0, c[0] - 70), max(0, c[1] - 70), max(0, c[2] - 70))
            for dz in range(scale):
                for dx in range(scale):
                    px[x * scale + dx, z * scale + dz] = c
    d = ImageDraw.Draw(im)
    X = lambda wx: (wx - head["x0"]) * scale  # noqa: E731
    Z = lambda wz: (wz - head["z0"]) * scale  # noqa: E731
    recs = records(text)
    plots = next((r for r in recs if r.get("step") == "plots"), None)
    if plots:
        for row in plots["plots"]:
            _, fam, x, _, z, _, fx, fz = row[:8]
            d.rectangle([X(x), Z(z), X(x + fx), Z(z + fz)], outline=(255, 255, 255))
    evo = [r for r in recs if r.get("step") == "evo"]
    founded = next((r for r in recs if r.get("step") == "founded"), None)
    streets = (evo[-1].get("streets") if evo and isinstance(evo[-1].get("streets"), list) else (founded or {}).get("streets")) or []
    for s in streets:
        f, n = s.get("f"), s.get("n")
        if not f or not n:
            continue
        for t in range(n):
            for w in range(13):
                wx = f["ox"] + t * f["ux"] + w * f["vx"]
                wz = f["oz"] + t * f["uz"] + w * f["vz"]
                d.rectangle([X(wx), Z(wz), X(wx) + scale - 1, Z(wz) + scale - 1], fill=(90, 90, 100))
    # the clock's own roads (the probe's 'roadcells' record)
    rc = next((r for r in recs if r.get("step") == "roadcells"), None)
    for r in (rc or {}).get("roads", []):
        for c in r.get("cells", []):
            d.rectangle([X(c[0]) - 1, Z(c[1]) - 1, X(c[0]) + scale, Z(c[1]) + scale], fill=(255, 140, 0))
    if roads_json:
        R = json.loads(Path(roads_json).read_text())
        for res in R["results"]:
            p0, p1 = res["P0"], res["P1"]
            if res.get("road"):
                for c in res["road"]["cells"]:
                    d.rectangle([X(c[0]) - 1, Z(c[1]) - 1, X(c[0]) + scale, Z(c[1]) + scale], fill=(40, 230, 60))
                d.text((X(p1[0]) + 4, Z(p1[1]) + 4), f"H{res['H1']}", fill=(40, 255, 60))
            else:
                d.line([X(p1[0]) - 6, Z(p1[1]) - 6, X(p1[0]) + 6, Z(p1[1]) + 6], fill=(255, 40, 40), width=2)
                d.line([X(p1[0]) - 6, Z(p1[1]) + 6, X(p1[0]) + 6, Z(p1[1]) - 6], fill=(255, 40, 40), width=2)
                d.text((X(p1[0]) + 8, Z(p1[1]) - 4), f"H{res['H1']}", fill=(255, 80, 80))
            d.ellipse([X(p0[0]) - 4, Z(p0[1]) - 4, X(p0[0]) + 4, Z(p0[1]) + 4], outline=(255, 255, 0), width=2)
    # legend + contour labels
    d.text((4, 4), f"ground y {lo}..{hi} (green low -> white high), water blue; plots white, kit streets grey; roads orange (clock) / green (harness); x {head['x0']}..{head['x1']} z {head['z0']}..{head['z1']}", fill=(255, 255, 255))
    for gx in range(head["x0"] - head["x0"] % 50 + 50, head["x1"], 50):
        d.line([X(gx), 0, X(gx), H * scale], fill=(255, 255, 255, 40))
        d.text((X(gx) + 2, 14), str(gx), fill=(230, 230, 230))
    for gz in range(head["z0"] - head["z0"] % 50 + 50, head["z1"], 50):
        d.line([0, Z(gz), W * scale, Z(gz)], fill=(255, 255, 255, 40))
        d.text((2, Z(gz) + 2), str(gz), fill=(230, 230, 230))
    im.save(out)
    print(out, im.size, "ground", lo, hi, "plots", len(plots["plots"]) if plots else 0, "streets", len(streets))


if __name__ == "__main__":
    main()
