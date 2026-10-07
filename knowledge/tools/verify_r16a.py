#!/usr/bin/env python3
"""verify_r16a.py — the gate for build_r16a.py (RP-06 1.4.22 + RP-07 1.4.28). Static checks only rule OUT (P1).
  A   file diff == the planned set (per pack)                 J  every changed / added JSON parses strictly
  K   manifest version + uuids kept                           V1 vex entity: only min_engine_version 1.21.0 + pw_hand added
  V2  RBW lint RP-06: 0 findings (1.21.0 reads strictly)      V3 hand animations: Mojang's item-bone channels, bones exist
  W1  wing census on the NEW builds: parrot + phantom inner|outer joint <= 0.10 px in every flight state
  W2  every animated bone exists; cube count per mob unchanged; the helper bones sit where build_r16a put them
  W3  bind pose: phantom unchanged (every cube's world box identical); parrot = only the outer feathers moved, by the seat shift
  W4  animation: every channel of every other bone identical; the tip's rotation moved to <tip>_hinge, one axis only"""
import hashlib, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, "/home/claude/tools")
import convb_round as R
import wing_contact as W
import molang_rbw_lint as RBW
from verify_rp07_1415_rp06_1410 import world_boxes

ROOT = Path("/home/claude")
fails, n = [], [0]
REP = json.load(open(ROOT / "_docs/r16/build_r16a.json"))


def check(tag, ok, msg=""):
    n[0] += 1; print(("PASS " if ok else "FAIL ") + tag + (f" — {msg}" if msg else ""))
    if not ok: fails.append(tag)


def diff(old, new):
    md5 = lambda p: hashlib.md5(p.read_bytes()).hexdigest()
    fo = {str(p.relative_to(old)): p for p in old.rglob("*") if p.is_file()}; fn = {str(p.relative_to(new)): p for p in new.rglob("*") if p.is_file()}
    return sorted(k for k in fo if k in fn and md5(fo[k]) != md5(fn[k])), sorted(set(fn) - set(fo)), sorted(set(fo) - set(fn))


PACKS = [("RP-06", ROOT / "_build/rp06-1421", ROOT / "_build/rp06-1422", [1, 4, 22],
          {"entity/vex.entity.json", REP["phantom"]["geometry_file"], REP["phantom"]["animation_file"], "manifest.json"}, {"animations/pw_vex_hand.animation.json"}),
         ("RP-07", ROOT / "_build/rp07-1427", ROOT / "_build/rp07-1428", [1, 4, 28],
          {"entity/allay.entity.json", REP["parrot"]["geometry_file"], REP["parrot"]["animation_file"], "manifest.json"}, {"animations/pw_allay_hand.animation.json"})]
for tag, old, new, ver, want_ch, want_add in PACKS:
    ch, add, rem = diff(old, new)
    check(f"A {tag} diff = plan", set(ch) == want_ch and set(add) == want_add and not rem, f"changed {ch} added {add} removed {rem}")
    bad = []
    for f in ch + add:
        if f.endswith(".json"):
            try: json.loads((new / f).read_text(encoding="utf-8-sig"))
            except Exception as e: bad.append((f, str(e)[:60]))
    check(f"J {tag} strict JSON on every changed / added file", not bad, str(bad))
    mo, mn = (json.loads((p / "manifest.json").read_text(encoding="utf-8-sig")) for p in (old, new))
    check(f"K {tag} manifest {ver}, uuids kept", mn["header"]["version"] == ver and mn["header"]["uuid"] == mo["header"]["uuid"]
          and all(a["version"] == ver and a["uuid"] == b["uuid"] for a, b in zip(mn["modules"], mo["modules"])))

# ---------------------------------------------------------------------------------------------------------------- vex / allay
R6o, R6, R7o, R7 = ROOT / "_build/rp06-1421", ROOT / "_build/rp06-1422", ROOT / "_build/rp07-1427", ROOT / "_build/rp07-1428"
eo = R.jl(R6o / "entity/vex.entity.json"); en = R.jl(R6 / "entity/vex.entity.json")
exp = json.loads(json.dumps(eo)); d = exp["minecraft:client_entity"]["description"]
d["min_engine_version"] = "1.21.0"; d["animations"]["pw_hand"] = "animation.pw_vex.hand"; d["scripts"]["animate"].append("pw_hand")
check("V1 vex entity: only min_engine_version 1.8.0 -> 1.21.0 + pw_hand added", en == exp and eo["minecraft:client_entity"]["description"]["min_engine_version"] == "1.8.0")
nent, finds = RBW.lint_pack(R6)
check("V2 RBW lint RP-06 1.4.22: 0 read-before-write findings", not finds, f"{nent} entities; {finds[:3]}")
ao = R.jl(R7o / "entity/allay.entity.json"); an = R.jl(R7 / "entity/allay.entity.json")
exp = json.loads(json.dumps(ao)); d = exp["minecraft:client_entity"]["description"]
d["animations"]["pw_hand"] = "animation.pw_allay.hand"; d["scripts"]["animate"].append("pw_hand")
check("V1b allay entity: only pw_hand added", an == exp)
for pack, gid, aid, bones_want in ((R6, "geometry.pw_vex", "animation.pw_vex.hand", {"rightItem": 0.7, "leftItem": 0.7}),
                                   (R7, "geometry.pw_allay", "animation.pw_allay.hand", {"rightItem": 0.7})):
    _, g = R.geo_file(pack, gid); names = {b["name"] for b in g["bones"]}
    a = W.anim_library(pack)[aid]["bones"]
    ok = set(a) == set(bones_want) and all(a[b]["scale"] == s for b, s in bones_want.items()) and set(bones_want) <= names
    check(f"V3 {aid}: item bones {sorted(bones_want)} scale 0.7 (Mojang), bones exist in {gid}", ok, str({b: a[b] for b in a}))
