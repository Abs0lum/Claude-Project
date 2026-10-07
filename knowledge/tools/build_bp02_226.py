#!/usr/bin/env python3
"""build_bp02_226.py — BP-02 1.3.226 from 1.3.225: THE LAND AND THE CORE (his 20:35 / 20:48).

  1. `pw:clock survey [radius]` / `surveyat x z [radius]`: the best three gentle sites for a city in the loaded land.
  2. HOMES OUTWARD: homes take the outermost streets first, packed from the far end inward; businesses keep the streets
     nearest the square.
  3. THE CORE GROWS: from town II a business whose slot lies outside the core (60..180 by tier) may take the lot of the
     nearest finished home inside it — the household moves out to a new home on the outskirts (re-homed by the census),
     the old house comes down, the business is planned on the freed frontage; one conversion a day.
  4. CONTOUR LANES (pw_civ_lanes.js): a home with no room on the streets takes a lot on a LANE — a 7-wide narrow road at ONE
     level following the hillside's contour from a street's dead end (no kerbs); its sewer GALLERY runs under the centre
     line into the dead end's hall, every lane house is joined to it by a branch; `pw:clock sewers` counts lane houses.
(1.3.225 was:

  1. FRONTAGE (the census, 10-05 20:3x: at town III 605 of 2,330 street-side cells were legal frontage and 0 positions were
     free from village on): houses front RAMPS as well as flats (rise <= 1 along the front; the floor at the highest
     sidewalk); a junction window that 3 side-street searches could not open is given back to the houses.
  2. EVERY HOME REACHES THE SEWER (his 20:36): a house beside room for its own hatch gets the hatch (access piece); any
     other house gets a BRANCH — 4 cells of the corridor's side wall cut at its shaft, the cellar gallery into the sewer
     hall (both at floor - 11 .. floor - 8 on flats and ramps); a re-laid piece is cut again. `pw:clock sewers` counts it.
  3. `pw:clock frontage [house]`: how many more houses fit and what refuses the rest.
  4. FISHERMEN (his 20:35): shore spots surveyed from village II; fishermen walk to them in work hours, wear the vanilla
     fisherman's clothes (event pw:skin_fisher), land fish (splash + sound); FISH is a ledger good (a "fishery" workshop,
     a fisher's wage), the market buys cod / salmon / tropical fish.
Usage: python3 tools/build_bp02_226.py   (bp02-226 must not exist)"""
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

B = Path("/home/claude/_build")
SRC, DST = B / "bp02-225", B / "bp02-226"
JS = Path("/home/claude/tools/bp02_src_226")
VERSION = [1, 3, 226]


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def rep(text, old, new, what):
    assert text.count(old) == 1, f"{what}: {text.count(old)} matches"
    return text.replace(old, new)


def main():
    if DST.exists():
        raise SystemExit(f"never rebuild {DST}")
    base = dict(line.split()[::-1] for line in (JS / "BASE-225.md5").read_text().splitlines())
    for name, h in base.items():
        assert md5(SRC / "scripts" / name) == h, f"225 drifted: {name}"
    # the unit tests first (a failing law never reaches a build)
    for test in sorted((JS / "tests").glob("test_*.mjs")):
        r = subprocess.run(["node", str(test)], capture_output=True, text=True, cwd=JS)
        assert r.returncode == 0, f"{test.name}: {r.stdout[-800:]} {r.stderr[-400:]}"
        print(r.stdout.strip().splitlines()[-1])
    shutil.copytree(SRC, DST)
    changed = []
    for p in sorted(JS.glob("*.js")):
        if base.get(p.name) != md5(p):
            shutil.copy2(p, DST / "scripts" / p.name)
            changed.append(p.name)
    mp = DST / "manifest.json"
    m = json.loads(mp.read_text())
    m["header"]["version"] = VERSION
    m["header"]["name"] = "AbsolutRealism Tectonic BP v1.3.226"
    for mod in m["modules"]:
        mod["version"] = VERSION
    m["header"]["description"] = ("v1.3.226 (2026-10-05) THE LAND AND THE CORE: /scriptevent pw:clock survey names the best ground for a city; homes "
                                  "go to the outskirts first and businesses stay central; the core grows by buying old homes next to it for new "
                                  "businesses (the family moves out to a new home). Includes 1.3.225 (streets unlocked, every home on the sewer, "
                                  "fishermen). Needs RP-01 1.3.124 + RP-12 1.0.1. Personal use.")
    mp.write_text(json.dumps(m, indent=1))
    mj = DST / "scripts/main.js"
    mj.write_text(rep(mj.read_text(), 'const PW_BUILD = "1.3.225";', 'const PW_BUILD = "1.3.226";', "PW_BUILD"))
    cp = DST / "scripts/pw_companion.js"
    if cp.exists():
        c = cp.read_text()
        if "companion v7 LOADED (pack v1.3.225" in c:
            cp.write_text(c.replace("companion v7 LOADED (pack v1.3.225", "companion v7 LOADED (pack v1.3.226"))
    for p in sorted((DST / "scripts").glob("*.js")):
        r = subprocess.run(["node", "--check", str(p)], capture_output=True, text=True)
        assert r.returncode == 0, f"{p.name}: {r.stderr[:300]}"
    # QuickJS refuses a duplicate top-level name that node accepts (gate 226-1 build 1: CORE_R twice)
    r = subprocess.run([sys.executable, "/home/claude/tools/js_dupcheck.py"] + [str(p) for p in sorted((DST / "scripts").glob("*.js"))], capture_output=True, text=True)
    assert r.returncode == 0, f"duplicate globals: {r.stdout[:600]}"
    print(f"DONE {DST} · scripts changed: {', '.join(changed)} · manifest + PW_BUILD 1.3.226")


if __name__ == "__main__":
    main()
