#!/usr/bin/env python3
"""install_trees_228.py — verify the program-228 regenerated tree templates against the shipped BP-02 1.3.227 set and
install ONLY the changed ones into tools/bp02_overlay_228/structures/pw/trees/ (build_bp02_228 copies the overlay).

Assertions (TREE-TRUNK-PLAN.md §7 + STRUCTURE-AUDIT F5):
  * 544 files, names == FT_TPL_NAMES (pw_ft_tpl_index.js, unchanged) in the same (sorted) order;
  * changed set == the plan's 269 trunk-tip "changed" rows + the 12 jungle_young evens (root fix); all else byte-identical;
  * per changed template: exactly one pw root, same block + states + local position as before; x/z size unchanged, y size
    not larger; every before-leaf still a leaf of the same species with the same states (pw:variant may differ only near
    a removed log: Manhattan <= 4); new leaves only on former logs; no wood added; wood keeps its block (except the doubled
    root above the root, which becomes the trunk log); minecraft:mangrove_roots and every other block unchanged; all wood
    26-connected to the root; 0 trunk logs above the crown top; logs removed / logs -> leaves == the plan's §10 columns;
  * per template (all 544): exactly one pw root, pw:tpl + 16 * pw:tpl_hi == nn.
Usage: install_trees_228.py NEW_DIR [--install]     (writes JSON results next to NEW_DIR as verify.json)"""
import hashlib
import json
import re
import shutil
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
import mcstructure as M  # noqa: E402

