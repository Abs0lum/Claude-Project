#!/usr/bin/env python3
"""entity_precedence.py — D-C284 standing check: which client-entity definition WINS in his stack.

When two packs define the same client entity identifier, the engine keeps ONE: the highest min_engine_version (L-ENT-PREC,
the 1.4.12 chicken fix), and on a tie the pack higher in his list (the 1.4.20 enderman: StripMine RP 3.0.1, above RP-07,
drew its April entity). This lists every identifier defined by two or more packs of his stack and the one that wins, and
flags every case where one of OUR packs' definitions loses to a pack above it on a tie or to a higher min_engine_version.
API: census(order) -> rows; order = [(name, dir-or-mcpack)], TOP pack first (his Resource Packs list order)."""
import sys, zipfile
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import molang_lint as ML

ROOT = Path("/home/claude")


def ver(s):
    try: return tuple(int(x) for x in str(s).split("."))
    except Exception: return (0,)


def entities(src):
    src = Path(src); out = {}
    if src.is_dir():
        items = [(str(p.relative_to(src)), p.read_bytes()) for p in (src / "entity").rglob("*.json")] if (src / "entity").exists() else []
    else:
        z = zipfile.ZipFile(src); items = [(n, z.read(n)) for n in z.namelist() if n.startswith("entity/") and n.endswith(".json")]
    for n, b in items:
        try: d = ML._parse_json(b.decode("utf-8-sig"))
        except Exception: continue
        desc = (d.get("minecraft:client_entity") or {}).get("description") or {}
        if desc.get("identifier"): out.setdefault(desc["identifier"], []).append((n, desc.get("min_engine_version")))
    return out


def census(order, ours=("RP-06", "RP-07", "RP-08")):
    defs = {}
    for rank, (name, src) in enumerate(order):
        for ident, lst in entities(src).items():
            for n, mev in lst: defs.setdefault(ident, []).append((rank, name, n, mev))
    rows = []
    for ident, lst in sorted(defs.items()):
        packs = {x[1] for x in lst}
        if len(packs) < 2: continue
        win = sorted(lst, key=lambda x: (tuple(-v for v in ver(x[3])), x[0]))[0]       # highest version, then highest pack
        lost = [x for x in lst if x is not win and any(x[1].startswith(o) for o in ours)]
        rows.append({"id": ident, "winner": f"{win[1]} {win[2]} ({win[3]})", "defs": [f"{x[1]} {x[2]} ({x[3]})" for x in lst],
                     "ours_lose": [f"{x[1]} {x[2]} ({x[3]})" for x in lost]})
    return rows


if __name__ == "__main__":
    ORDER = [("StripMine RP 3.0.1", ROOT / "_intake/stack-rps/PW-StripMine-RP-v3_0_1.mcpack"), ("RP-08", ROOT / "_build/rp08-148"),
             ("RP-07", ROOT / "_build/rp07-1421"), ("RP-06", ROOT / "_build/rp06-1415")]
    for r in census(ORDER):
        print(("LOSES " if r["ours_lose"] else "ok    ") + f"{r['id']:34} winner {r['winner']:60} lose {r['ours_lose']}")
