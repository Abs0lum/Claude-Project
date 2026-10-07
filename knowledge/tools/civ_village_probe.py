#!/usr/bin/env python3
"""civ_village_probe.py — BDS-only probe of the BP-02 village command (never shipped).
Builds _build/<OUT> (a BP whose script drives BP-02's clock through /scriptevent and reads every building back through
the clock's pw:clock_bld events), then the harness runs it with BP-02 + Markers BP.
Checks, per building, at each read-back:
  * every cell of the finished building (all 13 manifests) at its turned position: block id, and EVERY state turned by
    this probe's own rotation math (direction vectors pushed through the BDS-measured rotXZ — independent of the clock's
    lookup tables)
  * every marker (fam / kind / n tags) and hatch lid (hinge turned) at its turned cell; entity count == manifest
  * the street: grass path count in front of the plot; leaves / logs left over the plot
  * the intermediate read (after 3 village days): which stages each plot reached (staggered starts)
Usage: civ_village_probe.py OUT_DIR"""
import json
import shutil
import sys
import uuid
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
from civ_pack import manifests_js  # noqa: E402

MAIN = r'''// villageprobe (BDS only): lay the village through BP-02's clock, skip days, verify every building.
import { world, system } from "@minecraft/server";
import { MANIFESTS } from "./civ_manifests.js";
const log = (o) => console.warn("[CIVTEST] " + JSON.stringify(o));
const sleep = (t) => new Promise((r) => system.runTimeout(r, t));
const O = { x: 300, z: 300 };
const blds = new Map();
const stls = [];
system.afterEvents.scriptEventReceive.subscribe((ev) => {
  if (ev.id === "pw:clock_bld") { const b = JSON.parse(ev.message); blds.set(b.id, b); }
  if (ev.id === "pw:clock_stl") { try { stls.push(JSON.parse(ev.message)); } catch { /* too long */ } }
});
// ---- this probe's own rotation math: positions by the measured rotXZ; directions as vectors pushed through rotXZ
function rotXZ(x, z, sx, sz, r) {
  if (r === 1) return [sz - 1 - z, x];
  if (r === 2) return [sx - 1 - x, sz - 1 - z];
  if (r === 3) return [z, sx - 1 - x];
  return [x, z];
}
const VEC = { north: [0, -1], south: [0, 1], west: [-1, 0], east: [1, 0] };
const nameOf = (v) => Object.keys(VEC).find((k) => VEC[k][0] === v[0] && VEC[k][1] === v[1]);
function turnVec(d, sx, sz, r) {                    // turn a direction by moving one step from a cell and back
  const [ax, az] = rotXZ(4, 4, sx, sz, r);
  const [bx, bz] = rotXZ(4 + VEC[d][0], 4 + VEC[d][1], sx, sz, r);
  return nameOf([bx - ax, bz - az]);
}
const FD = { 2: "north", 3: "south", 4: "west", 5: "east" };
const BEDD = { 0: "south", 1: "west", 2: "north", 3: "east" };
const inv = (m, v) => Number(Object.keys(m).find((k) => m[k] === v));
const PWK = { "pw:n": "north", "pw:e": "east", "pw:s": "south", "pw:w": "west" };
function want(states, sx, sz, r) {
  const o = {};
  for (const [k, v] of Object.entries(states)) {
    if (k === "minecraft:cardinal_direction") o[k] = turnVec(v, sx, sz, r);
    else if (k === "facing_direction" && FD[v]) o[k] = inv(FD, turnVec(FD[v], sx, sz, r));
    else if (k === "direction") o[k] = inv(BEDD, turnVec(BEDD[v], sx, sz, r));
    else if (k === "pillar_axis" && v !== "y") { const d = turnVec(v === "x" ? "east" : "south", sx, sz, r); o[k] = (d === "east" || d === "west") ? "x" : "z"; }
    else if (PWK[k]) { const d = turnVec(PWK[k], sx, sz, r); o[Object.keys(PWK).find((q) => PWK[q] === d)] = v; }
    else o[k] = v;
  }
  return o;
}
function verify(dim, b) {
  const man = MANIFESTS[b.family];
  const [sx, sy, sz] = man.size;
  const r = b.rot;
  const [fx, fz] = r % 2 ? [sz, sx] : [sx, sz];
  let cells = 0, badId = 0, badState = 0;
  const firstBad = [];
  for (let x = 0; x < sx; x++) for (let y = 0; y < sy; y++) for (let z = 0; z < sz; z++) {
    const k = man.idx[(x * sy + y) * sz + z];
    if (k < 0) continue;
    const [name, states] = man.pal[k];
    const [ox, oz] = rotXZ(x, z, sx, sz, r);
    const blk = dim.getBlock({ x: b.x + ox, y: b.y + y, z: b.z + oz });
    cells++;
    // the world lives: dirt greens over (grass spread), villagers leave doors / gates open, a closed shop has webs in its door
    const same = blk && (blk.typeId === name || (name === "minecraft:dirt" && blk.typeId === "minecraft:grass_block") ||
      (b.closed && blk.typeId === "minecraft:web" && name.includes("door")));
    if (!same) { badId++; if (firstBad.length < 6) firstBad.push([x, y, z, name, blk && blk.typeId]); continue; }
    if (blk.typeId !== name) continue;
    const w = want(states, sx, sz, r), g = blk.permutation.getAllStates();
    if (name.includes("door") || name.includes("gate") || name.includes("trapdoor")) delete w.open_bit;
    if (name === "minecraft:wheat" || name === "minecraft:farmland") { delete w.growth; delete w.moisturized_amount; }   // the fields are harvested and watered by the day
    const diff = Object.entries(w).filter(([q, v]) => (typeof g[q] === "boolean" ? g[q] !== Boolean(v) : g[q] !== v));
    if (diff.length) { badState++; if (firstBad.length < 6) firstBad.push([x, y, z, name, JSON.stringify(Object.fromEntries(diff)), JSON.stringify(g)]); }
  }
  const found = dim.getEntities({ location: { x: b.x, y: b.y, z: b.z }, volume: { x: fx, y: sy, z: fz } })
    .filter((e) => e.typeId === "pw:marker" || e.typeId === "pw:hatch_lid");
  const used = new Set(), missing = [];
  let lidBad = 0;
  for (const m of man.ents) {
    if (b.closed && m.id === "pw:marker" && m.fam === "station") continue;      // a closed shop's stations are gone by design
    const [ox, oz] = rotXZ(m.cell[0], m.cell[2], sx, sz, r);
    const at = { x: b.x + ox, y: b.y + m.cell[1] + man.datum_y, z: b.z + oz };
    const i = found.findIndex((e, j) => !used.has(j) && e.typeId === m.id && Math.floor(e.location.x) === at.x &&
      Math.floor(e.location.y) === at.y && Math.floor(e.location.z) === at.z &&
      (m.id !== "pw:marker" || (e.hasTag(`civ:kind:${m.kind}`) && e.hasTag(`civ:n:${m.n}`))));
    if (i < 0) { missing.push(`${m.fam || "lid"}:${m.kind || ""}#${m.n ?? ""}@${m.cell}`); continue; }
    used.add(i);
    if (m.id === "pw:hatch_lid" && found[i].getProperty("pw:hinge") !== (m.hinge + r) % 4) lidBad++;
  }
  // street in front + anything tree-like left above the box
  let path = 0, pathCells = 0, over = 0;
  const pathMiss = [];
  if (b.street) {
    const [a0, a1, row] = b.street;                 // [along0, along1, the street's row (x-axis streets) or column (z-axis)]
    const SURF = new Set(["minecraft:grass_path", "minecraft:gravel", "minecraft:cobblestone", "minecraft:spruce_planks"]);   // path -> gravel -> cobble; bridges
    for (let u = a0; u <= a1; u++) for (let w = 0; w < 3; w++) {
      const x = b.streetAxis === "z" ? row + w : u, z = b.streetAxis === "z" ? u : row + w;
      pathCells++;
      let hit = false;
      for (let y = b.y + man.datum_y - 6; y < b.y + man.datum_y + 4; y++) if (SURF.has(dim.getBlock({ x, y, z })?.typeId)) { path++; hit = true; break; }
      if (!hit && pathMiss.length < 4) { const tb = dim.getTopmostBlock({ x, z }); pathMiss.push([x, z, tb?.typeId, tb?.location.y]); }
    }
  }
  for (let i = 0; i < fx; i++) for (let j = 0; j < fz; j++) for (let y = b.y + sy; y < b.y + sy + 24; y++) {
    const t = dim.getBlock({ x: b.x + i, y, z: b.z + j })?.typeId || "";
    if (t.includes("leaves") || t.includes("log")) over++;
  }
  return { id: b.id, fam: b.family.replace("pw:mvv_", "").replace("_a_r1", ""), rot: r, at: [b.x, b.y + man.datum_y, b.z],
           stage: b.stage, turnedByClock: b.turned || 0, cells, badId, badState, ents: found.length, wantEnts: man.ents.length,
           missing: missing.slice(0, 6), nMissing: missing.length, lidBad, path, pathCells, pathMiss, over, firstBad,
           ok: badId === 0 && badState === 0 && missing.length === 0 && (b.closed || found.length === man.ents.length) && lidBad === 0 };
}
async function main() {
  const dim = world.getDimension("overworld");
  try { dim.runCommand("tickingarea add 270 -64 250 400 320 350 village true"); } catch (e) { log({ step: "tickingarea", err: String(e) }); }
  for (let i = 0; i < 60; i++) {
    let ok = true;
    for (const [x, z] of [[272, 252], [398, 348], [300, 300], [380, 260]]) { try { if (!dim.getBlock({ x, y: 64, z })) ok = false; } catch { ok = false; } }
    if (ok) break;
    await sleep(20);
  }
  dim.runCommand(`scriptevent pw:clock villageat ${O.x} ${O.z} 7`);          // seed 7: the skins are chosen per plot
  await sleep(10);
  dim.runCommand("scriptevent pw:clock pause");               // only the probe's skips move the village
  dim.runCommand("scriptevent pw:clock skip 3");
  await sleep(10);
  dim.runCommand("scriptevent pw:clock status");
  await sleep(5);
  log({ step: "after3", stages: [...blds.values()].map((b) => [b.id, b.family.replace("pw:mvv_", "").replace("_a_r1", ""), b.stage, b.pending.length]) });
  dim.runCommand("scriptevent pw:clock skip 30");
  await sleep(20);
  blds.clear();
  dim.runCommand("scriptevent pw:clock status");
  await sleep(5);
  let all = 0, okN = 0;
  for (const b of [...blds.values()].sort((p, q) => p.id - q.id)) {
    const r = verify(dim, b);
    all++; if (r.ok) okN++;
    log({ step: "bld", ...r });
  }
  // dump the village region (what the server built, terrain included) for the review render
  const bs = [...blds.values()];
  const x0 = Math.min(...bs.map((b) => b.x)) - 3, x1 = Math.max(...bs.map((b) => b.x + 17)) + 3;
  const z0 = Math.min(...bs.map((b) => b.z)) - 3, z1 = Math.max(...bs.map((b) => b.z + 17)) + 3;
  const y0 = Math.min(...bs.map((b) => b.y + 15)) - 7, y1 = Math.max(...bs.map((b) => b.y + MANIFESTS[b.family].size[1])) + 2;
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
    if (y % 4 === 0) await sleep(1);
  }
  for (let i = 0; i < pal.length; i += 40) console.warn(`[CIVPAL] ${i} ${JSON.stringify(pal.slice(i, i + 40))}`);
  log({ step: "dumped", pal: pal.length });
  // snapshot round trip: save, load (stages re-placed, old entities cleared first), verify one building's entities again
  dim.runCommand("scriptevent pw:clock snapshot save vp");
  await sleep(4);
  dim.runCommand("scriptevent pw:clock snapshot load vp");
  await sleep(20);
  blds.clear();
  dim.runCommand("scriptevent pw:clock status");
  await sleep(5);
  const again = [...blds.values()].map((b) => verify(dim, b));
  log({ step: "snapshot", ok: again.every((r) => r.ok), bad: again.filter((r) => !r.ok).map((r) => [r.fam, r.ents, r.wantEnts, r.badId, r.badState]) });
  log({ step: "summary", buildings: all, ok: okN });
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
    (out / "scripts/main.js").write_text(MAIN)
    json.dump({"format_version": 2,
               "header": {"name": "PW VillageProbe BP (BDS only)", "description": "drives the BP-02 village clock and verifies it",
                          "uuid": str(uuid.uuid4()), "version": [0, 0, 1], "min_engine_version": [1, 21, 120]},
               "modules": [{"type": "script", "language": "javascript", "entry": "scripts/main.js", "uuid": str(uuid.uuid4()), "version": [0, 0, 1]},
                           {"type": "data", "uuid": str(uuid.uuid4()), "version": [0, 0, 1]}],
               "dependencies": [{"module_name": "@minecraft/server", "version": "2.3.0"}]},
              open(out / "manifest.json", "w"), indent=1)
    print(out, len(mans))


if __name__ == "__main__":
    build(sys.argv[1])
