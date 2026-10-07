#!/usr/bin/env python3
"""build_bp02_195.py — BP-02 v1.3.195 from v1.3.194 (R17, his answer 6 11:05 CT: "we can perform the full cut. We may be redesigning
the leaves soon anyway."; LEAF PROTOCOL D-C315 / D-C321).
  LEAVES  the 9 pw:<wood>_leaves blocks lose pw:open_n / open_e / open_s / open_w and the bone_visibility that read them
          (2,688 -> 168 permutations each). Every corner filler now always shows: leaves with canopy on both
          north and south sides look exactly as today; a leaf whose north / south side faces air shows its fillers there (4-6 px,
          render _docs/leaves/LEAF-CUT-BEFORE-AFTER.png). Variant 0 (the far cube) is UNCHANGED (his answer 5 waits on the far-
          block question, D-C321).
  SCRIPT  main.js _markLeaf no longer writes the four states (4 getBlock reads fewer per marked leaf); PW_BUILD 1.3.195.
Everything else byte-identical to 1.3.194. Rollback = BP-02 1.3.194. Test in a COPY of the test world (placed leaves carry the
removed states until the engine drops them). verify: verify_bp02_195.py"""
import json, shutil, sys, time
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import molang_lint as ML

ROOT = Path("/home/claude")
SRC, DST, VER = ROOT / "_build/bp02-194", ROOT / "_build/bp02-195", [1, 3, 195]
DATE = "2026-09-30"
DROP = ("pw:open_n", "pw:open_e", "pw:open_s", "pw:open_w")
WOODS = ("acacia", "birch", "cherry", "dark_oak", "jungle", "mangrove", "oak", "pale_oak", "spruce")
MARK_LINES = ['      .withState("pw:open_n", dim.getBlock({ x: x, y: y, z: z - 1 })?.isAir ?? false)\n',
              '      .withState("pw:open_s", dim.getBlock({ x: x, y: y, z: z + 1 })?.isAir ?? false)\n',
              '      .withState("pw:open_e", dim.getBlock({ x: x + 1, y: y, z: z })?.isAir ?? false)\n',
              '      .withState("pw:open_w", dim.getBlock({ x: x - 1, y: y, z: z })?.isAir ?? false)\n']


def log(m):
    print(m)
    with open(ROOT / "_logs/phase_log.md", "a") as f: f.write(f"[{time.strftime('%H:%M')} CT {time.strftime('%m-%d')}] BUILD bp02-195: {m}\n")


def main():
    if DST.exists(): shutil.rmtree(DST)
    shutil.copytree(SRC, DST)
    for w in WOODS:
        p = DST / f"blocks/{w}_leaves.json"
        d = ML._parse_json(p.read_text(encoding="utf-8")); blk = d["minecraft:block"]; st = blk["description"]["states"]
        assert all(k in st for k in DROP), (w, list(st))
        for k in DROP: st.pop(k)
        n = 0
        for perm in blk.get("permutations", []):
            assert not any(k in perm["condition"] for k in DROP), (w, perm["condition"])
            g = perm["components"].get("minecraft:geometry")
            if isinstance(g, dict) and "bone_visibility" in g:
                assert set(g) == {"identifier", "bone_visibility"} and all(any(k in v for k in DROP) for v in g["bone_visibility"].values()), (w, g)
                perm["components"]["minecraft:geometry"] = g["identifier"]; n += 1
        assert n == 6, (w, n)
        p.write_text(json.dumps(d, indent=2), encoding="utf-8")
    log(f"leaves: {len(WOODS)} blocks, states {DROP} + bone_visibility (6 permutations each) removed")
    mp = DST / "scripts/main.js"; s = mp.read_text(encoding="utf-8")
    for ln in MARK_LINES:
        assert s.count(ln) == 1, ln
        s = s.replace(ln, "", 1)
    assert s.count('const PW_BUILD = "1.3.194";') == 1
    s = s.replace('const PW_BUILD = "1.3.194";', 'const PW_BUILD = "1.3.195";', 1)
    assert "pw:open_" not in s
    mp.write_text(s, encoding="utf-8")
    log("main.js: _markLeaf side-flag writes removed; PW_BUILD 1.3.195")
    man = DST / "manifest.json"; m = json.loads(man.read_text(encoding="utf-8-sig"))
    m["header"]["version"] = VER; m["header"]["name"] = "AbsolutRealism Tectonic BP v1.3.195"
    for mod in m["modules"]: mod["version"] = VER
    m["header"]["description"] = (f"v1.3.195 ({DATE}) R17: the leaf blocks drop their four side flags (every leaf shows all its corner "
        "fill-ins; block permutations down to about 19,500). Includes all of v1.3.194.")
    man.write_text(json.dumps(m, indent=1), encoding="utf-8")
    log("manifest 1.3.195")


if __name__ == "__main__":
    main()
