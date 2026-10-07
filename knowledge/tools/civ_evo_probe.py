#!/usr/bin/env python3
"""civ_evo_probe.py — BDS-only probe of the SETTLEMENT layer (V3) + ELEVATION handling (his 22:23) in BP-02 1.3.207.
Reuses civ_village_probe's verifier (rotation math, cell/marker/lid checks) and adds:
  * site choice: among candidate corners inside the ticking area, the one whose ground spans the most height over a
    village-sized footprint (a slope), so terraces, street steps and stoops are exercised
  * the evolution script: found (villageat) -> skip 20 -> skip 10 (village2 at 25) -> skip 40 (town at 60) -> skip 70
    (town2 at 120) -> decline on + skip 45 (two shops closed: webs, stations gone) -> immigrate (reopened) -> decline off
    -> immigrate (a newcomers' cottage) -> skip 80 (city at 200) -> skip 30 (all finished); after every step every FINISHED
    plot is verified cell by cell, and the settlement's streets / closures are tallied
  * elevation checks per finished plot: no air directly under any floor-slab cell of the footprint (terrace), the street
    segment in front has no step larger than one block, the door's front cell is reachable by one-block steps (stoop)
  * a region dump of the whole settlement for civ_dump_render
Usage: civ_evo_probe.py OUT_DIR"""
import json
import sys
import uuid
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
from civ_pack import manifests_js  # noqa: E402
import civ_village_probe as VP  # noqa: E402

HELPERS = VP.MAIN.split("async function main() {")[0]      # log, sleep, O, blds, rotXZ, want(), verify()

