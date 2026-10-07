#!/usr/bin/env python3
"""build_bp02_191.py — BP-02 v1.3.191 (D-C293, his 20:22 "fix the zombie and sheep overrides - we won't need them" + his pick
"Keep the sheep line"):
  * entities/zombie.json REMOVED — a stale copy of an OLDER vanilla zombie (format 1.26.0: the old drowned-conversion event names,
    no collision boxes, the old pushable components) whose only addition was the property pw:variant; no resource pack draws
    zombie variants any more (census 20:2x: no RP-06/07/08 entity or render controller reads pw:variant), so the game's own
    current zombie takes over.
  * scripts/main.js — the PW_VARIANTS entity block (random pw:variant on every zombie spawn + the chat line "[pw_variants] v0.1.1
    ZOMBIE-PROOF loaded. Zombies now have 16 variant slots") removed with the file it served; the BLOCK variant system
    (pw:randomize_variant, pw:variant_dump) is a different feature and stays. PW_BUILD -> "1.3.191".
  * entities/sheep.json KEPT (Mojang's current sheep + one line: sheep graze pw:grass_block -> dirt, the ground-parity law).
Usage: build_bp02_191.py -> _build/bp02-191"""
import json, shutil, time
from pathlib import Path

ROOT = Path("/home/claude")
SRC, DST, VER, DATE = ROOT / "_build/bp02-190", ROOT / "_build/bp02-191", "1.3.191", "2026-09-29"
BLOCK_START = "\n\n// ============================================================\n// PW_VARIANTS — merged from pw_variants BP in v2.9.0 consolidation\n"
BLOCK_END_LINE = '    console.log("[pw_variants] v0.1.1 loaded — zombie variant system active");\n});\n'


def log(m):
    print(m)
    with open(ROOT / "_logs/phase_log.md", "a") as f: f.write(f"[{time.strftime('%H:%M')} CT {time.strftime('%m-%d')}] BUILD bp02-191: {m}\n")


def main():
    if DST.exists(): shutil.rmtree(DST)
    shutil.copytree(SRC, DST)
    (DST / "entities/zombie.json").unlink()
    mj = DST / "scripts/main.js"; t = mj.read_text(encoding="utf-8")
    assert t.count(BLOCK_START) == 1 and t.count(BLOCK_END_LINE) == 1, "PW_VARIANTS block boundaries not unique"
    i0 = t.index(BLOCK_START); i1 = t.index(BLOCK_END_LINE) + len(BLOCK_END_LINE)
    assert i0 < i1 and "VARIANT_SPECIES" in t[i0:i1] and "DYNAMIC HELD-TORCH" not in t[i0:i1]
    removed = t[i0:i1]
    t = t[:i0] + t[i1:]
    old_build = 'const PW_BUILD = "1.3.189";'
    assert t.count(old_build) == 1, "PW_BUILD line not found"
    t = t.replace(old_build, f'const PW_BUILD = "{VER}";')
    mj.write_text(t, encoding="utf-8")
    (ROOT / "_docs/bp02_191_removed_block.js").write_text(removed.lstrip("\n"), encoding="utf-8")   # kept for the record
    mp = DST / "manifest.json"; m = json.loads(mp.read_text(encoding="utf-8")); v = [1, 3, 191]
    m["header"]["version"] = v; m["header"]["name"] = f"AbsolutRealism Tectonic BP v{VER}"
    for mod in m["modules"]: mod["version"] = v
    m["header"]["description"] = (f"v{VER} ({DATE}) STALE ZOMBIE OVERRIDE REMOVED (D-C293, his ruling): entities/zombie.json was an older "
        "vanilla zombie copy (old drowned-conversion events, no collision boxes) carrying a pw:variant property nothing draws any more - the game's "
        "own current zombie takes over; the matching zombie-variant spawn script and its chat line are gone. The sheep override stays (sheep graze "
        "pw:grass_block, the ground-parity rule). Script build id 1.3.191. Everything else byte-identical to v1.3.190 (real-life sizes).")
    mp.write_text(json.dumps(m, indent=1), encoding="utf-8")
    log(f"zombie.json removed; PW_VARIANTS block removed from main.js ({removed.count(chr(10))} lines); PW_BUILD {VER}; manifest {VER}")


if __name__ == "__main__":
    main()
