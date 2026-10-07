// test_survey.mjs — 1.3.231 (CIV-LAND) THE WIDE SURVEY (pw_civ_land.js): tiles, the grown field, one pass against a fake
// world (loaded / sleeping / held tiles), and the field's text ("d1" deltas; the old run list still read). Usage:
// node tests/test_survey.mjs
import * as LAND from "../pw_civ_land.js";
import { readFileSync } from "node:fs";
import { gunzipSync } from "node:zlib";
let n = 0, bad = 0;
const ok = (name, cond, info) => { n++; if (!cond) bad++; console.log(`${cond ? "PASS" : "FAIL"} ${n} ${name}${cond ? "" : " — " + JSON.stringify(info).slice(0, 400)}`); };
const W = LAND.WIDE;

// --- 1. the radius follows the boundary stones
ok("radius: a village (border 64) gets the base 192", LAND.wideRadius(64) === 192, LAND.wideRadius(64));
ok("radius: a city (border 176) gets 272 (176 + 96)", LAND.wideRadius(176) === 272, LAND.wideRadius(176));
ok("radius: a capital (border 420) is capped at 320", LAND.wideRadius(420) === 320, LAND.wideRadius(420));

// --- 2. tiles
const cx = -147, cz = 98, R = 192;
const core = LAND.makeSite(cx - 80, cz - 80, 160, 160);
for (let x = core.x0; x < core.x0 + 160; x++) for (let z = core.z0; z < core.z0 + 160; z++) core.set(x, z, 70 + ((x * 7 + z * 3) & 7), false);
const tiles = LAND.surveyTiles(cx, cz, R, W.tile, core);
ok("tiles: chunk-aligned, 128 x 128 (8 x 8 chunks)", tiles.every(([x0, z0, x1, z1]) => x0 % 16 === 0 && z0 % 16 === 0 && x1 - x0 === 127 && z1 - z0 === 127), tiles.slice(0, 2));
// the clock's ensureTicking pads a box by 8 and keeps it chunk-aligned: 128 + 16 = 144 -> 10 chunks, the engine's cap
ok("tiles: a padded tile is 10 x 10 chunks at most (the ticking-area cap)", tiles.every(([x0, z0, x1, z1]) => (Math.ceil((x1 + 9) / 16) - Math.floor((x0 - 8) / 16)) <= 10 && (Math.ceil((z1 + 9) / 16) - Math.floor((z0 - 8) / 16)) <= 10));
{
  let miss = 0;
  for (let x = cx - R; x < cx + R; x += 3) for (let z = cz - R; z < cz + R; z += 3) {
    const inCore = core.inside(x, z);
    if (!inCore && !tiles.some(([x0, z0, x1, z1]) => x >= x0 && x <= x1 && z >= z0 && z <= z1)) miss++;
  }
  ok("tiles: every column of the wide square outside the core lies in a tile", miss === 0, miss);
}
const allTiles = LAND.surveyTiles(cx, cz, R, W.tile, null);
ok(`tiles: ${tiles.length} to read (of ${allTiles.length}; tiles wholly inside the core are skipped)`, tiles.length <= allTiles.length && tiles.length >= 9, [tiles.length, allTiles.length]);
const dC = (t) => Math.hypot((t[0] + t[2]) / 2 - cx, (t[1] + t[3]) / 2 - cz);
ok("tiles: nearest the centre first", tiles.every((t, i) => i === 0 || dC(tiles[i - 1]) <= dC(t) + 1e-9));

