#!/usr/bin/env python3
"""verify_mers_round.py — gate for the MERS round builds (rp07-1439, rp06-1425, rp08-149, rp04-143).
Static checks only rule OUT problems (P1); his Vibrant Visuals witness rules IN."""
import hashlib
import json
import random
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import mers_derive as D  # noqa: E402

PAIRS = {"rp07-1439": ("rp07-1438", [1, 4, 39]), "rp06-1425": ("rp06-1424", [1, 4, 25]),
         "rp08-149": ("rp08-148", [1, 4, 9]), "rp04-143": ("rp04-142", [1, 3, 143])}
ORDERS = {"world file 09-22": ["rp08-149", "rp07-1439", "rp06-1425", "rp04-143"],
          "install-set line": ["rp07-1439", "rp06-1425", "rp08-149", "rp04-143"]}
results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print(("PASS " if ok else "FAIL ") + name + (f" — {detail}" if detail else ""))


def files(d):
    return {p.relative_to(d).as_posix() for p in d.rglob("*") if p.is_file()}


def md5(p):
    return hashlib.md5(p.read_bytes()).hexdigest()


def find(pack, rel):
    for ext in (".png", ".tga"):
        p = ROOT / "_build" / pack / (rel + ext)
        if p.exists():
            return p
    return None


manifest = json.loads((ROOT / "_logs/mers_round_manifest.json").read_text())
inv = json.loads((ROOT / "_docs/mers/MERS-INVENTORY.json").read_text())

# A — every texture set parses, format 1.21.30, its colour / MERS / normal sit beside it in the SAME pack
bad, n_sets = [], 0
for new in PAIRS:
    for ts in (ROOT / "_build" / new).rglob("*.texture_set.json"):
        n_sets += 1
        try:
            d = json.loads(ts.read_text(encoding="utf-8-sig"))
            t = d["minecraft:texture_set"]
            assert d["format_version"] in ("1.21.30",) or ts.name == "blaze.texture_set.json"
            for key in ("color", "metalness_emissive_roughness_subsurface", "normal"):
                v = t.get(key)
                if isinstance(v, str):
                    assert any((ts.parent / (v + e)).exists() for e in (".png", ".tga")), (key, v)
        except Exception as e:  # noqa: BLE001
            bad.append(f"{new}/{ts.name}: {e!r}")
check("A sets parse + companions in the same pack", not bad, f"{n_sets} sets; {bad[:3]}")

# B — MERS + normal are the colour's size
bad, pre = [], []
for new in PAIRS:
    ours = set(manifest["added"].get(new, []))
    for ts in (ROOT / "_build" / new).rglob("*.texture_set.json"):
        mine = ts.relative_to(ROOT / "_build" / new).as_posix() in ours
        t = json.loads(ts.read_text(encoding="utf-8-sig"))["minecraft:texture_set"]
        col = next((ts.parent / (t["color"] + e) for e in (".png", ".tga") if (ts.parent / (t["color"] + e)).exists()), None)
        for key in ("metalness_emissive_roughness_subsurface", "normal"):
            v = t.get(key)
            if isinstance(v, str) and col is not None:
                f = next(ts.parent / (v + e) for e in (".png", ".tga") if (ts.parent / (v + e)).exists())
                if Image.open(f).size != Image.open(col).size:
                    (bad if mine else pre).append(f"{new}/{f.name}")
check("B MERS / normal size == colour size (this round's sets)", not bad, f"{len(bad)} mismatched {bad[:3]}")
print(f"     info: {len(pre)} PRE-EXISTING block sets with a smaller MER/normal than colour (not this round): {pre[:4]}")

# C — only additions (+ replaced raw normals) + manifest.json changed vs the source build
bad = []
for new, (old, ver) in PAIRS.items():
    a, b = ROOT / "_build" / old, ROOT / "_build" / new
    fa, fb = files(a), files(b)
    added = set(manifest["added"].get(new, []))
    replaced = set(manifest["replaced_raw_normals"].get(new, []))
    if fa - fb:
        bad.append(f"{new} lost {len(fa - fb)}")
    if (fb - fa) - added:
        bad.append(f"{new} unexpected new {sorted((fb - fa) - added)[:3]}")
    changed = [f for f in fa & fb if f != "manifest.json" and f not in added and md5(a / f) != md5(b / f)]
    changed = [f for f in changed if f not in replaced]
    if changed:
        bad.append(f"{new} changed {changed[:3]}")
