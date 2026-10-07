#!/usr/bin/env python3
"""acad2v2_check.py — static checks of an Academy II layout (acad2v2_layout.py), round 232 (#23 / #24).

Usage:  acad2v2_check.py <layout dir> [<baseline layout dir>]
        With a baseline, the report also lists every secret whose marker / host changed and every problem that is NEW
        relative to the baseline (exit 1 if the move introduced one).

Checks (static only: they rule problems OUT, the in-game build rules them IN):
  O1  overlaps(): non-container rooms on one level that double-book a cell (the layout's own rule; passages / tunnels /
      sewers / water exempt).
  O2  passage x room overlaps on G (a walk running THROUGH a building's ground floor) — listed, informational.
  F1  every U room and every B1 room stands over / under a G building (bridges, tunnels, sewers, water, quay, catacombs,
      the precinct wall and the cliff exempt).
  C1  COVERED connectivity on G: buildings + passages, edges = overlap or a shared edge >= 1 cell; flood from the Entrance
      Range (the design claim "covered walks joining every building").
  C2  PAVED connectivity on G: C1 + courts, flood from the Gatehouse.
  C3  OPEN-GROUND raster flood on G (every cell that is not a building, wall or cliff is walkable) from the gate; lists
      enclosed pockets and every building that touches no reached cell.
  C4  U-level clusters: the U rooms inside one G building must join each other (shared edge / overlap).
  C5  the B2 network (tunnels, water, quay, plus the guard cellar, the crypt and the tower's B1 room) joins up.
  S1  each secret's host room on its level (smallest non-container rect holding the marker); route points outside every
      rect are listed.
  T1  STAIRS (if the layout defines them): the well + its 1-cell wall ring lie inside the named host on every level the
      stair passes; the spiral law of tools/spiral_site.py (one quarter turn = 1 block; head tread flush; mid floors
      1 <= a < q - 2); headroom from that law (>= 2 everywhere; >= 3 for vanilla stairs); storey clear heights >= 2.
  P1  piece-grid census (64-block pieces; core = r1..r4 x c1..c4 = Academy I, ring = the rest): each G building core /
      ring / STRADDLE.
"""
import importlib.util
import os
import sys

LEVEL_FEET = {"G": 0, "U": 6, "B1": -7, "B2": -12}
CLEAR = {"G": 5, "U": 5, "B1": 6, "B2": 4}          # air rows: G 0..4 (U slab at 5), U 6..10, B1 -7..-2 (G slab -1), B2 design 4
UNDERGROUND = {"tunnel", "sewer", "water", "catacomb"}
CONTAINERS_DEFAULT = {"court", "wall", "cliff", "garden"}


