// test_shifts.mjs — 1.3.228 (B4 / PEOPLE II): pure.
// BF5 shift templates (24 letters an hour), the id's start offset (stable, -200..+200), the 7-day plan (days off, keepers on
// the town's day), PE5 the walk home (6 ticks a block, a climb x1.5) and the home-too-far complaint (> 160), the rain ruling
// (quarrymen, woodcutters, builders keep half; nobody else loses anything), PE1 work-beat weights and spots, PE2 the inn's
// mood gain, BF7 the nearest free job / home, the far-home move and the move to another town when nothing is free.
import * as PEOPLE from "../pw_civ_people.js";
import { CIV_BUILDINGS } from "../pw_civ_buildings.js";
let pass = 0, fail = 0;
const ok = (c, m, extra) => { if (c) pass++; else { fail++; console.log("FAIL", m, extra === undefined ? "" : JSON.stringify(extra)); } };
const { SHIFT, COMMUTE, RAIN, WORKBEAT, INN, MOVE } = PEOPLE;
const person = (id, o = {}) => ({ id, name: `P${id}`, sex: "m", born: 0, home: 1, job: 100, trade: "bakery", spouse: null, parents: [], kids: [], friends: {}, mood: 55, alive: true, knows: [], ...o });

// ------------------------------------------------------------------------------------------------ 1. offsets
{
  let lo = Infinity, hi = -Infinity, sum = 0, stable = true;
  const bins = new Array(8).fill(0);
  const N = 40000;
  for (let id = 1; id <= N; id++) {
    const o = PEOPLE.shiftOffset(id);
    if (o !== PEOPLE.shiftOffset(id)) stable = false;
    lo = Math.min(lo, o); hi = Math.max(hi, o); sum += o;
    bins[Math.min(7, Math.floor((o + 200) / 401 * 8))]++;
  }
  ok(stable, "the offset is stable per id");
  ok(lo >= -200 && hi <= 200 && Number.isInteger(lo) && Number.isInteger(hi), "offsets lie in -200..+200 (integers)", [lo, hi]);
  ok(lo <= -195 && hi >= 195, "offsets reach both ends", [lo, hi]);
  ok(Math.abs(sum / N) < 4, "offsets centre on 0", sum / N);
  ok(bins.every((n) => Math.abs(n - N / 8) < N / 8 * 0.08), "offsets spread evenly (8 bins within 8 %)", bins);
}

// ------------------------------------------------------------------------------------------------ 2. templates and slots
{
  ok(Object.values(SHIFT.T).every((t) => t.length === 24 && /^[WMIR]+$/.test(t)), "every template has 24 hours of W / M / I / R");
  ok(PEOPLE.hourOf(0) === 6 && PEOPLE.hourOf(1000) === 7 && PEOPLE.hourOf(18000) === 0 && PEOPLE.hourOf(23999) === 5 && PEOPLE.hourOf(13000) === 19, "hours: tod 0 = 06:00, tod 18000 = midnight");
  const T = (p, o) => PEOPLE.shiftTemplate(p, o);
  ok(T(person(1, { job: "watch" })) === "night" && T(person(1, { job: "sewer_keeper" })) === "day" && T(person(1, { job: "fisher" })) === "early"
     && T(person(1, { trade: "farm_wheat" })) === "early" && T(person(1, { keeper: true }), { keeper: true, kind: "bakery" }) === "late"
     && T(person(1), { kind: "inn" }) === "late" && T(person(1), { keeper: true, kind: "quarry" }) === "standard" && T(person(1)) === "standard"
     && T(person(1), { child: true }) === "child", "the template comes from the job");
  ok(T(person(1, { job: "watch", shift: "standard" })) === "standard" && T(person(1, { shift: "nonsense" })) === "standard", "p.shift (the only saved field) overrides; an unknown id is ignored");
  // the standard template is the old town SCHED shifted by the person's offset (a work day, no walk home)
  let same = true, nightSame = true, n = 0;
  for (let id = 1; id <= 60; id++) {
    const p = person(id), w = person(id, { job: "watch" }), o = PEOPLE.shiftOffset(id);
    for (let tod = 0; tod < 24000; tod += 250) {
      const day = [0, 1, 2, 3, 4, 5, 6].find((d) => !PEOPLE.dayOff(p, d, { tpl: "standard" }));
      const t = ((tod - o) % 24000 + 24000) % 24000;
      const want = t >= 1000 && t < 11000;
      if ((PEOPLE.shiftAt(p, tod, day + 7).slot === "W") !== want && Math.abs(t - 1000) > 1 && Math.abs(t - 11000) > 1 && tod - o >= 0) same = false;
      const dayW = [0, 1, 2, 3, 4, 5, 6].find((d) => !PEOPLE.dayOff(w, d, { tpl: "night" }));
      const wantN = t >= 13000 && t < 23000;
      if (tod - o >= 0 && tod - o < 24000 && (PEOPLE.shiftAt(w, tod, dayW + 7).slot === "W") !== wantN) nightSame = false;
      n++;
    }
  }
  ok(same, "standard = work 1000..11000 shifted by the offset (the old SCHED)");
  ok(nightSame, "the watch works only at night (13000..23000 shifted by the offset)");
  ok(PEOPLE.shiftAt(person(5, { job: "watch" }), 5000, 3).slot !== "W" && PEOPLE.shiftAt(person(5), 15000, 3).slot === "R", "the watch rests by day; the standard rests at night");
}

