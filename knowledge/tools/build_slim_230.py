#!/usr/bin/env python3
"""build_slim_230.py — BP-02 1.3.230 "SLIM": the PS5-join crash isolation build (his 00:23 CT 2026-10-07 report).

Hypothesis (unproven): the world's block-permutation count. Our BPs define 57,512 custom permutations (BP-02 1.3.229
55,891 + Markers 1,621; 1.3.227 had 34,536); Microsoft documents a 65,536 cap for all blocks of a world, and vanilla adds
its own on top. A joining console rebuilds every permutation from what the host sends.

This build changes ONE thing against 1.3.229: the 266 ramp blocks (19 stones x 2/4/8-block shapes) drop their texture-
variant state pw:var (4 or 8 values) and keep variant 0's look. 21,760 ramp permutations -> 5,320 (-16,440).
  blocks/pw_ramp_*.json  : "pw:var" removed from states; only the pw:var == 0 permutations kept, the clause removed.
  4 road structures      : palette entries lose pw:var (palette de-duplicated, indices remapped).
Scripts never read or set pw:var on ramps (grep); RP files are unchanged (variant 0's textures).
"""
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
import mcstructure as M  # noqa: E402

B = Path("/home/claude/_build")
SRC, DST = B / "bp02-229", B / "bp02-230"
NOTE = ("v1.3.230 (2026-10-07) SLIM TEST for the PS5 join crash: the 266 street-ramp blocks drop their texture-variant "
        "state (21,760 -> 5,320 block permutations); everything else = 1.3.229. ")
VAR_CLAUSE = re.compile(r"\s*&&\s*q\.block_state\('pw:var'\)\s*==\s*0|q\.block_state\('pw:var'\)\s*==\s*0\s*&&\s*")
VAR_ANY = re.compile(r"q\.block_state\('pw:var'\)\s*==\s*(\d+)")


def slim_block(path):
    """Drop pw:var from one ramp block file. Returns (permutations before, after) or None when the block has no pw:var."""
    j = json.loads(path.read_text(encoding="utf-8-sig"))
    b = j["minecraft:block"]
    states = b["description"].get("states") or {}
    if "pw:var" not in states:
        return None
    del states["pw:var"]
    before = b.get("permutations", [])
    kept = []
    for p in before:
        m = VAR_ANY.search(p.get("condition", ""))
        if m and m.group(1) != "0":
            continue
        p["condition"] = VAR_CLAUSE.sub("", p["condition"]).strip()
        if "pw:var" in p["condition"]:
            raise SystemExit(f"{path.name}: unhandled pw:var clause: {p['condition']}")
        kept.append(p)
    b["permutations"] = kept
    path.write_text(json.dumps(j, indent=1))
    return len(before), len(kept)


def slim_structure(path):
    """Remove pw:var from ramp palette entries; de-duplicate the palette and remap both index layers."""
    st = M.Structure.from_bytes(path.read_bytes())
    new_pal, key_of, remap = [], {}, {}
    changed = 0
    for old_i, (name, states, ver) in enumerate(st.palette):
        if "ramp" in name and "pw:var" in states:
            states = {k: v for k, v in states.items() if k != "pw:var"}
            changed += 1
        key = (name, tuple(sorted((k, v.type, repr(v.value)) for k, v in states.items())), ver)
        if key not in key_of:
            key_of[key] = len(new_pal)
            new_pal.append((name, states, ver))
        remap[old_i] = key_of[key]
    if not changed:
        return 0
    st.palette = new_pal
    st.layer0 = [remap[k] if k >= 0 else k for k in st.layer0]
    st.layer1 = [remap[k] if k >= 0 else k for k in st.layer1]
    path.write_bytes(st.to_bytes())
    return changed


def main():
    if DST.exists():
        raise SystemExit(f"{DST} exists — versions are never reused")
    shutil.copytree(SRC, DST)
    nb = pb = pa = 0
    for f in sorted((DST / "blocks").rglob("pw_ramp_*.json")):
        r = slim_block(f)
        if r:
            nb += 1
            pb += r[0]
            pa += r[1]
    ns = sum(1 for f in sorted((DST / "structures").rglob("*.mcstructure")) if slim_structure(f))
    main_js = DST / "scripts/main.js"
    s = main_js.read_text()
    if s.count('const PW_BUILD = "1.3.229";') != 1:
        raise SystemExit("PW_BUILD line not found")
    main_js.write_text(s.replace('const PW_BUILD = "1.3.229";', 'const PW_BUILD = "1.3.230";'))
    m = json.loads((DST / "manifest.json").read_text(encoding="utf-8-sig"))
    m["header"]["version"] = [1, 3, 230]
    m["header"]["name"] = m["header"]["name"].replace("v1.3.229", "v1.3.230")
    m["header"]["description"] = NOTE + m["header"]["description"]
    for mod in m["modules"]:
        mod["version"] = [1, 3, 230]
    (DST / "manifest.json").write_text(json.dumps(m, indent=1))
    print(f"ramp blocks slimmed {nb} (permutation entries {pb} -> {pa}); structures rewritten {ns}; PW_BUILD 1.3.230")


if __name__ == "__main__":
    main()