check("C nothing but the MERS round's files changed", not bad, "; ".join(bad))

# D — manifests: version bumped, uuids unchanged
bad = []
for new, (old, ver) in PAIRS.items():
    ma = json.loads((ROOT / "_build" / old / "manifest.json").read_text(encoding="utf-8-sig"))
    mb = json.loads((ROOT / "_build" / new / "manifest.json").read_text(encoding="utf-8-sig"))
    if mb["header"]["version"] != ver or any(m["version"] != ver for m in mb["modules"]):
        bad.append(f"{new} version")
    if ma["header"]["uuid"] != mb["header"]["uuid"] or [m["uuid"] for m in ma["modules"]] != [m["uuid"] for m in mb["modules"]]:
        bad.append(f"{new} uuid")
check("D manifests: version bumped, uuids kept", not bad, "; ".join(bad))

# E — coverage under BOTH pack orders: the winning colour of every tier1 / derive texture carries a set
for oname, order in ORDERS.items():
    missing = []
    for t in inv:
        if t["class"] not in ("tier1", "derive") or t.get("existing_set"):
            continue
        win = next((p for p in order if find(p, t["rel"])), None)
        if win is None:
            continue  # colour lives below our four packs (RP-01) — not in this round
        if not (ROOT / "_build" / win / (t["rel"] + ".texture_set.json")).exists():
            missing.append(f"{win}:{t['rel']}")
    check(f"E coverage, order '{oname}'", not missing, f"{len(missing)} without a set {missing[:3]}")

# F — tier 1 MERS == Lesson #156 of the Patrix _s (24 random, recomputed independently of the writer)
random.seed(7)
t1 = [t for t in inv if t["class"] == "tier1"]
bad = []
for t in random.sample(t1, min(24, len(t1))):
    pack = next(p for p in ORDERS["world file 09-22"] if find(p, t["rel"]))
    got = np.asarray(Image.open(ROOT / "_build" / pack / (t["rel"] + "_mers.png")).convert("RGBA")).astype(int)
    spec = np.asarray(Image.open(t["patrix_s"]).convert("RGBA")).astype(int)
    R, G, B, A = (spec[..., i] for i in range(4))
    want = np.stack([np.where(G >= 230, 255, 0), np.where(A < 255, A, 0), 255 - R,
                     np.where(B >= 65, np.round((B - 64) * 255 / 191), 0)], -1).astype(np.uint8)
    if want.shape != got.shape:
        want = np.asarray(Image.fromarray(want, "RGBA").resize(got.shape[1::-1], Image.BOX)).astype(int).copy()
        want[..., 0] = np.where(want[..., 0] >= 128, 255, 0)
    if np.abs(want - got).max() > 1:
        bad.append(t["rel"])
check("F tier-1 MERS == #156 of Patrix's _s (24 sampled)", not bad, f"{bad[:3]}")

# G — derived maps: emissive 0 everywhere, metal only on metal-class objects
bad = []
report = json.loads((ROOT / "_docs/mers/MERS-DERIVE-REPORT.json").read_text())
for r in report:
    if r.get("kind") != "derive":
        continue
    if r["mean"][1] != 0 or (r["mean"][0] > 0 and r.get("material") != "metal"):
        bad.append(r["rel"])
check("G derived: no glow, metal only on metal objects", not bad, f"{len(bad)} {bad[:3]}")

# H — pack sizes under his 250 MB cap
sizes = {new: sum(p.stat().st_size for p in (ROOT / "_build" / new).rglob("*") if p.is_file()) / 1e6 for new in PAIRS}
check("H unzipped pack sizes < 250 MB", all(v < 250 for v in sizes.values()), ", ".join(f"{k} {v:.0f} MB" for k, v in sizes.items()))

# I — unit tests of the formulas
import subprocess  # noqa: E402
r = subprocess.run([sys.executable, str(ROOT / "tools/test_mers_derive.py")], capture_output=True, text=True)
check("I formula unit tests", r.returncode == 0, r.stdout.strip())

n_ok = sum(ok for _, ok, _ in results)
print(f"\nGATE {n_ok}/{len(results)}")
sys.exit(0 if n_ok == len(results) else 1)
