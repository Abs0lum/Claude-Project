#!/usr/bin/env python3
"""build_bp02_210.py — BP-02 1.3.210 from the frozen 1.3.209 (never rebuilt): the CIVITAS fix round after the GS-1 probe.
  * GS-1 (D-C505): layPlannedStreet judged a street cell's role from its PREVIOUS cell only, so the first cell of every
    run after a jog was laid as a centred cross and its two body cells were never laid (a hole / a bump at every run
    start, both axes; gs1probe-0.0.2: 6 unlaid cells at the forest village's two junctions, present from founding).
    Now a run cell is judged from EITHER neighbour; jog cells keep their centred cross.
  * TREEGROW registry: chunked text properties (the 400-cap registry could pass 32,767 chars) — pw_fell / main.js
Writes _build/bp02-210; bumps manifest header + module versions, the description and the PW-DEPENDENCIES stamp.
Then: node tests · bds_load gate · gs1probe-0.0.3 regression (0 unlaid body cells)."""
import json
import re
import shutil
from pathlib import Path

B = Path("/home/claude/_build")
SRC, DST = B / "bp02-209", B / "bp02-210"
S = Path("/home/claude/tools/bp02_src")


GROW_OLD = """function _growSave() {
  try {
    const arr = [...(_growRegistry.values())].slice(0, 400).map((i) => [i.type, i.dim, i.x, i.y, i.z, i.due - system.currentTick]);
    world.setDynamicProperty(PW_GROW_KEY, JSON.stringify(arr));
  } catch (e) { logErr("treegrow-save: " + (e && e.message ? e.message : e)); }
}
function _growLoad() {
  try {
    const raw = world.getDynamicProperty(PW_GROW_KEY);
    if (typeof raw !== "string") return 0;
    let n = 0;
    for (const [type, dim, x, y, z, left] of JSON.parse(raw)) {
      _growRegistry.set(`${dim}|${x},${y},${z}`, { type, dim, x, y, z, due: system.currentTick + Math.max(40, left | 0) }); n++;
    }
    return n;
  } catch (e) { logErr("treegrow-load-registry: " + (e && e.message ? e.message : e)); return 0; }
}"""
GROW_NEW = """// the registry on disk: one dynamic property holds at most 32,767 chars (the CIVITAS state law, D-C499) — 400 entries of
// ["minecraft:mangrove_propagule","minecraft:overworld",x,y,z,left] could pass it, so entries are saved COMPACT (type and
// dimension as indexes into the two tables, ~25 chars each: 400 entries = ~10,000 chars) and split over numbered chunks
// pw:treegrow:0 .. :n of 30,000 chars should the cap ever grow. The old long form (an array of arrays with string ids)
// still loads (a world saved by 1.3.209).
const PW_GROW_TYPES = Object.keys(PW_GROW_POOLS);
const PW_GROW_DIMS = ["minecraft:overworld", "minecraft:nether", "minecraft:the_end"];
const PW_GROW_CHUNK = 30000;
function _growSave() {
  try {
    const arr = [...(_growRegistry.values())].slice(0, 400).map((i) => [PW_GROW_TYPES.indexOf(i.type), PW_GROW_DIMS.indexOf(i.dim), i.x, i.y, i.z, i.due - system.currentTick]);
    const text = JSON.stringify(arr);
    const parts = [];
    for (let k = 0; k < text.length; k += PW_GROW_CHUNK) parts.push(text.slice(k, k + PW_GROW_CHUNK));
    world.setDynamicProperty(PW_GROW_KEY, undefined);
    world.setDynamicProperty(PW_GROW_KEY + ":n", parts.length);
    for (let k = 0; k < parts.length; k++) world.setDynamicProperty(`${PW_GROW_KEY}:${k}`, parts[k]);
    // drop stale chunks beyond the new count (the registry shrank)
    for (let k = parts.length; k < parts.length + 4; k++) { try { if (world.getDynamicProperty(`${PW_GROW_KEY}:${k}`) !== undefined) world.setDynamicProperty(`${PW_GROW_KEY}:${k}`, undefined); } catch {} }
  } catch (e) { logErr("treegrow-save: " + (e && e.message ? e.message : e)); }
}
function _growLoad() {
  try {
    let raw = world.getDynamicProperty(PW_GROW_KEY);                 // the 1.3.209 single property
    if (typeof raw !== "string") {
      const n = world.getDynamicProperty(PW_GROW_KEY + ":n");
      if (typeof n !== "number" || n <= 0) return 0;
      raw = "";
      for (let k = 0; k < n; k++) { const part = world.getDynamicProperty(`${PW_GROW_KEY}:${k}`); if (typeof part !== "string") return 0; raw += part; }
    }
    let count = 0;
    for (const [t, d, x, y, z, left] of JSON.parse(raw)) {
      const type = typeof t === "number" ? PW_GROW_TYPES[t] : t, dim = typeof d === "number" ? PW_GROW_DIMS[d] : d;
      if (!type || !dim) continue;
      _growRegistry.set(`${dim}|${x},${y},${z}`, { type, dim, x, y, z, due: system.currentTick + Math.max(40, left | 0) }); count++;
    }
    return count;
  } catch (e) { logErr("treegrow-load-registry: " + (e && e.message ? e.message : e)); return 0; }
}"""