SHIP = Path("/home/claude/_build/bp02-227/structures/pw/trees")
INDEX = Path("/home/claude/_build/bp02-227/scripts/pw_ft_tpl_index.js")
PLAN = Path("/home/claude/_docs/program228/TREE-TRUNK-PLAN.md")
OVERLAY = Path("/home/claude/tools/bp02_overlay_228/structures/pw/trees")
VOID = {"minecraft:structure_void", "minecraft:air"}


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def load(p):
    _, root = M.decode(Path(p).read_bytes())
    st = root.value["structure"].value
    size = tuple(t.value for t in root.value["size"].value)
    sx, sy, sz = size
    l0 = [t.value for t in st["block_indices"].value[0].value]
    pal = [(e.value["name"].value, json.dumps(e.value["states"].plain(), sort_keys=True)) for e in
           st["palette"].value["default"].value["block_palette"].value]
    cells = {}
    for idx, pi in enumerate(l0):
        if pi >= 0 and pal[pi][0] not in VOID:
            cells[(idx // (sy * sz), (idx // sz) % sy, idx % sz)] = pal[pi]
    return size, cells


def is_root(n):
    return n.startswith("pw:") and n.endswith("_root")


def is_leaf(n):
    return n.endswith("_leaves")


def is_log(n):           # wood that is trunk / limb (not the vanilla mangrove prop roots)
    return (n.startswith("pw:") and any(n.endswith(s) for s in ("_young", "_mature", "_old", "_elder", "_root"))) \
        or (n.startswith("minecraft:") and n.endswith("_log"))


def is_wood(n):
    return is_log(n) or n == "minecraft:mangrove_roots"


def trunk_of(cells, rootc):
    """the root's footprint (root + root-layer logs within 2 that carry a log above: the 2x2 elders), followed upward
    through logs within one column of the layer below (TREE-TRUNK-PLAN §1)."""
    rx, ry, rz = rootc
    logs = {p for p, (n, _) in cells.items() if is_log(n)}
    layer = {rootc} | {p for p in logs if p[1] == ry and max(abs(p[0] - rx), abs(p[2] - rz)) <= 2 and (p[0], ry + 1, p[2]) in logs}
    trunk = set(layer)
    y = ry
    while layer:
        y += 1
        cols = {(p[0] + dx, p[2] + dz) for p in layer for dx in (-1, 0, 1) for dz in (-1, 0, 1)}
        layer = {p for p in logs if p[1] == y and (p[0], p[2]) in cols}
        trunk |= layer
    return trunk


def plan_rows():
    rows = {}
    for line in PLAN.read_text().splitlines():
        m = re.match(r"\| ([a-z_]+_\d\d) \| (changed|=) \|(.*)\|$", line)
        if m:
            cols = [c.strip() for c in m.group(3).split("|")]
            rows[m.group(1)] = {"changed": m.group(2) == "changed", "removed": int(cols[8]), "to_leaves": int(cols[9])}
    return rows


def connected(wood, start):
    seen, stack = {start}, [start]
    while stack:
        a = stack.pop()
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    b = (a[0] + dx, a[1] + dy, a[2] + dz)
                    if b in wood and b not in seen:
                        seen.add(b)
                        stack.append(b)
    return seen


def main():
    new_dir = Path(sys.argv[1])
    names = json.loads(re.search(r"FT_TPL_NAMES = (\[.*?\]);", INDEX.read_text(), re.S).group(1))
    ship = sorted(p.stem for p in SHIP.glob("*.mcstructure"))
    new = sorted(p.stem for p in new_dir.glob("*.mcstructure"))
    assert len(new) == 544 and new == ship, "template set differs"
    assert names == new, "FT_TPL_NAMES order/name mismatch"
    plan = plan_rows()
    assert len(plan) == 544, len(plan)
    root_fix = {f"jungle_young_{i:02d}" for i in range(0, 24, 2)}
    expect = {k for k, r in plan.items() if r["changed"]} | root_fix
    changed = sorted(s for s in new if md5(SHIP / f"{s}.mcstructure") != md5(new_dir / f"{s}.mcstructure"))
    fails, res = [], {}
    assert set(changed) == expect, f"changed set != plan: extra {sorted(set(changed) - expect)[:10]} missing {sorted(expect - set(changed))[:10]}"
    for s in new:
        size, cells = load(new_dir / f"{s}.mcstructure")
        roots = [p for p, (n, _) in cells.items() if is_root(n)]
        if len(roots) != 1:
            fails.append(f"{s}: {len(roots)} roots")
            continue
        st = json.loads(cells[roots[0]][1])
        if st["pw:tpl"] + 16 * st["pw:tpl_hi"] != int(s[-2:]):
            fails.append(f"{s}: root index")
    var_far = Counter()
    for s in changed:
        bsize, b = load(SHIP / f"{s}.mcstructure")
        asize, a = load(new_dir / f"{s}.mcstructure")
        r = {"size": [bsize, asize]}
        f = lambda m: fails.append(f"{s}: {m}")  # noqa: E731
        if (bsize[0], bsize[2]) != (asize[0], asize[2]) or asize[1] > bsize[1]:
            f(f"size {bsize} -> {asize}")
        broots = sorted((p for p, (n, _) in b.items() if is_root(n)), key=lambda p: p[1])
        aroots = [p for p, (n, _) in a.items() if is_root(n)]
        if len(aroots) != 1 or aroots[0] != broots[0] or a[aroots[0]] != b[broots[0]]:
            f("root moved / changed")
        rootc = broots[0]
        doubled = {p for p in broots[1:]}                       # the 12 jungle evens: the copy one block up
        if doubled and (s not in root_fix or doubled != {(rootc[0], rootc[1] + 1, rootc[2])}):
            f(f"unexpected extra roots {doubled}")
        bw = {p for p, (n, _) in b.items() if is_wood(n)}
        aw = {p for p, (n, _) in a.items() if is_wood(n)}
        if aw - bw:
            f(f"wood added at {sorted(aw - bw)[:4]}")
        for p in aw & bw:
            if a[p] != b[p] and not (p in doubled and is_log(a[p][0]) and not is_root(a[p][0])):
                f(f"wood block changed at {p}: {b[p][0]} -> {a[p][0]}")
        removed = bw - aw
        bl = {p for p, (n, _) in b.items() if is_leaf(n)}
        al = {p for p, (n, _) in a.items() if is_leaf(n)}
        if bl - al:
            f(f"{len(bl - al)} before-leaves lost")
        if (al - bl) - removed:
            f(f"{len((al - bl) - removed)} new leaves not on former logs")
        leaf_names = {b[p][0] for p in bl}
        if {a[p][0] for p in al} != leaf_names:
            f("leaf species changed")
        for p in bl & al:
            if a[p] == b[p]:
                continue
            sa, sb = json.loads(a[p][1]), json.loads(b[p][1])
            sa.pop("pw:variant"), sb.pop("pw:variant")
            if a[p][0] != b[p][0] or sa != sb:
                f(f"leaf state changed at {p}")
                continue
            d = min((abs(p[0] - q[0]) + abs(p[1] - q[1]) + abs(p[2] - q[2]) for q in removed), default=99)
            var_far[d] += 1
            if d > 4:
                f(f"leaf variant changed {d} from a removed log at {p}")
        for p, v in b.items():
            if not is_wood(v[0]) and not is_leaf(v[0]) and a.get(p) != v:
                f(f"other block changed at {p}: {v[0]}")
        for p, v in a.items():
            if not is_wood(v[0]) and not is_leaf(v[0]) and b.get(p) != v:
                f(f"other block added at {p}: {v[0]}")
        mr_b = {p: v for p, v in b.items() if v[0] == "minecraft:mangrove_roots"}
        mr_a = {p: v for p, v in a.items() if v[0] == "minecraft:mangrove_roots"}
        if mr_a != mr_b:
            f("mangrove_roots changed")
        if connected(aw, rootc) != aw:
            f(f"{len(aw - connected(aw, rootc))} wood cells not connected to the root")
        crown_top = max(p[1] for p in al)
        abv = [p for p in trunk_of(a, rootc) if p[1] > crown_top]
        if abv:
            f(f"{len(abv)} trunk logs above the crown top")
        btop, atop = max(p[1] for p in trunk_of(b, rootc)), max(p[1] for p in trunk_of(a, rootc))
        n_rm, n_lv = len(removed), len(al - bl)
        pr = plan.get(s)
        if s in root_fix and not pr["changed"]:
            if removed or (al - bl):
                f("root-fix template lost logs / gained leaves")
        elif (n_rm, n_lv) != (pr["removed"], pr["to_leaves"]):
            f(f"removed/leaves {n_rm}/{n_lv} != plan {pr['removed']}/{pr['to_leaves']}")
        r.update({"trunk_tip": [btop - rootc[1], atop - rootc[1]], "crown_top": crown_top - rootc[1], "logs_removed": n_rm,
                  "logs_to_leaves": n_lv, "leaves": [len(bl), len(al)], "wood": [len(bw), len(aw)], "root_fix": s in root_fix})
        res[s] = r
    groups = Counter(s.rsplit("_", 1)[0] for s in changed)
    out = {"changed": changed, "n_changed": len(changed), "n_identical": 544 - len(changed), "groups": dict(sorted(groups.items())),
           "root_fix": sorted(root_fix), "trunk_tip_changed": sorted(k for k, r in plan.items() if r["changed"]),
           "variant_change_distance": dict(sorted(var_far.items())), "fails": fails, "per_template": res}
    (new_dir.parent / "verify.json").write_text(json.dumps(out, indent=1))
    print(f"changed {len(changed)} (trunk-tip {len(out['trunk_tip_changed'])}, root-fix {len(root_fix)}, overlap "
          f"{len(root_fix & set(out['trunk_tip_changed']))}) · identical {544 - len(changed)} · groups {dict(sorted(groups.items()))}")
    print(f"leaf pw:variant changes by Manhattan distance to a removed log: {dict(sorted(var_far.items()))}")
    print(f"FAILS {len(fails)}", *fails[:30], sep="\n  ")
    if fails:
        raise SystemExit(1)
    if "--install" in sys.argv:
        if OVERLAY.exists() and any(OVERLAY.iterdir()):
            raise SystemExit(f"{OVERLAY} not empty")
        OVERLAY.mkdir(parents=True, exist_ok=True)
        for s in changed:
            shutil.copy2(new_dir / f"{s}.mcstructure", OVERLAY / f"{s}.mcstructure")
        got = sorted(p.stem for p in OVERLAY.glob("*.mcstructure"))
        assert got == changed
        for s in changed:
            assert md5(OVERLAY / f"{s}.mcstructure") == md5(new_dir / f"{s}.mcstructure")
        print(f"INSTALLED {len(got)} -> {OVERLAY}")


if __name__ == "__main__":
    main()