EVO = HELPERS + r'''
const NOT_GROUND = ["leaves", "log", "_wood", "grass", "fern", "flower", "vine", "snow_layer", "bush", "mushroom", "sapling", "roots",
  "propagule", "dandelion", "poppy", "tulip", "petals", "orchid", "allium", "bluet", "daisy", "cornflower", "lily", "rose", "peony",
  "lilac", "sunflower", "azalea", "berry", "dripleaf", "moss_carpet", "pumpkin", "melon", "cactus", "sugar_cane", "bamboo", "deadbush",
  "web", "torch", "pw:", "air"];
function groundY(dim, x, z) {
  try {
    let b = dim.getTopmostBlock({ x, z });
    for (let i = 0; b && i < 48; i++) {
      const id = b.typeId;
      if (!(NOT_GROUND.some((s) => id.includes(s))) || id.includes("grass_block") || id.includes("grass_path")) return b.location.y;   // "grass" caught grass_path: every yard read one too low (0.0.15)
      b = b.below();
    }
    return b ? b.location.y : undefined;
  } catch { return undefined; }
}
function siteRange(dim, x0, z0) {
  const hs = [];
  for (let x = x0; x < x0 + 80; x += 4) for (let z = z0 - 20; z < z0 + 24; z += 4) { const g = groundY(dim, x, z); if (g !== undefined) hs.push(g); }
  if (hs.length < 20) return null;
  hs.sort((a, b) => a - b);
  return { lo: hs[0], hi: hs[hs.length - 1], range: hs[hs.length - 1] - hs[0], water: 0 };
}
function elevationChecks(dim, b) {
  const man = MANIFESTS[b.family];
  const [sx, sy, sz] = man.size;
  const r = b.rot;
  const [fx, fz] = r % 2 ? [sz, sx] : [sx, sz];
  const slab = b.y + man.datum_y - 1;
  let floating = 0;                                  // the wall ring only: inside it a cellar is air under the floor by design
  for (let i = 0; i < fx; i++) for (let j = 0; j < fz; j++) {
    if (!(i === 0 || j === 0 || i === fx - 1 || j === fz - 1)) continue;
    const under = dim.getBlock({ x: b.x + i, y: slab - 1, z: b.z + j });
    const at = dim.getBlock({ x: b.x + i, y: slab, z: b.z + j });
    if (at && at.typeId !== "minecraft:air" && under && under.typeId === "minecraft:air") floating++;
  }
  let bigStep = 0, steps = 0;
  const bigAt = [];
  if (b.street) {
    const [a0, a1, row] = b.street;                 // along the street's middle row / column (axis-aware since the two-axis planner)
    let prev, pu;
    const SURF = new Set(["minecraft:grass_path", "minecraft:gravel", "minecraft:cobblestone", "minecraft:spruce_planks"]);
    for (let u = a0; u <= a1; u++) {
      const x = b.streetAxis === "z" ? row + 1 : u, z = b.streetAxis === "z" ? u : row + 1;
      const g = groundY(dim, x, z);
      const onStreet = g !== undefined && SURF.has(dim.getBlock({ x, y: g, z })?.typeId);      // the tuple reaches one cell past the plot: beyond the street's end is not the street
      if (!onStreet) { prev = undefined; continue; }
      if (prev !== undefined) { if (Math.abs(g - prev) > 1) { bigStep++; if (bigAt.length < 3) bigAt.push([x, z, prev, g]); } else if (g !== prev) steps++; }
      prev = g; pu = u;
    }
  }
  // the door's front cell: climb from the street row to the slab by <= 1-block steps along the door column
  let stoopOk = true;
  const doorEnt = (man.ents || []).find((m) => m.fam === "station" && m.kind === "door");     // the table's door cell (run 0.0.14: the middle column was a false alarm on cottage_l)
  const door = doorEnt ? doorEnt.cell : [0, 0, Math.floor(sz / 2)];
  const cells = [];
  for (let k = 1; k <= 5; k++) { const [ox, oz] = rotXZ(-k, door[2], sx, sz, r); cells.push({ x: b.x + ox, z: b.z + oz }); }
  let y = slab;
  for (const c of cells) {
    const g = groundY(dim, c.x, c.z);
    if (g === undefined) break;
    if (g > y + 1 || g < y - 1) { if (g < y - 1) stoopOk = false; }
    y = g;
    if (g <= slab - 1 && Math.abs(g - slab) <= 1) break;
  }
  return { floating, bigStep, steps, stoopOk, bigAt, stoopCells: stoopOk ? null : cells.map((c) => [c.x, c.z, groundY(dim, c.x, c.z)]) };
}
const SURF = new Set(["minecraft:grass_path", "minecraft:gravel", "minecraft:cobblestone", "minecraft:spruce_planks"]);
/** the GS-1 gate (D-C505): every street body cell of every settlement vs its profile — the lay model: run cells lay the
 *  3-wide body on the far side of the key; jog cells a centred cross; a run's first cell after a jog both; square cells
 *  are the square's. Returns per-settlement counts + the first bad cells. */
function bodyGate(dim) {
  const out = { cells: 0, ok: 0, nearMiss: 0, bad: 0, unloaded: 0, first: [] };   // nearMiss: a street surface one above / below (two keys' shapes overlap at a smooth step)
  for (const st of stls) {
    const axis = st.axis || "x";
    const runs = [];
    for (const s of st.streets || []) for (const r of s.runs || []) runs.push(r);
    const isRun = (kx, kz) => runs.some((r) => axis === "z" ? (r.z === kx && kz >= r.x0 && kz <= r.x1) : (r.z === kz && kx >= r.x0 && kx <= r.x1));
    const has = (x, z) => st.profile && st.profile[`${x},${z}`] !== undefined;
    const sq = st.square ? [st.square.x, st.square.x + 11, st.square.z, st.square.z + 11] : null;
    const inSquare = (x, z) => sq && x >= sq[0] && x <= sq[1] && z >= sq[2] && z <= sq[3];
    const seen = new Set();
    for (const key of Object.keys(st.profile || {})) {
      const [kx, kz] = key.split(",").map(Number);
      const h = st.profile[key];
      const run = isRun(kx, kz);
      const behind = axis === "z" ? [[kx - 1, kz - 1], [kx, kz - 1], [kx + 1, kz - 1]] : [[kx - 1, kz - 1], [kx - 1, kz], [kx - 1, kz + 1]];
      const predRun = axis === "z" ? isRun(kx, kz - 1) && has(kx, kz - 1) : isRun(kx - 1, kz) && has(kx - 1, kz);
      const turn = run && !predRun && behind.some(([bx, bz]) => has(bx, bz));
      const shapes = [];
      for (let w = 0; w < 3; w++) {
        if (run) shapes.push(axis === "z" ? [kx + w, kz] : [kx, kz + w]); else shapes.push(axis === "z" ? [kx, kz + w - 1] : [kx + w - 1, kz]);
      }
      if (turn) for (let w = 0; w < 3; w++) shapes.push(axis === "z" ? [kx, kz + w - 1] : [kx + w - 1, kz]);
      for (const [x, z] of shapes) {
        const k2 = `${x},${z}`;
        if (seen.has(k2) || inSquare(x, z)) continue;
        seen.add(k2);
        out.cells++;
        let top;
        try { const b = dim.getBlock({ x, y: h, z }); top = b ? b.typeId : "?"; } catch { out.unloaded++; continue; }
        if (SURF.has(top)) { out.ok++; continue; }
        let near = false;
        for (const dy of [-1, 1]) { try { const b2 = dim.getBlock({ x, y: h + dy, z }); if (b2 && SURF.has(b2.typeId)) near = true; } catch {} }
        if (near) { out.nearMiss++; continue; }
        out.bad++;
        if (out.first.length < 8) out.first.push([st.id, x, z, h, top.replace("minecraft:", "")]);
      }
    }
  }
  return out;
}
async function tally(dim) {
  const bs = [...blds.values()].sort((p, q) => p.id - q.id);
  let ok = 0; const bad = [], elev = { floating: 0, bigStep: 0, steps: 0, stoopBad: 0 }, detail = [], unloaded = [];
  for (const b of bs) {
    if (b.stage < 4) continue;
    await sleep(1);                                   // one plot per tick: the script watchdog interrupts a long tick
    let r, e;
    try { r = verify(dim, b); e = elevationChecks(dim, b); } catch (err) { unloaded.push([b.id, b.x, b.z, String(err).slice(0, 60)]); continue; }   // a plot beyond the ticking areas
    if (r.ok) ok++; else bad.push([b.family, r.rot, r.badId, r.badState, r.nMissing, r.ents, r.wantEnts, r.firstBad.slice(0, 2)]);
    elev.floating += e.floating; elev.bigStep += e.bigStep; elev.steps += e.steps; if (!e.stoopOk) elev.stoopBad++;
    if ((e.floating || e.bigStep || !e.stoopOk) && detail.length < 14) detail.push({ id: b.id, fam: b.family.replace("pw:mvv_", ""), at: [b.x, b.y + 15, b.z], rot: b.rot, street: b.street, axis: b.streetAxis, stl: b.settlement, floating: e.floating, bigStep: e.bigStep, bigAt: e.bigAt, stoop: e.stoopCells });
  }
  elev.detail = detail; elev.unloaded = unloaded.slice(0, 6); elev.nUnloaded = unloaded.length;
  const ys = bs.filter((b) => b.settled !== false).map((b) => b.y + 15);
  return { plots: bs.length, finished: bs.filter((b) => b.stage >= 4).length, verifiedOk: ok, bad: bad.slice(0, 6),
           streetsZ: [...new Set(bs.map((b) => b.street ? b.street[2] : "?"))].sort((a, c) => a - c),
           closed: bs.filter((b) => b.closed).map((b) => b.family.replace("pw:mvv_", "")), floorRange: ys.length ? [Math.min(...ys), Math.max(...ys)] : null, elev,
           stateBytes: stls.length ? stls[0].stateBytes : null };
}
async function readback(dim) { blds.clear(); stls.length = 0; dim.runCommand("scriptevent pw:clock status"); await sleep(6); }
async function main() {
  const dim = world.getDimension("overworld");
  // one ticking area may hold at most 100 chunks: 160 x 160 blocks (x 230..389, z 230..389); the city (3 streets, 90 wide) fits
  let ta;
  // chunk-aligned 10 x 10 chunks (x 240..399, z 240..399): the limit is 100 chunks per area
  try { ta = dim.runCommand("tickingarea add 240 -64 240 399 320 399 village true"); } catch (e) { log({ step: "tickingarea", err: String(e) }); }
  log({ step: "tickingarea", result: ta ? ta.successCount : "thrown" });
  for (let i = 0; i < 150; i++) {
    let ok = true;
    for (const [x, z] of [[242, 242], [398, 398], [320, 320], [250, 390], [390, 250]]) { try { if (!dim.getBlock({ x, y: 64, z })) ok = false; } catch { ok = false; } }
    if (ok) break;
    await sleep(20);
  }
  const areas = new Set();                                  // daughter sites get their own ticking area (chunk-aligned 10 x 10)
  const areaFor = (x, z) => {
    const ax = Math.floor((x - 80) / 16) * 16, az = Math.floor((z - 80) / 16) * 16;
    const key = `${ax},${az}`;
    if (areas.has(key)) return;
    areas.add(key);
    try { const r = dim.runCommand(`tickingarea add ${ax} -64 ${az} ${ax + 159} 320 ${az + 159} d${areas.size} true`); log({ step: "tickingarea2", at: [ax, az], result: r.successCount }); } catch (e) { log({ step: "tickingarea2", err: String(e) }); }
  };
  // the site: the candidate corner with the most relief over a village footprint (the settlement grows +-26 z and +90 x)
  const cands = [];
  for (let x = 252; x <= 292; x += 20) for (let z = 294; z <= 334; z += 20) { const r = siteRange(dim, x, z); if (r) cands.push({ x, z, ...r }); }
  cands.sort((a, b) => b.range - a.range);
  const site = cands.find((c) => c.range >= 5 && c.range <= 16) || cands[0] || { x: 300, z: 300, range: "?" };
  log({ step: "site", chosen: site, candidates: cands.slice(0, 6) });
  dim.runCommand(`scriptevent pw:clock villageat ${site.x} ${site.z} 7`);
  await sleep(10);
  dim.runCommand("scriptevent pw:clock pause");
  // founding reads the land as a job: wait until the settlement reports itself built (plots handed out)
  let founded = null;
  for (let i = 0; i < 60 && !founded; i++) {
    await sleep(20);
    stls.length = 0;
    dim.runCommand("scriptevent pw:clock status");
    await sleep(4);
    founded = stls.find((x) => x.phase === "built" || x.planned === false);
  }
  log({ step: "founded", phase: founded ? founded.phase : "timeout", planned: founded ? founded.planned : null, square: founded ? founded.square : null,
        h0: founded ? founded.h0 : null, streets: founded ? founded.streets.map((st) => ({ kind: st.kind, runs: st.runs ? st.runs.map((r) => [r.x0, r.x1, r.z]) : null, laid: st.laid, nCells: st.nCells })) : null,
        siteKnown: founded ? founded.siteKnown : null, missed: founded ? founded.missed : null, log: founded ? founded.log : null });
  if (founded && founded.square) for (const [dx, dz] of [[-100, -100], [60, -100], [-100, 60], [60, 60]]) areaFor(founded.square.x + 6 + dx, founded.square.z + 6 + dz);
  const steps = [["skip 6", "first plots finished"], ["skip 14", "village building"], ["skip 10", "village2 at 25 (+4)"], ["skip 40", "town at 60 (+6)"], ["skip 70", "town2 at 120 (+7)"],
                 ["decline on 1", "declining"], ["skip 45", "2 shops closed"], ["immigrate cottage_s 1", "one reopened"], ["decline off 1", "recovering"],
                 ["immigrate cottage_s 1", "newcomers' cottage"], ["skip 80", "city at 200 (+11)"], ["skip 30", "all finished"],
                 ["skip 40", "daughter settlers (prosperous 30 days, pop >= 24)"], ["skip 40", "daughter built + road"], ["skip 30", "trade along the road"]];
  const seen = new Map();                                   // plot id -> badId at its first finished tally (degradation tracer)
  for (const [cmd, expect] of steps) {
    dim.runCommand(`scriptevent pw:clock ${cmd}`);
    await sleep(40);
    await readback(dim);
    for (const x of stls) if (x.daughter) {
      areaFor(x.daughter.x, x.daughter.z);
      // the corridor between the two squares: the road job needs loaded ground all the way (chunk-aligned boxes along the line)
      const sq = x.square ? { x: x.square.x + 6, z: x.square.z + 6 } : null;
      if (sq) areaFor(Math.round((sq.x + x.daughter.x) / 2), Math.round((sq.z + x.daughter.z) / 2));      // one midpoint box: 80 + 80 + 80 covers up to 230
    }
    // a daughter reads her land once her chunks tick: wait for her (up to 120 s) before the next step
    if (stls.some((x) => x.mother && x.phase === "reading")) {
      for (let i = 0; i < 60; i++) { await sleep(40); await readback(dim); if (!stls.some((x) => x.mother && x.phase === "reading")) break; }
      log({ step: "daughter", built: stls.filter((x) => x.mother).map((x) => [x.name, x.phase, x.siteKnown, x.square, x.streets.length]) });
    }
    const stl = stls.find((x) => !x.mother) || stls[stls.length - 1];
    const t = await tally(dim);
    const degraded = [];
    for (const b of [...blds.values()]) {
      if (b.stage < 4) continue;
      await sleep(1);
      const r = verify(dim, b);
      const prev = seen.get(b.id);
      if (prev === undefined) seen.set(b.id, r.badId);
      else if (r.badId > prev) { degraded.push([b.id, b.family.replace("pw:mvv_", ""), prev, r.badId, r.firstBad.slice(0, 2)]); seen.set(b.id, r.badId); }
    }
    const body = bodyGate(dim);
    log({ step: "evo", cmd, expect, ...t, degraded, body, tier: stl ? stl.tier : null, population: stl ? stl.population : null, ledger: stl ? stl.ledger : null,
          nStreets: stl ? stl.streets.length : null, chronicle: stl ? stl.log : null,
          settlements: stls.map((x) => ({ id: x.id, name: x.name, phase: x.phase, tier: x.tier, pop: x.population, plots: [...blds.values()].filter((b) => b.settlement === x.id).length,
                                           roads: x.roads, daughter: x.daughter, wall: x.wall ? x.wall.blocks : null, docks: x.docks ? x.docks.cells : null, siteKnown: x.siteKnown })) });
  }
  // every plot's box (for the overlap / tracer analysis)
  for (const x of stls) if (x.profile) log({ step: "profile", id: x.id, axis: x.axis, n: Object.keys(x.profile).length, keys: Object.entries(x.profile).map(([k, h]) => `${k}:${h}`).join(" ") });   // the street keys, for dump reads
  log({ step: "plots", plots: [...blds.values()].sort((p, q) => p.id - q.id).map((b) => { const m = MANIFESTS[b.family]; const [fx, fz] = b.rot % 2 ? [m.size[2], m.size[0]] : [m.size[0], m.size[2]];
        return [b.id, b.family.replace("pw:mvv_", ""), b.x, b.y + 15, b.z, b.rot, fx, fz, b.street ? b.street[2] : null, b.stage, b.closed ? 1 : 0, b.onSquare ? 1 : 0]; }) });
  dim.runCommand("scriptevent pw:clock laylog");           // the instrumented clock (bp02-211-laylog) prints its per-cell lay log; others ignore it
  await sleep(10);
  const bs = [...blds.values()];
  const x0 = Math.min(...bs.map((b) => b.x)) - 3, x1 = Math.max(...bs.map((b) => b.x + 17)) + 3;
  const z0 = Math.min(...bs.map((b) => b.z)) - 3, z1 = Math.max(...bs.map((b) => b.z + 17)) + 3;
  const y0 = Math.min(...bs.map((b) => b.y + 15)) - 9, y1 = Math.max(...bs.map((b) => b.y + MANIFESTS[b.family].size[1])) + 2;
  const pal = [], pk = new Map();
  log({ step: "dumphead", x0, x1, z0, z1, y0, y1 });
  for (let y = y0; y <= y1; y++) {
    const runs = [];
    let last = -2, n = 0;
    for (let x = x0; x <= x1; x++) for (let z = z0; z <= z1; z++) {
      const blk = dim.getBlock({ x, y, z });
      let k = -1;
      if (blk && blk.typeId !== "minecraft:air") {
        const key = blk.typeId + JSON.stringify(blk.permutation.getAllStates());
        if (!pk.has(key)) { pk.set(key, pal.length); pal.push([blk.typeId, blk.permutation.getAllStates()]); }
        k = pk.get(key);
      }
      if (k === last) n++; else { if (n) runs.push(n > 1 ? `${last}*${n}` : `${last}`); last = k; n = 1; }
    }
    runs.push(n > 1 ? `${last}*${n}` : `${last}`);
    const s = runs.join(",");
    for (let i = 0; i < s.length; i += 3000) console.warn(`[CIVDUMP] ${y} ${i} ${s.slice(i, i + 3000)}`);
    if (y % 2 === 0) await sleep(1);
  }
  for (let i = 0; i < pal.length; i += 40) console.warn(`[CIVPAL] ${i} ${JSON.stringify(pal.slice(i, i + 40))}`);
  log({ step: "dumped", pal: pal.length });
  log({ step: "DONE" });
}
system.runTimeout(() => { main().catch((e) => console.warn("[CIVTEST] " + JSON.stringify({ step: "main", err: String(e), st: e.stack }))); }, 100);
'''


def build(out):
    out = Path(out)
    if out.exists():
        raise SystemExit(f"never rebuild {out}")
    (out / "scripts").mkdir(parents=True)
    js, mans = manifests_js("/home/claude/_staging/civ")
    (out / "scripts/civ_manifests.js").write_text(js)
    (out / "scripts/main.js").write_text(EVO)
    json.dump({"format_version": 2,
               "header": {"name": "PW EvoProbe BP (BDS only)", "description": "settlement tiers + elevation handling, read back",
                          "uuid": str(uuid.uuid4()), "version": [0, 0, 1], "min_engine_version": [1, 21, 120]},
               "modules": [{"type": "script", "language": "javascript", "entry": "scripts/main.js", "uuid": str(uuid.uuid4()), "version": [0, 0, 1]},
                           {"type": "data", "uuid": str(uuid.uuid4()), "version": [0, 0, 1]}],
               "dependencies": [{"module_name": "@minecraft/server", "version": "2.3.0"}]},
              open(out / "manifest.json", "w"), indent=1)
    print(out, len(mans))


if __name__ == "__main__":
    build(sys.argv[1])
