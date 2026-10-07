#!/usr/bin/env python3
"""kit_village_probe.py — BDS probe of the STREETKIT VILLAGE (BP-02 1.3.219): found a village on a slope, let the street
queue drain, skip days until the first plots finish, grow to town (widening, park, side street), and read back:
  * every settlement: kit streets (role, length, ramps, bridges, tees, access pieces, outfall exits), queue, chronicle
  * every finished building verified cell by cell against the 219 templates (doors + sewer ports included)
  * FLUSH: for each kit plot, the corridor cell in front of its door (w 0) holds the verge / sidewalk at the plot's H
  * ACCESS: the street's gallery cells at the shaft (y = H - 14 + 3..5 at w 0 / 12) are open, and the house's port cells
  * KEEPERS: villagers tagged civ:keeper, their distance to their shop's station at noon (work hours)
  * a region dump (CIVDUMP) of the whole settlement for tools/civ_topmap.py
Usage: kit_village_probe.py OUT_PROBE_DIR  (then: bds_civtest.py --seconds 1500 BP02 MARKERS OUT_PROBE_DIR)"""
import json
import sys
import uuid
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
import mcstructure as M  # noqa: E402

SHORT = Path("/tmp/claude-0/-home-claude/c0a4a7ef-9c52-560d-ac77-bcf688f4b3d2/scratchpad/evoshort/scripts")
BP219 = Path("/home/claude/_build/bp02-219")


def manifests():
    """the probe's manifests: the 218 ones (entities, datum) with palette + cells re-read from the 219 templates"""
    t = (SHORT / "civ_manifests.js").read_text()
    j = json.loads(t[t.index("{"):t.rindex("}") + 1])
    # 0.0.26d (the probe crashed on the MANOR — a 219 family the 218 manifests never had): every staged 219 family the
    # 218 list lacks is added from its staged manifest (name, size, datum_y; entities -> ents)
    for mf in sorted(Path("/home/claude/_staging/civ/manifests").glob("*.json")):
        fam = "pw:" + mf.stem
        if fam in j or not (BP219 / "structures/pw" / (mf.stem + ".mcstructure")).exists():
            continue
        sm = json.loads(mf.read_text())
        j[fam] = {"name": sm.get("name", fam), "size": sm["size"], "datum_y": sm.get("datum_y", 0), "ents": sm.get("entities", [])}
    for fam, m in j.items():
        st = M.Structure.from_bytes((BP219 / "structures/pw" / (fam.split(":")[1] + ".mcstructure")).read_bytes())
        pal, key, idx = [], {}, []
        for k in st.layer0:
            if k < 0:
                idx.append(-1)
                continue
            n, states, _ = st.palette[k]
            plain = {a: (bool(v.value) if a.endswith("_bit") else v.value) for a, v in states.items()}
            kk = json.dumps([n, plain], sort_keys=True)
            if kk not in key:
                key[kk] = len(pal)
                pal.append([n, plain])
            idx.append(key[kk])
        if list(st.size) != m["size"]:
            raise SystemExit(f"{fam}: size {st.size} != {m['size']}")
        m["pal"], m["idx"] = pal, idx
    return f"// kit_village_probe.py: {len(j)} manifests, cells re-read from BP-02 1.3.219\nexport const MANIFESTS = " + json.dumps(j, separators=(",", ":")) + ";\n"


HEAD = (SHORT / "main.js").read_text().split("async function readback(dim)")[0]
# the helper part stops before tally(); keep verify() and the rotation helpers only
HEAD = HEAD.split("function tally(")[0] if "function tally(" in HEAD else HEAD
HEAD = HEAD.rstrip()
# the legacy verifier walks b.street as [along0, along1, row]; a kit plot's b.street is [street id, t, side] — skip it there
assert HEAD.count("  if (b.street) {") >= 1
HEAD = HEAD.replace("  if (b.street) {", "  if (b.street && !b.kit) {")
assert HEAD.count('import { world, system') == 1
HEAD = HEAD.replace('import { world, system } from "@minecraft/server";', 'import { world, system, BlockPermutation } from "@minecraft/server";')
if HEAD.endswith("async"):
    HEAD = HEAD[:-5]

