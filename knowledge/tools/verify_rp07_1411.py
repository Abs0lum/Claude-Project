#!/usr/bin/env python3
"""verify_rp07_1411.py — gate for RP-07 v1.4.11 (trader llama = ordinary llama geometry). Packages on GATE OPEN.
  A diff vs v1.4.10: exactly manifest.json + models/entity/trader_llama.geo.json changed; nothing added/removed
  B the trader geometry == the llama geometry except the identifier (bones, cubes, UVs, pivots, rotations byte-equal after rename);
    the rendered pose puts the body ON the legs (body y-min <= leg y-max) and the head pivot at 24 — computed with the
    engine rotation convention that keeps the witnessed cow/wolf coherent (D-C253)
  C entity/trader_llama.entity.json still binds geometry.trader_llama.patrix (default + baby) + controller.render.pw_trader_llama;
    every texture it binds exists
  D every bone driven by the animations the trader entity actually binds (setup/walk/look_at_target/baby_transform/ar_walk/ar_idle/
    pw_ambient/pw_eyes — the ones OUR files define) exists in the new geometry, or is a known no-op bone
    (placeholder_bone in the shims; r_pupil/l_pupil — pw_eyes is the house's benign no-op, absent in the ordinary llama too)
  E manifest v1.4.11 + stamp, uuid unchanged
  F every JSON that parsed in v1.4.10 still parses; the set of unparseable files is UNCHANGED (3 pre-existing, logged for the backlog)
  G textures/textures_list.json unchanged; the 4 composite trader textures still present
"""
import json, re, sys, hashlib, zipfile, datetime
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
from entity_render import load_geo, extents
ROOT = Path("/home/claude"); OUT = Path("/mnt/user-data/outputs"); A, B = ROOT / "_build/rp07-1410", ROOT / "_build/rp07-1411"
NAME = "RP-07-AbsolutRealism-Neutral-Mobs-RP-v1_4_11.mcpack"; DATE = "2026-09-27"
res = []
def check(name, ok, detail=""):
    res.append((name, bool(ok))); print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f" — {detail}" if detail else ""))
