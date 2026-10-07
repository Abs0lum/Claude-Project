#!/usr/bin/env python3
"""kit_village_probe_031.py — probe 0.0.31 = the 0.0.29 kit-village ladder (tools/kit_village_probe.py) + THE PALACE
(D-C570, BP-02 1.3.222): after the bench, `grow` to city II and poll the clock a survey day at a time until the Seat of
Government is laid (palace block search + the crown's survey ticking area), then skip in fours until the four quarters
stand furnished in lockstep; verify each piece cell by cell against its model, count the hidden world's blocks
(pw:jib_panel, pw:secret_painting) in the palace box, read the terrace under the corners. Manifests are re-read from
BP-02 1.3.222 (the palace pieces from _staging/civ/palace/manifests).
Usage: kit_village_probe_031.py OUT_PROBE_DIR  (then: bds_civtest.py --seconds 3600 BP02-221 MARKERS-0.2.4 OUT_PROBE_DIR)"""
import json
import sys
import uuid
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
import kit_village_probe as P  # noqa: E402
import mcstructure as M  # noqa: E402

BP221 = Path("/home/claude/_build/bp02-222")
P.BP219 = BP221


def manifests():
    t = (P.SHORT / "civ_manifests.js").read_text()
    j = json.loads(t[t.index("{"):t.rindex("}") + 1])
    for mdir in (Path("/home/claude/_staging/civ/manifests"), Path("/home/claude/_staging/civ/palace/manifests")):
        for mf in sorted(mdir.glob("*.json")):
            fam = "pw:" + mf.stem
            if fam in j or not (BP221 / "structures/pw" / (mf.stem + ".mcstructure")).exists():
                continue
            sm = json.loads(mf.read_text())
            j[fam] = {"name": sm.get("name", fam), "size": sm["size"], "datum_y": sm.get("datum_y", 0), "ents": sm.get("entities", [])}
    for fam, m in j.items():
        st = M.Structure.from_bytes((BP221 / "structures/pw" / (fam.split(":")[1] + ".mcstructure")).read_bytes())
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
    return f"// kit_village_probe_031.py: {len(j)} manifests, cells re-read from BP-02 1.3.222\nexport const MANIFESTS = " + json.dumps(j, separators=(",", ":")) + ";\n"