pre = R.jl(R7 / "entity/allay.entity.json")["minecraft:client_entity"]["description"]["scripts"]["pre_animation"]
check("V3b allay sets variable.holding_trident before the trident turn reads it", any(s.startswith("variable.holding_trident") for s in pre))

# ---------------------------------------------------------------------------------------------------------------- wings
W.SPECS["phantom_new"] = dict(W.SPECS["phantom"], pack=R6); W.SPECS["parrot_new"] = dict(W.SPECS["parrot"], pack=R7)
res = W.census(["phantom_new", "parrot_new"])
worst = {m: max(s["edge_max"] for st in res[m].values() for lab, s in st.items() if s.get("shown") and "|" in lab and "body" not in lab) for m in res}
check("W1 wing joints (phantom wing|tip, parrot inner|outer) <= 0.10 px in every flight state", all(v <= 0.10 for v in worst.values()), str(worst))
for tag, oldp, newp, gid, aid, tips in (("phantom", R6o, R6, "geometry.pw_phantom", "animation.pw_phantom.jem", ("left_wing_tip2", "right_wing_tip2")),
                                        ("parrot", R7o, R7, "geometry.pw_parrot", "animation.pw_parrot.jem", ("left_wing_fly2", "right_wing_fly2"))):
    _, go = R.geo_file(oldp, gid); _, gn = R.geo_file(newp, gid)
    bo = {b["name"]: b for b in go["bones"]}; bn = {b["name"]: b for b in gn["bones"]}
    an_ = W.anim_library(newp)[aid]["bones"]; ao_ = W.anim_library(oldp)[aid]["bones"]
    cubes = lambda bs: sum(len(b.get("cubes", [])) for b in bs)
    check(f"W2 {tag}: every animated bone exists; cube count kept ({cubes(go['bones'])}); helpers {[t + '_hinge' for t in tips]} present",
          set(an_) <= set(bn) and cubes(go["bones"]) == cubes(gn["bones"]) and all(t + "_hinge" in bn and bn[t + "_hinge"]["parent"] == t for t in tips))
    wo = {(nm, i): np.array(p) for nm, i, p, *_ in world_boxes(go["bones"])}
    wn = {}
    for nm, i, p, *_ in world_boxes(gn["bones"]):
        key = nm[:-6] if nm.endswith("_hinge") and nm[:-6] in tips else nm
        wn[(key, i)] = np.array(p)
    moved = {k: float(np.abs(wn[k] - wo[k]).max()) for k in wo if k in wn}
    if tag == "phantom":
        check("W3 phantom bind pose unchanged (every cube's world box identical)", len(moved) == len(wo) and max(moved.values()) < 1e-3, f"max {max(moved.values()):.2e}")
    else:
        sub = set()
        for t in tips: sub |= set(W.subtree(go["bones"], t))
        inner_same = all(v < 1e-3 for (nm, i), v in moved.items() if nm not in sub)
        outer = [(nm, i) for (nm, i) in moved if nm in sub]
        shifts = {k: (wn[k] - wo[k]).mean(0) for k in outer}
        ok = inner_same and len(moved) == len(wo) and all(abs(np.linalg.norm(v) - 1.3355) < 0.01 for v in shifts.values())
        check("W3 parrot bind pose: only the outer feathers moved, each by the 1.34 px seat shift", ok,
              str({k[0]: [round(float(x), 3) for x in v] for k, v in list(shifts.items())[:4]}))
    others_same = all(json.dumps(an_.get(b), sort_keys=True) == json.dumps(ao_.get(b), sort_keys=True) for b in ao_ if b not in tips)
    tip_ok = all(t not in an_ or "rotation" not in an_[t] for t in tips) and all(
        sum(1 for x in an_[t + "_hinge"]["rotation"] if x not in (0, 0.0)) == 1 for t in tips)
    check(f"W4 {tag} animation: other bones identical; tip rotation moved to <tip>_hinge on one axis", others_same and tip_ok,
          str({t + "_hinge": an_.get(t + "_hinge") for t in tips})[:300])
print(f"\n{'GATE OPEN' if not fails else 'GATE SHUT'} {n[0] - len(fails)}/{n[0]}")
sys.exit(1 if fails else 0)