// ------------------------------------------------------------------------------------------------ 3. the week: days off
{
  const tally = (tpl, kOpts = {}) => {
    const starts = new Array(7).fill(0);
    let good = true;
    for (let id = 1; id <= 700; id++) {
      const p = person(id);
      const offs = [];
      for (let d = 70; d < 77; d++) if (PEOPLE.dayOff(p, d, { tpl, seed: 9, ...kOpts })) offs.push(d % 7);
      if (offs.length !== (SHIFT.off[tpl] || 0)) good = false;
      if (offs.length === 2 && !(((offs[1] - offs[0]) + 7) % 7 === 1 || ((offs[0] - offs[1]) + 7) % 7 === 1)) good = false;   // consecutive
      if (offs.length) starts[PEOPLE.restStart(p, 9, !!kOpts.keeper)]++;
    }
    return { good, starts };
  };
  const st = tally("standard"), nt = tally("night"), ch = tally("child"), kp = tally("late", { keeper: true });
  ok(st.good, "standard: exactly one day off in 7");
  ok(nt.good, "the watch: two consecutive days off in 7");
  ok(ch.good, "children: no days off (no work days)");
  ok(st.starts.every((n) => n > 70 && n < 130), "the rest days spread over the week (by id)", st.starts);
  ok(kp.good && kp.starts.every((n) => n > 50), "keepers rest on their own days, spread over the week (no shop-wide closed day)", kp.starts);
  // a day off turns work into idle; the next day works
  const p = person(11), d0 = [0, 1, 2, 3, 4, 5, 6].find((d) => PEOPLE.dayOff(p, d, { tpl: "standard" }));
  const o = PEOPLE.shiftOffset(11);
  const a = PEOPLE.shiftAt(p, 5000 + o, d0), b = PEOPLE.shiftAt(p, 5000 + o, d0 + 1 === 7 ? 0 : d0 + 1);
  ok(a.slot === "I" && a.off && b.slot === "W" && !b.off, "a day off: work hours become idle; the next day is a work day", [a, b]);
  ok(PEOPLE.onShift(p, 5000 + o, d0 + 1 === 7 ? 0 : d0 + 1) && !PEOPLE.onShift(p, 5000 + o, d0), "onShift follows the plan");
}

