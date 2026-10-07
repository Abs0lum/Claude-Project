#!/usr/bin/env python3
"""world_cut.py — read the BLOCKS of a Bedrock world copy (LevelDB) and cut boxes out of it.

Why: his old worlds hold buildings that were never saved as structure templates (the town hall, the bakery, old
streets); the blocks live only in the chunks. This decodes every overworld SubChunkPrefix record (tag 0x2F) of
version 8/9 into a sparse block map, finds clusters of built blocks, and writes a box out as an .mcstructure
(tools/mcstructure.py writer) so the generators can read it like any other template.

Key layout (overworld): chunkX int32 LE | chunkZ int32 LE | tag 0x2F | y-index int8   (other dims add dim int32)
SubChunk v8/v9: version, n storages, (v9: y-index int8), then per storage:
  header byte = bitsPerBlock << 1 | runtimeFlag ; ceil(4096 / (32 // bpb)) uint32 words ; int32 palette size ;
  palette = little-endian NBT compounds {name, states, version}. Index order inside a subchunk: (x*16 + z)*16 + y.
Newest record wins: .ldb files in number order, then the .log (WAL) on top; deletions drop the key.

Usage: world_cut.py <world_dir> census                 -> cluster list of built blocks
       world_cut.py <world_dir> cut x0 y0 z0 x1 y1 z1 <out.mcstructure>
Complexity: O(stored subchunks * 4096)."""
import glob
import struct
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
import ldbscan as L          # noqa: E402
import mcstructure as M      # noqa: E402

NATURAL = {"air", "stone", "dirt", "grass_block", "grass", "short_grass", "tall_grass", "water", "flowing_water", "lava",
           "flowing_lava", "bedrock", "gravel", "sand", "sandstone", "deepslate", "tuff", "granite", "diorite", "andesite",
           "coal_ore", "iron_ore", "copper_ore", "gold_ore", "redstone_ore", "lapis_ore", "diamond_ore", "emerald_ore",
           "deepslate_coal_ore", "deepslate_iron_ore", "deepslate_copper_ore", "deepslate_gold_ore", "deepslate_redstone_ore",
           "deepslate_lapis_ore", "deepslate_diamond_ore", "deepslate_emerald_ore", "snow_layer", "snow", "ice", "packed_ice",
           "clay", "mycelium", "podzol", "coarse_dirt", "dirt_with_roots", "rooted_dirt", "seagrass", "kelp", "fern",
           "large_fern", "dandelion", "poppy", "red_flower", "yellow_flower", "double_plant", "sweet_berry_bush", "vine",
           "glow_lichen", "moss_block", "moss_carpet", "pointed_dripstone", "dripstone_block", "calcite", "amethyst_block",
           "budding_amethyst", "smooth_basalt", "cave_vines", "cave_vines_body_with_berries", "cave_vines_head_with_berries",
           "azalea", "flowering_azalea", "big_dripleaf", "small_dripleaf_block", "hanging_roots", "spore_blossom",
           "mud", "mangrove_roots", "muddy_mangrove_roots", "dead_bush", "cactus", "sugar_cane", "reeds", "bush",
           "leaf_litter", "firefly_bush", "wildflowers", "cobweb", "infested_stone", "magma", "obsidian", "bubble_column"}


def records(world):
    """{key: value} with newest-wins semantics (ldb in number order, then WAL)."""
    kv = {}
    for f in sorted(glob.glob(f"{world}/db/*.ldb"), key=lambda p: int(Path(p).stem)):
        for k, v in L.ldb_entries(f):
            if v is None:
                kv.pop(k, None)
            else:
                kv[k] = v
    for f in sorted(glob.glob(f"{world}/db/*.log"), key=lambda p: int(Path(p).stem)):
        for k, v in L.wal_entries(f):
            if v is None:
                kv.pop(k, None)
            else:
                kv[k] = v
    return kv


