#!/usr/bin/env python3
"""build_bp02_216.py — BP-02 1.3.216 from the frozen 1.3.214 (never rebuilt).

His 12:21 ruling (door recipe = Option A): pw:wall_oak_planks (6 oak planks, 2x3 = the vanilla door grid) loses the
`crafting_table` tag and is crafted at the Builder's Table only, so an ordinary crafting table makes doors again.
Plus the stale [PW-C2] boot label (it printed "pack v1.3.206") now reads the real pack version.
Nothing else changes. 1.3.215 (2-block tree search) stays HELD for his question list; its number is never reused."""
import json
import shutil
from pathlib import Path

B = Path("/home/claude/_build")
SRC, DST = B / "bp02-214", B / "bp02-216"


def replace_once(text, old, new, what):
    """Replace exactly one occurrence or stop the build (Python str.replace is silent on no-match)."""
    if text.count(old) != 1:
        raise SystemExit(f"{what}: expected 1 match, found {text.count(old)}")
    return text.replace(old, new)


def main():
    if DST.exists():
        raise SystemExit(f"never rebuild {DST}")
    shutil.copytree(SRC, DST)

    # 1. door recipe clash (Option A)
    rp = DST / "recipes/pw_wall_oak_planks.json"
    r = json.loads(rp.read_text())
    tags = r["minecraft:recipe_shaped"]["tags"]
    if tags != ["crafting_table", "pw:builders_table"]:
        raise SystemExit(f"unexpected tags {tags}")
    r["minecraft:recipe_shaped"]["tags"] = ["pw:builders_table"]
    rp.write_text(json.dumps(r, indent=1))

    # 2. stale companion label
    cp = DST / "scripts/pw_companion.js"
    cp.write_text(replace_once(cp.read_text(), "companion v7 LOADED (pack v1.3.206 ", "companion v7 LOADED (pack v1.3.216 ", "C2 label"))

    # 3. build stamp
    mj = DST / "scripts/main.js"
    mj.write_text(replace_once(mj.read_text(), 'const PW_BUILD = "1.3.214";', 'const PW_BUILD = "1.3.216";', "PW_BUILD"))

    # 4. manifest
    m = json.loads((DST / "manifest.json").read_text())
    m["header"]["version"] = [1, 3, 216]
    for mod in m["modules"]:
        mod["version"] = [1, 3, 216]
    m["header"]["name"] = "AbsolutRealism Tectonic BP v1.3.216"
    desc = m["header"]["description"]
    if not desc.startswith("v1.3.214 (2026-10-03) "):
        raise SystemExit("description prefix not found")
    m["header"]["description"] = ("v1.3.216 (2026-10-03) door fix: the oak plank wall is crafted at the Builder's Table only "
                                  "(it shared the door's 6-plank grid). Includes all of " + desc)[:1000]
    (DST / "manifest.json").write_text(json.dumps(m, indent=1))

    dep = DST / "PW-DEPENDENCIES.md"
    dep.write_text(replace_once(dep.read_text(), "v1.3.214 (light blocks cleared again:",
                                "v1.3.216 (oak plank wall at the Builder's Table only; light blocks cleared again:", "deps stamp"))
    print(f"DONE {DST}")


if __name__ == "__main__":
    main()