// ------------------------------------------------------------------------------------------------ 4. the walk home (PE5)
{
  ok(PEOPLE.travelTicks({ x: 0, y: 64, z: 0 }, { x: 100, y: 64, z: 0 }) === 600, "100 blocks on the level = 600 ticks (6 a block)");
  ok(PEOPLE.travelTicks({ x: 0, y: 64, z: 0 }, { x: 30, y: 104, z: 0 }) === Math.ceil(6 * Math.hypot(30, 60)), "a climb counts 1.5 times (30 across, 40 up = 6 x hypot(30, 60))");
  ok(PEOPLE.travelTicks({ x: 0, y: 0, z: 0 }, { x: 0, y: 0, z: 3 }) === 18 && PEOPLE.travelTicks(null, { x: 1 }) === 0, "a short walk; an unknown place is 0");
  ok(PEOPLE.travelTicks({ x: 0, z: 0 }, { x: 5000, z: 0 }) === COMMUTE.max, "capped at COMMUTE.max", COMMUTE.max);
  // a person with a work day (find one, offset known)
  const p = person(21), o = PEOPLE.shiftOffset(21);
  const day = 7 + [0, 1, 2, 3, 4, 5, 6].find((d) => !PEOPLE.dayOff(p, d, { tpl: "standard" }));
  const at = (tod, travel) => PEOPLE.shiftAt(p, tod + o, day, { travel });
  // near home (600 ticks): the work day is whole; he leaves the square 600 ticks before the rest block (tod 13000)
  ok(at(10900, 600).slot === "W" && at(11500, 600).slot === "M" && at(12399, 600).slot === "M" && at(12400, 600).slot === "R" && at(12400, 600).home, "a 600-tick walk: home by night (leaves the square at 12400)");
  // far home (2,500 ticks > the 2,000-tick meet block): the work ends early
  ok(at(10400, 2500).slot === "W" && at(10500, 2500).slot === "R" && at(10500, 2500).home && at(10500, 0).slot === "W", "a far home (2500 ticks) ends the shift 500 ticks early");
  ok(at(10999, 0).slot === "W" && at(11000, 0).slot === "M", "no walk known: the template as it is");
  const w = person(22, { job: "watch" }), ow = PEOPLE.shiftOffset(22), dw = 7 + [0, 1, 2, 3, 4, 5, 6].find((d) => !PEOPLE.dayOff(w, d, { tpl: "night" }));
  ok(PEOPLE.shiftAt(w, 22000 + ow, dw, { travel: 600 }).slot === "W" && PEOPLE.shiftAt(w, 22500 + ow, dw, { travel: 600 }).slot === "R", "the watch leaves its round to be home when its rest starts (05:00)");
  ok(PEOPLE.homeFar({ x: 0, z: 0 }, { x: 161, z: 0 }) && !PEOPLE.homeFar({ x: 0, z: 0 }, { x: 160, z: 0 }) && !PEOPLE.homeFar({ x: 0, z: 0 }, {}), "home too far: over 160 blocks (unknown = no)");
  ok(PEOPLE.whyOf(person(1), { phase: "work", busy: true, homeFar: true }) === "HOME_FAR" && PEOPLE.whyOf(person(1), { phase: "work", busy: true }) === "WORKING"
     && PEOPLE.whyOf(person(1), { phase: "work", worker: "NO_FACE", homeFar: true }) === "NO_FACE", "the complaint is a why code (after the work module's own reason)");
}

// ------------------------------------------------------------------------------------------------ 5. rain: half for the three
{
  for (const t of ["quarry", "lumberyard", "builders"]) ok(PEOPLE.rainKeep(t, 1) === 0.5 && PEOPLE.rainKeep(t, 0) === 1 && PEOPLE.rainKeep(t, 0.5) === 0.75, `${t}: half kept in a wet day, 3/4 in a half-wet one`);
  for (const t of ["bakery", "butcher", "smithy", "fishery", "fisher", "inn", "farm_wheat", "watch"]) ok(PEOPLE.rainKeep(t, 1) === 1 && PEOPLE.rainOutput(t, 40, 1, 60) === 40, `${t}: rain costs nothing`);
  ok(PEOPLE.rainOutput("quarry", 30, 0.5, 60) === 45, "half wet: 30 carried in the dry half -> the wet half keeps half that rate (45)");
  ok(PEOPLE.rainOutput("lumberyard", 40, 0, 40) === 40, "dry: what was carried");
  ok(PEOPLE.rainOutput("quarry", 0, 1, 60) === 30 && PEOPLE.rainOutput("quarry", 2, 0.9, 60) === 2 + 0.5 * 60 * 0.9, "mostly wet: half the abstract rate over the wet hours");
  const day = (w) => PEOPLE.rainOutput("quarry", 60 * (1 - w), w, 60);
  ok(Math.abs(day(0) - 60) < 1e-9 && Math.abs(day(0.5) - 45) < 1e-9 && Math.abs(day(1) - 30) < 1e-9, "a steady 60-a-day quarry: 60 dry, 45 half wet, 30 all wet (= half)");
  ok(PEOPLE.whyOf(person(1), { phase: "work", shelter: true }) === "SHELTER" && PEOPLE.WHY.SHELTER, "sheltering is its own why code");
}