PALACE = r'''
  // 0.0.30 (D-C570): THE PALACE — city II lays the Seat of Government; the four quarters rise in lockstep as the crown's works
  {
    dim.runCommand("scriptevent pw:clock grow");                 // city I -> city II
    await sleep(40);
    await waitQueue(dim, "grow city2", 200);
    let st = null, found = false;
    for (let i = 0; i < 40 && !found; i++) {                     // a survey day at a time: the search, the crown's ticking area, the chunk load
      dim.runCommand("scriptevent pw:clock skip 2");
      await sleep(80);
      await waitQueue(dim, "palace search", 200);
      await readback(dim);
      st = stls[0];
      found = !!(st && st.palace);
      if (i % 5 === 4 || found) log({ step: "palacesearch", i, tier: st && st.tier, palace: st && st.palace, search: st && st.palaceSearch, pending: st && st.palacePending, tries: st && st.palaceTries, ticking: st && st.ticking });
    }
    if (!found) { log({ step: "palace", err: "not laid after 80 survey days", search: st && st.palaceSearch, ticking: st && st.ticking, chronicle: st && st.log }); }
    else {
      // the stages: 28 village days in lockstep (6 + 8 + 8 + 6); poll until all four stand furnished and placed
      let pieces = [];
      for (let i = 0; i < 60; i++) {
        dim.runCommand("scriptevent pw:clock skip 2");
        await sleep(80);
        await waitQueue(dim, "palace stages", 300);
        await readback(dim);
        pieces = [...blds.values()].filter((b) => b.palace);
        const stages = pieces.map((b) => [b.palace.q, b.stage, b.pending.length, b.filled ?? null]);
        if (i % 3 === 2) log({ step: "palacestages", i, stages, ticking: stls[0] && stls[0].ticking });
        if (pieces.length === 4 && pieces.every((b) => b.stage >= 4 && !b.pending.length)) { log({ step: "palacestages", i, stages, done: true }); break; }
      }
      await sleep(100);
      // the palace's chunks must tick for the verify and the gallery: one 160 x 160 area over the block (the probe holds 5 of 10 slots, the clock up to 4)
      try { const pal0 = stls[0] && stls[0].palace; if (pal0) { const ax = Math.floor((pal0.x0 - 2) / 16) * 16, az = Math.floor((pal0.z0 - 2) / 16) * 16; dim.runCommand(`tickingarea add ${ax} -64 ${az} ${ax + 159} 320 ${az + 159} palace true`); await sleep(200); } } catch (e) { log({ step: "palacearea", err: String(e) }); }
      // verify the four pieces against the stage-4 model at a stride of 2 (49k cells each; the full 196k in one tick would
      // trip the probe's own 10 s watchdog), one piece per tick
      const results = [];
      const verifySparse = (b) => {
        const man = MANIFESTS[b.family];
        const [sx, sy, sz] = man.size;
        let cells = 0, badId = 0, badState = 0;
        const firstBad = [];
        for (let x = 0; x < sx; x += 2) for (let y = man.datum_y - 2; y < sy; y += 2) for (let z = 0; z < sz; z += 2) {   // below the foundations the land is the world's own (light s0)
          const k = man.idx[(x * sy + y) * sz + z];
          if (k < 0) continue;
          const [name, states] = man.pal[k];
          const [ox, oz] = rotXZ(x, z, sx, sz, b.rot);
          const blk = dim.getBlock({ x: b.x + ox, y: b.y + y, z: b.z + oz });
          cells++;
          const same = blk && (blk.typeId === name || (name === "minecraft:dirt" && blk.typeId === "minecraft:grass_block"));
          if (!same) { badId++; if (firstBad.length < 6) firstBad.push([x, y, z, name, blk && blk.typeId]); continue; }
          const w = want(states, sx, sz, b.rot), g = blk.permutation.getAllStates();
          if (name.includes("door") || name.includes("gate") || name.includes("trapdoor")) delete w.open_bit;
          const diff = Object.entries(w).filter(([q, v]) => (typeof g[q] === "boolean" ? g[q] !== Boolean(v) : g[q] !== v));
          if (diff.length) { badState++; if (firstBad.length < 6) firstBad.push([x, y, z, name, JSON.stringify(Object.fromEntries(diff))]); }
        }
        return { cells, badId, badState, firstBad, ok: badId === 0 && badState === 0 };
      };
      for (const b of pieces) {
        let r;
        try { r = verifySparse(b); } catch (e) { results.push([b.id, b.palace.q, "verify threw", String(e).slice(0, 160)]); await sleep(1); continue; }
        results.push({ id: b.id, q: b.palace.q, rot: b.rot, at: [b.x, b.y, b.z], ok: r.ok, cells: r.cells, badId: r.badId, badState: r.badState, firstBad: r.firstBad.slice(0, 4) });
        await sleep(1);
      }
      // the hidden world: our two walk-through blocks inside the palace box (every other column, 36 layers), the terrace under the corners
      const pal = stls[0] && stls[0].palace;
      const counts = { jib: 0, painting: 0, water: 0, air: 0 };
      if (pal) {
        for (let x = pal.x0; x < pal.x0 + 128; x += 2) {
          for (let z = pal.z0; z < pal.z0 + 128; z += 2) for (let y = pal.H - 1; y < pal.H + 35; y++) {
            let id; try { id = dim.getBlock({ x, y, z })?.typeId; } catch { id = undefined; }
            if (id === "pw:jib_panel") counts.jib++; else if (id === "pw:secret_painting") counts.painting++; else if (id === "minecraft:water") counts.water++; else if (id === "minecraft:air") counts.air++;
          }
          if (x % 4 === 0) await sleep(1);
        }
        counts.under = [[0, 0], [127, 0], [0, 127], [127, 127], [64, 64], [64, 0], [0, 64]].map(([i, j]) => { let a, b2; try { a = dim.getBlock({ x: pal.x0 + i, y: pal.H - 1, z: pal.z0 + j })?.typeId; b2 = dim.getBlock({ x: pal.x0 + i, y: pal.H - 6, z: pal.z0 + j })?.typeId; } catch { a = "?"; } return [i, j, a, b2]; });
      }
      log({ step: "palace", palace: pal, pieces: results, counts, chronicle: stls[0] && stls[0].log });
      try { dim.runCommand("scriptevent pw:clock log"); } catch { /* */ }
      await sleep(2);
    }
  }
'''

