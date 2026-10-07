#!/usr/bin/env python3
"""build_bp02_214.py — BP-02 1.3.214 from the frozen 1.3.212 (never rebuilt): LIGHT BLOCKS ARE CLEARED AGAIN (D-C515).
On 1.26 the block that BlockPermutation.resolve("minecraft:light_block", {block_light_level: N}) places reports the FLATTENED id
`minecraft:light_block_N` (BDS 1.26.52, ledger probe run A). pw_mob_light.clearLight and the golden-crown aura's _pwClearCrownLight
removed a light only when typeId === "minecraft:light_block" -> never -> every light either system stood up stayed in the world
(proven on the delivered 212: boot sweep / tick dropped both records, both light blocks stayed across two restarts).
Fix: both tests accept every `minecraft:light_block*` id. Nothing else changes. 1.3.213 (snow fix v3) stays HELD for his
question 6 — its number is skipped, never reused."""
import json
import shutil
from pathlib import Path

B = Path("/home/claude/_build")
SRC, DST = B / "bp02-212", B / "bp02-214"
S = Path("/home/claude/tools/bp02_src")


def main():
    if DST.exists():
        raise SystemExit(f"never rebuild {DST}")
    shutil.copytree(SRC, DST)
    shutil.copy2(S / "pw_mob_light.js", DST / "scripts/pw_mob_light.js")
    mj = DST / "scripts/main.js"
    js = mj.read_text()
    old = '    if (b && b.typeId === "minecraft:light_block") b.setType("minecraft:air");'
    new = ('    // v1.3.214 (D-C515): the engine reports the flattened id minecraft:light_block_14 — the old exact test never matched,\n'
           '    // so the crown left a light above every cell its wearer walked through. Any light block at our recorded cell is ours.\n'
           '    if (b && String(b.typeId).startsWith("minecraft:light_block")) b.setType("minecraft:air");')
    if js.count(old) != 1:
        raise SystemExit("crown clear line not found once")
    js = js.replace(old, new)
    if js.count('const PW_BUILD = "1.3.212";') != 1:
        raise SystemExit("PW_BUILD line not found once")
    js = js.replace('const PW_BUILD = "1.3.212";', 'const PW_BUILD = "1.3.214";')
    mj.write_text(js)
    m = json.loads((DST / "manifest.json").read_text())
    m["header"]["version"] = [1, 3, 214]
    for mod in m["modules"]:
        mod["version"] = [1, 3, 214]
    m["header"]["name"] = "AbsolutRealism Tectonic BP v1.3.214"
    desc = m["header"]["description"]
    if not desc.startswith("v1.3.212 (2026-10-03) "):
        raise SystemExit("description prefix not found")
    m["header"]["description"] = ("v1.3.214 (2026-10-03) light fix: the mob lights (blaze, magma cube, glow squid) and the golden-crown light are "
                                  "removed again (1.26 reports light_block_<level>; before, every light stayed). Includes all of " + desc)[:1000]
    (DST / "manifest.json").write_text(json.dumps(m, indent=1))
    dep = DST / "PW-DEPENDENCIES.md"
    t = dep.read_text()
    t2 = t.replace("v1.3.212 (TREEGROW registry reload fix;", "v1.3.214 (light blocks cleared again: flattened ids; TREEGROW registry reload fix;", 1)
    if t2 == t:
        raise SystemExit("PW-DEPENDENCIES stamp not found")
    dep.write_text(t2)
    print(f"DONE {DST} (manifest 1.3.214, pw_mob_light clearLight + crown clear accept light_block_*, PW_BUILD 1.3.214)")


if __name__ == "__main__":
    main()