// ------------------------------------------------------------------------------------------------ 6. work beats (PE1)
{
  const want = Object.fromEntries(WORKBEAT.w), total = WORKBEAT.w.reduce((a, [, n]) => a + n, 0);
  ok(want.main === 8 && want.near === 5 && want.second === 5 && want.store === 6 && want.door === 7, "weights: main 8, near 5, second 5, side tasks 6 and 7");
  const got = {}; let N = 0;
  for (let pid = 1; pid <= 200; pid++) for (let k = 0; k < 200; k++) { const b = PEOPLE.beatOf(pid, k * WORKBEAT.window + 17); got[b] = (got[b] || 0) + 1; N++; }
  ok(Object.keys(want).every((b) => Math.abs(got[b] / N - want[b] / total) < 0.01), "40,000 draws follow the weights (within 1 %)", { got, N });
  ok(PEOPLE.beatOf(7, 1200) === PEOPLE.beatOf(7, 1799) && PEOPLE.beatOf(7, 1200) === PEOPLE.beatOf(7, 1200), "a beat lasts its 600-tick window (deterministic)");
  let changes = 0; for (let k = 1; k < 100; k++) if (PEOPLE.beatOf(3, k * 600) !== PEOPLE.beatOf(3, (k - 1) * 600)) changes++;
  ok(changes > 40, "beats change from window to window", changes);
  // look-at cells from the real bakery and smithy templates
  const fam = (stem) => Object.values(CIV_BUILDINGS).find((d) => d.stem === stem);
  const bak = fam("mvv_bakery_a_r1"), smi = fam("mvv_smithy_a_r1");
  const lb = PEOPLE.lookCells("bakery", bak.dir.concat(bak.chests)), ls = PEOPLE.lookCells("smithy", smi.dir.concat(smi.chests));
  ok(lb.main.length >= 2 && lb.second.length >= 4, "the bakery looks at its furnaces / hearth and its barrels / shelves", [lb.main.length, lb.second.length]);
  ok(ls.main.length >= 2, "the smithy looks at its anvil / blast furnace", ls.main.length);
  ok(PEOPLE.lookCells("bakery", [[0, 0, 0, "minecraft:furnace", {}], [1, 0, 0, "pw:furn_shelf_oak"], [2, 0, 0, "minecraft:stone"]]).main.length === 1, "prefix match, namespaces ignored, other blocks skipped");
  // spots
  const sp = { station: { x: 10.5, y: 64, z: 10.5 }, main: [{ x: 12, y: 64, z: 10 }], second: [{ x: 10, y: 65, z: 13 }, { x: 30, y: 64, z: 30 }], store: { x: 8, y: 64, z: 9 }, door: { in: { x: 14.5, y: 64, z: 10.5 }, out: { x: 15.5, y: 64, z: 10.5 } } };
  const m = PEOPLE.workSpot("main", sp), nr = PEOPLE.workSpot("near", sp), sc = PEOPLE.workSpot("second", sp), so = PEOPLE.workSpot("store", sp), dr = PEOPLE.workSpot("door", sp);
  ok(m.stand.x === 10.5 && m.look.x === 12.5, "main: at the station, facing the trade's own block");
  ok(nr.stand.x === 10.5 && nr.look && nr.look.z === 13.5, "near: at the station, looking at another block");
  ok(sc.look.z === 13.5 && Math.hypot(sc.stand.x - 10.5, sc.stand.z - 10.5) <= WORKBEAT.reach && Math.hypot(sc.stand.x - 10.5, sc.stand.z - 13.5) <= 1.5, "second: beside a shelf within 4 of the station (the far one is never chosen)", sc);
  ok(so.look.x === 8.5 && dr.stand.x === 14.5 && dr.look.x === 15.5, "the store chest; the door step facing out");
  ok(PEOPLE.workSpot("second", { station: sp.station }).beat === "main" && PEOPLE.workSpot("main", {}) === null, "nothing to do -> the main task; no station -> nothing");
  ok(Math.abs(PEOPLE.yawTo({ x: 0, z: 0 }, { x: 0, z: 5 })) < 1e-9 && Math.abs(PEOPLE.yawTo({ x: 0, z: 0 }, { x: -5, z: 0 }) - 90) < 1e-9, "yaw: south 0, west 90 (the fisherman's formula)");
}

