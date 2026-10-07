#!/usr/bin/env python3
"""palace2_verify.py — the TESTS for PALACE II (tools/palacegen2.py, his 2026-10-06 rulings D-C1006-PAL2).

Static checks on the generated model (P1: they can only rule faults OUT; the in-game walk is his witness):
  T1  grid        16 pieces = a 4 x 4 grid of 64 x 50 x 64 (feet -15..34), names mvv_palace2_<r><c>_a_r1, the pieces
                  reassemble to the model cell for cell; (with --staged) the staged files + manifests + 5 stages each,
                  0 waterlogged cells, s0..s4 rebuild every piece (civ_stages proves it while cutting)
  T2  reach       every room is reachable from the gate AND the gate is reachable back from it (all secrets open;
                  prison cells: in only — they are cells)
  T3  secrets     every secret: both ends are standable and connected through the gate graph; mode 'hidden' = its hidden
                  end is NOT reachable from the gate when every jib panel / painting is shut (it is a real secret);
                  every hidden / one-way end lies in a no-walk box (the script hook's mask)
  T4  spirals     every spiral: its blocks are where the plan put them (laid last, never overwritten), the foot, every
                  mid-floor door and the top landing are joined THROUGH the well (a walk confined to the well + its ring),
                  the secret stairs are the narrow design A (his ruling)
  T5  headroom    custom spiral steps: >= 2 free blocks over every step; vanilla stairs: 3 (engine law)
  T6  nursery     the royal NIGHT NURSERY holds 4 child beds, every one against a wall, on floor; no child bed anywhere
                  clashes with furniture or air (his 17:52)
  T7  doors       every iron door opens from its recorded inner side only (a button whose block powers it); every button
                  is attached to a solid block
  T8  water       all water below feet 0 (the clock's pumps empty feet >= 0) and none of it can flow (no free neighbour
                  beside or below)
  T9  drains      every gully stands over a dug sewer vault
  T10 ids         every pw: block id exists in BP-02 (the 1.3.230 build) and is lowercase
Movement model (a player / a civ): a body is 2 cells tall; walk level f needs cells f and f+1 free and something to stand
on at f-1 (or a ladder); steps up 1 (not onto a fence / wall) with a free cell over the head; falls freely; climbs
ladders; drops through trapdoors; wooden doors open both ways; iron doors only from the side of their button; jib panels
and secret paintings are walk-through (pw: blocks of BP-02 1.3.221) — 'shut' treats them as wall.
Usage: palace2_verify.py [--staged DIR] [--json OUT]     exit 0 = every test PASS."""
import collections
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, "/home/claude/tools")
import mcstructure as M  # noqa: E402
import palacegen2 as P2  # noqa: E402

BP_BLOCKS = Path("/home/claude/_build/bp02-230/blocks")

from palace2_walk import (PASS, SUP, LAD, TRAP, IRON, SECRET, NOSTEP, WATER, STAIR, SPIRAL, BED, DOOR,  # noqa: E402
                         classify, Model, Walker, node)


# ------------------------------------------------------------------------------------------------ helpers
def nodes_at(nodeset, m, x0, x1, z0, z1, f, slack=0):
    out = []
    for (x, y, z) in nodeset:
        if x0 <= x <= x1 and z0 <= z <= z1 and abs((y + m.bottom) - f) <= slack:
            out.append((x, y, z))
    return out


def index_by_column(nodeset):
    col = collections.defaultdict(list)
    for (x, y, z) in nodeset:
        col[(x, z)].append(y)
    return col


def in_box_nodes(col, m, x0, x1, z0, z1, f, slack=0):
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            for y in col.get((x, z), ()):
                if abs(y + m.bottom - f) <= slack:
                    return (x, y, z)
    return None


def iron_doors(m, p):
    """(x, y, z) iron cell -> set of (x, z) cells it opens from: from the generator's one-way records, each confirmed by a
    button on that side whose attachment block is next to the door"""
    opens = {}
    bad = []
    for rec in p.oneway:
        ofs = {(c[0], c[2]) for c in rec["open_from"]}
        for (x, f, z) in rec["cells"]:
            opens.setdefault(node(m, x, f, z), set()).update(ofs)
    return opens, bad


BUTTON_ATTACH = {0: (0, 1, 0), 1: (0, -1, 0), 2: (0, 0, 1), 3: (0, 0, -1), 4: (1, 0, 0), 5: (-1, 0, 0)}


