#!/usr/bin/env python3
"""castle_verify.py — "constructed correctly" (his C2, 23:11 CT 10-04): an OFFLINE walkability / enclosure / roof / water
audit of a castlegen model before anything is placed. A player is a 1 x 2 column standing on a solid block; the audit
floods the model from the cell outside the gate (steps of 1 up, drops of 3, doors open, iron bars and panes solid, light
blocks and jib panels walk-through, diagonal moves only where nothing pinches).

Checks (all must pass for a castle to be CONSTRUCTED CORRECTLY):
  R1 ward        every paved ward cell is reachable from outside the gate
  R2 rooms       every room is entered: >= 90 % of its standable floor cells (v0.3: cells inside a spiral stair's well
                 are not room floor — the keep_4 93/101 artifact, F2)
  R3 beds        every bed is reachable (a cell beside it)
  R4 towers      every tower is entered at the ground and every tower floor is reachable (the spiral works); R4b the
                 gatehouse flank towers carry the A_turret spiral, never the fallback newel (F3)
  R5 walk        >= 95 % of the wall-walk cells are reachable (through the towers); R5b >= 90 % of the mural passage
  R6 enclosure   with the gate AND the postern SEALED nothing inside the curtain is reachable from outside
  R7 roofs       every room floor cell has a block over it (no rain inside)
  R8 markers     every station / zone marker stands on a reachable cell (port:sewer markers are pipe ports: excluded)
  R9 drains      every drain head (gully, garderobe chute, kitchen / stable / smithy gully, ditch gully) and every trench
                 cell connects by empty channel to the OUTFALL; the town junction too; no cellar / basement joins a drain
  R10 water      water sources only in the moat / lake, the well shaft and the fountain jet (0 anywhere else)
  R11 beds       garrison steps (lord: G1 >= 6, G2 >= 12, G3 >= 11 -> 29 men + the constable = 30, Conwy; grand: + G4 to
                 60, Krak) + the household (constable, steward, chaplain, marshal, 2 cooks, 2 grooms) + the lord's bed
  R12 hidden     every hidden room is reachable, and NOT reachable once its jib panel / painting is closed
  R13 pieces     (castlegen.write_all) the union of the written pieces == the model, cell for cell
  R14 skyway     the marked skyway slot (walking level 8, 2 wide, 3 high) is clear air
  R15 spacing    no curtain run between towers / gatehouse towers / keep is longer than 34 (<= 32 + rounding)
Usage: castle_verify.py --skin=A|B --size=lord|grand --seed=N   (or import and call verify(castle))"""
import json
import math
import sys
from collections import deque
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")

AIRLIKE = {"minecraft:air", "minecraft:structure_void", "minecraft:light_block_14", "minecraft:light_block_15", "minecraft:torch",
           "minecraft:wall_torch", "minecraft:tall_grass", "minecraft:short_grass", "minecraft:fern", "pw:jib_panel", "pw:secret_painting",
           "minecraft:carpet", "minecraft:rail"}
LIQUID = {"minecraft:water", "minecraft:lava", "minecraft:flowing_water"}


def passable(name, states=None):
    """can a player's body occupy this cell?"""
    if name is None or name in AIRLIKE or name in LIQUID:
        return True
    if name.endswith("_door") or name.endswith("fence_gate"):
        return True
    if name.endswith("carpet") or name.endswith("_sign") or name.endswith("_button") or name.endswith("pressure_plate"):
        return True
    return False


def standable(name):
    """can a player stand ON this cell (as the block under the feet)?"""
    if name is None or name in AIRLIKE or name in LIQUID:
        return False
    if name.endswith("_door") or name.endswith("fence_gate") or name.endswith("carpet"):
        return False
    return True


