#!/usr/bin/env python3
"""mob_normals_apply.py — task #172 (his 17:55 approval + 18:59 N1 = a, N2 = b): copies the staged creature normal maps,
new texture sets and Mojang MERS copies (_staging/mobnormals/<pack name>/...) into the undelivered build of that pack.
Overwrites only texture_set.json files (they gain their 'normal' layer); every other staged file must be NEW there."""
import json
import shutil
from pathlib import Path

STAGE = Path("/home/claude/_staging/mobnormals")
DEST = {"RP-07 1.4.44": "rp07-1444", "RP-08 1.4.13": "rp08-1413", "RP-04 1.3.156": "rp04-156", "RP-03 1.3.67": "rp03-67",
        "RP-06 1.4.29": "rp06-1429", "RP-01 1.3.117": "rp01-117"}
report = {}
kept = []
for pack_dir in sorted(STAGE.iterdir()):
    dest = Path("/home/claude/_build") / DEST[pack_dir.name]
    n_new = n_set = 0
    for f in pack_dir.rglob("*"):
        if not f.is_file():
            continue
        rel = f.relative_to(pack_dir)
        out = dest / rel
        if out.exists() and not f.name.endswith(".texture_set.json"):
            if out.read_bytes() == f.read_bytes():
                continue
            if f.name.endswith("_n.png"):      # an existing normal the set never referenced: keep it (authored), the set now uses it
                kept.append(str(out.relative_to(dest)))
                continue
            raise SystemExit(f"would overwrite a non-set file: {out}")
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, out)
        n_set += f.name.endswith(".texture_set.json")
        n_new += not f.name.endswith(".texture_set.json")
    report[dest.name] = {"files_added": n_new, "sets_written": n_set}
report["kept_existing_normals"] = kept
Path("/home/claude/_docs/mers/MOB-NORMALS-APPLY.json").write_text(json.dumps(report, indent=1))
print(report)
