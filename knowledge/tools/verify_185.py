#!/usr/bin/env python3
"""verify_185.py — gate for BP-02 v1.3.185 (room-smoke wall test, D-C228); packages on GATE OPEN."""
import json, re, sys, hashlib, zipfile, subprocess, shutil, tempfile
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import api_audit as AA
ROOT = Path("/home/claude"); OUT = Path("/mnt/user-data/outputs"); A, B = ROOT / "_build/bp02-184", ROOT / "_build/bp02-185"; DATE = "2026-09-22"
res = []
def check(n, ok, d=""): res.append((n, bool(ok))); print(("PASS " if ok else "FAIL ") + n + ("" if ok else f"  -> {str(d)[:400]}"))
def load(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))

man = load(B / "manifest.json"); m0 = load(A / "manifest.json")
check("A manifest v1.3.185 + stamp; uuid and module pins unchanged (@minecraft/server 2.0.0, server-ui 2.0.0)",
      man["header"]["version"] == [1, 3, 185] and man["header"]["description"].startswith(f"v1.3.185 ({DATE})") and man["header"]["uuid"] == m0["header"]["uuid"]
      and man.get("dependencies") == m0.get("dependencies"))
for f in ("pw_homestead.js", "pw_homestead_logic.js", "main.js"):
    r = subprocess.run(["node", "--check", str(B / "scripts" / f)], capture_output=True, text=True); check(f"B {f} syntax (node --check)", r.returncode == 0, r.stderr[:200])
hs = (B / "scripts/pw_homestead.js").read_text(encoding="utf-8")
code = AA.strip_comments_and_strings(hs)
room_src = hs[hs.index("function roomFor("):hs.index("function emitRoomSmoke(")]
check("B roomFor uses L.floodRoom + L.smokePasses; no .isSolid anywhere in BP-02 script code",
      "L.floodRoom(" in room_src and "L.smokePasses(" in room_src and not any(".isSolid" in AA.strip_comments_and_strings((B / "scripts" / p.name).read_text(encoding="utf-8")) for p in (B / "scripts").glob("*.js")))
check("B the build scripts are exactly tools/homestead_src (the tested sources)",
      all((B / "scripts" / f).read_bytes() == (ROOT / "tools/homestead_src" / f).read_bytes() for f in ("pw_homestead.js", "pw_homestead_logic.js")))
with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    shutil.copy(B / "scripts/pw_homestead_logic.js", td / "pw_homestead_logic.js"); shutil.copy(ROOT / "tools/homestead_src/test_logic.mjs", td / "test_logic.mjs")
    r = subprocess.run(["node", "test_logic.mjs"], cwd=td, capture_output=True, text=True)
    mm = re.search(r"(\d+) tests passed", r.stdout)
    check(f"C unit tests on the SHIPPED logic: {mm.group(1) if mm else '?'} passed (fuel/phases/hazards + smokePasses + floodRoom + the D-C228 regression)", r.returncode == 0 and mm and int(mm.group(1)) >= 21, (r.stdout + r.stderr)[-400:])
    # D integration: the shipped roomFor + getBlockSafe, sliced out and run against a stub world
    gbs = re.search(r"^function getBlockSafe\(.*$", hs, re.M).group(0)
    harness = r'''
import * as L from "./pw_homestead_logic.js";
const system = { currentTick: 1000 }; const rooms = new Map(); const ROOM_MAX_CELLS = 400, ROOM_RADIUS = 12, ROOM_TTL_TICKS = 600;
''' + gbs + "\n" + room_src + r'''
function makeWorld(doorOpen, withDoor) {
  const g = new Map();
  for (let x = 0; x <= 6; x++) for (let y = 0; y <= 4; y++) for (let z = 0; z <= 6; z++) {
    const inside = x >= 1 && x <= 5 && y >= 1 && y <= 3 && z >= 1 && z <= 5; g.set(`${x},${y},${z}`, inside ? "minecraft:air" : "minecraft:oak_planks"); }
  g.set("0,1,3", "pw:hearth_oak_planks"); g.set("3,1,3", "pw:furn_table_oak");
  if (withDoor) { g.set("6,1,2", "minecraft:wooden_door"); g.set("6,2,2", "minecraft:wooden_door"); }
  return { getBlock: ({ x, y, z }) => { const id = g.get(`${x},${y},${z}`) ?? "minecraft:air";
    return { typeId: id, permutation: { getState: (k) => (k === "open_bit" ? doorOpen : undefined) } }; } };
}
const hearth = { location: { x: 0, y: 1, z: 3 }, permutation: { getState: (k) => (k === "minecraft:cardinal_direction" ? "east" : undefined) } };
const a = roomFor("k1", makeWorld(false, false), hearth); rooms.clear();
const b = roomFor("k2", makeWorld(false, true), hearth); rooms.clear();
const c = roomFor("k3", makeWorld(true, true), hearth); rooms.clear();
const unloaded = { getBlock: ({ x }) => { if (x > 3) throw new Error("unloaded"); return { typeId: "minecraft:air", permutation: { getState: () => undefined } }; } };
const d = roomFor("k4", unloaded, hearth);
console.log(JSON.stringify({ enclosed: [a.open, a.cells.length], closedDoor: b.open, openDoor: c.open, unloaded: d.open, cachedUntil: a.until }));
'''
    (td / "harness.mjs").write_text(harness, encoding="utf-8")
    r = subprocess.run(["node", "harness.mjs"], cwd=td, capture_output=True, text=True)
    try: o = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception: o = {}
    check(f"D the SHIPPED roomFor on a stub world: enclosed room CLOSED ({o.get('enclosed')}), closed door CLOSED, open door OPEN, unloaded cell OPEN, cache TTL kept",
          o.get("enclosed") == [False, 75] and o.get("closedDoor") is False and o.get("openDoor") is True and o.get("unloaded") is True and o.get("cachedUntil") == 1600, (o, r.stderr[-300:]))