def load(d):
    spec = importlib.util.spec_from_file_location(f"layout_{abs(hash(d))}", os.path.join(d, "acad2v2_layout.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def ov(a, b):
    return a[0] <= b[2] and b[0] <= a[2] and a[1] <= b[3] and b[1] <= a[3]


def touch(a, b):
    """length of the shared edge between two disjoint rects (0 = none / corner only)"""
    if a[2] + 1 == b[0] or b[2] + 1 == a[0]:
        return max(0, min(a[3], b[3]) - max(a[1], b[1]) + 1)
    if a[3] + 1 == b[1] or b[3] + 1 == a[1]:
        return max(0, min(a[2], b[2]) - max(a[0], b[0]) + 1)
    return 0


def inside(p, r):
    return r[0] <= p[0] <= r[2] and r[1] <= p[1] <= r[3]


def contains(outer, inner):
    return outer[0] <= inner[0] and outer[1] <= inner[1] and inner[2] <= outer[2] and inner[3] <= outer[3]


def name(item, k):
    c, r, l = item
    return l or f"{c}#{k}@{r}"


def flood(nodes, start_ids):
    """nodes: list of (id, rect); BFS over overlap / shared edge"""
    seen = set(start_ids)
    todo = list(start_ids)
    rect = dict(nodes)
    while todo:
        i = todo.pop()
        for j, r in nodes:
            if j not in seen and (ov(rect[i], r) or touch(rect[i], r) > 0):
                seen.add(j)
                todo.append(j)
    return seen


def host(level, p, containers):
    """the host's display name; its IDENTITY (label, or '<category> (unlabelled)') is what a move must keep"""
    best = None
    for k, (c, r, l) in enumerate(level):
        if inside(p, r) and c not in containers:
            area = (r[2] - r[0] + 1) * (r[3] - r[1] + 1)
            if best is None or area < best[0]:
                best = (area, name((c, r, l), k), l or f"{c} (unlabelled)")
    if best:
        return best[1], best[2]
    for k, (c, r, l) in enumerate(level):
        if inside(p, r):
            return name((c, r, l), k), l or f"{c} (unlabelled)"
    return "OPEN GROUND", "OPEN GROUND"


def piece_rows(r):
    return range(r[0] // 64, r[2] // 64 + 1), range(r[1] // 64, r[3] // 64 + 1)


def run(L):
    out, problems = [], []
    cont = getattr(L, "CONTAINERS", CONTAINERS_DEFAULT)
    say = out.append

    # O1
    for lv in ("G", "U", "B"):
        bad = L.overlaps(getattr(L, lv))
        say(f"O1 overlaps({lv}) = {bad}")
        for b in bad:
            problems.append(f"O1 {lv} overlap {b[0]} x {b[2]}")
    # O2
    rooms_g = [(k, it) for k, it in enumerate(L.G) if it[0] not in cont and it[0] != "passage"]
    pas_g = [(k, it) for k, it in enumerate(L.G) if it[0] == "passage"]
    o2 = []
    for kp, p in pas_g:
        for kr, rr in rooms_g:
            if ov(p[1], rr[1]):
                o2.append(f"{name(p, kp)} runs through {name(rr, kr)}")
    say(f"O2 passage-through-building (G, informational): {len(o2)}" + "".join(f"\n     - {t}" for t in o2))
    for t in o2:
        problems.append(f"O2 {t}")
    # F1
    g_build = [it[1] for it in L.G if it[0] not in cont and it[0] != "passage"]
    f1 = []
    for lv in ("U", "B"):
        for k, it in enumerate(getattr(L, lv)):
            c, r, l = it
            if c in cont or c in UNDERGROUND or c == "passage":
                continue
            cells_ok = all(any(inside((x, z), g) for g in g_build) for x in (r[0], r[2]) for z in (r[1], r[3]))
            if not cells_ok:
                f1.append(f"{lv} {name(it, k)} {r} not over/under a G building")
    say(f"F1 upper/basement rooms without a G footprint: {len(f1)}" + "".join(f"\n     - {t}" for t in f1))
    problems += [f"F1 {t}" for t in f1]
    # C1 / C2
    walls = {"wall", "cliff"}
    nodes_cov = [(name(it, k), it[1]) for k, it in enumerate(L.G) if it[0] not in cont]
    nodes_pav = nodes_cov + [(name(it, k), it[1]) for k, it in enumerate(L.G) if it[0] in cont and it[0] not in walls]
    for tag, nodes, start in (("C1 covered (buildings + passages) from the Entrance Range", nodes_cov, "Entrance Range"),
                              ("C2 paved (C1 + courts) from the Gatehouse", nodes_pav, "Gatehouse")):
        reach = flood(nodes, [start])
        miss = [n for n, _ in nodes if n not in reach]
        say(f"{tag}: {len(reach)}/{len(nodes)} reached; NOT reached: {miss}")
        problems += [f"{tag.split()[0]} unreached {n}" for n in miss]
    # C3 raster
    N = L.SIZE
    block = [[0] * N for _ in range(N)]                  # 0 open, 1 building, 2 wall/cliff
    for c, r, l in L.G:
        v = 2 if c in walls else (1 if (c not in cont and c != "passage") else None)
        if v is None:
            continue
        for x in range(r[0], min(r[2], N - 1) + 1):
            row = block[x]
            for z in range(r[1], min(r[3], N - 1) + 1):
                row[z] = max(row[z], v)
    seen = [[False] * N for _ in range(N)]
    sx, sz = 23, 191
    stack = [(sx, sz)]
    seen[sx][sz] = True
    while stack:
        x, z = stack.pop()
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            a, b = x + dx, z + dz
            if 0 <= a < N and 0 <= b < N and not seen[a][b] and block[a][b] == 0:
                seen[a][b] = True
                stack.append((a, b))
    pockets, pseen = [], [[False] * N for _ in range(N)]
    for x in range(N):
        for z in range(N):
            if block[x][z] == 0 and not seen[x][z] and not pseen[x][z]:
                st, cells, bb = [(x, z)], 0, [x, z, x, z]
                pseen[x][z] = True
                while st:
                    a, b = st.pop()
                    cells += 1
                    bb = [min(bb[0], a), min(bb[1], b), max(bb[2], a), max(bb[3], b)]
                    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        u, v = a + dx, b + dz
                        if 0 <= u < N and 0 <= v < N and block[u][v] == 0 and not seen[u][v] and not pseen[u][v]:
                            pseen[u][v] = True
                            st.append((u, v))
                pockets.append((cells, tuple(bb)))
    big = [p for p in pockets if p[1][0] < 312]          # the area beyond the cliff (quay row, feet -12) is not ground level
    say(f"C3 open-ground flood from the gate (23,191): enclosed pockets inside the precinct = {len(big)}"
        + "".join(f"\n     - {c} cells, bbox x{bb[0]}-{bb[2]} z{bb[1]}-{bb[3]}" for c, bb in big))
    problems += [f"C3 pocket bbox x{bb[0]}-{bb[2]} z{bb[1]}-{bb[3]} ({c} cells)" for c, bb in big]
    untouched = []
    for k, it in enumerate(L.G):
        c, r, l = it
        if c in cont or c == "passage":
            continue
        ok = False
        for x in range(max(0, r[0] - 1), min(N - 1, r[2] + 1) + 1):
            for z in (r[1] - 1, r[3] + 1):
                if 0 <= z < N and seen[x][z]:
                    ok = True
        for z in range(max(0, r[1] - 1), min(N - 1, r[3] + 1) + 1):
            for x in (r[0] - 1, r[2] + 1):
                if 0 <= x < N and seen[x][z]:
                    ok = True
        if not ok:
            untouched.append(name(it, k))
    say(f"C3 buildings with no reached open cell beside them (entered only through other buildings): {untouched}")
    # C4
    c4 = []
    for kg, g in enumerate(L.G):
        if g[0] in cont or g[0] == "passage":
            continue
        us = [(name(it, k), it[1]) for k, it in enumerate(L.U) if it[0] not in cont and contains(g[1], it[1])]
        if len(us) > 1:
            reach = flood(us, [us[0][0]])
            if len(reach) < len(us):
                c4.append(f"{name(g, kg)}: U rooms not joined {[n for n, _ in us if n not in reach]}")
    say(f"C4 U-level clusters split: {c4}")
    problems += [f"C4 {t}" for t in c4]
    # C5
    tb = getattr(L, "TOWER_B1", "MUNIMENT ARCHIVE")
    b2 = [(name(it, k), it[1]) for k, it in enumerate(L.B)
          if it[0] in ("tunnel", "water", "catacomb") or (it[2] in ("QUAY (-12)", "Guard cellar", "FOUNDERS' CRYPT", tb))
          or (it[0] == "court" and it[1][0] >= 320)]
    reach = flood(b2, ["Guard cellar"])
    must = ["Basin", "WATER GATE canal", "FOUNDERS' CRYPT", "QUAY (-12)", tb, "CATACOMBS"]
    miss = [m for m in must if m not in reach]
    say(f"C5 B2 network from the Guard cellar: {len(reach)}/{len(b2)} reached; required {must}; missing {miss}")
    problems += [f"C5 B2 missing {m}" for m in miss]
    # tunnel x sewer crossings (each needs a culvert / bridge at build time)
    xs = []
    for it in L.B:
        if it[0] != "tunnel":
            continue
        for jt in L.B:
            if jt[0] == "sewer" and ov(it[1], jt[1]):
                xs.append(f"tunnel {it[1]} x sewer {jt[1]}")
    say(f"   tunnel x sewer crossings (pre-existing design pattern; culvert needed at each): {len(xs)}"
        + "".join(f"\n     - {t}" for t in xs))
    # S1 secrets
    lvmap = {"G": L.G, "U": L.U, "B": L.B}
    hosts = {}
    say("S1 secrets: # | level | marker | host")
    for n, (nm, lv, mk, route) in sorted(L.SECRETS.items()):
        h, ident = host(lvmap[lv], mk, cont)
        hosts[n] = (lv, mk, h, tuple(route), ident)
        say(f"     {n:>2} | {lv} | {mk} | {h}  ({nm})")
        if h == "OPEN GROUND":
            problems.append(f"S1 secret {n} marker on open ground")
    miss_pts = []
    for n, (nm, lv, mk, route) in sorted(L.SECRETS.items()):
        for p in route:
            if not any(inside(p, it[1]) for it in lvmap[lv]) and not (lv == "U" and n == 4):
                miss_pts.append(f"{n} {lv} {p}")
    for n, pts in sorted(L.B_ROUTES.items()):
        for p in pts[1:-1]:
            if not any(inside(p, it[1]) for it in L.B):
                miss_pts.append(f"{n} B-route {p}")
    say(f"   route points in no rect (open-ground ends / turns): {miss_pts}")
    # T1 stairs
    stairs = getattr(L, "STAIRS", None)
    if stairs is None:
        say("T1 STAIRS: not defined in this layout (skipped)")
    else:
        for lv, c in CLEAR.items():
            if c < 2:
                problems.append(f"T1 storey {lv} clear {c} < 2")
        say(f"T1 storey clear heights: {CLEAR} (all >= 2; vanilla stairs need 3: {all(c >= 3 for c in CLEAR.values())})")
        for s in stairs:
            n_ = {"A": 1, "B": 2, "C": 3}[s["type"]]
            x0, z0 = s["well"]
            well = (x0, z0, x0 + 2 * n_ - 1, z0 + 2 * n_ - 1)
            ring = (well[0] - 1, well[1] - 1, well[2] + 1, well[3] + 1)
            f0, floors = s["f0"], sorted(s["floors"])
            top = floors[-1]
            q = top - f0
            mids = [S - f0 - 1 for S in floors[:-1]]
            law = all(1 <= a < q - 2 for a in mids)
            hosts_ok = []
            for lvname, label in s["hosts"].items():
                lv = {"G": L.G, "U": L.U, "B1": L.B}[lvname]
                hr = [label] if isinstance(label, tuple) else [it[1] for it in lv if it[2] == label]
                if isinstance(label, tuple):        # a rect host must itself be a room / void on that level
                    hr = [it[1] for it in lv if it[1] == label]
                ok = bool(hr) and contains(hr[0], ring)
                hosts_ok.append(f"{lvname}:{label}={'ok' if ok else 'FAIL'}")
                if not ok:
                    problems.append(f"T1 stair {s['name']} wall ring {ring} not inside {lvname} {label}")
            # spiral law headroom: a full turn rises 4 blocks; one tread 1 block -> 3 clear mid-run; the head landing
            # 2.0 .. 2.75 (tools/spiral_site.py docstring, his >= 2-block law)
            head_min = 2.0
            say(f"T1 {s['name']} ({s['type']}, well {well}, wall ring {ring}): feet {f0} -> {top}, q = {q} quarters, mid floors "
                f"{mids} law {'ok' if law else 'FAIL'}; headroom mid-run 3, head landing >= {head_min}; hosts {hosts_ok}")
            if not law:
                problems.append(f"T1 stair {s['name']} mid floor too close to foot/top")
    # P1 piece census
    say("P1 piece census (core r1..r4 x c1..c4 = x/z 64..319):")
    for k, it in enumerate(L.G):
        c, r, l = it
        if c in ("wall", "cliff"):
            continue
        rows, cols = piece_rows(r)
        pcs = [(i, j) for i in rows for j in cols]
        core = [p for p in pcs if 1 <= p[0] <= 4 and 1 <= p[1] <= 4]
        kind = "core" if len(core) == len(pcs) else ("ring" if not core else "STRADDLE")
        extra = ""
        if kind == "STRADDLE":
            cut = (max(r[0], 64), max(r[1], 64), min(r[2], 319), min(r[3], 319))
            extra = f" | core part {cut}"
        say(f"     {kind:8} {c:8} {name(it, k):30} {r} pieces {['r%dc%d' % p for p in pcs]}{extra}")
    return out, problems, hosts


def main():
    d = sys.argv[1]
    L = load(d)
    out, problems, hosts = run(L)
    print(f"=== acad2v2_check: {os.path.join(d, 'acad2v2_layout.py')}")
    print("\n".join(out))
    rc = 0
    if len(sys.argv) > 2:
        B = load(sys.argv[2])
        _, bprob, bhosts = run(B)
        print(f"\n=== against baseline {os.path.join(sys.argv[2], 'acad2v2_layout.py')}")
        moved = []
        for n in sorted(hosts):
            a, b = bhosts.get(n), hosts[n]
            if a != b:
                moved.append(n)
                print(f"  secret {n:>2}: {a[0]} {a[1]} host '{a[4]}' route {list(a[3])}  ->  {b[0]} {b[1]} host '{b[4]}' route {list(b[3])}")
        for n in sorted(set(B.B_ROUTES) | set(L.B_ROUTES)):
            if B.B_ROUTES.get(n) != L.B_ROUTES.get(n):
                print(f"  B-route {n:>2}: {B.B_ROUTES.get(n)}  ->  {L.B_ROUTES.get(n)}")
        hchg = [n for n in moved if bhosts[n][4] != hosts[n][4]]
        print(f"  secrets changed: {len(moved)} {moved}; host NAME changed: {hchg}")
        new = [p for p in problems if p not in bprob]
        gone = [p for p in bprob if p not in problems]
        print(f"  problems: baseline {len(bprob)}, now {len(problems)}; NEW {len(new)}: {new}")
        print(f"  problems resolved vs baseline: {gone}")
        if new or hchg:
            rc = 1
    else:
        print(f"\nproblems ({len(problems)}): {problems}")
    print(f"\nRESULT: {'PASS' if rc == 0 else 'FAIL'}")
    sys.exit(rc)


if __name__ == "__main__":
    main()