class Walker:
    def __init__(self, b):
        self.b = b
        self.sx, self.sy, self.sz = b.size
        self.bottom, self.top = b.bottom, b.bottom + self.sy - 1
        self.blocked = set()

    def name(self, x, f, z):
        if not (0 <= x < self.sx and 0 <= z < self.sz and self.bottom <= f <= self.top):
            return "minecraft:bedrock" if f < self.bottom else None
        if (x, f, z) in self.blocked:
            return "minecraft:bedrock"
        return self.b.get(x, f, z)

    def can_stand(self, x, f, z):
        return standable(self.name(x, f - 1, z)) and passable(self.name(x, f, z)) and passable(self.name(x, f + 1, z))

    def column_fit(self, x, f, z):
        return passable(self.name(x, f, z)) and passable(self.name(x, f + 1, z))

    def moves(self, x, f, z):
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            nx, nz = x + dx, z + dz
            if dx and dz:
                if not (self.column_fit(x + dx, f, z) and self.column_fit(x, f, z + dz)):
                    continue
            for nf in (f, f + 1, f - 1, f - 2, f - 3):
                if nf == f + 1 and not passable(self.name(x, f + 2, z)):
                    # a stair tread (vanilla stairs, the program-228 spiral) is walked up, not jumped: his >= 2-block
                    # headroom law (15:1x) — only the two cells of the body are needed
                    sup = self.name(nx, f, nz) or ""
                    if not ("_stairs" in sup or sup.startswith("pw:spiral")):
                        continue
                if nf < f and not all(self.column_fit(nx, g, nz) for g in range(nf, f + 1)):
                    continue
                if self.can_stand(nx, nf, nz):
                    yield (nx, nf, nz)
                    break
        n = self.name(x, f, z)
        if n == "minecraft:ladder":
            for nf in (f + 1, f - 1):
                if self.name(x, nf, z) == "minecraft:ladder" or self.can_stand(x, nf, z):
                    yield (x, nf, z)

    def flood(self, starts):
        seen = set()
        q = deque()
        for s in starts:
            if self.can_stand(*s):
                seen.add(s); q.append(s)
        while q:
            c = q.popleft()
            for n in self.moves(*c):
                if n not in seen:
                    seen.add(n); q.append(n)
        return seen


def drain_flood(c, start):
    """water's way: from `start` through empty channel cells (air / water / iron grates below grade, and every carved
    channel cell at any height — the garderobe chutes)"""
    seen = {start}
    q = deque([start])
    ch = c.channel
    while q:
        x, f, z = q.popleft()
        for dx, df, dz in ((1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1), (0, 1, 0), (0, -1, 0)):
            n = (x + dx, f + df, z + dz)
            if n in seen:
                continue
            nm = c.get(*n)
            if nm is None:
                continue
            if (n[1] <= -2 and nm in ("minecraft:air", "minecraft:water", "minecraft:iron_bars")) or (n in ch and nm in ("minecraft:air", "minecraft:water")):
                seen.add(n); q.append(n)
    return seen


def tower_gaps(c):
    """R15: per ring edge, the gaps between the towers (incl. gatehouse towers, keep) that stand on it"""
    rings = c.poi.get("rings", [])
    tw = [(t["cx"], t["cz"], t["r"]) for t in c.poi["towers"] if t.get("kind") in ("tower", "gatetower", "keep", "posterntower")]
    worst = 0
    detail = []
    for pts in rings:
        n = len(pts)
        for i in range(n):
            a, b = pts[i], pts[(i + 1) % n]
            L = math.hypot(b[0] - a[0], b[1] - a[1])
            if L < 1:
                continue
            ux, uz = (b[0] - a[0]) / L, (b[1] - a[1]) / L
            ts = []
            for (x, z, r) in tw:
                t = (x - a[0]) * ux + (z - a[1]) * uz
                d = abs((x - a[0]) * uz - (z - a[1]) * ux)
                if -r - 2 <= t <= L + r + 2 and d <= r + 3:
                    ts.append(max(0.0, min(L, t)))
            ts = sorted(set([round(t, 1) for t in ts]))
            if not ts or ts[0] > 6:
                ts = [0.0] + ts                 # an edge end without a tower counts from the corner
            if ts[-1] < L - 6:
                ts = ts + [L]
            g = max((q - p for p, q in zip(ts, ts[1:])), default=L)
            detail.append(round(g, 1))
            worst = max(worst, g)
    return round(worst, 1), detail


