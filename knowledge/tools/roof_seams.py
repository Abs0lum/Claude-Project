#!/usr/bin/env python3
"""roof_seams.py — numeric seam test for the roof kit (task #174): the true-law top surface of each assembly
(tools/roof_heightfield.py, 1 sample per pixel), then every step across a CELL BORDER where both columns hold roof
pieces. A sound roof has no step bigger than ~2.5 px at a border (boards are 1.2 thick, eave/plumb offsets ~1.7);
a quarter-turned or inverted piece shows up as a 6-16 px step. Also reports steps inside a cell (> 4 px) as a
sanity check on the piece itself. Output: _docs/blocks/ROOF-SEAMS-<label>.json + a printed table."""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, "/home/claude/tools")
import roof_heightfield as RH  # noqa: E402

ROOF = ("pw:roof", "pw:crown_ring")


def run(label):
    man = json.loads(Path("/home/claude/_staging/roof_kit_manifest.json").read_text())
    W, H, D = man["size"]
    items = RH.CR.scene(man, min_feet=0)                           # skip the stone pad (datum 1 -> feet 0 and up)
    roofcells = {(x, z) for x, y, z, n, _s in man["blocks"] if n.startswith(ROOF)}
    out = {}
    for a in man["assemblies"]:
        x0, w = a["x"], a["width"]
        zs = sorted({z for (x, z) in roofcells if x0 <= x < x0 + w})
        z0, z1 = zs[0], zs[-1] + 1
        hf = RH.heightfield(items, x0 * 16, z0 * 16, w * 16, (z1 - z0) * 16)
        steps = []
        for j in range(hf.shape[0]):
            for i in range(hf.shape[1] - 1):
                if (i + 1) % 16 == 0:
                    ca, cb = (x0 + i // 16, z0 + j // 16), (x0 + (i + 1) // 16, z0 + j // 16)
                    if ca in roofcells and cb in roofcells and not np.isnan(hf[j, i]) and not np.isnan(hf[j, i + 1]):
                        steps.append(abs(hf[j, i + 1] - hf[j, i]))
        for i in range(hf.shape[1]):
            for j in range(hf.shape[0] - 1):
                if (j + 1) % 16 == 0:
                    ca, cb = (x0 + i // 16, z0 + j // 16), (x0 + i // 16, z0 + (j + 1) // 16)
                    if ca in roofcells and cb in roofcells and not np.isnan(hf[j, i]) and not np.isnan(hf[j + 1, i]):
                        steps.append(abs(hf[j + 1, i] - hf[j, i]))
        s = np.array(steps) if steps else np.zeros(1)
        holes = int(np.isnan(hf[[(z - z0) * 16 + 8 for (x, z) in roofcells if x0 <= x < x0 + w],
                                 [(x - x0) * 16 + 8 for (x, z) in roofcells if x0 <= x < x0 + w]]).sum())
        out[a["assembly"]] = {"border_samples": len(steps), "max_step_px": round(float(s.max()), 2),
                              "steps_over_2.5": int((s > 2.5).sum()), "steps_over_6": int((s > 6).sum()),
                              "p95_step": round(float(np.percentile(s, 95)), 2), "centre_holes": holes}
        print(f"{a['assembly']:<20} border samples {len(steps):5d}  max step {s.max():5.2f}  >2.5: {(s > 2.5).sum():4d}  >6: {(s > 6).sum():4d}  p95 {np.percentile(s, 95):4.2f}  centre holes {holes}")
    Path(f"/home/claude/_docs/blocks/ROOF-SEAMS-{label}.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "now")
