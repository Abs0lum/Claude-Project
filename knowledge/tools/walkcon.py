"""walkcon.py — 2.5D walk connectivity of a civtest dump (vanilla-ish mob rules): which standing places a villager can
reach from a start. Classes: PASS (no collision), HALF (a floor inside the cell: slab, stairs, ramp quarters, bed),
TALL (fence / wall / pane / bars / gate: 1.5 high, never crossed, never stood on), FULL (the rest).
Moves: 4-neighbours, up <= 1.0 (a jump), down <= 3.0 (a drop); ladders join their column vertically.
Usage: walkcon.py grid.pkl x y z [x y z ...]  (the first point is the start; others are checked)"""
import pickle, sys
from collections import deque
import numpy as np

PASS_K = ["air", "short_grass", "tall_grass", "fern", "flower", "sapling", "torch", "lantern", "carpet", "snow_layer", "vine", "sign",
          "light_block", "dandelion", "poppy", "tulip", "orchid", "allium", "bluet", "daisy", "cornflower", "lily_of", "rose_bush", "peony",
          "lilac", "sunflower", "button", "lever", "pressure_plate", "rail", "redstone_wire", "tripwire", "_door", "ladder", "deadbush", "bush",
          "mushroom", "petals", "leaf_litter", "web"]
TALL_K = ["fence", "_wall", "cobblestone_wall", "pane", "iron_bars", "gate"]
def classify(name, st):
    n = name.replace("minecraft:", "")
    if name == "minecraft:air": return ("PASS", 0)
    if "water" in n or "lava" in n: return ("LIQ", 0)
    if any(k in n for k in TALL_K) and "wall_sign" not in n and "wall_banner" not in n: return ("TALL", 1.5)
    if any(k in n for k in PASS_K): return ("PASS", 0)
    if "_slab" in n:
        top = st.get("top_slot_bit") or st.get("minecraft:vertical_half") == "top"
        return ("FULL", 1) if top else ("HALF", 0.5)
    if "ramp_" in n:
        q = int(n.split("_q")[-1]) if "_q" in n else 4
        return ("HALF", q * 0.25)
    if "stairs" in n:
        return ("FULL", 1) if st.get("upside_down_bit") else ("HALF", 0.5)
    if n == "bed": return ("HALF", 0.5625)
    if "trapdoor" in n: return ("PASS", 0)
    return ("FULL", 1)

def build(G):
    A, names, states = G["A"], G["names"], G["states"]
    cls = [classify(n, s) for n, s in zip(names, states)]
    kind = np.zeros(A.shape, dtype=np.int8)       # 0 PASS 1 HALF 2 FULL 3 TALL 4 LIQ 5 LADDER
    hh = np.zeros(A.shape, dtype=np.float32)
    code = {"PASS": 0, "HALF": 1, "FULL": 2, "TALL": 3, "LIQ": 4}
    lut_k = np.array([code[c[0]] for c in cls] + [0], dtype=np.int8)
    lut_h = np.array([c[1] for c in cls] + [0], dtype=np.float32)
    idx = np.where(A < 0, len(cls), A)
    kind = lut_k[idx]; hh = lut_h[idx]
    lad = np.array(["ladder" in n for n in names] + [False])
    kind = np.where(lad[idx], 5, kind)
    return kind, hh

def stand_e(kind, hh, y, x, z):
    """the floor height of a standing place with feet in cell (y, x, z), or None"""
    ny = kind.shape[0]
    if y <= 0 or y + 2 >= ny: return None
    k, k1, k2, kb = kind[y, x, z], kind[y + 1, x, z], kind[y + 2, x, z], kind[y - 1, x, z]
    if k == 5: return float(y)                                         # in a ladder: always "standing" (climbing)
    if k == 1:                                                        # a half block: feet on it
        if k1 in (0, 5) and (hh[y, x, z] <= 0.05 or k2 in (0, 5)): return y + float(hh[y, x, z])
        return None
    if k == 0 and k1 in (0, 5):
        if kb == 2 or (kb == 1 and hh[y - 1, x, z] >= 0.99): return float(y)
    return None

def main():
    G = pickle.load(open(sys.argv[1], "rb"))
    kind, hh = build(G)
    x0, z0, y0 = G["x0"], G["z0"], G["y0"]
    ny, nx, nz = kind.shape
    E = np.full(kind.shape, np.nan, dtype=np.float32)
    for y in range(1, ny - 2):
        for x in range(nx):
            col_k = kind[:, x, :]
        # vectorised: compute per (x,z) at this y
        k, k1, k2, kb = kind[y], kind[y + 1], kind[y + 2], kind[y - 1]
        h = hh[y]; hb = hh[y - 1]
        lad = (k == 5)
        half = (k == 1) & ((k1 == 0) | (k1 == 5)) & ((h <= 0.05) | (k2 == 0) | (k2 == 5))
        plain = (k == 0) & ((k1 == 0) | (k1 == 5)) & ((kb == 2) | ((kb == 1) & (hb >= 0.99)))
        e = np.full(k.shape, np.nan, dtype=np.float32)
        e[plain] = y; e[half] = y + h[half]; e[lad] = y
        E[y] = e
    pts = [tuple(map(int, sys.argv[i:i + 3])) for i in range(2, len(sys.argv), 3)]
    def node(px, py, pz):
        """the standing place nearest a world point (feet y within -2..+2)"""
        x, z = px - x0, pz - z0
        for dy in (0, -1, 1, -2, 2):
            y = py - y0 + dy
            if 0 < y < ny - 2 and 0 <= x < nx and 0 <= z < nz and not np.isnan(E[y, x, z]): return (y, x, z)
        return None
    s = node(*pts[0])
    print("start", pts[0], "->", s, None if s is None else E[s])
    comp = np.zeros(kind.shape, dtype=np.int32)
    def flood(s, cid):
        q = deque([s]); comp[s] = cid; n = 0
        while q:
            y, x, z = q.popleft(); n += 1; e = E[y, x, z]
            if kind[y, x, z] == 5:
                for dy in (-1, 1):
                    yy = y + dy
                    if 0 < yy < ny - 2 and not np.isnan(E[yy, x, z]) and comp[yy, x, z] == 0: comp[yy, x, z] = cid; q.append((yy, x, z))
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                xx, zz = x + dx, z + dz
                if not (0 <= xx < nx and 0 <= zz < nz): continue
                for yy in range(max(1, y - 4), min(ny - 2, y + 3)):
                    e2 = E[yy, xx, zz]
                    if np.isnan(e2) or comp[yy, xx, zz]: continue
                    if e2 - e > 1.01 or e - e2 > 3.01: continue
                    # head room for a jump up: the cell above our head must be free when climbing a full block
                    if e2 - e > 0.6 and kind[min(ny - 1, y + 2), x, z] not in (0, 5): continue
                    comp[yy, xx, zz] = cid; q.append((yy, xx, zz))
        return n
    n = flood(s, 1)
    print("reachable places from start:", n)
    for p in pts[1:]:
        q = node(*p)
        print(p, "->", "NO STAND" if q is None else ("REACH" if comp[q] == 1 else "cut off"))
    np.save("comp.npy", comp); np.save("E.npy", E)

if __name__ == "__main__":
    main()