// ------------------------------------------------------------------------------------------------ 7. the inn (PE2)
{
  let acc = 0, mood = 30, gained = 0;
  for (let t = 0; t < 1200; t += 100) { const r = PEOPLE.innStep(acc, 100, mood); acc = r.acc; mood += r.gain; gained += r.gain; }
  ok(gained === 1 && mood === 31, "1,200 ticks at the inn: +1 mood", [gained, mood]);
  for (let t = 0; t < 2400; t += 100) { const r = PEOPLE.innStep(acc, 100, mood); acc = r.acc; mood += r.gain; }
  ok(mood === 33, "3,600 ticks: +3", mood);
  ok(PEOPLE.innStep(0, 5000, 30).gain === 0 && PEOPLE.innStep(0, 5000, 30).acc === INN.stepMax, "a long gap counts at most INN.stepMax (no catch-up after a reload)");
  ok(PEOPLE.innStep(1199, 100, 54).gain === 1 && PEOPLE.innStep(1199, 100, 55).gain === 0 && PEOPLE.innStep(2399, 1, 54.5).gain <= 1, "never above INN.cap (55)");
  ok(PEOPLE.wantsInn({ mood: 39 }) && !PEOPLE.wantsInn({ mood: 40 }) && !PEOPLE.wantsInn(null), "only the unhappy (< 40) seek the inn");
  // a sad person at the inn every evening (dusk 2,000 ticks) for a week vs one with no inn
  let m1 = 30, a1 = 0;
  for (let d = 0; d < 7; d++) for (let t = 0; t < 2000; t += 100) { const r = PEOPLE.innStep(a1, 100, m1); a1 = r.acc; m1 += r.gain; }
  ok(m1 > 30 + 9 && m1 <= 30 + 12, "a week of evenings at the inn: about +11", m1);
}

