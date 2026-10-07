#!/usr/bin/env python3
"""filltest_probe.py — a 10-minute BDS experiment (10-05 10:5x, run 13: `/fill … air [] replace water` ran from the clock
with no exception and changed nothing): which /fill syntax removes standing water from a script, what successCount says,
and how big a volume one call takes. The probe holds a ticking area, lays a 64 x 64 x 6 pool of water sources, then tries
each syntax on a fresh pool and reads the water back. Prints [CIVTEST] JSON lines and DONE.
Usage: filltest_probe.py OUT_DIR  → run with bds_civtest.py --seconds 400 OUT_DIR"""
import json
import sys
import uuid
from pathlib import Path

MAIN = r'''
import { world, system } from "@minecraft/server";
const log = (o) => console.warn("[CIVTEST] " + JSON.stringify(o));
const sleep = (t) => new Promise((r) => system.runTimeout(r, t));
const X0 = 300, Z0 = 300, Y0 = 120, W = 64, D = 64, HGT = 6;        // the pool: above any terrain
function cmd(dim, s) { try { const r = dim.runCommand(s); return { ok: true, n: r.successCount }; } catch (e) { return { ok: false, err: String(e).slice(0, 160) }; } }
function count(dim, x0, y0, z0, x1, y1, z1, step = 4) {
  let water = 0, flowing = 0, air = 0, other = 0, miss = 0;
  for (let x = x0; x <= x1; x += step) for (let z = z0; z <= z1; z += step) for (let y = y0; y <= y1; y++) {
    let id; try { id = dim.getBlock({ x, y, z })?.typeId; } catch { id = undefined; }
    if (id === undefined) miss++; else if (id === "minecraft:water") water++; else if (id === "minecraft:flowing_water") flowing++; else if (id === "minecraft:air") air++; else other++;
  }
  return { water, flowing, air, other, miss };
}
async function pool(dim) {
  // a solid floor, then water sources
  cmd(dim, `fill ${X0} ${Y0 - 1} ${Z0} ${X0 + W - 1} ${Y0 - 1} ${Z0 + D - 1} stone`);
  const rs = [];
  for (let y = Y0; y < Y0 + HGT; y++) rs.push(cmd(dim, `fill ${X0} ${y} ${Z0} ${X0 + W - 1} ${y} ${Z0 + D - 1} water`));
  await sleep(40);
  return rs;
}
system.runTimeout(async () => {
  const dim = world.getDimension("overworld");
  log({ step: "ticking", r: cmd(dim, `tickingarea add ${X0 - 16} -64 ${Z0 - 16} ${X0 + W + 15} 320 ${Z0 + D + 15} pool true`) });
  await sleep(100);
  const tests = [
    ["A air [] replace water, 7-layer slab", `fill ${X0} ${Y0} ${Z0} ${X0 + W - 1} ${Y0 + 6} ${Z0 + D - 1} air [] replace water`],
    ["B air replace water (no states token)", `fill ${X0} ${Y0} ${Z0} ${X0 + W - 1} ${Y0 + 6} ${Z0 + D - 1} air replace water`],
    ["C air replace minecraft:water", `fill ${X0} ${Y0} ${Z0} ${X0 + W - 1} ${Y0 + 6} ${Z0 + D - 1} air replace minecraft:water`],
    ["D air (no filter), 7 layers", `fill ${X0} ${Y0} ${Z0} ${X0 + W - 1} ${Y0 + 6} ${Z0 + D - 1} air`],
    ["E air replace water, 32768 exactly (8 layers)", `fill ${X0} ${Y0} ${Z0} ${X0 + W - 1} ${Y0 + 7} ${Z0 + D - 1} air replace water`],
    ["F air replace water, 1 layer", `fill ${X0} ${Y0} ${Z0} ${X0 + W - 1} ${Y0} ${Z0 + D - 1} air replace water`],
    ["G air replace water, 16x16x6 (1536)", `fill ${X0} ${Y0} ${Z0} ${X0 + 15} ${Y0 + 5} ${Z0 + 15} air replace water`],
  ];
  for (const [name, c] of tests) {
    const laid = await pool(dim);
    const before = count(dim, X0, Y0, Z0, X0 + W - 1, Y0 + HGT - 1, Z0 + D - 1);
    const r = cmd(dim, c);
    await sleep(5);
    const after = count(dim, X0, Y0, Z0, X0 + W - 1, Y0 + HGT - 1, Z0 + D - 1);
    await sleep(40);
    const later = count(dim, X0, Y0, Z0, X0 + W - 1, Y0 + HGT - 1, Z0 + D - 1);
    log({ step: "fill", name, cmd: c, laid: laid.map((q) => q.n ?? q.err), result: r, before, after, later });
    cmd(dim, `fill ${X0} ${Y0} ${Z0} ${X0 + W - 1} ${Y0 + HGT - 1} ${Z0 + D - 1} air`);
    cmd(dim, `fill ${X0} ${Y0} ${Z0} ${X0 + W - 1} ${Y0 + HGT - 1} ${Z0 + D - 1} air`);
    await sleep(20);
  }
  // the script API's own fill, if present
  try {
    const laid = await pool(dim);
    const before = count(dim, X0, Y0, Z0, X0 + W - 1, Y0 + HGT - 1, Z0 + D - 1);
    const mod = await import("@minecraft/server");
    const BV = mod.BlockVolume;
    const vol = new BV({ x: X0, y: Y0, z: Z0 }, { x: X0 + W - 1, y: Y0 + 6, z: Z0 + D - 1 });
    const res = dim.fillBlocks(vol, "minecraft:air", { ignoreChunkBoundErrors: true, blockFilter: { includeTypes: ["minecraft:water", "minecraft:flowing_water"] } });
    await sleep(5);
    const after = count(dim, X0, Y0, Z0, X0 + W - 1, Y0 + HGT - 1, Z0 + D - 1);
    log({ step: "fillBlocks", laid: laid.map((q) => q.n ?? q.err), capacity: res && res.getCapacity ? res.getCapacity() : null, before, after });
  } catch (e) { log({ step: "fillBlocks", err: String(e).slice(0, 200) }); }
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
               "header": {"name": "PW fill test probe 0.0.1 (BDS only)", "description": "/fill replace water from a script", "uuid": str(uuid.uuid4()),
                          "version": [0, 0, 1], "min_engine_version": [1, 21, 120]},
               "modules": [{"type": "script", "language": "javascript", "entry": "scripts/main.js", "uuid": str(uuid.uuid4()), "version": [0, 0, 1]},
                           {"type": "data", "uuid": str(uuid.uuid4()), "version": [0, 0, 1]}],
               "dependencies": [{"module_name": "@minecraft/server", "version": "2.3.0"}]}, open(out / "manifest.json", "w"), indent=1)
    print("built", out)


if __name__ == "__main__":
    build(sys.argv[1])
