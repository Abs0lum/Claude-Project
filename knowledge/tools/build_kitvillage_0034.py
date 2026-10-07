#!/usr/bin/env python3
"""build_kitvillage_0034.py — the gate probe 0.0.34 for BP-02 1.3.224 (his 16:50 report):
  * waitQueue also waits for the TIER WORK (a grow is now laid out plot by plot over beats);
  * VILLAGERS: at dusk and at work hours — how many stand within 4 of the well's centre, the market clerk(s), keepers at
    their stations (distance), the civs' spread over distinct cells;
  * BEYOND CITY II (his crash): grow -> CITY III, skip 24, grow -> METROPOLIS, skip 24 — the tier, plots, leftovers
    (the server runs with script-watchdog-hang-threshold=3000: any tick over 3 s kills the run = a failed gate).
Usage: python3 tools/build_kitvillage_0034.py"""
import json
import shutil
from pathlib import Path

B = Path("/home/claude/_build")
SRC, DST = B / "kitvillage-0.0.32", B / "kitvillage-0.0.34"


def rep(t, old, new):
    assert t.count(old) == 1, old[:80]
    return t.replace(old, new)


def main():
    if DST.exists():
        raise SystemExit(f"never rebuild {DST}")
    shutil.copytree(SRC, DST)
    mp = DST / "manifest.json"
    m = json.loads(mp.read_text())
    m["header"]["name"] = "PW KitVillage probe 0.0.34 (BDS only)"
    m["header"]["version"] = [0, 0, 34]
    for mod in m["modules"]:
        mod["version"] = [0, 0, 34]
    mp.write_text(json.dumps(m, indent=1))
    p = DST / "scripts/main.js"
    t = p.read_text()
    t = rep(t, "    if (st && q === 0 && !(st.lag > 0)) break;                 // 0.0.13: skipped days run one per beat (s.lag)",
            "    if (st && q === 0 && !(st.lag > 0) && !st.tierWork) break;   // 0.0.13: skipped days run one per beat (s.lag); 0.0.33: a tier's plots are laid over beats")
    t = rep(t, "  log({ step: \"roadcells\",", '''  // 0.0.33 (1.3.224, his 16:50): THE VILLAGERS — spread, the market clerk, the keepers at their posts
  {
    const civStats = async (label) => {
      await readback(dim);
      const st = stls[0];
      if (!st || !st.square) { log({ step: "civs", label, err: "no square" }); return; }
      const wx = st.square.x + 5.5, wz = st.square.z + 6, sy = st.square.y;
      let vs = [];
      try { vs = dim.getEntities({ type: "minecraft:villager_v2", tags: ["civ:villager"] }); } catch { vs = []; }
      const nearWell = vs.filter((v) => Math.hypot(v.location.x - wx, v.location.z - wz) <= 4).length;
      const cells = new Set(vs.map((v) => `${Math.floor(v.location.x)},${Math.floor(v.location.z)}`));
      const clerks = vs.filter((v) => v.getTags().some((g) => g.startsWith("civ:market:"))).map((v) => [v.nameTag, Math.round(v.location.x * 10) / 10, Math.round(v.location.z * 10) / 10, Math.round(Math.hypot(v.location.x - (st.square.x + 1.5), v.location.z - (st.square.z + 1.5)) * 10) / 10]);
      const keepersAt = vs.filter((v) => v.hasTag("civ:keeper") && !v.getTags().some((g) => g.startsWith("civ:market:"))).length;
      let stall = null; try { stall = [dim.getBlock({ x: st.square.x + 2, y: sy + 1, z: st.square.z + 1 })?.typeId, dim.getBlock({ x: st.square.x + 1, y: sy + 2, z: st.square.z })?.typeId]; } catch { stall = null; }
      log({ step: "civs", label, total: vs.length, nearWell, distinctCells: cells.size, clerks, keepers: keepersAt, stall, mclerk: st.mclerk || null });
    };
    dim.runCommand("time set 3000"); await sleep(1200); await civStats("work hours (3000)");
    dim.runCommand("time set 11500"); await sleep(1200); await civStats("dusk (11500)");
    dim.runCommand("time set 3000"); await sleep(200);
  }
  // 0.0.33: BEYOND CITY II (his crash: the watchdog 'Hang' when he grew past city 2) — the server's hang limit is 3 s here
  {
    for (const [cmd, expect] of [["grow", "CITY III"], ["skip 24", "city III built"], ["grow", "METROPOLIS"], ["skip 24", "metropolis built"]]) {
      const t0 = Date.now();
      dim.runCommand(`scriptevent pw:clock ${cmd}`);
      await sleep(40);
      await waitQueue(dim, cmd, 400);
      await readback(dim);
      const st = stls[0];
      log({ step: "beyond", cmd, expect, tier: st && st.tier, plots: blds.size, tierWork: st && st.tierWork ? [st.tierWork.i, st.tierWork.items.length] : null, leftover: st && st.leftover && st.leftover.length, landRejects: st && st.landRejects, slotWhy: st && st.slotWhy, secs: Math.round((Date.now() - t0) / 1000), chronicle: st && st.log && st.log.slice(-6) });
    }
  }
  log({ step: "roadcells",''')
    # 0.0.34: the world dump read a 476 x 476 layer per tick (~3 s: the probe's own Hang under the 3 s limit) - a pause every 40 columns
    t = rep(t, "    for (let x = x0; x <= x1; x++) for (let z = z0; z <= z1; z++) {\n      let blk;\n      try { blk = dim.getBlock({ x, y, z }); } catch { blk = undefined; }\n      let k = -1;",
            "    for (let x = x0; x <= x1; x++) { if ((x - x0) % 40 === 39) await sleep(1); for (let z = z0; z <= z1; z++) {\n      let blk;\n      try { blk = dim.getBlock({ x, y, z }); } catch { blk = undefined; }\n      let k = -1;")
    t = rep(t, "      if (k === last) n++; else { if (n) runs.push(n > 1 ? `${last}*${n}` : `${last}`); last = k; n = 1; }\n    }\n    runs.push(",
            "      if (k === last) n++; else { if (n) runs.push(n > 1 ? `${last}*${n}` : `${last}`); last = k; n = 1; }\n    } }\n    runs.push(")
    p.write_text(t)
    print(f"DONE {DST}")


if __name__ == "__main__":
    main()