def decode_subchunk(val):
    """-> (list of palette dicts, list of 4096 indices) for storage 0, or None."""
    ver = val[0]
    if ver not in (8, 9):
        return None
    n = val[1]
    i = 3 if ver == 9 else 2
    out = None
    for s in range(n):
        hdr = val[i]
        i += 1
        bpb = hdr >> 1
        if bpb == 0:
            idx = [0] * 4096
        else:
            per = 32 // bpb
            words = (4096 + per - 1) // per
            ws = struct.unpack_from(f"<{words}I", val, i)
            i += words * 4
            mask = (1 << bpb) - 1
            idx = [0] * 4096
            p = 0
            for w in ws:
                for k in range(per):
                    if p >= 4096:
                        break
                    idx[p] = (w >> (k * bpb)) & mask
                    p += 1
        npal = struct.unpack_from("<i", val, i)[0] if bpb else 1
        if bpb:
            i += 4
        pal = []
        r = M._R(val)
        r.i = i
        for _ in range(npal):
            t = r.u("<b")
            r.string()
            pal.append(r.payload(t).plain())
        i = r.i
        if s == 0:
            out = (pal, idx)
    return out


def blocks(world, keep=None, box=None):
    """{(x, y, z): (name, states)} for every non-air block in stored overworld subchunks.
    keep(name) -> bool limits what is stored (big worlds do not fit in memory as a full map);
    box = (x0, z0, x1, z1) limits the chunks read."""
    kv = records(world)
    res = {}
    for k, v in kv.items():
        if len(k) != 10 or k[8] != 0x2F:
            continue
        cx, cz = struct.unpack_from("<ii", k, 0)
        cy = struct.unpack_from("<b", k, 9)[0]
        if box and not (box[0] // 16 <= cx <= box[2] // 16 and box[1] // 16 <= cz <= box[3] // 16):
            continue
        try:
            d = decode_subchunk(v)
        except Exception:
            continue
        if not d:
            continue
        pal, idx = d
        names = [p.get("name", "?").replace("minecraft:", "") for p in pal]
        wanted = [n != "air" and (keep is None or keep(n)) for n in names]
        if not any(wanted):
            continue
        for p_i, pi in enumerate(idx):
            if not wanted[pi]:
                continue
            n = names[pi]
            lx, lz, ly = p_i >> 8, (p_i >> 4) & 15, p_i & 15
            res[(cx * 16 + lx, cy * 16 + ly, cz * 16 + lz)] = (n, pal[pi].get("states", {}))
    return res


def census(world):
    b = blocks(world)
    built = {p: v for p, v in b.items() if v[0] not in NATURAL and not v[0].endswith(("_leaves", "_log", "_sapling"))}
    print(f"{world}: {len(b)} blocks, {len(built)} built")
    # cluster by 8-block cells, flood-fill
    cells = {}
    for (x, y, z) in built:
        cells.setdefault((x // 8, z // 8), []).append((x, y, z))
    seen, groups = set(), []
    for c in cells:
        if c in seen:
            continue
        stack, g = [c], []
        seen.add(c)
        while stack:
            q = stack.pop()
            g.append(q)
            for dx in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    n = (q[0] + dx, q[1] + dz)
                    if n in cells and n not in seen:
                        seen.add(n)
                        stack.append(n)
        pts = [p for q in g for p in cells[q]]
        groups.append(pts)
    groups.sort(key=len, reverse=True)
    for pts in groups[:20]:
        xs, ys, zs = zip(*pts)
        top = Counter(built[p][0] for p in pts).most_common(8)
        print(f"  {len(pts):6d} built  x {min(xs)}..{max(xs)}  y {min(ys)}..{max(ys)}  z {min(zs)}..{max(zs)}  {top}")
    return b


def cut(world, box, out):
    x0, y0, z0, x1, y1, z1 = box
    b = blocks(world)
    sx, sy, sz = x1 - x0 + 1, y1 - y0 + 1, z1 - z0 + 1
    pal, pidx, idx = [], {}, []
    for x in range(sx):
        for y in range(sy):
            for z in range(sz):
                n, st = b.get((x0 + x, y0 + y, z0 + z), ("air", {}))
                key = (n, repr(sorted(st.items())))
                if key not in pidx:
                    pidx[key] = len(pal)
                    pal.append((n, st))
                idx.append(pidx[key])
    M.write_structure(out, (sx, sy, sz), pal, idx, origin=(x0, y0, z0)) if hasattr(M, "write_structure") else None
    return (sx, sy, sz), pal, idx


if __name__ == "__main__":
    w, cmd = sys.argv[1], sys.argv[2]
    if cmd == "census":
        census(w)
    elif cmd == "cut":
        box = tuple(int(a) for a in sys.argv[3:9])
        print(cut(w, box, sys.argv[9])[0])
