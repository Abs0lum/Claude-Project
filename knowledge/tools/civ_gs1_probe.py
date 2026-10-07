#!/usr/bin/env python3
"""civ_gs1_probe.py — GS-1 (D-C500, open): two street body cells in the forest village (settlement 3 of evo run 0.0.17,
square (55, 60)) read a gravel surface ONE BELOW the profile with no fill under them, while their key cell is right.
This probe founds a village at that same square directly (villageat 61 66 — the flattest-knoll search is deterministic
on the pristine seed) and, after founding and after each clock step, compares EVERY street body cell's real surface
with the profile height: a timeline of mismatches tells WHEN the cells go wrong (the lay at founding, the hardening at
village2, a later street, a road …). Job-only, BDS; never shipped.
Usage: civ_gs1_probe.py _build/gs1probe-0.0.1  (then tools/bds_civtest.py --seconds 600 _build/bp02-209 _build/gs1probe-0.0.1)"""
import json
import sys
import uuid
from pathlib import Path

JS = r'''
import { world, system } from "@minecraft/server";
const log = (o) => console.warn("[CIVTEST] " + JSON.stringify(o));
const sleep = (t) => new Promise((r) => system.runTimeout(r, t));
const stls = [];
system.afterEvents.scriptEventReceive.subscribe((ev) => { if (ev.id === "pw:clock_stl") { try { stls.push(JSON.parse(ev.message)); } catch {} } });
const SURF = new Set(["minecraft:grass_path", "minecraft:gravel", "minecraft:cobblestone", "minecraft:spruce_planks"]);
function stack(dim, x, z, y0, y1) {
  const out = [];
  for (let y = y0; y <= y1; y++) { try { const b = dim.getBlock({ x, y, z }); if (b && b.typeId !== "minecraft:air") out.push(b.typeId.replace("minecraft:", "") + "@" + y); } catch { out.push("?@" + y); } }
  return out.join(" ");
}
/** every body cell of the settlement's streets vs the land — the LAY model: a RUN cell (inside a run's x0..x1 at the
 *  run's key row / column) is 3 wide on the far side of the key (the slot law); any other profile cell is a JOG cell,
 *  3 wide centred across its travel */
function checkBody(dim, st) {
  const axis = st.axis || "x";
  const runs = [];
  for (const s of st.streets || []) for (const r of s.runs || []) runs.push(r);
  const isRun = (kx, kz) => runs.some((r) => axis === "z" ? (r.z === kx && kz >= r.x0 && kz <= r.x1) : (r.z === kz && kx >= r.x0 && kx <= r.x1));
  // the square's own cells are the square's (levelled to its median, paved after the street): a street cross reaching
  // into the square's border row is the kerb between street and square, not a street defect
  const sq = st.square ? [st.square.x, st.square.x + 11, st.square.z, st.square.z + 11] : null;
  const inSquare = (x, z) => sq && x >= sq[0] && x <= sq[1] && z >= sq[2] && z <= sq[3];
  const bad = [], seen = new Set();
  let n = 0, ok = 0, jogCells = 0, squareCells = 0;
  for (const key of Object.keys(st.profile || {})) {
    const [kx, kz] = key.split(",").map(Number);
    const h = st.profile[key];
    const run = isRun(kx, kz);
    if (!run) jogCells++;
    // a run's first cell after a jog lays body + cross: its predecessor along the run is not a run key, and a jog key
    // lies behind it (straight behind or diagonal — runs are walked in increasing z (axis z) / x (axis x))
    const has = (x, z) => st.profile[`${x},${z}`] !== undefined;
    const behind = axis === "z" ? [[kx - 1, kz - 1], [kx, kz - 1], [kx + 1, kz - 1]] : [[kx - 1, kz - 1], [kx - 1, kz], [kx - 1, kz + 1]];
    const predRun = axis === "z" ? isRun(kx, kz - 1) && has(kx, kz - 1) : isRun(kx - 1, kz) && has(kx - 1, kz);
    const turn = run && !predRun && behind.some(([bx, bz]) => has(bx, bz));
    const shapes = [];
    for (let w = 0; w < 3; w++) {
      if (run) shapes.push(axis === "z" ? [kx + w, kz] : [kx, kz + w]);
      else shapes.push(axis === "z" ? [kx, kz + w - 1] : [kx + w - 1, kz]);
    }
    if (turn) for (let w = 0; w < 3; w++) shapes.push(axis === "z" ? [kx, kz + w - 1] : [kx + w - 1, kz]);
    for (let si = 0; si < shapes.length; si++) {
      const [x, z] = shapes[si], w = si % 3;
      const k2 = `${x},${z}`;
      if (seen.has(k2)) continue;
      seen.add(k2);
      if (inSquare(x, z)) { squareCells++; continue; }
      n++;
      let top;
      try { const b = dim.getBlock({ x, y: h, z }); top = b ? b.typeId : "?"; } catch { top = "unloaded"; }
      if (SURF.has(top)) { ok++; continue; }
      if (bad.length < 40) bad.push({ at: [x, z], w, key: [kx, kz], h, atH: top.replace("minecraft:", ""), stack: stack(dim, x, z, h - 3, h + 2) });
    }
  }
  return { cells: n, ok, jogKeys: jogCells, squareCells, bad };
}
async function status(dim) { stls.length = 0; dim.runCommand("scriptevent pw:clock status"); await sleep(6); return stls[0]; }
async function main() {
  const dim = world.getDimension("overworld");
  const AX = __AX__, AZ = __AZ__;                                   // the ticking area: 10 x 10 chunks from (AX, AZ)
  try { dim.runCommand(`tickingarea add ${AX} -64 ${AZ} ${AX + 159} 320 ${AZ + 159} gs1 true`); } catch (e) { log({ step: "ta", err: String(e) }); }
  for (let i = 0; i < 150; i++) {
    let ok = true;
    for (const [x, z] of [[AX + 2, AZ + 2], [AX + 158, AZ + 158], [AX + 80, AZ + 80], [AX + 8, AZ + 152], [AX + 152, AZ + 8]]) { try { if (!dim.getBlock({ x, y: 64, z })) ok = false; } catch { ok = false; } }
    if (ok) break;
    await sleep(20);
  }
  dim.runCommand("scriptevent pw:clock villageat __CX__ __CZ__ 7");
  await sleep(10);
  dim.runCommand("scriptevent pw:clock pause");
  let st = null;
  for (let i = 0; i < 60 && !(st && (st.phase === "built" || st.planned === false)); i++) { await sleep(20); st = await status(dim); }
  if (!st) { log({ step: "DONE", err: "no settlement" }); return; }
  log({ step: "founded", square: st.square, h0: st.h0, axis: st.axis, streets: (st.streets || []).map((s) => ({ kind: s.kind, axis: s.axis, laid: s.laid, nCells: s.nCells, runs: s.runs ? s.runs.map((r) => [r.x0, r.x1, r.z]) : null })), log: st.log });
  // the profile of the main street, as keys sorted (the forest village of 0.0.17: keys (39,30..33) 98, (39,34..38) 97)
  const keys = Object.keys(st.profile || {}).map((k) => k.split(",").map(Number).concat(st.profile[k])).sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  log({ step: "profile", n: keys.length, keys: keys.slice(0, 120) });
  log({ step: "body", when: "after founding", ...checkBody(dim, st) });
  for (const cmd of ["skip 6", "skip 14", "skip 10", "skip 40", "skip 70"]) {
    dim.runCommand(`scriptevent pw:clock ${cmd}`);
    await sleep(60);
    st = await status(dim);
    if (!st) continue;
    log({ step: "body", when: `after ${cmd} (day ${st.founded !== undefined ? "+" : ""}${cmd.split(" ")[1]}, tier ${st.tier})`, streets: (st.streets || []).length, ...checkBody(dim, st) });
  }
  log({ step: "DONE" });
}
system.run(() => main().catch((e) => log({ step: "DONE", err: String(e), stack: String(e.stack).slice(0, 300) })));   // never in early execution
'''