# E api audit on the shipped pack: isSolid gone; what remains is the reviewed, accepted list
rep = AA.audit(B)
names = sorted({f["name"] for f in rep["flags"]})
ACCEPTED = {"getBiome": "main.js fireflies: try/catch fallback (fireflies ignore biome) — backlog: pin >= 2.3.0",
            "getWeather": "main.js leaf wind: guarded (always calm) — backlog: weatherChange listener",
            "airSupply": "pw_homestead.js: 'in' feature-detect (known backlog)",
            "path": "pw_ground.js own spec field (false positive)", "count": "main.js own phase field (false positive)"}
check(f"E api_audit on v1.3.185: isSolid gone; remaining flags = the reviewed accepted set {sorted(ACCEPTED)}", "isSolid" not in names and set(names) <= set(ACCEPTED), names)
def th(root): return {str(p.relative_to(root)).replace("\\", "/"): hashlib.md5(p.read_bytes()).hexdigest() for p in root.rglob("*") if p.is_file()}
h0, h1 = th(A), th(B); ch = {k for k in h0 if k in h1 and h0[k] != h1[k]}
check("F diff vs v1.3.184: only the two homestead scripts + manifest + ledger stamp changed; nothing added/removed",
      set(h0) == set(h1) and ch == {"scripts/pw_homestead.js", "scripts/pw_homestead_logic.js", "manifest.json", "PW-DEPENDENCIES.md"}, sorted(ch))
led0, led1 = (A / "PW-DEPENDENCIES.md").read_text(encoding="utf-8"), (B / "PW-DEPENDENCIES.md").read_text(encoding="utf-8")
check("F ledger: only the version stamp moved (needs-hash unchanged)", led0.replace("v1.3.184 ·", "v1.3.185 ·", 1) == led1)
if any(not ok for _, ok in res): print("GATE CLOSED"); sys.exit(1)
out = OUT / "BP-02-AbsolutRealism-Tectonic-BP-v1_3_185.mcpack"
if out.exists(): out.unlink()
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for p in sorted(B.rglob("*")):
        if p.is_file(): z.write(p, str(p.relative_to(B)).replace("\\", "/"))
with zipfile.ZipFile(out) as z: zh = {n: hashlib.md5(z.read(n)).hexdigest() for n in z.namelist() if not n.endswith("/")}
assert zh == th(B)
print(f"\nGATE OPEN — {len(res)} checks\n  {out.name} {out.stat().st_size:,} B md5 {hashlib.md5(out.read_bytes()).hexdigest()}")
