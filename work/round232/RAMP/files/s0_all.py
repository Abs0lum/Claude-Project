"""For every stage-0 (plot) template: the highest row above the floor (datum 15) up to which EVERY cell is air
(contiguous from the floor), vs the template's top row. Prints families where they differ."""
import sys
sys.path.insert(0, "/home/user/Claude-Project/knowledge/tools")
import mcstructure as M
from pathlib import Path
d = Path(sys.argv[1])
for p in sorted(d.glob("mvv_*_s0.mcstructure")):
    _, root = M.decode(p.read_bytes()); r = root.plain()
    sx, sy, sz = r["size"]; st = r["structure"]; idx = st["block_indices"][0]
    names = [b["name"] for b in st["palette"]["default"]["block_palette"]]
    full = None
    for y in range(15, sy):
        ok = all(idx[(x * sy + y) * sz + z] >= 0 and names[idx[(x * sy + y) * sz + z]] == "minecraft:air" for x in range(sx) for z in range(sz))
        if not ok: break
        full = y - 15
    print(f"{p.name:40s} size {sx}x{sy}x{sz} top_row +{sy-16} all_air_to +{full}")