// --- 3. one pass against a fake world: tiles 0..2 loaded, the rest asleep until held for 2 polls; one hold refused
const prog = LAND.wideProgress(core, cx, cz, R);
ok("grown field: 384 x 384, the core's cells copied", prog.site.w === 384 && prog.site.d === 384 && prog.site.at(cx, cz) === core.at(cx, cz));
const world = { awake: new Set([0, 1, 2].map((i) => prog.tiles[i].join())), heldFor: new Map(), holds: 0, releases: 0, refuse: 1, calls: 0, coreCalls: 0 };
const ground = (x, z) => 60 + Math.floor(Math.hypot(x - cx, z - cz) / 8);
const io = {
  loaded: (t) => world.awake.has(t.join()) || (world.heldFor.get(t.join()) || 0) >= 2,
  column: (x, z) => { world.calls++; if (core.inside(x, z)) world.coreCalls++; return { g: ground(x, z), water: (x + z) % 97 === 0 }; },
  hold: (t) => { if (world.refuse > 0) { world.refuse--; return null; } world.holds++; world.heldFor.set(t.join(), 0); return { t: t.join() }; },
  release: (h) => { world.releases++; world.heldFor.delete(h.t); },
};
// a "pause" between passes: every held tile ages one poll (its chunks load after 2)
const pause = () => { for (const [k, v] of world.heldFor) world.heldFor.set(k, v + 1); };
let passes = 0, yields = 0, res;
for (;;) {
  const gen = LAND.wideSurveyPass(prog, io);
  let r = gen.next();
  while (!r.done) { yields++; r = gen.next(); }
  res = r.value; passes++;
  if (res === "done" || passes > 400) break;
  pause();
}
const expected = 384 * 384 - 160 * 160;
ok("pass: the survey finishes", res === "done", { res, passes, i: prog.i, of: prog.tiles.length });
ok(`pass: every column outside the core read once (${expected.toLocaleString()} reads)`, world.calls === expected && prog.read === expected, { calls: world.calls, read: prog.read });
ok("pass: the core's columns are never read again (its 'before' ground is kept)", world.coreCalls === 0 && prog.site.at(cx + 5, cz + 5) === core.at(cx + 5, cz + 5));
ok("pass: one ticking area per sleeping tile, each released after its read", world.holds === prog.tiles.length - 3 && world.releases === world.holds && world.heldFor.size === 0, world);
ok("pass: a refused hold waits (no tile skipped)", prog.skipped.length === 0, prog.skipped);
ok("pass: a background job (yields every 256 reads)", yields >= Math.floor(expected / 256), yields);
ok("pass: water read into the field", prog.site.isWater(cx + 150, cz - 53) === (((cx + 150 + cz - 53) % 97) === 0));
// a tile whose chunks never load is skipped after waitPolls, its area released
{
  const p2 = LAND.wideProgress(core, cx, cz, R);
  let holds = 0, rel = 0;
  const io2 = { loaded: () => false, column: () => null, hold: (t) => { holds++; return { t }; }, release: () => { rel++; } };
  let r2, k = 0;
  do { const g = LAND.wideSurveyPass(p2, io2); let r = g.next(); while (!r.done) r = g.next(); r2 = r.value; k++; } while (r2 !== "done" && k < 1000);
  ok("never loads: every tile skipped after its polls, every area released", r2 === "done" && p2.skipped.length === p2.tiles.length && holds === rel && holds === p2.tiles.length, { r2, k, skipped: p2.skipped.length, holds, rel });
}

// a re-run on the finished field: only the tiles holding unknown columns (a tile that never woke) are surveyed again
{
  const done = prog.site;
  const t = prog.tiles[5];
  for (let x = t[0]; x <= t[2]; x++) for (let z = t[1]; z <= t[3]; z++) if (done.inside(x, z)) { done.h[done.idx(x, z)] = -1; }
  const p3 = LAND.wideProgress(done, cx, cz, R);
  ok("re-run: the one tile left unknown is the only tile surveyed again", p3.tiles.length === 1 && p3.tiles[0].join() === t.join(), p3.tiles.length);
  const p4 = LAND.wideProgress(core, cx, cz, 320, done);
  ok("a wider ring (320): the known 384 field is kept, only the new rim (and the hole) is read", p4.site.at(cx + 150, cz + 150) === done.at(cx + 150, cz + 150) && p4.tiles.length > 0 && p4.tiles.length < LAND.surveyTiles(cx, cz, 320, W.tile, null).length, p4.tiles.length);
}