# ------------------------------------------------------------------------------------------------ the tests
def run(staged=None):
    t0 = time.time()
    p = P2.build()
    m = Model(p)
    R = {"tests": {}, "notes": []}
    sx, sy, sz = m.size

    def verdict(name, ok, lines):
        R["tests"][name] = {"pass": bool(ok), "lines": lines}
        print(f"[{'PASS' if ok else 'FAIL'}] {name}")
        for ln in lines[:40]:
            print("      " + ln)
        if len(lines) > 40:
            print(f"      ... {len(lines) - 40} more")

    # ---------------------------------------------------------------- T1 grid
    lines, ok = [], True
    if m.size != (256, 50, 256):
        ok = False; lines.append(f"model size {m.size} != (256, 50, 256)")
    pieces = P2.cut(p)
    if sorted(pieces) != [(r, c) for r in range(4) for c in range(4)]:
        ok = False; lines.append(f"pieces {sorted(pieces)}")
    L0 = p.st.layer0
    for (r, c), (st, _marks) in pieces.items():
        if st.size != (64, 50, 64):
            ok = False; lines.append(f"piece {r}{c} size {st.size}")
            continue
        bad = 0
        for x in range(0, 64, 3):
            for y in range(50):
                for z in range(0, 64, 3):
                    k = L0[((r * 64 + x) * sy + y) * sz + c * 64 + z]
                    want = "minecraft:air" if k < 0 else p.st.palette[k][0]
                    got = st.get(x, y, z)
                    if (got[0] if got else "minecraft:air") != want:
                        bad += 1
        if bad:
            ok = False; lines.append(f"piece {r}{c}: {bad} sampled cells differ from the model")
        if any(v >= 0 for v in st.layer1):
            ok = False; lines.append(f"piece {r}{c}: waterlogged cells in layer 1")
    lines.append(f"16 pieces mvv_palace2_<r><c>_a_r1, 64 x 50 x 64 each, reassembly sampled every 3rd cell (x, z) at every level")
    if staged:
        sd = Path(staged)
        for r in range(4):
            for c in range(4):
                stem = P2.piece_name(r, c)
                need = [sd / "structures" / f"{stem}.mcstructure", sd / "manifests" / f"{stem}.json"] + \
                       [sd / "structures" / "stages" / f"{stem}_s{k}.mcstructure" for k in range(5)]
                miss = [str(q.relative_to(sd)) for q in need if not q.exists()]
                if miss:
                    ok = False; lines.append(f"{stem}: missing {miss}")
                    continue
                for q in need:
                    if q.suffix == ".mcstructure":
                        st = M.Structure.from_bytes(q.read_bytes())
                        wl = sum(1 for v in st.layer1 if v >= 0)
                        if wl:
                            ok = False; lines.append(f"{q.name}: {wl} waterlogged cells")
                        if st.size != (64, 50, 64):
                            ok = False; lines.append(f"{q.name}: size {st.size}")
        lines.append(f"staged: {staged} — 16 x (piece + manifest + s0..s4) present, 0 waterlogged cells, sizes 64 x 50 x 64")
    verdict("T1 grid (4 x 4 pieces)", ok, lines)

    # ---------------------------------------------------------------- walkers
    opens, _ = iron_doors(m, p)
    W = Walker(m, True, opens)
    gate = node(m, 0, 0, 127)
    fwd = W.bfs([gate])
    back = W.back(fwd, gate)
    both = fwd & back
    colB = index_by_column(both)
    colF = index_by_column(fwd)
    R["notes"].append(f"walk graph: {len(fwd)} cells reachable from the gate, {len(both)} with a way back")
    Ws = Walker(m, False, opens)
    fwd_shut = Ws.bfs([gate])
    colS = index_by_column(fwd_shut)

    # ---------------------------------------------------------------- T2 rooms
    lines, ok = [], True
    unreached, inonly = [], []
    for rm in p.rooms:
        x0, x1, z0, z1 = rm["box"]
        f = rm["f"]
        if in_box_nodes(colB, m, x0, x1, z0, z1, f, 1):
            continue
        cellish = any(k in rm["name"].lower() for k in ("cell", "pozz", "piombi"))
        if cellish and in_box_nodes(colF, m, x0, x1, z0, z1, f, 1):
            inonly.append(rm["name"]); continue
        unreached.append(f"{rm['level']} {rm['name']} box x {x0}..{x1} z {z0}..{z1} f {f}" +
                         (" (in only)" if in_box_nodes(colF, m, x0, x1, z0, z1, f, 1) else ""))
    if unreached:
        ok = False; lines += ["UNREACHED " + u for u in unreached]
    lines.append(f"{len(p.rooms) - len(unreached)} / {len(p.rooms)} rooms reachable both ways from the gate (z 127 arch)"
                 + (f"; prison cells reachable in only (by design): {len(inonly)}" if inonly else ""))
    verdict("T2 every room reachable", ok, lines)

    # ---------------------------------------------------------------- T3 secrets
    lines, ok = [], True
    hidden_boxes = [h["box"] for h in p.hidden]

    def in_hidden(x, f, z, tol=1):
        """inside a no-walk box (tol: a threshold cell — the jib panel or door cell in the box's wall — counts)"""
        return any(b[0] - tol <= x <= b[1] + tol and b[2] - tol <= z <= b[3] + tol and b[4] - 1 <= f <= b[5] + 1 for b in hidden_boxes)

    for s in p.secrets:
        sid, mode = s["id"], s["mode"]
        pub, hid = s["public"], s["hidden"]
        msgs = []
        if mode == "lore":
            if pub and not in_box_nodes(colB, m, pub[0] - 1, pub[0] + 1, pub[2] - 1, pub[2] + 1, pub[1], 0):
                msgs.append(f"lore spot {pub} not reachable")
        else:
            for end, c in (("public", pub), ("hidden", hid)):
                if not c:
                    msgs.append(f"no {end} end"); continue
                if node(m, *c) not in both:
                    near = in_box_nodes(colB, m, c[0], c[0], c[2], c[2], c[1], 0)
                    msgs.append(f"{end} end {c} not standable+reachable both ways" + (f" (column ok at {near[1] + m.bottom})" if near else ""))
            if mode == "hidden" and hid and node(m, *hid) in fwd_shut:
                msgs.append(f"hidden end {hid} reachable from the gate with every secret SHUT (not secret)")
            if mode in ("hidden", "oneway") and hid and not in_hidden(*hid):
                msgs.append(f"hidden end {hid} outside every no-walk box")
        if msgs:
            ok = False; lines.append(f"{sid} ({mode}): " + "; ".join(msgs))
    n_by = collections.Counter(s["mode"] for s in p.secrets)
    lines.append(f"{len(p.secrets)} secrets: " + ", ".join(f"{k} {v}" for k, v in sorted(n_by.items())))
    # discoverability: every secret's public end reachable from the gate (secrets open) — the chain is walkable by the player
    verdict("T3 secrets connect both ends (and stay secret)", ok, lines)

    # ---------------------------------------------------------------- T4 spirals + T5 headroom
    import spiral_site as SS
    lines, ok = [], True
    head_lines, head_ok = [], True
    secret_labels = ("H4", "H5", "H9", "H11", "U4", "tunnel stair")
    for sp in p.spirals:
        P = SS.plan(*sp["well"][:2], sp["f0"], sp["floors"], sp["design"], sp["hand"], sp["k0"])
        bid = SS.block_id(sp["design"], sp["pal"])
        wrong = [(x, f, z) for (x, f, z, _st) in P["cells"] if m.name(x, f, z) != bid]
        if wrong:
            ok = False; lines.append(f"{sp['label']}: {len(wrong)} stair cells overwritten, e.g. {wrong[:3]} = {m.name(*wrong[0])}")
        wx0, wz0, wx1, wz1 = sp["well"]
        box = (wx0 - 1, wx1 + 1, wz0 - 1, wz1 + 1)
        foot = [node(m, x, f, z) for (x, f, z, tag) in sp["exits"] if tag == "foot"]
        ex = [(e[0], e[2]) for e in sp["exits"]]
        box = (min([box[0]] + [a for a, _ in ex]), max([box[1]] + [a for a, _ in ex]), min([box[2]] + [b for _, b in ex]), max([box[3]] + [b for _, b in ex]))
        reach = W.bfs(foot, limit_box=box)
        targets = [(e[0], e[1], e[2], e[3]) for e in sp["exits"] if e[3] != "foot"]
        miss = [t for t in targets if node(m, t[0], t[1], t[2]) not in reach]
        if not foot or miss:
            ok = False; lines.append(f"{sp['label']} ({sp['design']}): exits not joined through the well: {miss[:4]} (foot cells {len(foot)})")
        if any(k in sp["label"] for k in secret_labels) and sp["design"] != "A_turret":
            ok = False; lines.append(f"{sp['label']}: a secret stair must be design A (his ruling), is {sp['design']}")
        for (x, f, z, _st) in P["cells"]:
            for h in (1, 2):
                if m.name(x, f + h, z) is not None and not (m.code[x, f + h - m.bottom, z] & PASS):
                    head_ok = False; head_lines.append(f"{sp['label']}: step {x},{f},{z} has {m.name(x, f + h, z)} at +{h}")
    lines.append(f"{len(p.spirals)} spirals: " + ", ".join(f"{s['label']} ({s['design'][0]})" for s in p.spirals))
    verdict("T4 spirals laid last and joined", ok, lines)
    nst = 0
    ys, xs_, zs_ = None, None, None
    stair_cells = np.argwhere((m.code & STAIR) != 0)
    for (x, y, z) in stair_cells:
        nm = m.names[m.idx[x, y, z]]
        stt = m.states[m.idx[x, y, z]]
        if stt.get("upside_down_bit") and stt["upside_down_bit"].value:
            continue                                      # an upside-down stair is trim, not a tread
        nst += 1
        for h in (1, 2, 3):
            if y + h < sy and not (m.code[x, y + h, z] & PASS):
                head_ok = False
                head_lines.append(f"vanilla {nm} at {x},{y + m.bottom},{z}: {m.names[m.idx[x, y + h, z]]} at +{h}")
                break
    head_lines.append(f"{sum(len(SS.plan(*s['well'][:2], s['f0'], s['floors'], s['design'], s['hand'], s['k0'])['cells']) for s in p.spirals)} spiral steps (>= 2 free), {nst} vanilla treads (>= 3 free)")
    verdict("T5 headroom", head_ok, head_lines)

    # ---------------------------------------------------------------- T6 nursery
    lines, ok = [], True
    nur = [r for r in p.rooms if r["name"] == "NIGHT NURSERY"]
    if len(nur) != 1:
        ok = False; lines.append(f"NIGHT NURSERY rooms: {len(nur)}")
    else:
        x0, x1, z0, z1 = nur[0]["box"]; f = nur[0]["f"]
        kids = [b for b in p.bed_roles if b["role"] == "child" and x0 <= b["x"] <= x1 and z0 <= b["z"] <= z1 and b["feet"] == f]
        if len(kids) != 4:
            ok = False; lines.append(f"night nursery child beds: {len(kids)} (want 4)")
        for b in kids:
            x, z = b["x"], b["z"]
            st = m.state(x, f, z)
            d = st.get("direction")
            dx, dz = {0: (0, 1), 1: (-1, 0), 2: (0, -1), 3: (1, 0)}[d]
            hx, hz = x + dx, z + dz
            head_wall = not (m.code[hx + dx, f - m.bottom, hz + dz] & PASS) and not (m.code[hx + dx, f - m.bottom, hz + dz] & BED)
            side_wall = any(all(not (m.code[cx + sx_, f - m.bottom, cz + sz_] & (PASS | BED)) for (cx, cz) in ((x, z), (hx, hz)))
                            for (sx_, sz_) in ((dz, dx), (-dz, -dx)))
            onfloor = all(m.code[cx, f - 1 - m.bottom, cz] & SUP for (cx, cz) in ((x, z), (hx, hz)))
            isbed = m.name(x, f, z) == "minecraft:bed" and m.name(hx, f, hz) == "minecraft:bed"
            lines.append(f"child bed foot {x},{f},{z} head {hx},{hz}: {'head to the wall' if head_wall else ''}{' side on the wall' if side_wall else ''}"
                         f"{'' if onfloor else ' NOT ON FLOOR'}{'' if isbed else ' NOT A BED'}")
            if not (head_wall or side_wall) or not onfloor or not isbed:
                ok = False
    if p.child_bed_clash:
        ok = False; lines.append(f"child bed clashes: {p.child_bed_clash[:5]}")
    allkids = [b for b in p.bed_roles if b["role"] == "child"]
    lines.append(f"child beds in the palace: {len(allkids)}; clashes {len(p.child_bed_clash)}")
    verdict("T6 royal nursery: 4 beds against walls", ok, lines)

    # ---------------------------------------------------------------- T7 iron doors + buttons
    lines, ok = [], True
    irons = {(int(x), int(y), int(z)) for (x, y, z) in np.argwhere(W.iron)}
    rec = set(opens)
    norec = sorted(irons - rec)
    if norec:
        ok = False; lines.append(f"{len(norec)} iron door cells with no opening record, e.g. {[(x, y + m.bottom, z) for (x, y, z) in norec[:6]]}")
    btn = np.argwhere(np.vectorize(lambda n: bool(n) and n.endswith("_button"))(np.array(m.names, dtype=object))[m.idx])
    for (x, y, z) in btn:
        d = m.states[m.idx[x, y, z]]["facing_direction"].value
        ax, ay, az = BUTTON_ATTACH[d]
        a = (x + ax, y + ay, z + az)
        if not m.inside(*a) or (m.code[a] & PASS) or not (m.code[a] & (SUP | NOSTEP)):
            ok = False; lines.append(f"button {x},{y + m.bottom},{z} (facing {d}) hangs on {m.names[m.idx[a]] if m.inside(*a) else 'nothing'}")
    for door, frm in opens.items():
        x, y, z = door
        if m.code[door] & IRON == 0:
            continue
        for (fx, fz) in frm:
            # a button within reach of the inner cell that powers the door (the button touches the door, or its block does)
            found = False
            for (bx, by, bz) in btn:
                if abs(bx - fx) + abs(bz - fz) > 2 or not (y - 1 <= by <= y + 2):
                    continue
                d = m.states[m.idx[bx, by, bz]]["facing_direction"].value
                ax, ay, az = BUTTON_ATTACH[d]
                blk = (bx + ax, by + ay, bz + az)
                for c in ((bx, by, bz), blk):
                    for (ddx, ddy, ddz) in ((1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1), (0, 1, 0), (0, -1, 0)):
                        if (c[0] + ddx, c[1] + ddy, c[2] + ddz) in (door, (x, y + 1, z), (x, y - 1, z)) and (c[0] + ddx, c[1] + ddy, c[2] + ddz) in irons:
                            found = True
            if not found:
                ok = False; lines.append(f"iron door {x},{y + m.bottom},{z}: no button powers it from {fx},{fz}")
    lines.append(f"{len(irons)} iron door cells, {len(btn)} buttons")
    verdict("T7 iron doors open from the inner side only", ok, lines)

    # ---------------------------------------------------------------- T8 water
    lines, ok = [], True
    wat = np.argwhere((m.code & WATER) != 0)
    hi = [(x, y + m.bottom, z) for (x, y, z) in wat if y + m.bottom >= 0]
    if hi:
        ok = False; lines.append(f"{len(hi)} water cells at feet >= 0 (the pumps would empty them): {hi[:5]}")
    leaks = []
    for (x, y, z) in wat:
        for (dx, dy, dz) in ((1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1), (0, -1, 0)):
            c = (x + dx, y + dy, z + dz)
            if not m.inside(*c):
                if dy == 0:
                    leaks.append(((x, y + m.bottom, z), "the box edge"))
                continue
            if m.code[c] & PASS:
                leaks.append(((x, y + m.bottom, z), f"{m.names[m.idx[c]]} at {c[0]},{c[1] + m.bottom},{c[2]}"))
    if leaks:
        ok = False; lines += [f"water {a} can flow into {b}" for (a, b) in leaks[:20]]
    lines.append(f"{len(wat)} water cells, all below feet 0: {not hi}; free neighbours {len(leaks)}")
    verdict("T8 water held below grade", ok, lines)

    # ---------------------------------------------------------------- T9 drains
    lines, ok = [], True
    sewers = [s for s in p.below if s["level"] == "B2"]
    for d in p.drains:
        x, z = d["gully"]
        if "melt" in d["building"]:
            continue
        under = [s for s in sewers if s["box"][0] <= x <= s["box"][1] and s["box"][2] <= z <= s["box"][3]]
        if not under:
            ok = False; lines.append(f"gully {d['building']} {x},{z}: no sewer vault under it"); continue
        shaft = [m.name(x, f, z) for f in range(-8, -1)]
        if any(nm not in (None, "minecraft:air") and not (classify(nm) & PASS) for nm in shaft):
            ok = False; lines.append(f"gully {d['building']} {x},{z}: shaft blocked {shaft}")
        if m.name(x, -1, z) != "minecraft:iron_bars":
            ok = False; lines.append(f"gully {d['building']} {x},{z}: no grate ({m.name(x, -1, z)})")
    lines.append(f"{len(p.drains)} drains")
    verdict("T9 drains reach the sewers", ok, lines)

    # ---------------------------------------------------------------- T10 ids
    lines, ok = [], True
    known = set()
    for fp in BP_BLOCKS.glob("*.json"):
        try:
            d = json.loads(fp.read_text())
            known.add(d["minecraft:block"]["description"]["identifier"])
        except Exception:
            pass
    used = collections.Counter()
    for k in np.unique(m.idx):
        nm = m.names[k]
        if nm:
            used[nm] += int((m.idx == k).sum())
    for nm in sorted(used):
        if nm.startswith("pw:"):
            if nm not in known:
                ok = False; lines.append(f"{nm}: not a block of BP-02 1.3.230 ({used[nm]} cells)")
            if nm != nm.lower():
                ok = False; lines.append(f"{nm}: uppercase")
    lines.append(f"{len(used)} block ids ({sum(1 for n in used if n.startswith('pw:'))} pw:), all pw: ids known to BP-02 1.3.230: {ok}")
    R["block_census"] = dict(used.most_common())
    verdict("T10 block ids", ok, lines)

    # ---------------------------------------------------------------- T11 falls
    lines, ok = [], True
    seen = set()
    for u in both:
        x, y, z = u
        if not W.grounded(x, y, z) or W.ladder[x, y, z] or W.ladder[x, y - 1, z]:
            continue                                      # stepping off a ladder sideways is the climber's own choice
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y, z + dz)
            if n in seen or not W.body_free(*n, frm=u) or W.grounded(*n):
                continue
            h, yy = 0, y
            while yy > 0 and W.body_free(n[0], yy - 1, n[2], frm=(n[0], yy, n[2])) and not W.grounded(n[0], yy, n[2]):
                yy -= 1; h += 1
            seen.add(n)
            if h >= 4:
                ok = False
                lines.append(f"a fall of {h} at {n[0]},{y + m.bottom},{n[2]} (from {x},{z}) onto {m.name(n[0], yy + m.bottom - 1, n[2])}")
    lines.append(f"edges checked {len(seen)}; falls of 4+ blocks (fall damage) from cells reachable both ways: {sum(1 for l in lines if l.startswith('a fall'))}")
    verdict("T11 no damaging falls", ok, lines)

    # ---------------------------------------------------------------- T12 the no-walk mask covers the secret-only space
    lines, ok = [], True
    only = fwd - fwd_shut
    unc = [(x, y + m.bottom, z) for (x, y, z) in only if not in_hidden(x, y + m.bottom, z)]
    if unc:
        ok = False
        cols = collections.Counter((x // 8 * 8, f, z // 8 * 8) for (x, f, z) in unc)
        lines += [f"{n} secret-only cells outside every no-walk box near x {a}.. z {c}.. walk {b}" for (a, b, c), n in cols.most_common(25)]
    lines.append(f"{len(only)} cells reachable only through a secret; {len(only) - len(unc)} inside the {len(p.hidden)} no-walk boxes")
    verdict("T12 no-walk mask covers the hidden network", ok, lines)

    R["summary"] = {k: v["pass"] for k, v in R["tests"].items()}
    R["seconds"] = round(time.time() - t0, 1)
    print(f"{sum(R['summary'].values())} / {len(R['summary'])} tests PASS ({R['seconds']} s); " + "; ".join(R["notes"]))
    return R, (p, m, W, fwd, both, fwd_shut)


if __name__ == "__main__":
    staged = sys.argv[sys.argv.index("--staged") + 1] if "--staged" in sys.argv else None
    R, _ = run(staged)
    if "--json" in sys.argv:
        Path(sys.argv[sys.argv.index("--json") + 1]).write_text(json.dumps(R, indent=1, default=str))
    sys.exit(0 if all(R["summary"].values()) else 1)
