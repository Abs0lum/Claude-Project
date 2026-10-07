#!/usr/bin/env python3
"""palace_light_s0.py — a LIGHT plot stage for the palace pieces (gallery gate run 1: placing a piece's full s0 box
— 196,608 cells of air above and dirt below — took 6.8–8.2 s in one tick, two seconds under the script watchdog).
The s0 keeps only the ground work at and above the foundations (feet >= -2, non-air: foundations, lawn, courts, basin);
every other cell becomes STRUCTURE VOID. The air above and the ground below are the clock's palaceLandJob (a generator
over ticks: natural blocks inside the box are cleared, hollows under the slab are filled). The full s0 is kept beside it
as <stem>_s0_full.mcstructure for the record. Idempotent: a file already light is left alone.
Usage: palace_light_s0.py [STAGES_DIR]   (default _staging/civ/palace/stages)
Complexity: O(cells) per piece."""
import sys
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
import mcstructure as M  # noqa: E402

DATUM_Y = 15
KEEP_FROM = DATUM_Y - 2                       # feet -2 and up


def lighten(path):
    st = M.Structure.from_bytes(path.read_bytes())
    sx, sy, sz = st.size
    full = path.with_name(path.stem + "_full.mcstructure")
    if not full.exists():
        full.write_bytes(path.read_bytes())
    kept = voided = 0
    for x in range(sx):
        for y in range(sy):
            for z in range(sz):
                i = st.index(x, y, z)
                k = st.layer0[i]
                if k < 0:
                    continue
                name = st.palette[k][0]
                if y >= KEEP_FROM and name != "minecraft:air" and name != "minecraft:structure_void":
                    kept += 1
                    continue
                st.layer0[i] = -1
                st.layer1[i] = -1
                voided += 1
    path.write_bytes(st.to_bytes())
    return kept, voided


if __name__ == "__main__":
    # castle pieces (D-C572, 10-05): --keep-from=-6 keeps the moat (feet -4..-1) and the footings; --glob=mvv_castle_*_s0.mcstructure
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    opts = dict(a[2:].split("=", 1) for a in sys.argv[1:] if a.startswith("--") and "=" in a)
    if "keep-from" in opts:
        KEEP_FROM = DATUM_Y + int(opts["keep-from"])
    d = Path(args[0]) if args else Path("/home/claude/_staging/civ/palace/stages")
    for p in sorted(d.glob(opts.get("glob", "mvv_palace_*_s0.mcstructure"))):
        kept, voided = lighten(p)
        print(f"{p.name}: kept {kept} ground cells, voided {voided}")
