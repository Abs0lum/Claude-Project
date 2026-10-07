#!/usr/bin/env python3
"""std_groups.py — his 14:35 (10-01) prudence rule: build the STANDARD round in GROUPS, freeze each finished group, and put
them together at the end without anything being lost or overlapping.

Groups (every staged creature belongs to exactly ONE; ownership = every staged file whose name starts with the slug):
  birds_fold     the 26 spread-resting AnF birds (_docs/standard/FOLD-IDS.txt)        — flight + fold + legs
  birds_flutter  std_flutter.FLUTTER_IDS                                               — flutter + legs
  birds_flight   every other staged bird, bat, phantom                                 — flight v2 + legs
  quads          body_plan quadruped                                                   — Q1 joints
  plans          every other staged body plan                                          — std_plans
The SHARING layer (std_share.py) is applied LAST on top of the groups; it is checked by its own list (SHARING.json): every
applied `shared_<kind>` must exist in the target's animation file AND be named by its entity.

  freeze [GROUP ...]   copy the group's staged files to _staging/groups/<GROUP>/ (read-only) + MANIFEST.json {file: md5}.
                       Default: all groups. A group already frozen is re-frozen only when named explicitly (reopened).
  check                (the guard before every build) staged file vs its group's frozen md5 — CHANGED / MISSING / NEW;
                       ownership overlaps. Exit 1 on any finding. Nothing is ever deleted: a re-freeze
                       first moves the old frozen copy to _staging/groups/_history/<GROUP>-<stamp>/."""
import hashlib
import json
import shutil
import stat
import sys
import time
from pathlib import Path

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import std_convert as S  # noqa: E402
import std_flutter as F  # noqa: E402

GDIR = ROOT / "_staging/groups"
BASE = ROOT / "_staging/std"   # the guard ALWAYS checks the base groups, whatever folder a builder reads (15:2x 10-01)


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def staged_files():
    """{slug: [paths relative to the staging root]}"""
    out = {}
    for f in BASE.rglob("*"):
        if f.is_file():
            out.setdefault(f.name.split(".")[0], []).append(str(f.relative_to(BASE)))
    return out


def groups():
    census = json.loads((ROOT / "_docs/standard/SKELETON-CENSUS.json").read_text())
    fold = set((ROOT / "_docs/standard/FOLD-IDS.txt").read_text().split())
    flutter = set(F.FLUTTER_IDS)
    files = staged_files()
    g = {"birds_fold": {}, "birds_flutter": {}, "birds_flight": {}, "quads": {}, "plans": {}}
    owner = {}
    for c in census:
        slug = S.slug_of(c["id"])
        if slug not in files:
            continue
        if c["id"] in fold:
            k = "birds_fold"
        elif c["id"] in flutter:
            k = "birds_flutter"
        elif c["body_plan"] in ("bird", "bat") or c["id"] == "minecraft:phantom":
            k = "birds_flight"
        elif c["body_plan"] == "quadruped":
            k = "quads"
        else:
            k = "plans"
        owner.setdefault(slug, []).append(k)
        g[k][slug] = files[slug]
    return g, owner, files


def freeze(names):
    g, owner, _ = groups()
    stamp = time.strftime("%Y%m%d-%H%M%S")
    for name in names:
        dst = GDIR / name
        if dst.exists():
            hist = GDIR / "_history" / f"{name}-{stamp}"
            hist.parent.mkdir(parents=True, exist_ok=True)
            for p in dst.rglob("*"):
                p.chmod(p.stat().st_mode | stat.S_IWUSR)
            dst.chmod(dst.stat().st_mode | stat.S_IWUSR)
            shutil.move(str(dst), str(hist))
        man = {}
        for slug, rels in sorted(g[name].items()):
            for r in rels:
                (dst / r).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(BASE / r, dst / r)
                man[r] = md5(BASE / r)
        (dst / "MANIFEST.json").write_text(json.dumps({"group": name, "frozen": stamp, "creatures": len(g[name]),
                                                       "files": man}, indent=1))
        for p in dst.rglob("*"):
            p.chmod(p.stat().st_mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))
        print(f"frozen {name}: {len(g[name])} creatures, {len(man)} files")


def check():
    g, owner, files = groups()
    find = []
    over = {s: o for s, o in owner.items() if len(o) > 1}
    for s, o in over.items():
        find.append(f"OVERLAP {s}: {o}")
    claimed = {s for grp in g.values() for s in grp}
    for s in files:
        if s not in claimed:
            find.append(f"UNOWNED {s}: {files[s]}")
    n_ok = 0
    for name in g:
        man_p = GDIR / name / "MANIFEST.json"
        if not man_p.exists():
            find.append(f"NOT FROZEN {name}")
            continue
        man = json.loads(man_p.read_text())["files"]
        for r, h in man.items():
            if not (GDIR / name / r).exists() or md5(GDIR / name / r) != h:   # the frozen copy itself (root ignores a-w)
                find.append(f"FROZEN COPY DAMAGED {name}: {r}")
            p = BASE / r
            if not p.exists():
                find.append(f"MISSING {name}: {r}")
            elif md5(p) != h:
                find.append(f"CHANGED {name}: {r}")
            else:
                n_ok += 1
        now = {r for rels in g[name].values() for r in rels}
        for r in sorted(now - set(man)):
            find.append(f"NEW (not in frozen {name}): {r}")
        for r in sorted(set(man) - now):   # 16:5x: a creature that moved to another group (reclassified) must be re-frozen
            find.append(f"MOVED OUT (frozen in {name}, owned elsewhere now): {r}")
    n_sh = 0   # 10-01 15:1x: sharing is a LAYER now (std_layers.py checks it); the base groups hold no shared_ clips
    rows = []
    print(f"groups: " + ", ".join(f"{k} {len(v)}" for k, v in g.items()) +
          f" · frozen files matching {n_ok} · base only (the layers are checked by std_layers.py)")
    for x in find[:60]:
        print("  " + x)
    print("GUARD", "PASS" if not find else f"FAIL ({len(find)} findings)")
    return not find


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "freeze":
        names = sys.argv[2:] or [k for k in ("birds_fold", "birds_flutter", "birds_flight", "quads", "plans")
                                 if not (GDIR / k).exists()]
        freeze(names)
    else:
        sys.exit(0 if check() else 1)