def verify(c, verbose=True):
    """c: a castlegen Castle — returns (ok, report, reach)"""
    w = Walker(c)
    P = c.poi
    rep = {"size": c.v.W, "variety": c.v.describe()}
    reach = w.flood([P["gate_out"]])
    cols = {(x, z) for (x, f, z) in reach}
    # R1
    ward = P["ward"]
    ward_hit = sum(1 for (x, z) in ward if (x, z) in cols)
    rep["R1_ward"] = [ward_hit, len(ward)]
    # R2 rooms (spiral wells excluded, F2)
    wells = [s["well"] for s in c.spirals if "well" in s]
    def in_well(x, z):
        return any(a <= x <= b and d <= z <= e for (a, d, b, e) in wells)
    rooms = {}
    for kind, (x0, x1, z0, z1, f) in P["rooms"].items():
        cells = [(x, z) for x in range(x0, x1 + 1) for z in range(z0, z1 + 1) if not in_well(x, z) and any(w.can_stand(x, g, z) for g in (f, f + 1))]
        hit = sum(1 for (x, z) in cells if any((x, g, z) in reach for g in (f, f + 1)))
        rooms[kind] = [hit, len(cells)]
    rep["R2_rooms"] = rooms
    rooms_bad = {k: v for k, v in rooms.items() if v[0] < 0.9 * v[1]}
    rep["R2_failing"] = rooms_bad
    # R3
    bed_ok = 0
    bed_bad = []
    for (x, f, z) in P["beds"]:
        if any((x + dx, g, z + dz) in reach for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1), (0, 0), (2, 0), (-2, 0), (0, 2), (0, -2)) for g in (f, f + 1)):
            bed_ok += 1
        else:
            bed_bad.append((x, f, z))
    rep["R3_beds"] = [bed_ok, len(P["beds"])]
    rep["R3_unreached"] = bed_bad[:8]
    # R4
    towers = []
    for t in P["towers"]:
        if not t.get("check", True):
            continue
        inner = t["inner"]
        floors_hit = [any((x, fl + 1, z) in reach for (x, z) in inner) for fl in t["floors"]]
        ground = any((x, 0, z) in reach for (x, z) in inner)
        towers.append({"at": [t["cx"], t["cz"]], "kind": t.get("kind"), "ground": ground, "floors": floors_hit, "spiral": t.get("spiral")})
    rep["R4_towers"] = towers
    r4_bad = [t for t in towers if not (t["ground"] and all(t["floors"]))]
    rep["R4_failing"] = r4_bad
    gate_newel = [t for t in towers if t["kind"] == "gatetower" and t["spiral"] != "A_turret"]
    rep["R4b_gate_towers_newel"] = len(gate_newel)
    rep["spiral_fallbacks"] = sum(1 for s in c.spirals if s.get("fallback"))
    # R5
    walk = P["walk"]
    walk_hit = sum(1 for p in walk if p in reach)
    rep["R5_walk"] = [walk_hit, len(walk)]
    mural = P.get("mural", set())
    mural_hit = sum(1 for p in mural if p in reach)
    rep["R5b_mural"] = [mural_hit, len(mural)]
    # R6 (gate + posterns sealed)
    w2 = Walker(c)
    w2.blocked = set(P["sealed"])
    outside = w2.flood([P["gate_out"]])
    import castlegen as C
    poly = P["inside_poly"]
    leak = [cell for cell in outside if C.point_in_poly(poly, cell[0], cell[2])]
    rep["R6_enclosure_leaks"] = len(leak)
    rep["R6_first_leaks"] = sorted(leak)[:6]
    # R7
    bare = 0
    total = 0
    for kind, (x0, x1, z0, z1, f) in P["rooms"].items():
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                total += 1
                if not any(standable(w.name(x, g, z)) or (w.name(x, g, z) or "").startswith("pw:roof") for g in range(f + 2, w.top + 1)):
                    bare += 1
    rep["R7_bare_floor_cells"] = [bare, total]
    # R8
    mk_ok, mk_n, mk_bad = 0, 0, []
    for m in c.markers:
        if m.get("kind") == "sewer":
            continue
        mk_n += 1
        x, f, z = m["cell"]
        if any((x + dx, g, z + dz) in reach for dx, dz in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)) for g in (f, f + 1)):
            mk_ok += 1
        else:
            mk_bad.append((m.get("fam"), m.get("kind"), x, f, z))
    rep["R8_markers"] = [mk_ok, mk_n]
    rep["R8_unreached"] = mk_bad[:8]
    # R9 drains
    I = c.infra
    out = tuple(I["outfall"]) if I.get("outfall") else None
    dr = drain_flood(c, out) if out else set()
    heads = c.heads
    heads_ok = sum(1 for (x, f, z, k) in heads if (x, f, z) in dr)
    trench_ok = sum(1 for (x, z) in c.trench if (x, -14, z) in dr)
    junction_ok = bool(I.get("junction")) and tuple(I["junction"]) in dr
    dry_bad = 0
    for kind, (x0, x1, z0, z1, f) in P["rooms"].items():
        if f < 0:
            dry_bad += sum(1 for x in range(x0, x1 + 1) for z in range(z0, z1 + 1) if (x, f, z) in dr or (x, f + 1, z) in dr)
    sl = I.get("sluice")
    sluice_ok = (tuple(sl["drop"]) in dr) if sl else None
    rep["R9_drains"] = {"heads": [heads_ok, len(heads)], "trench": [trench_ok, len(c.trench)], "junction": junction_ok,
                        "sluice": sluice_ok, "cellar_cells_joined": dry_bad,
                        "by_kind": {k: sum(1 for h in heads if h[3] == k) for k in sorted({h[3] for h in heads})},
                        "unreached": [h for h in heads if (h[0], h[1], h[2]) not in dr][:6]}
    r9 = heads_ok == len(heads) and trench_ok == len(c.trench) and junction_ok and dry_bad == 0 and sluice_ok is not False
    # R10 water
    sx, sy, sz = c.size
    stray = []
    nwater = 0
    pal = c.st.palette
    wk = {k for k, p in enumerate(pal) if p[0] == "minecraft:water"}
    L0 = c.st.layer0
    for idx, k in enumerate(L0):
        if k in wk:
            nwater += 1
            x, rem = divmod(idx, sy * sz)
            y, z = divmod(rem, sz)
            cell = (x, y + c.bottom, z)
            if cell not in c.water_ok:
                stray.append(cell)
    rep["R10_water"] = {"sources": nwater, "stray": len(stray), "first": stray[:6]}
    # R11 beds
    roles, steps, offices = {}, {}, {}
    for b in c.bed_roles:
        roles[b["role"]] = roles.get(b["role"], 0) + 1
        if b["step"]:
            steps[b["step"]] = steps.get(b["step"], 0) + 1
        if b["office"]:
            offices[b["office"]] = offices.get(b["office"], 0) + 1
    lord = c.v.size_name == "lord"
    want_steps = {"G1": 6, "G2": 12, "G3": 11} if lord else {"G1": 6, "G2": 12, "G3": 15, "G4": 26}
    want_off = {"constable": 1, "steward": 1, "chaplain": 1, "marshal": 1, "cook": 2, "groom": 2, "lord": 1}
    short = {k: [steps.get(k, 0), v] for k, v in want_steps.items() if steps.get(k, 0) < v}
    short.update({k: [offices.get(k, 0), v] for k, v in want_off.items() if offices.get(k, 0) < v})
    guards = roles.get("guard", 0) + offices.get("constable", 0)
    if guards < (30 if lord else 60):
        short["garrison total"] = [guards, 30 if lord else 60]
    rep["R11_beds"] = {"by_role": roles, "steps": steps, "offices": offices, "garrison_men": guards, "short": short}
    # R12 hidden
    hid = []
    for hdn in P.get("hidden", []):
        inside = tuple(hdn["inside"])
        ok_in = inside in reach or any((inside[0] + dx, inside[1], inside[2] + dz) in reach for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        w3 = Walker(c)
        px, pf, pz = hdn["panel"]
        w3.blocked = {(px, pf, pz), (px, pf + 1, pz)}
        r3 = w3.flood([P["gate_out"]])
        closed = inside in r3
        hid.append({"what": hdn["what"], "reached": ok_in, "reached_with_panel_closed": closed})
    rep["R12_hidden"] = hid
    # R14 skyway slot
    sk_bad = 0
    sk_n = 0
    for s in c.skyway:
        for (x, z) in s["cells"]:
            for f in (8, 9, 10):
                sk_n += 1
                if w.name(x, f, z) not in ("minecraft:air", "minecraft:light_block_14", None):
                    sk_bad += 1
    rep["R14_skyway"] = {"slots": len(c.skyway), "cells": sk_n, "blocked": sk_bad}
    # R15 spacing
    worst, detail = tower_gaps(c)
    rep["R15_tower_gap_max"] = worst
    rep["R15_gaps"] = detail
    rep["reachable_cells"] = len(reach)
    ok = (ward_hit == len(ward) and not rooms_bad and bed_ok == len(P["beds"]) and not r4_bad and len(gate_newel) == 0
          and walk_hit >= 0.95 * max(1, len(walk)) and mural_hit >= 0.9 * max(1, len(mural))
          and len(leak) == 0 and bare == 0 and mk_ok == mk_n and r9 and len(stray) == 0 and not short
          and all(h["reached"] and not h["reached_with_panel_closed"] for h in hid) and sk_bad == 0 and worst <= 34)
    rep["OK"] = ok
    rm_ok = sum(1 for v in rooms.values() if v[0] >= 0.9 * v[1])
    rep["summary"] = (f"ward {ward_hit}/{len(ward)} rooms {rm_ok}/{len(rooms)} beds {bed_ok}/{len(P['beds'])} towers {len(towers) - len(r4_bad)}/{len(towers)} "
                      f"walk {walk_hit}/{len(walk)} mural {mural_hit}/{len(mural)} leaks {len(leak)} bare {bare} markers {mk_ok}/{mk_n} "
                      f"drains {heads_ok}/{len(heads)} stray-water {len(stray)} men {guards} gap {worst}")
    if verbose:
        print(json.dumps({k: v for k, v in rep.items() if k not in ("R4_towers", "R15_gaps")}, indent=1, default=list))
    return ok, rep, reach


def main():
    import castlegen as C
    v = C.Variety(C.arg("skin", "A"), C.arg("size", "lord"), C.arg("seed", 1))
    c = C.build(v)
    ok, rep, _ = verify(c)
    print("CONSTRUCTED CORRECTLY" if ok else "NOT YET")
    out = Path("/home/claude/_docs/castle/v0_3") / f"verify-{v.skin}-{v.size_name}-{v.seed}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rep, indent=1, default=list))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
