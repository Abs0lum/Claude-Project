#!/usr/bin/env python3
"""laketest_probe.py — his 12:12 CT 10-05: "a series of smaller, faster tests to definitely discover how to remove water".
A lake 6 deep (sources, surface cell y 120) over a 96 x 96 stone floor; a 32 x 32 BOX sunk in it with its floor 3 below the
surface (as the palace block stands at the harness site). Variants, each on a freshly re-laid lake, each read back after
5 / 100 / 400 ticks (water cells inside the box interior):
  V0 no wall (control)
  V1 wall in the box's EDGE column, top = the surface cell (y 120)
  V2 wall in the edge column, top = surface + 1 (y 121)             <- his guess
  V3 wall in the MARGIN column outside the box, top = surface
  V4 wall in the margin column, top = surface + 1
  V5 the upgrade order: edge wall to 121, drain, then margin wall to 121, then the edge wall removed (air), drain again
  V6 V2 but the box drained in two halves 60 ticks apart (regrowth across the seam)
  V7 V2 with two 1 x 2 doorways cut through the wall at the surface level (the palace's front doors) — do they leak?
Usage: laketest_probe.py OUT_DIR  → bds_civtest.py --seconds 600 OUT_DIR"""
import json
import sys
import uuid
from pathlib import Path