// ------------------------------------------------------------------------------------------------ 8. places (BF7)
{
  const town = () => {
    const P = PEOPLE.newPeople();
    return P;
  };
  const base = (o) => ({ day: 200, fed: 1, paid: true, seed: 3, sanitation: 1, foodDays: 5, levels: new Map(), ...o });
  // a. the free job NEAREST home
  {
    const P = town();
    const a = PEOPLE.newPerson(P, 200, { home: 1, age: 40, seed: 1 });
    const jobs = [{ id: 101, kind: "bakery", vacancies: 1, x: 100, z: 0 }, { id: 102, kind: "butcher", vacancies: 1, x: 10, z: 0 }];
    PEOPLE.dayStep(P, base({ homes: [{ id: 1, room: 0, x: 0, z: 0 }], jobs }));
    ok(a.job === 102 && jobs[1].vacancies === 0 && jobs[0].vacancies === 1, "a jobless adult takes the vacancy nearest his home (not the first listed)", a.job);
  }
  // a2. gate 228-10: the TOWN'S POSTS (string ids: the watch, the sewer keeper, builders ...) come before the shops, as before
  // B4 — a shop next door must not starve the night watch; BF7's nearest choice holds within each class
  {
    const P = town();
    const a = PEOPLE.newPerson(P, 200, { home: 1, age: 40, seed: 1 });
    const b = PEOPLE.newPerson(P, 200, { home: 1, age: 41, seed: 4 });
    const c = PEOPLE.newPerson(P, 200, { home: 1, age: 42, seed: 5 });
    const jobs = [{ id: 102, kind: "butcher", vacancies: 5, x: 2, z: 0 }, { id: "sewer_keeper", kind: "sewer_keeper", vacancies: 1, x: 300, z: 0 },
                  { id: "watch", kind: "watch", vacancies: 1, x: 90, z: 0 }];
    PEOPLE.dayStep(P, base({ homes: [{ id: 1, room: 0, x: 0, z: 0 }], jobs }));
    const got = [a, b, c].map((q) => q.job).sort((x, y) => String(x).localeCompare(String(y)));
    ok(JSON.stringify(got) === JSON.stringify([102, "sewer_keeper", "watch"]), "the town's posts (watch, sewer keeper) are filled before a nearer shop", got);
    ok(jobs[2].vacancies === 0 && jobs[1].vacancies === 0 && jobs[0].vacancies === 4, "each post taken once, the rest go to the shop", jobs.map((j) => j.vacancies));
    ok([a, b, c].filter((q) => q.job === "watch").length === 1, "one watchman for one post");
  }
  // a3. among the town's posts the nearest wins (BF7 within the class)
  {
    const P = town();
    const a = PEOPLE.newPerson(P, 200, { home: 1, age: 40, seed: 1 });
    const jobs = [{ id: "fisher", kind: "fisher", vacancies: 1, x: 200, z: 0 }, { id: "watch", kind: "watch", vacancies: 1, x: 20, z: 0 }];
    PEOPLE.dayStep(P, base({ homes: [{ id: 1, room: 0, x: 0, z: 0 }], jobs }));
    ok(a.job === "watch", "the nearest of the town's posts", a.job);
  }
  // b. a homeless person: the room nearest his work
  {
    const P = town();
    const a = PEOPLE.newPerson(P, 200, { home: null, job: 105, age: 40, seed: 2 });
    PEOPLE.dayStep(P, base({ homes: [{ id: 1, room: 1, x: 0, z: 0 }, { id: 2, room: 1, x: 190, z: 0 }], jobs: [{ id: 105, kind: "smithy", vacancies: 0, x: 200, z: 0 }] }));
    ok(a.home === 2, "a homeless worker takes the room nearest his work", a.home);
  }
  // c. a newcomer: the room nearest an open job
  {
    const P = town();
    for (let i = 0; i < 6; i++) { const q = PEOPLE.newPerson(P, 200, { home: 1, job: 101, age: 40, seed: 10 + i }); q.mood = 95; }
    P.faucet = 50;
    const homes = [{ id: 1, room: 4, x: 0, z: 0 }, { id: 2, room: 3, x: 300, z: 0 }];
    const r = PEOPLE.dayStep(P, base({ homes, jobs: [{ id: 101, kind: "bakery", vacancies: 0, x: 0, z: 0 }, { id: 109, kind: "quarry", vacancies: 2, x: 290, z: 0 }] }));
    const nb = r.arrivals.length ? PEOPLE.byId(P, r.arrivals[0]) : null;
    ok(nb && nb.home === 2, "a newcomer takes the room nearest an open job", nb && nb.home);
  }
  // d. no home free here for 3 days -> the household moves to another town
  {
    const P = town();
    const a = PEOPLE.newPerson(P, 150, { home: null, job: null, age: 40, seed: 3, sex: "m" });
    const b = PEOPLE.newPerson(P, 150, { home: null, job: null, age: 38, seed: 4, sex: "f" });
    const k = PEOPLE.newPerson(P, 195, { home: null, age: 3, seed: 5, parents: [a.id, b.id] });
    a.spouse = b.id; b.spouse = a.id; a.kids.push(k.id); b.kids.push(k.id);
    a.hl = 5; b.hl = 5; k.hl = 5;
    const asked = [];
    const r = PEOPLE.dayStep(P, base({ homes: [{ id: 1, room: 0, x: 0, z: 0 }], jobs: [], elsewhere: (need) => { asked.push(need); return { id: 9, name: "Brook" }; } }));
    ok(!a.alive && !b.alive && !k.alive && a.left === 200, "no home free: the household leaves (the census's own departure)");
    ok(r.movers.length === 1 && r.movers[0].to === 9 && r.movers[0].ids.length === 3 && r.movers[0].why === "home" && asked[0].people === 3 && !asked[0].job, "it moves as one household of 3 to the town the clock names", r.movers);
    ok(r.departures.includes(a.id) && r.events.some((e) => e.kind === "left" && e.text.includes("Brook")), "a departure and a 'left for Brook' event");
    // adopt into the other town's census
    const Q = PEOPLE.newPeople(); PEOPLE.newPerson(Q, 100, { home: 4 });
    const got = PEOPLE.adopt(Q, r.movers[0].people, 200, 7);
    const ga = got.find((q) => q.name === a.name), gb = got.find((q) => q.name === b.name), gk = got.find((q) => q.name === k.name);
    ok(got.length === 3 && got.every((q) => q.alive && q.home === 7) && ga.spouse === gb.id && gb.spouse === ga.id && gk.parents.includes(ga.id) && ga.kids.includes(gk.id), "they arrive in the other census: home 7, the marriage and the child kept (new ids)");
    ok(ga.born === a.born && ga.sex === a.sex && !ga.hl && Q.list.length === 4, "names, births and sexes kept; counters start fresh");
  }
  // e. none free and no other town: they stay
  {
    const P = town();
    const a = PEOPLE.newPerson(P, 150, { home: null, age: 40, seed: 3 }); a.hl = 9;
    const r1 = PEOPLE.dayStep(P, base({ homes: [], jobs: [], elsewhere: () => null }));
    const r2 = PEOPLE.dayStep(P, base({ day: 201, homes: [], jobs: [] }));
    ok(a.alive && r1.movers.length === 0 && r2.movers.length === 0, "no other town with room: they stay (the unhappy-leave law still applies)");
    const b = PEOPLE.newPerson(P, 150, { home: null, age: 40, seed: 4 }); b.hl = 1;
    const r3 = PEOPLE.dayStep(P, base({ day: 202, homes: [], jobs: [], elsewhere: () => ({ id: 2, name: "X" }) }));
    ok(b.alive && r3.movers.every((m) => !m.ids.includes(b.id)), "only after MOVE.homeless days without a home", MOVE.homeless);
  }
  // f. a free room here: the homeless take it, nobody moves
  {
    const P = town();
    const a = PEOPLE.newPerson(P, 150, { home: null, age: 40, seed: 3 }); a.hl = 9;
    const r = PEOPLE.dayStep(P, base({ homes: [{ id: 3, room: 2, x: 0, z: 0 }], jobs: [], elsewhere: () => ({ id: 2, name: "X" }) }));
    ok(a.alive && a.home === 3 && r.movers.length === 0, "a room here: taken, no move");
  }
  // g. jobless for MOVE.jobless days with no vacancy: moves for work (the other town must have a post)
  {
    const P = town();
    const a = PEOPLE.newPerson(P, 150, { home: 1, age: 40, seed: 3 }); a.jl = 6;
    const asked = [];
    const r = PEOPLE.dayStep(P, base({ homes: [{ id: 1, room: 0, x: 0, z: 0 }], jobs: [{ id: 101, kind: "bakery", vacancies: 0, x: 0, z: 0 }], elsewhere: (n) => { asked.push(n); return { id: 4, name: "Ford" }; } }));
    ok(!a.alive && r.movers[0].why === "job" && asked[0].job === true, "no work for 5 days and none free: moves to a town with a post");
    const P2 = town();
    const c = PEOPLE.newPerson(P2, 150, { home: 1, age: 40, seed: 3 }); c.jl = 6;
    PEOPLE.dayStep(P2, base({ homes: [{ id: 1, room: 0, x: 0, z: 0 }], jobs: [{ id: 101, kind: "bakery", vacancies: 1, x: 0, z: 0 }], elsewhere: () => ({ id: 4, name: "Ford" }) }));
    ok(c.alive && c.job === 101, "a vacancy here: he takes it and stays");
  }
  // h. a home over 160 blocks from work: the household takes a free room within 80 of the work, one a town a day
  {
    const P = town();
    const a = PEOPLE.newPerson(P, 150, { home: 1, job: 101, age: 40, seed: 3, sex: "m" });
    const b = PEOPLE.newPerson(P, 150, { home: 1, job: null, age: 39, seed: 4, sex: "f" });
    a.spouse = b.id; b.spouse = a.id;
    const c = PEOPLE.newPerson(P, 150, { home: 2, job: 101, age: 40, seed: 5 });
    const homes = [{ id: 1, room: 0, x: 0, z: 0 }, { id: 2, room: 0, x: 10, z: 0 }, { id: 3, room: 3, x: 290, z: 0 }, { id: 4, room: 3, x: 200, z: 0 }];
    const r = PEOPLE.dayStep(P, base({ homes, jobs: [{ id: 101, kind: "quarry", vacancies: 0, x: 300, z: 0 }] }));
    ok(a.home === 3 && b.home === 3 && homes[2].room === 1 && homes[0].room === 2, "the far household moves into the free room nearest the work (both of them)", [a.home, b.home]);
    ok(c.home === 2 && r.farMoved === 1 && r.far === 2, "one move a town a day (the next waits)", [c.home, r.far, r.farMoved]);
    const P3 = town();
    const d = PEOPLE.newPerson(P3, 150, { home: 1, job: 101, age: 40, seed: 3 });
    const dayC = 200 + ((10 - ((200 + d.id) % 10)) % 10);
    const r3 = PEOPLE.dayStep(P3, base({ day: dayC, homes: [{ id: 1, room: 0, x: 0, z: 0 }], jobs: [{ id: 101, kind: "quarry", vacancies: 0, x: 300, z: 0 }] }));
    ok(d.home === 1 && r3.events.some((e) => e.kind === "far" && e.text.includes("300 blocks")), "no room near work: he complains (every 10 days)", r3.events.map((e) => e.kind));
  }
  // i. children never move alone
  {
    const P = town();
    const a = PEOPLE.newPerson(P, 150, { home: 1, job: 101, age: 40, seed: 3 });
    const k = PEOPLE.newPerson(P, 196, { home: 1, age: 4, seed: 6, parents: [a.id] }); a.kids.push(k.id);
    const k2 = PEOPLE.newPerson(P, 196, { home: 5, age: 4, seed: 7, parents: [a.id] }); a.kids.push(k2.id);
    const hh = PEOPLE.household(P, a, 200);
    ok(hh.length === 2 && hh.includes(k) && !hh.includes(k2), "the household = him, a spouse at home and the children living there");
    PEOPLE.dayStep(P, base({ homes: [{ id: 1, room: 0, x: 0, z: 0 }, { id: 3, room: 2, x: 290, z: 0 }], jobs: [{ id: 101, kind: "quarry", vacancies: 0, x: 300, z: 0 }] }));
    ok(a.home === 3 && k.home === 3 && k2.home === 5, "the child at home moves with the parent; nobody else moves");
  }
  // j. beds counted from the template (two bed blocks = one bed); the base is off by default
  {
    const fam = (stem) => Object.values(CIV_BUILDINGS).find((d) => d.stem === stem);
    ok(PEOPLE.bedsOf(fam("mvv_cottage_s_a_r1").dir) === 1 && PEOPLE.bedsOf(fam("mvv_inn_a_r1").dir) === 4 && PEOPLE.bedsOf(fam("mvv_manor_a_r1").dir) === 11 && PEOPLE.bedsOf([]) === 0, "beds: cottage_s 1, inn 4, manor 11");
    ok(PEOPLE.PLACES.BEDS_BASE === false, "BEDS_BASE is off (capacity stays HOUSEHOLD x DENSITY)");
  }
  // k. a rest day carries no fatigue (B3's hook, fed by BF5)
  {
    const mk = () => { const P = town(); for (let i = 0; i < 4; i++) PEOPLE.newPerson(P, 100, { home: 1, job: 101, age: 40, seed: i }); return P; };
    const P1 = mk(), P2 = mk();
    const ctx = (o) => base({ homes: [{ id: 1, room: 0, x: 0, z: 0 }], jobs: [{ id: 101, kind: "bakery", vacancies: 6, x: 0, z: 0 }], ...o });
    for (let d = 0; d < 4; d++) { PEOPLE.dayStep(P1, ctx({ day: 200 + d })); PEOPLE.dayStep(P2, ctx({ day: 200 + d, restOf: () => true })); }
    ok(PEOPLE.meanMood(P2) > PEOPLE.meanMood(P1), "an understaffed shop tires its people, but not on their day off", [PEOPLE.meanMood(P1), PEOPLE.meanMood(P2)]);
  }
}

// ------------------------------------------------------------------------------------------------ 9. save cost: derived, not stored
{
  const P = PEOPLE.newPeople();
  for (let i = 0; i < 50; i++) PEOPLE.newPerson(P, 100, { home: 1, job: 101, age: 40, seed: i });
  const before = JSON.stringify(P).length;
  for (const q of P.list) { PEOPLE.shiftAt(q, 5000, 9, { travel: 600 }); PEOPLE.beatOf(q.id, 9000); PEOPLE.dayOff(q, 9); }
  ok(JSON.stringify(P).length === before && P.list.every((q) => q.shift === undefined), "shifts, offsets, plans and beats write nothing to the census");
}

console.log(`test_shifts: ${pass}/${pass + fail} passed`);
if (fail) process.exit(1);
