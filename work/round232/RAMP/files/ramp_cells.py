"""List every pw:ramp_* block in a road piece: (x, y, z) -> name + states, grouped per x (the travel axis)."""
import sys
sys.path.insert(0, "/home/user/Claude-Project/knowledge/tools")
import mcstructure as M
from pathlib import Path
from collections import Counter, defaultdict
for p in sys.argv[1:]:
    _, root = M.decode(Path(p).read_bytes()); r = root.plain()
    sx, sy, sz = r["size"]; st = r["structure"]; idx = st["block_indices"][0]
    pal = st["palette"]["default"]["block_palette"]
    print("==", Path(p).name, (sx, sy, sz))
    per = defaultdict(Counter)
    for x in range(sx):
        for y in range(sy):
            for z in range(sz):
                k = idx[(x * sy + y) * sz + z]
                if k < 0: continue
                b = pal[k]
                if "ramp" in b["name"]:
                    per[x][(y, b["name"], tuple(sorted(b["states"].items())), )] += 1
    for x in sorted(per):
        for (y, n, s), c in sorted(per[x].items()):
            zs = [z for z in range(sz) if idx[(x * sy + y) * sz + z] >= 0 and pal[idx[(x * sy + y) * sz + z]]["name"] == n]
            print(f"  x{x} y{y} {n} {dict(s)} x{c} z{min(zs)}..{max(zs)}")
