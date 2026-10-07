#!/usr/bin/env python3
"""build_bp02_228.py — BP-02 1.3.228 from 1.3.227 (program 228: the civ-mods features, batch by batch). Batches in this build: B1 heartbeat + engine hygiene, B2 sectioned saves + why-idle + real-tree felling, B3 needs/moods, B4 shifts, day-tail, stepped tier marks, ramp8 streets, palace vault, trees, benches.
(History of 1.3.227 below.)
build_bp02_227.py — BP-02 1.3.227 from 1.3.226: THE CITY RUNS SMOOTHLY (gate 226-2: a 3,170 ms watchdog hang at city II,
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
import os
import shutil
import subprocess
import sys
from pathlib import Path

B = Path("/home/claude/_build")
SRC, DST = B / "bp02-227", B / "bp02-228"
JS = Path("/home/claude/tools/bp02_src_228")
VERSION = [1, 3, 228]
NEW_SCRIPTS = {"pw_civ_beat.js", "pw_civ_save.js", "pw_civ_talk.js", "pw_civ_voice.js", "pw_civ_plan.js", "pw_civ_names.js", "pw_civ_player.js", "pw_civ_guest.js", "pw_civ_court.js", "pw_civ_court_data.js"}      # program 228 B1 / B2 / B5
NAV2 = ["entities/pw_menagerie/wa/rat.json", "entities/pw_menagerie/wa/erizo.json", "entities/pw_giants/giant_rat_wa.json"]


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def rep(text, old, new, what):
    assert text.count(old) == 1, f"{what}: {text.count(old)} matches"
    return text.replace(old, new)


def main():
    if DST.exists():
        raise SystemExit(f"never rebuild {DST}")
    base = dict(line.split()[::-1] for line in (JS / "BASE-227.md5").read_text().splitlines())
    for name, h in base.items():
        assert md5(SRC / "scripts" / name) == h, f"227 drifted: {name}"
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
        if not ref.exists():
            assert str(rel) in NEW_SCRIPTS, f"new script {rel}: not in NEW_SCRIPTS"
            shutil.copy2(p, DST / "scripts" / rel)
            changed.append(f"{rel} (new)")
            continue
        if md5(ref) != md5(p):
            shutil.copy2(p, DST / "scripts" / rel)
            changed.append(str(rel))
    # program 228: regenerated non-script files (structures, blocks, items…) from the generators, mirrored into the pack
    OV = Path("/home/claude/tools/bp02_overlay_228")
    if OV.exists():
        for p in sorted(OV.rglob("*")):
            if p.is_file():
                rel = p.relative_to(OV)
                (DST / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, DST / rel)
                changed.append(f"{rel} (overlay)")
    mp = DST / "manifest.json"
    m = json.loads(mp.read_text())
    m["header"]["version"] = VERSION
    m["header"]["name"] = "AbsolutRealism Tectonic BP v1.3.228"
    for mod in m["modules"]:
        mod["version"] = VERSION
    # B12 (his 12:20 + the BDS probe 2026-10-06 21:02Z: BDS 1.26.52 loads @minecraft/server 2.10.0 + server-ui 2.0.0):
    # the Script API moves 2.3.0 -> 2.10.0 (PW_API=2.3.0 builds the old one for a side-by-side check)
    for dep in m.get("dependencies", []):
        if dep.get("module_name") == "@minecraft/server": dep["version"] = os.environ.get("PW_API", "2.10.0")
    m["header"]["description"] = ("v1.3.228 (2026-10-06) program 228: one heartbeat for every town system, chunk-checked block reads, sectioned saves, "
                                  "why-idle codes (pw:clock why), real-tree felling with claimed work sites; needs + moods + shifts (rain shelter, "
                                  "workshop output never below half), daily chores spread over ticks, tier marks stepped; 8-block street ramps "
                                  "(preferred) in 19 stones + smooth-stone sidewalk ramps; palace vaulted hall + passage lean roof; tree trunk tips; "
                                  "park benches; civs speak (bubbles, petitions, overheard talk); weighted growth, district skins + names, town titles; "
                                  "weathering + council repairs; silver nickels, exact prices, notices, carters, the tax dial; the watch's pay, "
                                  "morale, alarm bell + civs banding against monsters; the chronicle; standing prices, gifts, festivals, "
                                  "the dusk speech, titles, a guide. Script API 2.10.0. Includes 1.3.227. Needs RP-01 1.3.125 + RP-04 1.3.159 + RP-13 1.0.0 + RP-12 1.0.1. Personal use.")
    mp.write_text(json.dumps(m, indent=1))
    mj = DST / "scripts/main.js"
    mj.write_text(rep(mj.read_text(), 'const PW_BUILD = "1.3.227";', 'const PW_BUILD = "1.3.228";', "PW_BUILD"))
    cp = DST / "scripts/pw_companion.js"
    cp.write_text(rep(cp.read_text(), "companion v7 LOADED (pack v1.3.227", "companion v7 LOADED (pack v1.3.228", "companion"))
    for p in sorted((DST / "scripts").rglob("*.js")):
        r = subprocess.run(["node", "--check", str(p)], capture_output=True, text=True)
        assert r.returncode == 0, f"{p.name}: {r.stderr[:300]}"
    r = subprocess.run([sys.executable, "/home/claude/tools/js_dupcheck.py"] + [str(p) for p in sorted((DST / "scripts").glob("*.js"))], capture_output=True, text=True)
    assert r.returncode == 0, f"duplicate globals: {r.stdout[:600]}"
    print(f"DONE {DST} · changed: {', '.join(changed)} · manifest + PW_BUILD 1.3.228")


if __name__ == "__main__":
    main()