def build(out, cx=61, cz=66, ax=-48, az=-32):
    """cx, cz = the villageat point (default: the forest village's square centre of run 0.0.17); ax, az = the
    chunk-aligned corner of the 160 x 160 ticking area (default: the box around it)"""
    out = Path(out)
    if out.exists():
        raise SystemExit(f"never rebuild {out}")
    (out / "scripts").mkdir(parents=True)
    js = JS.replace("__CX__", str(int(cx))).replace("__CZ__", str(int(cz))).replace("__AX__", str(int(ax))).replace("__AZ__", str(int(az)))
    (out / "scripts/main.js").write_text(js)
    json.dump({"format_version": 2,
               "header": {"name": "PW GS1Probe BP (BDS only)", "description": "GS-1: street body cells vs the profile, as a timeline",
                          "uuid": str(uuid.uuid4()), "version": [0, 0, 1], "min_engine_version": [1, 21, 120]},
               "modules": [{"type": "script", "language": "javascript", "entry": "scripts/main.js", "uuid": str(uuid.uuid4()), "version": [0, 0, 1]}],
               "dependencies": [{"module_name": "@minecraft/server", "version": "2.3.0"}]},
              open(out / "manifest.json", "w"), indent=1)
    print(out)


if __name__ == "__main__":
    build(sys.argv[1], *[int(a) for a in sys.argv[2:6]])
