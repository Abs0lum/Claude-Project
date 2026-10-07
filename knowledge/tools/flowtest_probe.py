#!/usr/bin/env python3
"""flowtest_probe.py — does `/fill … air replace flowing_water` (or `replace water`) remove FLOWING / FALLING water? (run 16's
pumps matched nothing while the sampler read thousands of water cells). A source column pours from y 126 into a dry stone
box (floor y 117, walls to 122); after 100 ticks the box holds falling + flowing water; each filter is tried on a fresh box.
Usage: flowtest_probe.py OUT_DIR → bds_civtest.py --seconds 300 OUT_DIR"""
import json
import sys
import uuid
from pathlib import Path

MAIN = r'''
import { world, system } from "@minecraft/server";
const log = (o) => console.warn("[CIVTEST] " + JSON.stringify(o));
const sleep = (t) => new Promise((r) => system.runTimeout(r, t));
const BX0 = 320, BZ0 = 320, BW = 24, BF = 117, TOP = 122;
const BX1 = BX0 + BW - 1, BZ1 = BZ0 + BW - 1;
const cmd = (dim, s) => { try { const r = dim.runCommand(s); return r.successCount; } catch (e) { return "ERR " + String(e).slice(0, 80); } };
function count(dim) {
  const st = {};
  let water = 0, flowing = 0, air = 0, miss = 0;
  for (let x = BX0 + 1; x <= BX1 - 1; x++) for (let z = BZ0 + 1; z <= BZ1 - 1; z++) for (let y = BF + 1; y <= TOP + 4; y++) {
    let b; try { b = dim.getBlock({ x, y, z }); } catch { b = undefined; }
    if (!b) { miss++; continue; }
    const id = b.typeId;
    if (id === "minecraft:water") water++; else if (id === "minecraft:flowing_water") flowing++; else if (id === "minecraft:air") air++;
    if (id.includes("water")) { const k = id + JSON.stringify(b.permutation.getAllStates()); st[k] = (st[k] || 0) + 1; }
  }
  return { water, flowing, air, miss, states: st };
}
async function loaded(dim) { for (let i = 0; i < 100; i++) { try { dim.getBlock({ x: BX0 - 8, y: BF, z: BZ0 - 8 }); dim.getBlock({ x: BX1 + 8, y: BF, z: BZ1 + 8 }); return i; } catch { await sleep(20); } } return -1; }
async function box(dim) {
  cmd(dim, `fill ${BX0 - 2} ${BF - 1} ${BZ0 - 2} ${BX1 + 2} ${TOP + 12} ${BZ1 + 2} air`);
  cmd(dim, `fill ${BX0} ${BF} ${BZ0} ${BX1} ${BF} ${BZ1} stone`);
  for (const [x0, z0, x1, z1] of [[BX0, BZ0, BX0, BZ1], [BX1, BZ0, BX1, BZ1], [BX0, BZ0, BX1, BZ0], [BX0, BZ1, BX1, BZ1]]) cmd(dim, `fill ${x0} ${BF} ${z0} ${x1} ${TOP} ${z1} stone`);
  // the spring: a 2 x 2 pool of sources on a ledge above the box, spilling over its edge into the box
  cmd(dim, `fill ${BX0 + 10} ${TOP + 5} ${BZ0 + 10} ${BX0 + 13} ${TOP + 5} ${BZ0 + 13} stone`);
  cmd(dim, `fill ${BX0 + 11} ${TOP + 6} ${BZ0 + 11} ${BX0 + 12} ${TOP + 6} ${BZ0 + 12} water`);
  await sleep(100);
}
system.runTimeout(async () => {
  const dim = world.getDimension("overworld");
  log({ step: "ticking", r: cmd(dim, `tickingarea add ${BX0 - 24} -64 ${BZ0 - 24} ${BX1 + 24} 320 ${BZ1 + 24} flow true`) });
  await sleep(100); log({ step: "loaded", waited: await loaded(dim) });
  const tests = [["F1 replace flowing_water", `air replace flowing_water`], ["F2 replace water", `air replace water`], ["F3 replace water then flowing_water", null], ["F4 plain air", `air`]];
  for (const [name, tail] of tests) {
    await box(dim);
    const before = count(dim);
    let r;
    if (tail) r = cmd(dim, `fill ${BX0 + 1} ${BF + 1} ${BZ0 + 1} ${BX1 - 1} ${TOP} ${BZ1 - 1} ${tail}`);
    else r = [cmd(dim, `fill ${BX0 + 1} ${BF + 1} ${BZ0 + 1} ${BX1 - 1} ${TOP} ${BZ1 - 1} air replace water`), cmd(dim, `fill ${BX0 + 1} ${BF + 1} ${BZ0 + 1} ${BX1 - 1} ${TOP} ${BZ1 - 1} air replace flowing_water`)];
    await sleep(2); const after = count(dim);
    log({ step: "flow", name, r, before: { water: before.water, flowing: before.flowing, states: before.states }, after: { water: after.water, flowing: after.flowing, states: after.states } });
  }
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
               "header": {"name": "PW flow test probe 0.0.1 (BDS only)", "description": "/fill replace on flowing water", "uuid": str(uuid.uuid4()),
                          "version": [0, 0, 1], "min_engine_version": [1, 21, 120]},
               "modules": [{"type": "script", "language": "javascript", "entry": "scripts/main.js", "uuid": str(uuid.uuid4()), "version": [0, 0, 1]},
                           {"type": "data", "uuid": str(uuid.uuid4()), "version": [0, 0, 1]}],
               "dependencies": [{"module_name": "@minecraft/server", "version": "2.3.0"}]}, open(out / "manifest.json", "w"), indent=1)
    print("built", out)


if __name__ == "__main__":
    build(sys.argv[1])