GALLERY = r"""
  // 0.0.31 (D-C571 v2): THE GALLERY — unique pictures hang in every furnished building and the palace; the registry never repeats
  {
    await sleep(100);
    await readback(dim);
    const bs = [...blds.values()];
    const perB = [];
    const seen = new Map();
    let total = 0, dup = 0;
    for (const b of bs) {
      const m = MANIFESTS[b.family]; if (!m) continue;
      const [fx, fz] = b.rot % 2 ? [m.size[2], m.size[0]] : [m.size[0], m.size[2]];
      let arts = [];
      try { arts = dim.getEntities({ location: { x: b.x - 1, y: b.y, z: b.z - 1 }, volume: { x: fx + 2, y: m.size[1], z: fz + 2 }, tags: ["pw_art"] }); } catch { arts = []; }
      const ids = arts.map((e) => e.typeId.replace("pw:art_", ""));
      for (const e of arts) { const id = e.typeId.replace("pw:art_", ""); if (seen.has(id) && seen.get(id) !== e.id) dup++; if (!seen.has(id)) seen.set(id, e.id); }   // a repeat = the same WORK on two entities (a boundary picture counted from two boxes is not one)
      total += ids.length;
      perB.push([b.id, b.family.replace("pw:mvv_", ""), b.stage, [b.art ?? null, b.artNext ?? null, b.artDone ?? null], ids.length, ids.slice(0, 3), arts.slice(0, 2).map((e) => [Math.round(e.location.x * 2) / 2, Math.round(e.location.y * 2) / 2, Math.round(e.location.z * 2) / 2, e.getProperty("pw:facing")])]);
      await sleep(1);
    }
    let status = null;
    try { dim.runCommand("scriptevent pw:gallery status"); } catch { /* */ }
    log({ step: "gallery", total, distinct: seen.size, duplicates: dup, buildings: perB.length, perBuilding: perB.slice(0, 48) });
    // the test ring: six works around the square (the registry + spawn path without the clock)
    try { const sq = stls[0] && stls[0].square; if (sq) { dim.runCommand(`scriptevent pw:gallery testat ${sq.x + 6} ${sq.y + 1} ${sq.z + 6} 6`); } } catch (e) { log({ step: "gallerytest", err: String(e) }); }
    await sleep(20);
    let ring = [];
    try { const sq = stls[0] && stls[0].square; if (sq) ring = dim.getEntities({ location: { x: sq.x + 6, y: sq.y, z: sq.z + 6 }, maxDistance: 12, tags: ["gallery:test"] }).map((e) => [e.typeId, e.getProperty("pw:facing")]); } catch { ring = []; }
    log({ step: "gallerytest", ring });
  }
"""


def build(out):
    out = Path(out)
    if out.exists():
        raise SystemExit(f"never rebuild {out}")
    (out / "scripts").mkdir(parents=True)
    (out / "scripts/civ_manifests.js").write_text(manifests())
    main = P.MAIN.replace("__MODE__", "full")
    anchor = "  // 0.0.25: THE WALK TEST"
    assert main.count(anchor) == 1
    main = main.replace(anchor, PALACE + GALLERY + anchor)
    (out / "scripts/main.js").write_text(P.HEAD + main)
    json.dump({"format_version": 2,
               "header": {"name": "PW KitVillage probe 0.0.31 (BDS only)", "description": "StreetKit village + the palace read back", "uuid": str(uuid.uuid4()),
                          "version": [0, 0, 31], "min_engine_version": [1, 21, 120]},
               "modules": [{"type": "script", "language": "javascript", "entry": "scripts/main.js", "uuid": str(uuid.uuid4()), "version": [0, 0, 31]},
                           {"type": "data", "uuid": str(uuid.uuid4()), "version": [0, 0, 31]}],
               "dependencies": [{"module_name": "@minecraft/server", "version": "2.3.0"}]}, open(out / "manifest.json", "w"), indent=1)
    print("built", out)


if __name__ == "__main__":
    build(sys.argv[1])
