#!/usr/bin/env python3
"""verify_rp07_1410.py — gate for RP-07 v1.4.10 (trader llama bodies); packages on GATE OPEN."""
import json, sys, hashlib, zipfile
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
ROOT = Path("/home/claude"); OUT = Path("/mnt/user-data/outputs"); A, B = ROOT / "_build/rp07-149", ROOT / "_build/rp07-1410"; DATE = "2026-09-22"
def load(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))
res = []
def check(n, ok, d=""): res.append((n, bool(ok))); print(("PASS " if ok else "FAIL ") + n + ("" if ok else f"  -> {str(d)[:300]}"))
VAR = ["creamy", "white", "brown", "gray"]
bad = []
for p in [B / "entity/trader_llama.entity.json", B / "render_controllers/pw_trader_llama.render.json", B / "manifest.json", B / "textures/textures_list.json"]:
    try: load(p)
    except Exception as e: bad.append((p.name, str(e)[:60]))
check("A changed JSON parses (entity, controller, manifest, textures_list)", not bad, bad)
ent = load(B / "entity/trader_llama.entity.json")["minecraft:client_entity"]["description"]
tex = ent["textures"]; miss = [k for k, v in tex.items() if not (B / (v + ".png")).exists()]
check("B entity textures default + variant_0..3 resolve to files", set(tex) == {"default", "variant_0", "variant_1", "variant_2", "variant_3"} and not miss, (tex, miss))
rc = load(B / "render_controllers/pw_trader_llama.render.json")["render_controllers"]["controller.render.pw_trader_llama"]
check("B controller picks Array.variants[math.clamp(query.variant,0,3)] over Texture.variant_0..3", rc["arrays"]["textures"]["Array.variants"] == [f"Texture.variant_{i}" for i in range(4)] and rc["textures"] == ["Array.variants[math.clamp(query.variant, 0, 3)]"])
check("B entity still uses geometry.trader_llama.patrix + controller.render.pw_trader_llama", ent["geometry"]["default"] == "geometry.trader_llama.patrix" and ent["render_controllers"] == ["controller.render.pw_trader_llama"])
L = B / "textures/entity/llama"; decor = np.array(Image.open(L / "trader_llama.png").convert("RGBA")).astype(int)
cbad = []
for v in VAR:
    body = np.array(Image.open(L / f"{v}.png").convert("RGBA")).astype(int); comp = np.array(Image.open(L / f"trader_llama_{v}.png").convert("RGBA")).astype(int)
    full = decor[..., 3] == 255; none = decor[..., 3] == 0
    e1 = np.abs(comp[full] - decor[full]).max() if full.any() else 0
    e2 = np.abs(comp[none] - body[none]).max()
    if e1 > 0 or e2 > 0 or comp.shape != (512, 1024, 4): cbad.append((v, int(e1), int(e2), comp.shape))
check("C composites exact: decor pixels (alpha 255) = decor, decor-transparent pixels = the body variant, 1024x512", not cbad, cbad)
# UV-window opacity on the model's faces: v1.4.9 texture vs v1.4.10 composite (geometry uv 128x64 -> texture x8)
geo = load(B / "models/entity/trader_llama.geo.json")["minecraft:geometry"][0]; S = 8
def windows():
    for b in geo["bones"]:
        for i, c in enumerate(b.get("cubes", [])):
            for f, u in c["uv"].items():
                (uu, vv), (w, h) = u["uv"], u["uv_size"]
                x0, x1 = sorted([uu * S, (uu + w) * S]); y0, y1 = sorted([vv * S, (vv + h) * S])
                if x1 - x0 >= 1 and y1 - y0 >= 1: yield b["name"], i, f, (int(x0), int(y0), int(x1), int(y1))
old = np.array(Image.open(A / "textures/entity/llama/trader_llama.png").convert("RGBA"))[..., 3]
new = np.array(Image.open(L / "trader_llama_creamy.png").convert("RGBA"))[..., 3]
rows = []
for bone, i, f, (x0, y0, x1, y1) in windows():
    if i != 0 or bone not in ("body_cube", "head2", "leg0", "leg1", "leg2", "leg3", "snout"): continue   # cube 0 = the solid body parts; 1..4 are fur/decor shells
    rows.append((bone, f, float((old[y0:y1, x0:x1] > 127).mean()), float((new[y0:y1, x0:x1] > 127).mean())))
