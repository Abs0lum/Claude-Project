#!/usr/bin/env python3
"""verify_ownership.py — OWNERSHIP GATE (his 00:07 'agreed'): every terrain key we define, the image its paths resolve
to (top of the stack) and that image's texture set must be in ONE pack.
  O1  keys defined by OUR packs, used by any block (BP material_instances or blocks.json): key pack == image pack
      whenever the image has a set somewhere.                                                             -> FAIL if any
  O1 known-later keys (base 'o1_known_keys') are reported, not failed — his 00:53 'handle more fully later'.
  O2  no NEW texture path / terrain key duplicated across our packs beyond the recorded baseline
      (_docs/blocks/OWN-BASELINE.json; first run records it).                                             -> FAIL if more
  info: vanilla-defined keys (normal texture-pack override) and their counts.
Stack = PW_STACK (stack_now). Writes _docs/blocks/VERIFY-OWNERSHIP.json."""
import glob
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import stack_now as S  # noqa: E402

EXT = (".png", ".tga", ".jpg")
BP = ["_build/bp02-206/blocks/**/*.json", "_build/bp03-134/blocks/**/*.json"]   # 10-02: + subfolders (roots, stumps, sf_nba)


def main():
    P = S.packs()
    T = S.terrain(P)
    used = set()
    for g in BP:
        for f in glob.glob(str(ROOT / g), recursive=True):
            used |= set(re.findall(r'"texture"\s*:\s*"([^"]+)"', open(f).read()))
    for p in P:
        for v in (p.json("blocks.json") or {}).values():
            if isinstance(v, dict):
                t = v.get("textures")
                used |= {t} if isinstance(t, str) else set(t.values()) if isinstance(t, dict) else set()
    o1, info = [], Counter()
    for key in sorted(used):
        if key not in T:
            continue
        kp = T[key][0]
        for path in S.paths_of(T[key][1]):
            ip = next((p for p in P if any(p.has(path + e) for e in EXT)), None)
            has_set = any(p.has(path + ".texture_set.json") for p in P)
            if ip is None or not has_set:
                continue
            if kp.startswith("vanilla"):
                info["vanilla key (override)"] += 1
                continue
            if ip.name != kp:
                o1.append([key, path, kp, ip.name])
    ours = [p for p in P if p.name.startswith("RP-")]
    paths, keys = {}, {}
    for p in ours:
        for f in p.files:
            if f.startswith("textures/") and f.endswith(EXT):
                paths.setdefault(f.rsplit(".", 1)[0], set()).add(p.name[:5])
        for k in ((p.json("textures/terrain_texture.json") or {}).get("texture_data") or {}):
            keys.setdefault(k, set()).add(p.name[:5])
    dup_p = sum(1 for v in paths.values() if len(v) > 1)
    dup_k = sum(1 for v in keys.values() if len(v) > 1)
    bl = ROOT / "_docs/blocks/OWN-BASELINE.json"
    if not bl.exists():
        bl.write_text(json.dumps({"dup_paths": dup_p, "dup_keys": dup_k, "recorded_for": S.ORDER[4][0]}, indent=1))
    base = json.loads(bl.read_text())
    known = set(base.get("o1_known_keys", []))
    o1_known = [a for a in o1 if a[0] in known]
    o1 = [a for a in o1 if a[0] not in known]
    o2 = dup_p > base["dup_paths"] or dup_k > base["dup_keys"]
    out = {"O1_fails": len(o1), "O1": o1[:200], "O1_known_later": len(o1_known), "O2_fail": o2, "dup_paths": dup_p, "dup_keys": dup_k, "baseline": base,
           "info": dict(info)}
    (ROOT / "_docs/blocks/VERIFY-OWNERSHIP.json").write_text(json.dumps(out, indent=1))
    print("O1 key/image pack mismatches:", len(o1), "(known, for the later full pass:", len(o1_known), ")", Counter((a[2][:5], a[3][:5]) for a in o1).most_common(8))
    print("O2 duplicates: paths", dup_p, "keys", dup_k, "baseline", base, "->", "FAIL" if o2 else "PASS")
    print("info:", dict(info))
    return 1 if (o1 or o2) else 0


if __name__ == "__main__":
    sys.exit(main())
