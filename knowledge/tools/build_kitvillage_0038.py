#!/usr/bin/env python3
"""build_kitvillage_0038.py — the gate probe 0.0.38 for BP-02 1.3.226 build 3 (his 21:51 witness: "the messages say things
are happening, but nothing is developing" — plots stayed pits at speed 20): after VILLAGE II is chartered the probe runs
the clock in REAL TIME (resume, speed 20 = a village day every 1,200 ticks) for 7,200 ticks and counts the stage changes
and the labour sites before and after ([CIVTEST] step "realtime"); the gate fails when nothing rose. Then it pauses and
the skip ladder goes on as before. Usage: python3 tools/build_kitvillage_0038.py"""
import json
import shutil
from pathlib import Path

B = Path("/home/claude/_build")
SRC, DST = B / "kitvillage-0.0.37", B / "kitvillage-0.0.38"


def rep(t, old, new, n=1):
    assert t.count(old) == n, (old[:80], t.count(old))
    return t.replace(old, new)


def main():
    if DST.exists():
        raise SystemExit(f"never rebuild {DST}")
    shutil.copytree(SRC, DST)
    mp = DST / "manifest.json"
    m = json.loads(mp.read_text())
    m["header"]["name"] = "PW KitVillage probe 0.0.38 (BDS only)"
    m["header"]["version"] = [0, 0, 38]
    for mod in m["modules"]:
        mod["version"] = [0, 0, 38]
    mp.write_text(json.dumps(m, indent=1))
    p = DST / "scripts/main.js"
    t = p.read_text()
    t = rep(t, "    await waitQueue(dim, cmd, 200);\n    await readback(dim);\n",
            '''    await waitQueue(dim, cmd, 200);
    await readback(dim);
    if (cmd === "grow" && expect === "village II") {          // 0.0.38: REAL TIME (his 21:51) — speed 20, 7,200 ticks
      const stagesOf = () => [...blds.values()].reduce((a, b) => a + Math.max(0, b.stage), 0);
      const laborOf = () => [...blds.values()].filter((b) => b.labor).length;
      const s0 = stagesOf(), l0 = laborOf(), t0 = system.currentTick;
      dim.runCommand("scriptevent pw:clock speed 20"); dim.runCommand("scriptevent pw:clock resume");
      for (let k = 0; k < 12; k++) { await sleep(600); }
      dim.runCommand("scriptevent pw:clock pause");
      await sleep(20); await readback(dim);
      const s1 = stagesOf(), l1 = laborOf();
      log({ step: "realtime", ticks: system.currentTick - t0, stagesBefore: s0, stagesAfter: s1, rose: s1 - s0, laborBefore: l0, laborAfter: l1,
            sites: [...blds.values()].filter((b) => b.labor).map((b) => [b.id, b.labor.k, Math.round(b.labor.done), b.labor.need, b.labor.crew || 0, Math.round((b.labor.crewDays || 0) * 10) / 10]).slice(0, 12) });
    }
''')
    p.write_text(t)
    print(f"DONE {DST}")


if __name__ == "__main__":
    main()