def patch_treegrow(path):
    js = path.read_text()
    if GROW_OLD not in js:
        raise SystemExit("TREEGROW save/load block not found in main.js")
    js = js.replace(GROW_OLD, GROW_NEW)
    path.write_text(js)
    print("main.js: TREEGROW registry -> compact + chunked")


def main():
    if DST.exists():
        raise SystemExit(f"never rebuild {DST}")
    shutil.copytree(SRC, DST)
    for f in ["pw_civ_clock.js", "pw_civ_land.js", "pw_civ_economy.js"]:
        shutil.copy2(S / f, DST / "scripts" / f)
    patch_treegrow(DST / "scripts/main.js")
    # the in-script banner (PW_BUILD) had stayed at "1.3.206" since 206 — the p23 q0 brief told him to expect
    # '[PW-VERSION] BP-02 v1.3.209' while the log says v1.3.206 (found at the 210 load gate, 02:10 CT 10-03)
    mj = DST / "scripts/main.js"
    js = mj.read_text()
    if 'const PW_BUILD = "1.3.206";' not in js:
        raise SystemExit("PW_BUILD line not found")
    mj.write_text(js.replace('const PW_BUILD = "1.3.206";', 'const PW_BUILD = "1.3.210";'))
    print("main.js: PW_BUILD -> 1.3.210 (the [PW-VERSION] / [TREEGROW] BOOT banners)")
    m = json.loads((DST / "manifest.json").read_text())
    m["header"]["version"] = [1, 3, 210]
    for mod in m["modules"]:
        mod["version"] = [1, 3, 210]
    m["header"]["name"] = "AbsolutRealism Tectonic BP v1.3.210"
    desc = m["header"]["description"]
    desc = re.sub(r"^v1\.3\.209 \(2026-10-03\) ", "", desc)
    m["header"]["description"] = ("v1.3.210 (2026-10-03) CIVITAS fix: every street run's first cell after a jog gets its full 3-wide body "
                                  "(GS-1: two cells per junction were never laid); TREEGROW registry in chunked properties. Includes all of v1.3.209: " + desc)[:1000]
    (DST / "manifest.json").write_text(json.dumps(m, indent=1))
    dep = DST / "PW-DEPENDENCIES.md"
    t = dep.read_text()
    t2 = t.replace("v1.3.209 (T4 exact falling set;", "v1.3.210 (GS-1 run-start body fix + TREEGROW chunked registry; T4 exact falling set;")
    assert t2 != t, "stamp not found"
    dep.write_text(t2)
    print(f"DONE {DST} (manifest 1.3.210, scripts: clock/land/economy from tools/bp02_src)")


if __name__ == "__main__":
    main()
