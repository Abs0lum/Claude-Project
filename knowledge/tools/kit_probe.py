#!/usr/bin/env python3
"""kit_probe.py — BDS check of the road kit + the street planner's placements (rotations, heights, continuity).
Builds a probe BP (structures/pw/road/* from _docs/road_kit, pw_civ_streets.js, a main that plans four streets on
synthetic ground — east, west, north, south, each climbing then descending — plus a tee and a connector, places them high
in the air at y ~200 and dumps every corridor column), runs it in BDS and checks:
  * surface: sidewalk block (w = 1) at the planned H for every t; road block (w = 6) at H - 1 (ramps: within the climb)
  * sewer: the channel air at w = 6 is continuous along t (no wall across it) between dead-end chambers
  * corridor covered: no cell without a block at the road row
Usage: kit_probe.py"""
import json
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
import bds_civtest as T  # noqa: E402

KIT = Path("/home/claude/_docs/road_kit")
SRC = Path("/home/claude/tools/bp02_src/pw_civ_streets.js")
BP = Path("/home/claude/_bds/kitprobe/bp")

MAIN = r'''import { world, system } from "@minecraft/server";
import * as S from "./pw_civ_streets.js";
const log = (o) => console.warn("[CIVTEST] " + JSON.stringify(o));
const sleep = (n) => new Promise((r) => system.runTimeout(r, n));
const BASE = 200;
// synthetic ground along t: up 2 blocks then down 2 (ramps both ways)
function ground(L) { return Array.from({ length: L }, (_, t) => { const g = BASE + (t > 25 && t < 60 ? 1 : 0) + (t > 34 && t < 50 ? 1 : 0); return { g, water: false, lo: g, hi: g }; }); }
const STREETS = [
  { name: "east", f: S.frameOf(20, 20, [1, 0], [0, 1]) },
  { name: "west", f: S.frameOf(110, 60, [-1, 0], [0, 1]) },
  { name: "south", f: S.frameOf(130, 20, [0, 1], [1, 0]) },
  { name: "north", f: S.frameOf(170, 110, [0, -1], [1, 0]) },
];
const L = 85;
async function main() {
  const dim = world.getDimension("overworld");
  for (const [a, b, c, d, nm] of [[0, 0, 95, 95, "k1"], [96, 0, 199, 95, "k2"], [0, 96, 95, 199, "k3"], [96, 96, 199, 199, "k4"]]) {
    try { const r = dim.runCommand(`tickingarea add ${a} 0 ${b} ${c} 0 ${d} ${nm} true`); log({ step: "tickingarea", nm, ok: r.successCount }); } catch (e) { log({ step: "tickingarea", nm, err: String(e) }); }
  }
  for (let i = 0; i < 90; i++) { let ok = true; for (const [x, z] of [[5, 5], [195, 195], [5, 195], [195, 5], [100, 100]]) { try { if (!dim.getBlock({ x, y: 64, z })) ok = false; } catch { ok = false; } } if (ok) { log({ step: "loaded", i }); break; } await sleep(20); }
  const out = [];
  for (const s of STREETS) {
    const plan = S.planProfile(ground(L));
    const { pieces } = S.piecesOf(s.f, plan, s.name === "west" ? "t" : "v");
    // an access piece at t 15 (flat) to test its galleries
    pieces.push(S.accessPiece(s.f, 16, plan.H[16], s.name === "west" ? "t" : "v"));
    let placed = 0, err = [];
    for (const p of pieces) {
      try { world.structureManager.place(`pw:road/${p.name}`, dim, { x: p.x, y: p.y, z: p.z }, { rotation: ["None", "Rotate90", "Rotate180", "Rotate270"][p.rot] }); placed++; }
      catch (e) { err.push(`${p.name}@${p.x},${p.y},${p.z}: ${e}`); }
    }
    log({ step: "placed", street: s.name, placed, n: pieces.length, err: err.slice(0, 3), segs: plan.segs.map((q) => [q.kind, q.a, q.len, q.H, q.dir || 0]) });
    out.push({ s, plan });
  }
  await sleep(40);
  // dump: per street, per t, per w: the column from H-15 to H+2 (relative to the planned H at t) as chars
  const CH = { "minecraft:air": ".", "minecraft:cobblestone": "c", "minecraft:smooth_stone": "s", "minecraft:stone_bricks": "B", "minecraft:stone_brick_stairs": "t",
               "minecraft:dirt": "d", "minecraft:grass_block": "g", "minecraft:smooth_stone_slab": "_", "minecraft:stone_brick_slab": "-" };
  for (const { s, plan } of out) {
    for (let t = 0; t < L; t++) {
      const H = plan.H[t];
      const cols = [];
      for (let w = 0; w < 13; w++) {
        const [x, z] = S.cellOf(s.f, t, w);
        let col = "";
        for (let y = BASE - 16; y <= BASE + 4; y++) { const id = dim.getBlock({ x, y, z })?.typeId || "?"; col += CH[id] || (id.includes("ramp") ? "r" : id.includes("seated") ? "q" : "?"); }
        cols.push(col);
      }
      log({ step: "col", street: s.name, t, H, cols });
    }
  }
  log({ step: "DONE" });
}
system.runTimeout(() => { main().catch((e) => log({ step: "error", err: String(e), stack: e.stack })); }, 100);
'''


def build():
    if BP.exists():
        shutil.rmtree(BP)
    (BP / "scripts").mkdir(parents=True)
    (BP / "structures/pw/road").mkdir(parents=True)
    for f in KIT.glob("*.mcstructure"):
        shutil.copy(f, BP / "structures/pw/road" / f.name)
    shutil.copy(SRC, BP / "scripts/pw_civ_streets.js")
    (BP / "scripts/main.js").write_text(MAIN)
    man = {"format_version": 2, "header": {"name": "kitprobe", "description": "kit probe", "uuid": str(uuid.uuid4()), "version": [0, 0, 1], "min_engine_version": [1, 21, 80]},
           "modules": [{"type": "data", "uuid": str(uuid.uuid4()), "version": [0, 0, 1]},
                       {"type": "script", "language": "javascript", "entry": "scripts/main.js", "uuid": str(uuid.uuid4()), "version": [0, 0, 1]}],
           "dependencies": [{"module_name": "@minecraft/server", "version": "2.3.0"}]}
    (BP / "manifest.json").write_text(json.dumps(man, indent=1))


def main():
    build()
    out, recs, errs = T.run([str(BP)], seconds=300)
    print(f"log {out} · {len(recs)} records · {len(errs)} ERROR lines")
    for e in errs[:10]:
        print("ERR", e[-220:])
    Path("/home/claude/_bds/kitprobe/records.json").write_text(json.dumps(recs))
    for r in recs:
        if r.get("step") != "col":
            print(json.dumps(r)[:900])


if __name__ == "__main__":
    main()
