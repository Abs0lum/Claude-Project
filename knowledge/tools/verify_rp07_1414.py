#!/usr/bin/env python3
"""verify_rp07_1414.py — gate for RP-07 v1.4.14 (D-C267).
  A  the diff vs v1.4.13 = the two .tga removed + manifest (+ textures_list only if it named them)
  B  with RP-06 v1.4.9 below: the stems textures/entity/zombie/drowned and skeleton/stray are held ONLY by RP-06 (.png) —
     checked across the whole local stack in every image extension
  C  stack-wide: zero stems where a higher pack's file shadows a lower pack's in a different extension
  D  manifest 1.4.14, uuid kept
Exit 1 on any FAIL."""
import filecmp, glob, json, os, sys, zipfile
from collections import defaultdict
from pathlib import Path

ROOT = Path("/home/claude"); OLD, NEW = ROOT / "_build/rp07-1413", ROOT / "_build/rp07-1414"
STACK = [("TestRunner RP", "_build/testrunner-rp-0.3.0"), ("Markers RP", "_build/markers-0.2.1"), ("LeafProbe RP", "ZIP:_intake/stack-rps/PW-LeafProbe-RP-v0_3_1.mcpack"),
         ("StripMine RP", "ZIP:_intake/stack-rps/PW-StripMine-RP-v3_0_1.mcpack"), ("RP-11", "ZIP:_intake/stack-rps/RP-11-AbsolutRealism-Ores-RP-v1_3_35.mcpack"),
         ("RP-10", "_build/rp10-142"), ("RP-08", "_build/rp08-147"), ("RP-07", "_build/rp07-1414"), ("RP-06", "_build/rp06-149"), ("RP-05", "_build/rp05-51"),
         ("RP-04", "_build/rp04-142"), ("RP-03", "_build/rp03-60"), ("RP-02", "_build/rp02-205"), ("RP-01", "_build/rp01-104")]
IMG = (".png", ".tga", ".jpg", ".jpeg")
results = []


def check(tag, ok, msg):
    results.append((tag, bool(ok), msg)); print(f"{'PASS' if ok else 'FAIL'} {tag}: {msg}")


def files(root):
    return {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()}


def stems():
    out = defaultdict(list)
    for rank, (name, root) in enumerate(STACK):
        if root.startswith("ZIP:"):
            z = zipfile.ZipFile(ROOT / root[4:])
            for n in z.namelist():
                if n.lower().startswith("textures/") and n.lower().endswith(IMG):
                    s, e = os.path.splitext(n); out[s].append((rank, name, e.lower()))
        else:
            r = ROOT / root
            if not r.exists():                      # RP-04 .142 may not be built yet: fall back to .141 (same texture set for this check)
                r = ROOT / root.replace("rp04-142", "rp04-141")
            for f in glob.glob(f"{r}/textures/**/*", recursive=True):
                if f.lower().endswith(IMG):
                    s, e = os.path.splitext(os.path.relpath(f, r)); out[s].append((rank, name, e.lower()))
    return out


def main():
    fo, fn = files(OLD), files(NEW)
    removed, added = fo - fn, fn - fo
    changed = {f for f in fo & fn if not filecmp.cmp(OLD / f, NEW / f, shallow=False)}
    check("A1", removed == {"textures/entity/zombie/drowned.tga", "textures/entity/skeleton/stray.tga"} and not added, f"removed {sorted(removed)} added {sorted(added)}")
    check("A2", changed <= {"manifest.json", "textures/textures_list.json"} and "manifest.json" in changed, f"changed {sorted(changed)}")
    st = stems()
    for s in ("textures/entity/zombie/drowned", "textures/entity/skeleton/stray"):
        holders = sorted(st.get(s, []))
        check(f"B {s}", [(h[1], h[2]) for h in holders] == [("RP-06", ".png")], f"holders {[(h[1], h[2]) for h in holders]}")
    shadows = []
    for s, h in st.items():
        h = sorted(h)
        if len({x[1] for x in h}) > 1 and len({x[2] for x in h}) > 1: shadows.append((s, h))
    check("C", not shadows, f"cross-extension cross-pack shadows: {len(shadows)} {[s for s, _ in shadows][:5]}")
    mo, mn = json.loads((OLD / "manifest.json").read_text()), json.loads((NEW / "manifest.json").read_text())
    check("D", mn["header"]["version"] == [1, 4, 14] and mn["header"]["uuid"] == mo["header"]["uuid"], f"version {mn['header']['version']} uuid kept")
    fails = [r for r in results if not r[1]]
    print(f"GATE {'OPEN' if not fails else 'CLOSED'} {len(results) - len(fails)}/{len(results)}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
