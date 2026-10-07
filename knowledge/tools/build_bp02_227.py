#!/usr/bin/env python3
"""build_bp02_227.py — BP-02 1.3.227 from 1.3.226: THE CITY RUNS SMOOTHLY (gate 226-2: a 3,170 ms watchdog hang at city II,
150 buildings; the profiler on that world found where the script time went).

  1. The SCHEDULE (every civ's goal) is a job: a pass gives the tick back after each civ, and what the goals read is gathered
     once per pass (buildings by id, the labour sites, the open shops, each household's shopper — this was a scan of the
     whole census per civ at market hours).
  2. The census lookup (PEOPLE.byId) is indexed; the workshops' hands cache uses it.
  3. Route planning shares 40 ms a tick (WALK.send); the walkers' sweep turns off only the follow groups still on.
  4. Shopkeepers: one lookup per keeper; their standing anchor is renewed only when it runs low.
  5. The Naturalist add-on's per-tick loops: the kakapo music check keeps only kakapos (it walked EVERY entity every tick —
     the hang was interrupted inside it), the deer graze check runs every 4 ticks (chances x4), the fowl flutter tracks
     its birds instead of 18 entity queries every 2 ticks.
  6. The town is saved every 30 s (it was every 5 s: 13-23 MB of dynamic properties a minute at city II).
  7. pw:rat_wa, pw:hedgehog_wa (erizo) and pw:giant_rat_wa had two navigation components (his content log): the generic one,
     which the engine refused, is removed (the walk one was the one in use).
  8. The tier work AND the daily leftover plots run one search phase per tick (gate 227-2: plan day 1,557 ms); stage
     placements share 200 ms a call (a carried day of 1,348 ms); the sewer-outfall veto is cached.
  9. His 00:54 (10-06): a tree in town with under 30 % of its original crown is taken down (canopyDaily).
  10. Gate 227-3 (twice): the server was OOM-killed at metropolis (5.9 GB). memprobe-0.0.1: Block.below() / above() /
      offset() leak ~650 B of server memory per call, never freed (dimension.getBlock / getTopmostBlock do not). The ground
      reader walked down with below() in every slot search. All such calls now use dimension.getBlock at the computed cell
      (pw_civ_clock groundAt + site survey, pw_companion, pw_homestead, and the add-on scripts AntHill, Flyingfish, Sloth).
  11. Gate 227-4 still grew (+90 MB / 30 s at metropolis). memprobe: EVERY Script API call that THROWS leaks ~650 B (3 M
      out-of-bounds getBlock throws: +1.94 GB); the planners' topmost-block reads at the edge of the loaded land threw
      "unloaded chunk" (leakdiag: 140 k throws = +92 MB). The hot reads (ground, water, site survey, leaf sweep, tree and
      canopy measures, walk graph) ask isChunkLoaded first and check isValid; the remaining throws are counted (STATESIZE).
Usage: python3 tools/build_bp02_227.py   (bp02-227 must not exist)"""
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

B = Path("/home/claude/_build")
SRC, DST = B / "bp02-226", B / "bp02-227"
JS = Path("/home/claude/tools/bp02_src_227")
VERSION = [1, 3, 227]
NAV2 = ["entities/pw_menagerie/wa/rat.json", "entities/pw_menagerie/wa/erizo.json", "entities/pw_giants/giant_rat_wa.json"]


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def rep(text, old, new, what):
    assert text.count(old) == 1, f"{what}: {text.count(old)} matches"
    return text.replace(old, new)


def main():
    if DST.exists():
        raise SystemExit(f"never rebuild {DST}")
    base = dict(line.split()[::-1] for line in (JS / "BASE-226.md5").read_text().splitlines())
    for name, h in base.items():
        assert md5(SRC / "scripts" / name) == h, f"226 drifted: {name}"
    for test in sorted((JS / "tests").glob("test_*.mjs")):
        r = subprocess.run(["node", str(test)], capture_output=True, text=True, cwd=JS)
        assert r.returncode == 0, f"{test.name}: {r.stdout[-800:]} {r.stderr[-400:]}"
        print(r.stdout.strip().splitlines()[-1])
    shutil.copytree(SRC, DST)
    changed = []
    for p in sorted(JS.rglob("*.js")):
        rel = p.relative_to(JS)
        if rel.parts[0] in ("node_modules", "tests"):
            continue
        ref = SRC / "scripts" / rel
        assert ref.exists(), f"new script {rel}: not expected in 227"
        if md5(ref) != md5(p):
            shutil.copy2(p, DST / "scripts" / rel)
            changed.append(str(rel))
    # the double navigation (his content log 21:51): keep navigation.walk, drop navigation.generic
    for rel in NAV2:
        fp = DST / rel
        d = json.loads(fp.read_text())
        comps = d["minecraft:entity"]["components"]
        assert "minecraft:navigation.generic" in comps and "minecraft:navigation.walk" in comps, rel
        del comps["minecraft:navigation.generic"]
        fp.write_text(json.dumps(d, indent=1))
        changed.append(rel)
    mp = DST / "manifest.json"
    m = json.loads(mp.read_text())
    m["header"]["version"] = VERSION
    m["header"]["name"] = "AbsolutRealism Tectonic BP v1.3.227"
    for mod in m["modules"]:
        mod["version"] = VERSION
    m["header"]["description"] = ("v1.3.227 (2026-10-05) THE CITY RUNS SMOOTHLY: the villagers' daily schedule, route planning, shopkeepers and "
                                  "the Naturalist animals' scripts no longer pile into one tick (the 3-second freeze at city II); the town saves "
                                  "every 30 s. Includes 1.3.226 (survey, homes outward, the core, lanes, every home on the sewer, fishermen). "
                                  "Needs RP-01 1.3.124 + RP-12 1.0.1. Personal use.")
    mp.write_text(json.dumps(m, indent=1))
    mj = DST / "scripts/main.js"
    mj.write_text(rep(mj.read_text(), 'const PW_BUILD = "1.3.226";', 'const PW_BUILD = "1.3.227";', "PW_BUILD"))
    cp = DST / "scripts/pw_companion.js"
    cp.write_text(rep(cp.read_text(), "companion v7 LOADED (pack v1.3.226", "companion v7 LOADED (pack v1.3.227", "companion"))
    for p in sorted((DST / "scripts").rglob("*.js")):
        r = subprocess.run(["node", "--check", str(p)], capture_output=True, text=True)
        assert r.returncode == 0, f"{p.name}: {r.stderr[:300]}"
    r = subprocess.run([sys.executable, "/home/claude/tools/js_dupcheck.py"] + [str(p) for p in sorted((DST / "scripts").glob("*.js"))], capture_output=True, text=True)
    assert r.returncode == 0, f"duplicate globals: {r.stdout[:600]}"
    print(f"DONE {DST} · changed: {', '.join(changed)} · manifest + PW_BUILD 1.3.227")


if __name__ == "__main__":
    main()
