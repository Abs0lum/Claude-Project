"""dumpgrid.py — load a civtest [CIVDUMP] region into a numpy (y, x, z) array of palette ids (-1 = air) + names."""
import json, re, sys, pickle
import numpy as np
from pathlib import Path

def load(log):
    head = None; rows = {}; pal = {}
    for line in Path(log).read_text(errors="ignore").splitlines():
        if "[CIVTEST]" in line and '"dumphead"' in line:
            head = json.loads(line.split("[CIVTEST] ", 1)[1]); rows = {}; pal = {}
        m = re.search(r"\[CIVDUMP\] (-?\d+) (\d+) (.*)$", line)
        if m: rows.setdefault(int(m.group(1)), {})[int(m.group(2))] = m.group(3)
        m = re.search(r"\[CIVPAL\] (\d+) (\[.*\])\s*$", line)
        if m:
            for j, e in enumerate(json.loads(m.group(2))): pal[int(m.group(1)) + j] = e
    x0, x1, z0, z1, y0, y1 = head["x0"], head["x1"], head["z0"], head["z1"], head["y0"], head["y1"]
    nx, nz, ny = x1 - x0 + 1, z1 - z0 + 1, y1 - y0 + 1
    A = np.full((ny, nx, nz), -1, dtype=np.int16)
    for y in rows:
        s = "".join(rows[y][i] for i in sorted(rows[y]))
        flat = []
        for run in s.split(","):
            if not run: continue
            k, n = (run.split("*") + ["1"])[:2]
            flat.extend([int(k)] * int(n))
        A[y - y0] = np.array(flat[: nx * nz], dtype=np.int16).reshape(nx, nz)
    names = [pal[i][0] for i in range(len(pal))]
    states = [pal[i][1] for i in range(len(pal))]
    return dict(A=A, names=names, states=states, x0=x0, z0=z0, y0=y0, nx=nx, nz=nz, ny=ny)

if __name__ == "__main__":
    G = load(sys.argv[1])
    pickle.dump(G, open(sys.argv[2], "wb"))
    print(G["A"].shape, len(G["names"]))