MAIN = r'''
const roads = new Map();                                      // road id -> { cells, H, dirs, turns, ramps, n }
system.afterEvents.scriptEventReceive.subscribe((ev) => {
  if (ev.id !== "pw:clock_road") return;
  try {
    const part = JSON.parse(ev.message);
    const r = roads.get(part.id) || { cells: [], H: [], dirs: [], turns: part.turns, ramps: part.ramps, n: part.n };
    for (let k = 0; k < part.cells.length; k++) { r.cells[part.i + k] = part.cells[k]; r.H[part.i + k] = part.H[k]; r.dirs[part.i + k] = part.dirs[k]; }
    roads.set(part.id, r);
  } catch (e) { log({ step: "road_part", err: String(e) }); }
});
async function readback(dim) { blds.clear(); stls.length = 0; roads.clear(); dim.runCommand("scriptevent pw:clock status"); await sleep(6); }
/** D-C534 §2.3: every narrow road — grade, surface, kerbs, ramps, elbows */
function roadChecks(dim) {
  const out = [];
  const DIRS4 = [[1, 0], [0, 1], [-1, 0], [0, -1]];
  for (const [id, r] of roads) {
    const n = r.cells.length;
    let surf = 0, kerb = 0, ramp = 0, rampBad = [], maxStep = 0, missing = 0, badSurf = [];
    const rampAt = new Map();
    for (const [ra, dir] of r.ramps) for (let q = 0; q < 4; q++) rampAt.set(dir > 0 ? ra + q : ra + 3 + q, dir > 0 ? q + 1 : 4 - q);
    const turnSet = new Set(r.turns);
    for (let i = 0; i < n; i++) {
      if (!r.cells[i]) { missing++; continue; }
      const [x, z] = r.cells[i], H = r.H[i], d = DIRS4[r.dirs[i]], p = [-d[1], d[0]];
      if (i > 0 && r.cells[i - 1]) maxStep = Math.max(maxStep, Math.abs(H - r.H[i - 1]));
      const read = (xx, yy, zz) => { let b; try { b = dim.getBlock({ x: xx, y: yy, z: zz }); } catch { return "?"; } return b ? b.typeId : "?"; };
      const s = read(x, H, z);
      if (s === "minecraft:cobblestone") surf++; else if (badSurf.length < 6) badSurf.push([i, x, H, z, s.replace("minecraft:", "")]);
      if (!turnSet.has(i)) {
        const k1 = read(x + p[0] * 3, H + 1, z + p[1] * 3), k2 = read(x - p[0] * 3, H + 1, z - p[1] * 3);
        if (k1 === "minecraft:cobblestone_wall" || k2 === "minecraft:cobblestone_wall") kerb++;
      }
      const q = rampAt.get(i);
      if (q) { const rb = read(x, H + 1, z); if (rb === `pw:ramp_cobble_4_q${q}`) ramp++; else if (rampBad.length < 4) rampBad.push([i, x, H + 1, z, rb, q]); }
    }
    out.push({ id, n, missing, surf, kerb, ramps: rampAt.size, rampOk: ramp, rampBad, maxStep, turns: r.turns.length, badSurf });
  }
  return out;
}
async function waitQueue(dim, label, maxLoops = 90) {
  let q = -1;
  for (let i = 0; i < maxLoops; i++) {
    await readback(dim);
    const st = stls[0];
    q = st ? st.kitQueue : -1;
    if (st && q === 0 && !(st.lag > 0)) break;                 // 0.0.13: skipped days run one per beat (s.lag)
    await sleep(40);
  }
  log({ step: "queue", label, left: q });
}
function kitChecks(dim) {
  // flush + access per kit plot
  const out = { flush: 0, flushBad: [], access: 0, accessBad: [], port: 0, portBad: [] };
  for (const b of blds.values()) {
    if (!b.kit || b.stage < 0) continue;
    const man = MANIFESTS[b.family];
    const [sx, , sz] = man.size;
    const H = b.kit.H;
    // the door: local (0, feet, doorZ) -> the cell in front: local x -1
    const door = man.door || null;
    // front cell = local (-1, z) for every z of the frontage: the corridor's outer cell (w 0 or 12): verge (grass) / sidewalk at H
    let bad = 0;
    for (let z = 0; z < sz; z++) {
      const [ox, oz] = rotXZ(-1, z, sx, sz, b.rot);
      const blk = dim.getBlock({ x: b.x + ox, y: H, z: b.z + oz });
      const above = dim.getBlock({ x: b.x + ox, y: H + 1, z: b.z + oz });
      const ok = blk && ["minecraft:grass_block", "minecraft:smooth_stone", "minecraft:dirt", "minecraft:stone_brick_stairs"].includes(blk.typeId) && above && above.typeId === "minecraft:air";
      if (!ok) { bad++; if (out.flushBad.length < 8) out.flushBad.push([b.id, z, blk && blk.typeId, above && above.typeId, b.x + ox, H, b.z + oz]); }
    }
    if (!bad) out.flush++;
    if (b.kit.shaftT === null || b.kit.shaftT === undefined) continue;
    // the shaft's street-side opening: local (0, 3..4) open in the house, (-1, 3..5) open in the street piece
    const zc = (MANIFESTS[b.family].shaftZ !== undefined) ? MANIFESTS[b.family].shaftZ : null;
    let shaftZ = null;
    for (let z = 0; z < sz; z++) { const k = man.idx[(1 * man.size[1] + 3) * sz + z]; if (k >= 0 && man.pal[k][0] === "minecraft:ladder") { shaftZ = z; break; } }
    void zc;
    if (shaftZ === null) continue;
    const cells = [];
    for (const [lx, ly] of [[0, 3], [0, 4], [-1, 3], [-1, 4], [-1, 5]]) {
      const [ox, oz] = rotXZ(lx, shaftZ, sx, sz, b.rot);
      const blk = dim.getBlock({ x: b.x + ox, y: b.y + ly, z: b.z + oz });
      cells.push(blk ? blk.typeId.replace("minecraft:", "") : "?");
    }
    const open = cells.every((c) => c === "air");
    if (open) out.access++; else if (out.accessBad.length < 10) out.accessBad.push([b.id, b.family.replace("pw:mvv_", ""), b.stage, cells]);
  }
  // D-C534 §2: the land rule per plot (kind / cut / fill from the slot, the bench cells and stilts from the prep)
  out.land = [...blds.values()].filter((b) => b.kit).map((b) => [b.id, b.family.replace("pw:mvv_", "").replace(/_r1$/, ""), b.land ? b.land.kind : "?", b.land ? b.land.cut : "?", b.land ? b.land.fill : "?", b.bench ?? null, b.stilts || null]);
  out.landRejects = stls[0] ? [stls[0].landRejects || 0, stls[0].landLast || null] : null;
  return out;
}
function markers(dim) {
  // Markers BP 0.2.3: every marker hidden (pw:vis false) and without its hit box (the hide event removes pw:hittable)
  let n = 0, vis = 0;
  for (const e of dim.getEntities({ type: "pw:marker" })) { n++; try { if (e.getProperty("pw:vis") === true) vis++; } catch { /* no property */ } }
  return { n, vis };
}
/** D-C533: the sewer's water. Per kit street: every t sampled — the trench cell (w6) at y H-13..H-11 (H read from the
 *  sidewalk's top block at w1); wet = a water source there. The well: its shaft column (water from y1 to y14 of its box)
 *  and the drain cells. Outfalls: the block in the exit space and the two cells beyond it (does the water get out?). */
function sewerChecks(dim) {
  const out = { streets: [], well: null, outfalls: [] };
  const st = stls[0];
  if (!st) return out;
  for (const s of st.streets || []) {
    if (s.kind !== "kit" || !s.f) continue;
    let n = 0, wet = 0, dry = [], unknown = 0;
    for (let t = s.tmin; t < s.tmin + s.n; t++) {
      const sx = s.f.ox + t * s.f.ux + 1 * s.f.vx, sz = s.f.oz + t * s.f.uz + 1 * s.f.vz;        // w 1 (sidewalk)
      const cx = s.f.ox + t * s.f.ux + 6 * s.f.vx, cz = s.f.oz + t * s.f.uz + 6 * s.f.vz;        // w 6 (trench)
      let top;
      try { top = dim.getTopmostBlock({ x: sx, z: sz }); } catch { top = undefined; }
      if (!top) { unknown++; continue; }
      const H = top.location.y;
      n++;
      let ok = false;
      let col = [];
      for (let y = H - 14; y <= H - 10; y++) { let b; try { b = dim.getBlock({ x: cx, y, z: cz }); } catch { b = undefined; } const id = b ? b.typeId.replace("minecraft:", "") : "?"; col.push(id === "water" ? "~" : id === "air" ? "." : id.slice(0, 3)); if (id === "water") ok = true; }
      if (ok) wet++; else if (dry.length < 14) dry.push([t, col.join("")]);
    }
    // expected: every cell except the dead ends' far walls (3 each) and one step cell per ramp
    const deadEnds = s.role === "connector" ? 0 : 2;
    out.streets.push({ id: s.id, role: s.role, n, wet, expect: n - 3 * deadEnds - (s.ramps || 0), unknown, dry });
  }
  const well = [...blds.values()].find((b) => b.onSquare);
  if (well) {
    let col = 0;
    for (let y = well.y + 1; y <= well.y + 14; y++) { let b; try { b = dim.getBlock({ x: well.x + 2, y, z: well.z + 3 }); } catch { b = undefined; } if (b && b.typeId === "minecraft:water") col++; }
    out.well = { shaftWater: col, of: 14, drain: st.wellDrain || null };
    if (st.wellDrain && st.wellDrain.done) {
      // the drain cells: from the shaft toward the main street's trench along the street's v axis
      const main = (st.streets || []).find((x) => x.kind === "kit" && x.role === "main");
      if (main) {
        const y = st.wellDrain.H - 13;
        const t = st.wellDrain.t;
        let wetD = 0, cells = [];
        for (let w = -8; w <= 6; w++) {
          const x = main.f.ox + t * main.f.ux + w * main.f.vx, z = main.f.oz + t * main.f.uz + w * main.f.vz;
          let b; try { b = dim.getBlock({ x, y, z }); } catch { b = undefined; }
          const id = b ? b.typeId.replace("minecraft:", "") : "?";
          cells.push(id === "water" ? "~" : id === "air" ? "." : id === "stone_bricks" ? "B" : id === "dirt" ? "d" : id.slice(0, 4));
          if (id === "water") wetD++;
        }
        out.well.drainCells = cells.join(" "); out.well.drainWet = wetD;
      }
    }
  }
  for (const s of st.streets || []) {
    for (const o of (s.outfalls || [])) {
      if (!o) { out.outfalls.push(null); continue; }
      const [ex, ez, dx, dz, fy, len, target, gone, mh] = o;
      const read = (x, y, z) => { let b; try { b = dim.getBlock({ x, y, z }); } catch { return "?"; } return b ? b.typeId.replace("minecraft:", "") : "?"; };
      if (target === "soakaway") {                                        // A0.2: the pit under the trench (hole, water falling, gravel)
        out.outfalls.push({ street: s.id, target, gone, exit: [ex, fy, ez], hole: read(ex, fy - 1, ez), pit: [fy - 3, fy - 5, fy - 7, fy - 9].map((y) => read(ex, y, ez)) });
        continue;
      }
      let wl = null;
      try { const g = dim.getBlock({ x: ex, y: fy, z: ez }); wl = g ? g.isWaterlogged : null; } catch { wl = "?"; }
      out.outfalls.push({ street: s.id, target: target || "v1", gone, manholes: mh, spill: read(ex + dx, fy, ez + dz) === "water" || read(ex + dx, fy - 1, ez + dz) === "water", exit: [ex, fy, ez], len, inSpace: [read(ex, fy, ez), read(ex, fy + 1, ez)], waterlogged: wl,
                          beyond1: [read(ex + dx, fy, ez + dz), read(ex + dx, fy - 1, ez + dz), read(ex + dx, fy - 2, ez + dz)],
                          beyond2: [read(ex + 2 * dx, fy, ez + 2 * dz), read(ex + 2 * dx, fy - 1, ez + 2 * dz), read(ex + 2 * dx, fy - 2, ez + 2 * dz)],
                          behind: read(ex - dx, fy, ez - dz) });
    }
  }
  return out;
}
/** D-C533 experiment: does flowing water pass iron bars on this engine? A channel at a fixed spot: floor of stone bricks,
 *  walls, a source, then bars, then 3 open cells; read after 80 ticks. */
async function barsExperiment(dim) {
  const x0 = 250, y = 200, z0 = 250;
  const set = (x, yy, z, id) => { try { dim.getBlock({ x, y: yy, z })?.setType(id); } catch { /* left */ } };
  for (let i = -1; i <= 6; i++) for (let k = -1; k <= 1; k++) { set(x0 + i, y - 1, z0 + k, "minecraft:stone_bricks"); set(x0 + i, y, z0 + k, k === 0 && i >= 0 && i <= 5 ? "minecraft:air" : "minecraft:stone_bricks"); set(x0 + i, y + 1, z0 + k, "minecraft:stone_bricks"); }
  set(x0 + 1, y, z0, "minecraft:iron_bars");
  await sleep(2);
  try { dim.getBlock({ x: x0, y, z: z0 })?.setPermutation(BlockPermutation.resolve("minecraft:water", { liquid_depth: 0 })); } catch (e) { log({ step: "bars", err: String(e) }); }
  await sleep(80);
  const read = (i) => { let b; try { b = dim.getBlock({ x: x0 + i, y, z: z0 }); } catch { return "?"; } return b ? `${b.typeId.replace("minecraft:", "")}${b.isWaterlogged ? "(wl)" : ""}` : "?"; };
  log({ step: "bars", cells: [0, 1, 2, 3, 4, 5].map(read) });
  // and a fence
  set(x0 + 1, y, z0, "minecraft:spruce_fence");
  for (let i = 2; i <= 5; i++) set(x0 + i, y, z0, "minecraft:air");
  await sleep(80);
  log({ step: "fence", cells: [0, 1, 2, 3, 4, 5].map(read) });
}
function keepers(dim) {
  const ks = [];
  for (const e of dim.getEntities({ tags: ["civ:keeper"] })) {
    const tag = e.getTags().find((t) => t.startsWith("civ:shop:"));
    const b = tag ? blds.get(Number(tag.slice(9))) : null;
    const d = b && b.station ? Math.round(Math.hypot(e.location.x - b.station.x, e.location.z - b.station.z) * 10) / 10 : null;
    ks.push([e.nameTag, b ? b.family.replace("pw:mvv_", "") : "?", d]);
  }
  return ks;
}
async function main() {
  const dim = world.getDimension("overworld");
  let ta;
  try { ta = dim.runCommand("tickingarea add 240 -64 240 399 320 399 village true"); } catch (e) { log({ step: "tickingarea", err: String(e) }); }
  try { dim.runCommand("tickingarea add 80 -64 240 239 320 399 west true"); dim.runCommand("tickingarea add 400 -64 240 559 320 399 east true");
        dim.runCommand("tickingarea add 240 -64 80 399 320 239 north true"); dim.runCommand("tickingarea add 240 -64 400 399 320 559 south true");
        // 0.0.15: the four corners stay ASLEEP on purpose — work there (a bench, a road) must be woken by the clock's own
        // ticking cores (D-C542); the engine allows 10 areas, the harness holds 5, the clock may take up to 4
        } catch (e) { log({ step: "tickingarea+", err: String(e) }); }
  log({ step: "tickingarea", result: ta ? ta.successCount : "thrown" });
  for (let i = 0; i < 150; i++) {
    let ok = true;
    for (const [x, z] of [[242, 242], [398, 398], [320, 320], [100, 300], [540, 300], [320, 100], [320, 540]]) { try { if (!dim.getBlock({ x, y: 64, z })) ok = false; } catch { ok = false; } }
    if (ok) break;
    await sleep(20);
  }
  const cands = [];
  for (let x = 280; x <= 360; x += 20) for (let z = 280; z <= 360; z += 20) { const r = siteRange(dim, x, z); if (r) cands.push({ x, z, ...r }); }
  cands.sort((a, b) => b.range - a.range);
  const site = cands.find((c) => c.range >= 4 && c.range <= 14) || cands[0] || { x: 320, z: 320, range: "?" };
  log({ step: "site", chosen: site, candidates: cands.slice(0, 6) });
  await barsExperiment(dim);
  dim.runCommand("time set noon");
  dim.runCommand(`scriptevent pw:clock villageat ${site.x} ${site.z} 7`);
  await sleep(10);
  dim.runCommand("scriptevent pw:clock pause");
  let founded = null;
  for (let i = 0; i < 60 && !founded; i++) { await sleep(20); await readback(dim); founded = stls.find((x) => x.phase === "built" || x.planned === false); }
  log({ step: "founded", phase: founded && founded.phase, kit: founded && founded.kit, square: founded && founded.square, streets: founded && founded.streets, log: founded && founded.log, kitQueue: founded && founded.kitQueue });
  await waitQueue(dim, "founding");
  dim.runCommand("scriptevent pw:clock tickslots");           // 0.0.15: the clock's ticking areas (D-C542) in the log
  await sleep(4);
  await readback(dim);
  log({ step: "foundplots", plots: [...blds.values()].map((b) => [b.id, b.family.replace("pw:mvv_", ""), b.x, b.y, b.z, b.rot, b.stage, b.kit || null]) });
  // D-C535: the 13-tier ladder — village I-III, town I-III, city I (the wall)
  const steps = [["skip 6", "first plots"], ["skip 14", "village built"], ["grow", "village II"], ["skip 12", "village II built"], ["grow", "village III"], ["skip 12", "village III built"],
                 ["grow", "town I: widened, park, grid"], ["skip 24", "town I built"], ["grow", "town II"], ["skip 24", "town II built"], ["grow", "town III"], ["skip 24", "town III built"],
                 ["grow", "city I: wall"], ["skip 46", "city built"], ["bench", "a bench + switchback road"], ["skip 6", "bench streets laid"]];
  const MODE = "__MODE__";
  if (MODE === "work") steps.splice(4);                                  // the focused run: village, village II built, then real time
  for (const [cmd, expect] of steps) {
    dim.runCommand(`scriptevent pw:clock ${cmd}`);
    await sleep(40);
    if (cmd === "bench") { for (let i = 0; i < 60; i++) { await readback(dim); const st = stls[0]; if (st && ((st.roads7 && st.roads7.length) || st.benchFail !== undefined)) break; await sleep(40); } }
    await waitQueue(dim, cmd, 200);
    await readback(dim);
    const st = stls[0];
    const fin = [...blds.values()].filter((b) => b.stage >= 4);
    let okN = 0;
    const bad = [], badKnown = [];
    for (const b of fin) {
      let r;
      try { r = verify(dim, b); } catch (e) { bad.push([b.id, b.family, "verify threw", String(e).slice(0, 120), [b.x, b.y, b.z, b.rot]]); continue; }
      // D-C533 / D-C534: the well's drain (y <= 2 of the template) and the quarry's growing pit are intentional changes
      // + a plot on stilts / a podium: the template's dirt under the house is intentionally absent (0.0.16)
      const landKind = b.land ? b.land.kind : null;
      const known = (r.fam === "well" && r.firstBad.every((c) => c[1] <= 2)) || (r.fam === "quarry" && r.firstBad.every((c) => c[3] === "minecraft:grass_block" || c[3] === "minecraft:dirt"))
        || ((landKind === "stilts" || landKind === "podium") && r.firstBad.every((c) => c[3] === "minecraft:dirt" || c[3] === "minecraft:grass_block"))
        || r.firstBad.every((c) => c[1] <= 2 && c[3] === "minecraft:dirt" && c[4] === "minecraft:stone_bricks")   // foundation cladding by a neighbour's retaining wall
        || (/farm/.test(r.fam) && r.firstBad.every((c) => /wheat|carrots|potatoes|beetroot/.test(c[3]) || (c[3] === "minecraft:grass_block" && c[4] === "minecraft:dirt")));   // 0.0.25c: crops harvested, grass grazed (life, not a fault)
      if (r.ok || known) { okN++; if (known) badKnown.push([r.id, r.fam, r.nMissing]); } else if (bad.length < 6) bad.push([r.id, r.fam, r.badId, r.badState, r.nMissing, r.firstBad.slice(0, 3)]);
      await sleep(1);
    }
    dim.runCommand("time set noon");
    await sleep(400);                                         // C2.1: keepers WALK to their stations now (~4 cells/s; a few duty beats)
    log({ step: "evo", cmd, expect, tier: st && st.tier, plots: blds.size, finished: fin.length, verifiedOk: okN, bad, badKnown, kit: kitChecks(dim), keepers: keepers(dim), markers: markers(dim), sewer: sewerChecks(dim), roads: roadChecks(dim), roads7: st && st.roads7, benchFail: st && st.benchFail,
          crossroads: st && st.crossroads, blocksClosed: st && st.blocksClosed, walls: st && st.walls, leftover: st && st.leftover, people: st && st.population, census: st && st.census, ticking: st && st.ticking, walk: st && st.walk, legs: st && st.legs, work: st && st.work, labor: st && st.labor, manholes: st && st.manholes && { laid: st.manholes.laid, planned: st.manholes.planned }, keys: st && st.keys, sewerLamps: st && st.sewerLamps, drain: st && st.drain, slotWhy: st && st.slotWhy, landLast: st && st.landLast, watch: st && st.watch, bodies: st && st.bodies, works: st && st.works, stewardship: st && st.stewardship, centres: st && st.centres, market: st && st.market, marketTry: st && st.marketTry, quarries: st && st.quarries, side: st && [st.roomAsked || 0, st.roomFound || 0, st.sideWhy, st.sideRest], prof: st && st.prof, civicLeft: st && st.civicLeft, counters: st && st.counters, links: st && st.roads, border: st && st.border,
          ledger: st && st.ledger, waiting: st && st.waiting, waitingN: st && st.waitingN, buildBudget: st && st.buildBudget,
          streets: st && st.streets, width: st && st.width, park: st && st.park, leaf: st && st.leafSwept, chronicle: st && st.log });
    try { dim.runCommand("scriptevent pw:clock log"); } catch { /* old clock */ }       // 0.0.23: the full chronicle (60 lines) into the server log
    await sleep(2);
  }
  // 0.0.25: THE WALK TEST — up to 8 villagers sent to the square / the farthest door / another street's door, traced by
  // the clock ([CIV-WALKTRACE] / [CIV-WALKSTALL] / [CIV-WALKTEST] lines); 2400 ticks at most
  {
    dim.runCommand("time set 2000");
    try { dim.runCommand("scriptevent pw:clock walktest 8"); } catch (e) { log({ step: "walktest", err: String(e) }); }
    await sleep(2500);
    await readback(dim);
    log({ step: "walktest", walk: stls[0] && stls[0].walk });
  }
  // C2.2 (D-C542): REAL-TIME WORK — work hours, the clock at its own pace; 150 s of the hands at the pit and the stand
  {
    dim.runCommand("time set 1000");
    dim.runCommand("scriptevent pw:clock realstage 0.2");        // C2.3: a real labour site (a fifth of the bill's labour)
    await readback(dim);
    const before = stls[0] && stls[0].work, laborBefore = stls[0] && stls[0].labor;
    const samples = [];
    for (let i = 0; i < (MODE === "work" ? 24 : 12); i++) { await sleep(500); await readback(dim); const s0 = stls[0]; samples.push({ t: i, prof: s0 && s0.prof, counters: s0 && s0.counters, gate: s0 && s0.marketGate, market: s0 && s0.market, marketTry: s0 && s0.marketTry, labor: s0 && s0.labor, work: s0 && s0.work && { total: s0.work.total, today: s0.work.today, workers: s0.work.workers, sample: s0.work.sample }, walk: s0 && s0.walk && { arrived: s0.walk.arrived, stuck: s0.walk.stuck, walking: s0.walk.walking, lost: s0.walk.lost, stuckBy: s0.walk.stuckBy, resting: s0.walk.resting } }); }
    log({ step: "worksamples", laborBefore, samples });
    const st = stls[0];
    const chest = (b) => { try { const def = MANIFESTS[b.family]; void def; const inv = b.store ? dim.getBlock(b.store)?.getComponent("minecraft:inventory") : null; const out = {}; if (inv && inv.container) for (let i = 0; i < inv.container.size; i++) { const it = inv.container.getItem(i); if (it) out[it.typeId] = (out[it.typeId] || 0) + it.amount; } return out; } catch (e) { return String(e); } };
    const shops = [...blds.values()].filter((b) => /quarry|lumberyard|bakery|butcher/.test(b.family)).map((b) => [b.id, b.family.replace("pw:mvv_", ""), b.store || null, chest(b)]);
    log({ step: "work", before, after: st && st.work, walk: st && st.walk, shops, keepers: keepers(dim) });
    // F3: the manholes — cover on the sidewalk, ladders down to the sewer gallery
    const mh = ((st && st.manholes && st.manholes.cells) || []).map(([x, H, z]) => {
      const id = (y) => { try { return dim.getBlock({ x, y, z })?.typeId.replace("minecraft:", "").replace("pw:", ""); } catch { return "?"; } };
      let ladders = 0; for (let y = H - 11; y <= H - 1; y++) if (id(y) === "ladder") ladders++;
      return [x, H, z, id(H), ladders, id(H - 12)];
    });
    log({ step: "manholes", summary: st && st.manholes && { laid: st.manholes.laid, planned: st.manholes.planned }, checks: mh, ok: mh.filter((m) => m[3] === "manhole_cover" && m[4] === 11).length });
  }
  // F5 (D-C538): THE WATCH at night — the rounds above and below ground, and three zombies let loose on the square
  {
    dim.runCommand("time set 14000");
    await readback(dim);
    const s0 = stls[0];
    const sq = s0 && s0.square;
    const before = s0 && s0.watch;
    if (sq) for (let k = 0; k < 3; k++) { try { dim.spawnEntity("minecraft:zombie", { x: sq.x + 3 + 3 * k, y: sq.y + 1, z: sq.z + 6 }); } catch (e) { log({ step: "zombie", err: String(e) }); } }
    const nightSamples = [];
    for (let i = 0; i < 12; i++) {
      await sleep(400); await readback(dim);
      const s1 = stls[0];
      let zombies = 0; try { zombies = dim.getEntities({ type: "minecraft:zombie", location: { x: sq.x + 6, y: sq.y, z: sq.z + 6 }, maxDistance: 64 }).length; } catch { zombies = -1; }
      nightSamples.push({ t: i, watch: s1 && s1.watch, zombies, keys: s1 && s1.keys && s1.keys.length, bodies: s1 && s1.bodies });
    }
    log({ step: "watch", before, samples: nightSamples });
    dim.runCommand("time set noon");
  }
  // the dump
  const bs = [...blds.values()];
  const st = stls[0];
  let x0 = Math.min(...bs.map((b) => b.x)) - 16, x1 = Math.max(...bs.map((b) => b.x + 17)) + 16;
  let z0 = Math.min(...bs.map((b) => b.z)) - 16, z1 = Math.max(...bs.map((b) => b.z + 17)) + 16;
  x0 = Math.max(x0, 82); z0 = Math.max(z0, 82); x1 = Math.min(x1, 557); z1 = Math.min(z1, 557);
  const y0 = Math.min(...bs.map((b) => b.y)) + 8, y1 = Math.max(...bs.map((b) => b.y + MANIFESTS[b.family].size[1])) + 2;
  log({ step: "plots", plots: bs.sort((p, q) => p.id - q.id).map((b) => { const m = MANIFESTS[b.family]; const [fx, fz] = b.rot % 2 ? [m.size[2], m.size[0]] : [m.size[0], m.size[2]];
        return [b.id, b.family.replace("pw:mvv_", ""), b.x, b.y + 15, b.z, b.rot, fx, fz, b.kit ? b.kit.sid : null, b.stage, b.closed ? 1 : 0, b.onSquare ? 1 : 0]; }) });
  const pal = [], pk = new Map();
  log({ step: "roadcells", roads: [...roads.values()].map((r) => ({ id: r.id, n: r.cells.length, cells: r.cells })) });   // 0.0.18: for the plan render
  log({ step: "dumphead", x0, x1, z0, z1, y0, y1 });
  for (let y = y0; y <= y1; y++) {
    const runs = [];
    let last = -2, n = 0;
    for (let x = x0; x <= x1; x++) for (let z = z0; z <= z1; z++) {
      let blk;
      try { blk = dim.getBlock({ x, y, z }); } catch { blk = undefined; }
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
  // 0.0.13: the GROUND HEIGHTMAP of the whole ticking square (for the offline road / bench planner harness): one row per z,
  // RLE of ground y (the clock's groundAt rule: the topmost block, walking down past plants, trees and snow); 'w' = water
  const NOTG = ["leaves", "_log", "_wood", "log", "short_grass", "tall_grass", "fern", "flower", "vine", "snow_layer", "bush", "mushroom", "sapling", "roots",
    "propagule", "dandelion", "poppy", "tulip", "petals", "orchid", "allium", "bluet", "daisy", "cornflower", "lily", "rose", "peony", "lilac", "sunflower", "azalea",
    "berry", "dripleaf", "moss_carpet", "pumpkin", "melon", "cactus", "sugar_cane", "bamboo", "deadbush", "web", "torch", "pw:"];
  const isG = (id) => id !== "minecraft:air" && (!NOTG.some((s) => id.includes(s)) || id.startsWith("pw:ground") || id.includes("grass_block"));
  const HX0 = 82, HX1 = 557, HZ0 = 82, HZ1 = 557;
  log({ step: "heighthead", x0: HX0, x1: HX1, z0: HZ0, z1: HZ1 });
  for (let z = HZ0; z <= HZ1; z++) {
    const runs = []; let last = null, n = 0;
    for (let x = HX0; x <= HX1; x++) {
      let v = "?";
      try {
        let b = dim.getTopmostBlock({ x, z });
        if (b) {
          if (b.typeId.includes("water")) v = "w";
          else { let y = b.y, id = b.typeId, guard = 0; while (!isG(id) && guard++ < 40) { y--; const bb = dim.getBlock({ x, y, z }); if (!bb) break; id = bb.typeId; if (id.includes("water")) { v = "w"; break; } } if (v !== "w") v = String(y); }
        }
      } catch { v = "?"; }
      if (v === last) n++; else { if (n) runs.push(n > 1 ? `${last}*${n}` : `${last}`); last = v; n = 1; }
    }
    runs.push(n > 1 ? `${last}*${n}` : `${last}`);
    console.warn(`[CIVHEIGHT] ${z} ${runs.join(",")}`);
    if (z % 2 === 0) await sleep(1);
  }
  log({ step: "heightdone" });
  log({ step: "DONE" });
}
system.runTimeout(() => { main().catch((e) => console.warn("[CIVTEST] " + JSON.stringify({ step: "main", err: String(e), st: e.stack }))); }, 100);
'''


def build(out):
    out = Path(out)
    if out.exists():
        raise SystemExit(f"never rebuild {out}")
    (out / "scripts").mkdir(parents=True)
    (out / "scripts/civ_manifests.js").write_text(manifests())
    mode = sys.argv[2] if len(sys.argv) > 2 else "full"
    (out / "scripts/main.js").write_text(HEAD + MAIN.replace("__MODE__", mode))
    json.dump({"format_version": 2,
               "header": {"name": "PW KitVillage probe (BDS only)", "description": "StreetKit village read back", "uuid": str(uuid.uuid4()),
                          "version": [0, 0, 1], "min_engine_version": [1, 21, 120]},
               "modules": [{"type": "script", "language": "javascript", "entry": "scripts/main.js", "uuid": str(uuid.uuid4()), "version": [0, 0, 1]},
                           {"type": "data", "uuid": str(uuid.uuid4()), "version": [0, 0, 1]}],
               "dependencies": [{"module_name": "@minecraft/server", "version": "2.3.0"}]}, open(out / "manifest.json", "w"), indent=1)
    print("built", out)


if __name__ == "__main__":
    build(sys.argv[1])
