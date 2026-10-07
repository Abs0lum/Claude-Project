#!/usr/bin/env python3
"""cascadetest_probe.py — D-C573 "move it": does a pond drained through a 1-wide lip into a stepped stone cascade, a basin
and a drop shaft to a sewer trench STAY FINITE (no new source blocks anywhere on the path) and leave the pond's level
where it was? A 24 x 24 pond (sources, surface y 130) on a terrace; a dam on its east side to y 131 with a 1-wide lip at
y 130; a race of steps down to a basin at y 118 (rim 119); a 1 x 1 drop shaft from the basin's far side to a trench at
y 110 running 40 cells to an open outfall. Reads every 200 ticks to 2,000: sources and flowing cells on the path, pond
sources, basin / trench / outfall water.
Variants: C1 as described · C2 the race 2 wide (two sources could meet?) · C3 a source block set in the basin (a fountain
jet) · C4 the trench closed at the outfall (does the trench fill and back up?)
Usage: cascadetest_probe.py OUT_DIR → bds_civtest.py --seconds 900 OUT_DIR"""
import json
import sys
import uuid
from pathlib import Path

MAIN = r'''
import { world, system } from "@minecraft/server";
const log = (o) => console.warn("[CIVTEST] " + JSON.stringify(o));
const sleep = (t) => new Promise((r) => system.runTimeout(r, t));
const cmd = (dim, s) => { try { return dim.runCommand(s).successCount; } catch (e) { return "ERR " + String(e).slice(0, 60); } };
const X0 = 300, Z0 = 300;                       // pond west edge; everything runs east (+x)
const PS = 130;                                 // pond surface cell
async function loaded(dim) { for (let i = 0; i < 100; i++) { try { dim.getBlock({ x: X0 - 8, y: 100, z: Z0 - 8 }); dim.getBlock({ x: X0 + 120, y: 100, z: Z0 + 32 }); return i; } catch { await sleep(20); } } return -1; }
function scan(dim, x0, y0, z0, x1, y1, z1) {
  let src = 0, flow = 0;
  for (let x = x0; x <= x1; x++) for (let y = y0; y <= y1; y++) for (let z = z0; z <= z1; z++) {
    let b; try { b = dim.getBlock({ x, y, z }); } catch { continue; }
    if (b && b.typeId === "minecraft:water") { const d = b.permutation.getState("liquid_depth"); if (d === 0) src++; else flow++; }
  }
  return [src, flow];
}
async function site(dim, v) {
  // clear and floor
  cmd(dim, `fill ${X0 - 4} 100 ${Z0 - 4} ${X0 + 115} 140 ${Z0 + 28} air`);
  for (let y = 100; y <= 108; y++) cmd(dim, `fill ${X0 - 4} ${y} ${Z0 - 4} ${X0 + 115} ${y} ${Z0 + 28} stone`);
  // the terrace under the pond (y 109..124 solid), the pond basin walls
  for (let y = 109; y <= 124; y++) cmd(dim, `fill ${X0 - 2} ${y} ${Z0 - 2} ${X0 + 26} ${y} ${Z0 + 26} stone`);
  for (let y = 125; y <= 131; y++) { cmd(dim, `fill ${X0 - 2} ${y} ${Z0 - 2} ${X0 + 25} ${y} ${Z0 + 26} stone`); }
  for (let y = 125; y <= PS; y++) cmd(dim, `fill ${X0} ${y} ${Z0} ${X0 + 23} ${y} ${Z0 + 23} water`);
  // the dam = the east wall at x X0+24..25 up to 131; the lip: 1 (or 2) wide at y PS, z 12
  const w = v === "C2" ? 2 : 1;
  cmd(dim, `fill ${X0 + 24} ${PS} ${Z0 + 12} ${X0 + 25} ${PS} ${Z0 + 11 + w} air`);
  // the race: steps east from x X0+26, each step 4 long and 2 down, 1 (or 2) wide, walled both sides
  let x = X0 + 26, y = PS - 1;
  while (y > 119) {
    cmd(dim, `fill ${x} ${y - 1} ${Z0 + 10} ${x + 3} ${y + 2} ${Z0 + 13 + w} stone`);
    cmd(dim, `fill ${x} ${y} ${Z0 + 12} ${x + 3} ${y + 2} ${Z0 + 11 + w} air`);
    x += 4; y -= 2;
  }
  // the basin: 7 x 7, floor 117, rim 119 (inside air 118..119), fed at its west side
  cmd(dim, `fill ${x} 117 ${Z0 + 8} ${x + 8} 120 ${Z0 + 16} stone`);
  cmd(dim, `fill ${x + 1} 118 ${Z0 + 9} ${x + 7} 120 ${Z0 + 15} air`);
  cmd(dim, `fill ${x} ${y} ${Z0 + 12} ${x} ${y + 2} ${Z0 + 11 + w} air`);
  if (v === "C3") cmd(dim, `setblock ${x + 4} 119 ${Z0 + 12} water`);
  // the drop shaft at the basin's far side: 1 x 1 from 117 down to the trench at 110
  const sx = x + 7, sz = Z0 + 12;
  cmd(dim, `fill ${sx} 110 ${sz} ${sx} 117 ${sz} air`);
  // the trench: 1 wide, floor 109, from the shaft 40 east; outfall open (air beyond) or closed (C4)
  cmd(dim, `fill ${sx} 110 ${sz} ${sx + 40} 111 ${sz} air`);
  if (v !== "C4") cmd(dim, `fill ${sx + 41} 100 ${sz - 3} ${sx + 50} 111 ${sz + 3} air`);   // the outfall drops into a pit
  return { lipX: X0 + 24, basin: [x, Z0 + 8], shaft: [sx, sz] };
}
system.runTimeout(async () => {
  const dim = world.getDimension("overworld");
  log({ step: "ticking", r: cmd(dim, `tickingarea add ${X0 - 16} -64 ${Z0 - 16} ${X0 + 127} 320 ${Z0 + 31} cascade true`) });
  await sleep(100); log({ step: "loaded", waited: await loaded(dim) });
  for (const v of ["C1", "C2", "C3", "C4"]) {
    const s = await site(dim, v);
    const pond0 = scan(dim, X0, 125, Z0, X0 + 23, PS, Z0 + 23);
    const rows = [];
    for (let t = 200; t <= 2000; t += 200) {
      await sleep(200);
      const pond = scan(dim, X0, 125, Z0, X0 + 23, PS + 1, Z0 + 23);
      const path = scan(dim, X0 + 24, 109, Z0 + 8, s.shaft[0] + 50, 131, Z0 + 16);
      rows.push({ t, pond, path });
    }
    log({ step: "cascade", v, site: s, pond0, rows });
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
               "header": {"name": "PW cascade test probe 0.0.1 (BDS only)", "description": "pond -> lip -> cascade -> basin -> shaft -> trench", "uuid": str(uuid.uuid4()),
                          "version": [0, 0, 1], "min_engine_version": [1, 21, 120]},
               "modules": [{"type": "script", "language": "javascript", "entry": "scripts/main.js", "uuid": str(uuid.uuid4()), "version": [0, 0, 1]},
                           {"type": "data", "uuid": str(uuid.uuid4()), "version": [0, 0, 1]}],
               "dependencies": [{"module_name": "@minecraft/server", "version": "2.3.0"}]}, open(out / "manifest.json", "w"), indent=1)
    print("built", out)


if __name__ == "__main__":
    build(sys.argv[1])
