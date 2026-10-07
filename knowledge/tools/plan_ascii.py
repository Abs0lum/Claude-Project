#!/usr/bin/env python3
"""plan_ascii.py — an ASCII plan of a civgen model region at one feet level (for laying stairs into rooms).
Legend: . air  # stone/brick  = planks/floor  | log/post  D door  B bed  S stair(any)  W window  L light  c chest/furniture  ? other"""
def ch(name):
    if name is None: return " "
    n = name.split(":")[-1]
    if n in ("air", "structure_void"): return "."
    if "light_block" in n: return "L"
    if "door" in n: return "D"
    if n == "bed": return "B"
    if "stairs" in n or "spiral" in n: return "S"
    if "glass" in n: return "W"
    if "log" in n or "fence" in n: return "|"
    if "planks" in n or "carpet" in n or "andesite" in n or "slab" in n: return "="
    if "brick" in n or "stone" in n or "cobble" in n: return "#"
    if any(k in n for k in ("chest", "barrel", "table", "chair", "lectern", "furn", "bookshelf")): return "c"
    if "roof" in n: return "^"
    return "?"


def plan(b, x0, x1, z0, z1, feet):
    rows = ["     " + "".join(str(x % 10) for x in range(x0, x1 + 1))]
    for z in range(z0, z1 + 1):
        rows.append(f"{z:4d} " + "".join(ch(b.get(x, feet, z)) for x in range(x0, x1 + 1)))
    return "\n".join(rows)