MAIN = r'''
import { world, system } from "@minecraft/server";
const log = (o) => console.warn("[CIVTEST] " + JSON.stringify(o));
const sleep = (t) => new Promise((r) => system.runTimeout(r, t));
const RX0 = 300, RZ0 = 300, RW = 96;                                  // the lake region
const YF = 114, YS = 120;                                             // the floor, the surface cell (water 115..120)
const BX0 = 332, BZ0 = 332, BW = 32;                                  // the box
const BF = 117;                                                       // the box's floor slab (stone); interior water 118..120
const cmd = (dim, s) => { try { const r = dim.runCommand(s); return r.successCount; } catch (e) { return "ERR " + String(e).slice(0, 80); } };
const X1 = RX0 + RW - 1, Z1 = RZ0 + RW - 1, BX1 = BX0 + BW - 1, BZ1 = BZ0 + BW - 1;
function count(dim) {
  let water = 0, flowing = 0, air = 0, miss = 0;
  for (let x = BX0 + 1; x <= BX1 - 1; x++) for (let z = BZ0 + 1; z <= BZ1 - 1; z++) for (let y = BF + 1; y <= YS + 2; y++) {
    let id; try { id = dim.getBlock({ x, y, z })?.typeId; } catch { id = undefined; }
    if (id === undefined) miss++; else if (id === "minecraft:water") water++; else if (id === "minecraft:flowing_water") flowing++; else if (id === "minecraft:air") air++;
  }
  return { water, flowing, air, miss };
}
async function loaded(dim) {                                          // the fresh world generates its chunks slowly: wait for all corners
  for (let i = 0; i < 100; i++) {
    let ok = true;
    for (const [x, z] of [[RX0, RZ0], [X1, RZ0], [RX0, Z1], [X1, Z1], [BX0 + 16, BZ0 + 16]]) { try { dim.getBlock({ x, y: YF, z }); } catch { ok = false; } }
    if (ok) return i;
    await sleep(20);
  }
  return -1;
}
async function lake(dim) {
  const w = await loaded(dim);
  const r = [cmd(dim, `fill ${RX0} ${YF} ${RZ0} ${X1} ${YF} ${Z1} stone`)];
  for (let y = YF + 1; y <= YS; y++) r.push(cmd(dim, `fill ${RX0} ${y} ${RZ0} ${X1} ${y} ${Z1} water`));
  r.push(cmd(dim, `fill ${RX0} ${YS + 1} ${RZ0} ${X1} ${YS + 3} ${Z1} air`));
  r.push(cmd(dim, `fill ${BX0} ${BF} ${BZ0} ${BX1} ${BF} ${BZ1} stone_bricks`));     // the box's slab
  for (let y = BF + 1; y <= YS; y++) r.push(cmd(dim, `fill ${BX0} ${y} ${BZ0} ${BX1} ${y} ${BZ1} water`));   // the box full of the lake
  await sleep(40);
  log({ step: "lake", waited: w, fills: r, box: count(dim) });
}
function ring(dim, x0, z0, x1, z1, top, block) {                        // four faces only (no lid): the palace's retaining wall
  cmd(dim, `fill ${x0} ${BF} ${z0} ${x0} ${top} ${z1} ${block}`); cmd(dim, `fill ${x1} ${BF} ${z0} ${x1} ${top} ${z1} ${block}`);
  cmd(dim, `fill ${x0} ${BF} ${z0} ${x1} ${top} ${z0} ${block}`); cmd(dim, `fill ${x0} ${BF} ${z1} ${x1} ${top} ${z1} ${block}`);
}
function wallEdge(dim, top) { ring(dim, BX0, BZ0, BX1, BZ1, top, "stone_bricks"); }
function wallMargin(dim, top) { ring(dim, BX0 - 1, BZ0 - 1, BX1 + 1, BZ1 + 1, top, "stone_bricks"); }
function drain(dim, x0 = BX0, x1 = BX1) { const r = []; for (let y = BF + 1; y <= YS + 2; y++) { r.push(cmd(dim, `fill ${x0} ${y} ${BZ0} ${x1} ${y} ${BZ1} air replace water`)); r.push(cmd(dim, `fill ${x0} ${y} ${BZ0} ${x1} ${y} ${BZ1} air replace flowing_water`)); } return r; }
async function read(dim, name, extra) {
  await sleep(5); const t5 = count(dim);
  await sleep(95); const t100 = count(dim);
  await sleep(300); const t400 = count(dim);
  log({ step: "variant", name, t5, t100, t400, extra: extra || null });
}
system.runTimeout(async () => {
  const dim = world.getDimension("overworld");
  log({ step: "ticking", r: cmd(dim, `tickingarea add ${RX0 - 16} -64 ${RZ0 - 16} ${X1 + 16} 320 ${Z1 + 16} lake true`) });
  await sleep(100);
  // V0 control
  await lake(dim); const c0 = count(dim); drain(dim); await read(dim, "V0 no wall", { before: c0 });
  // V1 edge wall to the surface
  await lake(dim); wallEdge(dim, YS); drain(dim); await read(dim, "V1 edge wall top = surface");
  // V2 edge wall to surface + 1
  await lake(dim); wallEdge(dim, YS + 1); drain(dim); await read(dim, "V2 edge wall top = surface+1");
  // V3 margin wall to the surface
  await lake(dim); wallMargin(dim, YS); drain(dim); await read(dim, "V3 margin wall top = surface");
  // V4 margin wall to surface + 1
  await lake(dim); wallMargin(dim, YS + 1); drain(dim); await read(dim, "V4 margin wall top = surface+1");
  // V5 the upgrade order: edge wall, drain, margin wall, remove the edge wall, drain
  await lake(dim); wallEdge(dim, YS + 1); drain(dim); await sleep(20); wallMargin(dim, YS + 1); await sleep(5);
  ring(dim, BX0, BZ0, BX1, BZ1, YS + 1, "air"); drain(dim); await read(dim, "V5 upgrade: edge -> margin, edge removed");
  // V6 two halves 60 ticks apart
  await lake(dim); wallEdge(dim, YS + 1); drain(dim, BX0, BX0 + BW / 2 - 1); await sleep(60); const mid = count(dim); drain(dim, BX0 + BW / 2, BX1); await read(dim, "V6 edge wall +1, two halves 60 ticks apart", { afterFirstHalf: mid });
  // V7 doorways in the edge wall at the surface level
  await lake(dim); wallEdge(dim, YS + 1); cmd(dim, `fill ${BX0} ${YS - 1} ${BZ0 + 10} ${BX0} ${YS} ${BZ0 + 10} air`); cmd(dim, `fill ${BX0} ${YS - 1} ${BZ0 + 20} ${BX0} ${YS} ${BZ0 + 20} air`); drain(dim); await read(dim, "V7 edge wall +1 with two 1x2 doorways at the surface");
  // V8 like V7 but the doorways are DOORS (closed spruce doors)
  await lake(dim); wallEdge(dim, YS + 1); cmd(dim, `fill ${BX0} ${YS - 1} ${BZ0 + 10} ${BX0} ${YS} ${BZ0 + 10} air`); cmd(dim, `setblock ${BX0} ${YS - 1} ${BZ0 + 10} spruce_door`); drain(dim); await read(dim, "V8 edge wall +1 with one closed door");
  // V9 what does a partial drain leave, and does `replace flowing_water` / `replace water` catch it? (run 16: 3805 sampled
  //    water cells, and 40 fill commands matched nothing)
  await lake(dim); wallEdge(dim, YS + 1);
  cmd(dim, `fill ${BX0 + 1} ${YS} ${BZ0 + 1} ${BX1 - 1} ${YS} ${BZ1 - 1} air replace water`);   // the top layer only
  await sleep(60); const partial = count(dim);
  const states = {};
  for (let x = BX0 + 1; x <= BX1 - 1; x += 3) for (let z = BZ0 + 1; z <= BZ1 - 1; z += 3) for (let y = BF + 1; y <= YS + 1; y++) {
    let b; try { b = dim.getBlock({ x, y, z }); } catch { b = undefined; }
    if (b && b.typeId.includes("water")) { const k = b.typeId + " " + JSON.stringify(b.permutation.getAllStates()); states[k] = (states[k] || 0) + 1; }
  }
  const rFlow = cmd(dim, `fill ${BX0 + 1} ${BF + 1} ${BZ0 + 1} ${BX1 - 1} ${YS + 1} ${BZ1 - 1} air replace flowing_water`);
  await sleep(2); const afterFlow = count(dim);
  const rWat = cmd(dim, `fill ${BX0 + 1} ${BF + 1} ${BZ0 + 1} ${BX1 - 1} ${YS + 1} ${BZ1 - 1} air replace water`);
  await sleep(2); const afterWat = count(dim);
  const rAll = cmd(dim, `fill ${BX0 + 1} ${BF + 1} ${BZ0 + 1} ${BX1 - 1} ${YS + 1} ${BZ1 - 1} air`);
  await sleep(2); const afterAll = count(dim);
  log({ step: "variant", name: "V9 partial drain, then replace flowing_water / water / plain air", partial, states, rFlow, afterFlow, rWat, afterWat, rAll, afterAll });
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
               "header": {"name": "PW lake test probe 0.0.1 (BDS only)", "description": "walls vs a lake: how to remove water for good", "uuid": str(uuid.uuid4()),
                          "version": [0, 0, 1], "min_engine_version": [1, 21, 120]},
               "modules": [{"type": "script", "language": "javascript", "entry": "scripts/main.js", "uuid": str(uuid.uuid4()), "version": [0, 0, 1]},
                           {"type": "data", "uuid": str(uuid.uuid4()), "version": [0, 0, 1]}],
               "dependencies": [{"module_name": "@minecraft/server", "version": "2.3.0"}]}, open(out / "manifest.json", "w"), indent=1)
    print("built", out)


if __name__ == "__main__":
    build(sys.argv[1])
