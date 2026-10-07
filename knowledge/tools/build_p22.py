#!/usr/bin/env python3
"""build_p22.py — lineup "p22" (PW-TestRunner BP, his 14:52 + 16:51 asks): ONLY what is new in p22, per creature one pen row:
  fam_<kind>      a family relative's clip retargeted onto this creature (FAMILY-SHARING.json, offered) — KEEP / DROP each
  shared_<kind>   REBAKED by sharefix (the p21 copy pulled a part loose; SHARE-FIX.json) — look again
  parade_<short>  a movement clip on a treadmill (PARADE.json) — what p21 marked FROZEN HERE
Each copy plays one clip (name tag = the clip). Creatures with more clips than fit one pen spill over (k / n).
Reads the BUILT packs (entity maps + animation ids must resolve) and the three reports. Writes pw_testrunner_p22.js via
build_p20.write_js (same step format as p21)."""
import json
import sys
from pathlib import Path

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import build_p20 as B  # noqa: E402
import std_convert as S  # noqa: E402


def build(rp_dirs, runner_ver, packs_line):
    census = {c["id"]: c for c in json.loads((ROOT / "_docs/standard/SKELETON-CENSUS.json").read_text())}
    plan = {r["id"]: r for r in json.loads((ROOT / "_docs/sizes/size_law_v2_plan.json").read_text())}
    E = B.entities(rp_dirs)
    lib = set()
    for d in rp_dirs:
        lib |= set(S.Pack(d).anims)
    fam = [r for r in json.loads((ROOT / "_docs/standard/FAMILY-SHARING.json").read_text()) if r.get("offered")]
    fix = [r for r in json.loads((ROOT / "_docs/standard/SHARE-FIX.json").read_text()) if r.get("result") == "REBAKED"]
    par = json.loads((ROOT / "_docs/standard/PARADE.json").read_text())
    want = {}
    for r in fam:
        want.setdefault(r["to"], []).append(("fam", f"fam_{r['kind']}", None))
    for r in fix:
        want.setdefault(r["to"], []).append(("rebaked", f"shared_{r['kind']}", None))
    for r in par:
        for p in r["parade"]:
            want.setdefault(r["id"], []).append(("parade", f"parade_{p['short']}", p["parade"]))
    order = ["quadruped", "bird", "insect_flying", "insect_walking", "arachnid", "crustacean", "lizard_croc", "amphibian",
             "turtle", "snake", "biped_ape", "macropod", "pinniped", "cetacean", "fish", "cephalopod", "jellyfish",
             "humanoid", "fantasy", "bat", "object"]
    mobs = sorted((m for m in want if m in E and m in census and m not in B.UNSAFE),
                  key=lambda m: (order.index(census[m]["body_plan"]) if census[m]["body_plan"] in order else 99,
                                 census[m].get("species") or m, m))
    data, n, missing = [], 0, []
    for m in mobs:
        desc, _ = E[m]
        amap = desc.get("animations") or {}
        clips = []
        for what, short, pid in want[m]:
            aid = pid or amap.get(short)
            if not aid or aid not in lib:
                missing.append((m, short))
                continue
            clips.append((what, short, aid))
        if not clips:
            continue
        water = census[m]["body_plan"] in B.WATER_PLANS
        cap = max(1, B.cap_for(B.width(plan.get(m, {})), water))
        chunks = [clips[k:k + cap] for k in range(0, len(clips), cap)]
        for ci, ch in enumerate(chunks, 1):
            n += 1
            ids = [{"mob": m, "label": f"{B.name_of(m).lower()} {s}", "name": s, "play": a} for _, s, a in ch]
            tail = f" ({ci} / {len(chunks)})" if len(chunks) > 1 else ""
            kinds = {w for w, _, _ in ch}
            data.append({"id": f"n{n:04d}", "group": f"P22 {census[m]['body_plan'].upper().replace('_', ' ')}",
                         "title": f"{B.name_of(m).upper()}{tail}"[:120],
                         "look": f"{B.name_of(m).upper()} — LEFT to RIGHT each copy plays ONE clip (its name tag): "
                                 f"{', '.join(s for _, s, _ in ch)}."
                                 + (" fam_ = a family relative's motion fitted to this body: KEEP or DROP (note)." if "fam" in kinds else "")
                                 + (" shared_ = re-copied the careful way (it came apart in p21): look again." if "rebaked" in kinds else "")
                                 + (" parade_ = a walk / run on a treadmill (in p21 it stood frozen): does the gait fit?" if "parade" in kinds else ""),
                         "rig": B.pen_for(ids, None, water, cap)})
    B.write_js("p22", data, runner_ver, packs_line, "p22: the new family motions, the re-copied shared clips, the treadmill gaits",
               "Look for: each copy moves as its name tag says; parts stay joined; the motion fits the animal. fam_: keep or drop. "
               "parade_: does the gait fit? A clip that looks wrong: note its name tag.")
    (ROOT / "_docs/standard/P22-NOT-SHOWN.md").write_text("# p22 — clips planned but not resolvable in the built packs\n\n"
                                                         + "\n".join(f"- {m}: {s}" for m, s in missing) + "\n")
    print(f"p22 {len(data)} steps · {len(mobs)} creatures · {sum(len(v) for v in want.values())} clips planned · "
          f"{len(missing)} unresolved")
    return data
