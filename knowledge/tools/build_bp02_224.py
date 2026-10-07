#!/usr/bin/env python3
"""build_bp02_224.py — BP-02 1.3.224 from 1.3.223: HIS 16:50 REPORT (one combined build, his answer 17:2x).

  1. THE CRASH (watchdog 'Hang' past City II): a tier-up is a queued charter laid out one plot per kit beat (City II was
     6-8 s in one tick); a skipped day every 10 ticks, never in the main beat's tick, one day per advance call; the clock's
     state saved at most every 100 ticks; palace pumps one job per group, one /fill per tick, never on skipped days, ended
     after three dry passes; pictures hung 8 per call; palace survey 2 candidates a day; ground cache 60k; two street
     searches at a time; the day's sub-steps named in the slow log.
  2. THE PALACE FINDER: a chat line when the palace is laid out (centre + direction from the square); status shows the
     survey / the site / the stage; the palace's own calendar in 'next in'.
  3. PAINTINGS (with RP-12 1.0.1): spawned at yaw 0; the CURATOR'S WAND (crafted: a gold ingot over a stick) takes a
     picture down (hit or use) and drops a FRAMED PAINTING (the same work), which hangs on any wall face it is used on.
  4. VILLAGERS: a market clerk at a stall on every square (broad buy list, sells the town's stock); shop keepers re-hired
     after a failed hire and home after hours; selling pays COINS (it paid pennies as coins, 12x); idle people spread over
     their own cells on the square's ring, their yards, the neighbourhood centre, the shops, the inn at dusk — rain sends
     them home; a civ shows a 'Talk' button (minecraft:interact); a lead in an unloaded chunk falls back nearer the walker.
  5. BIRCH v3: the trunk ends one block into the crown (his 16:50); the leaf-strip check is whole-cluster (never strips a
     crown that still touches its trunk).
  6. TERRAIN: ground is built up only over a drop of <= 15, stepped down outward in lifts of 3 (R5); beyond, the plot
     slides / tries other streets, then stilts over <= 24; unread ground waits; streets judge the WORST column (no street,
     embankment or dry-land pier over a drop > 15; the founding main street may relax it once); street edge walls are one
     lift over a stepped embankment; parallels try 8 pitches; the climbing leg names its first blocked cell.
Usage: python3 tools/build_bp02_224.py   (bp02-224 must not exist)"""
import hashlib
import importlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")

B = Path("/home/claude/_build")
SRC, DST = B / "bp02-223", B / "bp02-224"
JS = Path("/home/claude/tools/bp02_src_224")
OVERLAY = Path("/home/claude/tools/bp02_overlay_224")
VERSION = [1, 3, 224]


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def rep(text, old, new, what):
    assert text.count(old) == 1, f"{what}: {text.count(old)} matches"
    return text.replace(old, new)


def main():
    if DST.exists():
        raise SystemExit(f"never rebuild {DST}")
    # the 223 scripts must still be the ones src_224 was copied from (no drift)
    base = dict(line.split()[::-1] for line in (JS / "BASE-223.md5").read_text().splitlines())
    for name, h in base.items():
        assert md5(SRC / "scripts" / name) == h, f"223 drifted: {name}"
    shutil.copytree(SRC, DST)
    changed = []
    for p in sorted(JS.glob("*.js")):
        if base.get(p.name) != md5(p):
            shutil.copy2(p, DST / "scripts" / p.name)
            changed.append(p.name)
    for p in sorted(OVERLAY.rglob("*.json")):
        rel = p.relative_to(OVERLAY)
        (DST / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, DST / rel)
    # the civ villagers get an interaction (the 'Talk' button on touch / console; the script opens our windows)
    vp = DST / "entities/villager_v2.json"
    v = json.loads(vp.read_text())
    ent = v["minecraft:entity"]
    ent["component_groups"]["pw:civ"]["minecraft:interact"] = {"interactions": [{
        "on_interact": {"filters": {"all_of": [{"test": "is_family", "subject": "other", "value": "player"}]}, "event": "pw:civ_talk", "target": "self"},
        "interact_text": "action.interact.pw_talk", "swing": True}]}
    ent["events"]["pw:civ_talk"] = {}
    vp.write_text(json.dumps(v, indent=1))
    # BIRCH v3: the 72 templates from tree_gen (trunk ends one block into the crown)
    saved = sys.argv
    sys.argv = ["tree_gen.py", "birch"]
    TG = importlib.import_module("tree_gen")
    sys.argv = saved
    worst = 0
    for age in ("young", "mature", "old"):
        for idx in range(TG.PER_AGE):
            st, info, trunk, leaves, _ = TG.build("birch", age, idx)
            top = max(c[1] for c in trunk)
            assert top <= info["crown_base"] + TG.BIRCH_TRUNK_INTO_CROWN, (age, idx, top, info["crown_base"])
            lowest_leaf = min(c[1] for c in leaves)
            worst = max(worst, top - lowest_leaf)
            (DST / "structures/pw/trees" / f"birch_{age}_{idx:02d}.mcstructure").write_bytes(st.to_bytes())
    # manifest + version flags
    mp = DST / "manifest.json"
    m = json.loads(mp.read_text())
    m["header"]["version"] = VERSION
    m["header"]["name"] = "AbsolutRealism Tectonic BP v1.3.224"
    for mod in m["modules"]:
        mod["version"] = VERSION
    m["header"]["description"] = ("v1.3.224 (2026-10-05) HIS 16:50 REPORT: no watchdog hang past City II (tier-ups laid out plot by plot, skipped "
                                  "days paced); the palace announced and in status; the Curator's Wand + Framed Painting; market clerks on every "
                                  "square (sell for gold coins), keepers at their posts, villagers spread out; birch trunks end at the crown; "
                                  "towns build up only over drops of 15 or less (stepped), else follow the land, else stilts. Needs RP-01 1.3.124 + "
                                  "RP-12 1.0.1. Personal use.")
    mp.write_text(json.dumps(m, indent=1))
    mj = DST / "scripts/main.js"
    mj.write_text(rep(mj.read_text(), 'const PW_BUILD = "1.3.223";', 'const PW_BUILD = "1.3.224";', "PW_BUILD"))
    cp = DST / "scripts/pw_companion.js"
    if cp.exists():
        c = cp.read_text()
        if "companion v7 LOADED (pack v1.3.223" in c:
            cp.write_text(c.replace("companion v7 LOADED (pack v1.3.223", "companion v7 LOADED (pack v1.3.224"))
    for p in sorted((DST / "scripts").glob("*.js")):
        r = subprocess.run(["node", "--check", str(p)], capture_output=True, text=True)
        assert r.returncode == 0, f"{p.name}: {r.stderr[:300]}"
    print(f"DONE {DST} · scripts changed: {', '.join(changed)} · items: curators_wand, framed_painting · 72 birch templates v3 "
          f"(trunk <= crown base + {TG.BIRCH_TRUNK_INTO_CROWN}; worst trunk-into-leaves {worst}) · villager interact · manifest + PW_BUILD 1.3.224")


if __name__ == "__main__":
    main()
