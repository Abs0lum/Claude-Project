#!/usr/bin/env python3
"""palace2_walk.py — the MOVEMENT MODEL shared by tools/palace2_verify.py (the tests) and tools/palacegen2.py (the guard
rails): the palace box as numpy codes and a walker that moves like a player / a civ.
A body is 2 cells tall: walk level f needs cells f and f+1 free and something to stand on at f-1 (or a ladder); it steps
up 1 (not onto a fence / wall; on stairs without a jump), steps down 1, falls freely, climbs ladders, drops through
trapdoors; wooden doors open both ways; iron doors only from the side of their button; jib panels and secret paintings
(pw: walk-through blocks, BP-02 1.3.221) are passable when 'open', wall when 'shut'. Pure python + numpy."""
import collections

import numpy as np

PASS, SUP, LAD, TRAP, IRON, SECRET, NOSTEP, WATER, STAIR, SPIRAL, BED, DOOR = (1 << k for k in range(12))
FREE_NAMES = ("minecraft:air", "minecraft:light_block", "minecraft:structure_void", "minecraft:stone_button",
              "minecraft:wooden_button", "minecraft:lever")


def classify(name):
    if name is None or name.startswith(FREE_NAMES) or name.endswith("_carpet"):
        return PASS
    if name in ("pw:jib_panel", "pw:secret_painting"):
        return SECRET
    if name == "minecraft:iron_door":
        return IRON
    if name.endswith("_door"):
        return PASS | DOOR
    if name == "minecraft:ladder":
        return PASS | LAD
    if name.endswith("trapdoor"):
        return PASS | SUP | TRAP
    if name in ("minecraft:water", "minecraft:flowing_water"):
        return WATER
    if name.startswith("pw:spiral_stairs"):
        return SUP | SPIRAL
    if name.endswith("_stairs"):
        return SUP | STAIR
    if name.endswith("_fence") or name.endswith("_wall") or "fence_gate" in name:
        return NOSTEP
    if name.endswith(":bed"):
        return SUP | BED
    return SUP


class Model:
    """the palace as numpy codes + names; index (x, y, z) with y = feet - bottom"""

    def __init__(self, p):
        self.p = p
        sx, sy, sz = p.size
        self.size = (sx, sy, sz)
        self.bottom = p.bottom
        pal = p.st.palette
        names = [n for (n, _s, _v) in pal]
        codes = np.array([classify(n) for n in names] + [classify(None)], dtype=np.int32)
        L0 = np.array(p.st.layer0, dtype=np.int64)
        L0[L0 < 0] = len(names)                          # unset -> the extra 'None' entry (free)
        self.idx = L0.reshape((sx, sy, sz))
        self.names = names + [None]
        self.code = codes[self.idx]
        self.states = [s for (_n, s, _v) in pal] + [{}]

    def name(self, x, f, z):
        return self.names[self.idx[x, f - self.bottom, z]]

    def state(self, x, f, z):
        return {k: v.value for k, v in self.states[self.idx[x, f - self.bottom, z]].items()}

    def inside(self, x, y, z):
        sx, sy, sz = self.size
        return 0 <= x < sx and 0 <= y < sy and 0 <= z < sz


class Walker:
    """the movement model over the code grid; open_secrets decides jib panels / paintings"""

    def __init__(self, m, open_secrets=True, iron_open_from=None, closed_extra=()):
        self.m = m
        c = m.code
        sec = (c & SECRET) != 0
        self.passable = ((c & PASS) != 0) | (sec if open_secrets else np.zeros_like(sec))
        self.support = ((c & SUP) != 0) | (np.zeros_like(sec) if open_secrets else sec)
        for (x, y, z) in closed_extra:
            self.passable[x, y, z] = False
            self.support[x, y, z] = True
        self.iron = (c & IRON) != 0
        self.ladder = (c & LAD) != 0
        self.trap = (c & TRAP) != 0
        self.nostep = (c & NOSTEP) != 0
        self.stair = (c & (STAIR | SPIRAL)) != 0          # walked up without a jump: no extra cell over the head
        self.iron_open_from = iron_open_from or {}     # (x, y, z) iron cell -> set of (x, z) cells it opens from

    def body_free(self, x, y, z, frm=None):
        m = self.m
        if not (m.inside(x, y, z) and m.inside(x, y + 1, z)):
            return False
        for yy in (y, y + 1):
            if self.iron[x, yy, z]:
                if frm is None or (frm[0], frm[2]) not in self.iron_open_from.get((x, yy, z), ()):
                    if not (frm is not None and self.iron[frm[0], frm[1], frm[2]]):   # already inside the doorway
                        return False
            elif not self.passable[x, yy, z]:
                return False
        return True

    def grounded(self, x, y, z):
        if y == 0:
            return True
        return bool(self.support[x, y - 1, z] or self.ladder[x, y, z] or self.ladder[x, y - 1, z] or self.iron[x, y - 1, z])

    def moves(self, u):
        x, y, z = u
        out = []
        if not self.grounded(x, y, z):
            if self.body_free(x, y - 1, z, u) or (self.m.inside(x, y - 1, z) and self.iron[x, y - 1, z]):
                out.append((x, y - 1, z))
            return out
        if self.ladder[x, y, z] and self.body_free(x, y + 1, z, u):
            out.append((x, y + 1, z))
        if y > 0 and (self.ladder[x, y - 1, z] or self.trap[x, y - 1, z]) and self.passable[x, y - 1, z]:
            out.append((x, y - 1, z))
        head_free = self.m.inside(x, y + 2, z) and self.passable[x, y + 2, z]
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, nz = x + dx, z + dz
            if self.body_free(nx, y, nz, u):
                out.append((nx, y, nz))
            elif y > 0 and self.body_free(nx, y - 1, nz, u) and self.grounded(nx, y - 1, nz):
                out.append((nx, y - 1, nz))                     # a step down (a stair's next tread under a low lintel)
            elif (head_free or self.stair[nx, y, nz]) and self.body_free(nx, y + 1, nz, u) and self.support[nx, y, nz] and not self.nostep[nx, y, nz]:
                out.append((nx, y + 1, nz))
        return out

    def bfs(self, starts, limit_box=None):
        seen = set()
        dq = collections.deque()
        for s in starts:
            if self.body_free(*s):
                seen.add(s); dq.append(s)
        while dq:
            u = dq.popleft()
            for v in self.moves(u):
                if v in seen:
                    continue
                if limit_box and not (limit_box[0] <= v[0] <= limit_box[1] and limit_box[2] <= v[2] <= limit_box[3]):
                    continue
                seen.add(v); dq.append(v)
        return seen

    def back(self, fwd, target):
        """the nodes of fwd that can reach `target` (reverse walk over the forward graph restricted to fwd)"""
        preds = collections.defaultdict(list)
        for u in fwd:
            for v in self.moves(u):
                if v in fwd:
                    preds[v].append(u)
        seen = {target}
        dq = collections.deque([target])
        while dq:
            v = dq.popleft()
            for u in preds[v]:
                if u not in seen:
                    seen.add(u); dq.append(u)
        return seen



def node(m, x, f, z):
    return (x, f - m.bottom, z)
