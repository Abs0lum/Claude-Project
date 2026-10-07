#!/usr/bin/env python3
"""build_bp02_225.py — BP-02 1.3.225 from 1.3.224: THE STREETS UNLOCKED + FISHERMEN (his 20:01 / 20:35 / 20:36).

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
Usage: python3 tools/build_bp02_225.py   (bp02-225 must not exist)"""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

B = Path("/home/claude/_build")
SRC, DST = B / "bp02-224", B / "bp02-225"
JS = Path("/home/claude/tools/bp02_src_225")
VERSION = [1, 3, 225]


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def rep(text, old, new, what):
    assert text.count(old) == 1, f"{what}: {text.count(old)} matches"
    return text.replace(old, new)


def main():
    if DST.exists():
        raise SystemExit(f"never rebuild {DST}")
    base = dict(line.split()[::-1] for line in (JS / "BASE-224.md5").read_text().splitlines())
    for name, h in base.items():
        assert md5(SRC / "scripts" / name) == h, f"224 drifted: {name}"
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
    # the fisherman's clothes: variant 2 (the vanilla 'fisherman' group's value) without the vanilla job-site AI
    vp = DST / "entities/villager_v2.json"
    v = json.loads(vp.read_text())
    ent = v["minecraft:entity"]
    assert ent["component_groups"]["fisherman"]["minecraft:variant"]["value"] == 2
    ent["component_groups"]["pw:skin_fisher"] = {"minecraft:variant": {"value": 2}}
    ent["events"]["pw:skin_fisher"] = {"add": {"component_groups": ["pw:skin_fisher"]}}
    vp.write_text(json.dumps(v, indent=1))
    mp = DST / "manifest.json"
    m = json.loads(mp.read_text())
    m["header"]["version"] = VERSION
    m["header"]["name"] = "AbsolutRealism Tectonic BP v1.3.225"
    for mod in m["modules"]:
        mod["version"] = VERSION
    m["header"]["description"] = ("v1.3.225 (2026-10-05) THE STREETS UNLOCKED: houses front ramps too, unused cross-street gaps are given back, "
                                  "and EVERY home reaches the sewer (its own hatch or a branch tunnel); /scriptevent pw:clock frontage and "
                                  "pw:clock sewers; FISHERMEN on the shore (fish is a town good, the market buys it). Needs RP-01 1.3.124 + "
                                  "RP-12 1.0.1. Personal use.")
    mp.write_text(json.dumps(m, indent=1))
    mj = DST / "scripts/main.js"
    mj.write_text(rep(mj.read_text(), 'const PW_BUILD = "1.3.224";', 'const PW_BUILD = "1.3.225";', "PW_BUILD"))
    cp = DST / "scripts/pw_companion.js"
    if cp.exists():
        c = cp.read_text()
        if "companion v7 LOADED (pack v1.3.224" in c:
            cp.write_text(c.replace("companion v7 LOADED (pack v1.3.224", "companion v7 LOADED (pack v1.3.225"))
    for p in sorted((DST / "scripts").glob("*.js")):
        r = subprocess.run(["node", "--check", str(p)], capture_output=True, text=True)
        assert r.returncode == 0, f"{p.name}: {r.stderr[:300]}"
    print(f"DONE {DST} · scripts changed: {', '.join(changed)} · villager pw:skin_fisher · manifest + PW_BUILD 1.3.225")


if __name__ == "__main__":
    main()
