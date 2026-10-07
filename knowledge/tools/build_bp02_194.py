#!/usr/bin/env python3
"""build_bp02_194.py — BP-02 v1.3.194 from v1.3.193 (R16a; his picks D-C310 02:00 + 02:3x CT 09-30).
  LEAVES     the 9 pw:<wood>_leaves blocks lose pw:far (declared, never read or written) -> 5,376 -> 2,688 permutations each;
             the custom total ~64.7k -> ~40.5k. (D-C312: pw:open_n/e/s/w are READ by the leaf models' bone_visibility - the
             Directional Awareness fringe - so they stay, and _markLeaf keeps writing them.)
  MOB LIGHT  scripts/pw_mob_light.js (new): blazes, magma cubes and glow squids near a player carry a moving light block
             (blaze 13, magma cube 10, glow squid 6 - waterlogged, water sources only); left-over lights cleared at boot.
  PW_BUILD   version flag 1.3.191 -> 1.3.194 (the flag had not moved since the last script change).
Everything else byte-identical to 1.3.193. verify: verify_bp02_194.py"""
import json, re, shutil, sys, time
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import molang_lint as ML

ROOT = Path("/home/claude")
SRC, DST, VER = ROOT / "_build/bp02-193", ROOT / "_build/bp02-194", [1, 3, 194]
DATE = "2026-09-30"
DROP = ("pw:far",)   # D-C312: the side flags drive the leaf fringe (bone_visibility) - kept
WOODS = ("acacia", "birch", "cherry", "dark_oak", "jungle", "mangrove", "oak", "pale_oak", "spruce")


def log(m):
    print(m)
    with open(ROOT / "_logs/phase_log.md", "a") as f: f.write(f"[{time.strftime('%H:%M')} CT {time.strftime('%m-%d')}] BUILD bp02-194: {m}\n")


def main():
    if DST.exists(): shutil.rmtree(DST)
    shutil.copytree(SRC, DST)
    # ---- leaves: text-level removal of the five states (formatting of the rest kept byte-exact)
    for w in WOODS:
        p = DST / f"blocks/{w}_leaves.json"; raw = p.read_text(encoding="utf-8")
        d = ML._parse_json(raw); st = d["minecraft:block"]["description"]["states"]
        assert all(k in st for k in DROP), (w, list(st))
        for k in DROP: st.pop(k)
        for perm in d["minecraft:block"].get("permutations", []):
            assert not any(k in perm["condition"] for k in DROP), (w, perm["condition"])
        p.write_text(json.dumps(d, indent=2), encoding="utf-8")
    log(f"leaves: {len(WOODS)} blocks, states {DROP} removed")
    # ---- main.js: the four side-flag writes out, the import in, the version flag
    mp = DST / "scripts/main.js"; s = mp.read_text(encoding="utf-8")
    old_imp = 'import { weatherIn } from "./pw_weather.js";'
    assert s.count(old_imp) == 1
    s = s.replace(old_imp, 'import "./pw_mob_light.js"; // v1.3.194: self-lit mobs throw real light (blaze / magma cube / glow squid)\n' + old_imp, 1)
    assert s.count('const PW_BUILD = "1.3.191";') == 1
    s = s.replace('const PW_BUILD = "1.3.191";', 'const PW_BUILD = "1.3.194";', 1)
    mp.write_text(s, encoding="utf-8")
    shutil.copy(ROOT / "tools/bp02_src/pw_mob_light.js", DST / "scripts/pw_mob_light.js")
    log("main.js: pw_mob_light import, PW_BUILD 1.3.194 (the side-flag writes stay: D-C312)")
    # ---- manifest
    man = DST / "manifest.json"; m = json.loads(man.read_text(encoding="utf-8-sig"))
    m["header"]["version"] = VER; m["header"]["name"] = "AbsolutRealism Tectonic BP v1.3.194"
    for mod in m["modules"]: mod["version"] = VER
    m["header"]["description"] = (f"v1.3.194 ({DATE}) R16a: blazes, magma cubes and glow squids light their surroundings (a moving "
        "light block, cleared when they leave); the leaf blocks drop their unused pw:far state (block permutations ~64.7k -> ~40.5k, under "
        "the engine's 65,536 warning). Includes all of v1.3.193.")
    man.write_text(json.dumps(m, indent=1), encoding="utf-8")
    log("manifest 1.3.194")


if __name__ == "__main__":
    main()