// --- 4. the field as text
const roundTrip = (site) => { const t = LAND.siteEncode(site); const back = LAND.siteDecode(JSON.parse(JSON.stringify(t))); let diff = 0; for (let i = 0; i < site.h.length; i++) if (site.h[i] !== back.h[i] || site.water[i] !== back.water[i]) diff++; return { t, diff }; };
const legacyText = (site) => { const runs = []; let last = null, k = 0; for (let i = 0; i < site.h.length; i++) { const v = site.h[i] * 2 + site.water[i]; if (v === last) k++; else { if (k) runs.push(k > 1 ? `${last}*${k}` : `${last}`); last = v; k = 1; } } runs.push(k > 1 ? `${last}*${k}` : `${last}`); return { x0: site.x0, z0: site.z0, w: site.w, d: site.d, rle: runs.join(",") }; };
{
  const { t, diff } = roundTrip(prog.site);
  ok("d1: the grown field round-trips exactly", diff === 0, diff);
  const old = legacyText(prog.site), back = LAND.siteDecode(old);
  let d2 = 0; for (let i = 0; i < prog.site.h.length; i++) if (back.h[i] !== prog.site.h[i] || back.water[i] !== prog.site.water[i]) d2++;
  ok("the old run list (saved by 1.3.230 and before) is still read", d2 === 0, d2);
  console.log(`  synthetic 384 x 384: old ${old.rle.length.toLocaleString()} chars, d1 ${t.data.length.toLocaleString()} chars`);
}
// his kind of land: the BDS gate world's heightmap (civtest 10-05 19:02, 476 x 476 around a town on a mountain; 40 % of it
// unread — kept as unknown, -1)
{
  const txt = gunzipSync(readFileSync(new URL("./fixtures/civheight-20261005-190214.txt.gz", import.meta.url))).toString();
  const head = JSON.parse(txt.match(/\{"step":"heighthead".*\}/)[0]);
  const w = head.x1 - head.x0 + 1, d = head.z1 - head.z0 + 1;
  const site = LAND.makeSite(head.x0, head.z0, w, d);
  for (const m of txt.matchAll(/\[CIVHEIGHT\] (-?\d+) (\S+)/g)) {
    const z = Number(m[1]); let x = head.x0;
    for (const run of m[2].split(",")) { const [v, k] = run.split("*"); const cnt = k ? Number(k) : 1; for (let q = 0; q < cnt; q++, x++) { if (v === "?") continue; if (v === "w") site.set(x, z, 62, true); else site.set(x, z, Number(v), false); } }
  }
  const { t, diff } = roundTrip(site);
  const old = legacyText(site);
  ok("d1: the gate world's mountain round-trips exactly", diff === 0, diff);
  ok(`d1: smaller than the old text on it (${t.data.length.toLocaleString()} vs ${old.rle.length.toLocaleString()} chars)`, t.data.length < old.rle.length * 0.75, [t.data.length, old.rle.length]);
  let knownN = 0; for (let i = 0; i < site.h.length; i++) if (site.h[i] >= 0) knownN++;
  const perCol = t.data.length / knownN;                         // per KNOWN column (its unread 40 % costs almost nothing)
  console.log(`  gate mountain ${w} x ${d}: old ${old.rle.length.toLocaleString()} chars, d1 ${t.data.length.toLocaleString()} (${perCol.toFixed(2)} chars per known column, ${knownN.toLocaleString()} known) -> a 384 x 384 field ~ ${Math.round(perCol * 384 * 384 / 1000)} K chars, ${Math.ceil(perCol * 384 * 384 / 30000)} properties of 30,000`);
  ok("d1: a 384 x 384 field of this land fits in a handful of 30,000-character properties (<= 12)", Math.ceil(perCol * 384 * 384 / 30000) <= 12, perCol);
}
// extreme deltas (a cliff, a cave mouth read as -1) round-trip through the escape
{
  const s = LAND.makeSite(0, 0, 50, 3);
  for (let i = 0; i < 150; i++) { if (i % 11 === 0) continue; s.h[i] = i % 7 === 0 ? 300 : (i % 5 === 0 ? -64 + i : 64); s.water[i] = i % 13 === 0 ? 1 : 0; }
  const { diff } = roundTrip(s);
  ok("d1: cliffs of 200+, deep values and unknown cells round-trip", diff === 0, diff);
}
console.log(`test_survey: ${n - bad}/${n} passed`);
if (bad) process.exitCode = 1;