o_mean = np.mean([r[2] for r in rows]); n_mean = np.mean([r[3] for r in rows]); n_min = min(r[3] for r in rows)
check(f"D solid body faces (cube 0 of body/neck/snout/legs, {len(rows)} face windows) opaque: v1.4.9 mean {o_mean:.1%} -> v1.4.10 mean {n_mean:.1%}, min {n_min:.1%} (>= 90%)", n_min >= 0.90, sorted(rows, key=lambda r: r[3])[:4])
def th(root): return {str(p.relative_to(root)).replace("\\", "/"): hashlib.md5(p.read_bytes()).hexdigest() for p in root.rglob("*") if p.is_file()}
h0, h1 = th(A), th(B); added = set(h1) - set(h0); removed = set(h0) - set(h1); ch = {k for k in h0 if k in h1 and h0[k] != h1[k]}
check("E diff vs v1.4.9: +4 textures; changed only entity/controller/manifest/textures_list/ledger; nothing removed",
      added == {f"textures/entity/llama/trader_llama_{v}.png" for v in VAR} and not removed and ch == {"entity/trader_llama.entity.json", "render_controllers/pw_trader_llama.render.json", "manifest.json", "textures/textures_list.json", "PW-DEPENDENCIES.md"}, (sorted(added), sorted(removed), sorted(ch)))
man = load(B / "manifest.json")["header"]
check("E manifest v1.4.10 + stamp, uuid unchanged", man["version"] == [1, 4, 10] and man["description"].startswith(f"v1.4.10 ({DATE})") and man["uuid"] == load(A / "manifest.json")["header"]["uuid"])
# diagnostic sheet: decor | body | composite, UV windows of the solid faces outlined
try: font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
except Exception: font = ImageFont.load_default()
def onbg(p):
    im = Image.open(p).convert("RGBA"); bg = Image.new("RGBA", im.size, (60, 160, 60, 255)); bg.alpha_composite(im); return bg
panels = [("v1.4.9 bound texture = trader decor only (green = transparent)", onbg(A / "textures/entity/llama/trader_llama.png")),
          ("Patrix body variant creamy.png (never bound)", onbg(L / "creamy.png")),
          ("v1.4.10 trader_llama_creamy.png = body + decor", onbg(L / "trader_llama_creamy.png"))]
W = 1024 // 2; H = 512 // 2
sheet = Image.new("RGBA", (W, (H + 28) * 3 + 30), (18, 18, 20, 255)); d = ImageDraw.Draw(sheet)
for k, (lab, im) in enumerate(panels):
    im = im.copy(); dd = ImageDraw.Draw(im)
    for bone, i, f, (x0, y0, x1, y1) in windows():
        if i == 0 and bone in ("body_cube", "head2", "leg0", "leg1", "leg2", "leg3", "snout"): dd.rectangle([x0, y0, x1 - 1, y1 - 1], outline=(255, 40, 200, 255), width=3)
    y = 24 + k * (H + 28); sheet.paste(im.resize((W, H), Image.LANCZOS), (0, y)); d.text((4, y - 20), lab, fill=(255, 220, 140, 255), font=font)
d.text((4, sheet.height - 22), "magenta = the UV windows of the solid body/neck/leg faces", fill=(200, 200, 200, 255), font=font)
sheet.save(OUT / "rp07-trader-llama-textures.png")
if any(not ok for _, ok in res): print("GATE CLOSED"); sys.exit(1)
out = OUT / "RP-07-AbsolutRealism-Neutral-Mobs-RP-v1_4_10.mcpack"
if out.exists(): out.unlink()
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for p in sorted(B.rglob("*")):
        if p.is_file(): z.write(p, str(p.relative_to(B)).replace("\\", "/"))
with zipfile.ZipFile(out) as z: zh = {n: hashlib.md5(z.read(n)).hexdigest() for n in z.namelist() if not n.endswith("/")}
assert zh == th(B)
print(f"\nGATE OPEN — {len(res)} checks\n  {out.name} {out.stat().st_size:,} B md5 {hashlib.md5(out.read_bytes()).hexdigest()}")
