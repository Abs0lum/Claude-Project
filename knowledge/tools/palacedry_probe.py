#!/usr/bin/env python3
"""palacedry_probe.py — template or site? (10-05 14:5x: after 18 gate runs on the harness's lake-and-pond site the palace
still read wet; run 18's dump showed water sheets running down the ROOFS). The four FULL palace pieces (BP-02's
pw:mvv_palace_<q>_a_r1) are placed with structureManager on a stone platform high in the air (nothing natural near),
then the block is read for water after 20 / 200 / 600 / 1200 ticks: count, the levels, and the first cells found.
If water appears here the source is OUR TEMPLATE; if it stays dry the site is to blame.
Usage: palacedry_probe.py OUT_DIR  → bds_civtest.py --seconds 600 _build/bp02-222 OUT_DIR"""
import json
import sys
import uuid
from pathlib import Path

MAIN = r'''
import { world, system } from "@minecraft/server";
const log = (o) => console.warn("[CIVTEST] " + JSON.stringify(o));
const sleep = (t) => new Promise((r) => system.runTimeout(r, t));
const X0 = 304, Z0 = 304, Y0 = 170;                     // the pieces' box origin (feet 0 = Y0 + 15)
const PIECES = { sw: [0, 0], se: [0, 64], nw: [64, 0], ne: [64, 64] };
const cmd = (dim, s) => { try { return dim.runCommand(s).successCount; } catch (e) { return "ERR " + String(e).slice(0, 60); } };
function read(dim) {
  let water = 0; const levels = {}; const first = [];
  for (let x = X0; x < X0 + 128; x++) for (let z = Z0; z < Z0 + 128; z++) for (let y = Y0; y < Y0 + 48; y++) {
    let b; try { b = dim.getBlock({ x, y, z }); } catch { continue; }
    if (b && b.typeId === "minecraft:water") {
      water++; const f = y - Y0 - 15; levels[f] = (levels[f] || 0) + 1;
      if (first.length < 12) first.push([x - X0, f, z - Z0, b.permutation.getState("liquid_depth")]);
    }
  }
  return { water, levels, first };
}
system.runTimeout(async () => {
  const dim = world.getDimension("overworld");
  log({ step: "ticking", r: cmd(dim, `tickingarea add 288 -64 288 447 320 447 palacedry true`) });
  for (let i = 0; i < 100; i++) { try { dim.getBlock({ x: X0, y: 100, z: Z0 }); dim.getBlock({ x: X0 + 127, y: 100, z: Z0 + 127 }); break; } catch { await sleep(20); } }
  cmd(dim, `fill ${X0 - 2} ${Y0 - 1} ${Z0 - 2} ${X0 + 129} ${Y0 - 1} ${Z0 + 129} stone`);
  const placed = [];
  for (const [q, [ox, oz]] of Object.entries(PIECES)) {
    try { world.structureManager.place(`pw:mvv_palace_${q}_a_r1`, dim, { x: X0 + ox, y: Y0, z: Z0 + oz }, { includeEntities: false }); placed.push(q); }
    catch (e) { placed.push(`${q}: ${String(e).slice(0, 80)}`); }
    await sleep(10);
  }
  log({ step: "placed", placed });
  let t = 0;
  for (const wait of [20, 180, 400, 600]) { await sleep(wait); t += wait; log({ step: "dry", t, r: read(dim) }); }
  log({ step: "DONE" });
}, 200);
'''


def build(out):
    out = Path(out)
    if out.exists():
        raise SystemExit(f"never rebuild {out}")
    (out / "scripts").mkdir(parents=True)
    (out / "scripts/main.js").write_text(MAIN)
    json.dump({"format_version": 2,
               "header": {"name": "PW palace dry probe 0.0.1 (BDS only)", "description": "the palace on dry ground: template or site?", "uuid": str(uuid.uuid4()),
                          "version": [0, 0, 1], "min_engine_version": [1, 21, 120]},
               "modules": [{"type": "script", "language": "javascript", "entry": "scripts/main.js", "uuid": str(uuid.uuid4()), "version": [0, 0, 1]},
                           {"type": "data", "uuid": str(uuid.uuid4()), "version": [0, 0, 1]}],
               "dependencies": [{"module_name": "@minecraft/server", "version": "2.3.0"}]}, open(out / "manifest.json", "w"), indent=1)
    print("built", out)


if __name__ == "__main__":
    build(sys.argv[1])