def load(p): return json.loads(re.sub(r"^\s*//.*$", "", Path(p).read_text(encoding="utf-8-sig"), flags=re.M))
def md5(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()

# A
def th(root): return {str(p.relative_to(root)).replace("\\", "/"): md5(p) for p in root.rglob("*") if p.is_file()}
h0, h1 = th(A), th(B); added = set(h1) - set(h0); removed = set(h0) - set(h1); ch = {k for k in h0 if k in h1 and h0[k] != h1[k]}
check("A diff vs v1.4.10: only manifest.json + models/entity/trader_llama.geo.json changed", not added and not removed and ch == {"manifest.json", "models/entity/trader_llama.geo.json"}, (sorted(added), sorted(removed), sorted(ch)))

# B
gl = load(B / "models/entity/llama.geo.json"); gt = load(B / "models/entity/trader_llama.geo.json")
gl2 = json.loads(json.dumps(gl)); gl2["minecraft:geometry"][0]["description"]["identifier"] = "geometry.trader_llama.patrix"
check("B trader geometry == llama geometry except the identifier", gl2 == gt and gt["minecraft:geometry"][0]["description"]["identifier"] == "geometry.trader_llama.patrix")
cubes = load_geo(B / "models/entity/trader_llama.geo.json", "geometry.trader_llama.patrix")
body = extents(cubes, "body_cube"); legs = extents([c for c in cubes if c[0].startswith("leg")])
head_piv = next(b["pivot"] for b in gt["minecraft:geometry"][0]["bones"] if b["name"] == "head")
check("B pose: body sits on the legs (body y-min <= leg y-max), body top 24, legs 0..16, head pivot y 24", body[1][0] <= legs[1][1] and abs(body[1][1] - 24) <= 0.05 and legs[1] == (0.0, 16.0) and head_piv[1] == 24,
      f"body y {body[1]} z {body[2]}; legs y {legs[1]}; head pivot {head_piv}")
old = load_geo(A / "models/entity/trader_llama.geo.json", "geometry.trader_llama.patrix"); ob = extents(old, "body_cube"); ol = extents([c for c in old if c[0].startswith("leg")])
check("B the 1.4.10 pose it replaces DID float (recorded): body y-min > leg y-max", ob[1][0] > ol[1][1], f"1.4.10 body y {ob[1]} legs y {ol[1]}")

# C
ent = load(B / "entity/trader_llama.entity.json")["minecraft:client_entity"]["description"]
check("C entity binds geometry.trader_llama.patrix (default + baby) + controller.render.pw_trader_llama",
      ent["geometry"] == {"default": "geometry.trader_llama.patrix", "baby": "geometry.trader_llama.patrix"} and ent["render_controllers"] == ["controller.render.pw_trader_llama"])
missing_tex = [t for t in ent["textures"].values() if not (B / (t + ".png")).exists()]
check("C every bound texture exists", not missing_tex, str(missing_tex))

# D
anims = {}
for p in (B / "animations").glob("*.json"):
    try: anims.update(load(p).get("animations", {}))
    except Exception: pass
bones = {b["name"] for b in gt["minecraft:geometry"][0]["bones"]}
NOOP = {"placeholder_bone", "r_pupil", "l_pupil"}
bad = {}
for short, aid in ent["animations"].items():
    if aid not in anims: bad[aid] = "NOT DEFINED IN RP-07 (vanilla-provided)"; continue
    drv = set(anims[aid].get("bones", {})) - bones - NOOP
    if drv: bad[aid] = sorted(drv)
# vanilla-provided ids are allowed only for the known set
vanilla_ok = {"animation.quadruped.walk", "animation.common.look_at_target"}
bad = {k: v for k, v in bad.items() if not (v == "NOT DEFINED IN RP-07 (vanilla-provided)" and k in vanilla_ok)}
check("D every bone the BOUND animations drive exists in the new geometry (no-op bones allowed)", not bad, str(bad))
# vanilla quadruped.walk drives leg0..3; look_at_target drives head — both present
check("D vanilla walk/look bones present (leg0-3, head)", {"leg0", "leg1", "leg2", "leg3", "head"} <= bones)

# E
man = load(B / "manifest.json")["header"]
check("E manifest v1.4.11 + stamp, uuid unchanged", man["version"] == [1, 4, 11] and man["description"].startswith(f"v1.4.11 ({DATE})") and man["uuid"] == load(A / "manifest.json")["header"]["uuid"] and man["name"].endswith("v1.4.11"))

# F
def unparseable(root):
    out = set()
    for p in root.rglob("*.json"):
        try: load(p)
        except Exception: out.add(str(p.relative_to(root)).replace("\\", "/"))
    return out
u0, u1 = unparseable(A), unparseable(B)
check("F set of unparseable JSONs unchanged vs v1.4.10 (pre-existing, backlog)", u0 == u1, f"{sorted(u1)}")
check("F the two changed files parse", True)

# G
check("G textures_list unchanged; 4 composite trader textures present", h0["textures/textures_list.json"] == h1["textures/textures_list.json"] and all((B / f"textures/entity/llama/trader_llama_{v}.png").exists() for v in ("creamy", "white", "brown", "gray")))

if any(not ok for _, ok in res): print("GATE CLOSED"); sys.exit(1)
print(f"\nGATE OPEN — {len(res)} checks")
with open(ROOT / "_logs/phase_log.md", "a") as f: f.write(f"[{datetime.datetime.now().strftime('%H:%M')} CT 09-27] VERIFY rp07-1411 GATE OPEN {len(res)}/{len(res)} — packaging\n")
out = OUT / NAME
if out.exists(): out.unlink()
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for p in sorted(B.rglob("*")):
        if p.is_file(): z.write(p, str(p.relative_to(B)).replace("\\", "/"))
with zipfile.ZipFile(out) as z:
    zh = {n: hashlib.md5(z.read(n)).hexdigest() for n in z.namelist() if not n.endswith("/")}
    assert zh == h1 and "manifest.json" in z.namelist()
print(f"  {out.name} {out.stat().st_size:,} B md5 {md5(out)}")
