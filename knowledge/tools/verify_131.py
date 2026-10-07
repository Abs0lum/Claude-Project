#!/usr/bin/env python3
"""verify_131.py — GATE for RP-04 v1.3.131 (geometry-only follow-up to .130). Packages only if every check passes."""
import json, os, re, sys, hashlib, zipfile, subprocess
from pathlib import Path
ROOT = Path("/home/claude"); RP0, RP = ROOT / "_build/rp04-130", ROOT / "_build/rp04-131"; BP = ROOT / "_build/bp02-182"
OUT = Path("/mnt/user-data/outputs")
results = []
def check(n, ok, d=""):
    results.append((n, bool(ok), d)); print(("PASS " if ok else "FAIL ") + n + (f" — {d}" if d else "")); return bool(ok)
def load(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def md5(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()
def files(root): return {str(p.relative_to(root)).replace(os.sep, "/"): p for p in root.rglob("*") if p.is_file()}

a, b = files(RP0), files(RP)
diff = {n for n in set(a) | set(b) if n not in a or n not in b or a[n].read_bytes() != b[n].read_bytes()}
check("I change set = geometry + manifest + ledger only", diff == {"models/blocks/pw_homestead.geo.json", "manifest.json", "PW-DEPENDENCIES.md"}, sorted(diff))
try: json.loads((RP / "models/blocks/pw_homestead.geo.json").read_text(encoding="utf-8")); check("J strict parse pw_homestead.geo.json", True)
except Exception as e: check("J strict parse pw_homestead.geo.json", False, str(e))
doc = load(RP / "models/blocks/pw_homestead.geo.json"); G = {g["description"]["identifier"]: g for g in doc["minecraft:geometry"]}
check("G geometry ids unchanged (8)", set(G) == {"geometry.pw_flue_cap", "geometry.pw_rafter45", "geometry.pw_hearth_cold", "geometry.pw_hearth_fueled", "geometry.pw_hearth_lit", "geometry.pw_hearth_embers", "geometry.pw_flue_hollow", "geometry.pw_flue_cap_hollow"}, sorted(G))
def cubes(g, bone): return [c for bn in g["bones"] if bn["name"] == bone for c in bn["cubes"]]
def inst(c, f): return c["uv"][f].get("material_instance", "*")
for ph in ("cold", "fueled", "lit", "embers"):
    g = G[f"geometry.pw_hearth_{ph}"]; w = cubes(g, "walls")
    lo = [c for c in w if c["origin"][0] == -8][0]; hi = [c for c in w if c["origin"][0] == 6][0]
    ok = (len(w) == 2 and lo["size"] == [2, 15, 14] and hi["size"] == [2, 15, 14] and lo["origin"][1] == 1 and lo["origin"][2] == -8
          and inst(lo, "east") == "*" and inst(lo, "west") == "soot" and inst(hi, "west") == "*" and inst(hi, "east") == "soot"
          and inst(lo, "north") == "*" and inst(hi, "north") == "*" and inst(lo, "up") == "top" and "south" not in lo["uv"] and "down" not in lo["uv"])
    check(f"H {ph}: two side walls, 2 cubes, L-XFACE keys (outer material / inner soot), front material, top key", ok)
    fl = cubes(g, "floor")[0]
    check(f"H {ph}: floor outer faces = material, top = soot", inst(fl, "north") == "*" and inst(fl, "east") == "*" and inst(fl, "west") == "*" and inst(fl, "up") == "soot")
    check(f"H {ph}: logs {'present' if ph != 'cold' else 'absent'}", (len(cubes(g, "logs")) == 4) == (ph != "cold"))
    f = cubes(g, "flames")
    if ph == "lit": check("H lit flames 17x16 at y 2..18, +-45 about y, inflate 0.01", len(f) == 2 and all(c["size"] == [17.0, 16.0, 0] and c["origin"][1] == 2.0 and abs(c["rotation"][1]) == 45 and c.get("inflate") == 0.01 for c in f))
    elif ph == "embers": check("H embers flames 14x9 at y 3..12", len(f) == 2 and all(c["size"] == [14.0, 9.0, 0] and c["origin"][1] == 3.0 for c in f))
    else: check(f"H {ph}: no flames", len(f) == 0)
    vb = g["description"]; check(f"H {ph}: visible bounds cover the flame (height 2.0, offset 1.0)", vb["visible_bounds_height"] == 2.0 and vb["visible_bounds_offset"] == [0, 1.0, 0])
for gid in ("geometry.pw_flue_hollow", "geometry.pw_flue_cap_hollow"):
    w = cubes(G[gid], "walls"); lo = [c for c in w if c["origin"][0] == -8 and c["size"][0] == 2][0]; hi = [c for c in w if c["origin"][0] == 6][0]
    n = [c for c in w if c["origin"][2] == -8 and c["size"][2] == 2][0]; s = [c for c in w if c["origin"][2] == 6][0]
    check(f"X {gid}: x-walls swapped per L-XFACE, z-walls unchanged", inst(lo, "east") == "*" and inst(lo, "west") == "soot" and inst(hi, "west") == "*" and inst(hi, "east") == "soot"
          and inst(n, "north") == "*" and inst(n, "south") == "soot" and inst(s, "south") == "*" and inst(s, "north") == "soot")
check("X cap keeps the rim", len(cubes(G["geometry.pw_flue_cap_hollow"], "rim")) == 4)
# every hearth/flue material instance the BP uses exists in the geometries' faces (no orphan face instance, no missing instance)
used = set()
for gid, g in G.items():
    if not (gid.startswith("geometry.pw_hearth_") or gid.startswith("geometry.pw_flue_")): continue      # rafter declares its own 'end'
    for bn in g["bones"]:
        for c in bn["cubes"]:
            for f, v in c["uv"].items(): used.add(v.get("material_instance", "*"))
bp_inst = set()
for p in list((BP / "blocks").glob("pw_hearth_*.json"))[:1] + list((BP / "blocks").glob("pw_flue_*.json"))[:1]:
    blk = load(p)["minecraft:block"]
    for comps in [blk["components"]] + [pm.get("components", {}) for pm in blk["permutations"]]:
        bp_inst |= set(comps.get("minecraft:material_instances", {}).keys())
check("T every face instance the geometries use is declared by the BP-02 .182 blocks", used <= bp_inst, sorted(used - bp_inst))
m = load(RP / "manifest.json"); check("V manifest v1.3.131 stamped", m["header"]["version"] == [1, 3, 131] and all(x["version"] == [1, 3, 131] for x in m["modules"]) and "1.3.131" in m["header"]["description"])
check("L ledger stamped", "v1.3.131 ·" in (RP / "PW-DEPENDENCIES.md").read_text(encoding="utf-8"))
failed = [n for n, ok, _ in results if not ok]
if failed: print(f"\nGATE CLOSED — {failed}"); sys.exit(1)
out = OUT / "RP-04-AbsolutRealism-Basic-RP-v1_3_131.mcpack"
if out.exists(): out.unlink()
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for p in sorted(RP.rglob("*")):
        if p.is_file(): z.write(p, str(p.relative_to(RP)).replace(os.sep, "/"))
with zipfile.ZipFile(out) as z: zh = {n: hashlib.md5(z.read(n)).hexdigest() for n in z.namelist() if not n.endswith("/")}
check("Z1 from-zip identity", zh == {n: md5(p) for n, p in files(RP).items()})
r = subprocess.run(["python3", str(ROOT / "tools/verify_pack_versions.py"), str(out)], capture_output=True, text=True); print(r.stdout.strip())
check("Z2 version-spot gate", r.returncode == 0, r.stderr[:200])
failed = [n for n, ok, _ in results if not ok]
if failed: out.unlink(); print(f"\nGATE CLOSED at packaging — {failed}"); sys.exit(1)
print(f"\nGATE OPEN — {len(results)} checks; {out.name} {out.stat().st_size:,} B md5 {md5(out)}")
