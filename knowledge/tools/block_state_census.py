#!/usr/bin/env python3
"""block_state_census.py — his GO (D-C309 item 5): where do the 66,346 block permutations come from?
The game counts one permutation per possible state combination of every block (vanilla + custom). For a custom block that
is the product of its `description.states` value counts x its traits (placement_direction: cardinal 4 / facing 6 (+ y_rotation
offset keeps the count); placement_position: block_face 6, vertical_half 2). Census of every behavior pack in his stack.
Output: _docs/blocks/BLOCK-STATE-CENSUS.md + .json"""
import json, re, sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import molang_lint as ML

PACKS = {"BP-02 1.3.206": Path("/home/claude/_build/bp02-206"), "CIVITAS Markers 0.2.1": Path("/home/claude/_build/markers-0.2.1/BP")}
for d in sorted(Path("/tmp/claude-0/bps").iterdir()):
    if "StripMine" in d.name: continue                             # superseded by the 1.3.6 build above
    PACKS[d.name] = d


def n_values(v):
    if isinstance(v, list): return len(v)
    if isinstance(v, dict) and "values" in v:
        r = v["values"]
        if isinstance(r, dict) and "min" in r and "max" in r: return int(r["max"]) - int(r["min"]) + 1
        if isinstance(r, list): return len(r)
    return 1


TRAIT_COUNTS = {("placement_direction", "minecraft:cardinal_direction"): 4, ("placement_direction", "minecraft:facing_direction"): 6,
                ("placement_direction", "minecraft:corner_and_cardinal_direction"): 8,
                ("placement_position", "minecraft:block_face"): 6, ("placement_position", "minecraft:vertical_half"): 2}


def block_perms(desc):
    total, parts = 1, []
    for name, v in (desc.get("states") or {}).items():
        n = n_values(v); total *= n; parts.append((name, n))
    for tname, t in (desc.get("traits") or {}).items():
        tn = tname.split(":")[-1]
        for st in (t.get("enabled_states") or []):
            n = TRAIT_COUNTS.get((tn, st), None)
            if n is None: raise ValueError(f"unknown trait state {tname}/{st}")
            total *= n; parts.append((st, n))
    return total, parts


def family(ident):
    name = ident.split(":")[-1]
    for pat, fam in ((r"^roof|_roof|ridge", "roof pieces"), (r"angled_wall|^wall_|_wall$|wall_dual", "walls"), (r"^furn_|furniture", "furniture"),
                     (r"hearth|flue|rafter|ember|ash_bed", "homestead"), (r"slab|stair", "slabs / stairs"), (r"leaf|leaves", "leaves"),
                     (r"log|wood|bark|trunk", "logs / wood"), (r"frame_post|cornerpost", "CIVITAS frame"), (r"manhole|datum|port_", "CIVITAS markers"),
                     (r"door|trapdoor|window|glass|pane", "doors / windows / glass"), (r"arch|keystone|vault|oculus", "arches / vaults"),
                     (r"floor|plank", "floors / planks"), (r"grass|flower|bush|fern|moss|vine|plant|sapling", "plants"),
                     (r"ground|dirt|mud|sand|gravel|rock|stone|cobble", "ground / stone")):
        if re.search(pat, name): return fam
    return "other"


def census():
    rows = []
    for tag, root in PACKS.items():
        for f in sorted((root / "blocks").rglob("*.json")) if (root / "blocks").exists() else []:
            try: d = ML._parse_json(f.read_text(encoding="utf-8-sig"))
            except Exception as e: rows.append({"pack": tag, "file": str(f.relative_to(root)), "error": str(e)[:80]}); continue
            b = d.get("minecraft:block")
            if not b: continue
            desc = b.get("description", {}); ident = desc.get("identifier", "?")
            n, parts = block_perms(desc)
            rows.append({"pack": tag, "id": ident, "file": str(f.relative_to(root)), "perms": n, "states": parts, "family": family(ident),
                         "permutation_rules": len(b.get("permutations") or [])})
    return rows


if __name__ == "__main__":
    rows = census()
    ok = [r for r in rows if "perms" in r]
    tot = sum(r["perms"] for r in ok)
    by_pack = defaultdict(lambda: [0, 0]); by_fam = defaultdict(lambda: [0, 0])
    for r in ok:
        by_pack[r["pack"]][0] += 1; by_pack[r["pack"]][1] += r["perms"]
        by_fam[r["family"]][0] += 1; by_fam[r["family"]][1] += r["perms"]
    print(f"custom blocks {len(ok)} · permutations {tot:,} · errors {len(rows) - len(ok)}")
    for k, (n, p) in sorted(by_pack.items(), key=lambda kv: -kv[1][1]): print(f"  PACK {k:40s} blocks {n:5d}  perms {p:7,d}")
    for k, (n, p) in sorted(by_fam.items(), key=lambda kv: -kv[1][1]): print(f"  FAMILY {k:28s} blocks {n:5d}  perms {p:7,d}")
    top = sorted(ok, key=lambda r: -r["perms"])[:25]
    for r in top: print(f"  TOP {r['perms']:6d}  {r['id']:40s} {r['pack']:22s} {r['states']}")
    out = Path("/home/claude/_docs/blocks"); out.mkdir(parents=True, exist_ok=True)
    json.dump(rows, open(out / "BLOCK-STATE-CENSUS.json", "w"), indent=1)
